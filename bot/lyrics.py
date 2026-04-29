"""Fetch song lyrics from the free lyrics.ovh API."""
import logging
import re
from urllib.parse import quote
import httpx

logger = logging.getLogger(__name__)

def _strip(s: str) -> str:
    s = re.sub(r"\(.*?\)|\[.*?\]", "", s)
    s = re.sub(r"\b(official|video|audio|lyrics?|hd|hq|mv|m/?v|"
               r"remix|cover|live|extended|ft\.?|feat\.?)\b",
               "", s, flags=re.I)
    s = re.sub(r"\s+", " ", s).strip(" -—|·,.")
    return s.strip()

def split_title(raw_title: str) -> tuple[str, str]:
    title = _strip(raw_title or "")
    for sep in (" - ", " — ", " – ", " | ", " : "):
        if sep in title:
            parts = title.split(sep, 1)
            return _strip(parts[0]), _strip(parts[1])
    return "", title

def fetch_lyrics(artist: str, title: str) -> str | None:
    artist = (artist or "").strip()
    title = (title or "").strip()
    if not title:
        return None
    url = (
        "https://api.lyrics.ovh/v1/"
        f"{quote(artist or 'unknown', safe='')}/{quote(title, safe='')}"
    )
    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as c:
            resp = c.get(url)
        if resp.status_code == 200:
            data = resp.json()
            lyr = (data.get("lyrics") or "").strip()
            return lyr or None
        if resp.status_code == 404:
            return None
        logger.warning(f"lyrics.ovh status {resp.status_code}")
    except Exception as e:
        logger.warning(f"lyrics.ovh error: {e}")
    return None

def fetch_for_youtube_title(raw_title: str) -> tuple[str | None, str, str]:
    artist, song = split_title(raw_title)
    candidates = []
    if artist and song:
        candidates.append((artist, song))
        candidates.append((song, artist))
    if song:
        candidates.append(("", song))
    
    for a, s in candidates:
        lyr = fetch_lyrics(a, s)
        if lyr:
            return lyr, a, s
    return None, artist, song
