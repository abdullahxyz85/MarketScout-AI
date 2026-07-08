from __future__ import annotations

import asyncio
import logging
import time
from typing import Any, Awaitable, Dict, Optional

from langgraph.graph import END, StateGraph

logger = logging.getLogger("agent-service.pipeline")

import agents.competitor_agent as competitor_agent
import agents.funding_agent as funding_agent
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

# Single source of truth for pipeline order — progress is derived from a step's
# real position in this list (index / total), never a hand-picked percentage.
AGENT_SEQUENCE = [
    "Research Agent",
    "Competitor Agent",
    "Scientific Research Agent",
    "Patent Intelligence Agent",
    "Funding Agent",
    "Trend Agent",
    "Research Gap Agent",
    "SWOT Agent",
    "Opportunity Agent",
    "Risk Agent",
    "Innovation Scoring Agent",
    "Validation Agent",
    "Strategy Agent",
    "Report Generator",
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
    start = time.monotonic()
    try:
        result = await coro
    except Exception as exc:
        result = {}
        errors.append(f"{error_label}: {exc}")
        logger.exception("job %s: %s failed after %.1fs", job_id, agent_name, time.monotonic() - start)
    else:
        logger.info("job %s: %s completed in %.1fs", job_id, agent_name, time.monotonic() - start)
    progress = _progress_after(step_index)
    await _push(job_id, {"progress": progress, "current_agent": agent_name, "status": "completed", "done": False})
    return result, progress


# ─────────────────────────────────────────────
# LangGraph Node Definitions
# Each node: pushes running event → calls agent → updates state → pushes completed event
# ─────────────────────────────────────────────

async def _research_node(state: ResearchState) -> dict:
    idx = 0
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "ResearchAgent",
        research_agent.run(state["idea"], state["industry"], state["healthcare_mode"]),
    )
    return {"research": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _competitor_node(state: ResearchState) -> dict:
    idx = 1
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "CompetitorAgent",
        competitor_agent.run(state["idea"], state["industry"], state["healthcare_mode"]),
    )
    return {"competitors": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _scientific_node(state: ResearchState) -> dict:
    idx = 2
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "ScientificAgent",
        scientific_agent.run(state["idea"], state["industry"], state["healthcare_mode"]),
    )
    return {"scientific": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _patent_node(state: ResearchState) -> dict:
    idx = 3
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "PatentAgent",
        patent_agent.run(state["idea"], state["industry"], state["healthcare_mode"]),
    )
    return {"patents": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _funding_node(state: ResearchState) -> dict:
    idx = 4
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "FundingAgent",
        funding_agent.run(state["idea"], state["industry"], state["healthcare_mode"]),
    )
    return {"funding": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _trend_node(state: ResearchState) -> dict:
    idx = 5
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "TrendAgent",
        trend_agent.run(state["idea"], state["industry"], state["healthcare_mode"]),
    )
    return {"trends": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _research_gap_node(state: ResearchState) -> dict:
    idx = 6
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
    idx = 7
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
    idx = 8
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
    idx = 9
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
    idx = 10
    job_id = state["job_id"]
    errors = list(state.get("errors", []))
    result, progress = await _run_step(
        job_id, idx, errors, "InnovationScoringAgent",
        innovation_scoring_agent.run(dict(state)),
    )
    return {"innovation_score": result, "progress": progress, "current_agent": _next_agent_name(idx), "errors": errors}


async def _validation_node(state: ResearchState) -> dict:
    idx = 11
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
    idx = 12
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
    idx = 13
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

    graph.set_entry_point("research")
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
        "current_agent": "Research Agent",
        "errors": [],
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

    # Note: the terminal done=True SSE event (carrying the full result payload)
    # is pushed by the caller (router.py's _pipeline_task) once it has assembled
    # the complete response — pushing a done=True event here would race it and
    # cause the SSE stream to close before the real result is ever sent.
    return final_state
