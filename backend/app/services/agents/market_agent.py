from __future__ import annotations

from app.schemas.LLMmodels import LLMModels
from app.services.agents._utils import NO_THINK_INSTRUCTION, parse_json_object
from app.services.agents.agentic import CRITICAL_STANCE, gather_research_context
from app.services.fireworks_client import call_llm

MODEL = LLMModels.DeepSeek_V4_Pro

SYSTEM_PROMPT = (
    "You are a market sizing analyst. "
    f"{CRITICAL_STANCE} "
    "Anchor TAM/funding estimates in real figures (funding rounds, market reports, industry "
    "statistics) found in the research whenever available; otherwise give a conservative, "
    "well-reasoned estimate rather than an inflated one. Respond with ONLY a JSON object: "
    '{"tam": "$XXB", "market_score": 0-100 number, "funding_by_sector": [{"sector": "...", '
    '"funding": number in millions, "growth": number percent}]} with 4-5 sectors related to '
    "the idea's industry and adjacent verticals.\n\n"
    f"{NO_THINK_INSTRUCTION}"
)


async def run_market_agent(idea: str, industry: str | None) -> dict:
    context = await gather_research_context(
        idea, industry, "market sizing, funding rounds, and growth statistics"
    )
    prompt = (
        f"Startup idea: {idea}\nIndustry: {industry or 'unspecified'}\n\n"
        f"Web research findings:\n{context}\n\n"
        "Size the market and respond with the JSON object described."
    )
    text = await call_llm(prompt, system_prompt=SYSTEM_PROMPT, model=MODEL, max_tokens=2000)
    return parse_json_object(text, {"tam": "N/A", "market_score": 0, "funding_by_sector": []})
