from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response

from app.db.competitors import list_competitors_for_report
from app.db.reports import delete_report, get_report, list_reports, set_starred
from app.routers.users import get_current_user
from app.schemas.reports import Report
from app.schemas.users import User

router = APIRouter(prefix="/api/reports", tags=["reports"])


@router.get("/", response_model=list[Report], summary="List the current user's reports")
async def get_reports(current_user: User = Depends(get_current_user)):
    return await list_reports(current_user.id)


@router.get("/{report_id}", response_model=Report, summary="Get full report payload")
async def get_report_detail(report_id: str, current_user: User = Depends(get_current_user)):
    report = await get_report(report_id, current_user.id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return report


@router.post("/{report_id}/star", response_model=Report, summary="Toggle the starred flag on a report")
async def star_report(report_id: str, current_user: User = Depends(get_current_user)):
    report = await get_report(report_id, current_user.id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    updated = await set_starred(report_id, current_user.id, not report.starred)
    return updated


@router.delete("/{report_id}", summary="Delete a report")
async def remove_report(report_id: str, current_user: User = Depends(get_current_user)):
    deleted = await delete_report(report_id, current_user.id)
    if not deleted:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    return {"status": "ok"}


@router.get("/{report_id}/download", summary="Download a report export")
async def download_report(report_id: str, current_user: User = Depends(get_current_user)):
    report = await get_report(report_id, current_user.id)
    if report is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    competitors = await list_competitors_for_report(report_id)

    lines = [
        f"MarketScout AI — {report.title}",
        f"Industry: {report.industry or 'N/A'}",
        f"Market Score: {report.score}   Opportunity Score: {report.opportunity_score}   Risk: {report.risk_level}",
        "",
        report.description or "",
        "",
        "Competitors:",
        *[f"- {c.name} ({c.segment or 'N/A'}) — share {c.market_share}%, threat {c.threat}" for c in competitors],
        "",
        "Chart data:",
        json.dumps(report.chart_data, indent=2, ensure_ascii=False),
    ]
    content = "\n".join(lines)
    filename = f"{report.title.replace(' ', '_')}.txt"
    return Response(
        content=content,
        media_type="text/plain",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
