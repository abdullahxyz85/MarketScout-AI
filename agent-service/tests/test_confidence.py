"""
Tests for services/confidence.py

Contract under test:
  - Never modifies input data
  - confidence is always float in [0.0, 1.0]
  - evidence_strength is always one of "strong"|"moderate"|"weak"|"none"
  - reason is always a non-empty string
  - None / parse_error → confidence=0.0, strength="none"
  - Strong outputs (all fields, sources) → confidence >= 0.80
  - Degraded outputs → lower confidence than full outputs
"""
from __future__ import annotations

import copy
from typing import Any, Dict

import pytest

from services.confidence import ConfidenceResult, assess, assess_all


# ─── Fixtures ─────────────────────────────────────────────────────────────────

def _sources(n: int = 3) -> list:
    return [f"https://example.com/{i}" for i in range(n)]


def _full(agent: str) -> Dict[str, Any]:
    """Return a complete, high-quality output for each agent."""
    outputs: Dict[str, Dict[str, Any]] = {
        "idea_guard": {
            "verdict": "approved",
            "verdict_summary": "Clear, viable idea.",
            "clarity_score": 85,
            "vagueness_score": 15,
            "is_startup_idea": True,
            "legal_status": "legal",
            "ethical_status": "ethical",
            "technical_feasibility": "feasible",
            "market_potential": "strong",
            "rejection_reasons": [],
            "improvement_suggestions": [],
            "dimension_notes": {"clarity": "ok"},
        },
        "research": {
            "market_overview": "Large fast-growing market.",
            "key_players": ["A", "B", "C"],
            "market_size_estimate": "$20B",
            "recent_trends": ["trend1", "trend2"],
            "growth_rate": "18% CAGR",
            "target_customers": ["SMBs", "Enterprises"],
            "pain_points": ["pain1", "pain2"],
            "summary": "Strong opportunity.",
            "sources": _sources(4),
        },
        "competitor": {
            "competitors": [{"name": "Acme"}, {"name": "Beta"}],
            "competitive_landscape": "Moderately competitive.",
            "market_saturation_score": 55,
            "differentiation_opportunities": ["op1", "op2"],
            "sources": _sources(3),
        },
        "scientific": {
            "relevant_papers": ["Paper A", "Paper B"],
            "research_maturity": "mature",
            "research_maturity_score": 70,
            "key_findings": ["finding1"],
            "research_gaps": ["gap1"],
            "academic_consensus": "Broadly supported.",
            "sources": _sources(3),
        },
        "patent": {
            "existing_patents": ["US12345"],
            "patent_density_score": 35,
            "white_spaces": ["space1"],
            "freedom_to_operate_risks": ["risk1"],
            "ip_strategy_recommendation": "File provisional.",
            "sources": _sources(3),
        },
        "funding": {
            "recent_funding_rounds": [{"company": "X", "amount": "$5M"}],
            "funding_activity_score": 70,
            "total_market_funding_estimate": "$1B",
            "top_investors": ["a16z", "Sequoia"],
            "average_valuation_range": "$20M-$80M",
            "funding_trend": "rising",
            "investor_thesis": "AI-first automation.",
            "sources": _sources(3),
        },
        "trend": {
            "trends": ["AI adoption", "remote work"],
            "market_growth_rate": "20% CAGR",
            "emerging_technologies": ["LLMs", "automation"],
            "regulatory_trends": ["EU AI Act"],
            "market_forecast": "$50B by 2030",
            "disruptive_forces": ["OpenAI", "Microsoft"],
            "sources": _sources(3),
        },
        "research_gap": {
            "unexplored_opportunities": ["opp1", "opp2"],
            "missing_features_in_market": ["feat1"],
            "emerging_niches": ["niche1"],
            "competitor_blind_spots": ["blind1"],
            "technology_white_spaces": ["white1"],
            "novelty_score": 75,
            "differentiation_thesis": "Strong differentiation.",
            "sources": _sources(3),
        },
        "swot": {
            "strengths": ["s1", "s2"],
            "weaknesses": ["w1"],
            "opportunities": ["o1", "o2"],
            "threats": ["t1"],
        },
        "opportunity": {
            "market_gaps": ["gap1", "gap2"],
            "target_segments": [{"segment": "SMBs"}],
            "opportunity_score": 72,
            "blue_ocean_potential": "moderate",
        },
        "risk": {
            "risks": [{"name": "Market risk"}],
            "overall_risk_level": "medium",
            "risk_score": 38,
            "critical_risks": ["Market risk"],
            "risk_mitigation_roadmap": "Diversify early.",
        },
        "innovation_scoring": {
            "innovation_score": 76,
            "grade": "B",
            "score_explanation": "Strong novelty, moderate market saturation.",
        },
        "validation": {
            "challenged_assumptions": [{"assumption": "Users pay", "challenge": "No proof"}],
            "validation_experiments": ["Landing page test"],
            "confidence_level": "medium",
            "key_risks_identified": ["Low WTP"],
            "recommendation": "Run a 30-day pilot.",
        },
        "strategy": {
            "strategic_recommendations": ["Launch in SMB segment"],
            "innovation_hypotheses": ["AI cuts manual work 80%"],
            "go_to_market": "Product-led growth",
            "competitive_positioning": "Premium at mid price",
            "pricing_strategy": "Per-seat SaaS",
            "key_partnerships": ["Salesforce"],
            "success_metrics": ["MRR", "NPS"],
            "roadmap": [{"phase": "1"}],
        },
        "report": {
            "executive_summary": "Promising market.",
            "market_score": 78,
            "opportunity_score": 72,
            "competition_level": "medium",
            "recommendations": ["Launch MVP"],
            "key_metrics": {"mrr": "$50K"},
            "full_report": "Full markdown report text here.",
        },
    }
    return outputs[agent]


ALL_AGENTS = [
    "idea_guard", "research", "competitor", "scientific", "patent",
    "funding", "trend", "research_gap", "swot", "opportunity",
    "risk", "innovation_scoring", "validation", "strategy", "report",
]


# ─── ConfidenceResult contract ────────────────────────────────────────────────

def test_confidence_result_is_immutable():
    r = ConfidenceResult(confidence=0.9, evidence_strength="strong", reason="ok")
    with pytest.raises((AttributeError, TypeError)):
        r.confidence = 0.5  # type: ignore[misc]


def test_evidence_strength_values_are_valid():
    valid = {"strong", "moderate", "weak", "none"}
    for agent in ALL_AGENTS:
        result = assess(agent, _full(agent))
        assert result.evidence_strength in valid, (
            f"[{agent}] invalid evidence_strength: {result.evidence_strength!r}"
        )


# ─── assess() never mutates input ─────────────────────────────────────────────

@pytest.mark.parametrize("agent", ALL_AGENTS)
def test_assess_does_not_mutate_input(agent):
    original = _full(agent)
    snapshot = copy.deepcopy(original)
    assess(agent, original)
    assert original == snapshot, f"assess() mutated output for agent '{agent}'"


# ─── Return type guarantees ───────────────────────────────────────────────────

@pytest.mark.parametrize("agent", ALL_AGENTS)
def test_confidence_is_float_in_0_1(agent):
    result = assess(agent, _full(agent))
    assert isinstance(result.confidence, float)
    assert 0.0 <= result.confidence <= 1.0, (
        f"[{agent}] confidence out of range: {result.confidence}"
    )


@pytest.mark.parametrize("agent", ALL_AGENTS)
def test_reason_is_non_empty_string(agent):
    result = assess(agent, _full(agent))
    assert isinstance(result.reason, str) and len(result.reason) > 0, (
        f"[{agent}] reason is empty or not a string"
    )


# ─── Full outputs → strong confidence ─────────────────────────────────────────

@pytest.mark.parametrize("agent", ALL_AGENTS)
def test_full_output_yields_strong_or_moderate_confidence(agent):
    result = assess(agent, _full(agent))
    assert result.confidence >= 0.55, (
        f"[{agent}] expected >= 0.55, got {result.confidence} — reason: {result.reason}"
    )


@pytest.mark.parametrize("agent", ["research", "competitor", "funding", "trend"])
def test_web_agent_with_sources_yields_strong_confidence(agent):
    result = assess(agent, _full(agent))
    assert result.confidence >= 0.75, (
        f"[{agent}] expected >= 0.75 with 3 sources, got {result.confidence}"
    )
    assert result.evidence_strength == "strong"


# ─── None / parse_error → confidence=0.0 / strength="none" ───────────────────

def test_none_output_returns_zero_confidence():
    result = assess("research", None)
    assert result.confidence == 0.0
    assert result.evidence_strength == "none"
    assert "None" in result.reason or "skipped" in result.reason


def test_parse_error_dict_returns_zero_confidence():
    result = assess("swot", {"parse_error": True, "raw_response": "garbage"})
    assert result.confidence == 0.0
    assert result.evidence_strength == "none"
    assert "parse" in result.reason.lower() or "error" in result.reason.lower()


def test_non_dict_output_returns_zero_confidence():
    result = assess("research", "this is not a dict")
    assert result.confidence == 0.0
    assert result.evidence_strength == "none"


# ─── Degraded outputs → lower confidence ─────────────────────────────────────

def test_missing_sources_reduces_confidence():
    full = _full("research")
    degraded = {k: v for k, v in full.items() if k != "sources"}
    full_result    = assess("research", full)
    degraded_result = assess("research", degraded)
    assert degraded_result.confidence < full_result.confidence


def test_empty_sources_reduces_confidence():
    full = _full("competitor")
    degraded = {**full, "sources": []}
    full_result    = assess("competitor", full)
    degraded_result = assess("competitor", degraded)
    assert degraded_result.confidence < full_result.confidence


def test_missing_required_field_reduces_confidence():
    full = _full("swot")
    degraded = {k: v for k, v in full.items() if k != "strengths"}
    full_result    = assess("swot", full)
    degraded_result = assess("swot", degraded)
    assert degraded_result.confidence < full_result.confidence


def test_empty_lists_reduce_confidence():
    full = _full("risk")
    degraded = {**full, "risks": [], "critical_risks": []}
    full_result    = assess("risk", full)
    degraded_result = assess("risk", degraded)
    assert degraded_result.confidence < full_result.confidence


# ─── Score range violations ───────────────────────────────────────────────────

def test_out_of_range_score_reduces_confidence():
    full = _full("research_gap")
    bad  = {**full, "novelty_score": 150}
    full_result = assess("research_gap", full)
    bad_result  = assess("research_gap", bad)
    assert bad_result.confidence < full_result.confidence


def test_out_of_range_report_scores_reduce_confidence():
    full = _full("report")
    bad  = {**full, "market_score": -10, "opportunity_score": 200}
    full_result = assess("report", full)
    bad_result  = assess("report", bad)
    assert bad_result.confidence < full_result.confidence


# ─── Idea Guard specialised scorer ───────────────────────────────────────────

def test_idea_guard_approved_full_output_is_strong():
    result = assess("idea_guard", _full("idea_guard"))
    assert result.confidence >= 0.80
    assert result.evidence_strength == "strong"


def test_idea_guard_unknown_verdict_reduces_confidence():
    full = _full("idea_guard")
    bad  = {**full, "verdict": "maybe"}
    full_result = assess("idea_guard", full)
    bad_result  = assess("idea_guard", bad)
    assert bad_result.confidence < full_result.confidence
    assert "verdict" in bad_result.reason.lower()


def test_idea_guard_invalid_scores_reduce_confidence():
    full = _full("idea_guard")
    bad  = {**full, "clarity_score": 999, "vagueness_score": -5}
    full_result = assess("idea_guard", full)
    bad_result  = assess("idea_guard", bad)
    assert bad_result.confidence < full_result.confidence


# ─── Innovation scoring specialised scorer ────────────────────────────────────

def test_innovation_scoring_full_output_is_strong():
    result = assess("innovation_scoring", _full("innovation_scoring"))
    assert result.confidence >= 0.80
    assert result.evidence_strength == "strong"


def test_innovation_scoring_missing_grade_reduces_confidence():
    full = _full("innovation_scoring")
    bad  = {**full, "grade": "Z"}   # invalid grade
    full_result = assess("innovation_scoring", full)
    bad_result  = assess("innovation_scoring", bad)
    assert bad_result.confidence < full_result.confidence


def test_innovation_scoring_missing_explanation_reduces_confidence():
    full = _full("innovation_scoring")
    bad  = {**full, "score_explanation": ""}
    full_result = assess("innovation_scoring", full)
    bad_result  = assess("innovation_scoring", bad)
    assert bad_result.confidence < full_result.confidence


# ─── Unknown agent ────────────────────────────────────────────────────────────

def test_unknown_agent_returns_result_without_raising():
    result = assess("future_agent_v42", {"field": [1, 2, 3]})
    assert isinstance(result, ConfidenceResult)
    assert 0.0 <= result.confidence <= 1.0
    assert "unknown" in result.reason.lower()


def test_unknown_agent_empty_dict_returns_weak_or_lower():
    result = assess("future_agent_v42", {})
    assert result.evidence_strength in ("weak", "none")


# ─── evidence_strength thresholds ─────────────────────────────────────────────

def test_strong_threshold():
    result = assess("innovation_scoring", _full("innovation_scoring"))
    assert result.confidence >= 0.80
    assert result.evidence_strength == "strong"


def test_none_threshold_on_parse_error():
    result = assess("research", {"parse_error": True})
    assert result.confidence == 0.0
    assert result.evidence_strength == "none"


# ─── assess_all() ────────────────────────────────────────────────────────────

def test_assess_all_covers_all_known_agents():
    state = {agent: _full(agent) for agent in ALL_AGENTS}
    results = assess_all(state)
    for agent in ALL_AGENTS:
        assert agent in results, f"assess_all() missing agent '{agent}'"


def test_assess_all_handles_none_values():
    state: Dict[str, Any] = {
        "research": _full("research"),
        "competitor": None,
    }
    results = assess_all(state)
    assert results["competitor"].confidence == 0.0
    assert results["competitor"].evidence_strength == "none"


def test_assess_all_does_not_mutate_state():
    state = {agent: _full(agent) for agent in ["research", "swot", "risk"]}
    snapshot = copy.deepcopy(state)
    assess_all(state)
    assert state == snapshot


def test_assess_all_ignores_non_agent_scalar_keys():
    state: Dict[str, Any] = {
        "job_id": "abc-123",
        "idea": "An AI platform",
        "industry": "SaaS",
        "healthcare_mode": False,
        "progress": 100,
        "research": _full("research"),
    }
    results = assess_all(state)
    # Scalar non-agent keys must not appear in results
    assert "job_id" not in results
    assert "idea" not in results
    assert "progress" not in results
    assert "research" in results


def test_assess_all_empty_dict_returns_empty():
    assert assess_all({}) == {}


def test_assess_all_all_full_outputs_are_confident():
    state = {agent: _full(agent) for agent in ALL_AGENTS}
    results = assess_all(state)
    weak = [
        (a, r.confidence, r.reason)
        for a, r in results.items()
        if r.confidence < 0.55
    ]
    assert not weak, f"Unexpectedly low confidence: {weak}"
