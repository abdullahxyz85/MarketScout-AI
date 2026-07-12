from __future__ import annotations

import json
from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.utils import parse_json_response

_SYSTEM = (
    "You are a senior startup strategist. Generate evidence-based strategic recommendations, "
    "go-to-market strategy, innovation hypotheses, and an execution roadmap. "
    "Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    "You are a senior healthcare startup strategist. Generate strategic recommendations "
    "tailored to healthcare commercialization including payer engagement, clinical champion "
    "strategy, regulatory pathway, and health system partnerships. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(
    idea: str,
    industry: str,
    healthcare_mode: bool = False,
    research_data: Dict | None = None,
    competitor_data: Dict | None = None,
    opportunity_data: Dict | None = None,
    swot_data: Dict | None = None,
    validation_data: Dict | None = None,
    gap_data: Dict | None = None,
    trend_data: Dict | None = None,
) -> Dict[str, Any]:
    """
    Strategy Agent: synthesizes all research outputs into strategic recommendations,
    go-to-market strategy, innovation hypotheses, pricing strategy, and execution roadmap.
    """
    swot_strengths = ((swot_data or {}).get("strengths") or [])[:3]
    swot_opps = ((swot_data or {}).get("opportunities") or [])[:3]
    diff_strategies = ((opportunity_data or {}).get("differentiation_strategies") or [])[:3]
    target_segments = ((opportunity_data or {}).get("target_segments") or [])[:2]
    validation_rec = (validation_data or {}).get("recommendation", "")
    emerging_tech = ((trend_data or {}).get("emerging_technologies") or [])[:3]
    niches = ((gap_data or {}).get("emerging_niches") or [])[:2]
    gaps = ((gap_data or {}).get("unexplored_opportunities") or [])[:3]

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
Healthcare Mode: {healthcare_mode}

Key Strengths: {swot_strengths}
Market Opportunities: {swot_opps}
Differentiation Strategies: {diff_strategies}
Target Segments: {target_segments}
Validation Recommendation: {validation_rec}
Emerging Technologies: {emerging_tech}
Emerging Niches: {niches}
Market Gaps: {gaps}

Generate a comprehensive strategy. Return a JSON object with exactly this structure:
{{
  "strategic_recommendations": [
    "Specific recommendation 1",
    "Specific recommendation 2",
    "Specific recommendation 3",
    "Specific recommendation 4",
    "Specific recommendation 5"
  ],
  "innovation_hypotheses": [
    {{
      "hypothesis": "Clear hypothesis statement",
      "type": "customer_segment|pricing|product|technology|distribution",
      "rationale": "Why this hypothesis is worth testing"
    }}
  ],
  "go_to_market": "Comprehensive 3-4 sentence go-to-market strategy",
  "competitive_positioning": "Positioning statement and differentiation narrative",
  "pricing_strategy": "Recommended pricing model and rationale",
  "key_partnerships": ["Partner type 1", "Partner type 2", "Partner type 3"],
  "success_metrics": ["KPI 1", "KPI 2", "KPI 3", "KPI 4"],
  "roadmap": {{
    "month_1_3": ["Action 1", "Action 2", "Action 3"],
    "month_4_6": ["Action 4", "Action 5", "Action 6"],
    "month_7_12": ["Action 7", "Action 8", "Action 9"]
  }}
}}
Include 3-4 innovation hypotheses covering different types."""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=5000,
    )
    return parse_json_response(raw)


async def run_scenario_simulation(
    base_result: Dict[str, Any],
    scenario: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Simulate a 'what-if' scenario against a base research result.
    Analyzes the impact of scenario changes on market opportunity, competitive positioning,
    revenue potential, risk profile, and time-to-market.
    """
    report = base_result.get("report") or {}
    strategy = base_result.get("strategy") or {}
    innovation = base_result.get("innovation_score") or {}

    prompt = f"""Base Research:
Idea: {base_result.get('idea', '')}
Industry: {base_result.get('industry', '')}
Executive Summary: {report.get('executive_summary', '')[:400]}
Current Go-to-Market: {strategy.get('go_to_market', '')[:300]}
Innovation Score: {innovation.get('innovation_score', 'N/A')}/100

Scenario to Simulate:
{json.dumps(scenario, indent=2)}

Analyze the projected impact of this scenario change. Return a JSON object:
{{
  "scenario_summary": "What this scenario entails in 1-2 sentences",
  "impact_analysis": {{
    "market_opportunity": {{
      "change": "increase|decrease|neutral",
      "magnitude": "significant|moderate|minor",
      "explanation": "why"
    }},
    "competitive_positioning": {{
      "change": "stronger|weaker|neutral",
      "explanation": "why"
    }},
    "revenue_potential": {{
      "change": "higher|lower|similar",
      "estimated_range": "e.g. $5M-$20M ARR at year 3",
      "explanation": "why"
    }},
    "risk_profile": {{
      "change": "higher|lower|similar",
      "new_risks": ["new risk 1"],
      "mitigated_risks": ["mitigated risk 1"],
      "explanation": "why"
    }},
    "time_to_market": {{
      "change": "faster|slower|same",
      "estimated_timeline": "e.g. 12-18 months",
      "explanation": "why"
    }}
  }},
  "overall_recommendation": "Proceed|Proceed with Caution|Avoid",
  "key_action_items": ["action 1", "action 2", "action 3"]
}}"""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=(
            "You are a strategic scenario analyst. Evaluate business scenarios rigorously "
            "and provide evidence-based projections. Respond with valid JSON only."
        ),
        model=FireworksModel.DEEPSEEK_V4_FLASH,
        max_tokens=3000,
    )
    return parse_json_response(raw)
