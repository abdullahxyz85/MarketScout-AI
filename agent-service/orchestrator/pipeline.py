from __future__ import annotations

import asyncio
from typing import Any, Dict, Optional

from langgraph.graph import END, StateGraph

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


# ─────────────────────────────────────────────
# LangGraph Node Definitions
# Each node: pushes running event → calls agent → updates state → pushes completed event
# ─────────────────────────────────────────────

async def _research_node(state: ResearchState) -> dict:
    job_id = state["job_id"]
    await _push(job_id, {"progress": 3, "current_agent": "Research Agent", "status": "running", "done": False})
    errors = list(state.get("errors", []))
    try:
        result = await research_agent.run(state["idea"], state["industry"], state["healthcare_mode"])
    except Exception as exc:
        result = {}
        errors.append(f"ResearchAgent: {exc}")
    await _push(job_id, {"progress": 10, "current_agent": "Research Agent", "status": "completed", "done": False})
    return {"research": result, "progress": 10, "current_agent": "Competitor Agent", "errors": errors}


async def _competitor_node(state: ResearchState) -> dict:
    job_id = state["job_id"]
    await _push(job_id, {"progress": 11, "current_agent": "Competitor Agent", "status": "running", "done": False})
    errors = list(state.get("errors", []))
    try:
        result = await competitor_agent.run(state["idea"], state["industry"], state["healthcare_mode"])
    except Exception as exc:
        result = {}
        errors.append(f"CompetitorAgent: {exc}")
    await _push(job_id, {"progress": 20, "current_agent": "Competitor Agent", "status": "completed", "done": False})
    return {"competitors": result, "progress": 20, "current_agent": "Scientific Research Agent", "errors": errors}


async def _scientific_node(state: ResearchState) -> dict:
    job_id = state["job_id"]
    await _push(job_id, {"progress": 21, "current_agent": "Scientific Research Agent", "status": "running", "done": False})
    errors = list(state.get("errors", []))
    try:
        result = await scientific_agent.run(state["idea"], state["industry"], state["healthcare_mode"])
    except Exception as exc:
        result = {}
        errors.append(f"ScientificAgent: {exc}")
    await _push(job_id, {"progress": 30, "current_agent": "Scientific Research Agent", "status": "completed", "done": False})
    return {"scientific": result, "progress": 30, "current_agent": "Patent Intelligence Agent", "errors": errors}


async def _patent_node(state: ResearchState) -> dict:
    job_id = state["job_id"]
    await _push(job_id, {"progress": 31, "current_agent": "Patent Intelligence Agent", "status": "running", "done": False})
    errors = list(state.get("errors", []))
    try:
        result = await patent_agent.run(state["idea"], state["industry"], state["healthcare_mode"])
    except Exception as exc:
        result = {}
        errors.append(f"PatentAgent: {exc}")
    await _push(job_id, {"progress": 38, "current_agent": "Patent Intelligence Agent", "status": "completed", "done": False})
    return {"patents": result, "progress": 38, "current_agent": "Funding Agent", "errors": errors}


async def _funding_node(state: ResearchState) -> dict:
    job_id = state["job_id"]
    await _push(job_id, {"progress": 39, "current_agent": "Funding Agent", "status": "running", "done": False})
    errors = list(state.get("errors", []))
    try:
        result = await funding_agent.run(state["idea"], state["industry"], state["healthcare_mode"])
    except Exception as exc:
        result = {}
        errors.append(f"FundingAgent: {exc}")
    await _push(job_id, {"progress": 46, "current_agent": "Funding Agent", "status": "completed", "done": False})
    return {"funding": result, "progress": 46, "current_agent": "Trend Agent", "errors": errors}


async def _trend_node(state: ResearchState) -> dict:
    job_id = state["job_id"]
    await _push(job_id, {"progress": 47, "current_agent": "Trend Agent", "status": "running", "done": False})
    errors = list(state.get("errors", []))
    try:
        result = await trend_agent.run(state["idea"], state["industry"], state["healthcare_mode"])
    except Exception as exc:
        result = {}
        errors.append(f"TrendAgent: {exc}")
    await _push(job_id, {"progress": 54, "current_agent": "Trend Agent", "status": "completed", "done": False})
    return {"trends": result, "progress": 54, "current_agent": "Research Gap Agent", "errors": errors}


async def _research_gap_node(state: ResearchState) -> dict:
    job_id = state["job_id"]
    await _push(job_id, {"progress": 55, "current_agent": "Research Gap Agent", "status": "running", "done": False})
    errors = list(state.get("errors", []))
    try:
        result = await research_gap_agent.run(
            idea=state["idea"],
            industry=state["industry"],
            healthcare_mode=state["healthcare_mode"],
            competitor_data=state.get("competitors"),
            scientific_data=state.get("scientific"),
        )
    except Exception as exc:
        result = {}
        errors.append(f"ResearchGapAgent: {exc}")
    await _push(job_id, {"progress": 62, "current_agent": "Research Gap Agent", "status": "completed", "done": False})
    return {"research_gaps": result, "progress": 62, "current_agent": "SWOT Agent", "errors": errors}


async def _swot_node(state: ResearchState) -> dict:
    job_id = state["job_id"]
    await _push(job_id, {"progress": 63, "current_agent": "SWOT Agent", "status": "running", "done": False})
    errors = list(state.get("errors", []))
    try:
        result = await swot_agent.run(
            idea=state["idea"],
            industry=state["industry"],
            healthcare_mode=state["healthcare_mode"],
            research_data=state.get("research"),
            competitor_data=state.get("competitors"),
            trend_data=state.get("trends"),
            gap_data=state.get("research_gaps"),
        )
    except Exception as exc:
        result = {}
        errors.append(f"SWOTAgent: {exc}")
    await _push(job_id, {"progress": 68, "current_agent": "SWOT Agent", "status": "completed", "done": False})
    return {"swot": result, "progress": 68, "current_agent": "Opportunity Agent", "errors": errors}


async def _opportunity_node(state: ResearchState) -> dict:
    job_id = state["job_id"]
    await _push(job_id, {"progress": 69, "current_agent": "Opportunity Agent", "status": "running", "done": False})
    errors = list(state.get("errors", []))
    try:
        result = await opportunity_agent.run(
            idea=state["idea"],
            industry=state["industry"],
            healthcare_mode=state["healthcare_mode"],
            research_data=state.get("research"),
            competitor_data=state.get("competitors"),
            gap_data=state.get("research_gaps"),
            swot_data=state.get("swot"),
        )
    except Exception as exc:
        result = {}
        errors.append(f"OpportunityAgent: {exc}")
    await _push(job_id, {"progress": 74, "current_agent": "Opportunity Agent", "status": "completed", "done": False})
    return {"opportunities": result, "progress": 74, "current_agent": "Risk Agent", "errors": errors}


async def _risk_node(state: ResearchState) -> dict:
    job_id = state["job_id"]
    await _push(job_id, {"progress": 75, "current_agent": "Risk Agent", "status": "running", "done": False})
    errors = list(state.get("errors", []))
    try:
        result = await risk_agent.run(
            idea=state["idea"],
            industry=state["industry"],
            healthcare_mode=state["healthcare_mode"],
            competitor_data=state.get("competitors"),
            swot_data=state.get("swot"),
            patent_data=state.get("patents"),
        )
    except Exception as exc:
        result = {}
        errors.append(f"RiskAgent: {exc}")
    await _push(job_id, {"progress": 80, "current_agent": "Risk Agent", "status": "completed", "done": False})
    return {"risks": result, "progress": 80, "current_agent": "Innovation Scoring Agent", "errors": errors}


async def _innovation_scoring_node(state: ResearchState) -> dict:
    job_id = state["job_id"]
    await _push(job_id, {"progress": 81, "current_agent": "Innovation Scoring Agent", "status": "running", "done": False})
    errors = list(state.get("errors", []))
    try:
        result = await innovation_scoring_agent.run(dict(state))
    except Exception as exc:
        result = {}
        errors.append(f"InnovationScoringAgent: {exc}")
    await _push(job_id, {"progress": 85, "current_agent": "Innovation Scoring Agent", "status": "completed", "done": False})
    return {"innovation_score": result, "progress": 85, "current_agent": "Validation Agent", "errors": errors}


async def _validation_node(state: ResearchState) -> dict:
    job_id = state["job_id"]
    await _push(job_id, {"progress": 86, "current_agent": "Validation Agent", "status": "running", "done": False})
    errors = list(state.get("errors", []))
    try:
        result = await validation_agent.run(
            idea=state["idea"],
            industry=state["industry"],
            healthcare_mode=state["healthcare_mode"],
            research_data=state.get("research"),
            competitor_data=state.get("competitors"),
            opportunity_data=state.get("opportunities"),
            innovation_score_data=state.get("innovation_score"),
        )
    except Exception as exc:
        result = {}
        errors.append(f"ValidationAgent: {exc}")
    await _push(job_id, {"progress": 90, "current_agent": "Validation Agent", "status": "completed", "done": False})
    return {"validation": result, "progress": 90, "current_agent": "Strategy Agent", "errors": errors}


async def _strategy_node(state: ResearchState) -> dict:
    job_id = state["job_id"]
    await _push(job_id, {"progress": 91, "current_agent": "Strategy Agent", "status": "running", "done": False})
    errors = list(state.get("errors", []))
    try:
        result = await strategy_agent.run(
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
        )
    except Exception as exc:
        result = {}
        errors.append(f"StrategyAgent: {exc}")
    await _push(job_id, {"progress": 95, "current_agent": "Strategy Agent", "status": "completed", "done": False})
    return {"strategy": result, "progress": 95, "current_agent": "Report Generator", "errors": errors}


async def _report_node(state: ResearchState) -> dict:
    job_id = state["job_id"]
    await _push(job_id, {"progress": 96, "current_agent": "Report Generator", "status": "running", "done": False})
    errors = list(state.get("errors", []))
    try:
        result = await report_agent.run(
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
        )
    except Exception as exc:
        result = {}
        errors.append(f"ReportAgent: {exc}")
    await _push(job_id, {"progress": 99, "current_agent": "Report Generator", "status": "completed", "done": False})
    return {"report": result, "progress": 99, "current_agent": "Complete", "errors": errors}


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
    final_state = await pipeline.ainvoke(initial_state)

    # Build the evidence knowledge graph from all agent outputs
    try:
        from services.knowledge_graph import build_knowledge_graph
        final_state["knowledge_graph"] = build_knowledge_graph(dict(final_state))
    except Exception as exc:
        final_state["errors"] = list(final_state.get("errors", [])) + [f"KnowledgeGraph: {exc}"]

    # Push the terminal done=True event so SSE listeners can cleanly close
    await _push(job_id, {
        "progress": 100,
        "current_agent": "Complete",
        "status": "completed",
        "done": True,
        "innovation_score": (final_state.get("innovation_score") or {}).get("innovation_score"),
        "errors": final_state.get("errors", []),
    })

    return final_state
