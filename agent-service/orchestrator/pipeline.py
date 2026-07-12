from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Awaitable, Dict, Optional

from langgraph.graph import END, StateGraph

logger = logging.getLogger("agent-service.pipeline")

import agents.competitor_agent as competitor_agent
import agents.funding_agent as funding_agent
import agents.idea_guard_agent as idea_guard_agent
import agents.innovation_scoring_agent as innovation_scoring_agent
import agents.opportunity_agent as opportunity_agent
import agents.patent_agent as patent_agent
import agents.report_agent as report_agent
import agents.research_agent as research_agent
import agents.research_gap_agent as research_gap_agent
import agents.risk_agent as risk_agent
import agents.scientific_agent as scientific_agent
import agents.strategy_agent as strategy_agent
import agents.swot_agent as swot_agent
import agents.trend_agent as trend_agent
import agents.validation_agent as validation_agent
from schemas.state import ResearchState
from services import agent_logger
from services.output_validator import validate as _ov_validate
from services.hallucination_checker import check_claims as _hc_check_claims, extract_claims as _hc_extract_claims

# ── Validator key mapping: AGENT_SEQUENCE name → output_validator schema key ──
_VALIDATOR_KEY: Dict[str, str] = {
    "Idea Guard":                  "idea_guard",
    "Research Agent":              "research",
    "Competitor Agent":            "competitor",
    "Scientific Research Agent":   "scientific",
    "Patent Intelligence Agent":   "patent",
    "Funding Agent":               "funding",
    "Trend Agent":                 "trend",
    "Research Gap Agent":          "research_gap",
    "SWOT Agent":                  "swot",
    "Opportunity Agent":           "opportunity",
    "Risk Agent":                  "risk",
    "Innovation Scoring Agent":    "innovation_scoring",
    "Validation Agent":            "validation",
    "Strategy Agent":              "strategy",
    "Report Generator":            "report",
}

# Web agents that provide sources → eligible for hallucination checking
_WEB_AGENTS = {
    "Research Agent", "Competitor Agent", "Scientific Research Agent",
    "Patent Intelligence Agent", "Funding Agent", "Trend Agent", "Research Gap Agent",
}


def _post_validate(agent_name: str, result: Dict[str, Any], errors: list) -> None:
    """Run output_validator + hallucination_checker on a finished agent result.

    Mutates *result* in-place by adding:
      _validation_warnings  – list[str]  (schema violations)
      _hallucination_flags  – list[dict] (weak/unsupported claims)

    Never raises — all errors are caught and appended to the errors list.
    """
    try:
        validator_key = _VALIDATOR_KEY.get(agent_name, "")
        if validator_key:
            vr = _ov_validate(validator_key, result)
            if vr.warnings:
                result["_validation_warnings"] = vr.warnings
                for w in vr.warnings:
                    logger.warning("OutputValidator [%s]: %s", agent_name, w)

        if agent_name in _WEB_AGENTS:
            sources = result.get("sources") or []
            if sources:
                claims = _hc_extract_claims(result, max_claims=8)
                if claims:
                    hal_results = _hc_check_claims(claims, sources)
                    flags = [
                        {"claim": claim[:120], "status": r.status, "score": round(r.score, 3)}
                        for claim, r in zip(claims, hal_results)
                        if r.status != "Supported"
                    ]
                    if flags:
                        result["_hallucination_flags"] = flags
                        logger.warning(
                            "HallucinationChecker [%s]: %d unsupported claim(s)",
                            agent_name, len(flags),
                        )
    except Exception as exc:
        errors.append(f"PostValidate[{agent_name}]: {exc}")
        logger.debug("post_validate error for %s: %s", agent_name, exc)

# Single source of truth for pipeline order — progress is derived from a step's
# real position in this list (index / total), never a hand-picked percentage.
AGENT_SEQUENCE = [
    "Idea Guard",          # idx 0  — gate: rejects invalid/illegal/vague ideas
    "Research Agent",      # idx 1
    "Competitor Agent",    # idx 2
    "Scientific Research Agent",  # idx 3
    "Patent Intelligence Agent",  # idx 4
    "Funding Agent",       # idx 5
    "Trend Agent",         # idx 6
    "Research Gap Agent",  # idx 7
    "SWOT Agent",          # idx 8
    "Opportunity Agent",   # idx 9
    "Risk Agent",          # idx 10
    "Innovation Scoring Agent",   # idx 11
    "Validation Agent",    # idx 12
    "Strategy Agent",      # idx 13
    "Report Generator",    # idx 14
]
_TOTAL_STEPS = len(AGENT_SEQUENCE)


def _progress_before(step_index: int) -> int:
    """% complete right before running the step at step_index (0-based)."""
    return round(step_index / _TOTAL_STEPS * 100)


def _progress_after(step_index: int) -> int:
    """% complete right after finishing the step at step_index (0-based)."""
    return round((step_index + 1) / _TOTAL_STEPS * 100)


def _next_agent_name(step_index: int) -> str:
    return AGENT_SEQUENCE[step_index + 1] if step_index + 1 < _TOTAL_STEPS else "Complete"


# Module-level registry mapping job_id → asyncio.Queue
# Queues carry SSE progress events to the streaming endpoint.
_job_queues: Dict[str, asyncio.Queue] = {}


def register_queue(job_id: str) -> asyncio.Queue:
    """Register an asyncio.Queue for a new job and return it."""
    q: asyncio.Queue = asyncio.Queue()
    _job_queues[job_id] = q
    return q


def get_queue(job_id: str) -> Optional[asyncio.Queue]:
    """Return the queue for an existing job, or None if not found."""
    return _job_queues.get(job_id)


def cleanup_queue(job_id: str) -> None:
    """Remove the queue for a completed job."""
    _job_queues.pop(job_id, None)


async def _push(job_id: str, data: Dict[str, Any]) -> None:
    """Push a progress event to the job queue if it exists."""
    q = _job_queues.get(job_id)
    if q:
        await q.put(data)


async def _run_step(
    job_id: str,
    step_index: int,
    errors: list,
    error_label: str,
    coro: Awaitable[Dict[str, Any]],
) -> tuple[Dict[str, Any], int]:
    """Run one pipeline step: push running event, await the agent, log outcome,
    push completed event. Returns (result, progress_after) for the caller to merge into state."""
    agent_name = AGENT_SEQUENCE[step_index]
    await _push(job_id, {"progress": _progress_before(step_index), "current_agent": agent_name, "status": "running", "done": False})
    logger.info("job %s: %s started", job_id, agent_name)
    asyncio.create_task(agent_logger.log_agent_start(job_id, agent_name))
    start = time.monotonic()
    try:
        result = await coro
    except Exception as exc:
        result = {}
        errors.append(f"{error_label}: {exc}")
        duration = time.monotonic() - start
        logger.exception("job %s: %s failed after %.1fs", job_id, agent_name, duration)
        asyncio.create_task(agent_logger.log_agent_error(job_id, agent_name, duration, str(exc)))
    else:
        duration = time.monotonic() - start
        logger.info("job %s: %s completed in %.1fs", job_id, agent_name, duration)
        # ── Deterministic post-validation (output schema + hallucination check) ──
        _post_validate(agent_name, result, errors)
        asyncio.create_task(agent_logger.log_agent_complete(job_id, agent_name, duration, result))
    progress = _progress_after(step_index)
    await _push(job_id, {"progress": progress, "current_agent": agent_name, "status": "completed", "done": False})
    return result, progress


# ─────────────────────────────────────────────
# LangGraph Node Definitions
# Each node: pushes running event → calls agent → updates state → pushes completed event
# ─────────────────────────────────────────────

async def _idea_guard_node(state: ResearchState) -> dict:
    """Step 0 — gate agent.  If the idea is rejected the pipeline routes to END."""
    idx = 0
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "IdeaGuardAgent",
        idea_guard_agent.run(state["idea"], state["industry"]),
    )
    verdict = result.get("verdict", "approved")
    next_agent = _next_agent_name(idx) if verdict == "approved" else "Blocked"
    return {"idea_guard": result, "progress": progress, "current_agent": next_agent, "errors": errors}


def _idea_guard_route(state: ResearchState) -> str:
    """Conditional edge after Idea Guard: continue or short-circuit to END."""
    verdict = (state.get("idea_guard") or {}).get("verdict", "approved")
    if verdict == "approved":
        return "research"
    # For 'rejected' and 'needs_clarification' we stop the pipeline here.
    return END


async def _research_node(state: ResearchState) -> dict:
    idx = 1
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "ResearchAgent",
        research_agent.run(state["idea"], state["industry"], state["healthcare_mode"]),
    )
    return {"research": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _competitor_node(state: ResearchState) -> dict:
    idx = 2
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "CompetitorAgent",
        competitor_agent.run(state["idea"], state["industry"], state["healthcare_mode"]),
    )
    return {"competitors": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _scientific_node(state: ResearchState) -> dict:
    idx = 3
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "ScientificAgent",
        scientific_agent.run(state["idea"], state["industry"], state["healthcare_mode"]),
    )
    return {"scientific": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _patent_node(state: ResearchState) -> dict:
    idx = 4
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "PatentAgent",
        patent_agent.run(state["idea"], state["industry"], state["healthcare_mode"]),
    )
    return {"patents": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _funding_node(state: ResearchState) -> dict:
    idx = 5
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "FundingAgent",
        funding_agent.run(state["idea"], state["industry"], state["healthcare_mode"]),
    )
    return {"funding": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _trend_node(state: ResearchState) -> dict:
    idx = 6
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "TrendAgent",
        trend_agent.run(state["idea"], state["industry"], state["healthcare_mode"]),
    )
    return {"trends": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _research_gap_node(state: ResearchState) -> dict:
    idx = 7
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "ResearchGapAgent",
        research_gap_agent.run(
            idea=state["idea"],
            industry=state["industry"],
            healthcare_mode=state["healthcare_mode"],
            competitor_data=state.get("competitors"),
            scientific_data=state.get("scientific"),
        ),
    )
    return {"research_gaps": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _swot_node(state: ResearchState) -> dict:
    idx = 8
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "SWOTAgent",
        swot_agent.run(
            idea=state["idea"],
            industry=state["industry"],
            healthcare_mode=state["healthcare_mode"],
            research_data=state.get("research"),
            competitor_data=state.get("competitors"),
            trend_data=state.get("trends"),
            gap_data=state.get("research_gaps"),
        ),
    )
    return {"swot": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _opportunity_node(state: ResearchState) -> dict:
    idx = 9
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "OpportunityAgent",
        opportunity_agent.run(
            idea=state["idea"],
            industry=state["industry"],
            healthcare_mode=state["healthcare_mode"],
            research_data=state.get("research"),
            competitor_data=state.get("competitors"),
            gap_data=state.get("research_gaps"),
            swot_data=state.get("swot"),
        ),
    )
    return {"opportunities": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _risk_node(state: ResearchState) -> dict:
    idx = 10
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "RiskAgent",
        risk_agent.run(
            idea=state["idea"],
            industry=state["industry"],
            healthcare_mode=state["healthcare_mode"],
            competitor_data=state.get("competitors"),
            swot_data=state.get("swot"),
            patent_data=state.get("patents"),
        ),
    )
    return {"risks": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _innovation_scoring_node(state: ResearchState) -> dict:
    idx = 11
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "InnovationScoringAgent",
        innovation_scoring_agent.run(dict(state)),
    )
    return {"innovation_score": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _validation_node(state: ResearchState) -> dict:
    idx = 12
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "ValidationAgent",
        validation_agent.run(
            idea=state["idea"],
            industry=state["industry"],
            healthcare_mode=state["healthcare_mode"],
            research_data=state.get("research"),
            competitor_data=state.get("competitors"),
            opportunity_data=state.get("opportunities"),
            innovation_score_data=state.get("innovation_score"),
        ),
    )
    return {"validation": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _strategy_node(state: ResearchState) -> dict:
    idx = 13
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "StrategyAgent",
        strategy_agent.run(
            idea=state["idea"],
            industry=state["industry"],
            healthcare_mode=state["healthcare_mode"],
            research_data=state.get("research"),
            competitor_data=state.get("competitors"),
            opportunity_data=state.get("opportunities"),
            swot_data=state.get("swot"),
            validation_data=state.get("validation"),
            gap_data=state.get("research_gaps"),
            trend_data=state.get("trends"),
        ),
    )
    return {"strategy": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _report_node(state: ResearchState) -> dict:
    idx = 14
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "ReportAgent",
        report_agent.run(
            idea=state["idea"],
            industry=state["industry"],
            healthcare_mode=state["healthcare_mode"],
            research_data=state.get("research"),
            competitor_data=state.get("competitors"),
            swot_data=state.get("swot"),
            opportunity_data=state.get("opportunities"),
            risk_data=state.get("risks"),
            innovation_score_data=state.get("innovation_score"),
            strategy_data=state.get("strategy"),
            trend_data=state.get("trends"),
            validation_data=state.get("validation"),
        ),
    )
    return {"report": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


# ─────────────────────────────────────────────
# Pipeline Assembly
# ─────────────────────────────────────────────

def _build_pipeline():
    """Assemble and compile the LangGraph multi-agent pipeline."""
    graph = StateGraph(ResearchState)

    graph.add_node("idea_guard", _idea_guard_node)
    graph.add_node("research", _research_node)
    graph.add_node("competitor", _competitor_node)
    graph.add_node("scientific", _scientific_node)
    graph.add_node("patent", _patent_node)
    graph.add_node("funding", _funding_node)
    graph.add_node("trend", _trend_node)
    graph.add_node("research_gap", _research_gap_node)
    graph.add_node("swot", _swot_node)
    graph.add_node("opportunity", _opportunity_node)
    graph.add_node("risk", _risk_node)
    graph.add_node("innovation_scoring", _innovation_scoring_node)
    graph.add_node("validation", _validation_node)
    graph.add_node("strategy", _strategy_node)
    graph.add_node("report", _report_node)

    graph.set_entry_point("idea_guard")
    # Conditional routing: approved → research pipeline; rejected/needs_clarification → END
    graph.add_conditional_edges("idea_guard", _idea_guard_route, {"research": "research", END: END})
    graph.add_edge("research", "competitor")
    graph.add_edge("competitor", "scientific")
    graph.add_edge("scientific", "patent")
    graph.add_edge("patent", "funding")
    graph.add_edge("funding", "trend")
    graph.add_edge("trend", "research_gap")
    graph.add_edge("research_gap", "swot")
    graph.add_edge("swot", "opportunity")
    graph.add_edge("opportunity", "risk")
    graph.add_edge("risk", "innovation_scoring")
    graph.add_edge("innovation_scoring", "validation")
    graph.add_edge("validation", "strategy")
    graph.add_edge("strategy", "report")
    graph.add_edge("report", END)

    return graph.compile()


_compiled_pipeline = None


def get_pipeline():
    global _compiled_pipeline
    if _compiled_pipeline is None:
        _compiled_pipeline = _build_pipeline()
    return _compiled_pipeline


async def run_pipeline(
    job_id: str,
    idea: str,
    industry: str,
    healthcare_mode: bool,
) -> ResearchState:
    """Run the full multi-agent pipeline and return the final state."""
    initial_state: ResearchState = {
        "job_id": job_id,
        "idea": idea,
        "industry": industry,
        "healthcare_mode": healthcare_mode,
        "progress": 0,
        "current_agent": "Idea Guard",
        "errors": [],
        "idea_guard": None,
        "research": None,
        "competitors": None,
        "scientific": None,
        "patents": None,
        "funding": None,
        "trends": None,
        "research_gaps": None,
        "swot": None,
        "opportunities": None,
        "risks": None,
        "innovation_score": None,
        "validation": None,
        "strategy": None,
        "knowledge_graph": None,
        "report": None,
        "consistency_check": None,
    }
    pipeline = get_pipeline()
    pipeline_start = time.monotonic()
    final_state = await pipeline.ainvoke(initial_state)
    logger.info("job %s: all %d agents completed in %.1fs", job_id, _TOTAL_STEPS, time.monotonic() - pipeline_start)

    # Build the evidence knowledge graph from all agent outputs
    try:
        from services.knowledge_graph import build_knowledge_graph
        final_state["knowledge_graph"] = build_knowledge_graph(dict(final_state))
    except Exception as exc:
        logger.exception("job %s: knowledge graph build failed", job_id)
        final_state["errors"] = list(final_state.get("errors", [])) + [f"KnowledgeGraph: {exc}"]

    # Run post-pipeline consistency checks
    try:
        from services.consistency_checker import check as _consistency_check
        cc = _consistency_check(dict(final_state))
        final_state["consistency_check"] = {
            "passed": cc.passed,
            "mock_mode": cc.mock_mode,
            "score_coverage": cc.score_coverage,
            "suspicious_identical_scores": cc.suspicious_identical_scores,
            "warnings": cc.warnings,
            "errors": cc.errors,
        }
        if cc.errors:
            logger.warning(
                "job %s: consistency errors: %s", job_id, cc.errors
            )
        if cc.warnings:
            logger.info(
                "job %s: consistency warnings (%d): %s",
                job_id, len(cc.warnings), cc.warnings[0],
            )
    except Exception as exc:
        logger.exception("job %s: consistency check failed", job_id)
        final_state["errors"] = list(final_state.get("errors", [])) + [f"ConsistencyCheck: {exc}"]

    # Fire-and-forget: log pipeline completion with all final scores
    total_duration = time.monotonic() - pipeline_start
    asyncio.create_task(
        agent_logger.log_pipeline_complete(job_id, total_duration, dict(final_state))
    )

    return final_state
