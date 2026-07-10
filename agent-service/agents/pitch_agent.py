"""
Pitch Deck Agent
================
Generates a complete 10-slide pitch deck from the full pipeline state.
Each slide includes a title, headline, bullet content, and speaker notes.

Standard deck structure:
  1  Title / Company
  2  Problem
  3  Solution
  4  Market Size (TAM/SAM/SOM)
  5  Product / How It Works
  6  Business Model
  7  Traction & Validation
  8  Competitive Landscape
  9  Team
  10 The Ask

Independent agent — never registered in the main pipeline.

Usage
-----
    from agents.pitch_agent import run

    deck = await run(pipeline_state)
    for slide in deck["slides"]:
        print(slide["number"], slide["title"])
"""
from __future__ import annotations

from typing import Any, Dict

from services.fireworks_client import FireworksModel, call_llm
from services.utils import parse_json_response

_SYSTEM = (
    "You are a world-class pitch deck consultant who has helped 200+ startups raise "
    "from top-tier VCs including Y Combinator, Sequoia, and a16z. "
    "Create a compelling, concise, and visually-structured 10-slide pitch deck. "
    "Each slide must be punchy — maximum impact, minimum words. "
    "Speaker notes should be conversational and fill in the story behind the slide. "
    "Respond with valid JSON only, no markdown, no extra text."
)
_SYSTEM_HC = (
    "You are a pitch deck consultant specializing in healthcare and life sciences startups. "
    "Create a 10-slide pitch that addresses clinical evidence, regulatory pathway, "
    "payer/reimbursement strategy, and the clinical champion approach that healthcare "
    "investors expect to see. "
    "Respond with valid JSON only, no markdown, no extra text."
)

_SLIDE_GUIDE = """
Slide structure guidelines:
  Slide 1  — Title: Company name, tagline, one-liner, contact
  Slide 2  — Problem: The pain, who has it, why it matters now (use data)
  Slide 3  — Solution: Product/service, key differentiator, "wow" moment
  Slide 4  — Market Size: TAM → SAM → SOM with $ figures and sources
  Slide 5  — Product: How it works (3-step flow), key features, screenshot description
  Slide 6  — Business Model: Revenue streams, pricing, unit economics
  Slide 7  — Traction: Evidence of demand, early customers, validation experiments
  Slide 8  — Competition: 2×2 matrix or table, why we win
  Slide 9  — Team: Founders, advisors, why this team is uniquely positioned
  Slide 10 — The Ask: Funding amount, use of funds, milestones to achieve with this round
"""


async def run(state: Dict[str, Any]) -> Dict[str, Any]:
    """
    Pitch Deck Agent: generates a full 10-slide pitch deck from pipeline state.

    Parameters
    ----------
    state : dict
        Full pipeline state.

    Returns
    -------
    dict with "slides" list and deck metadata.
    """
    idea             = state.get("idea", "")
    industry         = state.get("industry", "")
    healthcare_mode  = state.get("healthcare_mode", False)

    research         = state.get("research")       or {}
    competitors      = state.get("competitors")    or {}
    opportunities    = state.get("opportunities")  or {}
    risks            = state.get("risks")           or {}
    strategy         = state.get("strategy")        or {}
    validation       = state.get("validation")      or {}
    funding          = state.get("funding")         or {}
    innovation_score = state.get("innovation_score") or {}
    swot             = state.get("swot")            or {}
    trends           = state.get("trends")          or {}
    patents          = state.get("patents")         or {}

    market_size      = research.get("market_size_estimate") or "Unknown"
    growth_rate      = research.get("growth_rate") or "Unknown"
    market_overview  = research.get("market_overview") or ""
    pain_points      = (research.get("pain_points") or [])[:3]
    target_customers = (research.get("target_customers") or [])[:2]

    comp_landscape   = competitors.get("competitive_landscape") or ""
    saturation       = competitors.get("market_saturation_score") or 50
    comp_list        = [c.get("name", "") for c in (competitors.get("competitors") or [])[:4]]
    differentiation  = (competitors.get("differentiation_opportunities") or [])[:3]

    opp_score        = opportunities.get("opportunity_score") or "N/A"
    market_gaps      = (opportunities.get("market_gaps") or [])[:3]
    target_segs      = (opportunities.get("target_segments") or [])[:2]

    risk_level       = risks.get("overall_risk_level") or "medium"

    gtm              = strategy.get("go_to_market") or ""
    pricing          = strategy.get("pricing_strategy") or ""
    success_metrics  = (strategy.get("success_metrics") or [])[:4]
    partnerships     = (strategy.get("key_partnerships") or [])[:3]

    confidence       = validation.get("confidence_level") or "medium"
    recommendation   = validation.get("recommendation") or ""
    experiments      = (validation.get("validation_experiments") or [])[:3]

    funding_activity = funding.get("funding_activity_score") or 50
    avg_valuation    = funding.get("average_valuation_range") or "Unknown"
    top_investors    = (funding.get("top_investors") or [])[:3]

    inno_score       = innovation_score.get("innovation_score") or "N/A"
    inno_explanation = innovation_score.get("score_explanation") or ""

    strengths        = (swot.get("strengths") or [])[:3]
    opps_swot        = (swot.get("opportunities") or [])[:2]
    market_trends    = (trends.get("trends") or [])[:3]
    ip_rec           = patents.get("ip_strategy_recommendation") or ""

    healthcare_context = ""
    if healthcare_mode:
        healthcare_context = (
            "\nHealthcare context: Include FDA/regulatory pathway, "
            "clinical evidence, payer/reimbursement strategy, "
            "and physician adoption approach."
        )

    prompt = f"""Startup Idea: {idea}
Industry: {industry}
{healthcare_context}

{_SLIDE_GUIDE}

=== RESEARCH DATA ===
Market Overview: {market_overview}
Market Size: {market_size} | Growth: {growth_rate}
Target Customers: {target_customers}
Pain Points: {pain_points}
Key Trends: {market_trends}

=== COMPETITIVE ANALYSIS ===
Landscape: {comp_landscape} | Saturation: {saturation}/100
Main Competitors: {comp_list}
Differentiation: {differentiation}

=== OPPORTUNITY ===
Opportunity Score: {opp_score}/100
Market Gaps: {market_gaps}
Target Segments: {target_segs}
SWOT Strengths: {strengths}
SWOT Opportunities: {opps_swot}

=== INNOVATION & IP ===
Innovation Score: {inno_score}/100 — {inno_explanation}
IP: {ip_rec}

=== STRATEGY ===
GTM: {gtm}
Pricing: {pricing}
Key Partners: {partnerships}
Success Metrics: {success_metrics}

=== VALIDATION ===
Confidence: {confidence} | Recommendation: {recommendation}
Validation Experiments: {experiments}

=== FUNDING LANDSCAPE ===
Activity: {funding_activity}/100 | Avg Valuation: {avg_valuation}
Active Investors: {top_investors}

=== RISK ===
Overall Risk: {risk_level}

Generate a compelling 10-slide pitch deck.
Return a JSON object with exactly this structure:
{{
  "deck_title": "Company/product name",
  "tagline": "One punchy tagline (max 8 words)",
  "slides": [
    {{
      "number": 1,
      "title": "Slide title (e.g. The Problem)",
      "headline": "Single bold headline sentence for this slide",
      "content": [
        "Bullet point 1 (concise, impactful)",
        "Bullet point 2",
        "Bullet point 3"
      ],
      "visual_suggestion": "Description of the chart, image, or diagram to use",
      "speaker_notes": "What the founder says while presenting this slide (2-4 sentences)"
    }}
  ],
  "key_message": "The single most important thing investors should remember",
  "estimated_duration_minutes": 10
}}
Generate all 10 slides. Each slide: 3-5 bullet points, a compelling headline, visual suggestion, and speaker notes."""

    raw = await call_llm(
        prompt=prompt,
        system_prompt=_SYSTEM_HC if healthcare_mode else _SYSTEM,
        model=FireworksModel.DEEPSEEK_V4_PRO,
        max_tokens=5000,
    )
    result = parse_json_response(raw)

    # Safety defaults
    result.setdefault("deck_title", idea[:60] if idea else "Startup Pitch")
    result.setdefault("tagline", "")
    result.setdefault("key_message", "")
    result.setdefault("estimated_duration_minutes", 10)

    slides = result.get("slides", [])
    if not isinstance(slides, list):
        slides = []

    # Ensure all slides have required fields
    for i, slide in enumerate(slides):
        if isinstance(slide, dict):
            slide.setdefault("number", i + 1)
            slide.setdefault("title", f"Slide {i + 1}")
            slide.setdefault("headline", "")
            slide.setdefault("content", [])
            slide.setdefault("visual_suggestion", "")
            slide.setdefault("speaker_notes", "")

    result["slides"] = slides
    result["slide_count"] = len(slides)

    result["_agent"]    = "pitch_agent"
    result["_idea"]     = idea
    result["_industry"] = industry

    return result
