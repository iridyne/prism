import pandas as pd
from typing import Any
from loguru import logger


class Normalizer:
    """Data normalization and standardization"""

    @staticmethod
    def normalize_fund_data(raw_data: dict[str, Any]) -> pd.DataFrame:
        """Normalize fund data to standard format"""
        logger.info("Normalizing fund data")

        # TODO: Implement normalization logic
        df = pd.DataFrame(raw_data.get("funds", {})).T
        return df

    @staticmethod
    def normalize_market_data(raw_data: dict[str, Any]) -> pd.DataFrame:
        """Normalize market data to standard format"""
        logger.info("Normalizing market data")

        df = pd.DataFrame(raw_data.get("markets", {})).T
        return df

    @staticmethod
    def handle_missing_values(df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in dataframe"""
        # Forward fill then backward fill
        return df.ffill().bfill()
