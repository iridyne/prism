from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies import get_analysis_service
from src.api.schemas import AnalysisResultOut
from src.database import get_db
from src.services.analysis_service import AnalysisService

router = APIRouter(prefix="/api/portfolios", tags=["analysis"])


@router.get("/{portfolio_id}/analysis", response_model=AnalysisResultOut)
async def get_latest_analysis(
    portfolio_id: str,
    db: AsyncSession = Depends(get_db),
    analysis_service: AnalysisService = Depends(get_analysis_service),
):
    analysis = await analysis_service.get_latest_analysis(db, portfolio_id)
    if analysis is None:
        raise HTTPException(status_code=404, detail="No analysis found")

    return AnalysisResultOut(
        portfolio_id=analysis.portfolio_id,
        overall_score=analysis.overall_score,
        summary=analysis.summary,
        recommendations=analysis.recommendations or [],
        correlation_warnings=analysis.correlation_warnings or [],
        backtest_metrics=analysis.backtest_metrics or {},
        agent_insights=analysis.agent_insights or [],
        created_at=analysis.created_at,
    )
