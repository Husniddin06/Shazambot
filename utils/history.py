"""Per-user download history (most recent N items)."""
import json
import logging
from utils.redis_cache import r

logger = logging.getLogger(__name__)

MAX_HISTORY = 20
_mem: dict[int, list[dict]] = {}

def _key(uid: int) -> str:
    return f"hist:{uid}"

def add(uid: int, video_id: str, title: str, want_mp3: bool) -> None:
    item = {
        "video_id": video_id,
        "title": title[:200],
        "kind": "mp3" if want_mp3 else "video",
    }
    payload = json.dumps(item, ensure_ascii=False)
    if r:
        try:
            pipe = r.pipeline()
            pipe.lpush(_key(uid), payload)
            pipe.ltrim(_key(uid), 0, MAX_HISTORY - 1)
            pipe.execute()
            return
        except Exception as e:
            logger.warning(f"history redis error: {e}")
    
    lst = _mem.setdefault(uid, [])
    lst.insert(0, item)
    del lst[MAX_HISTORY:]

def get(uid: int) -> list[dict]:
    if r:
        try:
            raw = r.lrange(_key(uid), 0, MAX_HISTORY - 1) or []
            out = []
            for s in raw:
                try:
                    out.append(json.loads(s))
                except Exception:
                    pass
            return out
        except Exception as e:
            logger.warning(f"history redis get error: {e}")
    return list(_mem.get(uid, []))

def clear(uid: int) -> None:
    if r:
        try:
            r.delete(_key(uid))
        except Exception:
            pass
    _mem.pop(uid, None)
