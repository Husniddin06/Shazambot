"""Top music charts via yt-dlp search, cached for 1 hour in Redis."""
import json
import logging
import time
import yt_dlp
from utils.redis_cache import r

logger = logging.getLogger(__name__)

_CACHE_KEY = "charts:top"
_CACHE_TTL = 3600
_mem: dict = {"data": [], "ts": 0.0}

def _fetch() -> list[dict]:
    opts = {
        "quiet": True,
        "no_warnings": True,
        "extract_flat": True,
        "skip_download": True,
        "noplaylist": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info("ytsearch10:top music hits this week", download=False)
    except Exception as e:
        logger.warning(f"charts fetch error: {e}")
        return []
    
    out = []
    for entry in (info or {}).get("entries", []) or []:
        if not entry:
            continue
        vid = entry.get("id")
        if not vid:
            continue
        out.append({"video_id": vid, "title": entry.get("title") or "Untitled"})
    return out

def get_top() -> list[dict]:
    if r:
        try:
            cached = r.get(_CACHE_KEY)
            if cached:
                return json.loads(cached)
        except Exception:
            pass
    else:
        if _mem["data"] and time.time() - _mem["ts"] < _CACHE_TTL:
            return _mem["data"]
    
    data = _fetch()
    if data:
        if r:
            try:
                r.setex(_CACHE_KEY, _CACHE_TTL, json.dumps(data, ensure_ascii=False))
            except Exception:
                pass
        else:
            _mem["data"] = data
            _mem["ts"] = time.time()
    return data
