import redis.asyncio as redis
import json
import os
import logging

class CacheService:
    def __init__(self, redis_url=None):
        self.redis_url = redis_url or os.getenv('REDIS_URL')
        self.client = None
        self.is_active = False

    async def connect(self):
        if not self.redis_url:
            self.is_active = False
            return
        
        if not self.client:
            try:
                self.client = await redis.from_url(self.redis_url, decode_responses=True)
                self.is_active = True
            except Exception as e:
                logging.warning(f"Redis-ga ulanib bo'lmadi: {e}. Keshsiz ishlanmoqda.")
                self.is_active = False

    async def get(self, key):
        if not self.is_active:
            await self.connect()
        
        if not self.is_active:
            return None
            
        try:
            data = await self.client.get(key)
            return json.loads(data) if data else None
        except:
            return None

    async def set(self, key, value, expire=3600):
        if not self.is_active:
            await self.connect()
            
        if not self.is_active:
            return
            
        try:
            await self.client.set(key, json.dumps(value), ex=expire)
        except:
            pass

    async def close(self):
        if self.client:
            await self.client.close()
