from __future__ import annotations

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Any, Dict

from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import Response, StreamingResponse

from orchestrator.pipeline import cleanup_queue, get_queue, register_queue, run_pipeline
from schemas.models import JobResponse, JobStatus, ResearchRequest, ScenarioRequest
from services import memory_service, report_generator
from services.compare_service import compare_competitors, compare_ideas

logger = logging.getLogger("agent-service.router")

def _sse_stream(queue: asyncio.Queue) -> StreamingResponse:
    """Wrap an asyncio.Queue into a StreamingResponse with text/event-stream content type."""
    async def _generate():
        while True:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=120.0)
                yield f"data: {json.dumps(event)}\n\n"
                if event.get("done"):
                    break
            except asyncio.TimeoutError:
                yield f"data: {json.dumps({'progress': -1, 'done': False, 'heartbeat': True})}\n\n"
    return StreamingResponse(
        _generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

# In-memory job registry: job_id -> { status, created_at, idea, industry, result }
_jobs: Dict[str, Dict[str, Any]] = {}

router = APIRouter()


async def _pipeline_task(
    job_id: str,
    request: ResearchRequest,
    queue: asyncio.Queue,
) -> None:
    """Background task that runs the full multi-agent pipeline and publishes SSE events."""
    logger.info("job %s: pipeline started (idea=%r, industry=%r)", job_id, request.idea, request.industry)
    try:
        final_state = await run_pipeline(
            job_id=job_id,
            idea=request.idea,
            industry=request.industry,
            healthcare_mode=request.healthcare_mode,
        )

        # ── Idea Guard check ─────────────────────────────────────────────────
        idea_guard = final_state.get("idea_guard") or {}
        verdict = idea_guard.get("verdict", "approved")

        if verdict in ("rejected", "needs_clarification"):
            # Pipeline was short-circuited — surface the guard's feedback.
            _jobs[job_id]["status"] = JobStatus.FAILED
            _jobs[job_id]["result"] = dict(final_state)
            logger.warning(
                "job %s: idea guard %s — %s",
                job_id, verdict, idea_guard.get("verdict_summary", ""),
            )
            await queue.put({
                "progress": 0,
                "current_agent": "Idea Guard",
                "status": verdict,
                "done": True,
                "idea_guard_verdict": verdict,
                "idea_guard": idea_guard,
                "error": idea_guard.get("verdict_summary", "Idea rejected by Idea Guard."),
            })
            return
        # ─────────────────────────────────────────────────────────────────────

        _jobs[job_id]["status"] = JobStatus.COMPLETED
        _jobs[job_id]["result"] = dict(final_state)

        errors = final_state.get("errors") or []
        if errors:
            logger.warning("job %s: completed with %d agent-level error(s): %s", job_id, len(errors), errors)
        else:
            logger.info("job %s: completed successfully", job_id)

        # Exclude non-serializable internals from SSE payload
        result_payload = {k: v for k, v in final_state.items() if k != "job_id"}

        await queue.put({
            "progress": 100,
            "current_agent": "Complete",
            "status": "completed",
            "done": True,
            "result": result_payload,
        })

        if request.user_id:
            asyncio.create_task(
                memory_service.save_research_result(
                    job_id=job_id,
                    idea=request.idea,
                    industry=request.industry,
                    user_id=request.user_id,
                    result=dict(final_state),
                )
            )

    except Exception as exc:
        logger.exception("job %s: pipeline failed", job_id)
        _jobs[job_id]["status"] = JobStatus.FAILED
        await queue.put({
            "progress": 0,
            "current_agent": "Error",
            "done": True,
            "error": str(exc),
        })
    finally:
        # Delay cleanup on a separate task so a slow/late SSE reconnect can still
        # find the queue, without blocking this background task (and therefore
        # the request/reload lifecycle) for 5 extra minutes after completion.
        asyncio.create_task(_delayed_cleanup(job_id))


async def _delayed_cleanup(job_id: str, delay_seconds: int = 300) -> None:
    await asyncio.sleep(delay_seconds)
    cleanup_queue(job_id)
    logger.debug("job %s: queue cleaned up", job_id)


@router.post("/research/start", response_model=JobResponse, tags=["research"])
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    """
    Start a new multi-agent market research job.
    Returns a job_id that can be used to stream progress via SSE.
    """
    job_id = str(uuid.uuid4())
    queue = register_queue(job_id)
    created_at = datetime.utcnow().isoformat()

    _jobs[job_id] = {
        "status": JobStatus.RUNNING,
        "created_at": created_at,
        "idea": request.idea,
        "industry": request.industry,
        "result": None,
    }

    background_tasks.add_task(_pipeline_task, job_id, request, queue)

    return JobResponse(job_id=job_id, status=JobStatus.RUNNING, created_at=created_at)


@router.get("/research/{job_id}/stream", tags=["research"])
async def stream_research_progress(job_id: str):
    """
    Server-Sent Events (SSE) endpoint. Streams agent progress events in real time.
    Each event: { progress, current_agent, status, done, result? }
    The stream closes automatically when done=true.
    """
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = _jobs[job_id]

    if job["status"] == JobStatus.COMPLETED and job["result"]:
        async def _already_done():
            yield f"data: {json.dumps({'progress': 100, 'current_agent': 'Complete', 'done': True})}\n\n"
        return StreamingResponse(_already_done(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"})

    queue = get_queue(job_id)
    if not queue:
        raise HTTPException(status_code=410, detail="Stream no longer available for this job")

    return _sse_stream(queue)


@router.get("/research/{job_id}/status", response_model=JobResponse, tags=["research"])
async def get_job_status(job_id: str):
    """Return the current status of a research job."""
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return JobResponse(job_id=job_id, status=job["status"], created_at=job["created_at"])


@router.get("/research/{job_id}/result", tags=["research"])
async def get_research_result(job_id: str):
    """
    Return the complete research result for a completed job.
    Returns HTTP 202 if the job is still in progress.
    """
    job = _jobs.get(job_id)
    if not job:
        result_from_db = await memory_service.get_research_result(job_id)
        if result_from_db:
            return result_from_db
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] == JobStatus.RUNNING:
        raise HTTPException(status_code=202, detail="Job is still running")

    if job["status"] == JobStatus.FAILED:
        raise HTTPException(status_code=500, detail="Job failed")

    return job["result"]


@router.get("/research/{job_id}/report/pdf", tags=["research"])
async def download_pdf_report(job_id: str):
    """Generate and return a PDF market intelligence report for a completed job."""
    job = _jobs.get(job_id)
    if job and job["status"] == JobStatus.COMPLETED and job["result"]:
        result = job["result"]
    else:
        # In-memory job registry is wiped on every service restart/reload;
        # fall back to the persisted result so PDFs stay downloadable afterward.
        result = await memory_service.get_research_result(job_id)
        if not result:
            raise HTTPException(status_code=404, detail="Completed job not found")

    pdf_bytes = report_generator.generate_pdf_report(result)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="marketscout_{job_id[:8]}.pdf"'},
    )


@router.post("/research/{job_id}/scenario", tags=["research"])
async def simulate_scenario(job_id: str, request: ScenarioRequest):
    """
    Run a 'what-if' scenario simulation against a completed research result.
    Analyzes impact on market opportunity, competitive positioning, revenue, risk, and timeline.
    """
    job = _jobs.get(job_id)
    base_result = (job or {}).get("result") if job else None

    if not base_result:
        base_result = await memory_service.get_research_result(job_id)

    if not base_result:
        raise HTTPException(status_code=404, detail="Base research result not found")

    from agents.strategy_agent import run_scenario_simulation

    result = await run_scenario_simulation(
        base_result=base_result,
        scenario=request.scenario.model_dump(exclude_none=True),
    )
    return result


@router.get("/research/history/{user_id}", tags=["research"])
async def get_user_history(user_id: str):
    """Return the research history for a given user from persistent storage."""
    history = await memory_service.get_user_research_history(user_id=user_id)
    return {"history": history}


@router.get("/compare/ideas", tags=["compare"])
async def compare_two_ideas(
    job_id_a: str,
    job_id_b: str,
    label_a: str = "Idea A",
    label_b: str = "Idea B",
):
    """
    Compare two completed research jobs side-by-side across all key dimensions.
    Returns per-dimension scores, deltas, winners, and an overall recommendation.
    """
    async def _get_result(job_id: str) -> Dict[str, Any]:
        job = _jobs.get(job_id)
        if job and job.get("result"):
            return job["result"]
        result = await memory_service.get_research_result(job_id)
        if result:
            return result
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    state_a, state_b = await asyncio.gather(_get_result(job_id_a), _get_result(job_id_b))
    return compare_ideas(state_a, state_b, label_a=label_a, label_b=label_b)


@router.get("/compare/competitors", tags=["compare"])
async def compare_two_competitors(
    job_id_a: str,
    job_id_b: str,
    label_a: str = "Idea A",
    label_b: str = "Idea B",
):
    """
    Compare the competitive landscapes of two completed research jobs.
    Returns side-by-side competitor lists, saturation scores, and a verdict.
    """
    async def _get_result(job_id: str) -> Dict[str, Any]:
        job = _jobs.get(job_id)
        if job and job.get("result"):
            return job["result"]
        result = await memory_service.get_research_result(job_id)
        if result:
            return result
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    state_a, state_b = await asyncio.gather(_get_result(job_id_a), _get_result(job_id_b))
    return compare_competitors(state_a, state_b, label_a=label_a, label_b=label_b)
