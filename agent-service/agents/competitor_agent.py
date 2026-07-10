from __future__ import annotations

import asyncio
from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.tavily_client import search
from services.utils import ANTI_HALLUCINATION_SUFFIX, extract_source_urls, format_sources_for_prompt, parse_json_response, truncate_sources

_SYSTEM = (
    "You are a competitive intelligence analyst. Given web data, identify and analyze "
    "the key competitors to the startup idea. Base every claim on the retrieved sources. "
    "Respond with valid JSON only, no markdown."
)
_SYSTEM_HC = (
    "You are a competitive intelligence analyst specializing in healthcare. Identify "
    "hospital systems, digital health startups, medical device companies, and pharma "
    "players competing in this space. Base every claim on the retrieved sources. "
    "Respond with valid JSON only, no markdown."
)


async def run(idea: str, industry: str, healthcare_mode: bool = False) -> Dict[str, Any]:
    """
    Competitor Agent: searches for competitors in the market and produces a structured
    competitive landscape analysis with threat levels and market share estimates.
    """
    queries = [
        f"{idea} {industry} top competitors startups companies",
        f"best companies {industry} {idea} comparison market share",
        f"{idea} alternative solutions competitive analysis",
    ]
    if healthcare_mode:
        queries.append(f"{idea} healthcare competitors hospitals pharma digital health companies")

    raw_results = await asyncio.gather(
        *[search(q, max_results=4) for q in queries[:4]],
        return_exceptions=True,
    )
    search_results = []
    for r in raw_results:
        if isinstance(r, list):
            search_results.extend(r)

    sources_text = format_sources_for_prompt(truncate_sources(search_results[:10]))

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
Healthcare Mode: {healthcare_mode}

Web Research Data:
{sources_text}

Return a JSON object with exactly this structure:
{{
  "competitors": [
    {{
      "name": "Company Name",
      "description": "what they do in one sentence",
      "market_share": "estimated % or range",
      "strengths": ["strength1", "strength2"],
      "weaknesses": ["weakness1", "weakness2"],
      "threat_level": "high|medium|low",
      "revenue": "estimated revenue",
      "founded": "year",
      "target_segment": "who they target"
    }}
  ],
  "competitive_landscape": "2-3 sentence overview of the competitive environment",
  "market_saturation_score": 65,
  "differentiation_opportunities": ["opportunity1", "opportunity2"],
  "evidence_quality": "high|medium|low|insufficient_evidence",
  "unsupported_claims": ["list of field names not found in sources, or empty array"]
}}
Include 3 to 6 competitors. market_saturation_score is 0-100 (100 = fully saturated).
{suffix}""".format(suffix=ANTI_HALLUCINATION_SUFFIX)

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=2000,
    )
    result = parse_json_response(raw)
    result["sources"] = extract_source_urls(search_results)
    return result
