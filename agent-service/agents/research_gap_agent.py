from __future__ import annotations

import asyncio
from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.tavily_client import search
from services.utils import ANTI_HALLUCINATION_SUFFIX, PROMPT_INJECTION_GUARD, extract_source_urls, format_sources_for_prompt, parse_json_response, truncate_sources

_SYSTEM = (
    PROMPT_INJECTION_GUARD +
    "You are a market gap and innovation analyst. Identify unexplored opportunities and "
    "missing features based ONLY on the retrieved sources. "
    "Do not invent gaps not evidenced in the data. "
    "Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    PROMPT_INJECTION_GUARD +
    "You are a healthcare market gap analyst. Identify unmet clinical needs and care gaps "
    "based ONLY on retrieved sources. Do not fabricate clinical outcomes or patient data. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(
    idea: str,
    industry: str,
    healthcare_mode: bool = False,
    competitor_data: Dict | None = None,
    scientific_data: Dict | None = None,
) -> Dict[str, Any]:
    """
    Research Gap Agent: compares competitors, publications, and GitHub projects to identify
    unexplored opportunities, missing features, and emerging niches in the target market.
    """
    queries = [
        f"{idea} {industry} market gap unmet need missing solution problem",
        f"{idea} {industry} what is missing limitations current solutions",
        f"{industry} github open source projects {idea} innovation",
    ]
    if healthcare_mode:
        queries.append(f"{idea} unmet clinical need care gap patient outcome improvement")

    raw_results = await asyncio.gather(
        *[search(q, max_results=4) for q in queries[:4]],
        return_exceptions=True,
    )
    search_results = []
    for r in raw_results:
        if isinstance(r, list):
            search_results.extend(r)

    sources_text = format_sources_for_prompt(truncate_sources(search_results[:10]))

    competitor_context = ""
    if competitor_data and competitor_data.get("differentiation_opportunities"):
        opps = competitor_data["differentiation_opportunities"]
        competitor_context = f"\nKnown differentiation opportunities from competitor analysis: {opps}"

    scientific_context = ""
    if scientific_data and scientific_data.get("research_gaps"):
        gaps = scientific_data["research_gaps"]
        scientific_context = f"\nKnown research gaps from scientific analysis: {gaps}"

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
Healthcare Mode: {healthcare_mode}
{competitor_context}
{scientific_context}

Web Research Data:
{sources_text}

Return a JSON object with exactly this structure:
{{
  "unexplored_opportunities": ["opportunity1", "opportunity2", "opportunity3"],
  "missing_features_in_market": ["missing feature1", "missing feature2"],
  "emerging_niches": ["niche1", "niche2"],
  "competitor_blind_spots": ["blind spot1", "blind spot2"],
  "technology_white_spaces": ["white space1", "white space2"],
  "novelty_score": 75,
  "differentiation_thesis": "2-3 sentences on how this idea can uniquely differentiate itself",
  "evidence_quality": "high|medium|low|insufficient_evidence",
  "unsupported_claims": ["list of field names not found in sources, or empty array"]
}}
novelty_score is 0-100 (100 = highly novel, no similar solution exists).
{suffix}""".format(suffix=ANTI_HALLUCINATION_SUFFIX)

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=1500,
    )
    result = parse_json_response(raw)
    result["sources"] = extract_source_urls(search_results)
    return result
