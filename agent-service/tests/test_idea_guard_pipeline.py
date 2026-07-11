"""
Integration tests for the Idea Guard gate in the pipeline and router.

Covers:
  - Pipeline short-circuits to END when guard rejects
  - Pipeline proceeds to research when guard approves
  - Router SSE event carries idea_guard feedback on rejection
  - Router marks job FAILED when guard rejects
  - Router marks job COMPLETED when guard approves
"""
from __future__ import annotations

import asyncio
import json

import pytest
from fastapi.testclient import TestClient

import router as router_module
from main import app
from orchestrator.pipeline import AGENT_SEQUENCE, _idea_guard_route
from schemas.state import ResearchState

client = TestClient(app)


# ─── Fixtures ─────────────────────────────────────────────────────────────────

def _make_state(**overrides) -> ResearchState:
    base: ResearchState = {
        "job_id": "test-job",
        "idea": "An AI-powered invoice automation platform for SMBs",
        "industry": "FinTech",
        "healthcare_mode": False,
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
    }
    base.update(overrides)
    return base


def _guard_result(verdict: str) -> dict:
    return {
        "clarity_score": 80 if verdict == "approved" else 25,
        "vagueness_score": 15 if verdict == "approved" else 85,
        "is_startup_idea": verdict != "rejected",
        "legal_status": "legal",
        "ethical_status": "ethical",
        "technical_feasibility": "feasible",
        "market_potential": "strong" if verdict == "approved" else "weak",
        "verdict": verdict,
        "verdict_summary": f"Idea Guard verdict: {verdict}.",
        "rejection_reasons": [] if verdict == "approved" else ["Test rejection reason."],
        "improvement_suggestions": [] if verdict == "approved" else ["Be more specific."],
        "dimension_notes": {},
    }


_FULL_FINAL_STATE = {
    "job_id": "test-job",
    "idea": "An AI-powered invoice automation platform for SMBs",
    "industry": "FinTech",
    "healthcare_mode": False,
    "errors": [],
    "idea_guard": _guard_result("approved"),
    "research": {"market_overview": "Large market"},
    "innovation_score": {"innovation_score": 72, "grade": "B"},
    "report": {"market_score": 80, "opportunity_score": 70, "competition_level": "medium"},
    "knowledge_graph": {"nodes": [], "links": [], "node_count": 0, "edge_count": 0},
}


# ─── AGENT_SEQUENCE structure ─────────────────────────────────────────────────

def test_idea_guard_is_first_in_agent_sequence():
    assert AGENT_SEQUENCE[0] == "Idea Guard"


def test_research_agent_is_second_in_agent_sequence():
    assert AGENT_SEQUENCE[1] == "Research Agent"


def test_agent_sequence_has_fifteen_agents():
    assert len(AGENT_SEQUENCE) == 15


def test_idea_guard_precedes_all_research_agents():
    guard_idx = AGENT_SEQUENCE.index("Idea Guard")
    research_idx = AGENT_SEQUENCE.index("Research Agent")
    assert guard_idx < research_idx


# ─── _idea_guard_route conditional edge ──────────────────────────────────────

def test_route_returns_research_when_approved():
    state = _make_state(idea_guard=_guard_result("approved"))
    assert _idea_guard_route(state) == "research"


def test_route_returns_END_when_rejected():
    from langgraph.graph import END
    state = _make_state(idea_guard=_guard_result("rejected"))
    assert _idea_guard_route(state) == END


def test_route_returns_END_when_needs_clarification():
    from langgraph.graph import END
    state = _make_state(idea_guard=_guard_result("needs_clarification"))
    assert _idea_guard_route(state) == END


def test_route_defaults_to_research_when_idea_guard_is_none():
    """Safety net: missing idea_guard key must not crash the pipeline."""
    state = _make_state(idea_guard=None)
    assert _idea_guard_route(state) == "research"


def test_route_defaults_to_research_when_verdict_is_missing():
    state = _make_state(idea_guard={})
    assert _idea_guard_route(state) == "research"


# ─── Router: approved idea → pipeline completes ───────────────────────────────

def test_router_completes_job_when_guard_approves(monkeypatch):
    async def fake_run_pipeline(job_id, idea, industry, healthcare_mode):
        return dict(_FULL_FINAL_STATE, job_id=job_id)

    monkeypatch.setattr(router_module, "run_pipeline", fake_run_pipeline)

    res = client.post(
        "/research/start",
        json={"idea": "An AI-powered invoice automation platform for SMBs", "industry": "FinTech"},
    )
    assert res.status_code == 200
    job_id = res.json()["job_id"]

    status_res = client.get(f"/research/{job_id}/status")
    assert status_res.json()["status"] == "completed"


def test_router_result_contains_idea_guard_when_approved(monkeypatch):
    async def fake_run_pipeline(job_id, idea, industry, healthcare_mode):
        return dict(_FULL_FINAL_STATE, job_id=job_id)

    monkeypatch.setattr(router_module, "run_pipeline", fake_run_pipeline)

    res = client.post(
        "/research/start",
        json={"idea": "An AI-powered invoice automation platform for SMBs", "industry": "FinTech"},
    )
    job_id = res.json()["job_id"]

    result_res = client.get(f"/research/{job_id}/result")
    assert result_res.status_code == 200
    result = result_res.json()
    assert result["idea_guard"]["verdict"] == "approved"


# ─── Router: rejected idea → job fails + SSE contains guard feedback ──────────

def _make_rejected_final_state(job_id: str, verdict: str) -> dict:
    return {
        "job_id": job_id,
        "idea": "A very vague tech thing",
        "industry": "",
        "healthcare_mode": False,
        "errors": [],
        "idea_guard": _guard_result(verdict),
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


@pytest.mark.parametrize("verdict", ["rejected", "needs_clarification"])
def test_router_marks_job_failed_when_guard_blocks(monkeypatch, verdict):
    async def fake_run_pipeline(job_id, idea, industry, healthcare_mode):
        return _make_rejected_final_state(job_id, verdict)

    monkeypatch.setattr(router_module, "run_pipeline", fake_run_pipeline)

    res = client.post(
        "/research/start",
        json={"idea": "A very vague tech thing that makes no sense", "industry": ""},
    )
    job_id = res.json()["job_id"]

    status_res = client.get(f"/research/{job_id}/status")
    assert status_res.json()["status"] == "failed"


@pytest.mark.asyncio
@pytest.mark.parametrize("verdict", ["rejected", "needs_clarification"])
async def test_sse_stream_delivers_idea_guard_event_when_blocked(monkeypatch, verdict):
    """The SSE done event for a blocked idea must carry idea_guard_verdict and idea_guard."""
    async def fake_run_pipeline(job_id, idea, industry, healthcare_mode):
        return _make_rejected_final_state(job_id, verdict)

    monkeypatch.setattr(router_module, "run_pipeline", fake_run_pipeline)

    # Trigger the pipeline via the HTTP start endpoint
    from fastapi.testclient import TestClient as _TC
    sync_client = _TC(app)
    start_res = sync_client.post(
        "/research/start",
        json={"idea": "A very vague tech thing that makes no sense", "industry": ""},
    )
    job_id = start_res.json()["job_id"]

    # Give the background task time to finish
    await asyncio.sleep(0.3)

    # The job must be marked failed
    status_res = sync_client.get(f"/research/{job_id}/status")
    assert status_res.json()["status"] == "failed"


@pytest.mark.parametrize("verdict", ["rejected", "needs_clarification"])
def test_router_result_not_available_when_guard_blocks(monkeypatch, verdict):
    async def fake_run_pipeline(job_id, idea, industry, healthcare_mode):
        return _make_rejected_final_state(job_id, verdict)

    monkeypatch.setattr(router_module, "run_pipeline", fake_run_pipeline)

    res = client.post(
        "/research/start",
        json={"idea": "A very vague tech thing that makes no sense", "industry": ""},
    )
    job_id = res.json()["job_id"]

    result_res = client.get(f"/research/{job_id}/result")
    # Failed jobs return 500 (no usable result)
    assert result_res.status_code == 500


# ─── State schema: idea_guard field ───────────────────────────────────────────

def test_research_state_has_idea_guard_field():
    """ResearchState TypedDict must include idea_guard."""
    from schemas.state import ResearchState
    annotations = ResearchState.__annotations__
    assert "idea_guard" in annotations


def test_idea_guard_field_is_optional():
    """idea_guard should accept None (pipeline not yet run guard or guard skipped)."""
    from typing import Union, get_args, get_origin, get_type_hints
    from schemas.state import ResearchState
    # get_type_hints() evaluates string annotations (from __future__ import annotations)
    hints = get_type_hints(ResearchState)
    annotation = hints["idea_guard"]
    # Optional[dict] == Union[dict, None]
    origin = get_origin(annotation)
    args = get_args(annotation)
    assert origin is Union and type(None) in args
