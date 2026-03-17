from __future__ import annotations

from fastapi import APIRouter, Query
from loguru import logger

from src.fetchers.fund_fetcher import FundFetcher
from src.fetchers.market_fetcher import MarketFetcher

router = APIRouter(prefix="/api", tags=["data"])

fund_fetcher = FundFetcher()
market_fetcher = MarketFetcher()


@router.get("/funds/search")
async def search_funds(q: str = Query(..., min_length=1)):
    logger.info(f"Searching funds with query: {q}")
    return {"results": [], "query": q}


@router.get("/funds/{code}")
async def get_fund(code: str):
    logger.info(f"Fetching fund data for {code}")
    return await fund_fetcher.fetch(code)


@router.get("/markets")
async def get_markets():
    logger.info("Fetching market data")
    return await market_fetcher.fetch()
