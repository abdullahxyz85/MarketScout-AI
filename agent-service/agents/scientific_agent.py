from __future__ import annotations

import asyncio
from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.tavily_client import search
from services.utils import ANTI_HALLUCINATION_SUFFIX, extract_source_urls, format_sources_for_prompt, parse_json_response, truncate_for_search, truncate_sources

_SYSTEM = (
    "You are a scientific research analyst. Summarize ONLY the research found in the "
    "provided sources. Do not invent paper titles, authors, or findings. "
    "Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    "You are a clinical and biomedical research analyst. Report ONLY clinical trials, "
    "studies, and guidelines found in the provided sources. "
    "Do not fabricate trial results, publication titles, or clinical outcomes. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(idea: str, industry: str, healthcare_mode: bool = False) -> Dict[str, Any]:
    """
    Scientific Research Agent: searches for relevant academic publications and research
    findings, then assesses the scientific maturity of the market space.
    """
    search_idea = truncate_for_search(idea)
    queries = [
        f"{search_idea} {industry} research paper scientific study 2023 2024",
        f"{search_idea} technology academic publication findings",
    ]
    if healthcare_mode:
        queries.extend([
            f"{search_idea} clinical trial results pubmed 2024",
            f"{search_idea} medical research evidence systematic review",
        ])
    else:
        queries.append(f"{industry} AI technology research innovation study")

    raw_results = await asyncio.gather(
        *[search(q, max_results=4, include_domains=(
            ["scholar.google.com", "pubmed.ncbi.nlm.nih.gov", "arxiv.org", "semanticscholar.org"]
            if healthcare_mode else
            ["arxiv.org", "scholar.google.com", "semanticscholar.org", "researchgate.net"]
        )) for q in queries[:3]],
        return_exceptions=True,
    )
    search_results = []
    for r in raw_results:
        if isinstance(r, list):
            search_results.extend(r)

    sources_text = format_sources_for_prompt(truncate_sources(search_results[:8]))

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
Healthcare Mode: {healthcare_mode}

Research Data Found:
{sources_text}

Return a JSON object with exactly this structure:
{{
  "relevant_papers": [
    {{
      "title": "Paper or study title",
      "summary": "key finding in 1-2 sentences",
      "relevance": "how this relates to the startup idea",
      "year": "publication year",
      "authors": "Author et al. or institution"
    }}
  ],
  "research_maturity": "early|growing|mature",
  "research_maturity_score": 60,
  "key_findings": ["finding1", "finding2", "finding3"],
  "research_gaps": ["gap1", "gap2"],
  "academic_consensus": "brief description of the scientific consensus on this space",
  "evidence_quality": "high|medium|low|insufficient_evidence",
  "unsupported_claims": ["list of field names not found in sources, or empty array"]
}}
Include 3 to 5 papers. research_maturity_score is 0-100 (100 = very mature field).
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
