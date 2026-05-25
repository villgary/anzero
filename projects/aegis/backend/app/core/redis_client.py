import redis.asyncio as redis
from typing import Any, Optional

class RedisClient:
    def __init__(self, url: str):
        self.url = url
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        self.client = redis.from_url(self.url, decode_responses=True)

    async def disconnect(self):
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[str]:
        if not self.client:
            raise RuntimeError("Client not connected")
        return await self.client.get(key)

    async def set(self, key: str, value: Any, ex: Optional[int] = None):
        if not self.client:
            raise RuntimeError("Client not connected")
        await self.client.set(key, value, ex=ex)

    async def incr(self, key: str) -> int:
        if not self.client:
            raise RuntimeError("Client not connected")
        return await self.client.incr(key)
