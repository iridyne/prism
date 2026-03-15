from typing import Any
from datetime import datetime
from . import BaseFetcher
from loguru import logger
import akshare as ak


class MarketFetcher(BaseFetcher):
    """Fetch market indices data using akshare"""

    async def fetch(self, symbols: list[str] | None = None) -> dict[str, Any]:
        """
        Fetch market index data

        Args:
            symbols: List of index codes (e.g., ['sh000001', 'sz399001'])
        """
        if symbols is None:
            symbols = ['sh000001', 'sz399001']  # Shanghai Composite, Shenzhen Component

        logger.info(f"Fetching market data for {symbols}")

        markets_data = {}
        for symbol in symbols:
            try:
                df = ak.stock_zh_index_spot_em()
                index_data = df[df["代码"] == symbol]
                if not index_data.empty:
                    row = index_data.iloc[0]
                    markets_data[symbol] = {
                        "name": row["名称"],
                        "price": float(row["最新价"]),
                        "change_pct": float(row["涨跌幅"]),
                        "change": float(row["涨跌额"]),
                        "volume": float(row["成交量"]),
                        "amount": float(row["成交额"])
                    }
            except Exception as e:
                logger.error(f"Failed to fetch index {symbol}: {e}")
                markets_data[symbol] = {"error": str(e)}

        return {
            "timestamp": datetime.now().isoformat(),
            "markets": markets_data
        }
