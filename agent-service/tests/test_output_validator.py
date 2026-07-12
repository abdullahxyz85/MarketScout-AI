"""
Tests for services/output_validator.py

Contract under test:
  - Never modifies input data
  - Returns status="pass" when output is correct
  - Returns status="warning" when output is degraded
  - Warnings are human-readable strings
  - validate_all() handles a full state dict
"""
from __future__ import annotations

import copy
from typing import Any, Dict

import pytest

from services.output_validator import ValidationResult, validate, validate_all


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _sources(n: int = 2) -> list:
    return [f"https://example.com/{i}" for i in range(n)]


def _good(agent: str) -> Dict[str, Any]:
    """Return a minimal but valid output for each agent."""
    outputs = {
        "idea_guard": {
            "verdict": "approved",
            "verdict_summary": "Clear, ethical startup idea.",
            "clarity_score": 80,
            "vagueness_score": 20,
            "is_startup_idea": True,
            "legal_status": "legal",
            "ethical_status": "ethical",
            "technical_feasibility": "feasible",
            "market_potential": "strong",
            "rejection_reasons": [],
            "improvement_suggestions": [],
            "dimension_notes": {},
        },
        "research": {
            "market_overview": "Large growing market.",
            "key_players": ["Company A", "Company B"],
            "market_size_estimate": "$10B",
            "recent_trends": ["trend1"],
            "growth_rate": "15% CAGR",
            "target_customers": ["SMBs"],
            "pain_points": ["pain1"],
            "summary": "Strong market.",
            "sources": _sources(),
        },
        "competitor": {
            "competitors": [{"name": "Acme", "description": "desc"}],
            "competitive_landscape": "Moderately competitive.",
            "market_saturation_score": 55,
            "differentiation_opportunities": ["op1"],
            "sources": _sources(),
        },
        "scientific": {
            "relevant_papers": ["Paper A"],
            "research_maturity": "mature",
            "research_maturity_score": 70,
            "key_findings": ["finding1"],
            "research_gaps": ["gap1"],
            "academic_consensus": "Supported.",
            "sources": _sources(),
        },
        "patent": {
            "existing_patents": ["US12345"],
            "patent_density_score": 40,
            "white_spaces": ["space1"],
            "freedom_to_operate_risks": ["risk1"],
            "ip_strategy_recommendation": "File a provisional patent.",
            "sources": _sources(),
        },
        "funding": {
            "recent_funding_rounds": [{"company": "X", "amount": "$5M"}],
            "funding_activity_score": 65,
            "total_market_funding_estimate": "$500M",
            "top_investors": ["a16z"],
            "average_valuation_range": "$10M-$50M",
            "funding_trend": "rising",
            "investor_thesis": "AI-first automation.",
            "sources": _sources(),
        },
        "trend": {
            "trends": ["AI adoption"],
            "market_growth_rate": "20% CAGR",
            "emerging_technologies": ["LLMs"],
            "regulatory_trends": ["EU AI Act"],
            "market_forecast": "$50B by 2030",
            "disruptive_forces": ["OpenAI"],
            "sources": _sources(),
        },
        "research_gap": {
            "unexplored_opportunities": ["opp1"],
            "missing_features_in_market": ["feature1"],
            "emerging_niches": ["niche1"],
            "competitor_blind_spots": ["blind1"],
            "technology_white_spaces": ["white1"],
            "novelty_score": 72,
            "differentiation_thesis": "Strong.",
            "sources": _sources(),
        },
        "swot": {
            "strengths": ["s1"],
            "weaknesses": ["w1"],
            "opportunities": ["o1"],
            "threats": ["t1"],
        },
        "opportunity": {
            "market_gaps": ["gap1"],
            "target_segments": [{"segment": "SMBs"}],
            "opportunity_score": 68,
            "blue_ocean_potential": "moderate",
        },
        "risk": {
            "risks": [{"name": "Market risk", "category": "market", "severity": "medium"}],
            "overall_risk_level": "medium",
            "risk_score": 40,
            "critical_risks": ["Market risk"],
            "risk_mitigation_roadmap": "Diversify early.",
        },
        "innovation_scoring": {
            "innovation_score": 73,
            "grade": "B",
            "score_explanation": "Strong novelty, moderate market.",
            "score_breakdown": [
                {"dimension": "novelty", "source_agent": "research_gaps",
                 "source_field": "novelty_score", "raw_value": 75,
                 "status": "available", "weight": 0.25,
                 "adjusted_value": 71.25, "weighted_contribution": 17.81,
                 "evidence_multiplier": 0.95, "evidence_quality": "medium",
                 "source_count": 3, "unsupported_claims": 0,
                 "inverted": False, "warnings": []},
            ],
        },
        "validation": {
            "challenged_assumptions": [{"assumption": "Users will pay", "challenge": "No proven demand"}],
            "validation_experiments": ["Run a landing page test"],
            "confidence_level": "medium",
            "key_risks_identified": ["Low willingness to pay"],
            "recommendation": "Run a 30-day pilot.",
        },
        "strategy": {
            "strategic_recommendations": ["Launch in SMB segment first"],
            "innovation_hypotheses": ["AI reduces manual work 80%"],
            "go_to_market": "Direct sales + product-led growth",
            "competitive_positioning": "Premium quality at mid price",
            "pricing_strategy": "Per-seat SaaS",
            "key_partnerships": ["Salesforce"],
            "success_metrics": ["MRR", "NPS"],
            "roadmap": [{"phase": "1", "goal": "MVP"}],
        },
        "report": {
            "executive_summary": "Promising startup.",
            "market_score": 75,
            "opportunity_score": 70,
            "competition_level": "medium",
            "recommendations": ["Launch MVP in Q3"],
            "key_metrics": {"mrr_target": "$50K"},
            "full_report": "Full markdown report...",
        },
    }
    return outputs[agent]


# ─── ValidationResult contract ────────────────────────────────────────────────

def test_validation_result_pass_is_truthy():
    r = ValidationResult(status="pass", warnings=[])
    assert bool(r) is True


def test_validation_result_warning_is_falsy():
    r = ValidationResult(status="warning", warnings=["something wrong"])
    assert bool(r) is False


def test_validation_result_is_immutable():
    r = ValidationResult(status="pass", warnings=[])
    with pytest.raises((AttributeError, TypeError)):
        r.status = "warning"  # type: ignore[misc]


# ─── validate() never mutates input ───────────────────────────────────────────

@pytest.mark.parametrize("agent", list(_good.__code__.co_consts) if False else [
    "idea_guard", "research", "competitor", "scientific", "patent",
    "funding", "trend", "research_gap", "swot", "opportunity",
    "risk", "innovation_scoring", "validation", "strategy", "report",
])
def test_validate_does_not_mutate_input(agent):
    original = _good(agent)
    snapshot = copy.deepcopy(original)
    validate(agent, original)
    assert original == snapshot, f"validate() mutated the output for agent '{agent}'"


# ─── All agents: valid output → pass ─────────────────────────────────────────

@pytest.mark.parametrize("agent", [
    "idea_guard", "research", "competitor", "scientific", "patent",
    "funding", "trend", "research_gap", "swot", "opportunity",
    "risk", "innovation_scoring", "validation", "strategy", "report",
])
def test_valid_output_returns_pass(agent):
    result = validate(agent, _good(agent))
    assert result.status == "pass", f"[{agent}] Expected pass, got warnings: {result.warnings}"
    assert result.warnings == []


# ─── parse_error outputs ──────────────────────────────────────────────────────

def test_parse_error_flag_returns_warning():
    result = validate("research", {"parse_error": True, "raw_response": "not json"})
    assert result.status == "warning"
    assert any("parse" in w.lower() or "unparseable" in w.lower() for w in result.warnings)


def test_non_dict_output_returns_warning():
    result = validate("research", "this is a string not a dict")
    assert result.status == "warning"
    assert any("not a dict" in w for w in result.warnings)


def test_none_output_returns_warning():
    result = validate("research", None)
    assert result.status == "warning"


# ─── Missing required fields ──────────────────────────────────────────────────

def test_missing_required_field_returns_warning():
    output = _good("research")
    del output["market_overview"]
    result = validate("research", output)
    assert result.status == "warning"
    assert any("market_overview" in w for w in result.warnings)


def test_none_required_field_returns_warning():
    output = _good("competitor")
    output["competitive_landscape"] = None
    result = validate("competitor", output)
    assert result.status == "warning"
    assert any("competitive_landscape" in w for w in result.warnings)


def test_empty_string_required_field_returns_warning():
    output = _good("risk")
    output["risk_mitigation_roadmap"] = ""
    result = validate("risk", output)
    assert result.status == "warning"
    assert any("risk_mitigation_roadmap" in w for w in result.warnings)


def test_empty_list_required_field_returns_warning():
    output = _good("swot")
    output["strengths"] = []
    result = validate("swot", output)
    assert result.status == "warning"
    assert any("strengths" in w for w in result.warnings)


# ─── Score range validation ───────────────────────────────────────────────────

@pytest.mark.parametrize("bad_score", [-1, 101, 999, -0.5])
def test_score_out_of_range_returns_warning(bad_score):
    output = _good("research_gap")
    output["novelty_score"] = bad_score
    result = validate("research_gap", output)
    assert result.status == "warning"
    assert any("novelty_score" in w for w in result.warnings)


@pytest.mark.parametrize("good_score", [0, 1, 50, 99, 100])
def test_score_at_boundary_passes(good_score):
    output = _good("innovation_scoring")
    output["innovation_score"] = good_score
    result = validate("innovation_scoring", output)
    assert result.status == "pass"


def test_non_numeric_score_returns_warning():
    output = _good("competitor")
    output["market_saturation_score"] = "high"
    result = validate("competitor", output)
    assert result.status == "warning"
    assert any("market_saturation_score" in w for w in result.warnings)


def test_idea_guard_scores_validated():
    output = _good("idea_guard")
    output["clarity_score"] = 150   # out of range
    result = validate("idea_guard", output)
    assert result.status == "warning"
    assert any("clarity_score" in w for w in result.warnings)


# ─── Sources validation ───────────────────────────────────────────────────────

def test_missing_sources_returns_warning_for_web_search_agent():
    output = _good("research")
    del output["sources"]
    result = validate("research", output)
    assert result.status == "warning"
    assert any("sources" in w for w in result.warnings)


def test_empty_sources_returns_warning():
    output = _good("competitor")
    output["sources"] = []
    result = validate("competitor", output)
    assert result.status == "warning"
    assert any("sources" in w.lower() for w in result.warnings)


def test_non_list_sources_returns_warning():
    output = _good("funding")
    output["sources"] = "https://example.com"
    result = validate("funding", output)
    assert result.status == "warning"
    assert any("sources" in w for w in result.warnings)


def test_sources_not_checked_for_swot_agent():
    """SWOT agent does no web search — sources check must not fire."""
    output = _good("swot")
    result = validate("swot", output)
    assert result.status == "pass"


def test_sources_not_checked_for_report_agent():
    output = _good("report")
    result = validate("report", output)
    assert result.status == "pass"


# ─── Citations (non-empty list fields) ───────────────────────────────────────

def test_all_list_fields_empty_returns_warning():
    output = _good("swot")
    output["strengths"] = []
    output["weaknesses"] = []
    output["opportunities"] = []
    output["threats"] = []
    result = validate("swot", output)
    assert result.status == "warning"


def test_at_least_one_list_item_passes_citation_check():
    output = _good("strategy")
    result = validate("strategy", output)
    assert result.status == "pass"


# ─── Unknown agent ────────────────────────────────────────────────────────────

def test_unknown_agent_returns_warning_with_no_schema_message():
    result = validate("totally_unknown_agent", {"some_field": "value"})
    assert result.status == "warning"
    assert any("no schema" in w.lower() for w in result.warnings)


def test_unknown_agent_does_not_raise():
    result = validate("future_agent_v99", {"data": [1, 2, 3]})
    assert isinstance(result, ValidationResult)


# ─── validate_all() ───────────────────────────────────────────────────────────

def test_validate_all_skips_none_values():
    state = {
        "research": _good("research"),
        "competitor": None,          # not run yet
        "scientific": None,
    }
    results = validate_all(state)
    assert "research" in results
    assert "competitor" not in results
    assert "scientific" not in results


def test_validate_all_returns_pass_for_all_good_outputs():
    state = {
        "research": _good("research"),
        "swot": _good("swot"),
        "risk": _good("risk"),
    }
    results = validate_all(state)
    assert all(r.status == "pass" for r in results.values())


def test_validate_all_returns_warning_for_bad_output():
    bad_research = _good("research")
    bad_research["market_overview"] = ""          # empty required field
    state = {
        "research": bad_research,
        "swot": _good("swot"),
    }
    results = validate_all(state)
    assert results["research"].status == "warning"
    assert results["swot"].status == "pass"


def test_validate_all_does_not_mutate_state():
    state = {
        "research": _good("research"),
        "competitor": _good("competitor"),
    }
    snapshot = copy.deepcopy(state)
    validate_all(state)
    assert state == snapshot


def test_validate_all_empty_dict_returns_empty_results():
    results = validate_all({})
    assert results == {}
