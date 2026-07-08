from __future__ import annotations

from fastapi import APIRouter, Depends

from app.db.reports import list_reports
from app.routers.users import get_current_user
from app.schemas.users import User

router = APIRouter(prefix="/api/healthcare", tags=["healthcare"])


@router.get("/overview", summary="Healthcare-mode demand/regulatory/adoption overview")
async def get_healthcare_overview(current_user: User = Depends(get_current_user)):
    reports = await list_reports(current_user.id)
    healthcare_reports = [r for r in reports if r.healthcare_mode]
    latest = healthcare_reports[0] if healthcare_reports else None
    chart_data = latest.chart_data if latest else {}
    healthcare = chart_data.get("healthcare") or {}
    trend = chart_data.get("trend", [])

    healthcare_trend = [
        {
            "month": point.get("month"),
            "demand": point.get("score", 0),
            "regulatory": point.get("opportunity", 0),
            "adoption": max(0, 100 - point.get("risk", 0)),
        }
        for point in trend
    ]

    return {
        "kpis": {
            "tam": chart_data.get("tam", "N/A"),
            "clinical_demand": healthcare.get("clinical_demand", 0),
            "regulatory_readiness": healthcare.get("regulatory_readiness", 0),
            "provider_adoption": healthcare.get("provider_adoption", "+0%"),
        },
        "trend": healthcare_trend,
        "readiness": healthcare.get("readiness", []),
        "watchlist": healthcare.get("watchlist", []),
    }
