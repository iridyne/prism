from __future__ import annotations

from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from src.fetchers.fund_fetcher import FundFetcher
from src.fetchers.market_fetcher import MarketFetcher


class DebateState(TypedDict):
    positions: list[dict[str, Any]]
    preferences: dict[str, Any]
    fund_data: dict[str, Any]
    market_data: dict[str, Any]
    insights: list[dict[str, Any]]


def _clamp_score(value: float) -> int:
    return max(0, min(100, int(round(value))))


class PrismKernel:
    """Core analysis engine used by background analysis jobs."""

    def __init__(self) -> None:
        self.fund_fetcher = FundFetcher()
        self.market_fetcher = MarketFetcher()
        self._workflow = self._build_workflow()

    def _build_workflow(self):
        graph = StateGraph(DebateState)

        async def fundamental_agent(state: DebateState) -> DebateState:
            funds = state["fund_data"].get("funds", {})
            changes = []
            for code in [p["code"] for p in state["positions"]]:
                item = funds.get(code, {})
                change = item.get("change")
                if isinstance(change, (int, float)):
                    changes.append(change)
            avg_change = sum(changes) / len(changes) if changes else 0.0
            score = _clamp_score(55 + avg_change * 5)
            state["insights"].append(
                {
                    "agent": "fundamental",
                    "confidence": 0.72,
                    "score": score,
                    "analysis": f"持仓基金近端净值变化均值约为 {avg_change:.2f}% 。",
                }
            )
            return state

        async def technical_agent(state: DebateState) -> DebateState:
            markets = state["market_data"].get("markets", {})
            move = []
            for val in markets.values():
                pct = val.get("change_pct")
                if isinstance(pct, (int, float)):
                    move.append(pct)
            avg_market_move = sum(move) / len(move) if move else 0.0
            score = _clamp_score(58 + avg_market_move * 4)
            trend = "偏强" if avg_market_move > 0 else "偏弱"
            state["insights"].append(
                {
                    "agent": "technical",
                    "confidence": 0.68,
                    "score": score,
                    "analysis": f"大盘短期动量 {trend}，均值变动约 {avg_market_move:.2f}% 。",
                }
            )
            return state

        async def risk_agent(state: DebateState) -> DebateState:
            allocations = [float(p.get("allocation", 0.0)) for p in state["positions"]]
            max_alloc = max(allocations) if allocations else 0.0
            concentration_penalty = max(0.0, (max_alloc - 0.35) * 100)
            score = _clamp_score(80 - concentration_penalty)
            state["insights"].append(
                {
                    "agent": "risk",
                    "confidence": 0.8,
                    "score": score,
                    "analysis": f"单基金最高仓位 {max_alloc:.2%}，集中度惩罚 {concentration_penalty:.1f}。",
                }
            )
            return state

        graph.add_node("fundamental", fundamental_agent)
        graph.add_node("technical", technical_agent)
        graph.add_node("risk", risk_agent)

        graph.set_entry_point("fundamental")
        graph.add_edge("fundamental", "technical")
        graph.add_edge("technical", "risk")
        graph.add_edge("risk", END)

        return graph.compile()

    async def analyze(
        self,
        *,
        positions: list[dict[str, Any]],
        preferences: dict[str, Any],
        progress_cb,
    ) -> dict[str, Any]:
        await progress_cb(10, "Loading fund data...")
        fund_codes = [p["code"] for p in positions]
        fund_data = await self.fund_fetcher.fetch(fund_codes)

        await progress_cb(35, "Loading market sentiment...")
        market_data = await self.market_fetcher.fetch()

        await progress_cb(60, "Running MAS debate via LangGraph...")
        state: DebateState = {
            "positions": positions,
            "preferences": preferences,
            "fund_data": fund_data,
            "market_data": market_data,
            "insights": [],
        }
        final_state = await self._workflow.ainvoke(state)
        insights = final_state["insights"]

        await progress_cb(82, "Synthesizing recommendations...")
        overall_score = _clamp_score(sum(i["score"] for i in insights) / len(insights)) if insights else 50

        allocations = sorted(
            [float(p.get("allocation", 0.0)) for p in positions], reverse=True
        )
        top2 = sum(allocations[:2]) if allocations else 0.0

        warnings: list[str] = []
        if top2 > 0.7:
            warnings.append(f"前两大仓位合计 {top2:.0%}，组合相关性风险偏高。")

        risk_level = preferences.get("risk_level", "medium")
        recommendations: list[str] = [
            "保持每周一次组合回顾，重点关注回撤与仓位漂移。",
            "将高相关基金进行风格分散，降低单一赛道暴露。",
        ]
        if risk_level == "low":
            recommendations.append("低风险偏好建议控制单基金仓位不超过 30%。")
        elif risk_level == "high":
            recommendations.append("高风险偏好可保留成长暴露，但需设置止损与调仓阈值。")

        summary = (
            f"综合评分 {overall_score}/100。"
            f"当前组合包含 {len(positions)} 只基金，"
            f"风险偏好为 {risk_level}。"
        )

        metrics = {
            "position_count": len(positions),
            "top2_allocation": round(top2, 4),
            "fund_data_points": len(fund_data.get("funds", {})),
            "market_indexes": len(market_data.get("markets", {})),
        }

        await progress_cb(100, "Analysis complete")

        return {
            "overall_score": overall_score,
            "summary": summary,
            "recommendations": recommendations,
            "correlation_warnings": warnings,
            "backtest_metrics": metrics,
            "agent_insights": insights,
        }
