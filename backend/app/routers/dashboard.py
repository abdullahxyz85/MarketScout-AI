from __future__ import annotations

from fastapi import APIRouter, Depends

from app.db.competitors import list_competitors
from app.db.reports import list_reports
from app.routers.users import get_current_user
from app.schemas.users import User

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/overview", summary="Aggregated stats for the main dashboard")
async def get_dashboard_overview(report_id: str | None = None, current_user: User = Depends(get_current_user)):
    reports = await list_reports(current_user.id)
    all_competitors = await list_competitors(current_user.id)

    selected = next((r for r in reports if r.id == report_id), None) if report_id else None
    focused = selected or (reports[0] if reports else None)

    chart_data = focused.chart_data if focused else {}
    if not isinstance(chart_data, dict):
        chart_data = {}
    swot_raw = chart_data.get("swot")
    if not isinstance(swot_raw, dict):
        swot_raw = {}

    # When a specific report is selected, scope competitors/scores to that report;
    # otherwise show an aggregate view across every report (the "All projects" case).
    if selected is not None:
        competitors = [c for c in all_competitors if c.report_id == selected.id]
        market_score = selected.score
        opportunity_score = selected.opportunity_score
    else:
        competitors = all_competitors
        market_score = sum(r.score for r in reports) / len(reports) if reports else 0
        opportunity_score = sum(r.opportunity_score for r in reports) / len(reports) if reports else 0

    radar = [
        {"metric": "Research", "you": min(round(market_score), 100), "avg": 62},
        {"metric": "Speed", "you": 88, "avg": 54},
        {"metric": "Accuracy", "you": min(round(market_score) + 3, 100), "avg": 67},
        {"metric": "Coverage", "you": min(len(competitors) * 4, 100), "avg": 58},
        {"metric": "Reports", "you": min(len(reports) * 8, 100), "avg": 48},
        {"metric": "Insights", "you": min(round(opportunity_score) + 5, 100), "avg": 61},
    ]

    return {
        "selected_report_id": focused.id if focused else None,
        "kpis": {
            "market_score": round(market_score, 1),
            "opportunity_score": round(opportunity_score, 1),
            "competitors_found": len(competitors),
            "reports_count": len(reports),
        },
        "trend": chart_data.get("trend", []),
        "funding_by_sector": chart_data.get("funding_by_sector", []),
        "pie": chart_data.get("pie", []),
        "radar": radar,
        "competitors": [
            {
                "name": c.name,
                "marketShare": c.market_share,
                "threat": c.threat,
                "trend": c.trend,
                "revenue": c.revenue,
            }
            for c in competitors[:5]
        ],
        "recent_research": [
            {"title": r.title, "date": r.created_at, "score": r.score, "id": r.id}
            for r in reports[:5]
        ],
        "swot": {
            "strengths": swot_raw.get("strengths") or [],
            "weaknesses": swot_raw.get("weaknesses") or [],
            "opportunities": swot_raw.get("opportunities") or [],
            "threats": swot_raw.get("threats") or [],
        },
    }
