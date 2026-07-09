"""
Confidence Engine
=================
Computes a confidence assessment for any agent output **without modifying it**.

For each agent output it produces a ConfidenceResult containing:

    confidence      – float  0.0–1.0   (1.0 = fully confident)
    evidence_strength – "strong" | "moderate" | "weak" | "none"
    reason          – human-readable explanation string

Rules
-----
- Read-only: the original output dict is never touched.
- No LLM calls: pure deterministic logic on the already-returned data.
- Works on every agent registered in the pipeline (15 agents).
- Gracefully handles None, parse_error dicts, or unknown agents.

Usage
-----
    from services.confidence import assess, assess_all

    result = assess("research", agent_output)
    print(result.confidence)        # 0.85
    print(result.evidence_strength) # "strong"
    print(result.reason)            # "8 sources, all required fields present."

    all_results = assess_all(pipeline_state)
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Literal, Optional


# ─── Result type ──────────────────────────────────────────────────────────────

EvidenceStrength = Literal["strong", "moderate", "weak", "none"]


@dataclass(frozen=True)
class ConfidenceResult:
    confidence: float          # 0.0 – 1.0
    evidence_strength: EvidenceStrength
    reason: str


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _clamp(value: float) -> float:
    return max(0.0, min(1.0, value))


def _safe_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _source_count(output: Dict[str, Any]) -> int:
    sources = output.get("sources")
    if isinstance(sources, list):
        return len(sources)
    return 0


def _non_empty_lists(output: Dict[str, Any]) -> int:
    """Count top-level list fields that are non-empty (excluding 'sources')."""
    return sum(
        1 for k, v in output.items()
        if k != "sources" and isinstance(v, list) and len(v) > 0
    )


def _has_parse_error(output: Any) -> bool:
    return not isinstance(output, dict) or bool(output.get("parse_error"))


def _required_fields_present(output: Dict[str, Any], fields: list[str]) -> tuple[int, int]:
    """Return (present_count, total_count) for required field list."""
    present = sum(
        1 for f in fields
        if f in output and output[f] is not None and output[f] != "" and output[f] != []
    )
    return present, len(fields)


def _strength_from_confidence(c: float) -> EvidenceStrength:
    if c >= 0.80:
        return "strong"
    if c >= 0.55:
        return "moderate"
    if c > 0.0:
        return "weak"
    return "none"


# ─── Per-agent scorers ────────────────────────────────────────────────────────
# Each scorer receives the output dict and returns (raw_score: float, reason: str).
# raw_score is already in [0.0, 1.0].

def _score_with_sources(
    output: Dict[str, Any],
    required_fields: list[str],
    score_fields: list[str],
) -> tuple[float, str]:
    """
    Generic scorer for agents that do web research.
    Weights: required-fields 40%, sources 40%, non-empty-lists 20%.
    """
    present, total = _required_fields_present(output, required_fields)
    fields_ratio = present / total if total else 1.0

    sources = _source_count(output)
    # 3+ sources = full score, 0 = zero
    source_score = _clamp(sources / 3.0)

    lists_ok = _non_empty_lists(output)
    list_score = _clamp(lists_ok / max(1, len([f for f in required_fields
                                               if isinstance(output.get(f), list)])))

    # Penalise out-of-range numeric scores
    score_penalty = 0.0
    for field in score_fields:
        val = _safe_float(output.get(field, 50))
        if not (0 <= val <= 100):
            score_penalty += 0.1

    score = (fields_ratio * 0.40 + source_score * 0.40 + list_score * 0.20) - score_penalty
    parts = [
        f"{present}/{total} required fields",
        f"{sources} source(s)",
    ]
    if score_penalty > 0:
        parts.append("score(s) out of range")
    return _clamp(score), ", ".join(parts) + "."


def _score_no_sources(
    output: Dict[str, Any],
    required_fields: list[str],
    score_fields: list[str],
) -> tuple[float, str]:
    """
    Generic scorer for agents that do NOT do web research.
    Weights: required-fields 60%, non-empty-lists 40%.
    """
    present, total = _required_fields_present(output, required_fields)
    fields_ratio = present / total if total else 1.0

    list_fields_count = sum(
        1 for f in required_fields if isinstance(output.get(f), list)
    )
    lists_ok = _non_empty_lists(output)
    list_score = _clamp(lists_ok / max(1, list_fields_count)) if list_fields_count else 1.0

    score_penalty = 0.0
    for field in score_fields:
        val = _safe_float(output.get(field, 50))
        if not (0 <= val <= 100):
            score_penalty += 0.1

    score = (fields_ratio * 0.60 + list_score * 0.40) - score_penalty
    parts = [f"{present}/{total} required fields"]
    if lists_ok:
        parts.append(f"{lists_ok} non-empty list(s)")
    if score_penalty > 0:
        parts.append("score(s) out of range")
    return _clamp(score), ", ".join(parts) + "."


# Specialised scorer for idea_guard (binary verdict matters most)
def _score_idea_guard(output: Dict[str, Any]) -> tuple[float, str]:
    required = [
        "verdict", "verdict_summary", "clarity_score", "vagueness_score",
        "is_startup_idea", "legal_status", "ethical_status",
        "technical_feasibility", "market_potential",
    ]
    present, total = _required_fields_present(output, required)
    fields_ratio = present / total if total else 1.0

    clarity  = _safe_float(output.get("clarity_score",  50))
    vagueness = _safe_float(output.get("vagueness_score", 50))

    score_ok = (0 <= clarity <= 100) and (0 <= vagueness <= 100)
    verdict   = output.get("verdict", "")
    verdict_ok = verdict in ("approved", "needs_clarification", "rejected")

    base = fields_ratio * 0.70
    if score_ok:
        base += 0.15
    if verdict_ok:
        base += 0.15

    parts = [f"{present}/{total} required fields"]
    if not score_ok:
        parts.append("invalid scores")
    if not verdict_ok:
        parts.append(f"unknown verdict '{verdict}'")
    return _clamp(base), ", ".join(parts) + "."


# Specialised scorer for innovation_scoring (depends on downstream data)
def _score_innovation(output: Dict[str, Any]) -> tuple[float, str]:
    score_val = _safe_float(output.get("innovation_score", -1))
    grade     = output.get("grade", "")
    expl      = output.get("score_explanation", "")

    score_ok = 0 <= score_val <= 100
    grade_ok = grade in ("A", "B", "C", "D")
    expl_ok  = isinstance(expl, str) and len(expl) > 10

    base = (0.45 if score_ok else 0.0) + (0.25 if grade_ok else 0.0) + (0.30 if expl_ok else 0.0)
    parts = []
    if score_ok:
        parts.append(f"score={score_val}")
    if grade_ok:
        parts.append(f"grade={grade}")
    if not expl_ok:
        parts.append("no explanation")
    return _clamp(base), (", ".join(parts) or "missing data") + "."


# ─── Schema registry ──────────────────────────────────────────────────────────

_WEB_AGENTS = {
    "research": {
        "required": ["market_overview", "key_players", "market_size_estimate",
                     "recent_trends", "growth_rate", "target_customers", "pain_points", "summary"],
        "scores":   [],
    },
    "competitor": {
        "required": ["competitors", "competitive_landscape",
                     "market_saturation_score", "differentiation_opportunities"],
        "scores":   ["market_saturation_score"],
    },
    "scientific": {
        "required": ["relevant_papers", "research_maturity", "research_maturity_score",
                     "key_findings", "research_gaps", "academic_consensus"],
        "scores":   ["research_maturity_score"],
    },
    "patent": {
        "required": ["existing_patents", "patent_density_score", "white_spaces",
                     "freedom_to_operate_risks", "ip_strategy_recommendation"],
        "scores":   ["patent_density_score"],
    },
    "funding": {
        "required": ["recent_funding_rounds", "funding_activity_score",
                     "total_market_funding_estimate", "top_investors",
                     "average_valuation_range", "funding_trend", "investor_thesis"],
        "scores":   ["funding_activity_score"],
    },
    "trend": {
        "required": ["trends", "market_growth_rate", "emerging_technologies",
                     "regulatory_trends", "market_forecast", "disruptive_forces"],
        "scores":   [],
    },
    "research_gap": {
        "required": ["unexplored_opportunities", "missing_features_in_market",
                     "emerging_niches", "competitor_blind_spots",
                     "technology_white_spaces", "novelty_score", "differentiation_thesis"],
        "scores":   ["novelty_score"],
    },
}

_PURE_AGENTS = {
    "swot": {
        "required": ["strengths", "weaknesses", "opportunities", "threats"],
        "scores":   [],
    },
    "opportunity": {
        "required": ["market_gaps", "target_segments", "opportunity_score", "blue_ocean_potential"],
        "scores":   ["opportunity_score"],
    },
    "risk": {
        "required": ["risks", "overall_risk_level", "risk_score",
                     "critical_risks", "risk_mitigation_roadmap"],
        "scores":   ["risk_score"],
    },
    "validation": {
        "required": ["challenged_assumptions", "validation_experiments",
                     "confidence_level", "key_risks_identified", "recommendation"],
        "scores":   [],
    },
    "strategy": {
        "required": ["strategic_recommendations", "innovation_hypotheses",
                     "go_to_market", "competitive_positioning", "pricing_strategy",
                     "key_partnerships", "success_metrics", "roadmap"],
        "scores":   [],
    },
    "report": {
        "required": ["executive_summary", "market_score", "opportunity_score",
                     "competition_level", "recommendations", "key_metrics", "full_report"],
        "scores":   ["market_score", "opportunity_score"],
    },
}


# ─── Public API ───────────────────────────────────────────────────────────────

def assess(agent_name: str, output: Any) -> ConfidenceResult:
    """
    Assess the confidence of a single agent output.

    Parameters
    ----------
    agent_name : str
        Pipeline key for the agent (e.g. "research", "swot", "idea_guard").
    output : Any
        The dict returned by the agent's run() function.

    Returns
    -------
    ConfidenceResult
        .confidence       – float 0.0–1.0
        .evidence_strength – "strong" | "moderate" | "weak" | "none"
        .reason           – human-readable explanation
    """
    # ── Guard: None or unparseable ──────────────────────────────────────────
    if output is None:
        return ConfidenceResult(
            confidence=0.0,
            evidence_strength="none",
            reason="Output is None — agent did not run or was skipped.",
        )
    if _has_parse_error(output):
        raw = output.get("raw_response", "") if isinstance(output, dict) else output
        preview = str(raw)[:80]
        return ConfidenceResult(
            confidence=0.0,
            evidence_strength="none",
            reason=f"LLM parse error — unparseable output. Preview: {preview!r}",
        )

    # ── Specialised scorers ─────────────────────────────────────────────────
    if agent_name == "idea_guard":
        raw, reason = _score_idea_guard(output)
    elif agent_name == "innovation_scoring":
        raw, reason = _score_innovation(output)
    # ── Web-search agents ───────────────────────────────────────────────────
    elif agent_name in _WEB_AGENTS:
        schema = _WEB_AGENTS[agent_name]
        raw, reason = _score_with_sources(output, schema["required"], schema["scores"])
    # ── Pure-LLM agents ─────────────────────────────────────────────────────
    elif agent_name in _PURE_AGENTS:
        schema = _PURE_AGENTS[agent_name]
        raw, reason = _score_no_sources(output, schema["required"], schema["scores"])
    # ── Unknown agent ───────────────────────────────────────────────────────
    else:
        lists_ok = _non_empty_lists(output)
        raw = _clamp(0.40 + lists_ok * 0.10)
        reason = f"Unknown agent '{agent_name}' — basic heuristic only, {lists_ok} non-empty list(s)."

    strength = _strength_from_confidence(raw)
    return ConfidenceResult(confidence=round(raw, 4), evidence_strength=strength, reason=reason)


def assess_all(agent_outputs: Dict[str, Any]) -> Dict[str, ConfidenceResult]:
    """
    Assess confidence for every agent output in a pipeline state dict.

    None values are assessed (and return confidence=0.0 / strength="none").
    Non-agent keys (job_id, idea, industry, …) are silently ignored when
    their value is not a dict.

    Parameters
    ----------
    agent_outputs : dict
        The full pipeline state dict keyed by agent name.

    Returns
    -------
    dict[str, ConfidenceResult]
    """
    agent_keys = set(_WEB_AGENTS) | set(_PURE_AGENTS) | {"idea_guard", "innovation_scoring"}
    results: Dict[str, ConfidenceResult] = {}
    for key, value in agent_outputs.items():
        # Only process known agent keys or dict/None values
        if key not in agent_keys and not isinstance(value, (dict, type(None))):
            continue
        if key in agent_keys or isinstance(value, (dict, type(None))):
            results[key] = assess(key, value)
    return results
