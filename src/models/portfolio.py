from __future__ import annotations

from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from src.database import Base


class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(String, primary_key=True)
    name = Column(String, nullable=False)

    # New MVP schema for wizard-based portfolio setup.
    positions = Column(JSON, nullable=True)
    preferences = Column(JSON, nullable=True)
    status = Column(String, nullable=False, default="pending_analysis")

    # Legacy field kept for backward compatibility.
    description = Column(String, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    holdings = relationship("Holding", back_populates="portfolio", cascade="all, delete-orphan")


class Holding(Base):
    __tablename__ = "holdings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    portfolio_id = Column(String, ForeignKey("portfolios.id"), nullable=False)
    fund_code = Column(String, nullable=False)
    fund_name = Column(String)
    shares = Column(Float, nullable=False)
    cost_basis = Column(Float, nullable=False)
    purchase_date = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

    portfolio = relationship("Portfolio", back_populates="holdings")
