from __future__ import annotations

from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.utils import parse_json_response

_SYSTEM = (
    "You are a strategic analyst specializing in SWOT analysis. Given comprehensive market "
    "research data, produce a rigorous SWOT analysis for the startup idea. "
    "Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    "You are a strategic healthcare analyst specializing in SWOT analysis. Given market data, "
    "produce a SWOT analysis that includes healthcare-specific factors such as regulatory "
    "compliance, reimbursement dynamics, clinical evidence requirements, and interoperability. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(
    idea: str,
    industry: str,
    healthcare_mode: bool = False,
    research_data: Dict | None = None,
    competitor_data: Dict | None = None,
    trend_data: Dict | None = None,
    gap_data: Dict | None = None,
) -> Dict[str, Any]:
    """
    SWOT Agent: synthesizes research, competitor, trend, and gap data into a comprehensive
    Strengths, Weaknesses, Opportunities, and Threats analysis.
    """
    research_summary = (research_data or {}).get("summary", "")
    competitors = [((c.get("name") or "") + ": " + (c.get("description") or ""))
                   for c in ((competitor_data or {}).get("competitors") or [])[:4]]
    trends = [(t.get("name", "")) for t in ((trend_data or {}).get("trends") or [])[:4]]
    opportunities = ((gap_data or {}).get("unexplored_opportunities") or [])[:3]
    blind_spots = ((gap_data or {}).get("competitor_blind_spots") or [])[:2]

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
Healthcare Mode: {healthcare_mode}

Market Research Summary: {research_summary}

Key Competitors: {competitors}
Market Trends: {trends}
Identified Opportunities: {opportunities}
Competitor Blind Spots: {blind_spots}

Return a JSON object with exactly this structure:
{{
  "strengths": [
    "Strength 1 specific to this idea",
    "Strength 2",
    "Strength 3",
    "Strength 4"
  ],
  "weaknesses": [
    "Weakness 1 specific to this idea",
    "Weakness 2",
    "Weakness 3"
  ],
  "opportunities": [
    "Market opportunity 1",
    "Market opportunity 2",
    "Market opportunity 3",
    "Market opportunity 4"
  ],
  "threats": [
    "Market or competitive threat 1",
    "Threat 2",
    "Threat 3"
  ]
}}
Be specific and data-driven. Each item should be a full sentence."""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=3000,
    )
    return parse_json_response(raw)
