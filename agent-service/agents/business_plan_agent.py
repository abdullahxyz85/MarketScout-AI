"""
Business Plan Agent
===================
Generates a structured business plan from the full pipeline state.

Independent agent — never registered in the main pipeline.
Can be called on-demand after the pipeline completes.

Usage
-----
    from agents.business_plan_agent import run

    plan = await run(pipeline_state)
"""
from __future__ import annotations

from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.utils import parse_json_response

_SYSTEM = (
    "You are a senior startup business strategist and entrepreneur with 20+ years of experience "
    "writing business plans that have secured millions in funding. "
    "Generate a comprehensive, investor-ready business plan based on the market research data provided. "
    "Be specific, data-driven, and realistic. "
    "Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    "You are a senior healthcare startup strategist with deep expertise in digital health, "
    "medtech, and biopharma commercialization. Generate a business plan that addresses "
    "clinical evidence, regulatory pathways (FDA/CE), reimbursement strategy, and "
    "hospital procurement dynamics. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Business Plan Agent: synthesizes all pipeline research into a structured
    investor-ready business plan.

    Parameters
    ----------
    state : dict
        Full pipeline state (ResearchState or equivalent dict with agent outputs).

    Returns
    -------
    dict with structured business plan sections.
    """
    idea             = state.get("idea", "")
    industry         = state.get("industry", "")
    healthcare_mode  = state.get("healthcare_mode", False)

    # Extract key data from agents
    research         = state.get("research")      or state.get("research_data") or {}
    competitors      = state.get("competitors")   or state.get("competitor_data") or {}
    swot             = state.get("swot")           or state.get("swot_data") or {}
    opportunities    = state.get("opportunities")  or state.get("opportunity_data") or {}
    risks            = state.get("risks")          or state.get("risk_data") or {}
    strategy         = state.get("strategy")       or state.get("strategy_data") or {}
    validation       = state.get("validation")     or state.get("validation_data") or {}
    funding          = state.get("funding")        or state.get("funding_data") or {}
    innovation_score = state.get("innovation_score") or {}
    trends           = state.get("trends")         or state.get("trend_data") or {}

    market_size      = research.get("market_size_estimate") or "Unknown"
    growth_rate      = research.get("growth_rate") or "Unknown"
    market_overview  = research.get("market_overview") or ""
    pain_points      = (research.get("pain_points") or [])[:3]
    target_customers = (research.get("target_customers") or [])[:3]
    saturation       = competitors.get("market_saturation_score") or 50
    differentiation  = (competitors.get("differentiation_opportunities") or [])[:3]
    strengths        = (swot.get("strengths") or [])[:3]
    opp_score        = opportunities.get("opportunity_score") or "N/A"
    market_gaps      = (opportunities.get("market_gaps") or [])[:3]
    risk_level       = risks.get("overall_risk_level") or "medium"
    critical_risks   = (risks.get("critical_risks") or [])[:3]
    gtm              = strategy.get("go_to_market") or ""
    pricing          = strategy.get("pricing_strategy") or ""
    partnerships     = (strategy.get("key_partnerships") or [])[:3]
    roadmap          = strategy.get("roadmap") or {}
    recommendation   = validation.get("recommendation") or ""
    funding_activity = funding.get("funding_activity_score") or 50
    top_investors    = (funding.get("top_investors") or [])[:3]
    avg_valuation    = funding.get("average_valuation_range") or "Unknown"
    inno_score       = innovation_score.get("innovation_score") or "N/A"
    market_trends    = (trends.get("trends") or [])[:3]

    healthcare_context = ""
    if healthcare_mode:
        healthcare_context = (
            "\nHealthcare context: Include FDA/CE regulatory pathway, "
            "reimbursement strategy (CMS/payer), clinical evidence requirements, "
            "and hospital/health-system procurement approach."
        )

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
{healthcare_context}

=== RESEARCH DATA ===
Market Overview: {market_overview}
Market Size: {market_size}
Growth Rate: {growth_rate}
Target Customers: {target_customers}
Pain Points: {pain_points}
Market Saturation: {saturation}/100
Differentiation Opportunities: {differentiation}

=== COMPETITIVE & STRATEGIC DATA ===
Key Strengths: {strengths}
Market Gaps: {market_gaps}
Opportunity Score: {opp_score}/100
Innovation Score: {inno_score}/100
Go-to-Market: {gtm}
Pricing Strategy: {pricing}
Key Partnerships: {partnerships}
Roadmap: {roadmap}

=== VALIDATION & RISK ===
Validation Recommendation: {recommendation}
Risk Level: {risk_level}
Critical Risks: {critical_risks}

=== MARKET CONTEXT ===
Funding Activity: {funding_activity}/100
Top Investors in Space: {top_investors}
Average Valuation: {avg_valuation}
Key Trends: {market_trends}

Generate a comprehensive, investor-ready business plan.
Return a JSON object with exactly this structure:
{{
  "executive_summary": "4-5 sentence summary of the entire business opportunity",
  "problem_statement": "Clear description of the problem being solved",
  "solution": "Description of the product/service and how it solves the problem",
  "value_proposition": "Unique value proposition in one sentence",
  "target_market": {{
    "primary_segment": "Primary customer segment",
    "secondary_segment": "Secondary customer segment",
    "market_size": "TAM/SAM/SOM estimates",
    "customer_profile": "Detailed ideal customer profile"
  }},
  "product": {{
    "description": "What the product/service is",
    "key_features": ["feature1", "feature2", "feature3"],
    "technology_stack": "Key technologies used",
    "mvp_scope": "What the MVP would include"
  }},
  "business_model": {{
    "revenue_streams": ["stream1", "stream2"],
    "pricing_model": "How the product is priced",
    "unit_economics": "LTV, CAC, gross margin estimates",
    "monetization_timeline": "When revenue begins"
  }},
  "go_to_market": {{
    "launch_strategy": "Initial launch approach",
    "channels": ["channel1", "channel2", "channel3"],
    "early_adopters": "Who to target first and why",
    "growth_strategy": "How to scale beyond initial launch"
  }},
  "competitive_advantage": "Why this startup wins vs. alternatives",
  "competition": {{
    "main_competitors": ["competitor1", "competitor2"],
    "differentiation": "Key differentiators",
    "moat": "Defensible competitive moat"
  }},
  "team_requirements": [
    {{"role": "Role title", "skills": "Required skills", "priority": "immediate|6months|year1"}}
  ],
  "financial_projections": {{
    "funding_required": "How much funding is needed and why",
    "use_of_funds": ["item1 — X%", "item2 — Y%"],
    "year_1_revenue": "Year 1 revenue estimate",
    "year_3_revenue": "Year 3 revenue estimate",
    "break_even": "Estimated break-even timeline",
    "key_assumptions": ["assumption1", "assumption2"]
  }},
  "milestones": [
    {{"phase": "Phase name", "timeline": "e.g. 0-3 months", "goals": ["goal1", "goal2"]}}
  ],
  "risks_and_mitigations": [
    {{"risk": "Risk description", "mitigation": "How to mitigate it", "severity": "high|medium|low"}}
  ],
  "success_metrics": ["metric1", "metric2", "metric3"]
}}"""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_PRO,
        max_tokens=4000,
    )
    result = parse_json_response(raw)

    # Safety defaults
    result.setdefault("executive_summary", "")
    result.setdefault("problem_statement", "")
    result.setdefault("solution", "")
    result.setdefault("value_proposition", "")
    result.setdefault("target_market", {})
    result.setdefault("product", {})
    result.setdefault("business_model", {})
    result.setdefault("go_to_market", {})
    result.setdefault("competitive_advantage", "")
    result.setdefault("competition", {})
    result.setdefault("team_requirements", [])
    result.setdefault("financial_projections", {})
    result.setdefault("milestones", [])
    result.setdefault("risks_and_mitigations", [])
    result.setdefault("success_metrics", [])

    # Metadata
    result["_agent"] = "business_plan_agent"
    result["_idea"]  = idea
    result["_industry"] = industry

    return result
