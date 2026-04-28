import redis
import os
import logging
from config import REDIS_URL

try:
    r = redis.from_url(REDIS_URL, decode_responses=True)
except Exception as e:
    logging.error(f"Redis connection error: {e}")
    r = None

def get_cache(key):
    if not r: return None
    try:
        return r.get(key)
    except Exception as e:
        logging.error(f"Redis get error: {e}")
        return None

def set_cache(key, value, ex=3600):
    if not r: return
    try:
        r.set(key, value, ex=ex)
    except Exception as e:
        logging.error(f"Redis set error: {e}")

def is_premium(user_id):
    if not r: return False
    try:
        return r.get(f"premium:{user_id}") == "1"
    except:
        return False

def set_premium(user_id):
    if not r: return
    try:
        r.set(f"premium:{user_id}", "1")
    except:
        pass
