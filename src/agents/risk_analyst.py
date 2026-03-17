from typing import Any

from loguru import logger

from .base_agent import BaseAgent


class RiskAnalyst(BaseAgent):
    """Analyzes portfolio risk and correlation"""

    def __init__(self):
        super().__init__(
            name="RiskAnalyst",
            model="claude-sonnet-4-6",
            temperature=0.2
        )

    async def analyze(self, data: dict[str, Any]) -> dict[str, Any]:
        logger.info("Analyzing portfolio risk")

        prompt = f"""Analyze risk factors for the following portfolio:

{data}

Provide:
1. Concentration risk assessment
2. Correlation analysis
3. Downside risk metrics
4. Risk mitigation recommendations

Be concise."""

        response = await self.llm.ainvoke(prompt)

        return {
            "agent": self.name,
            "analysis": response.content,
            "confidence": 0.80,
            "reasoning": "Based on portfolio composition and risk metrics"
        }
