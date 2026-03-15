from typing import Any
from datetime import datetime
from . import BaseFetcher
from loguru import logger
import akshare as ak
import pandas as pd


class FundFetcher(BaseFetcher):
    """Fetch domestic fund data using akshare"""

    async def fetch(self, fund_codes: list[str]) -> dict[str, Any]:
        """
        Fetch fund information

        Args:
            fund_codes: List of fund codes
        """
        logger.info(f"Fetching data for {len(fund_codes)} funds")

        funds_data = {}
        for code in fund_codes:
            try:
                # Get fund net value
                df = ak.fund_open_fund_info_em(fund=code, indicator="单位净值走势")
                if not df.empty:
                    latest = df.iloc[-1]
                    funds_data[code] = {
                        "name": code,
                        "nav": float(latest["单位净值"]),
                        "date": latest["净值日期"],
                        "change": float(latest.get("日增长率", 0.0)) if "日增长率" in latest else 0.0
                    }
            except Exception as e:
                logger.error(f"Failed to fetch fund {code}: {e}")
                funds_data[code] = {"error": str(e)}

        return {
            "timestamp": datetime.now().isoformat(),
            "funds": funds_data
        }
