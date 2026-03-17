from __future__ import annotations

import asyncio
from datetime import datetime
from uuid import uuid4

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from src.core.prism_kernel import PrismKernel
from src.models import AnalysisResult, Portfolio
from src.services.progress_hub import ProgressHub
from src.services.task_store import TaskState, TaskStore


class AnalysisService:
    def __init__(
        self,
        *,
        session_maker: async_sessionmaker[AsyncSession],
        kernel: PrismKernel,
        progress_hub: ProgressHub,
        task_store: TaskStore,
    ) -> None:
        self._session_maker = session_maker
        self._kernel = kernel
        self._progress_hub = progress_hub
        self._task_store = task_store

    async def start_analysis(self, portfolio_id: str) -> str:
        task_id = f"task_{uuid4().hex[:12]}"
        initial_state = TaskState(
            task_id=task_id,
            portfolio_id=portfolio_id,
            status="queued",
            progress=0,
            message="Task queued",
            timestamp=datetime.utcnow(),
        )
        await self._task_store.put(initial_state)
        asyncio.create_task(self._run_analysis(task_id=task_id, portfolio_id=portfolio_id))
        return task_id

    async def get_task(self, task_id: str) -> TaskState | None:
        return await self._task_store.get(task_id)

    async def get_latest_analysis(
        self, db: AsyncSession, portfolio_id: str
    ) -> AnalysisResult | None:
        result = await db.execute(
            select(AnalysisResult)
            .where(AnalysisResult.portfolio_id == portfolio_id)
            .order_by(desc(AnalysisResult.created_at))
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def _emit(self, task_id: str, payload: dict) -> None:
        await self._progress_hub.publish(task_id, payload)

    async def _update_state(
        self,
        task_id: str,
        *,
        status: str | None = None,
        progress: int | None = None,
        message: str | None = None,
        error: str | None = None,
    ) -> None:
        state = await self._task_store.update(
            task_id,
            status=status,
            progress=progress,
            message=message,
            error=error,
        )
        if state is None:
            return
        await self._emit(
            task_id,
            {
                "task_id": state.task_id,
                "portfolio_id": state.portfolio_id,
                "status": state.status,
                "progress": state.progress,
                "message": state.message,
                "timestamp": state.timestamp.isoformat(),
                "error": state.error,
            },
        )

    async def _run_analysis(self, *, task_id: str, portfolio_id: str) -> None:
        await self._update_state(
            task_id,
            status="running",
            progress=5,
            message="Starting analysis",
        )

        try:
            async with self._session_maker() as db:
                result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
                portfolio = result.scalar_one_or_none()
                if portfolio is None:
                    await self._update_state(
                        task_id,
                        status="failed",
                        progress=100,
                        message="Portfolio not found",
                        error="portfolio_not_found",
                    )
                    return

                portfolio.status = "analyzing"
                await db.commit()

                if not portfolio.positions:
                    portfolio.status = "pending_analysis"
                    await db.commit()
                    await self._update_state(
                        task_id,
                        status="failed",
                        progress=100,
                        message="Portfolio has no positions",
                        error="empty_positions",
                    )
                    return

                async def progress_cb(progress: int, message: str) -> None:
                    await self._update_state(
                        task_id,
                        status="running",
                        progress=progress,
                        message=message,
                    )

                analysis = await self._kernel.analyze(
                    positions=portfolio.positions,
                    preferences=portfolio.preferences or {},
                    progress_cb=progress_cb,
                )

                existing_result = await self.get_latest_analysis(db, portfolio_id)
                if existing_result is None:
                    existing_result = AnalysisResult(portfolio_id=portfolio_id)
                    db.add(existing_result)

                existing_result.overall_score = analysis["overall_score"]
                existing_result.summary = analysis["summary"]
                existing_result.recommendations = analysis["recommendations"]
                existing_result.correlation_warnings = analysis["correlation_warnings"]
                existing_result.backtest_metrics = analysis["backtest_metrics"]
                existing_result.agent_insights = analysis["agent_insights"]
                existing_result.created_at = datetime.utcnow()

                portfolio.status = "active"
                await db.commit()

            await self._update_state(
                task_id,
                status="completed",
                progress=100,
                message="Analysis complete",
            )

        except Exception as exc:  # noqa: BLE001
            async with self._session_maker() as db:
                result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
                portfolio = result.scalar_one_or_none()
                if portfolio is not None:
                    portfolio.status = "pending_analysis"
                    await db.commit()
            await self._update_state(
                task_id,
                status="failed",
                progress=100,
                message="Analysis failed",
                error=str(exc),
            )
