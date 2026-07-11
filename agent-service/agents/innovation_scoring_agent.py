from __future__ import annotations

from typing import Any, Dict, List

from services.fireworks_client import FireworksModel, call_llm
from services.utils import parse_json_response

# ── Evidence quality penalties ─────────────────────────────────────────────
# Each agent's evidence_quality and _hallucination_flags reduce its sub-score.
# "insufficient_evidence" → 40% penalty; "low" → 20%; ≥1 hallucination flag → 10% each (max 30%).
_EQ_PENALTY = {
    "high":                   0.00,
    "medium":                 0.05,
    "low":                    0.20,
    "insufficient_evidence":  0.40,
}


def _evidence_multiplier(agent_output: Dict[str, Any]) -> float:
    """Return a 0.6–1.0 multiplier based on evidence_quality + hallucination flags."""
    eq = (agent_output.get("evidence_quality") or "medium").lower()
    base_penalty = _EQ_PENALTY.get(eq, 0.05)

    flags: List[dict] = agent_output.get("_hallucination_flags") or []
    hal_penalty = min(0.30, len(flags) * 0.10)

    return max(0.60, 1.0 - base_penalty - hal_penalty)


async def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Innovation Scoring Agent: computes a composite innovation score from all agent outputs
    using a weighted formula, adjusts each sub-score by evidence quality, then uses the
    LLM to generate a contextual explanation.

    Score components (weighted):
    - Novelty score (from research_gap_agent):           25%
    - Market opportunity (inverse of saturation):         20%
    - Funding activity (from funding_agent):              15%
    - Research maturity (from scientific_agent):          15%
    - IP white space (inverse of patent density):         10%
    - Low competition bonus (inverse of saturation):      15%

    Each sub-score is multiplied by the evidence quality multiplier of its source agent
    before aggregation.  A fully hallucinated agent output contributes at most 60% of its
    nominal score.
    """
    research_gaps = state.get("research_gaps") or {}
    competitors   = state.get("competitors")   or {}
    funding       = state.get("funding")       or {}
    scientific    = state.get("scientific")    or {}
    patents       = state.get("patents")       or {}

    # Raw sub-scores
    novelty          = _safe_int(research_gaps.get("novelty_score"), 50)
    saturation       = _safe_int(competitors.get("market_saturation_score"), 50)
    funding_activity = _safe_int(funding.get("funding_activity_score"), 50)
    research_maturity= _safe_int(scientific.get("research_maturity_score"), 50)
    patent_density   = _safe_int(patents.get("patent_density_score"), 50)

    # Evidence-quality multipliers per source agent
    m_gaps      = _evidence_multiplier(research_gaps)
    m_comp      = _evidence_multiplier(competitors)
    m_funding   = _evidence_multiplier(funding)
    m_scientific= _evidence_multiplier(scientific)
    m_patents   = _evidence_multiplier(patents)

    # Weighted composite with quality-adjusted sub-scores
    composite = (
        novelty           * m_gaps       * 0.25
        + (100 - saturation) * m_comp    * 0.20
        + funding_activity * m_funding   * 0.15
        + research_maturity* m_scientific* 0.15
        + (100 - patent_density) * m_patents * 0.10
        + (100 - saturation) * m_comp    * 0.15
    )
    score = round(min(100, max(0, composite)))
    grade = "A" if score >= 80 else "B" if score >= 65 else "C" if score >= 50 else "D"

    # Summarise evidence quality for transparency
    overall_eq = _overall_evidence_quality([research_gaps, competitors, funding, scientific, patents])

    explanation_prompt = f"""The startup idea "{state.get('idea', '')}" in the {state.get('industry', '')} space
has received the following innovation scores (evidence-quality adjusted):
- Novelty (×{m_gaps:.2f}): {round(novelty * m_gaps)}/100
- Market Opportunity (×{m_comp:.2f}): {round((100 - saturation) * m_comp)}/100
- Funding Activity (×{m_funding:.2f}): {round(funding_activity * m_funding)}/100
- Research Maturity (×{m_scientific:.2f}): {round(research_maturity * m_scientific)}/100
- IP White Space (×{m_patents:.2f}): {round((100 - patent_density) * m_patents)}/100
- Overall Innovation Score: {score}/100 (Grade {grade})
- Evidence Quality: {overall_eq}

Write a concise 2-3 sentence explanation of what this score means, including any caveats
about data quality. Be specific and actionable."""

    explanation = await call_llm(
        prompt=explanation_prompt,
        system_prompt="You are a startup analyst. Be concise and data-driven.",
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=300,
    )

    return {
        "scores": {
            "novelty":          round(novelty * m_gaps),
            "market_saturation":round((100 - saturation) * m_comp),
            "funding_activity": round(funding_activity * m_funding),
            "research_maturity":round(research_maturity * m_scientific),
            "patent_density":   round((100 - patent_density) * m_patents),
            "competition_level":round((100 - saturation) * m_comp),
        },
        "innovation_score": score,
        "grade": grade,
        "score_explanation": (explanation or "").strip(),
        "evidence_quality": overall_eq,
        "quality_multipliers": {
            "research_gaps": round(m_gaps, 2),
            "competitors":   round(m_comp, 2),
            "funding":       round(m_funding, 2),
            "scientific":    round(m_scientific, 2),
            "patents":       round(m_patents, 2),
        },
    }


def _overall_evidence_quality(agents: List[Dict[str, Any]]) -> str:
    """Return an aggregate evidence quality label from a list of agent outputs."""
    order = ["high", "medium", "low", "insufficient_evidence"]
    worst = 0
    for a in agents:
        eq = (a.get("evidence_quality") or "medium").lower()
        idx = order.index(eq) if eq in order else 1
        worst = max(worst, idx)
        if a.get("_hallucination_flags"):
            worst = max(worst, 2)  # at least "low" if any flags
    return order[worst]


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
