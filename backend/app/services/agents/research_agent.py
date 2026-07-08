from __future__ import annotations

from app.schemas.LLMmodels import LLMModels
from app.services.agents._utils import NO_THINK_INSTRUCTION, parse_json_object
from app.services.agents.agentic import CRITICAL_STANCE, gather_research_context
from app.services.fireworks_client import call_llm

MODEL = LLMModels.DeepSeek_V4_Pro

SYSTEM_PROMPT = (
    "You are a senior market research analyst. "
    f"{CRITICAL_STANCE} "
    "Use the provided web research to ground your analysis in real, current information — "
    "cite concrete facts, numbers, and company/market names from it when relevant. If the "
    "evidence is thin or the idea looks like a crowded/derivative space, say so directly. "
    'Respond with ONLY a JSON object: {"title": "short, neutral report title (no hype words)", '
    '"description": "3-4 sentence market summary grounded in the research, stating weaknesses '
    'or crowding plainly if that is what the evidence shows", '
    '"tam": "total addressable market estimate, e.g. $12B"}\n\n'
    f"{NO_THINK_INSTRUCTION}"
)


async def run_research_agent(idea: str, industry: str | None, healthcare_mode: bool) -> dict:
    context = await gather_research_context(
        idea, industry, "overall market size, existing players, and recent trends"
    )
    prompt = (
        f"Startup idea: {idea}\n"
        f"Industry: {industry or 'unspecified'}\n"
        f"Healthcare mode: {healthcare_mode}\n\n"
        f"Web research findings:\n{context}\n\n"
        "Analyze the market opportunity and respond with the JSON object described."
    )
    text = await call_llm(prompt, system_prompt=SYSTEM_PROMPT, model=MODEL, max_tokens=2000)
    return parse_json_object(text, {"title": idea[:60], "description": "", "tam": "N/A"})
