from __future__ import annotations

from app.schemas.LLMmodels import LLMModels
from app.services.agents._utils import NO_THINK_INSTRUCTION, parse_json_object
from app.services.agents.agentic import CRITICAL_STANCE, gather_research_context
from app.services.fireworks_client import call_llm

MODEL = LLMModels.MINIMAX_M3

SYSTEM_PROMPT = (
    "You are a strategy consultant. "
    f"{CRITICAL_STANCE} "
    "Ground the SWOT in real market conditions found in the research (competitor moves, "
    "regulation, tech shifts). Weaknesses and threats should be as specific and unflinching "
    "as strengths and opportunities — do not pad the list with token weaknesses to balance "
    "an otherwise glowing analysis. Respond with ONLY a JSON object: "
    '{"strengths": ["..."], "weaknesses": ["..."], "opportunities": ["..."], "threats": ["..."]} '
    "with 3-5 specific, non-generic bullet points in each list.\n\n"
    f"{NO_THINK_INSTRUCTION}"
)


async def run_swot_agent(idea: str, industry: str | None) -> dict:
    context = await gather_research_context(
        idea, industry, "competitor weaknesses, regulatory hurdles, and market challenges"
    )
    prompt = (
        f"Startup idea: {idea}\nIndustry: {industry or 'unspecified'}\n\n"
        f"Web research findings:\n{context}\n\n"
        "Produce the SWOT JSON object described."
    )
    text = await call_llm(prompt, system_prompt=SYSTEM_PROMPT, model=MODEL, max_tokens=2000)
    return parse_json_object(
        text, {"strengths": [], "weaknesses": [], "opportunities": [], "threats": []}
    )
