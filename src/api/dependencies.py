from __future__ import annotations

from functools import lru_cache

from src.core.prism_kernel import PrismKernel
from src.database import async_session_maker
from src.services.analysis_service import AnalysisService
from src.services.portfolio_service import PortfolioService
from src.services.progress_hub import ProgressHub
from src.services.task_store import TaskStore


@lru_cache(maxsize=1)
def get_progress_hub() -> ProgressHub:
    return ProgressHub()


@lru_cache(maxsize=1)
def get_task_store() -> TaskStore:
    return TaskStore()


@lru_cache(maxsize=1)
def get_prism_kernel() -> PrismKernel:
    return PrismKernel()


@lru_cache(maxsize=1)
def get_portfolio_service() -> PortfolioService:
    return PortfolioService()


@lru_cache(maxsize=1)
def get_analysis_service() -> AnalysisService:
    return AnalysisService(
        session_maker=async_session_maker,
        kernel=get_prism_kernel(),
        progress_hub=get_progress_hub(),
        task_store=get_task_store(),
    )
