from __future__ import annotations

import asyncio
from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.tavily_client import search
from services.utils import ANTI_HALLUCINATION_SUFFIX, PROMPT_INJECTION_GUARD, extract_source_urls, format_sources_for_prompt, idea_to_query, parse_json_response, truncate_sources

_SYSTEM = (
    PROMPT_INJECTION_GUARD +
    "You are a patent intelligence analyst. Analyze ONLY the provided patent data and return "
    "a structured JSON report. Base every patent claim on the retrieved sources. "
    "Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    PROMPT_INJECTION_GUARD +
    "You are a biomedical patent analyst. Assess the IP landscape for this healthcare "
    "startup strictly from retrieved sources. Do not invent patent numbers, titles, or holders. "
    "Respond with valid JSON only, no markdown."
)


async def run(idea: str, industry: str, healthcare_mode: bool = False) -> Dict[str, Any]:
    """
    Patent Intelligence Agent: analyzes public patent databases to identify existing IP,
    white spaces for innovation, and freedom-to-operate risks.
    """
    kw = idea_to_query(idea)
    queries = [
        f"{kw} {industry} patent intellectual property USPTO",
        f"{kw} technology patent landscape existing IP",
    ]
    if healthcare_mode:
        queries.append(f"{kw} medical device pharma patent clinical method claim")
    else:
        queries.append(f"{kw} software patent AI innovation IP landscape")

    raw_results = await asyncio.gather(
        *[search(q, max_results=4, include_domains=[
            "patents.google.com", "patents.justia.com", "USPTO.gov",
            "freepatentsonline.com", "espacenet.epo.org",
        ]) for q in queries[:3]],
        return_exceptions=True,
    )
    search_results = []
    for r in raw_results:
        if isinstance(r, list):
            search_results.extend(r)

    # Fallback search without domain restriction if no results found
    if not search_results:
        try:
            fallback = await search(f"{kw} {industry} patent analysis IP", max_results=6)
            search_results.extend(fallback)
        except Exception:
            pass  # Rate limit or other error — continue without fallback results

    sources_text = format_sources_for_prompt(truncate_sources(search_results[:8]))

    no_source_note = ""
    if not search_results:
        no_source_note = (
            "\nNOTE: No web sources were retrieved. Use your domain knowledge to: "
            "(1) describe 2-3 REAL known patent families or key holders in this IP space, "
            "(2) identify technology white spaces based on the idea's novelty, "
            "(3) assess freedom-to-operate risks from known patent holders. "
            "Set existing_patents titles to known patent areas (not specific patent numbers). "
            "List patent numbers in unsupported_claims. "
            "patent_density_score MUST be filled in.\n"
        )

    suffix = ANTI_HALLUCINATION_SUFFIX
    prompt = f"""Startup Idea: {idea}
Industry: {industry}
Healthcare Mode: {healthcare_mode}

Patent Research Data:
{sources_text}
{no_source_note}

Return a JSON object with exactly this structure:
{{
  "existing_patents": [
    {{
      "title": "Patent title or description",
      "holder": "Company or inventor",
      "description": "what the patent covers",
      "year": "filing or grant year",
      "risk_level": "high|medium|low"
    }}
  ],
  "patent_density_score": 45,
  "white_spaces": ["IP opportunity1", "IP opportunity2"],
  "freedom_to_operate_risks": ["risk1", "risk2"],
  "ip_strategy_recommendation": "Recommended IP approach for this startup",
  "evidence_quality": "high|medium|low|insufficient_evidence",
  "unsupported_claims": ["list of field names not found in sources, or empty array"]
}}
patent_density_score is 0-100 (100 = extremely crowded IP space, hard to operate freely).
{suffix}"""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=4000,
        temperature=0,  # deterministic — patent_density_score must be stable
    )
    result = parse_json_response(raw)
    result["sources"] = extract_source_urls(search_results)
    return result


