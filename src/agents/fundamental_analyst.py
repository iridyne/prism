from typing import Any
from .base_agent import BaseAgent
from loguru import logger


class FundamentalAnalyst(BaseAgent):
    """Analyzes fund fundamentals and manager performance"""

    def __init__(self):
        super().__init__(
            name="FundamentalAnalyst",
            model="claude-sonnet-4-6",
            temperature=0.2
        )

    async def analyze(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze fund fundamentals

        Args:
            data: Fund data including NAV, performance, manager info
        """
        logger.info(f"Analyzing fundamentals for {len(data.get('funds', {}))} funds")

        prompt = f"""Analyze the following fund data and provide investment insights:

{data}

Provide:
1. Key strengths and weaknesses
2. Manager performance assessment
3. Risk factors
4. Investment recommendation

Be concise and actionable."""

        response = await self.llm.ainvoke(prompt)

        return {
            "agent": self.name,
            "analysis": response.content,
            "confidence": 0.75,
            "reasoning": "Based on fund fundamentals and historical performance"
        }
