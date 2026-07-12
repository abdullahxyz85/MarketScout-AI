"""
Investor Agent
==============
Generates a structured investor summary (executive memo) from the
full pipeline state — ready to share with VCs or angels.

Independent agent — never registered in the main pipeline.

Usage
-----
    from agents.investor_agent import run

    memo = await run(pipeline_state)
"""
from __future__ import annotations

from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.utils import parse_json_response

_SYSTEM = (
    "You are a top-tier venture capital partner with 15+ years of experience evaluating "
    "startups across SaaS, deep tech, marketplace, and consumer sectors. "
    "Write a concise, compelling investor summary memo that a VC partner would send "
    "to their investment committee. Be data-driven, skeptical, and highlight both "
    "the opportunity and the key risks. "
    "Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    "You are a healthcare-focused venture capital partner specializing in digital health, "
    "medtech, and life sciences. Write an investor memo that addresses clinical evidence, "
    "regulatory risk, reimbursement strategy, and healthcare market dynamics. "
    "Respond with valid JSON only, no markdown, no extra text."
)


async def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Investor Agent: produces a structured investor summary memo suitable
    for sharing with venture capitalists or angel investors.

    Parameters
    ----------
    state : dict
        Full pipeline state.

    Returns
    -------
    dict with investor summary sections.
    """
    idea             = state.get("idea", "")
    industry         = state.get("industry", "")
    healthcare_mode  = state.get("healthcare_mode", False)

    research         = state.get("research")      or {}
    competitors      = state.get("competitors")   or {}
    opportunities    = state.get("opportunities")  or {}
    risks            = state.get("risks")          or {}
    strategy         = state.get("strategy")       or {}
    validation       = state.get("validation")     or {}
    funding          = state.get("funding")        or {}
    innovation_score = state.get("innovation_score") or {}
    swot             = state.get("swot")           or {}
    trends           = state.get("trends")         or {}

    market_size      = research.get("market_size_estimate", "Unknown")
    growth_rate      = research.get("growth_rate", "Unknown")
    market_overview  = research.get("market_overview", "")
    pain_points      = (research.get("pain_points") or [])[:3]

    saturation       = competitors.get("market_saturation_score", 50)
    comp_landscape   = competitors.get("competitive_landscape", "")
    differentiation  = (competitors.get("differentiation_opportunities") or [])[:3]

    opp_score        = opportunities.get("opportunity_score", "N/A")
    blue_ocean       = opportunities.get("blue_ocean_potential", "")
    market_gaps      = (opportunities.get("market_gaps") or [])[:3]

    risk_level       = risks.get("overall_risk_level", "medium")
    risk_score       = risks.get("risk_score", 50)
    critical_risks   = (risks.get("critical_risks") or [])[:3]

    gtm              = strategy.get("go_to_market", "")
    pricing          = strategy.get("pricing_strategy", "")
    strategic_recs   = (strategy.get("strategic_recommendations") or [])[:3]

    confidence       = validation.get("confidence_level", "medium")
    recommendation   = validation.get("recommendation", "")
    challenged       = (validation.get("challenged_assumptions") or [])[:2]

    funding_activity = funding.get("funding_activity_score", 50)
    top_investors    = (funding.get("top_investors") or [])[:5]
    avg_valuation    = funding.get("average_valuation_range", "Unknown")
    funding_trend    = funding.get("funding_trend", "")
    recent_rounds    = (funding.get("recent_funding_rounds") or [])[:3]

    inno_score       = innovation_score.get("innovation_score", "N/A")
    grade            = innovation_score.get("grade", "N/A")
    inno_explanation = innovation_score.get("score_explanation", "")

    strengths        = (swot.get("strengths") or [])[:3]
    weaknesses       = (swot.get("weaknesses") or [])[:3]
    market_trends    = (trends.get("trends") or [])[:3]

    healthcare_context = ""
    if healthcare_mode:
        healthcare_context = (
            "\nHealthcare context: evaluate regulatory pathway, "
            "reimbursement potential, clinical evidence strength, "
            "and physician/hospital adoption likelihood."
        )

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
{healthcare_context}

=== MARKET DATA ===
Market Overview: {market_overview}
Market Size: {market_size}
Growth Rate: {growth_rate}
Pain Points: {pain_points}
Key Trends: {market_trends}

=== COMPETITIVE ANALYSIS ===
Landscape: {comp_landscape}
Saturation: {saturation}/100
Differentiation: {differentiation}
Blue Ocean Potential: {blue_ocean}

=== OPPORTUNITY & INNOVATION ===
Opportunity Score: {opp_score}/100
Market Gaps: {market_gaps}
Innovation Score: {inno_score}/100 (Grade: {grade})
Innovation Thesis: {inno_explanation}

=== STRATEGY ===
Go-to-Market: {gtm}
Pricing: {pricing}
Strategic Recommendations: {strategic_recs}

=== VALIDATION ===
Confidence: {confidence}
Recommendation: {recommendation}
Key Challenged Assumptions: {challenged}

=== RISKS ===
Overall Risk Level: {risk_level} ({risk_score}/100)
Critical Risks: {critical_risks}

=== FUNDING LANDSCAPE ===
Activity Score: {funding_activity}/100
Top Investors Active in Space: {top_investors}
Average Valuation Range: {avg_valuation}
Funding Trend: {funding_trend}
Recent Rounds: {recent_rounds}

=== SWOT ===
Strengths: {strengths}
Weaknesses: {weaknesses}

Write a compelling, honest investor summary memo.
Return a JSON object with exactly this structure:
{{
  "one_liner": "Single sentence pitch: [Company] does [X] for [Y] to achieve [Z]",
  "investment_thesis": "2-3 sentences: why this is a compelling investment right now",
  "problem": "The core problem — size, urgency, and why it matters to investors",
  "solution": "The proposed solution and why it is differentiated",
  "market_opportunity": {{
    "tam": "Total Addressable Market estimate",
    "sam": "Serviceable Addressable Market estimate",
    "som": "Serviceable Obtainable Market (3-5 year target)",
    "growth_driver": "Primary driver of market growth"
  }},
  "business_model": {{
    "model_type": "e.g. SaaS, marketplace, transactional",
    "primary_revenue": "Main revenue stream",
    "unit_economics": "LTV/CAC ratio, gross margin estimate",
    "scalability": "high|medium|low"
  }},
  "traction_signals": ["Signal 1 from research", "Signal 2", "Signal 3"],
  "competitive_moat": "Defensible competitive advantage",
  "key_risks": [
    {{"risk": "Risk description", "severity": "high|medium|low", "mitigation": "How to address"}}
  ],
  "why_now": "Market timing argument — why this opportunity exists today",
  "funding_ask": {{
    "recommended_round": "e.g. Pre-seed, Seed, Series A",
    "amount_range": "e.g. $500K-$2M",
    "use_of_funds": ["Hiring — 40%", "Product — 30%", "GTM — 20%", "Ops — 10%"],
    "runway": "Expected runway at this funding level"
  }},
  "exit_strategy": "Potential exit paths (acquisition targets, IPO likelihood)",
  "red_flags": ["Any concern that would make a VC pass"],
  "green_flags": ["Strong positive signals that support investment"],
  "verdict": "invest|pass|watch",
  "verdict_rationale": "1-2 sentence honest assessment"
}}"""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_PRO,
        max_tokens=3500,
    )
    result = parse_json_response(raw)

    # Safety defaults
    result.setdefault("one_liner", "")
    result.setdefault("investment_thesis", "")
    result.setdefault("problem", "")
    result.setdefault("solution", "")
    result.setdefault("market_opportunity", {})
    result.setdefault("business_model", {})
    result.setdefault("traction_signals", [])
    result.setdefault("competitive_moat", "")
    result.setdefault("key_risks", [])
    result.setdefault("why_now", "")
    result.setdefault("funding_ask", {})
    result.setdefault("exit_strategy", "")
    result.setdefault("red_flags", [])
    result.setdefault("green_flags", [])
    result.setdefault("verdict", "watch")
    result.setdefault("verdict_rationale", "")

    result["_agent"]    = "investor_agent"
    result["_idea"]     = idea
    result["_industry"] = industry

    return result
