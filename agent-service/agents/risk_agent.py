from __future__ import annotations

from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.utils import parse_json_response

_SYSTEM = (
    "You are a startup risk analyst. Evaluate the business, technical, market, and operational "
    "risks for this startup idea. Provide structured risk data with severity levels and "
    "mitigation strategies. Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    "You are a healthcare startup risk analyst. Evaluate clinical, regulatory (FDA, HIPAA, GDPR), "
    "reimbursement, liability, and adoption risks specific to healthcare innovations. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(
    idea: str,
    industry: str,
    healthcare_mode: bool = False,
    competitor_data: Dict | None = None,
    swot_data: Dict | None = None,
    patent_data: Dict | None = None,
) -> Dict[str, Any]:
    """
    Risk Agent: evaluates business, technical, market, and operational risks with
    severity/probability scores and concrete mitigation strategies.
    """
    threats = ((swot_data or {}).get("threats") or [])[:3]
    weaknesses = ((swot_data or {}).get("weaknesses") or [])[:3]
    ip_risks = ((patent_data or {}).get("freedom_to_operate_risks") or [])[:2]
    saturation = (competitor_data or {}).get("market_saturation_score", 50)

    healthcare_context = ""
    if healthcare_mode:
        healthcare_context = (
            "\nHealthcare-specific risks to consider: FDA clearance/approval timelines, "
            "HIPAA compliance, clinical evidence requirements, physician adoption resistance, "
            "hospital procurement cycles, reimbursement (CMS/payer) risks."
        )

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
Market Saturation: {saturation}/100
{healthcare_context}

SWOT Threats: {threats}
SWOT Weaknesses: {weaknesses}
IP Risks: {ip_risks}

Return a JSON object with exactly this structure:
{{
  "risks": [
    {{
      "name": "Risk name",
      "category": "market|technical|regulatory|financial|operational|competitive",
      "description": "detailed description of this risk",
      "severity": "high|medium|low",
      "probability": "high|medium|low",
      "mitigation": "concrete action to mitigate this risk"
    }}
  ],
  "overall_risk_level": "high|medium|low",
  "risk_score": 35,
  "critical_risks": ["Most critical risk 1", "Most critical risk 2"],
  "risk_mitigation_roadmap": "2-3 sentence overall risk mitigation strategy"
}}
Include 5-7 risks covering different categories.
risk_score is 0-100 (100 = extremely risky venture, 0 = very low risk)."""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=3000,
    )
    return parse_json_response(raw)
