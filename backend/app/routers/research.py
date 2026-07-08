from __future__ import annotations

import asyncio
import json

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse

from app.db.research_runs import create_research_run, get_research_run
from app.routers.users import get_current_user
from app.schemas.research import ResearchRequest, ResearchStartResponse
from app.schemas.users import User
from app.services.research_pipeline import run_research_pipeline

router = APIRouter(prefix="/api/research", tags=["research"])


@router.post("/", response_model=ResearchStartResponse, summary="Start a research pipeline run")
async def start_research(payload: ResearchRequest, current_user: User = Depends(get_current_user)):
    run = await create_research_run(
        user_id=current_user.id,
        idea=payload.idea,
        industry=payload.industry,
        healthcare_mode=payload.healthcare_mode,
        status="pending",
        progress=0,
    )
    asyncio.create_task(
        run_research_pipeline(
            run_id=run.id,
            user_id=current_user.id,
            idea=payload.idea,
            industry=payload.industry,
            healthcare_mode=payload.healthcare_mode,
        )
    )
    return ResearchStartResponse(report_id=run.id)


@router.get("/{run_id}/stream", summary="Stream live progress for a research run via SSE")
async def stream_research(run_id: str, current_user: User = Depends(get_current_user)):
    run = await get_research_run(run_id, current_user.id)
    if run is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Research run not found")

    async def event_stream():
        while True:
            run = await get_research_run(run_id, current_user.id)
            if run is None:
                break
            payload = {
                "status": run.status,
                "current_agent": run.current_agent,
                "progress": run.progress,
                "report_id": run.report_id,
                "error": run.error,
            }
            yield f"data: {json.dumps(payload)}\n\n"
            if run.status in ("completed", "failed"):
                break
            await asyncio.sleep(1)

    return StreamingResponse(event_stream(), media_type="text/event-stream")
