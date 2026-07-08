from __future__ import annotations

from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.utils import parse_json_response

_SYSTEM = (
    "You are a market opportunity analyst. Identify and assess market gaps, target segments, "
    "and differentiation strategies for the startup idea based on competitive and market data. "
    "Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    "You are a healthcare market opportunity analyst. Identify underserved patient populations, "
    "care delivery gaps, payer-driven opportunities, and value-based care alignment. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(
    idea: str,
    industry: str,
    healthcare_mode: bool = False,
    research_data: Dict | None = None,
    competitor_data: Dict | None = None,
    gap_data: Dict | None = None,
    swot_data: Dict | None = None,
) -> Dict[str, Any]:
    """
    Opportunity Agent: identifies market gaps, addressable customer segments,
    differentiation strategies, and computes an opportunity score.
    """
    pain_points = (research_data or {}).get("pain_points", [])[:4]
    competitor_weaknesses = [(c.get("name", "") + " weaknesses: " + str(c.get("weaknesses", [])))
                             for c in (competitor_data or {}).get("competitors", [])[:3]]
    gaps = (gap_data or {}).get("unexplored_opportunities", [])[:3]
    swot_opps = (swot_data or {}).get("opportunities", [])[:3]
    saturation = (competitor_data or {}).get("market_saturation_score", 50)

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
Healthcare Mode: {healthcare_mode}
Market Saturation Score: {saturation}/100

Customer Pain Points: {pain_points}
Competitor Weaknesses: {competitor_weaknesses}
Identified Market Gaps: {gaps}
SWOT Opportunities: {swot_opps}

Return a JSON object with exactly this structure:
{{
  "market_gaps": [
    "Specific market gap 1",
    "Specific market gap 2",
    "Specific market gap 3"
  ],
  "target_segments": [
    {{
      "segment": "Segment name",
      "size": "estimated addressable size",
      "addressability": "high|medium|low",
      "willingness_to_pay": "high|medium|low",
      "description": "why this segment is attractive"
    }}
  ],
  "differentiation_strategies": [
    "Differentiation strategy 1",
    "Differentiation strategy 2",
    "Differentiation strategy 3"
  ],
  "blue_ocean_potential": "Description of untapped market space unique to this idea",
  "opportunity_score": 78
}}
opportunity_score is 0-100. Include 2-3 target segments."""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=1500,
    )
    return parse_json_response(raw)
