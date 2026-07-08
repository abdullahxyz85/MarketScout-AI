from __future__ import annotations

import logging

from app.db.competitors import create_competitors
from app.db.reports import create_report
from app.db.research_runs import update_research_run
from app.schemas.research import AGENT_SEQUENCE
from app.services.agents.competitor_agent import run_competitor_agent
from app.services.agents.healthcare_agent import run_healthcare_agent
from app.services.agents.market_agent import run_market_agent
from app.services.agents.opportunity_agent import run_opportunity_agent
from app.services.agents.research_agent import run_research_agent
from app.services.agents.risk_agent import run_risk_agent
from app.services.agents.swot_agent import run_swot_agent
from app.services.agents.trend_agent import run_trend_agent

logger = logging.getLogger(__name__)

PIE_COLORS = ["#6366f1", "#a855f7", "#06b6d4", "#10b981", "#f59e0b", "#f43f5e"]


async def _set_progress(run_id: str, agent: str, index: int) -> None:
    progress = round((index / len(AGENT_SEQUENCE)) * 100)
    await update_research_run(run_id, current_agent=agent, progress=progress, status="running")


async def run_research_pipeline(run_id: str, user_id: str, idea: str, industry: str | None, healthcare_mode: bool) -> None:
    try:
        await _set_progress(run_id, AGENT_SEQUENCE[0], 1)
        research = await run_research_agent(idea, industry, healthcare_mode)

        await _set_progress(run_id, AGENT_SEQUENCE[1], 2)
        competitors = await run_competitor_agent(idea, industry)

        await _set_progress(run_id, AGENT_SEQUENCE[2], 3)
        market = await run_market_agent(idea, industry)

        await _set_progress(run_id, AGENT_SEQUENCE[3], 4)
        trend = await run_trend_agent(idea, industry)

        await _set_progress(run_id, AGENT_SEQUENCE[4], 5)
        swot = await run_swot_agent(idea, industry)

        await _set_progress(run_id, AGENT_SEQUENCE[5], 6)
        opportunity = await run_opportunity_agent(idea, industry)

        await _set_progress(run_id, AGENT_SEQUENCE[6], 7)
        risk = await run_risk_agent(idea, industry)

        healthcare_data = None
        if healthcare_mode:
            healthcare_data = await run_healthcare_agent(idea)

        await _set_progress(run_id, AGENT_SEQUENCE[7], 8)

        pie_data = [
            {
                "name": c.get("name", "Unknown"),
                "value": c.get("market_share", 0),
                "color": PIE_COLORS[i % len(PIE_COLORS)],
            }
            for i, c in enumerate(competitors[:6])
        ]

        chart_data = {
            "trend": trend,
            "funding_by_sector": market.get("funding_by_sector", []),
            "pie": pie_data,
            "swot": swot,
            "opportunity_highlights": opportunity.get("highlights", []),
            "risks": risk.get("risks", []),
            "tam": market.get("tam") or research.get("tam"),
            "healthcare": healthcare_data,
        }

        report = await create_report(
            user_id=user_id,
            research_run_id=run_id,
            title=research.get("title", idea[:60]),
            description=research.get("description", ""),
            industry=industry,
            healthcare_mode=healthcare_mode,
            score=market.get("market_score", 0),
            opportunity_score=opportunity.get("opportunity_score", 0),
            risk_level=risk.get("risk_level", "Medium"),
            pages=max(len(competitors), 12),
            starred=False,
            chart_data=chart_data,
        )

        if competitors:
            await create_competitors(
                [
                    {
                        "user_id": user_id,
                        "report_id": report.id,
                        "name": c.get("name", "Unknown"),
                        "segment": c.get("segment"),
                        "market_share": c.get("market_share", 0),
                        "threat": c.get("threat", "medium"),
                        "trend": c.get("trend", "stable"),
                        "revenue": c.get("revenue"),
                    }
                    for c in competitors
                ]
            )

        await update_research_run(
            run_id,
            current_agent="Report Generator",
            progress=100,
            status="completed",
            report_id=report.id,
        )
    except Exception as exc:  # noqa: BLE001
        logger.exception("Research pipeline failed for run %s", run_id)
        await update_research_run(run_id, status="failed", error=str(exc))
