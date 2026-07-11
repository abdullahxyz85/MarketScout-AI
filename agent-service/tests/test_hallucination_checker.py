"""
Tests for services/hallucination_checker.py

Contract under test:
  - Never modifies inputs (claims, sources)
  - status is always "Supported" | "Weak" | "Unknown"
  - score is always float in [0.0, 1.0]
  - matched_sources contains only valid 0-based indices
  - reason is always a non-empty string
  - Supported when claim keywords appear strongly in sources
  - Weak when partial overlap
  - Unknown when no overlap / no sources / empty claim
  - extract_claims() extracts string claims from agent output dicts
  - check_claims() returns one result per claim in order
"""
from __future__ import annotations

import copy
from typing import Any, Dict, List

import pytest

from services.hallucination_checker import (
    SUPPORTED, WEAK, UNKNOWN,
    CheckResult,
    check,
    check_claims,
    extract_claims,
)


# ─── Source fixtures ──────────────────────────────────────────────────────────

def _src(content: str, title: str = "Source", url: str = "https://example.com") -> Dict[str, Any]:
    return {"content": content, "title": title, "url": url}


STRONG_SOURCE = _src(
    "The global AI market size is estimated at $45 billion in 2024, "
    "growing at 18% CAGR through 2029. Key players include OpenAI, "
    "Microsoft, and Google. Healthcare AI adoption is accelerating with "
    "FDA approvals for diagnostic tools increasing year over year.",
    title="AI Market Report 2024",
)

WEAK_SOURCE = _src(
    "Technology markets are growing. Investors are interested in AI. "
    "The sector shows promising trends.",
    title="Generic Tech Overview",
)

UNRELATED_SOURCE = _src(
    "Rainfall patterns in the Amazon basin changed significantly during El Niño. "
    "Agricultural output in Brazil fell 12% in Q3. Soybean exports declined.",
    title="Agriculture Report",
)


# ─── CheckResult contract ─────────────────────────────────────────────────────

def test_check_result_is_immutable():
    r = CheckResult(status=SUPPORTED, score=0.9, matched_sources=[0], reason="ok")
    with pytest.raises((AttributeError, TypeError)):
        r.status = WEAK  # type: ignore[misc]


def test_check_result_status_type():
    r = check("AI market is $45B", [STRONG_SOURCE])
    assert r.status in (SUPPORTED, WEAK, UNKNOWN)


def test_check_result_score_in_0_1():
    r = check("AI market is $45B", [STRONG_SOURCE])
    assert 0.0 <= r.score <= 1.0


def test_check_result_reason_is_non_empty_string():
    r = check("AI market is $45B", [STRONG_SOURCE])
    assert isinstance(r.reason, str) and len(r.reason) > 0


def test_matched_sources_are_valid_indices():
    sources = [STRONG_SOURCE, WEAK_SOURCE, UNRELATED_SOURCE]
    r = check("AI market growth 18% CAGR 2024", sources)
    for idx in r.matched_sources:
        assert 0 <= idx < len(sources)


# ─── check() never mutates inputs ────────────────────────────────────────────

def test_check_does_not_mutate_claim():
    claim = "The AI market is $45B in 2024"
    original = claim
    check(claim, [STRONG_SOURCE])
    assert claim == original


def test_check_does_not_mutate_sources():
    sources = [copy.deepcopy(STRONG_SOURCE), copy.deepcopy(WEAK_SOURCE)]
    snapshot = copy.deepcopy(sources)
    check("AI market growth", sources)
    assert sources == snapshot


# ─── Status: Supported ────────────────────────────────────────────────────────

def test_strong_keyword_overlap_returns_supported():
    r = check(
        "The global AI market is growing at 18% CAGR",
        [STRONG_SOURCE],
    )
    assert r.status == SUPPORTED
    assert r.score >= 0.60


def test_factual_dollar_amount_in_source_returns_supported():
    r = check("Market size $45 billion in 2024", [STRONG_SOURCE])
    assert r.status == SUPPORTED


def test_multiple_sources_one_strong_match_returns_supported():
    sources = [UNRELATED_SOURCE, STRONG_SOURCE]
    r = check("AI market growth 18% CAGR 2024", sources)
    assert r.status == SUPPORTED
    # The strong source index (1) should be in matched_sources
    assert 1 in r.matched_sources


def test_supported_result_reason_mentions_source_count():
    r = check("AI market $45 billion 2024", [STRONG_SOURCE])
    assert r.status == SUPPORTED
    assert "source" in r.reason.lower()


# ─── Status: Weak ─────────────────────────────────────────────────────────────

def test_partial_overlap_returns_weak():
    # The claim has keywords that appear in WEAK_SOURCE ("AI", "technology", "market")
    # but also specific factual tokens ($45B, 2029) that are NOT in WEAK_SOURCE,
    # so the overall score should land in the Weak band [0.25, 0.60).
    r = check(
        "AI technology market growing $45B revenue by 2029",
        [WEAK_SOURCE],
    )
    assert r.status == WEAK
    assert 0.25 <= r.score < 0.60


def test_weak_result_reason_mentions_partial():
    r = check("AI technology market growing $45B revenue by 2029", [WEAK_SOURCE])
    assert r.status == WEAK
    assert "partial" in r.reason.lower() or "insufficient" in r.reason.lower()


def test_weak_score_is_below_supported_threshold():
    r = check("AI technology market growing $45B revenue by 2029", [WEAK_SOURCE])
    assert r.score < 0.60


# ─── Status: Unknown ──────────────────────────────────────────────────────────

def test_empty_claim_returns_unknown():
    r = check("", [STRONG_SOURCE])
    assert r.status == UNKNOWN
    assert r.score == 0.0
    assert r.matched_sources == []


def test_whitespace_only_claim_returns_unknown():
    r = check("   ", [STRONG_SOURCE])
    assert r.status == UNKNOWN


def test_no_sources_returns_unknown():
    r = check("AI market is $45B", [])
    assert r.status == UNKNOWN
    assert r.score == 0.0


def test_unrelated_source_returns_unknown():
    r = check("AI market $45 billion OpenAI Microsoft 2024", [UNRELATED_SOURCE])
    assert r.status == UNKNOWN


def test_url_only_source_returns_unknown():
    """URL-only strings have no text content — claim cannot be verified."""
    r = check("AI market is $45B in 2024", ["https://example.com/report"])
    assert r.status == UNKNOWN


def test_stop_words_only_claim_returns_unknown():
    r = check("is the and or but a an", [STRONG_SOURCE])
    assert r.status == UNKNOWN


def test_unknown_reason_mentions_no_overlap():
    r = check("soybean export Brazil agriculture Amazon", [STRONG_SOURCE])
    assert r.status == UNKNOWN
    assert "overlap" in r.reason.lower() or "score" in r.reason.lower()


# ─── Factual token matching ───────────────────────────────────────────────────

def test_percentage_token_matched_in_source():
    source = _src("The sector grew 18% in 2024 driven by AI adoption.")
    r = check("Growth rate is 18% in 2024", [source])
    assert r.status in (SUPPORTED, WEAK)
    assert r.score > 0.0


def test_year_token_matched_in_source():
    source = _src("In 2025, the market is expected to exceed $100 billion.")
    r = check("Forecast for 2025 market size", [source])
    assert r.score > 0.0


def test_acronym_matched_in_source():
    source = _src("FDA approved several AI diagnostic tools for clinical use in 2024.")
    r = check("FDA approvals for AI diagnostics increasing", [source])
    assert r.status in (SUPPORTED, WEAK)


# ─── Multiple sources ────────────────────────────────────────────────────────

def test_best_score_across_sources_is_used():
    sources = [UNRELATED_SOURCE, UNRELATED_SOURCE, STRONG_SOURCE]
    r_multi  = check("AI market growth 18% CAGR", sources)
    r_single = check("AI market growth 18% CAGR", [STRONG_SOURCE])
    # Best score should be at least as good as single strong source
    assert r_multi.score >= r_single.score - 0.01   # floating point tolerance


def test_all_unrelated_sources_returns_unknown():
    r = check("AI OpenAI Microsoft $45B 2024", [UNRELATED_SOURCE, UNRELATED_SOURCE])
    assert r.status == UNKNOWN


# ─── Source formats ───────────────────────────────────────────────────────────

def test_source_dict_with_title_only_is_used():
    source = {"title": "AI market size $45 billion 2024 growing fast"}
    r = check("AI market $45 billion 2024", [source])
    assert r.score > 0.0


def test_source_dict_with_url_field_is_handled():
    source = {"url": "https://ai-market.com/report-2024-45-billion"}
    r = check("AI market", [source])
    # Should not crash, URL contains some text
    assert isinstance(r, CheckResult)


def test_source_as_plain_string_is_handled():
    source = "The AI market is estimated at 45 billion dollars in 2024."
    r = check("AI market $45 billion 2024", [source])
    assert isinstance(r, CheckResult)
    assert 0.0 <= r.score <= 1.0


# ─── check_claims() ──────────────────────────────────────────────────────────

def test_check_claims_returns_one_result_per_claim():
    claims = ["AI market $45B 2024", "soybean exports Brazil", "FDA approval diagnostics"]
    results = check_claims(claims, [STRONG_SOURCE])
    assert len(results) == len(claims)


def test_check_claims_preserves_order():
    claims = ["AI market $45B 2024 growth CAGR", "soybean export Amazon rainfall"]
    results = check_claims(claims, [STRONG_SOURCE])
    assert results[0].score >= results[1].score   # first is about AI, should score higher


def test_check_claims_empty_list_returns_empty():
    results = check_claims([], [STRONG_SOURCE])
    assert results == []


def test_check_claims_does_not_mutate_inputs():
    claims   = ["AI market growth", "Microsoft OpenAI"]
    sources  = [copy.deepcopy(STRONG_SOURCE)]
    c_snap   = claims[:]
    s_snap   = copy.deepcopy(sources)
    check_claims(claims, sources)
    assert claims   == c_snap
    assert sources  == s_snap


# ─── extract_claims() ────────────────────────────────────────────────────────

def test_extract_claims_returns_list_of_strings():
    output = {
        "market_overview": "The AI market is $45B and growing at 18% CAGR.",
        "key_players": ["OpenAI", "Microsoft"],
        "sources": ["https://example.com"],
    }
    claims = extract_claims(output)
    assert isinstance(claims, list)
    assert all(isinstance(c, str) for c in claims)


def test_extract_claims_skips_sources_key():
    output = {"sources": ["https://example.com/1", "https://example.com/2"]}
    claims = extract_claims(output)
    assert "https://example.com/1" not in claims


def test_extract_claims_skips_short_strings():
    output = {"summary": "ok", "overview": "The AI market size is very large globally."}
    claims = extract_claims(output)
    assert "ok" not in claims
    assert any("AI market" in c for c in claims)


def test_extract_claims_respects_max_claims():
    output = {f"field_{i}": f"This is a verifiable claim number {i} about the market." for i in range(20)}
    claims = extract_claims(output, max_claims=5)
    assert len(claims) <= 5


def test_extract_claims_deduplicates():
    repeated = "The AI market is very large and growing."
    output = {"summary": repeated, "overview": repeated}
    claims = extract_claims(output)
    assert claims.count(repeated) == 1


def test_extract_claims_handles_nested_list_of_dicts():
    output = {
        "competitors": [
            {"name": "Acme Corp", "description": "Acme provides AI solutions for enterprise clients."},
            {"name": "Beta Inc",  "description": "Beta offers ML-based automation for SMBs."},
        ]
    }
    claims = extract_claims(output)
    assert any("Acme" in c or "enterprise" in c for c in claims)


def test_extract_claims_non_dict_input_returns_empty():
    assert extract_claims("not a dict") == []  # type: ignore[arg-type]
    assert extract_claims(None) == []           # type: ignore[arg-type]
    assert extract_claims([]) == []             # type: ignore[arg-type]


def test_extract_claims_skips_parse_error_key():
    output = {"parse_error": True, "raw_response": "garbage", "summary": "Valid claim about the market."}
    claims = extract_claims(output)
    assert True not in claims
    assert "garbage" not in claims


def test_extract_claims_empty_dict_returns_empty():
    assert extract_claims({}) == []


# ─── End-to-end: extract then check ─────────────────────────────────────────

def test_extract_and_check_pipeline():
    agent_output = {
        "market_overview": "The global AI market reached $45 billion in 2024 with 18% CAGR growth.",
        "key_players": ["OpenAI", "Microsoft", "Google"],
        "growth_rate": "18% CAGR through 2029",
        "sources": ["https://example.com/report"],
    }
    sources = [STRONG_SOURCE]
    claims  = extract_claims(agent_output)
    results = check_claims(claims, sources)

    assert len(results) == len(claims)
    # At least one claim should be Supported given STRONG_SOURCE content
    statuses = [r.status for r in results]
    assert SUPPORTED in statuses or WEAK in statuses
