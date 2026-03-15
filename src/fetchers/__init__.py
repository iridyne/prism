from abc import ABC, abstractmethod
from typing import Any
import httpx
from loguru import logger


class BaseFetcher(ABC):
    """Base class for all data fetchers"""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    @abstractmethod
    async def fetch(self, **kwargs) -> dict[str, Any]:
        """Fetch data from source"""
        pass

    async def close(self):
        await self.client.aclose()
