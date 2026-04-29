"""Per-user favorites (starred songs)."""
import json
import logging
from utils.redis_cache import r

logger = logging.getLogger(__name__)

MAX_FAVORITES = 50
_mem: dict[int, dict[str, dict]] = {}

def _key(uid: int) -> str:
    return f"fav:{uid}"

def add(uid: int, video_id: str, title: str) -> bool:
    item = {"video_id": video_id, "title": title[:200]}
    payload = json.dumps(item, ensure_ascii=False)
    if r:
        try:
            existing = r.hget(_key(uid), video_id)
            if existing:
                return False
            count = r.hlen(_key(uid)) or 0
            if count >= MAX_FAVORITES:
                return False
            r.hset(_key(uid), video_id, payload)
            return True
        except Exception as e:
            logger.warning(f"favorites redis error: {e}")
    
    bucket = _mem.setdefault(uid, {})
    if video_id in bucket or len(bucket) >= MAX_FAVORITES:
        return False
    bucket[video_id] = item
    return True

def remove(uid: int, video_id: str) -> bool:
    if r:
        try:
            return bool(r.hdel(_key(uid), video_id))
        except Exception:
            pass
    return _mem.get(uid, {}).pop(video_id, None) is not None

def list_all(uid: int) -> list[dict]:
    if r:
        try:
            raw = r.hvals(_key(uid)) or []
            out = []
            for s in raw:
                try:
                    out.append(json.loads(s))
                except Exception:
                    pass
            return out
        except Exception:
            pass
    return list(_mem.get(uid, {}).values())

def has(uid: int, video_id: str) -> bool:
    if r:
        try:
            return bool(r.hexists(_key(uid), video_id))
        except Exception:
            pass
    return video_id in _mem.get(uid, {})

def count(uid: int) -> int:
    if r:
        try:
            return int(r.hlen(_key(uid)) or 0)
        except Exception:
            pass
    return len(_mem.get(uid, {}))
