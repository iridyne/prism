from __future__ import annotations

from datetime import datetime
from typing import Any

import akshare as ak
from loguru import logger

from src.fetchers import BaseFetcher
from src.storage.cache_manager import CacheManager


class FundFetcher(BaseFetcher):
    """Fetch domestic fund data using akshare."""

    def __init__(self):
        super().__init__()
        self.cache = CacheManager()

    async def fetch(self, fund_codes: str | list[str]) -> dict[str, Any]:
        if isinstance(fund_codes, str):
            codes = [fund_codes]
        else:
            codes = list(fund_codes)

        logger.info(f"Fetching data for {len(codes)} funds")
        await self.cache.connect()

        funds_data: dict[str, Any] = {}
        has_error = False
        for code in codes:
            cache_key = f"fund:{code}"
            cached = await self.cache.get(cache_key)
            if cached:
                funds_data[code] = cached
                continue

            try:
                df = ak.fund_open_fund_info_em(fund=code, indicator="单位净值走势")
                if df is None or df.empty:
                    funds_data[code] = {"name": code, "nav": 0.0, "change": 0.0}
                    continue

                latest = df.iloc[-1]
                fund_data = {
                    "name": code,
                    "nav": float(latest.get("单位净值", 0.0)),
                    "date": str(latest.get("净值日期", "")),
                    "change": float(latest.get("日增长率", 0.0)) if "日增长率" in latest else 0.0,
                }
                funds_data[code] = fund_data
                await self.cache.set(cache_key, fund_data, ttl=300)
            except Exception as exc:  # noqa: BLE001
                logger.error(f"Failed to fetch fund {code}: {exc}")
                funds_data[code] = {"name": code, "nav": 0.0, "change": 0.0, "error": str(exc)}
                has_error = True

        await self.cache.close()
        return {
            "timestamp": datetime.now().isoformat(),
            "source": "akshare",
            "quality": "degraded" if has_error else "ok",
            "funds": funds_data,
        }
