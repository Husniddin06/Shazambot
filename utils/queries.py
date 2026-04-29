"""Top user search queries (for admin analytics)."""
from utils.redis_cache import r

_mem: dict[str, int] = {}

def record(query: str) -> None:
    q = (query or "").strip().lower()[:80]
    if not q:
        return
    if r:
        try:
            r.zincrby("stats:queries", 1, q)
            return
        except Exception:
            pass
    _mem[q] = _mem.get(q, 0) + 1

def top(n: int = 10) -> list[tuple[str, int]]:
    if r:
        try:
            raw = r.zrevrange("stats:queries", 0, n - 1, withscores=True) or []
            return [(q, int(s)) for q, s in raw]
        except Exception:
            pass
    items = sorted(_mem.items(), key=lambda kv: -kv[1])[:n]
    return items
