from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

from loguru import logger


class CacheManager:
    """Process-local TTL cache used by fetchers in MVP."""

    _instance: "CacheManager | None" = None
    _cache: dict[str, tuple[Any, datetime]] = {}
    _lock: asyncio.Lock | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def connect(self) -> None:
        # Reserved for future external cache backend (redis/memcached).
        return

    async def close(self) -> None:
        # Reserved for future external cache backend cleanup.
        return

    async def _get_lock(self) -> asyncio.Lock:
        if self._lock is None:
            self._lock = asyncio.Lock()
        return self._lock

    async def get(self, key: str) -> Any | None:
        lock = await self._get_lock()
        async with lock:
            if key not in self._cache:
                return None

            value, expiry = self._cache[key]
            if datetime.now() < expiry:
                logger.debug(f"Cache hit: {key}")
                return value

            del self._cache[key]
            logger.debug(f"Cache expired: {key}")
            return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> None:
        lock = await self._get_lock()
        async with lock:
            expiry = datetime.now() + timedelta(seconds=ttl)
            self._cache[key] = (value, expiry)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")

    async def clear_expired(self) -> None:
        lock = await self._get_lock()
        async with lock:
            now = datetime.now()
            expired = [k for k, (_, exp) in self._cache.items() if now >= exp]
            for key in expired:
                del self._cache[key]
            if expired:
                logger.debug(f"Cleared {len(expired)} expired cache entries")
