from typing import Any
import pandas as pd
import numpy as np
from loguru import logger


class PortfolioAnalyzer:
    """Analyze portfolio holdings and calculate metrics"""

    def analyze(self, holdings: list[dict[str, Any]], market_data: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze portfolio holdings

        Args:
            holdings: List of {fund_code, shares, cost_basis}
            market_data: Current market prices and fund data

        Returns:
            Portfolio metrics and analysis
        """
        logger.info(f"Analyzing portfolio with {len(holdings)} positions")

        df = pd.DataFrame(holdings)

        # Calculate current values
        df['current_price'] = df['fund_code'].map(
            lambda code: market_data.get('funds', {}).get(code, {}).get('nav', 0)
        )
        df['current_value'] = df['shares'] * df['current_price']
        df['cost_value'] = df['shares'] * df['cost_basis']
        df['pnl'] = df['current_value'] - df['cost_value']
        df['return_pct'] = (df['pnl'] / df['cost_value'] * 100).round(2)

        total_value = df['current_value'].sum()
        total_cost = df['cost_value'].sum()
        total_pnl = df['pnl'].sum()
        total_return = (total_pnl / total_cost * 100) if total_cost > 0 else 0

        # Calculate weights
        df['weight'] = (df['current_value'] / total_value * 100).round(2)

        # Risk metrics (simplified)
        returns = df['return_pct'].values
        volatility = np.std(returns) if len(returns) > 1 else 0
        sharpe = (np.mean(returns) / volatility) if volatility > 0 else 0

        return {
            "total_value": round(total_value, 2),
            "total_cost": round(total_cost, 2),
            "total_pnl": round(total_pnl, 2),
            "total_return_pct": round(total_return, 2),
            "volatility": round(volatility, 2),
            "sharpe_ratio": round(sharpe, 2),
            "holdings": df.to_dict('records'),
            "position_count": len(holdings)
        }
