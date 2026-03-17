from abc import ABC, abstractmethod
from typing import Any

from langchain_anthropic import ChatAnthropic
from loguru import logger

from src.config import settings


class BaseAgent(ABC):
    """Abstract base class for all agents"""

    def __init__(self, name: str, model: str = "claude-sonnet-4-6", temperature: float = 0.2):
        self.name = name
        self.llm = ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=settings.anthropic_api_key
        )
        logger.info(f"Initialized agent: {name}")

    @abstractmethod
    async def analyze(self, data: dict[str, Any]) -> dict[str, Any]:
        """
        Analyze data and return findings

        Returns:
            dict with keys: analysis, confidence (0-1), reasoning
        """
        pass
