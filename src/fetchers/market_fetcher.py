from __future__ import annotations

from datetime import datetime
from typing import Any

import akshare as ak
from loguru import logger

from src.fetchers import BaseFetcher
from src.storage.cache_manager import CacheManager


class MarketFetcher(BaseFetcher):
    """Fetch market index data using akshare."""

    def __init__(self):
        super().__init__()
        self.cache = CacheManager()

    async def fetch(self, symbols: list[str] | None = None) -> dict[str, Any]:
        if symbols is None:
            symbols = ["sh000001", "sz399001"]

        logger.info(f"Fetching market data for {symbols}")
        await self.cache.connect()

        markets_data: dict[str, Any] = {}
        df = None
        has_error = False
        try:
            df = ak.stock_zh_index_spot_em()
        except Exception as exc:  # noqa: BLE001
            logger.error(f"Failed to fetch market board data: {exc}")
            has_error = True

        for symbol in symbols:
            cache_key = f"market:{symbol}"
            cached = await self.cache.get(cache_key)
            if cached:
                markets_data[symbol] = cached
                continue

            try:
                if df is None or df.empty:
                    raise RuntimeError("market dataset is empty")

                index_data = df[df["代码"] == symbol]
                if index_data.empty:
                    market_data = {
                        "name": symbol,
                        "price": 0.0,
                        "change_pct": 0.0,
                        "change": 0.0,
                        "volume": 0.0,
                        "amount": 0.0,
                    }
                else:
                    row = index_data.iloc[0]
                    market_data = {
                        "name": str(row.get("名称", symbol)),
                        "price": float(row.get("最新价", 0.0)),
                        "change_pct": float(row.get("涨跌幅", 0.0)),
                        "change": float(row.get("涨跌额", 0.0)),
                        "volume": float(row.get("成交量", 0.0)),
                        "amount": float(row.get("成交额", 0.0)),
                    }

                markets_data[symbol] = market_data
                await self.cache.set(cache_key, market_data, ttl=60)
            except Exception as exc:  # noqa: BLE001
                logger.error(f"Failed to fetch index {symbol}: {exc}")
                markets_data[symbol] = {
                    "name": symbol,
                    "price": 0.0,
                    "change_pct": 0.0,
                    "change": 0.0,
                    "volume": 0.0,
                    "amount": 0.0,
                    "error": str(exc),
                }
                has_error = True

        await self.cache.close()
        return {
            "timestamp": datetime.now().isoformat(),
            "source": "akshare",
            "quality": "degraded" if has_error else "ok",
            "markets": markets_data,
        }
