from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import text
from sqlalchemy.exc import OperationalError, ProgrammingError
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from src.config import settings

engine = create_async_engine(settings.database_url, echo=False)
async_session_maker = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def _safe_add_column(table: str, ddl: str) -> None:
    """Best-effort schema evolution for local SQLite/dev environments."""
    try:
        async with engine.begin() as conn:
            await conn.exec_driver_sql(f"ALTER TABLE {table} ADD COLUMN {ddl}")
    except (OperationalError, ProgrammingError):
        # Column already exists or backend does not allow this statement in current state.
        return


async def init_db() -> None:
    # Ensure known tables exist first.
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Lightweight compatibility migration (works for MVP without forcing alembic step).
    await _safe_add_column("portfolios", "positions JSON")
    await _safe_add_column("portfolios", "preferences JSON")
    await _safe_add_column("portfolios", "status VARCHAR DEFAULT 'pending_analysis'")

    await _safe_add_column("analysis_results", "overall_score INTEGER")
    await _safe_add_column("analysis_results", "recommendations JSON")
    await _safe_add_column("analysis_results", "correlation_warnings JSON")
    await _safe_add_column("analysis_results", "backtest_metrics JSON")
    await _safe_add_column("analysis_results", "summary VARCHAR")
    await _safe_add_column("analysis_results", "agent_insights JSON")

    # A small index helps the latest-analysis query.
    try:
        async with engine.begin() as conn:
            await conn.execute(
                text(
                    "CREATE INDEX IF NOT EXISTS idx_analysis_results_portfolio_created "
                    "ON analysis_results (portfolio_id, created_at DESC)"
                )
            )
    except (OperationalError, ProgrammingError):
        return
