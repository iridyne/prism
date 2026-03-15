import redis.asyncio as redis
from typing import Any
import json
from loguru import logger
from src.config import settings


class CacheManager:
    """Redis-based cache manager"""

    def __init__(self):
        self.redis: redis.Redis | None = None

    async def connect(self):
        """Connect to Redis"""
        self.redis = await redis.from_url(settings.redis_url)
        logger.info("Connected to Redis")

    async def get(self, key: str) -> Any | None:
        """Get value from cache"""
        if not self.redis:
            return None

        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int = 300):
        """Set value in cache with TTL (seconds)"""
        if not self.redis:
            return

        await self.redis.setex(key, ttl, json.dumps(value))

    async def close(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.aclose()
