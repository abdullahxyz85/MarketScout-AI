from __future__ import annotations

from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.utils import parse_json_response

_SYSTEM = (
    "You are the Idea Guard — a strict but fair startup idea validator. "
    "Your job is to protect the research pipeline from vague, nonsensical, illegal, or "
    "unethical ideas, while letting through genuine startup concepts that deserve deep analysis. "
    "You must be objective, precise, and constructive. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(idea: str, industry: str) -> Dict[str, Any]:
    """
    Idea Guard Agent: validates a startup idea across six dimensions before the
    main research pipeline starts.  Returns a structured verdict.

    Dimensions checked:
      1. Clarity        – Is the idea clearly articulated?
      2. Startup nature – Is this a genuine business / product / service concept?
      3. Legality       – Is the idea legal in major jurisdictions?
      4. Ethics         – Is the idea ethically sound (no harm, exploitation, etc.)?
      5. Technical plausibility – Can it be built with today's or near-future technology?
      6. Market existence – Is there a plausible target market with real demand?

    Verdict options:
      - "approved"           → pipeline continues normally
      - "needs_clarification" → idea is too vague; user should refine it
      - "rejected"           → idea is illegal, unethical, non-startup, or clearly infeasible
    """

    prompt = f"""Startup Idea: {idea}
Industry: {industry if industry else "not specified"}

Evaluate this startup idea across the six dimensions below and return your verdict.

Scoring rules:
- clarity_score: 0–100 (0 = completely meaningless, 100 = crystal clear)
- vagueness_score: 0–100 (0 = perfectly specific, 100 = impossibly vague)
- technical_feasibility: "feasible" | "challenging" | "not_feasible"
- legal_status: "legal" | "questionable" | "illegal"
- ethical_status: "ethical" | "questionable" | "unethical"
- market_potential: "strong" | "moderate" | "weak" | "none"
- is_startup_idea: true if this describes a concrete business, product, service, or platform; false otherwise
- verdict:
    * "approved"            if clarity_score >= 50, vagueness_score <= 65, is_startup_idea=true,
                              legal_status != "illegal", ethical_status != "unethical",
                              technical_feasibility != "not_feasible", market_potential != "none"
    * "needs_clarification" if clarity_score is between 30 and 49, or vagueness_score > 65, or
                              is_startup_idea=true but the description is too generic to research
    * "rejected"            if legal_status="illegal", or ethical_status="unethical",
                              or is_startup_idea=false, or technical_feasibility="not_feasible",
                              or market_potential="none"

Return a JSON object with exactly this structure (no extra keys, no markdown):
{{
  "clarity_score": <0-100>,
  "vagueness_score": <0-100>,
  "is_startup_idea": <true|false>,
  "legal_status": "<legal|questionable|illegal>",
  "ethical_status": "<ethical|questionable|unethical>",
  "technical_feasibility": "<feasible|challenging|not_feasible>",
  "market_potential": "<strong|moderate|weak|none>",
  "verdict": "<approved|needs_clarification|rejected>",
  "verdict_summary": "<One sentence explaining the overall verdict>",
  "rejection_reasons": [
    "<Reason 1 if verdict is rejected or needs_clarification, else empty list>"
  ],
  "improvement_suggestions": [
    "<Actionable suggestion to make the idea clearer or more viable, else empty list>"
  ],
  "dimension_notes": {{
    "clarity": "<brief note>",
    "startup_nature": "<brief note>",
    "legality": "<brief note>",
    "ethics": "<brief note>",
    "technical_feasibility": "<brief note>",
    "market": "<brief note>"
  }}
}}"""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=1200,
    )

    result = parse_json_response(raw)

    # ── Fallback / safety defaults ──────────────────────────────────────────
    result.setdefault("clarity_score", 50)
    result.setdefault("vagueness_score", 50)
    result.setdefault("is_startup_idea", True)
    result.setdefault("legal_status", "legal")
    result.setdefault("ethical_status", "ethical")
    result.setdefault("technical_feasibility", "feasible")
    result.setdefault("market_potential", "moderate")
    result.setdefault("verdict", "approved")
    result.setdefault("verdict_summary", "")
    result.setdefault("rejection_reasons", [])
    result.setdefault("improvement_suggestions", [])
    result.setdefault("dimension_notes", {})

    return result
