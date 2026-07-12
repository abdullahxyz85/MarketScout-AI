from __future__ import annotations

import asyncio
from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.tavily_client import search
from services.utils import ANTI_HALLUCINATION_SUFFIX, PROMPT_INJECTION_GUARD, extract_source_urls, format_sources_for_prompt, idea_to_query, parse_json_response, truncate_sources

_SYSTEM = (
    PROMPT_INJECTION_GUARD +
    "You are a venture capital and startup funding analyst. Analyze ONLY the provided "
    "funding data and return structured investment activity data. "
    "Do not invent funding rounds, amounts, or investor names not found in the sources. "
    "Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    PROMPT_INJECTION_GUARD +
    "You are a healthcare venture capital analyst. Analyze ONLY the provided funding data "
    "for digital health, medtech, and biotech. Do not fabricate funding rounds or amounts. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(idea: str, industry: str, healthcare_mode: bool = False) -> Dict[str, Any]:
    """
    Funding Agent: researches recent funding rounds, investor activity, and capital
    flow trends in the target market to assess funding attractiveness.
    """
    kw = idea_to_query(idea)
    queries = [
        f"{kw} {industry} startup funding round 2024 2025 venture capital",
        f"{industry} VC investment funding deals Series A B 2024",
    ]
    if healthcare_mode:
        queries.append(f"{kw} digital health medtech funding investment 2024")
    else:
        queries.append(f"{kw} startup raised funding investors crunchbase 2024")

    raw_results = await asyncio.gather(
        *[search(q, max_results=5) for q in queries[:3]],
        return_exceptions=True,
    )
    search_results = []
    for r in raw_results:
        if isinstance(r, list):
            search_results.extend(r)

    sources_text = format_sources_for_prompt(truncate_sources(search_results[:10]))

    suffix = ANTI_HALLUCINATION_SUFFIX

    no_source_note = ""
    if not search_results:
        no_source_note = (
            "\nNOTE: No web sources were retrieved. Use your domain knowledge to: "
            "(1) identify 2-3 REAL VC firms known to invest in this space as top_investors, "
            "(2) provide a general funding_trend assessment, "
            "(3) estimate a funding_activity_score based on general sector knowledge. "
            "Set recent_funding_rounds to [] and total_market_funding_estimate/average_valuation_range "
            "to null (no verified data). Mark them in unsupported_claims.\n"
        )

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
Healthcare Mode: {healthcare_mode}

Funding Research Data:
{sources_text}
{no_source_note}

Return a JSON object with exactly this structure:
{{
  "recent_funding_rounds": [
    {{
      "company": "Company name",
      "amount": "$XM",
      "stage": "Seed|Series A|Series B|Series C|IPO",
      "date": "YYYY-MM or YYYY",
      "investors": ["VC Firm 1", "VC Firm 2"]
    }}
  ],
  "funding_activity_score": 70,
  "total_market_funding_estimate": "e.g. $2.3B in 2024",
  "top_investors": ["firm1", "firm2", "firm3"],
  "average_valuation_range": "e.g. $20M-$80M at Seed/Series A",
  "funding_trend": "increasing|stable|decreasing",
  "investor_thesis": "what investors are looking for in this space",
  "evidence_quality": "high|medium|low|insufficient_evidence",
  "unsupported_claims": ["list of field names not found in sources, or empty array"]
}}
funding_activity_score is 0-100 (100 = very active funding environment).
{suffix}"""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=4000,
        temperature=0,  # deterministic — funding_activity_score must be stable
    )
    result = parse_json_response(raw)
    result["sources"] = extract_source_urls(search_results)
    return result


