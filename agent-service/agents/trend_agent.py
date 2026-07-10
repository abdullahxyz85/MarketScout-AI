from __future__ import annotations

import asyncio
from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.tavily_client import search
from services.utils import ANTI_HALLUCINATION_SUFFIX, extract_source_urls, format_sources_for_prompt, parse_json_response, truncate_for_search, truncate_sources

_SYSTEM = (
    "You are a market trend analyst. Identify and analyze ONLY trends, technologies, "
    "and regulatory shifts found in the provided sources. "
    "Do not describe trends not supported by the retrieved data. "
    "Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    "You are a healthcare market trend analyst. Identify ONLY trends found in the provided "
    "sources: clinical adoption, FDA/CMS shifts, reimbursement changes, digital health tech. "
    "Do not fabricate regulatory approvals or clinical data. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(idea: str, industry: str, healthcare_mode: bool = False) -> Dict[str, Any]:
    """
    Trend Agent: identifies market trends, emerging technologies, regulatory changes,
    and disruptive forces affecting the target market space.
    """
    search_idea = truncate_for_search(idea)
    queries = [
        f"{industry} market trends 2024 2025 emerging technology",
        f"{search_idea} {industry} industry disruption innovation trends",
        f"{industry} regulatory technology AI automation trends 2025",
    ]
    if healthcare_mode:
        queries.extend([
            f"digital health trends 2024 2025 FDA AI regulation",
            f"healthcare technology adoption telemedicine AI clinical trends",
        ])

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

Trend Research Data:
{sources_text}

Return a JSON object with exactly this structure:
{{
  "trends": [
    {{
      "name": "Trend name",
      "description": "what this trend is",
      "direction": "growing|stable|declining",
      "impact": "high|medium|low",
      "time_horizon": "e.g. 1-2 years or 3-5 years"
    }}
  ],
  "market_growth_rate": "e.g. 18% CAGR 2024-2029",
  "emerging_technologies": ["tech1", "tech2", "tech3"],
  "regulatory_trends": ["regulatory shift 1", "regulatory shift 2"],
  "market_forecast": "1-2 sentence market forecast",
  "disruptive_forces": ["force1", "force2"],
  "evidence_quality": "high|medium|low|insufficient_evidence",
  "unsupported_claims": ["list of field names not found in sources, or empty array"]
}}
Include 4 to 6 trends.
{ANTI_HALLUCINATION_SUFFIX}"""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=2500,
    )
    result = parse_json_response(raw)
    result["sources"] = extract_source_urls(search_results)
    return result
