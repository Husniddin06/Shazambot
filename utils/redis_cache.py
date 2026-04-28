import redis
import os
from config import REDIS_URL

r = redis.from_url(REDIS_URL, decode_responses=True)

def get_cache(key):
    try:
        return r.get(key)
    except:
        return None

def set_cache(key, value):
    try:
        r.set(key, value, ex=3600)
    except:
        pass
