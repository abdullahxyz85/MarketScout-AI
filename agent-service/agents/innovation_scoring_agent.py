from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, Tuple

from services.fireworks_client import FireworksModel, call_llm
from services.utils import parse_json_response

logger = logging.getLogger("agent-service.innovation_scoring")

# ── Evidence quality penalties ────────────────────────────────────────────────
_EQ_PENALTY = {
    "high":                   0.00,
    "medium":                 0.05,
    "low":                    0.20,
    "insufficient_evidence":  0.40,
}

# ── Dimension registry ────────────────────────────────────────────────────────
# Each entry: (dimension_name, state_key, score_field, weight, invert)
# invert=True → effective_score = 100 - raw_score  (lower saturation/density = better)
_DIMENSIONS: List[Tuple[str, str, str, float, bool]] = [
    ("novelty",           "research_gaps", "novelty_score",           0.25, False),
    ("market_opp",        "competitors",   "market_saturation_score", 0.20, True),
    ("funding",           "funding",       "funding_activity_score",  0.15, False),
    ("research_maturity", "scientific",    "research_maturity_score", 0.15, False),
    ("ip_space",          "patents",       "patent_density_score",    0.10, True),
    ("competition_bonus", "competitors",   "market_saturation_score", 0.15, True),
]

# Total weight used to cross-check the dimension registry
_TOTAL_WEIGHT = sum(d[3] for d in _DIMENSIONS)  # must equal 1.0


def _evidence_multiplier(agent_output: Dict[str, Any]) -> Tuple[float, str]:
    """Return (multiplier 0.60–1.0, evidence_quality_label)."""
    eq = (agent_output.get("evidence_quality") or "medium").lower()
    base_penalty = _EQ_PENALTY.get(eq, 0.05)
    flags: List[dict] = agent_output.get("_hallucination_flags") or []
    hal_penalty = min(0.30, len(flags) * 0.10)
    return max(0.60, 1.0 - base_penalty - hal_penalty), eq


def _get_score(agent_output: Dict[str, Any], field: str) -> Tuple[Optional[float], str]:
    """
    Read a numeric score from an agent output dict.
    Returns (value, status) where status is one of:
      "available"    — score present and in [0, 100]
      "missing"      — field not present in output
      "out_of_range" — field present but outside [0, 100]
      "parse_error"  — field present but not numeric
      "agent_failed" — agent output is empty / parse_error dict
    Never silently returns a neutral default.
    """
    if not agent_output or agent_output.get("parse_error"):
        return None, "agent_failed"
    val = agent_output.get(field)
    if val is None:
        return None, "missing"
    try:
        score = float(val)
    except (TypeError, ValueError):
        return None, "parse_error"
    if not (0 <= score <= 100):
        return None, "out_of_range"
    return score, "available"


async def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Innovation Scoring Agent — computes a composite innovation score with full provenance.

    Score components (weighted, total = 1.0):
      novelty           25%  — research_gap_agent.novelty_score
      market_opp        20%  — inverse of competitor_agent.market_saturation_score
      funding           15%  — funding_agent.funding_activity_score
      research_maturity 15%  — scientific_agent.research_maturity_score
      ip_space          10%  — inverse of patent_agent.patent_density_score
      competition_bonus 15%  — inverse of competitor_agent.market_saturation_score

    Each raw score is multiplied by an evidence-quality multiplier (0.60–1.00).

    Renormalization policy (Part 3 of audit spec):
      final_score = Σ(weight_i × adjusted_i) / available_weight
    where available_weight = Σ(weight_i) for dimensions with status="available".

    If available_weight < 0.70 → score is marked provisional.
    If available_weight = 0   → score is None (insufficient evidence).

    NEVER uses a neutral fallback of 50.  Missing scores are explicitly NULL.
    """
    # ── Gather agent outputs ──────────────────────────────────────────────────
    agent_outputs: Dict[str, Dict[str, Any]] = {
        "research_gaps": state.get("research_gaps") or {},
        "competitors":   state.get("competitors")   or {},
        "funding":       state.get("funding")       or {},
        "scientific":    state.get("scientific")    or {},
        "patents":       state.get("patents")       or {},
    }

    # ── Build per-dimension breakdown ─────────────────────────────────────────
    breakdown: List[Dict[str, Any]] = []
    total_weighted_sum = 0.0
    available_weight   = 0.0

    for dim_name, state_key, score_field, weight, invert in _DIMENSIONS:
        output = agent_outputs[state_key]
        raw_score, status = _get_score(output, score_field)
        mult, eq_label   = _evidence_multiplier(output)

        # Collect per-dimension warnings
        dim_warnings: List[str] = []
        if status == "missing":
            dim_warnings.append(f"{score_field} not found in {state_key} output")
        elif status == "out_of_range":
            dim_warnings.append(f"{score_field} outside [0,100] in {state_key}")
        elif status == "parse_error":
            dim_warnings.append(f"{score_field} in {state_key} is not numeric")
        elif status == "agent_failed":
            dim_warnings.append(f"{state_key} agent output is empty or failed to parse")

        flags = output.get("_hallucination_flags") or []
        if flags:
            dim_warnings.append(
                f"{len(flags)} unsupported claim(s) detected by hallucination checker"
            )

        val_warnings = output.get("_validation_warnings") or []
        if val_warnings:
            dim_warnings.extend(val_warnings[:2])

        # Compute effective score only when available
        if status == "available" and raw_score is not None:
            effective = (100.0 - raw_score) if invert else raw_score
            adjusted  = effective * mult
            contrib   = adjusted * weight
            total_weighted_sum += contrib
            available_weight   += weight
        else:
            effective = None
            adjusted  = None
            contrib   = None

        sources = output.get("sources") or []

        breakdown.append({
            "dimension":            dim_name,
            "source_agent":         state_key,
            "source_field":         score_field,
            "inverted":             invert,
            "raw_value":            raw_score,
            "evidence_multiplier":  round(mult, 3),
            "adjusted_value":       round(adjusted, 2) if adjusted is not None else None,
            "weight":               weight,
            "weighted_contribution": round(contrib, 3) if contrib is not None else None,
            "evidence_quality":     eq_label,
            "source_count":         len(sources),
            "unsupported_claims":   len(flags),
            "status":               status,
            "warnings":             dim_warnings,
        })

    # ── Compute final score ───────────────────────────────────────────────────
    if available_weight == 0.0:
        final_score   = None
        score_coverage = 0.0
        is_provisional = True
        grade          = None
    else:
        # Renormalize by available weight so missing dimensions don't drag the score to 0
        renormalized  = total_weighted_sum / available_weight
        final_score   = round(min(100.0, max(0.0, renormalized)))
        score_coverage = round(available_weight, 3)
        is_provisional = available_weight < 0.70
        grade = (
            "A" if final_score >= 80 else
            "B" if final_score >= 65 else
            "C" if final_score >= 50 else "D"
        )

    # ── Consistency detection ─────────────────────────────────────────────────
    consistency_warnings: List[str] = []

    # Check for suspicious identical raw scores (distinct agent+field combos)
    unique_raw: List[float] = [
        b["raw_value"] for b in breakdown
        if b["status"] == "available"
        and b["raw_value"] is not None
        and not (
            # deduplicate: competition_bonus reuses competitors/market_saturation_score
            b["dimension"] == "competition_bonus"
        )
    ]
    if len(unique_raw) >= 3 and len(set(unique_raw)) == 1:
        consistency_warnings.append(
            f"SUSPICIOUS_IDENTICAL_SCORES: All {len(unique_raw)} sub-scores are "
            f"{unique_raw[0]}/100. This typically indicates mock search data or "
            "LLM returning neutral scores due to lack of real context."
        )
        logger.warning(
            "InnovationScoring[%s]: all sub-scores identical (%s)",
            state.get("job_id", "?"), unique_raw[0],
        )

    # Check mock mode
    from config import settings
    mock_active = not bool(settings.TAVILY_API_KEY)
    if mock_active:
        consistency_warnings.append(
            "MOCK_SEARCH_ACTIVE: Scores are derived from synthetic data. "
            "Results are NOT representative of real market conditions."
        )

    # ── LLM explanation ───────────────────────────────────────────────────────
    explanation = ""
    if final_score is not None:
        available_dims = [b for b in breakdown if b["status"] == "available"]
        dim_lines = "\n".join(
            f"  - {b['dimension']}: raw={b['raw_value']}, "
            f"×{b['evidence_multiplier']} → adjusted={b['adjusted_value']}/100 (weight={b['weight']})"
            for b in available_dims
        )
        provisional_note = (
            f"PROVISIONAL — only {score_coverage:.0%} of score dimensions "
            "have real evidence.\n" if is_provisional else ""
        )
        explanation_prompt = (
            f"Startup idea: \"{state.get('idea', '')}\" in the "
            f"{state.get('industry', '')} space.\n\n"
            f"Innovation score breakdown:\n{dim_lines}\n\n"
            f"Final score: {final_score}/100 (Grade {grade})\n"
            f"Score coverage: {score_coverage:.0%}\n"
            f"{provisional_note}"
            "Write a concise 2-3 sentence explanation of what this score means, "
            "including caveats about data quality. Be specific and actionable."
        )
        raw_explanation = await call_llm(
            prompt=explanation_prompt,
            system_prompt="You are a startup analyst. Be concise and data-driven.",
            model=FireworksModel.DEEPSEEK_V4_FLASH,
            max_tokens=300,
        )
        explanation = (raw_explanation or "").strip()

    # ── Overall evidence quality ──────────────────────────────────────────────
    overall_eq = _overall_evidence_quality(list(agent_outputs.values()))

    # ── Return ────────────────────────────────────────────────────────────────
    return {
        # Primary outputs
        "innovation_score":    final_score,
        "grade":               grade,
        "score_coverage":      score_coverage,
        "is_provisional":      is_provisional,
        "score_breakdown":     breakdown,
        "score_explanation":   explanation,
        "evidence_quality":    overall_eq,
        "consistency_warnings": consistency_warnings,
        # Legacy flat scores for backward-compatible consumers (frontend, PDF)
        # Use None (not 0) when a dimension is missing so callers can detect it.
        "scores": {
            b["dimension"]: b["adjusted_value"]
            for b in breakdown
        },
        "quality_multipliers": {
            state_key: round(_evidence_multiplier(output)[0], 2)
            for state_key, output in agent_outputs.items()
        },
    }


# ── Helpers ───────────────────────────────────────────────────────────────────

def _overall_evidence_quality(agents: List[Dict[str, Any]]) -> str:
    """Return the worst evidence quality label across a list of agent outputs."""
    order = ["high", "medium", "low", "insufficient_evidence"]
    worst = 0
    for a in agents:
        eq  = (a.get("evidence_quality") or "medium").lower()
        idx = order.index(eq) if eq in order else 1
        worst = max(worst, idx)
        if a.get("_hallucination_flags"):
            worst = max(worst, 2)   # at least "low" if any hallucination flags
    return order[worst]
