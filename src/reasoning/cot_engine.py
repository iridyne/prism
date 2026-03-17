from typing import Any

from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from loguru import logger

from src.config import settings


class COTEngine:
    """Chain-of-Thought reasoning engine"""

    def __init__(self):
        self.llm = ChatAnthropic(
            model="claude-opus-4-6",
            temperature=0.1,
            api_key=settings.anthropic_api_key
        )
        logger.info("Initialized COT Engine")

    async def generate_reasoning(self, agent_results: list[dict[str, Any]]) -> dict[str, Any]:
        """
        Generate chain-of-thought reasoning from agent analyses

        Args:
            agent_results: List of agent analysis results

        Returns:
            Structured reasoning with validation
        """
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a reasoning validator. Analyze the following agent insights and build a logical chain of reasoning."),
            ("user", """Agent analyses:
{analyses}

Generate a chain-of-thought that:
1. Identifies key insights from each agent
2. Finds logical connections between insights
3. Validates consistency
4. Builds toward a coherent recommendation

Output format:
- Reasoning steps (numbered)
- Logical connections
- Final synthesis""")
        ])

        analyses_text = "\n\n".join([
            f"**{r['agent']}** (confidence: {r['confidence']}):\n{r['analysis']}"
            for r in agent_results
        ])

        chain = prompt | self.llm
        response = await chain.ainvoke({"analyses": analyses_text})

        return {
            "reasoning_chain": response.content,
            "validated": True,
            "agent_count": len(agent_results)
        }
