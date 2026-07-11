"""
Regression tests for innovation scoring provenance and consistency checks.

Tests the 16 scenarios from the audit spec (Part 13):

 1. Three different ideas produce different sub-scores (mock fixtures)
 2. Missing upstream field → None (not 48 / not 50)
 3. All-identical scores → consistency_warnings populated
 4. Low score coverage (< 70%) → is_provisional = True
 5. grade must match final_score numerically
 6. Consistency checker detects score mismatch between innovation and report
 7. Consistency checker detects opportunity mismatch
 8. _get_score: valid score returns (value, "available")
 9. _get_score: missing field returns (None, "missing")
10. _get_score: out-of-range value returns (None, "out_of_range")
11. _get_score: non-numeric returns (None, "parse_error")
12. _get_score: empty dict returns (None, "agent_failed")
13. Renormalization: final score uses available_weight, not total weight
14. Evidence multiplier high quality → 1.0
15. Evidence multiplier with hallucination flags → reduced multiplier
16. Score breakdown contains per-dimension provenance fields
"""
from __future__ import annotations

import asyncio
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _make_state(
    novelty: Any = 75,
    saturation: Any = 40,
    funding: Any = 60,
    maturity: Any = 55,
    patent: Any = 30,
    eq: str = "high",
) -> Dict[str, Any]:
    """Build a minimal ResearchState for the scoring agent."""
    return {
        "job_id": "test-job",
        "idea": "Test idea",
        "industry": "SaaS",
        "research_gaps": {
            "novelty_score": novelty,
            "evidence_quality": eq,
        },
        "competitors": {
            "market_saturation_score": saturation,
            "evidence_quality": eq,
        },
        "funding": {
            "funding_activity_score": funding,
            "evidence_quality": eq,
        },
        "scientific": {
            "research_maturity_score": maturity,
            "evidence_quality": eq,
        },
        "patents": {
            "patent_density_score": patent,
            "evidence_quality": eq,
        },
    }


async def _run(state: Dict[str, Any]) -> Dict[str, Any]:
    """Call the innovation scoring agent with a mocked LLM."""
    with patch(
        "agents.innovation_scoring_agent.call_llm",
        new_callable=AsyncMock,
        return_value="Good idea with solid fundamentals.",
    ):
        from agents.innovation_scoring_agent import run
        return await run(state)


# ─── Test 8–12: _get_score unit tests ────────────────────────────────────────

def test_get_score_valid():
    from agents.innovation_scoring_agent import _get_score
    val, status = _get_score({"novelty_score": 75}, "novelty_score")
    assert status == "available"
    assert val == 75.0


def test_get_score_missing():
    from agents.innovation_scoring_agent import _get_score
    val, status = _get_score({"other_field": 50}, "novelty_score")
    assert status == "missing"
    assert val is None


def test_get_score_out_of_range():
    from agents.innovation_scoring_agent import _get_score
    val, status = _get_score({"novelty_score": 150}, "novelty_score")
    assert status == "out_of_range"
    assert val is None


def test_get_score_non_numeric():
    from agents.innovation_scoring_agent import _get_score
    val, status = _get_score({"novelty_score": "high"}, "novelty_score")
    assert status == "parse_error"
    assert val is None


def test_get_score_empty_dict():
    from agents.innovation_scoring_agent import _get_score
    # An empty dict means the agent produced no output → agent_failed (not just missing)
    val, status = _get_score({}, "novelty_score")
    assert status == "agent_failed"
    assert val is None


def test_get_score_agent_failed():
    from agents.innovation_scoring_agent import _get_score
    val, status = _get_score({"parse_error": True}, "novelty_score")
    assert status == "agent_failed"
    assert val is None


# ─── Test 14–15: evidence multiplier ─────────────────────────────────────────

def test_evidence_multiplier_high_quality():
    from agents.innovation_scoring_agent import _evidence_multiplier
    mult, eq = _evidence_multiplier({"evidence_quality": "high"})
    assert mult == 1.0
    assert eq == "high"


def test_evidence_multiplier_with_flags():
    from agents.innovation_scoring_agent import _evidence_multiplier
    flags = [{"claim": "x", "status": "Weak", "score": 0.2}] * 3
    mult, _ = _evidence_multiplier({
        "evidence_quality": "medium",
        "_hallucination_flags": flags,
    })
    # medium penalty=0.05, 3 flags × 0.10 = 0.30 (capped) → 1.0 - 0.05 - 0.30 = 0.65
    assert mult == pytest.approx(0.65, abs=0.01)


# ─── Test 2: missing field → None ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_missing_upstream_field_returns_null():
    """Missing source score must produce status='missing' in breakdown, not 50."""
    state = _make_state()
    del state["research_gaps"]["novelty_score"]   # remove novelty_score
    result = await _run(state)

    novelty_dim = next(
        (d for d in result["score_breakdown"] if d["dimension"] == "novelty"),
        None,
    )
    assert novelty_dim is not None
    assert novelty_dim["raw_value"] is None
    assert novelty_dim["status"] == "missing"
    # Legacy flat dict must also be None (not 50 or 48)
    assert result["scores"].get("novelty") is None


# ─── Test 3: all-identical scores → warning ───────────────────────────────────

@pytest.mark.asyncio
async def test_identical_scores_trigger_warning():
    """When all 5 raw scores are the same value, consistency_warnings must be set."""
    state = _make_state(
        novelty=50, saturation=50, funding=50, maturity=50, patent=50
    )
    result = await _run(state)
    assert any(
        "SUSPICIOUS_IDENTICAL_SCORES" in w
        for w in result.get("consistency_warnings", [])
    ), f"Expected identical-score warning, got: {result.get('consistency_warnings')}"


# ─── Test 4: low score coverage → provisional ────────────────────────────────

@pytest.mark.asyncio
async def test_low_coverage_marks_provisional():
    """If only 1 of 5 dimensions is available, score_coverage < 0.70 → is_provisional."""
    state = _make_state(
        novelty=None, saturation=None, funding=None, maturity=None, patent=30
    )
    # Remove all score fields except patent
    for key in ["research_gaps", "competitors", "funding", "scientific"]:
        state[key] = {"evidence_quality": "high"}  # no score field
    result = await _run(state)
    assert result["is_provisional"] is True
    assert result["score_coverage"] < 0.70


# ─── Test 5: grade matches score ──────────────────────────────────────────────

@pytest.mark.asyncio
@pytest.mark.parametrize("novelty,saturation,funding,maturity,patent,expected_grade", [
    (90, 10, 90, 90, 10, "A"),   # Very high scores → A
    (40, 70, 30, 30, 80, "D"),   # Very low scores → D
])
async def test_grade_matches_score(novelty, saturation, funding, maturity, patent, expected_grade):
    state = _make_state(novelty=novelty, saturation=saturation, funding=funding,
                        maturity=maturity, patent=patent, eq="high")
    result = await _run(state)
    score = result["innovation_score"]
    grade = result["grade"]
    if score is not None:
        if score >= 80:
            assert grade == "A"
        elif score >= 65:
            assert grade == "B"
        elif score >= 50:
            assert grade == "C"
        else:
            assert grade == "D"


# ─── Test 1: different ideas → different scores ───────────────────────────────

@pytest.mark.asyncio
async def test_different_inputs_produce_different_scores():
    """
    Three very different mock agent outputs must produce three different scores.
    This is the core regression for the 'all ideas score 48' bug.
    """
    state_high = _make_state(novelty=90, saturation=10, funding=85, maturity=80, patent=5, eq="high")
    state_mid  = _make_state(novelty=55, saturation=55, funding=50, maturity=45, patent=50, eq="medium")
    state_low  = _make_state(novelty=20, saturation=90, funding=15, maturity=10, patent=90, eq="low")

    r_high, r_mid, r_low = await asyncio.gather(
        _run(state_high), _run(state_mid), _run(state_low)
    )

    scores = [r_high["innovation_score"], r_mid["innovation_score"], r_low["innovation_score"]]
    assert scores[0] > scores[1] > scores[2], (
        f"Expected descending scores but got: {scores}. "
        "Different inputs must produce different scores."
    )


# ─── Test 13: renormalization ─────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_renormalization_with_missing_dimensions():
    """
    When one dimension is missing, the score is renormalized by available_weight
    so the result is not dragged artificially low.
    """
    # Remove funding (weight=0.15). Expected available_weight = 0.85
    state_full    = _make_state(novelty=70, saturation=30, funding=70, maturity=70, patent=30, eq="high")
    state_missing = _make_state(novelty=70, saturation=30, funding=70, maturity=70, patent=30, eq="high")
    state_missing["funding"] = {"evidence_quality": "high"}  # no funding_activity_score

    r_full    = await _run(state_full)
    r_missing = await _run(state_missing)

    # With renormalization, missing one dimension should give a similar score,
    # not a score that's 15% lower.
    if r_full["innovation_score"] and r_missing["innovation_score"]:
        diff = abs(r_full["innovation_score"] - r_missing["innovation_score"])
        assert diff <= 10, (
            f"Renormalized score should be close to full score. "
            f"full={r_full['innovation_score']}, missing={r_missing['innovation_score']}, diff={diff}"
        )


# ─── Test 16: breakdown contains provenance ───────────────────────────────────

@pytest.mark.asyncio
async def test_score_breakdown_contains_provenance():
    """Each dimension in score_breakdown must have all required provenance fields."""
    required_fields = {
        "dimension", "source_agent", "source_field", "inverted",
        "raw_value", "evidence_multiplier", "adjusted_value",
        "weight", "weighted_contribution", "evidence_quality",
        "source_count", "unsupported_claims", "status", "warnings",
    }
    state = _make_state()
    result = await _run(state)
    for dim in result["score_breakdown"]:
        missing = required_fields - set(dim.keys())
        assert not missing, f"Dimension '{dim.get('dimension')}' missing fields: {missing}"


# ─── Consistency checker tests ────────────────────────────────────────────────

def test_consistency_checker_detects_innovation_mismatch():
    """Consistency checker must flag innovation/report score gap > 15."""
    from services.consistency_checker import check
    state = {
        "innovation_score": {
            "innovation_score": 80,
            "grade": "A",
            "score_coverage": 1.0,
            "is_provisional": False,
            "score_breakdown": [],
            "consistency_warnings": [],
        },
        "report": {
            "market_score": 50,       # 30-point gap
            "opportunity_score": 75,
        },
        "opportunities": {"opportunity_score": 75},
        "risks": {"overall_risk_level": "medium"},
    }
    result = check(state)
    assert any("SCORE_MISMATCH" in w for w in result.warnings), (
        f"Expected SCORE_MISMATCH warning, got: {result.warnings}"
    )


def test_consistency_checker_detects_opportunity_mismatch():
    """Consistency checker must flag opportunity score gap > 15."""
    from services.consistency_checker import check
    state = {
        "innovation_score": {
            "innovation_score": 70,
            "grade": "B",
            "score_coverage": 1.0,
            "is_provisional": False,
            "score_breakdown": [],
            "consistency_warnings": [],
        },
        "report": {
            "market_score": 70,
            "opportunity_score": 30,   # large gap from canonical 80
        },
        "opportunities": {"opportunity_score": 80},
        "risks": {"overall_risk_level": "low"},
    }
    result = check(state)
    assert any("SCORE_MISMATCH" in w for w in result.warnings)


def test_consistency_checker_identical_scores_error():
    """Consistency checker must raise an error for identical scores (non-mock mode)."""
    from services.consistency_checker import check
    breakdown = [
        {"source_agent": "research_gaps", "source_field": "novelty_score",
         "status": "available", "raw_value": 50},
        {"source_agent": "competitors",   "source_field": "market_saturation_score",
         "status": "available", "raw_value": 50},
        {"source_agent": "funding",       "source_field": "funding_activity_score",
         "status": "available", "raw_value": 50},
        {"source_agent": "scientific",    "source_field": "research_maturity_score",
         "status": "available", "raw_value": 50},
        {"source_agent": "patents",       "source_field": "patent_density_score",
         "status": "available", "raw_value": 50},
    ]
    state = {
        "innovation_score": {
            "innovation_score": 48,
            "grade": "D",
            "score_coverage": 1.0,
            "is_provisional": False,
            "score_breakdown": breakdown,
            "consistency_warnings": [],
        },
        "report": {},
        "opportunities": {},
        "risks": {},
    }
    result = check(state)
    assert result.suspicious_identical_scores is True
    assert any("SUSPICIOUS_IDENTICAL_SCORES" in e for e in result.errors)
