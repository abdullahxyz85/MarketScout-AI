from __future__ import annotations

from app.schemas.LLMmodels import LLMModels
from app.services.agents._utils import NO_THINK_INSTRUCTION, parse_json_object
from app.services.agents.agentic import CRITICAL_STANCE, gather_research_context
from app.services.fireworks_client import call_llm

MODEL = LLMModels.Qwen_V37_PLUS

SYSTEM_PROMPT = (
    "You are an opportunity analyst. "
    f"{CRITICAL_STANCE} "
    "Use the research to spot concrete, underserved gaps (whitespace competitors are "
    "missing, emerging customer segments, unmet regulatory/tech shifts) rather than vague "
    "optimism. If the research shows the gap is already being filled by an incumbent or a "
    "well-funded competitor, say that instead of inventing an opportunity, and score "
    "accordingly. A low opportunity_score is a valid outcome. Respond with ONLY a JSON "
    'object: {"opportunity_score": 0-100 number, "highlights": ["...", "..."]} with 3-4 '
    "specific, evidence-based highlights.\n\n"
    f"{NO_THINK_INSTRUCTION}"
)


async def run_opportunity_agent(idea: str, industry: str | None) -> dict:
    context = await gather_research_context(
        idea, industry, "unmet needs and whether existing players already cover them"
    )
    prompt = (
        f"Startup idea: {idea}\nIndustry: {industry or 'unspecified'}\n\n"
        f"Web research findings:\n{context}\n\n"
        "Produce the opportunity JSON object described."
    )
    text = await call_llm(prompt, system_prompt=SYSTEM_PROMPT, model=MODEL, max_tokens=1800)
    return parse_json_object(text, {"opportunity_score": 0, "highlights": []})
