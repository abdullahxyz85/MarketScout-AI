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
    """
    market_overview = (research_data or {}).get("market_overview") or ""
    market_size = (research_data or {}).get("market_size_estimate") or ""
    growth_rate = (research_data or {}).get("growth_rate") or ""
    innovation_score = (innovation_score_data or {}).get("innovation_score") or "N/A"
    score_explanation = (innovation_score_data or {}).get("score_explanation") or ""
    opportunity_score = (opportunity_data or {}).get("opportunity_score") or "N/A"
    overall_risk = (risk_data or {}).get("overall_risk_level") or "medium"
    saturation = (competitor_data or {}).get("market_saturation_score") or 50
    strategic_recs = ((strategy_data or {}).get("strategic_recommendations") or [])[:5]
    gtm = (strategy_data or {}).get("go_to_market") or ""
    validation_rec = (validation_data or {}).get("recommendation") or ""
    confidence = (validation_data or {}).get("confidence_level") or "medium"
    trends = [(t.get("name", "")) for t in ((trend_data or {}).get("trends") or [])[:3]]
    funding_trend = ((research_data or {}).get("recent_trends") or [])[:3]

    competition_level = (
        "high" if saturation >= 70
        else "medium" if saturation >= 40
        else "low"
    )

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
Healthcare Mode: {healthcare_mode}

Market Overview: {market_overview}
Market Size: {market_size}
Growth Rate: {growth_rate}
Innovation Score: {innovation_score}/100 — {score_explanation}
Opportunity Score: {opportunity_score}/100
Competition Level: {competition_level} (saturation: {saturation}/100)
Overall Risk Level: {overall_risk}
Validation Confidence: {confidence}
Validation Recommendation: {validation_rec}
Key Market Trends: {trends}
Recent Trends: {funding_trend}
Strategic Recommendations: {strategic_recs}
Go-to-Market: {gtm}

Write the final executive market intelligence report. Return a JSON object:
{{
  "executive_summary": "Comprehensive 4-5 sentence executive summary covering market opportunity, competitive landscape, innovation potential, and strategic outlook",
  "market_score": 85,
  "opportunity_score": 78,
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
  "full_report": "Write a 400-500 word comprehensive narrative market report in plain text covering: 1) Market Opportunity, 2) Competitive Landscape, 3) Innovation Potential, 4) Risks, 5) Strategic Recommendations"
}}"""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_PRO,
        max_tokens=5000,
    )
    return parse_json_response(raw)
