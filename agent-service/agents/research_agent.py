from __future__ import annotations

import asyncio
from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.tavily_client import search
from services.utils import ANTI_HALLUCINATION_SUFFIX, PROMPT_INJECTION_GUARD, extract_source_urls, format_sources_for_prompt, idea_to_query, parse_json_response, truncate_sources

_SYSTEM = (
    PROMPT_INJECTION_GUARD +
    "You are a senior market research analyst. Analyze ONLY the provided web data and return "
    "a structured JSON report. Base every claim on the retrieved sources. "
    "Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    PROMPT_INJECTION_GUARD +
    "You are a healthcare market research analyst specializing in medical technology, "
    "digital health, pharma, and clinical innovations. Analyze ONLY the provided web data "
    "including regulatory context, payer dynamics, and clinical adoption factors. "
    "Base every claim strictly on retrieved sources. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(idea: str, industry: str, healthcare_mode: bool = False) -> Dict[str, Any]:
    """
    Research Agent: performs parallel web searches on the startup idea and synthesizes
    findings into a structured market overview using the Fireworks AI LLM.
    """
    kw = idea_to_query(idea)
    queries = [
        f"{kw} {industry} market size 2024 2025",
        f"{kw} startup competitors market overview",
        f"{industry} market growth investment trends 2025",
    ]
    if healthcare_mode:
        queries.append(f"{kw} FDA regulatory approval healthcare clinical market")

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

    no_source_note = ""
    if not search_results:
        no_source_note = (
            "\nNOTE: No web sources were retrieved. Use your domain knowledge to fill in: "
            "key_players (real known companies in this space), recent_trends (known industry trends), "
            "target_customers, pain_points, and market_overview. "
            "Set market_size_estimate and growth_rate to null (no verified data) and list them in "
            "unsupported_claims. All descriptive fields MUST be filled with domain knowledge.\n"
        )

    suffix = ANTI_HALLUCINATION_SUFFIX
    prompt = f"""Startup Idea: {idea}
Industry: {industry}
Healthcare Mode: {healthcare_mode}

Web Research Data:
{sources_text}
{no_source_note}

Return a JSON object with exactly this structure:
{{
  "market_overview": "2-3 sentence description of the market",
  "key_players": ["company1", "company2", "company3"],
  "market_size_estimate": "e.g. $45B globally by 2027",
  "recent_trends": ["trend1", "trend2", "trend3"],
  "growth_rate": "e.g. 18% CAGR 2024-2029",
  "target_customers": ["segment1", "segment2"],
  "pain_points": ["pain1", "pain2", "pain3"],
  "summary": "comprehensive paragraph summarizing the market landscape",
  "evidence_quality": "high|medium|low|insufficient_evidence",
  "unsupported_claims": ["list of field names not found in sources, or empty array"]
}}
{suffix}"""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=4000,
    )
    result = parse_json_response(raw)
    result["sources"] = source_urls
    return result


