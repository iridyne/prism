from typing import Any, TypedDict

from langgraph.graph import StateGraph
from loguru import logger


class AgentState(TypedDict):
    """State shared across agents"""
    input_data: dict[str, Any]
    agent_results: list[dict[str, Any]]
    final_recommendation: dict[str, Any] | None


class MessageBus:
    """Manages inter-agent communication using LangGraph"""

    def __init__(self):
        self.graph = StateGraph(AgentState)
        logger.info("Initialized MessageBus")

    def add_agent_node(self, name: str, agent_func):
        """Add an agent as a node in the graph"""
        self.graph.add_node(name, agent_func)

    def build(self):
        """Build the execution graph"""
        return self.graph.compile()
