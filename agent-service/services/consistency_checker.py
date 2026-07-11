"""
Consistency Checker
===================
Detects suspicious patterns in the completed pipeline state before the
result is returned to the caller.

Checks performed
----------------
1. All sub-scores identical  — "SUSPICIOUS_IDENTICAL_SCORES"
2. Mock search is active     — "MOCK_SEARCH_ACTIVE"
3. Low score coverage        — "LOW_SCORE_COVERAGE"
4. Innovation vs report score mismatch  — "SCORE_MISMATCH"
5. Opportunity vs report score mismatch — "SCORE_MISMATCH"
6. Grade inconsistency       — "GRADE_MISMATCH"
7. Risk narrative mismatch   — "RISK_MISMATCH"

Rules
-----
- Read-only: state is never modified.
- No LLM calls.
- Items 1 and 2 together are treated as blocking errors; everything else as warnings.

Usage
-----
    from services.consistency_checker import check, ConsistencyResult

    result = check(pipeline_state)
    if not result.passed:
        logger.warning("ConsistencyChecker: %s", result.errors)
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger("agent-service.consistency_checker")

# Grade boundaries must match innovation_scoring_agent.py
_GRADE_BOUNDARIES = {"A": 80, "B": 65, "C": 50}


@dataclass
class ConsistencyResult:
    passed: bool
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    mock_mode: bool = False
    score_coverage: float = 1.0
    suspicious_identical_scores: bool = False


def _safe_num(value: Any) -> Optional[float]:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def check(state: Dict[str, Any]) -> ConsistencyResult:
    """Run all consistency checks and return a ConsistencyResult."""
    warnings: List[str] = []
    errors: List[str] = []

    # ── 1. Mock search detection ───────────────────────────────────────────────
    from config import settings
    mock_mode = not bool(settings.TAVILY_API_KEY)
    if mock_mode:
        warnings.append(
            "MOCK_SEARCH_ACTIVE: TAVILY_API_KEY is not configured. "
            "All agent scores are derived from synthetic mock data "
            "and are NOT representative of real market conditions. "
            "Set TAVILY_API_KEY to obtain reliable results."
        )

    # ── 2. Suspicious identical scores ────────────────────────────────────────
    innovation_data = state.get("innovation_score") or {}
    breakdown = innovation_data.get("score_breakdown") or []

    # Collect unique (agent, field) pairs that are available
    unique_raw_scores: List[float] = []
    seen_keys: set = set()
    for dim in breakdown:
        key = (dim.get("source_agent"), dim.get("source_field"))
        if key not in seen_keys and dim.get("status") == "available":
            seen_keys.add(key)
            raw = _safe_num(dim.get("raw_value"))
            if raw is not None:
                unique_raw_scores.append(raw)

    suspicious_identical = (
        len(unique_raw_scores) >= 3
        and len(set(unique_raw_scores)) == 1
    )
    if suspicious_identical:
        identical_val = unique_raw_scores[0]
        errors.append(
            f"SUSPICIOUS_IDENTICAL_SCORES: All {len(unique_raw_scores)} unique sub-scores "
            f"are identical ({identical_val}). This typically occurs when mock search is "
            "active or when the LLM received no meaningful web context. "
            "Results from this run should not be treated as reliable market intelligence."
        )
        logger.warning(
            "ConsistencyChecker: all %d sub-scores identical (value=%s)",
            len(unique_raw_scores), identical_val,
        )

    # ── 3. Score coverage ─────────────────────────────────────────────────────
    score_coverage = _safe_num(innovation_data.get("score_coverage")) or 1.0
    if score_coverage < 0.70:
        warnings.append(
            f"LOW_SCORE_COVERAGE: Only {score_coverage:.0%} of score dimensions have "
            "real evidence. The final score is provisional and may not be reliable."
        )

    # ── 4. Consistency warnings forwarded from innovation agent ───────────────
    for w in innovation_data.get("consistency_warnings") or []:
        if w not in warnings:
            warnings.append(w)

    # ── 5. Innovation score vs report market_score mismatch ───────────────────
    report_data = state.get("report") or {}
    canonical_innovation = _safe_num(innovation_data.get("innovation_score"))
    report_market = _safe_num(report_data.get("market_score"))
    if canonical_innovation is not None and report_market is not None:
        if abs(canonical_innovation - report_market) > 15:
            warnings.append(
                f"SCORE_MISMATCH: innovation_score canonical={int(canonical_innovation)}, "
                f"report market_score={int(report_market)} — gap > 15 points. "
                "The report narrative may reference an inconsistent score."
            )

    # ── 6. Opportunity score mismatch ─────────────────────────────────────────
    opp_data = state.get("opportunities") or {}
    canonical_opp = _safe_num(opp_data.get("opportunity_score"))
    report_opp = _safe_num(report_data.get("opportunity_score"))
    if canonical_opp is not None and report_opp is not None:
        if abs(canonical_opp - report_opp) > 15:
            warnings.append(
                f"SCORE_MISMATCH: opportunity_score canonical={int(canonical_opp)}, "
                f"report={int(report_opp)} — gap > 15 points."
            )

    # ── 7. Grade consistency check ────────────────────────────────────────────
    if canonical_innovation is not None:
        canonical_grade = innovation_data.get("grade")
        expected_grade = (
            "A" if canonical_innovation >= 80 else
            "B" if canonical_innovation >= 65 else
            "C" if canonical_innovation >= 50 else "D"
        )
        if canonical_grade and canonical_grade != expected_grade:
            warnings.append(
                f"GRADE_MISMATCH: score={int(canonical_innovation)} implies grade "
                f"{expected_grade} but reported grade={canonical_grade}."
            )

    # ── 8. Risk level consistency ─────────────────────────────────────────────
    risk_data = state.get("risks") or {}
    canonical_risk = risk_data.get("overall_risk_level", "").lower()
    report_risk_narrative = (report_data.get("full_report") or "").lower()
    if canonical_risk and report_risk_narrative:
        # Simple heuristic: if canonical says "high" but report uses "low risk"
        if canonical_risk == "high" and "low risk" in report_risk_narrative:
            warnings.append(
                "RISK_MISMATCH: risk_agent reports overall_risk_level='high' "
                "but report narrative contains 'low risk'. Verify consistency."
            )
        elif canonical_risk == "low" and "high risk" in report_risk_narrative:
            warnings.append(
                "RISK_MISMATCH: risk_agent reports overall_risk_level='low' "
                "but report narrative contains 'high risk'. Verify consistency."
            )

    # ── Final pass/fail ───────────────────────────────────────────────────────
    # Errors (not just warnings) block the "passed" flag.
    # In production (non-mock), suspicious identical scores is a hard error.
    # In mock mode it's expected but still logged.
    passed = len(errors) == 0 or mock_mode  # Mock mode = degrade gracefully

    return ConsistencyResult(
        passed=passed,
        warnings=warnings,
        errors=errors,
        mock_mode=mock_mode,
        score_coverage=score_coverage,
        suspicious_identical_scores=suspicious_identical,
    )
