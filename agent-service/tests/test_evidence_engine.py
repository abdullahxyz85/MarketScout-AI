"""
Tests for services/evidence_engine.py
"""
from __future__ import annotations

import copy
from typing import Any, Dict

import pytest

from services.evidence_engine import Evidence, extract, extract_all, summarise


# ─── Fixtures ─────────────────────────────────────────────────────────────────

def _sources(n: int = 2) -> list:
    return [f"https://example.com/{i}" for i in range(n)]


def _research_output() -> Dict[str, Any]:
    return {
        "market_overview": "The AI market is large and growing rapidly.",
        "market_size_estimate": "$45B globally by 2027",
        "growth_rate": "18% CAGR 2024-2029",
        "recent_trends": ["AI adoption", "Remote work tools"],
        "pain_points": ["High manual effort", "Lack of automation"],
        "target_customers": ["SMBs"],
        "summary": "Strong market opportunity with high growth.",
        "sources": _sources(3),
    }


def _patent_output() -> Dict[str, Any]:
    return {
        "existing_patents": ["US12345 — AI scheduling system"],
        "patent_density_score": 40,
        "white_spaces": ["No patents for SMB-focused scheduling"],
        "freedom_to_operate_risks": ["One broad patent may conflict"],
        "ip_strategy_recommendation": "File a provisional patent immediately.",
        "sources": _sources(2),
    }


def _funding_output() -> Dict[str, Any]:
    return {
        "recent_funding_rounds": [{"company": "Acme", "amount": "$5M Series A"}],
        "funding_activity_score": 70,
        "total_market_funding_estimate": "$500M in 2024",
        "top_investors": ["a16z"],
        "average_valuation_range": "$20M-$80M",
        "funding_trend": "Rising interest from tier-1 VCs",
        "investor_thesis": "AI automation for SMBs is a key trend",
        "sources": _sources(3),
    }


def _swot_output() -> Dict[str, Any]:
    return {
        "strengths": ["Strong product differentiation"],
        "weaknesses": ["Limited sales team"],
        "opportunities": ["Underserved SMB segment"],
        "threats": ["Large incumbents entering market"],
    }


def _idea_guard_output() -> Dict[str, Any]:
    return {
        "verdict": "approved",
        "verdict_summary": "Clear, legal, and technically feasible startup concept.",
        "rejection_reasons": [],
        "improvement_suggestions": ["Consider a narrower target segment"],
    }


# ─── Evidence dataclass contract ──────────────────────────────────────────────

def test_evidence_is_immutable():
    ev = Evidence(claim="Test claim", agent="research",
                  evidence_type="market_data", source_urls=[], strength="strong")
    with pytest.raises((AttributeError, TypeError)):
        ev.claim = "mutated"  # type: ignore[misc]


def test_evidence_to_dict_contains_required_keys():
    ev = Evidence(claim="Test claim about market size",
                  agent="research", evidence_type="market_data",
                  source_urls=["https://x.com"], strength="strong")
    d = ev.to_dict()
    for key in ("claim", "agent", "evidence_type", "source_urls", "strength"):
        assert key in d


# ─── extract() never mutates input ───────────────────────────────────────────

@pytest.mark.parametrize("agent,output_fn", [
    ("research",  _research_output),
    ("patent",    _patent_output),
    ("funding",   _funding_output),
    ("swot",      _swot_output),
    ("idea_guard", _idea_guard_output),
])
def test_extract_does_not_mutate_input(agent, output_fn):
    output   = output_fn()
    snapshot = copy.deepcopy(output)
    extract(agent, output)
    assert output == snapshot


# ─── extract() returns Evidence list ─────────────────────────────────────────

def test_extract_research_returns_evidence_list():
    evidences = extract("research", _research_output())
    assert isinstance(evidences, list)
    assert len(evidences) > 0
    assert all(isinstance(ev, Evidence) for ev in evidences)


def test_extract_research_evidence_has_correct_agent():
    evidences = extract("research", _research_output())
    assert all(ev.agent == "research" for ev in evidences)


def test_extract_research_evidence_has_correct_type():
    evidences = extract("research", _research_output())
    types = {ev.evidence_type for ev in evidences}
    assert "market_data" in types or "trend_data" in types


def test_extract_research_attaches_source_urls():
    evidences = extract("research", _research_output())
    # At least some evidence should carry source URLs
    with_sources = [ev for ev in evidences if ev.source_urls]
    assert len(with_sources) > 0


def test_extract_patent_returns_ip_evidence():
    evidences = extract("patent", _patent_output())
    assert len(evidences) > 0
    assert all(ev.evidence_type == "patent_data" for ev in evidences)


def test_extract_patent_includes_recommendation():
    evidences = extract("patent", _patent_output())
    claims = [ev.claim for ev in evidences]
    assert any("provisional patent" in c.lower() for c in claims)


def test_extract_funding_returns_evidence():
    evidences = extract("funding", _funding_output())
    assert len(evidences) > 0
    assert all(ev.evidence_type == "funding_data" for ev in evidences)


def test_extract_swot_includes_all_quadrants():
    evidences = extract("swot", _swot_output())
    types = {ev.evidence_type for ev in evidences}
    assert "swot_data" in types or "opportunity_data" in types or "risk_data" in types


def test_extract_idea_guard_includes_verdict_summary():
    evidences = extract("idea_guard", _idea_guard_output())
    claims = [ev.claim for ev in evidences]
    assert any("feasible" in c.lower() or "legal" in c.lower() for c in claims)


# ─── Strength values ──────────────────────────────────────────────────────────

def test_evidence_strength_is_valid():
    for agent, output_fn in [("research", _research_output),
                              ("patent", _patent_output),
                              ("swot", _swot_output)]:
        for ev in extract(agent, output_fn()):
            assert ev.strength in ("strong", "moderate", "weak"), (
                f"[{agent}] invalid strength: {ev.strength!r}"
            )


def test_research_with_three_sources_yields_strong_evidence():
    output = _research_output()  # has 3 sources
    evidences = extract("research", output)
    strong = [ev for ev in evidences if ev.strength == "strong"]
    assert len(strong) > 0


# ─── Edge cases ───────────────────────────────────────────────────────────────

def test_extract_none_returns_empty_list():
    assert extract("research", None) == []


def test_extract_parse_error_returns_empty_list():
    assert extract("research", {"parse_error": True}) == []


def test_extract_empty_dict_returns_empty_list():
    assert extract("research", {}) == []


def test_extract_unknown_agent_returns_generic_evidence():
    output = {"description": "This is a new experimental agent output field."}
    evidences = extract("future_agent_v9", output)
    assert isinstance(evidences, list)
    # Should not raise; may return generic evidence or empty list
    assert all(isinstance(ev, Evidence) for ev in evidences)


def test_extract_all_skips_none_outputs():
    state = {
        "research": _research_output(),
        "patent":   None,
        "funding":  _funding_output(),
    }
    evidences = extract_all(state)
    agents = {ev.agent for ev in evidences}
    assert "research" in agents
    assert "patent"   not in agents
    assert "funding"  in agents


def test_extract_all_does_not_mutate_state():
    state = {
        "research": _research_output(),
        "swot":     _swot_output(),
    }
    snapshot = copy.deepcopy(state)
    extract_all(state)
    assert state == snapshot


def test_extract_all_respects_max_per_agent():
    state = {"research": _research_output(), "funding": _funding_output()}
    evidences = extract_all(state, max_per_agent=2)
    per_agent: Dict[str, int] = {}
    for ev in evidences:
        per_agent[ev.agent] = per_agent.get(ev.agent, 0) + 1
    for agent, count in per_agent.items():
        assert count <= 2, f"[{agent}] exceeded max_per_agent: {count}"


# ─── summarise() ─────────────────────────────────────────────────────────────

def test_summarise_returns_required_keys():
    evidences = extract("research", _research_output())
    s = summarise(evidences)
    for key in ("total", "by_type", "by_strength", "by_agent", "strong_claims"):
        assert key in s


def test_summarise_total_matches_evidence_count():
    evidences = extract("research", _research_output())
    s = summarise(evidences)
    assert s["total"] == len(evidences)


def test_summarise_strong_claims_are_strings():
    evidences = extract_all({
        "research": _research_output(),
        "patent":   _patent_output(),
    })
    s = summarise(evidences)
    assert all(isinstance(c, str) for c in s["strong_claims"])


def test_summarise_empty_list():
    s = summarise([])
    assert s["total"] == 0
    assert s["strong_claims"] == []
