from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_analysis_service, get_portfolio_service
from src.api.schemas import AnalysisTaskResponse, PortfolioCreate, PortfolioOut
from src.database import get_db
from src.services.analysis_service import AnalysisService
from src.services.portfolio_service import PortfolioService

router = APIRouter(prefix="/api/portfolios", tags=["portfolios"])


@router.post("", response_model=PortfolioOut, status_code=status.HTTP_201_CREATED)
async def create_portfolio(
    payload: PortfolioCreate,
    db: AsyncSession = Depends(get_db),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    portfolio = await portfolio_service.create(db, payload)
    return PortfolioOut(
        id=portfolio.id,
        name=portfolio.name,
        positions=portfolio.positions or [],
        preferences=portfolio.preferences or {},
        status=portfolio.status,
        created_at=portfolio.created_at,
    )


@router.get("", response_model=list[PortfolioOut])
async def list_portfolios(
    db: AsyncSession = Depends(get_db),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    portfolios = await portfolio_service.list_all(db)
    return [
        PortfolioOut(
            id=p.id,
            name=p.name,
            positions=p.positions or [],
            preferences=p.preferences or {},
            status=p.status,
            created_at=p.created_at,
        )
        for p in portfolios
    ]


@router.get("/{portfolio_id}", response_model=PortfolioOut)
async def get_portfolio(
    portfolio_id: str,
    db: AsyncSession = Depends(get_db),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
):
    portfolio = await portfolio_service.get_or_none(db, portfolio_id)
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return PortfolioOut(
        id=portfolio.id,
        name=portfolio.name,
        positions=portfolio.positions or [],
        preferences=portfolio.preferences or {},
        status=portfolio.status,
        created_at=portfolio.created_at,
    )


@router.post("/{portfolio_id}/analyze", response_model=AnalysisTaskResponse)
async def run_analysis(
    portfolio_id: str,
    db: AsyncSession = Depends(get_db),
    portfolio_service: PortfolioService = Depends(get_portfolio_service),
    analysis_service: AnalysisService = Depends(get_analysis_service),
):
    portfolio = await portfolio_service.get_or_none(db, portfolio_id)
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    task_id = await analysis_service.start_analysis(portfolio_id)
    return AnalysisTaskResponse(task_id=task_id, status="queued")
