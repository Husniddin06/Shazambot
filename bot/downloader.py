import os
import shutil
import uuid
import logging
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

def download(url: str, mp3: bool = False) -> tuple[str, str]:
    """Returns (filepath, work_dir). Caller is responsible for cleanup of work_dir."""
    if not is_allowed_url(url):
        raise DownloadError("Bu sayt qo'llab-quvvatlanmaydi.")
    
    work_dir = os.path.join("downloads", uuid.uuid4().hex)
    os.makedirs(work_dir, exist_ok=True)
    
    output_template = os.path.join(work_dir, "%(id)s.%(ext)s")
    
    opts = {
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "restrictfilenames": True,
        "max_filesize": MAX_BYTES,
        "format": "best[filesize<50M]/best",
    }

    if mp3:
        opts["format"] = "bestaudio/best"
        opts["postprocessors"] = [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }]

    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if mp3:
                base, _ = os.path.splitext(filename)
                filename = base + ".mp3"
    except yt_dlp.utils.DownloadError as e:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise DownloadError(f"Yuklab bo'lmadi: {e}") from e
    except Exception as e:
        shutil.rmtree(work_dir, ignore_errors=True)
        logger.exception("download xatosi")
        raise DownloadError("Ichki xatolik yuz berdi.") from e

    if not os.path.exists(filename):
        shutil.rmtree(work_dir, ignore_errors=True)
        raise DownloadError("Fayl yaratilmadi.")

    if os.path.getsize(filename) > MAX_BYTES:
        shutil.rmtree(work_dir, ignore_errors=True)
        raise DownloadError(f"Fayl {MAX_FILE_SIZE_MB}MB dan katta. Telegram qabul qilmaydi.")

    return filename, work_dir
