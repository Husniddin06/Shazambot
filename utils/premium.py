import logging
from utils.redis_cache import r

logger = logging.getLogger(__name__)

def is_premium(user_id: int) -> bool:
    if not r:
        return False
    try:
        return r.get(f"premium:{user_id}") == "1"
    except Exception as e:
        logger.warning(f"Premium tekshirish xatosi: {e}")
        return False

def set_premium(user_id: int, days: int | None = None):
    if not r:
        return
    key = f"premium:{user_id}"
    try:
        if days:
            r.setex(key, days * 86400, "1")
        else:
            r.set(key, "1")
        r.sadd("users:premium", user_id)
    except Exception as e:
        logger.warning(f"Premium yozish xatosi: {e}")

def track_user(user_id: int):
    if not r:
        return
    try:
        r.sadd("users:all", user_id)
    except Exception:
        pass

def increment_downloads():
    if not r:
        return
    try:
        r.incr("stats:downloads")
    except Exception:
        pass

def get_stats() -> dict:
    if not r:
        return {"users": 0, "premium": 0, "downloads": 0}
    try:
        return {
            "users": r.scard("users:all") or 0,
            "premium": r.scard("users:premium") or 0,
            "downloads": int(r.get("stats:downloads") or 0),
        }
    except Exception:
        return {"users": 0, "premium": 0, "downloads": 0}
