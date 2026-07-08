from __future__ import annotations

from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.utils import parse_json_response

_SYSTEM = (
    "You are a critical business analyst. Challenge assumptions, identify weak evidence, "
    "and suggest validation experiments for startup ideas. Be rigorous and honest. "
    "Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    "You are a critical healthcare business analyst. Challenge clinical assumptions, "
    "highlight evidence gaps, regulatory hurdles, and suggest validation experiments "
    "including pilot studies, payer validation, and physician interviews. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(
    idea: str,
    industry: str,
    healthcare_mode: bool = False,
    research_data: Dict | None = None,
    competitor_data: Dict | None = None,
    opportunity_data: Dict | None = None,
    innovation_score_data: Dict | None = None,
) -> Dict[str, Any]:
    """
    Validation Agent: acts as a critical reviewer by challenging assumptions, identifying
    weak evidence, highlighting business risks, and suggesting validation experiments.
    """
    market_overview = (research_data or {}).get("market_overview", "")
    opportunity_score = (opportunity_data or {}).get("opportunity_score", 50)
    innovation_score = (innovation_score_data or {}).get("innovation_score", 50)
    blue_ocean = (opportunity_data or {}).get("blue_ocean_potential", "")
    saturation = (competitor_data or {}).get("market_saturation_score", 50)
    differentiation = (competitor_data or {}).get("differentiation_opportunities", [])

    healthcare_context = ""
    if healthcare_mode:
        healthcare_context = (
            "\nHealthcare-specific assumptions to challenge: clinical efficacy claims, "
            "physician adoption assumptions, reimbursement pathway assumptions, "
            "patient data access assumptions, regulatory timeline assumptions."
        )

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
Healthcare Mode: {healthcare_mode}
Market Overview: {market_overview}
Opportunity Score: {opportunity_score}/100
Innovation Score: {innovation_score}/100
Blue Ocean Potential: {blue_ocean}
Market Saturation: {saturation}/100
Differentiation Claims: {differentiation}
{healthcare_context}

Act as a devil's advocate. Challenge the key assumptions and suggest how to validate them.

Return a JSON object with exactly this structure:
{{
  "challenged_assumptions": [
    {{
      "assumption": "The assumption being made",
      "challenge": "Why this assumption might be wrong or overstated",
      "evidence_strength": "strong|moderate|weak",
      "impact_if_wrong": "high|medium|low"
    }}
  ],
  "validation_experiments": [
    "Concrete experiment or action to validate assumption 1",
    "Validation experiment 2",
    "Validation experiment 3"
  ],
  "confidence_level": "high|medium|low",
  "key_risks_identified": ["risk1", "risk2", "risk3"],
  "recommendation": "Overall 1-2 sentence recommendation on whether to proceed, pivot, or abandon"
}}
Include 3-5 challenged assumptions and 4-6 validation experiments."""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_PRO,
        max_tokens=3000,
    )
    return parse_json_response(raw)
