from __future__ import annotations

import asyncio
from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.tavily_client import search
from services.utils import extract_source_urls, format_sources_for_prompt, parse_json_response, truncate_sources

_SYSTEM = (
    "You are a senior market research analyst. Analyze the provided web data and return "
    "a structured JSON report. Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    "You are a healthcare market research analyst specializing in medical technology, "
    "digital health, pharma, and clinical innovations. Analyze the provided web data "
    "including regulatory context, payer dynamics, and clinical adoption factors. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(idea: str, industry: str, healthcare_mode: bool = False) -> Dict[str, Any]:
    """
    Research Agent: performs parallel web searches on the startup idea and synthesizes
    findings into a structured market overview using the Fireworks AI LLM.
    """
    queries = [
        f"{idea} {industry} market size 2024 2025",
        f"{idea} startup competitors market overview",
        f"{industry} market growth investment trends 2025",
    ]
    if healthcare_mode:
        queries.append(f"{idea} FDA regulatory approval healthcare clinical market")

    raw_results = await asyncio.gather(
        *[search(q, max_results=4) for q in queries[:4]],
        return_exceptions=True,
    )
    search_results = []
    for r in raw_results:
        if isinstance(r, list):
            search_results.extend(r)

    sources_text = format_sources_for_prompt(truncate_sources(search_results[:10]))
    source_urls = extract_source_urls(search_results)

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
Healthcare Mode: {healthcare_mode}

Web Research Data:
{sources_text}

Return a JSON object with exactly this structure:
{{
  "market_overview": "2-3 sentence description of the market",
  "key_players": ["company1", "company2", "company3"],
  "market_size_estimate": "e.g. $45B globally by 2027",
  "recent_trends": ["trend1", "trend2", "trend3"],
  "growth_rate": "e.g. 18% CAGR 2024-2029",
  "target_customers": ["segment1", "segment2"],
  "pain_points": ["pain1", "pain2", "pain3"],
  "summary": "comprehensive paragraph summarizing the market landscape"
}}"""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=1500,
    )
    result = parse_json_response(raw)
    result["sources"] = source_urls
    return result
