from typing import Any

from loguru import logger

from src.reasoning.cot_engine import COTEngine


class RecommendationEngine:
    """Generate actionable portfolio recommendations"""

    def __init__(self):
        self.cot_engine = COTEngine()
        logger.info("Initialized Recommendation Engine")

    async def generate(
        self,
        portfolio_analysis: dict[str, Any],
        agent_results: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """
        Generate recommendations from portfolio analysis and agent insights

        Args:
            portfolio_analysis: Portfolio metrics
            agent_results: Agent analysis results

        Returns:
            Structured recommendations with reasoning
        """
        logger.info("Generating recommendations")

        # Generate COT reasoning
        cot_result = await self.cot_engine.generate_reasoning(agent_results)

        # Aggregate confidence scores
        avg_confidence = sum(r['confidence'] for r in agent_results) / len(agent_results)

        # Build recommendation
        recommendation = {
            "summary": f"Portfolio analysis complete. Total value: ¥{portfolio_analysis['total_value']:,.2f}, Return: {portfolio_analysis['total_return_pct']:.2f}%",
            "portfolio_metrics": portfolio_analysis,
            "agent_insights": agent_results,
            "reasoning_chain": cot_result['reasoning_chain'],
            "confidence": round(avg_confidence, 2),
            "actions": self._generate_actions(portfolio_analysis, agent_results)
        }

        return recommendation

    def _generate_actions(
        self,
        portfolio: dict[str, Any],
        agents: list[dict[str, Any]]
    ) -> list[str]:
        """Generate actionable recommendations"""
        actions = []

        # Simple rule-based actions
        if portfolio['total_return_pct'] < -10:
            actions.append("Consider reviewing underperforming positions")

        if portfolio['volatility'] > 20:
            actions.append("High volatility detected - consider risk management")

        # Add agent-specific insights
        for agent in agents:
            if agent['confidence'] > 0.8:
                actions.append(f"High confidence insight from {agent['agent']}")

        return actions if actions else ["Hold current positions"]
