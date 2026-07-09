"""
Tests for services/quality_report.py
"""
from __future__ import annotations

import copy
from typing import Any, Dict

import pytest

from services.quality_report import QualityReport, generate


# ─── Pipeline state fixtures ──────────────────────────────────────────────────

def _src(n: int = 3) -> list:
    return [f"https://pubmed.ncbi.nlm.nih.gov/{i}" for i in range(n)]


def _full_state() -> Dict[str, Any]:
    return {
        "job_id":          "test-job",
        "idea":            "AI invoice automation for SMBs",
        "industry":        "FinTech",
        "healthcare_mode": False,
        "progress":        100,
        "idea_guard": {
            "verdict": "approved", "verdict_summary": "Clear viable idea.",
            "clarity_score": 85, "vagueness_score": 15,
            "is_startup_idea": True, "legal_status": "legal",
            "ethical_status": "ethical", "technical_feasibility": "feasible",
            "market_potential": "strong",
            "rejection_reasons": [], "improvement_suggestions": [], "dimension_notes": {},
        },
        "research": {
            "market_overview": "Large growing market.",
            "key_players": ["A", "B"], "market_size_estimate": "$20B",
            "recent_trends": ["AI"], "growth_rate": "18% CAGR",
            "target_customers": ["SMBs"], "pain_points": ["manual work"],
            "summary": "Great opportunity.", "sources": _src(4),
        },
        "competitors": {
            "competitors": [{"name": "Acme"}],
            "competitive_landscape": "Moderate competition.",
            "market_saturation_score": 55,
            "differentiation_opportunities": ["op1"],
            "sources": _src(3),
        },
        "scientific": {
            "relevant_papers": ["Paper A"],
            "research_maturity": "mature", "research_maturity_score": 70,
            "key_findings": ["finding1"], "research_gaps": ["gap1"],
            "academic_consensus": "Supported.", "sources": _src(3),
        },
        "patents": {
            "existing_patents": ["US12345"], "patent_density_score": 35,
            "white_spaces": ["space1"], "freedom_to_operate_risks": ["risk1"],
            "ip_strategy_recommendation": "File provisional.", "sources": _src(2),
        },
        "funding": {
            "recent_funding_rounds": [{"company": "X", "amount": "$5M"}],
            "funding_activity_score": 70, "total_market_funding_estimate": "$1B",
            "top_investors": ["a16z"], "average_valuation_range": "$20M-$80M",
            "funding_trend": "rising", "investor_thesis": "AI-first automation.",
            "sources": _src(3),
        },
        "trends": {
            "trends": ["AI adoption"], "market_growth_rate": "20% CAGR",
            "emerging_technologies": ["LLMs"], "regulatory_trends": ["EU AI Act"],
            "market_forecast": "$50B by 2030", "disruptive_forces": ["OpenAI"],
            "sources": _src(3),
        },
        "research_gaps": {
            "unexplored_opportunities": ["opp1"], "missing_features_in_market": ["feat1"],
            "emerging_niches": ["niche1"], "competitor_blind_spots": ["blind1"],
            "technology_white_spaces": ["white1"], "novelty_score": 75,
            "differentiation_thesis": "Strong diff.", "sources": _src(3),
        },
        "swot": {
            "strengths": ["s1"], "weaknesses": ["w1"],
            "opportunities": ["o1"], "threats": ["t1"],
        },
        "opportunities": {
            "market_gaps": ["gap1"], "target_segments": [{"segment": "SMBs"}],
            "opportunity_score": 72, "blue_ocean_potential": "moderate",
        },
        "risks": {
            "risks": [{"name": "Market risk"}], "overall_risk_level": "medium",
            "risk_score": 38, "critical_risks": ["Market risk"],
            "risk_mitigation_roadmap": "Diversify early.",
        },
        "innovation_score": {
            "innovation_score": 76, "grade": "B",
            "score_explanation": "Strong novelty, moderate saturation.",
        },
        "validation": {
            "challenged_assumptions": [{"assumption": "Users pay", "challenge": "No proof"}],
            "validation_experiments": ["Landing page test"],
            "confidence_level": "medium", "key_risks_identified": ["Low WTP"],
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
            "market_score": 78, "opportunity_score": 72,
            "competition_level": "medium", "recommendations": ["Launch MVP"],
            "key_metrics": {"mrr": "$50K"}, "full_report": "Full report text.",
        },
        "knowledge_graph": {"nodes": [], "links": []},
    }


def _empty_state() -> Dict[str, Any]:
    return {"job_id": "test", "idea": "test", "industry": "tech",
            "healthcare_mode": False}


def _partial_state() -> Dict[str, Any]:
    """State with only 3 agents completed."""
    return {
        "research":  _full_state()["research"],
        "competitors": _full_state()["competitors"],
        "swot":      _full_state()["swot"],
    }


# ─── QualityReport contract ───────────────────────────────────────────────────

def test_quality_report_is_immutable():
    report = generate(_full_state())
    with pytest.raises((AttributeError, TypeError)):
        report.pipeline_quality = 0.0  # type: ignore[misc]


def test_quality_report_to_dict_has_required_keys():
    report = generate(_full_state())
    d = report.to_dict()
    for key in ("pipeline_quality", "hallucination_risk", "missing_evidence",
                "consistency", "overall_grade", "agent_scores",
                "source_credibility", "warnings", "summary"):
        assert key in d


# ─── generate() never mutates state ──────────────────────────────────────────

def test_generate_does_not_mutate_state():
    state    = _full_state()
    snapshot = copy.deepcopy(state)
    generate(state)
    assert state == snapshot


# ─── pipeline_quality ────────────────────────────────────────────────────────

def test_pipeline_quality_is_float_in_0_1():
    report = generate(_full_state())
    assert 0.0 <= report.pipeline_quality <= 1.0


def test_full_pipeline_quality_is_high():
    report = generate(_full_state())
    assert report.pipeline_quality >= 0.60, (
        f"Expected >= 0.60 for full state, got {report.pipeline_quality}"
    )


def test_empty_state_pipeline_quality_is_zero_or_low():
    report = generate(_empty_state())
    assert report.pipeline_quality <= 0.30


def test_partial_state_pipeline_quality_lower_than_full():
    # Partial state has only 3 agents — it must have many more missing agents than full
    full    = generate(_full_state())
    partial = generate(_partial_state())
    assert len(partial.missing_evidence) > len(full.missing_evidence)


# ─── hallucination_risk ──────────────────────────────────────────────────────

def test_hallucination_risk_is_valid_literal():
    report = generate(_full_state())
    assert report.hallucination_risk in ("low", "medium", "high")


def test_full_pipeline_has_low_or_medium_hallucination_risk():
    report = generate(_full_state())
    assert report.hallucination_risk in ("low", "medium")


def test_empty_state_has_high_hallucination_risk():
    report = generate(_empty_state())
    assert report.hallucination_risk == "high"


def test_partial_state_has_higher_risk_than_full():
    full_risk    = generate(_full_state()).hallucination_risk
    partial_risk = generate(_partial_state()).hallucination_risk
    order = {"low": 0, "medium": 1, "high": 2}
    assert order[partial_risk] >= order[full_risk]


# ─── missing_evidence ────────────────────────────────────────────────────────

def test_missing_evidence_is_list():
    report = generate(_full_state())
    assert isinstance(report.missing_evidence, list)


def test_full_state_has_no_missing_evidence():
    # Full state has all core agents (keys match ResearchState: competitors, patents, etc.)
    report = generate(_full_state())
    assert len(report.missing_evidence) == 0, (
        f"Unexpected missing agents: {report.missing_evidence}"
    )


def test_empty_state_has_many_missing_agents():
    report = generate(_empty_state())
    assert len(report.missing_evidence) >= 10


def test_partial_state_lists_missing_agents():
    report = generate(_partial_state())
    assert len(report.missing_evidence) > 5


def test_parse_error_output_is_counted_as_missing():
    state = {
        "research":    {"parse_error": True},
        "competitors": _full_state()["competitors"],
    }
    report = generate(state)
    assert "research" in report.missing_evidence


# ─── consistency ─────────────────────────────────────────────────────────────

def test_consistency_is_float_in_0_1():
    report = generate(_full_state())
    assert 0.0 <= report.consistency <= 1.0


def test_consistent_scores_yield_high_consistency():
    """All scores set to ~50 → very consistent."""
    state = {
        "competitors":         {"market_saturation_score": 50, "competitors": ["x"],
                                "competitive_landscape": "ok",
                                "differentiation_opportunities": ["op"],
                                "sources": []},
        "scientific":          {"research_maturity_score": 52, "relevant_papers": ["p"],
                                "research_maturity": "ok", "key_findings": ["f"],
                                "research_gaps": ["g"], "academic_consensus": "ok",
                                "sources": []},
        "patents":             {"patent_density_score": 48, "existing_patents": ["p"],
                                "white_spaces": ["w"], "freedom_to_operate_risks": ["r"],
                                "ip_strategy_recommendation": "File now.", "sources": []},
        "innovation_score":    {"innovation_score": 51, "grade": "C",
                                "score_explanation": "Average innovation score."},
    }
    report = generate(state)
    assert report.consistency >= 0.70, f"Expected >= 0.70, got {report.consistency}"


def test_wildly_inconsistent_scores_yield_lower_consistency():
    """Scores ranging from 5 to 95 → lower consistency than scores all near 50."""
    inconsistent_state = {
        "competitors":      {"market_saturation_score": 5,  "competitors": [], "competitive_landscape": "x",
                             "differentiation_opportunities": [], "sources": []},
        "scientific":       {"research_maturity_score": 95, "relevant_papers": [], "research_maturity": "x",
                             "key_findings": [], "research_gaps": [], "academic_consensus": "x", "sources": []},
        "patents":          {"patent_density_score": 5,  "existing_patents": [], "white_spaces": [],
                             "freedom_to_operate_risks": [], "ip_strategy_recommendation": "ok", "sources": []},
        "risks":            {"risks": [], "overall_risk_level": "low", "risk_score": 95,
                             "critical_risks": [], "risk_mitigation_roadmap": "none."},
        "innovation_score": {"innovation_score": 50, "grade": "C", "score_explanation": "mid."},
    }
    consistent_state = {
        "competitors":      {"market_saturation_score": 50, "competitors": [], "competitive_landscape": "x",
                             "differentiation_opportunities": [], "sources": []},
        "scientific":       {"research_maturity_score": 52, "relevant_papers": [], "research_maturity": "x",
                             "key_findings": [], "research_gaps": [], "academic_consensus": "x", "sources": []},
        "patents":          {"patent_density_score": 51, "existing_patents": [], "white_spaces": [],
                             "freedom_to_operate_risks": [], "ip_strategy_recommendation": "ok", "sources": []},
        "risks":            {"risks": [], "overall_risk_level": "medium", "risk_score": 49,
                             "critical_risks": [], "risk_mitigation_roadmap": "none."},
        "innovation_score": {"innovation_score": 51, "grade": "C", "score_explanation": "mid."},
    }
    inconsistent = generate(inconsistent_state).consistency
    consistent   = generate(consistent_state).consistency
    assert inconsistent < consistent, (
        f"Expected inconsistent ({inconsistent}) < consistent ({consistent})"
    )


# ─── overall_grade ───────────────────────────────────────────────────────────

def test_overall_grade_is_valid():
    report = generate(_full_state())
    assert report.overall_grade in ("A", "B", "C", "D", "F")


def test_full_pipeline_grade_is_not_f():
    report = generate(_full_state())
    assert report.overall_grade != "F"


def test_empty_state_grade_is_f():
    report = generate(_empty_state())
    assert report.overall_grade == "F"


# ─── agent_scores ────────────────────────────────────────────────────────────

def test_agent_scores_values_in_0_1():
    report = generate(_full_state())
    for agent, score in report.agent_scores.items():
        assert 0.0 <= score <= 1.0, f"[{agent}] score out of range: {score}"


# ─── source_credibility ──────────────────────────────────────────────────────

def test_source_credibility_is_float_in_0_1():
    report = generate(_full_state())
    assert 0.0 <= report.source_credibility <= 1.0


def test_pubmed_sources_yield_high_credibility():
    state = {
        "research": {
            "market_overview": "Large market.", "key_players": ["A"],
            "market_size_estimate": "$10B", "recent_trends": ["t"],
            "growth_rate": "15%", "target_customers": ["SMBs"],
            "pain_points": ["p"], "summary": "Good.",
            "sources": [f"https://pubmed.ncbi.nlm.nih.gov/{i}" for i in range(4)],
        }
    }
    report = generate(state)
    assert report.source_credibility == 1.0


def test_no_sources_yields_zero_credibility():
    state = {"swot": {"strengths": ["s"], "weaknesses": ["w"],
                      "opportunities": ["o"], "threats": ["t"]}}
    report = generate(state)
    assert report.source_credibility == 0.0


# ─── warnings ────────────────────────────────────────────────────────────────

def test_warnings_is_list_of_strings():
    report = generate(_full_state())
    assert isinstance(report.warnings, list)
    assert all(isinstance(w, str) for w in report.warnings)


def test_degraded_output_produces_warnings():
    state = {
        "research": {
            "market_overview": "",   # empty required field
            "sources": [],
        }
    }
    report = generate(state)
    assert len(report.warnings) > 0


# ─── summary ─────────────────────────────────────────────────────────────────

def test_summary_is_non_empty_string():
    report = generate(_full_state())
    assert isinstance(report.summary, str) and len(report.summary) > 20


def test_summary_mentions_grade():
    report = generate(_full_state())
    assert report.overall_grade in report.summary


def test_summary_mentions_hallucination_risk():
    report = generate(_full_state())
    assert "hallucination" in report.summary.lower()
