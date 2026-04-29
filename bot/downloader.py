import os
import shutil
import uuid
import logging
from typing import Callable, Optional, List, Dict
from urllib.parse import urlparse
import yt_dlp
from config import MAX_FILE_SIZE_MB

logger = logging.getLogger(__name__)

ALLOWED_HOSTS = {
    "youtube.com", "www.youtube.com", "youtu.be", "m.youtube.com", "music.youtube.com",
    "instagram.com", "www.instagram.com",
    "tiktok.com", "www.tiktok.com", "vm.tiktok.com",
    "twitter.com", "www.twitter.com", "x.com", "www.x.com",
    "facebook.com", "www.facebook.com", "fb.watch", "m.facebook.com",
    "soundcloud.com", "www.soundcloud.com",
}

MAX_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024

class DownloadError(Exception):
    pass

def is_allowed_url(url: str) -> bool:
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            return False
        host = (parsed.hostname or "").lower()
        return host in ALLOWED_HOSTS
    except Exception:
        return False

def is_youtube_url(url: str) -> bool:
    try:
        host = (urlparse(url).hostname or "").lower()
        return host in {
            "youtube.com", "www.youtube.com", "youtu.be",
            "m.youtube.com", "music.youtube.com",
        }
    except Exception:
        return False

def extract_youtube_id(url: str) -> str | None:
    try:
        p = urlparse(url)
        host = (p.hostname or "").lower()
        if host == "youtu.be":
            return p.path.lstrip("/").split("/", 1)[0] or None
        if host.endswith("youtube.com"):
            from urllib.parse import parse_qs
            qs = parse_qs(p.query)
            if "v" in qs and qs["v"]:
                return qs["v"][0]
            parts = [x for x in p.path.split("/") if x]
            if len(parts) >= 2 and parts[0] in ("shorts", "embed", "v"):
                return parts[1]
    except Exception:
        pass
    return None

def get_playlist_info(url: str) -> List[Dict]:
    """Extracts basic info for all videos in a playlist."""
    opts = {
        "extract_flat": True,
        "quiet": True,
        "no_warnings": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if "entries" in info:
                return [{"id": e["id"], "title": e["title"], "url": e["url"]} for e in info["entries"] if e]
    except Exception as e:
        logger.error(f"Playlist extraction error: {e}")
    return []

def download(
    url: str,
    mp3: bool = False,
    quality: str = "192",
    progress_hook: Optional[Callable[[dict], None]] = None,
) -> tuple[str, str]:
    """Download media. Returns (filepath, work_dir)."""
    if not is_allowed_url(url):
        raise DownloadError("Site not supported.")
    
    work_dir = os.path.join("downloads", uuid.uuid4().hex)
    os.makedirs(work_dir, exist_ok=True)
    
    output_template = os.path.join(work_dir, "%(id)s.%(ext)s")
    
    common = {
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "restrictfilenames": True,
    }

    if progress_hook:
        common["progress_hooks"] = [progress_hook]

    if mp3:
        if quality not in ("128", "192", "320"):
            quality = "192"
        opts = {
            **common,
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": quality,
            }],
        }
    else:
        opts = {
            **common,
            "format": "bestvideo[height<=720]+bestaudio/best[height<=720]/best",
            "merge_output_format": "mp4",
        }

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if mp3:
                base, _ = os.path.splitext(filename)
                filename = base + ".mp3"
            elif not os.path.exists(filename):
                # Handle cases where extension might change after merge
                base, _ = os.path.splitext(filename)
                for ext in (".mp4", ".mkv", ".webm"):
                    if os.path.exists(base + ext):
                        filename = base + ext
                        break
    except yt_dlp.utils.DownloadError as e:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise DownloadError(f"Download failed: {e}") from e
    except Exception as e:
        shutil.rmtree(work_dir, ignore_errors=True)
        logger.exception("download error")
        raise DownloadError("Internal error.") from e

    if not os.path.exists(filename):
        shutil.rmtree(work_dir, ignore_errors=True)
        raise DownloadError("File was not created.")

    if os.path.getsize(filename) > MAX_BYTES:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise DownloadError(f"File is larger than {MAX_FILE_SIZE_MB}MB.")

    return filename, work_dir
