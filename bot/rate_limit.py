from utils.redis_cache import r, is_premium

async def check_limit(user_id: int, limit: int = 3, window: int = 5) -> bool:
    # Premium foydalanuvchilar uchun limit yo'q
    if is_premium(user_id):
        return True
        
    if not r:
        # Redis bo'lmasa, limit qo'llanilmaydi (yoki xohishga ko'ra boshqa mantiq)
        return True
        
    key = f"rl:{user_id}"
    try:
        count = r.incr(key)
        if count == 1:
            r.expire(key, window)
        return count <= limit
    except:
        return True
