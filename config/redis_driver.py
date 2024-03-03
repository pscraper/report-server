import aioredis


class RedisDriver:
    def __init__(self):
        self.redis_url = "redis://127.0.0.1:6379"
        self.redis_client = aioredis.from_url(self.redis_url)

    async def set_key(self, key, val, ttl = 3600):
        await self.redis_client.set(key, val)
        if ttl:
            await self.redis_client.expire(key, ttl)
        return True
    
    async def get_key(self, key):
        return await self.redis_client.get(key)
    
    async def del_key(self, key):
        return await self.redis_client.delete(key)
    