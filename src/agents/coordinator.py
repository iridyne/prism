import asyncio
from typing import Any

from langgraph.graph import END, StateGraph
from loguru import logger

from .base_agent import BaseAgent
from .communication.message_bus import AgentState


class Coordinator:
    """Orchestrates multi-agent collaboration"""

    def __init__(self, agents: list[BaseAgent]):
        self.agents = {agent.name: agent for agent in agents}
        self.graph = StateGraph(AgentState)
        self._build_graph()
        logger.info(f"Coordinator initialized with {len(agents)} agents")

    def _build_graph(self):
        """Build the agent execution graph"""

        async def run_agents(state: AgentState) -> AgentState:
            """Run all agents in parallel"""
            results = await asyncio.gather(
                *[agent.analyze(state["input_data"]) for agent in self.agents.values()]
            )
            state["agent_results"] = results
            return state

        async def aggregate_results(state: AgentState) -> AgentState:
            """Aggregate agent results into final recommendation"""
            results = state["agent_results"]

            avg_confidence = sum(r["confidence"] for r in results) / len(results)
            combined_analysis = "\n\n".join([
                f"**{r['agent']}** (confidence: {r['confidence']:.2f}):\n{r['analysis']}"
                for r in results
            ])

            state["final_recommendation"] = {
                "recommendation": combined_analysis,
                "confidence": avg_confidence,
                "agent_count": len(results)
            }
            return state

        self.graph.add_node("run_agents", run_agents)
        self.graph.add_node("aggregate", aggregate_results)

        self.graph.set_entry_point("run_agents")
        self.graph.add_edge("run_agents", "aggregate")
        self.graph.add_edge("aggregate", END)

        self.workflow = self.graph.compile()

    async def analyze(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Run multi-agent analysis

        Args:
            data: Input data for analysis

        Returns:
            Final recommendation with aggregated insights
        """
        logger.info("Starting multi-agent analysis")

        initial_state: AgentState = {
            "input_data": data,
            "agent_results": [],
            "final_recommendation": None
        }

        final_state = await self.workflow.ainvoke(initial_state)
        return final_state["final_recommendation"]
