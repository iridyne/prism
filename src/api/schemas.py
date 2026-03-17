from __future__ import annotations

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator


class PositionInput(BaseModel):
    code: str = Field(..., min_length=1, description="Fund code")
    allocation: float = Field(..., gt=0, le=1, description="Allocation ratio 0-1")


class PreferencesInput(BaseModel):
    risk_level: Literal["low", "medium", "high"] = "medium"
    horizon_months: int = Field(12, ge=1, le=360)
    target_return: float | None = None


class PortfolioCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    positions: list[PositionInput] = Field(..., min_length=1)
    preferences: PreferencesInput

    @model_validator(mode="after")
    def validate_allocations(self) -> "PortfolioCreate":
        total = sum(p.allocation for p in self.positions)
        if abs(total - 1.0) > 0.001:
            raise ValueError("positions allocations must sum to 1.0 (+/- 0.001)")

        codes = [p.code for p in self.positions]
        if len(codes) != len(set(codes)):
            raise ValueError("positions fund code must be unique")
        return self


class PortfolioOut(BaseModel):
    id: str
    name: str
    positions: list[dict[str, Any]]
    preferences: dict[str, Any]
    status: str
    created_at: datetime


class AnalysisTaskResponse(BaseModel):
    task_id: str
    status: str


class TaskStatusResponse(BaseModel):
    task_id: str
    portfolio_id: str
    status: str
    progress: int
    message: str
    timestamp: datetime
    error: str | None = None


class AnalysisResultOut(BaseModel):
    portfolio_id: str
    overall_score: int | None
    summary: str | None
    recommendations: list[str]
    correlation_warnings: list[str]
    backtest_metrics: dict[str, Any]
    agent_insights: list[dict[str, Any]]
    created_at: datetime
