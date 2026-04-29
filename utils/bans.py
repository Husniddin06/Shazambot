"""Banned users management."""
from utils.redis_cache import r

_mem: set[int] = set()

def is_banned(uid: int) -> bool:
    if r:
        try:
            return bool(r.sismember("users:banned", uid))
        except Exception:
            pass
    return uid in _mem

def ban(uid: int) -> None:
    _mem.add(uid)
    if r:
        try:
            r.sadd("users:banned", uid)
        except Exception:
            pass

def unban(uid: int) -> None:
    _mem.discard(uid)
    if r:
        try:
            r.srem("users:banned", uid)
        except Exception:
            pass

def list_banned() -> list[int]:
    if r:
        try:
            return [int(x) for x in (r.smembers("users:banned") or set())]
        except Exception:
            pass
    return list(_mem)
