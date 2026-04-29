"""Daily download limits for free users."""
import logging
from datetime import datetime, timezone, timedelta
from utils.redis_cache import r
from utils.premium import is_premium

logger = logging.getLogger(__name__)

DAILY_LIMIT_FREE = 10
_mem: dict[str, int] = {}

def _today_key(uid: int) -> str:
    today = datetime.now(timezone.utc).strftime("%Y%m%d")
    return f"daily:{uid}:{today}"

def _seconds_until_midnight() -> int:
    now = datetime.now(timezone.utc)
    nxt = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    return max(60, int((nxt - now).total_seconds()))

def used_today(uid: int) -> int:
    if r:
        try:
            return int(r.get(_today_key(uid)) or 0)
        except Exception:
            pass
    return _mem.get(_today_key(uid), 0)

def remaining(uid: int) -> int:
    if is_premium(uid):
        return 999_999
    return max(0, DAILY_LIMIT_FREE - used_today(uid))

def can_download(uid: int) -> bool:
    return remaining(uid) > 0

def record_download(uid: int) -> None:
    if is_premium(uid):
        return
    key = _today_key(uid)
    if r:
        try:
            count = r.incr(key)
            if count == 1:
                r.expire(key, _seconds_until_midnight())
            return
        except Exception as e:
            logger.warning(f"limits redis error: {e}")
    _mem[key] = _mem.get(key, 0) + 1
