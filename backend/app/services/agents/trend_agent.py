from __future__ import annotations

from app.schemas.LLMmodels import LLMModels
from app.services.agents._utils import NO_THINK_INSTRUCTION, parse_json_response
from app.services.agents.agentic import CRITICAL_STANCE, gather_research_context
from app.services.fireworks_client import call_llm

MODEL = LLMModels.DeepSeek_V4_Flash

SYSTEM_PROMPT = (
    "You are a market trend analyst. "
    f"{CRITICAL_STANCE} "
    "Use the research (recent news, funding activity, adoption signals) to project a "
    "realistic 6-month trajectory — reflect volatility, slowdowns, or setbacks the evidence "
    "suggests instead of defaulting to a smooth upward line. A flat or declining trend is a "
    "valid and expected outcome if that's what the evidence shows. Respond with ONLY a JSON "
    'array: [{"month": "Jan", "score": 0-100, "opportunity": 0-100, "risk": 0-100}, ...] '
    "with exactly 6 entries ending near the present month.\n\n"
    f"{NO_THINK_INSTRUCTION}"
)


async def run_trend_agent(idea: str, industry: str | None) -> list[dict]:
    context = await gather_research_context(
        idea, industry, "recent news, funding momentum, and adoption or slowdown signals"
    )
    prompt = (
        f"Startup idea: {idea}\nIndustry: {industry or 'unspecified'}\n\n"
        f"Web research findings:\n{context}\n\n"
        "Produce the 6-month trend JSON array described."
    )
    text = await call_llm(prompt, system_prompt=SYSTEM_PROMPT, model=MODEL, max_tokens=1800)
    result = parse_json_response(text)
    return result if isinstance(result, list) else result.get("trend", [])
