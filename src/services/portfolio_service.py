from __future__ import annotations

from datetime import datetime
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.schemas import PortfolioCreate
from src.models import Portfolio


class PortfolioService:
    async def create(self, db: AsyncSession, payload: PortfolioCreate) -> Portfolio:
        portfolio = Portfolio(
            id=f"pf_{uuid4().hex[:12]}",
            name=payload.name,
            positions=[p.model_dump() for p in payload.positions],
            preferences=payload.preferences.model_dump(),
            status="pending_analysis",
            created_at=datetime.utcnow(),
        )
        db.add(portfolio)
        await db.commit()
        await db.refresh(portfolio)
        return portfolio

    async def list_all(self, db: AsyncSession) -> list[Portfolio]:
        result = await db.execute(select(Portfolio).order_by(Portfolio.created_at.desc()))
        return list(result.scalars().all())

    async def get_or_none(self, db: AsyncSession, portfolio_id: str) -> Portfolio | None:
        result = await db.execute(select(Portfolio).where(Portfolio.id == portfolio_id))
        return result.scalar_one_or_none()
