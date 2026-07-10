from __future__ import annotations

import asyncio
import json
import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import Response, StreamingResponse

from orchestrator.pipeline import cleanup_queue, get_queue, register_queue, run_pipeline
from schemas.models import AskRequest, JobResponse, JobStatus, ResearchRequest, ScenarioRequest
from services import memory_service, report_generator
from services.auth_guard import _DEV_USER, require_auth
from services.compare_service import compare_competitors, compare_ideas
from services import rate_limiter

logger = logging.getLogger("agent-service.router")

# ── UUID validation ────────────────────────────────────────────────────────────
_UUID_RE = re.compile(
    r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$',
    re.IGNORECASE,
)

def _validate_uuid(value: str, field: str = "job_id") -> str:
    if not _UUID_RE.match(value):
        raise HTTPException(
            status_code=422,
            detail=f"Invalid {field} format. Must be a UUID.",
        )
    return value


# ── Secure error helper ────────────────────────────────────────────────────────
def _internal_error(exc: Exception, corr_id: str) -> HTTPException:
    """Log the real exception server-side and return a safe generic error to the client."""
    logger.exception("internal error corr_id=%s", corr_id)
    return HTTPException(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail=f"An internal error occurred. Reference: {corr_id}",
    )


# ── Job ownership helper ───────────────────────────────────────────────────────
def _assert_owns_job(job: Dict[str, Any], auth_user_id: str) -> None:
    """
    Raise HTTP 404 if the caller does not own this job.

    We return 404 (not 403) to avoid revealing whether the job exists for
    another user. In dev mode (_DEV_USER), ownership is not enforced.
    """
    from config import settings
    if not settings.AGENT_AUTH_ENABLED or auth_user_id == _DEV_USER:
        return
    owner = job.get("owner_user_id")
    if owner is not None and owner != auth_user_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Job not found")

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
        headers={"Cache-Control": "no-cache, no-store", "X-Accel-Buffering": "no"},
    )

# In-memory job registry: job_id → { status, created_at, idea, industry, result, owner_user_id }
_jobs: Dict[str, Dict[str, Any]] = {}

router = APIRouter()


async def _pipeline_task(
    job_id: str,
    request: ResearchRequest,
    queue: asyncio.Queue,
    auth_user_id: str | None = None,
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

        # Persist result using auth_user_id from JWT token (never request body)
        effective_user_id = (
            auth_user_id if auth_user_id and auth_user_id != _DEV_USER
            else None
        )
        if effective_user_id:
            asyncio.create_task(
                memory_service.save_research_result(
                    job_id=job_id,
                    idea=request.idea,
                    industry=request.industry,
                    user_id=effective_user_id,
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
            "error": "An internal error occurred. Please try again.",
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
async def start_research(
    request: ResearchRequest,
    background_tasks: BackgroundTasks,
    auth_user_id: str = Depends(require_auth),
):
    """
    Start a new multi-agent market research job.
    Returns a job_id that can be used to stream progress via SSE.
    """
    # Rate-limit expensive research jobs
    await rate_limiter.check_research_start(auth_user_id)

    job_id = str(uuid.uuid4())
    queue = register_queue(job_id)
    created_at = datetime.utcnow().isoformat()

    _jobs[job_id] = {
        "status": JobStatus.RUNNING,
        "created_at": created_at,
        "idea": request.idea,
        "industry": request.industry,
        "result": None,
        "owner_user_id": auth_user_id,  # always set from auth token, never from body
    }

    background_tasks.add_task(_pipeline_task, job_id, request, queue, auth_user_id)

    return JobResponse(job_id=job_id, status=JobStatus.RUNNING, created_at=created_at)


@router.get("/research/{job_id}/stream", tags=["research"])
async def stream_research_progress(job_id: str, auth_user_id: str = Depends(require_auth)):
    """
    Server-Sent Events (SSE) endpoint. Streams agent progress events in real time.
    Each event: { progress, current_agent, status, done, result? }
    The stream closes automatically when done=true.
    """
    _validate_uuid(job_id)
    if job_id not in _jobs:
        raise HTTPException(status_code=404, detail="Job not found")

    job = _jobs[job_id]
    _assert_owns_job(job, auth_user_id)

    if job["status"] == JobStatus.COMPLETED and job["result"]:
        async def _already_done():
            yield f"data: {json.dumps({'progress': 100, 'current_agent': 'Complete', 'done': True})}\n\n"
        return StreamingResponse(_already_done(), media_type="text/event-stream",
                                 headers={"Cache-Control": "no-cache, no-store", "X-Accel-Buffering": "no"})

    queue = get_queue(job_id)
    if not queue:
        raise HTTPException(status_code=410, detail="Stream no longer available for this job")

    return _sse_stream(queue)


@router.get("/research/{job_id}/status", response_model=JobResponse, tags=["research"])
async def get_job_status(job_id: str, auth_user_id: str = Depends(require_auth)):
    """Return the current status of a research job."""
    _validate_uuid(job_id)
    job = _jobs.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    _assert_owns_job(job, auth_user_id)
    return JobResponse(job_id=job_id, status=job["status"], created_at=job["created_at"])


@router.get("/research/{job_id}/result", tags=["research"])
async def get_research_result(job_id: str, auth_user_id: str = Depends(require_auth)):
    """
    Return the complete research result for a completed job.
    Returns HTTP 202 if the job is still in progress.
    """
    _validate_uuid(job_id)
    job = _jobs.get(job_id)
    if job:
        _assert_owns_job(job, auth_user_id)
    if not job:
        result_from_db = await memory_service.get_research_result(job_id, owner_user_id=auth_user_id)
        if result_from_db:
            return result_from_db
        raise HTTPException(status_code=404, detail="Job not found")

    if job["status"] == JobStatus.RUNNING:
        raise HTTPException(status_code=202, detail="Job is still running")

    if job["status"] == JobStatus.FAILED:
        raise HTTPException(status_code=500, detail="Job failed")

    return job["result"]


@router.get("/research/{job_id}/report/pdf", tags=["research"])
async def download_pdf_report(job_id: str, auth_user_id: str = Depends(require_auth)):
    """Generate and return a PDF market intelligence report for a completed job."""
    _validate_uuid(job_id)
    await rate_limiter.check_pdf(auth_user_id)
    corr_id = str(uuid.uuid4())
    job = _jobs.get(job_id)
    if job:
        _assert_owns_job(job, auth_user_id)
    if job and job["status"] == JobStatus.COMPLETED and job["result"]:
        result = job["result"]
    else:
        result = await memory_service.get_research_result(job_id, owner_user_id=auth_user_id)
        if not result:
            raise HTTPException(status_code=404, detail="Completed job not found")

    try:
        pdf_bytes = report_generator.generate_pdf_report(result)
    except Exception as exc:
        corr_id = str(uuid.uuid4())
        raise _internal_error(exc, corr_id)
    safe_job_id = job_id.replace('/', '').replace('..', '')[:8]
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f'attachment; filename="marketscout_{safe_job_id}.pdf"',
            "Cache-Control": "private, no-store",
        },
    )


@router.post("/research/{job_id}/scenario", tags=["research"])
async def simulate_scenario(job_id: str, request: ScenarioRequest, auth_user_id: str = Depends(require_auth)):
    """
    Run a 'what-if' scenario simulation against a completed research result.
    """
    _validate_uuid(job_id)
    await rate_limiter.check_scenario(auth_user_id)
    job = _jobs.get(job_id)
    if job:
        _assert_owns_job(job, auth_user_id)
    base_result = (job or {}).get("result") if job else None

    if not base_result:
        base_result = await memory_service.get_research_result(job_id, owner_user_id=auth_user_id)

    if not base_result:
        raise HTTPException(status_code=404, detail="Base research result not found")

    from agents.strategy_agent import run_scenario_simulation
    result = await run_scenario_simulation(
        base_result=base_result,
        scenario=request.scenario.model_dump(exclude_none=True),
    )
    return result


@router.get("/research/history/me", tags=["research"])
async def get_my_history(auth_user_id: str = Depends(require_auth)):
    """Return the research history for the authenticated user."""
    history = await memory_service.get_user_research_history(user_id=auth_user_id)
    return {"history": history}


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
    _: str = Depends(require_auth),
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
    _: str = Depends(require_auth),
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


# ── Shared helper ─────────────────────────────────────────────────────────────

async def _get_completed_state(job_id: str, auth_user_id: str) -> Dict[str, Any]:
    """Retrieve a completed job's full pipeline state with ownership enforcement."""
    _validate_uuid(job_id)
    job = _jobs.get(job_id)
    if job:
        _assert_owns_job(job, auth_user_id)
        if job.get("result"):
            return job["result"]
    result = await memory_service.get_research_result(job_id, owner_user_id=auth_user_id)
    if result:
        return result
    raise HTTPException(
        status_code=404,
        detail="Completed job not found. Run a market research first.",
    )


# ── Startup Kit endpoints (LLM-based, on-demand) ──────────────────────────────

@router.get("/research/{job_id}/business-plan", tags=["startup-kit"])
async def get_business_plan(job_id: str, auth_user_id: str = Depends(require_auth)):
    """Generate a comprehensive 15-section business plan from a completed research job."""
    await rate_limiter.check_llm_doc(auth_user_id, "business-plan")
    from agents.business_plan_agent import run as _run
    state = await _get_completed_state(job_id, auth_user_id)
    return await _run(state)


@router.get("/research/{job_id}/investor-memo", tags=["startup-kit"])
async def get_investor_memo(job_id: str, auth_user_id: str = Depends(require_auth)):
    """Generate a VC-style investor memo with verdict from a completed research job."""
    await rate_limiter.check_llm_doc(auth_user_id, "investor-memo")
    from agents.investor_agent import run as _run
    state = await _get_completed_state(job_id, auth_user_id)
    return await _run(state)


@router.get("/research/{job_id}/pitch-deck", tags=["startup-kit"])
async def get_pitch_deck(job_id: str, auth_user_id: str = Depends(require_auth)):
    """Generate a 10-slide structured pitch deck from a completed research job."""
    await rate_limiter.check_llm_doc(auth_user_id, "pitch-deck")
    from agents.pitch_agent import run as _run
    state = await _get_completed_state(job_id, auth_user_id)
    return await _run(state)


# ── Quality & Evidence endpoints (deterministic, no LLM) ─────────────────────

@router.get("/research/{job_id}/quality-report", tags=["quality"])
async def get_quality_report(job_id: str, auth_user_id: str = Depends(require_auth)):
    """Return a deterministic pipeline quality report (grade A-F, hallucination risk, etc.)."""
    from services.quality_report import generate
    state = await _get_completed_state(job_id, auth_user_id)
    return generate(state).to_dict()


@router.get("/research/{job_id}/evidence", tags=["quality"])
async def get_evidence(job_id: str, auth_user_id: str = Depends(require_auth)):
    """Extract and summarise all grounded evidence claims from a completed research job."""
    from services.evidence_engine import extract_all, summarise
    state = await _get_completed_state(job_id, auth_user_id)
    evidences = extract_all(state)
    return {
        "evidences": [e.to_dict() for e in evidences],
        "summary": summarise(evidences),
        "total": len(evidences),
    }


@router.get("/research/{job_id}/sources", tags=["quality"])
async def get_source_credibility(job_id: str, auth_user_id: str = Depends(require_auth)):
    """Rank all sources from a completed research job by credibility (1\u20135 stars)."""
    from services.source_ranker import rank as _rank
    state = await _get_completed_state(job_id, auth_user_id)
    seen: set = set()
    ranked = []
    for val in state.values():
        if not isinstance(val, dict):
            continue
        for src in (val.get("sources") or []):
            url = src if isinstance(src, str) else (src.get("url", "") if isinstance(src, dict) else "")
            if url and url not in seen:
                seen.add(url)
                r = _rank(url)
                ranked.append({
                    "url": url,
                    "stars": r.stars,
                    "score": r.score,
                    "category": r.category,
                    "label": r.label,
                })
    ranked.sort(key=lambda x: x["score"], reverse=True)
    avg = round(sum(x["score"] for x in ranked) / max(len(ranked), 1), 3)
    return {
        "ranked_sources": ranked,
        "top_sources": ranked[:5],
        "average_credibility": avg,
        "total_sources": len(ranked),
    }


# ── Ask Your Research endpoint (LLM Q&A over pipeline results) ───────────────

@router.post("/research/{job_id}/ask", tags=["ask"])
async def ask_research(job_id: str, request: AskRequest, auth_user_id: str = Depends(require_auth)):
    """
    Ask a natural-language question about a completed research job.
    The LLM answers strictly from the pipeline results \u2014 no hallucination.
    """
    await rate_limiter.check_ask(auth_user_id)
    state = await _get_completed_state(job_id, auth_user_id)
    from services.fireworks_client import call_llm, FireworksModel

    idea = state.get("idea", "")
    industry = state.get("industry", "")
    report = state.get("report") or {}
    research = state.get("research") or {}
    competitors = state.get("competitors") or {}
    innovation = state.get("innovation_score") or {}
    risks = state.get("risks") or {}
    opportunities = state.get("opportunities") or {}
    scientific = state.get("scientific") or {}
    patents = state.get("patents") or {}
    gaps = state.get("research_gaps") or {}
    strategy = state.get("strategy") or {}

    context = f"""You are an expert research assistant for a startup market intelligence platform.
Answer the user's question using ONLY the research data below. If the data does not contain
enough information to answer, say so clearly. Do not invent facts.

=== RESEARCH CONTEXT ===
Idea: {idea}
Industry: {industry}

Executive Summary: {report.get("executive_summary", "N/A")}
Market Score: {report.get("market_score", "N/A")}/100
Innovation Score: {innovation.get("innovation_score", "N/A")}/100
Innovation Grade: {innovation.get("grade", "N/A")}
Competition Level: {report.get("competition_level", "N/A")}
Overall Risk Level: {risks.get("overall_risk_level", "N/A")}

Market Size: {research.get("market_size", "N/A")}
Growth Rate: {research.get("growth_rate", "N/A")}
TAM: {research.get("tam", "N/A")}

Key Competitors: {", ".join(c.get("name","") for c in (competitors.get("competitors") or [])[:5])}

Top Opportunities: {"; ".join((opportunities.get("top_opportunities") or [])[:3])}
Key Risks: {"; ".join(r.get("description","") for r in (risks.get("key_risks") or [])[:3])}
Research Gaps: {"; ".join((gaps.get("identified_gaps") or [])[:3])}
Strategy Summary: {strategy.get("executive_summary", "N/A")}

Scientific Maturity: {scientific.get("research_maturity", "N/A")}
Patent Landscape: {patents.get("ip_landscape", "N/A")}
Freedom to Operate: {patents.get("freedom_to_operate", "N/A")}

Recommendations: {"; ".join((report.get("recommendations") or [])[:5])}
=== END CONTEXT ===
"""

    answer = await call_llm(
        prompt=request.question,
        system_prompt=context,
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=800,
    )

    return {
        "question": request.question,
        "answer": answer.strip(),
        "job_id": job_id,
        "idea": idea,
        "industry": industry,
    }
