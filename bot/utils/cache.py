import redis.asyncio as redis
import json
import os

class CacheService:
    def __init__(self, redis_url=None):
        self.redis_url = redis_url or os.getenv('REDIS_URL', 'redis://localhost:6379')
        self.client = None

    async def connect(self):
        if not self.client:
            self.client = await redis.from_url(self.redis_url, decode_responses=True)

    async def get(self, key):
        await self.connect()
        data = await self.client.get(key)
        return json.loads(data) if data else None

    async def set(self, key, value, expire=3600):
        await self.connect()
        await self.client.set(key, json.dumps(value), ex=expire)

    async def close(self):
        if self.client:
            await self.client.close()
