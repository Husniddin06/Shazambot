"""User-selected MP3 quality (kbps)."""
from utils.redis_cache import r

ALLOWED = ("128", "192", "320")
DEFAULT = "192"
_mem: dict[int, str] = {}

def get(uid: int) -> str:
    if r:
        try:
            v = r.get(f"quality:{uid}")
            if v in ALLOWED:
                return v
        except Exception:
            pass
    return _mem.get(uid, DEFAULT)

def set_(uid: int, quality: str) -> bool:
    if quality not in ALLOWED:
        return False
    _mem[uid] = quality
    if r:
        try:
            r.set(f"quality:{uid}", quality)
        except Exception:
            pass
    return True
