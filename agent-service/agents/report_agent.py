from __future__ import annotations

from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.utils import parse_json_response

_SYSTEM = (
    "You are a market intelligence report writer. Synthesize all research data into a "
    "polished executive report with key scores and strategic recommendations. "
    "Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    "You are a healthcare market intelligence report writer. Synthesize all research data "
    "into an executive report tailored for healthcare innovators, including regulatory pathway, "
    "clinical evidence summary, and payer strategy. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(
    idea: str,
    industry: str,
    healthcare_mode: bool = False,
    research_data: Dict | None = None,
    competitor_data: Dict | None = None,
    swot_data: Dict | None = None,
    opportunity_data: Dict | None = None,
    risk_data: Dict | None = None,
    innovation_score_data: Dict | None = None,
    strategy_data: Dict | None = None,
    trend_data: Dict | None = None,
    validation_data: Dict | None = None,
) -> Dict[str, Any]:
    """
    Report Agent: synthesizes all agent outputs into a final executive market intelligence
    report with scores, recommendations, and key metrics using the most capable model.

    Canonical scores (innovation_score, opportunity_score) are read from the pipeline
    state and injected into the output directly — the LLM is NOT asked to generate or
    re-estimate them, preventing narrative/canonical score mismatches.
    """
    market_overview = (research_data or {}).get("market_overview", "")
    market_size = (research_data or {}).get("market_size_estimate", "")
    growth_rate = (research_data or {}).get("growth_rate", "")

    # ── Canonical scores — read from agent outputs, not LLM-generated ────────
    canonical_innovation = (innovation_score_data or {}).get("innovation_score")
    canonical_grade      = (innovation_score_data or {}).get("grade")
    is_provisional       = (innovation_score_data or {}).get("is_provisional", False)
    score_coverage       = (innovation_score_data or {}).get("score_coverage", 1.0)
    score_explanation    = (innovation_score_data or {}).get("score_explanation", "")
    canonical_opp        = (opportunity_data or {}).get("opportunity_score")
    consistency_warnings = (innovation_score_data or {}).get("consistency_warnings") or []

    overall_risk    = (risk_data or {}).get("overall_risk_level", "medium")
    saturation      = (competitor_data or {}).get("market_saturation_score", 50)
    strategic_recs  = ((strategy_data or {}).get("strategic_recommendations") or [])[:5]
    gtm             = (strategy_data or {}).get("go_to_market", "")
    validation_rec  = (validation_data or {}).get("recommendation", "")
    confidence      = (validation_data or {}).get("confidence_level", "medium")
    trends          = [(t.get("name", "")) for t in ((trend_data or {}).get("trends") or [])[:3]]
    funding_trend   = ((research_data or {}).get("recent_trends") or [])[:3]

    competition_level = (
        "high" if saturation >= 70
        else "medium" if saturation >= 40
        else "low"
    )

    # Build provenance note for the prompt
    score_note = (
        f"Innovation Score: {canonical_innovation}/100 (Grade {canonical_grade}"
        + (", PROVISIONAL" if is_provisional else "")
        + f") — {score_explanation}\n"
        f"Opportunity Score: {canonical_opp}/100 (canonical from opportunity agent)\n"
    ) if canonical_innovation is not None else (
        "Innovation Score: INSUFFICIENT EVIDENCE — do not invent a score\n"
        "Opportunity Score: see opportunity agent output\n"
    )

    consistency_note = ""
    if consistency_warnings:
        consistency_note = (
            "\nDATA QUALITY WARNINGS (must mention in executive summary):\n"
            + "\n".join(f"  - {w}" for w in consistency_warnings[:3])
            + "\n"
        )

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
Healthcare Mode: {healthcare_mode}

Market Overview: {market_overview}
Market Size: {market_size}
Growth Rate: {growth_rate}
{score_note}
Competition Level: {competition_level} (saturation: {saturation}/100)
Overall Risk Level: {overall_risk}
Validation Confidence: {confidence}
Validation Recommendation: {validation_rec}
Key Market Trends: {trends}
Recent Trends: {funding_trend}
Strategic Recommendations: {strategic_recs}
Go-to-Market: {gtm}
{consistency_note}
IMPORTANT INSTRUCTIONS:
- Do NOT invent or change any numeric score. The innovation_score and opportunity_score
  values provided above are canonical and must not be modified.
- Do NOT introduce new market size, CAGR, or funding figures that are not already
  present in the data above. If data is missing, say so explicitly.
- If data quality warnings are listed above, reflect them honestly in the executive summary.
- Write "PROVISIONAL SCORE" in the summary if is_provisional is true.

Write the final executive market intelligence report. Return a JSON object:
{{
  "executive_summary": "Comprehensive 4-5 sentence executive summary covering market opportunity, competitive landscape, innovation potential, and strategic outlook. If data quality issues exist, mention them.",
  "competition_level": "{competition_level}",
  "recommendations": [
    "Top recommendation 1",
    "Top recommendation 2",
    "Top recommendation 3",
    "Top recommendation 4",
    "Top recommendation 5"
  ],
  "key_metrics": {{
    "market_size": "{market_size}",
    "growth_rate": "{growth_rate}",
    "time_to_market": "estimated months to launch MVP",
    "investment_required": "estimated seed/series A range",
    "target_customers": "primary customer description"
  }},
  "full_report": "Write a 400-500 word comprehensive narrative market report in plain text covering: 1) Market Opportunity, 2) Competitive Landscape, 3) Innovation Potential, 4) Risks, 5) Strategic Recommendations. Include a disclaimer if data is based on mock/synthetic search."
}}"""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_PRO,
        max_tokens=4000,
    )
    result = parse_json_response(raw)

    # ── Inject canonical scores directly — never trust LLM to restate them ───
    if canonical_innovation is not None:
        result["market_score"]    = canonical_innovation   # canonical innovation score
        result["innovation_grade"] = canonical_grade
        result["is_provisional"]  = is_provisional
        result["score_coverage"]  = score_coverage
    if canonical_opp is not None:
        result["opportunity_score"] = canonical_opp        # canonical opp score

    result["consistency_warnings"] = consistency_warnings
    return result

    # (removed — folded into the new prompt/return block above)

