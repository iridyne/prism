from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

import httpx


class BaseFetcher(ABC):
    """Base class for all data fetchers."""

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    @abstractmethod
    async def fetch(self, *args, **kwargs) -> dict[str, Any]:
        raise NotImplementedError

    async def close(self):
        await self.client.aclose()
