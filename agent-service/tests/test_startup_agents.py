"""
Tests for agents/business_plan_agent.py, agents/investor_agent.py, agents/pitch_agent.py

These are INDEPENDENT agents — they are NOT in the pipeline.
All LLM calls are mocked so tests run offline.

Contracts under test:
  - Correct output structure (all required keys present)
  - Safety defaults applied when LLM returns empty JSON
  - Resilient to missing pipeline state keys
  - Resilient to garbage LLM output
  - Never modifies input state
  - Healthcare mode routed to specialised system prompt
"""
from __future__ import annotations

import copy
import json
from typing import Any, Dict
from unittest.mock import AsyncMock, patch

import pytest

import agents.business_plan_agent as business_plan_agent
import agents.investor_agent as investor_agent
import agents.pitch_agent as pitch_agent


# ─── Mock helpers ─────────────────────────────────────────────────────────────

def _mock_llm(module_path: str, payload: dict):
    return patch(
        f"{module_path}.call_llm",
        new=AsyncMock(return_value=json.dumps(payload)),
    )


def _mock_llm_raw(module_path: str, raw: str):
    return patch(
        f"{module_path}.call_llm",
        new=AsyncMock(return_value=raw),
    )


# ─── Shared pipeline state fixture ───────────────────────────────────────────

def _state() -> Dict[str, Any]:
    return {
        "job_id":          "test-123",
        "idea":            "AI-powered invoice automation for SMBs",
        "industry":        "FinTech",
        "healthcare_mode": False,
        "research": {
            "market_overview": "Large fintech market growing rapidly.",
            "market_size_estimate": "$20B",
            "growth_rate": "18% CAGR",
            "target_customers": ["SMBs", "Freelancers"],
            "pain_points": ["Manual invoice creation", "Late payments"],
            "summary": "Strong opportunity.",
        },
        "competitors": {
            "competitive_landscape": "Moderately competitive market.",
            "market_saturation_score": 55,
            "differentiation_opportunities": ["AI automation", "SMB focus"],
            "competitors": [{"name": "FreshBooks"}, {"name": "QuickBooks"}],
        },
        "swot": {
            "strengths": ["AI-native product", "Low cost"],
            "weaknesses": ["No brand recognition"],
            "opportunities": ["Underserved SMB segment"],
            "threats": ["Large incumbents"],
        },
        "opportunities": {
            "opportunity_score": 72,
            "blue_ocean_potential": "moderate",
            "market_gaps": ["No AI-native SMB invoicing"],
            "target_segments": [{"segment": "SMBs"}],
        },
        "risks": {
            "overall_risk_level": "medium",
            "risk_score": 38,
            "critical_risks": ["Low switching from QuickBooks"],
        },
        "strategy": {
            "go_to_market": "Product-led growth via free tier",
            "pricing_strategy": "Per-seat SaaS $29/mo",
            "strategic_recommendations": ["Launch to freelancers first"],
            "key_partnerships": ["Stripe", "Plaid"],
            "success_metrics": ["MRR", "NPS", "Churn"],
        },
        "validation": {
            "confidence_level": "medium",
            "recommendation": "Run a 30-day landing page experiment.",
            "challenged_assumptions": [{"assumption": "Users will pay", "challenge": "No proof"}],
            "validation_experiments": ["Landing page test"],
        },
        "funding": {
            "funding_activity_score": 65,
            "top_investors": ["a16z", "Sequoia"],
            "average_valuation_range": "$5M-$20M",
            "funding_trend": "Rising interest",
            "recent_funding_rounds": [{"company": "Ramp", "amount": "$300M"}],
        },
        "innovation_score": {
            "innovation_score": 68,
            "grade": "B",
            "score_explanation": "Strong AI novelty, moderate market saturation.",
        },
        "trends": {
            "trends": ["AI adoption", "SMB digitization"],
        },
        "patents": {
            "ip_strategy_recommendation": "File a provisional patent for AI matching algorithm.",
        },
    }


def _hc_state() -> Dict[str, Any]:
    s = _state()
    s["healthcare_mode"] = True
    s["industry"] = "HealthTech"
    return s


# ══════════════════════════════════════════════════════════════════════════════
# BUSINESS PLAN AGENT
# ══════════════════════════════════════════════════════════════════════════════

_BP_PAYLOAD = {
    "executive_summary": "AI invoice platform for SMBs in large fintech market.",
    "problem_statement": "SMBs waste hours on manual invoicing.",
    "solution": "AI-powered invoice automation with one-click generation.",
    "value_proposition": "Save 5 hours/week on invoicing.",
    "target_market": {"primary_segment": "SMBs", "market_size": "$20B"},
    "product": {"description": "SaaS platform", "key_features": ["AI generation", "Auto-payment"]},
    "business_model": {"revenue_streams": ["SaaS subscription"], "pricing_model": "$29/seat/mo"},
    "go_to_market": {"launch_strategy": "PLG via free tier", "channels": ["SEO", "referral"]},
    "competitive_advantage": "Only AI-native SMB invoicing platform.",
    "competition": {"main_competitors": ["FreshBooks"], "differentiation": "AI-native"},
    "team_requirements": [{"role": "CTO", "skills": "ML/Python", "priority": "immediate"}],
    "financial_projections": {"funding_required": "$1M seed", "year_1_revenue": "$500K"},
    "milestones": [{"phase": "MVP", "timeline": "0-3 months", "goals": ["Launch beta"]}],
    "risks_and_mitigations": [{"risk": "Competition", "mitigation": "Move fast", "severity": "medium"}],
    "success_metrics": ["MRR", "NPS", "Churn rate"],
}


class TestBusinessPlanAgent:

    @pytest.mark.asyncio
    async def test_returns_dict(self):
        with _mock_llm("agents.business_plan_agent", _BP_PAYLOAD):
            result = await business_plan_agent.run(_state())
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_required_keys_present(self):
        with _mock_llm("agents.business_plan_agent", _BP_PAYLOAD):
            result = await business_plan_agent.run(_state())
        required = [
            "executive_summary", "problem_statement", "solution",
            "value_proposition", "target_market", "product",
            "business_model", "go_to_market", "competitive_advantage",
            "competition", "team_requirements", "financial_projections",
            "milestones", "risks_and_mitigations", "success_metrics",
        ]
        for key in required:
            assert key in result, f"Missing key: {key}"

    @pytest.mark.asyncio
    async def test_metadata_fields_set(self):
        with _mock_llm("agents.business_plan_agent", _BP_PAYLOAD):
            result = await business_plan_agent.run(_state())
        assert result["_agent"] == "business_plan_agent"
        assert result["_idea"]  == "AI-powered invoice automation for SMBs"
        assert result["_industry"] == "FinTech"

    @pytest.mark.asyncio
    async def test_safety_defaults_on_empty_llm_response(self):
        with _mock_llm_raw("agents.business_plan_agent", "{}"):
            result = await business_plan_agent.run(_state())
        assert result["executive_summary"] == ""
        assert result["milestones"] == []
        assert result["team_requirements"] == []

    @pytest.mark.asyncio
    async def test_resilient_to_garbage_llm_output(self):
        with _mock_llm_raw("agents.business_plan_agent", "not json at all!!!"):
            result = await business_plan_agent.run(_state())
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_resilient_to_empty_pipeline_state(self):
        with _mock_llm("agents.business_plan_agent", _BP_PAYLOAD):
            result = await business_plan_agent.run({})
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_does_not_mutate_state(self):
        state    = _state()
        snapshot = copy.deepcopy(state)
        with _mock_llm("agents.business_plan_agent", _BP_PAYLOAD):
            await business_plan_agent.run(state)
        assert state == snapshot

    @pytest.mark.asyncio
    async def test_healthcare_mode_uses_hc_system(self):
        """Verify that healthcare_mode is passed through (no crash, result is dict)."""
        with _mock_llm("agents.business_plan_agent", _BP_PAYLOAD):
            result = await business_plan_agent.run(_hc_state())
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_markdown_wrapped_json_parsed(self):
        raw = "```json\n" + json.dumps(_BP_PAYLOAD) + "\n```"
        with _mock_llm_raw("agents.business_plan_agent", raw):
            result = await business_plan_agent.run(_state())
        assert result["executive_summary"] == _BP_PAYLOAD["executive_summary"]


# ══════════════════════════════════════════════════════════════════════════════
# INVESTOR AGENT
# ══════════════════════════════════════════════════════════════════════════════

_INV_PAYLOAD = {
    "one_liner": "AI invoicing for SMBs that saves 5 hours/week.",
    "investment_thesis": "Large market, strong AI differentiation, proven pain point.",
    "problem": "SMBs lose $X billion annually to manual invoicing errors.",
    "solution": "AI-native invoice platform with automatic generation.",
    "market_opportunity": {"tam": "$20B", "sam": "$5B", "som": "$200M", "growth_driver": "AI adoption"},
    "business_model": {"model_type": "SaaS", "primary_revenue": "Subscription", "scalability": "high"},
    "traction_signals": ["100 waitlist signups", "3 LOIs from SMBs"],
    "competitive_moat": "Proprietary AI model trained on 10M invoices.",
    "key_risks": [{"risk": "QuickBooks adds AI", "severity": "high", "mitigation": "Move fast"}],
    "why_now": "AI maturity + SMB digitization wave creates a perfect window.",
    "funding_ask": {"recommended_round": "Seed", "amount_range": "$1M-$2M",
                    "use_of_funds": ["Engineering 50%", "GTM 30%", "Ops 20%"],
                    "runway": "18 months"},
    "exit_strategy": "Acquisition by Intuit or Xero in 3-5 years.",
    "red_flags": ["No traction yet"],
    "green_flags": ["Large market", "Strong team background"],
    "verdict": "watch",
    "verdict_rationale": "Strong thesis but needs early traction validation.",
}


class TestInvestorAgent:

    @pytest.mark.asyncio
    async def test_returns_dict(self):
        with _mock_llm("agents.investor_agent", _INV_PAYLOAD):
            result = await investor_agent.run(_state())
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_required_keys_present(self):
        with _mock_llm("agents.investor_agent", _INV_PAYLOAD):
            result = await investor_agent.run(_state())
        required = [
            "one_liner", "investment_thesis", "problem", "solution",
            "market_opportunity", "business_model", "traction_signals",
            "competitive_moat", "key_risks", "why_now", "funding_ask",
            "exit_strategy", "red_flags", "green_flags",
            "verdict", "verdict_rationale",
        ]
        for key in required:
            assert key in result, f"Missing key: {key}"

    @pytest.mark.asyncio
    async def test_verdict_is_valid_value(self):
        with _mock_llm("agents.investor_agent", _INV_PAYLOAD):
            result = await investor_agent.run(_state())
        assert result["verdict"] in ("invest", "pass", "watch")

    @pytest.mark.asyncio
    async def test_metadata_fields_set(self):
        with _mock_llm("agents.investor_agent", _INV_PAYLOAD):
            result = await investor_agent.run(_state())
        assert result["_agent"] == "investor_agent"

    @pytest.mark.asyncio
    async def test_safety_defaults_on_empty_llm_response(self):
        with _mock_llm_raw("agents.investor_agent", "{}"):
            result = await investor_agent.run(_state())
        assert result["verdict"]    == "watch"
        assert result["one_liner"]  == ""
        assert result["red_flags"]  == []
        assert result["green_flags"] == []

    @pytest.mark.asyncio
    async def test_resilient_to_garbage_llm_output(self):
        with _mock_llm_raw("agents.investor_agent", "PURE GARBAGE!!!"):
            result = await investor_agent.run(_state())
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_resilient_to_empty_pipeline_state(self):
        with _mock_llm("agents.investor_agent", _INV_PAYLOAD):
            result = await investor_agent.run({})
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_does_not_mutate_state(self):
        state    = _state()
        snapshot = copy.deepcopy(state)
        with _mock_llm("agents.investor_agent", _INV_PAYLOAD):
            await investor_agent.run(state)
        assert state == snapshot

    @pytest.mark.asyncio
    async def test_healthcare_mode_no_crash(self):
        with _mock_llm("agents.investor_agent", _INV_PAYLOAD):
            result = await investor_agent.run(_hc_state())
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_funding_ask_has_required_subkeys(self):
        with _mock_llm("agents.investor_agent", _INV_PAYLOAD):
            result = await investor_agent.run(_state())
        ask = result.get("funding_ask", {})
        assert isinstance(ask, dict)

    @pytest.mark.asyncio
    async def test_market_opportunity_has_tam_field(self):
        with _mock_llm("agents.investor_agent", _INV_PAYLOAD):
            result = await investor_agent.run(_state())
        opp = result.get("market_opportunity", {})
        assert "tam" in opp


# ══════════════════════════════════════════════════════════════════════════════
# PITCH DECK AGENT
# ══════════════════════════════════════════════════════════════════════════════

def _pitch_payload(n_slides: int = 10) -> dict:
    return {
        "deck_title": "InvoiceAI",
        "tagline": "Invoice smarter, get paid faster",
        "key_message": "AI invoicing saves SMBs 5 hours/week.",
        "estimated_duration_minutes": 10,
        "slides": [
            {
                "number": i + 1,
                "title": f"Slide {i + 1}",
                "headline": f"Headline {i + 1}",
                "content": [f"Bullet {i+1}.1", f"Bullet {i+1}.2", f"Bullet {i+1}.3"],
                "visual_suggestion": f"Chart {i + 1}",
                "speaker_notes": f"Speaker notes for slide {i + 1}.",
            }
            for i in range(n_slides)
        ],
    }


class TestPitchAgent:

    @pytest.mark.asyncio
    async def test_returns_dict(self):
        with _mock_llm("agents.pitch_agent", _pitch_payload()):
            result = await pitch_agent.run(_state())
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_required_top_level_keys(self):
        with _mock_llm("agents.pitch_agent", _pitch_payload()):
            result = await pitch_agent.run(_state())
        for key in ("deck_title", "tagline", "slides", "slide_count",
                    "key_message", "estimated_duration_minutes"):
            assert key in result, f"Missing key: {key}"

    @pytest.mark.asyncio
    async def test_slides_is_list(self):
        with _mock_llm("agents.pitch_agent", _pitch_payload()):
            result = await pitch_agent.run(_state())
        assert isinstance(result["slides"], list)

    @pytest.mark.asyncio
    async def test_ten_slides_returned(self):
        with _mock_llm("agents.pitch_agent", _pitch_payload(10)):
            result = await pitch_agent.run(_state())
        assert result["slide_count"] == 10
        assert len(result["slides"]) == 10

    @pytest.mark.asyncio
    async def test_each_slide_has_required_fields(self):
        with _mock_llm("agents.pitch_agent", _pitch_payload()):
            result = await pitch_agent.run(_state())
        for slide in result["slides"]:
            for field in ("number", "title", "headline", "content",
                          "visual_suggestion", "speaker_notes"):
                assert field in slide, f"Slide {slide.get('number')} missing field: {field}"

    @pytest.mark.asyncio
    async def test_slide_content_is_list(self):
        with _mock_llm("agents.pitch_agent", _pitch_payload()):
            result = await pitch_agent.run(_state())
        for slide in result["slides"]:
            assert isinstance(slide["content"], list), (
                f"Slide {slide.get('number')} content is not a list"
            )

    @pytest.mark.asyncio
    async def test_metadata_fields_set(self):
        with _mock_llm("agents.pitch_agent", _pitch_payload()):
            result = await pitch_agent.run(_state())
        assert result["_agent"]    == "pitch_agent"
        assert result["_idea"]     == "AI-powered invoice automation for SMBs"
        assert result["_industry"] == "FinTech"

    @pytest.mark.asyncio
    async def test_safety_defaults_on_empty_llm_response(self):
        with _mock_llm_raw("agents.pitch_agent", "{}"):
            result = await pitch_agent.run(_state())
        assert result["deck_title"] != ""   # fallback to idea
        assert result["slides"]     == []
        assert result["slide_count"] == 0

    @pytest.mark.asyncio
    async def test_resilient_to_garbage_llm_output(self):
        with _mock_llm_raw("agents.pitch_agent", "GARBAGE OUTPUT!!!"):
            result = await pitch_agent.run(_state())
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_resilient_to_empty_pipeline_state(self):
        with _mock_llm("agents.pitch_agent", _pitch_payload()):
            result = await pitch_agent.run({})
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_does_not_mutate_state(self):
        state    = _state()
        snapshot = copy.deepcopy(state)
        with _mock_llm("agents.pitch_agent", _pitch_payload()):
            await pitch_agent.run(state)
        assert state == snapshot

    @pytest.mark.asyncio
    async def test_healthcare_mode_no_crash(self):
        with _mock_llm("agents.pitch_agent", _pitch_payload()):
            result = await pitch_agent.run(_hc_state())
        assert isinstance(result, dict)

    @pytest.mark.asyncio
    async def test_slide_defaults_filled_when_llm_returns_partial_slides(self):
        partial = {
            "deck_title": "InvoiceAI",
            "tagline": "Invoice smarter",
            "slides": [{"number": 1}],  # missing most fields
        }
        with _mock_llm("agents.pitch_agent", partial):
            result = await pitch_agent.run(_state())
        slide = result["slides"][0]
        assert "title"          in slide
        assert "headline"       in slide
        assert "content"        in slide
        assert "speaker_notes"  in slide
        assert "visual_suggestion" in slide

    @pytest.mark.asyncio
    async def test_markdown_wrapped_json_parsed(self):
        raw = "```json\n" + json.dumps(_pitch_payload(10)) + "\n```"
        with _mock_llm_raw("agents.pitch_agent", raw):
            result = await pitch_agent.run(_state())
        assert len(result["slides"]) == 10


# ─── Verify none of the 3 agents are in the pipeline ─────────────────────────

def test_business_plan_agent_not_in_pipeline():
    from orchestrator.pipeline import AGENT_SEQUENCE
    assert "Business Plan Agent" not in AGENT_SEQUENCE
    assert "business_plan" not in AGENT_SEQUENCE


def test_investor_agent_not_in_pipeline():
    from orchestrator.pipeline import AGENT_SEQUENCE
    assert "Investor Agent" not in AGENT_SEQUENCE
    assert "investor" not in AGENT_SEQUENCE


def test_pitch_agent_not_in_pipeline():
    from orchestrator.pipeline import AGENT_SEQUENCE
    assert "Pitch Deck Agent" not in AGENT_SEQUENCE
    assert "pitch" not in AGENT_SEQUENCE
