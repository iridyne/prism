from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String

from src.database import Base


class AnalysisResult(Base):
    __tablename__ = "analysis_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)

    # MVP result fields
    overall_score = Column(Integer, nullable=True)
    recommendations = Column(JSON, nullable=True)
    correlation_warnings = Column(JSON, nullable=True)
    backtest_metrics = Column(JSON, nullable=True)
    summary = Column(String, nullable=True)
    agent_insights = Column(JSON, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Legacy compatibility fields kept nullable.
    timestamp = Column(DateTime, nullable=True)
    trigger_reason = Column(String, nullable=True)
    reasoning_chain = Column(JSON, nullable=True)
    confidence_score = Column(Float, nullable=True)


class PortfolioSnapshot(Base):
    __tablename__ = "portfolio_snapshots"

    id = Column(String, primary_key=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    total_value = Column(Float, nullable=True)
    daily_return = Column(Float, nullable=True)
    metrics = Column(JSON, nullable=True)
