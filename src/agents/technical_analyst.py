from typing import Any

from loguru import logger

from .base_agent import BaseAgent


class TechnicalAnalyst(BaseAgent):
    """Analyzes technical indicators and price trends"""

    def __init__(self):
        super().__init__(
            name="TechnicalAnalyst",
            model="claude-sonnet-4-6",
            temperature=0.2
        )

    async def analyze(self, data: dict[str, Any]) -> dict[str, Any]:
        logger.info("Analyzing technical indicators")

        prompt = f"""Analyze technical indicators for the following data:

{data}

Provide:
1. Trend analysis (bullish/bearish/neutral)
2. Key support/resistance levels
3. Momentum indicators
4. Trading signals

Be concise."""

        response = await self.llm.ainvoke(prompt)

        return {
            "agent": self.name,
            "analysis": response.content,
            "confidence": 0.70,
            "reasoning": "Based on technical indicators and price action"
        }
