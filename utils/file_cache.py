"""Cache of Telegram file_ids for already-uploaded media."""
import logging
from utils.redis_cache import r

logger = logging.getLogger(__name__)

_AUDIO_KEY = "cache:audio"
_VIDEO_KEY = "cache:video"
_mem_audio: dict[str, str] = {}
_mem_video: dict[str, str] = {}

def _key(want_mp3: bool) -> str:
    return _AUDIO_KEY if want_mp3 else _VIDEO_KEY

def _mem(want_mp3: bool) -> dict[str, str]:
    return _mem_audio if want_mp3 else _mem_video

def get_file_id(video_id: str, want_mp3: bool) -> str | None:
    if not video_id:
        return None
    if r:
        try:
            v = r.hget(_key(want_mp3), video_id)
            if v:
                return v
        except Exception as e:
            logger.warning(f"file_cache redis get error: {e}")
    return _mem(want_mp3).get(video_id)

def set_file_id(video_id: str, want_mp3: bool, file_id: str) -> None:
    if not video_id or not file_id:
        return
    _mem(want_mp3)[video_id] = file_id
    if r:
        try:
            r.hset(_key(want_mp3), video_id, file_id)
        except Exception as e:
            logger.warning(f"file_cache redis set error: {e}")

def cache_size() -> dict[str, int]:
    if r:
        try:
            return {
                "audio": r.hlen(_AUDIO_KEY) or 0,
                "video": r.hlen(_VIDEO_KEY) or 0,
            }
        except Exception:
            pass
    return {"audio": len(_mem_audio), "video": len(_mem_video)}
