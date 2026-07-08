from __future__ import annotations

from app.schemas.LLMmodels import LLMModels
from app.services.agents._utils import NO_THINK_INSTRUCTION, parse_json_response
from app.services.agents.agentic import CRITICAL_STANCE, gather_research_context
from app.services.fireworks_client import call_llm

MODEL = LLMModels.Qwen_V37_PLUS

SYSTEM_PROMPT = (
    "You are a competitive intelligence analyst. "
    f"{CRITICAL_STANCE} "
    "Prefer real, identifiable companies found in the web research over invented ones — use "
    "the findings to name actual competitors, their positioning, and rough scale. Do not "
    "understate a competitor's strength to make the idea look more open; if the space is "
    "already dominated by a few large players, reflect that with high market_share/threat "
    "values. Only fall back to plausible archetypal competitors if the research has no "
    "relevant names. Identify 4-6 competitors. Respond with ONLY a JSON array of objects: "
    '[{"name": "...", "segment": "...", "market_share": 0-100 number, '
    '"threat": "low|medium|high", "trend": "up|down|stable", "revenue": "$XXM"}]\n\n'
    f"{NO_THINK_INSTRUCTION}"
)


async def run_competitor_agent(idea: str, industry: str | None) -> list[dict]:
    context = await gather_research_context(
        idea, industry, "named real competitors, their market position, and market share"
    )
    prompt = (
        f"Startup idea: {idea}\nIndustry: {industry or 'unspecified'}\n\n"
        f"Web research findings:\n{context}\n\n"
        "List the top competitors as the JSON array described."
    )
    text = await call_llm(prompt, system_prompt=SYSTEM_PROMPT, model=MODEL, max_tokens=2500)
    result = parse_json_response(text)
    return result if isinstance(result, list) else result.get("competitors", [])
