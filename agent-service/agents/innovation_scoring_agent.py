from __future__ import annotations

from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.utils import parse_json_response


async def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Innovation Scoring Agent: computes a composite innovation score from all agent outputs
    using a weighted formula, then uses the LLM to generate a contextual explanation.

    Score components (weighted):
    - Novelty score (from research_gap_agent):           25%
    - Market opportunity (inverse of saturation):         20%
    - Funding activity (from funding_agent):              15%
    - Research maturity (from scientific_agent):          15%
    - IP white space (inverse of patent density):         10%
    - Low competition bonus (inverse of saturation):      15%
    """
    research_gaps = state.get("research_gaps") or {}
    competitors = state.get("competitors") or {}
    funding = state.get("funding") or {}
    scientific = state.get("scientific") or {}
    patents = state.get("patents") or {}

    novelty = _safe_int(research_gaps.get("novelty_score"), 50)
    saturation = _safe_int(competitors.get("market_saturation_score"), 50)
    funding_activity = _safe_int(funding.get("funding_activity_score"), 50)
    research_maturity = _safe_int(scientific.get("research_maturity_score"), 50)
    patent_density = _safe_int(patents.get("patent_density_score"), 50)

    composite = (
        novelty * 0.25
        + (100 - saturation) * 0.20
        + funding_activity * 0.15
        + research_maturity * 0.15
        + (100 - patent_density) * 0.10
        + (100 - saturation) * 0.15
    )
    score = round(min(100, max(0, composite)))
    grade = "A" if score >= 80 else "B" if score >= 65 else "C" if score >= 50 else "D"

    explanation_prompt = f"""The startup idea "{state.get('idea', '')}" in the {state.get('industry', '')} space
has received the following innovation scores:
- Novelty: {novelty}/100
- Market Opportunity (vs saturation): {100 - saturation}/100
- Funding Activity: {funding_activity}/100
- Research Maturity: {research_maturity}/100
- IP White Space: {100 - patent_density}/100
- Overall Innovation Score: {score}/100 (Grade {grade})

Write a concise 2-3 sentence explanation of what this score means, highlighting the key
strengths and weaknesses. Be specific and actionable."""

    # GPT_OSS_20B is not available on all accounts — fall back to the reliable flash model
    explanation = await call_llm(
        prompt=explanation_prompt,
        system_prompt="You are a startup analyst. Be concise and data-driven.",
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=300,
    )

    return {
        "scores": {
            "novelty": novelty,
            "market_saturation": 100 - saturation,
            "funding_activity": funding_activity,
            "research_maturity": research_maturity,
            "patent_density": 100 - patent_density,
            "competition_level": 100 - saturation,
        },
        "innovation_score": score,
        "grade": grade,
        "score_explanation": (explanation or "").strip(),
    }


def _safe_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default
