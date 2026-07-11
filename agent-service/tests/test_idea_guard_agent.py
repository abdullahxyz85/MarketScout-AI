"""
Unit tests for agents/idea_guard_agent.py

All LLM calls are monkeypatched so tests run offline without API keys.
"""
from __future__ import annotations

import json
from unittest.mock import AsyncMock, patch

import pytest

import agents.idea_guard_agent as idea_guard_agent


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _mock_llm(payload: dict):
    """Return an async context that makes call_llm return a JSON string."""
    return patch(
        "agents.idea_guard_agent.call_llm",
        new=AsyncMock(return_value=json.dumps(payload)),
    )


_APPROVED_PAYLOAD = {
    "clarity_score": 80,
    "vagueness_score": 20,
    "is_startup_idea": True,
    "legal_status": "legal",
    "ethical_status": "ethical",
    "technical_feasibility": "feasible",
    "market_potential": "strong",
    "verdict": "approved",
    "verdict_summary": "Clear, ethical, technically feasible B2B SaaS concept.",
    "rejection_reasons": [],
    "improvement_suggestions": [],
    "dimension_notes": {
        "clarity": "Well-articulated idea.",
        "startup_nature": "Clearly a startup concept.",
        "legality": "Fully legal in major jurisdictions.",
        "ethics": "No ethical concerns.",
        "technical_feasibility": "Standard ML stack, achievable.",
        "market": "SMB productivity market is large and growing.",
    },
}

_VAGUE_PAYLOAD = {
    "clarity_score": 30,
    "vagueness_score": 80,
    "is_startup_idea": True,
    "legal_status": "legal",
    "ethical_status": "ethical",
    "technical_feasibility": "feasible",
    "market_potential": "weak",
    "verdict": "needs_clarification",
    "verdict_summary": "Idea is too vague to research; please add specifics.",
    "rejection_reasons": ["The description lacks a target user, problem, or solution."],
    "improvement_suggestions": ["Define the target user and the specific pain point."],
    "dimension_notes": {
        "clarity": "Very generic description.",
        "startup_nature": "Could be a startup but needs definition.",
        "legality": "Legal.",
        "ethics": "No concerns.",
        "technical_feasibility": "Unknown without more detail.",
        "market": "Market unclear due to vague scope.",
    },
}

_REJECTED_ILLEGAL_PAYLOAD = {
    "clarity_score": 70,
    "vagueness_score": 10,
    "is_startup_idea": True,
    "legal_status": "illegal",
    "ethical_status": "unethical",
    "technical_feasibility": "feasible",
    "market_potential": "none",
    "verdict": "rejected",
    "verdict_summary": "Idea involves illegal activities and cannot be researched.",
    "rejection_reasons": ["Activity is illegal in all major jurisdictions."],
    "improvement_suggestions": [],
    "dimension_notes": {
        "clarity": "Clear but illegal.",
        "startup_nature": "Not a viable startup.",
        "legality": "Illegal.",
        "ethics": "Unethical.",
        "technical_feasibility": "Technically possible but moot.",
        "market": "No legitimate market.",
    },
}

_NOT_STARTUP_PAYLOAD = {
    "clarity_score": 60,
    "vagueness_score": 30,
    "is_startup_idea": False,
    "legal_status": "legal",
    "ethical_status": "ethical",
    "technical_feasibility": "feasible",
    "market_potential": "none",
    "verdict": "rejected",
    "verdict_summary": "This is not a startup idea; it describes a personal goal.",
    "rejection_reasons": ["No product, service, or business model described."],
    "improvement_suggestions": ["Describe what product or service you would build."],
    "dimension_notes": {
        "clarity": "Clear sentence but not a business idea.",
        "startup_nature": "Personal goal, not a startup.",
        "legality": "Legal.",
        "ethics": "Ethical.",
        "technical_feasibility": "N/A.",
        "market": "No market without a product.",
    },
}


# ─── Output structure ─────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_result_contains_all_required_keys():
    with _mock_llm(_APPROVED_PAYLOAD):
        result = await idea_guard_agent.run("An AI scheduling assistant for SMBs", "SaaS")

    required = {
        "clarity_score", "vagueness_score", "is_startup_idea",
        "legal_status", "ethical_status", "technical_feasibility",
        "market_potential", "verdict", "verdict_summary",
        "rejection_reasons", "improvement_suggestions", "dimension_notes",
    }
    assert required.issubset(result.keys())


@pytest.mark.asyncio
async def test_result_scores_are_integers_in_range():
    with _mock_llm(_APPROVED_PAYLOAD):
        result = await idea_guard_agent.run("An AI scheduling assistant for SMBs", "SaaS")

    assert 0 <= result["clarity_score"] <= 100
    assert 0 <= result["vagueness_score"] <= 100


@pytest.mark.asyncio
async def test_result_verdict_is_one_of_allowed_values():
    with _mock_llm(_APPROVED_PAYLOAD):
        result = await idea_guard_agent.run("An AI scheduling assistant for SMBs", "SaaS")

    assert result["verdict"] in ("approved", "needs_clarification", "rejected")


# ─── Verdict: approved ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_clear_startup_idea_is_approved():
    with _mock_llm(_APPROVED_PAYLOAD):
        result = await idea_guard_agent.run(
            "An AI-powered invoice automation platform for small businesses",
            "FinTech",
        )

    assert result["verdict"] == "approved"
    assert result["is_startup_idea"] is True
    assert result["legal_status"] == "legal"
    assert result["ethical_status"] == "ethical"
    assert result["rejection_reasons"] == []


@pytest.mark.asyncio
async def test_approved_idea_has_no_rejection_reasons():
    with _mock_llm(_APPROVED_PAYLOAD):
        result = await idea_guard_agent.run("B2B SaaS for HR automation", "HR Tech")

    assert result["rejection_reasons"] == []


# ─── Verdict: needs_clarification ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_vague_idea_returns_needs_clarification():
    with _mock_llm(_VAGUE_PAYLOAD):
        result = await idea_guard_agent.run("An app for productivity", "")

    assert result["verdict"] == "needs_clarification"
    assert result["vagueness_score"] > 65
    assert len(result["rejection_reasons"]) >= 1
    assert len(result["improvement_suggestions"]) >= 1


@pytest.mark.asyncio
async def test_needs_clarification_has_improvement_suggestions():
    with _mock_llm(_VAGUE_PAYLOAD):
        result = await idea_guard_agent.run("Something with AI and blockchain", "Tech")

    assert len(result["improvement_suggestions"]) >= 1


# ─── Verdict: rejected ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_illegal_idea_is_rejected():
    with _mock_llm(_REJECTED_ILLEGAL_PAYLOAD):
        result = await idea_guard_agent.run("A marketplace for illegal weapons", "Crime")

    assert result["verdict"] == "rejected"
    assert result["legal_status"] == "illegal"
    assert len(result["rejection_reasons"]) >= 1


@pytest.mark.asyncio
async def test_non_startup_idea_is_rejected():
    with _mock_llm(_NOT_STARTUP_PAYLOAD):
        result = await idea_guard_agent.run("I want to become a chess grandmaster", "")

    assert result["verdict"] == "rejected"
    assert result["is_startup_idea"] is False


@pytest.mark.asyncio
async def test_rejected_idea_has_non_empty_verdict_summary():
    with _mock_llm(_REJECTED_ILLEGAL_PAYLOAD):
        result = await idea_guard_agent.run("A marketplace for illegal weapons", "")

    assert result["verdict_summary"] != ""


# ─── Resilience: bad LLM responses ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_fallback_defaults_applied_when_llm_returns_empty_json():
    with patch("agents.idea_guard_agent.call_llm", new=AsyncMock(return_value="{}")):
        result = await idea_guard_agent.run("A B2B SaaS idea for legal teams", "LegalTech")

    # All defaults must be present and safe
    assert result["verdict"] == "approved"
    assert result["legal_status"] == "legal"
    assert result["ethical_status"] == "ethical"
    assert result["rejection_reasons"] == []
    assert result["improvement_suggestions"] == []


@pytest.mark.asyncio
async def test_agent_does_not_raise_on_garbage_llm_output():
    with patch("agents.idea_guard_agent.call_llm", new=AsyncMock(return_value="not json at all!!!")):
        result = await idea_guard_agent.run("A B2B SaaS idea for legal teams", "LegalTech")

    # Must return a dict (with fallback defaults), not raise
    assert isinstance(result, dict)
    assert "verdict" in result


@pytest.mark.asyncio
async def test_agent_does_not_raise_on_markdown_wrapped_json():
    raw = "```json\n" + json.dumps(_APPROVED_PAYLOAD) + "\n```"
    with patch("agents.idea_guard_agent.call_llm", new=AsyncMock(return_value=raw)):
        result = await idea_guard_agent.run("An AI platform for SMBs", "SaaS")

    assert result["verdict"] == "approved"


@pytest.mark.asyncio
async def test_industry_not_specified_does_not_crash():
    with _mock_llm(_APPROVED_PAYLOAD):
        result = await idea_guard_agent.run("An AI scheduling assistant for SMBs", "")

    assert result["verdict"] == "approved"


# ─── Dimension notes ──────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_dimension_notes_contains_all_six_dimensions():
    with _mock_llm(_APPROVED_PAYLOAD):
        result = await idea_guard_agent.run("An AI scheduling assistant for SMBs", "SaaS")

    notes = result["dimension_notes"]
    for dim in ("clarity", "startup_nature", "legality", "ethics", "technical_feasibility", "market"):
        assert dim in notes, f"Missing dimension note: {dim}"
