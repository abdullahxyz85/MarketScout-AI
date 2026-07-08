from __future__ import annotations

from app.schemas.LLMmodels import LLMModels
from app.services.agents._utils import NO_THINK_INSTRUCTION, parse_json_object
from app.services.agents.agentic import CRITICAL_STANCE, gather_research_context
from app.services.fireworks_client import call_llm

MODEL = LLMModels.DeepSeek_V4_Flash

SYSTEM_PROMPT = (
    "You are a risk analyst. "
    f"{CRITICAL_STANCE} "
    "Use the research to identify real regulatory, competitive, market, and execution risks "
    "(recent lawsuits, compliance changes, funding downturns, incumbent responses, past "
    "failures of similar startups) rather than boilerplate risks. Do not soften a risk to make "
    "the idea look safer than the evidence supports — if the space looks genuinely risky, set "
    "risk_level to High. Respond with ONLY a JSON object: {\"risk_level\": \"Low|Medium|High\", "
    '"risk_score": 0-100 number, "risks": ["...", "..."]} with 3-4 specific key risks.\n\n'
    f"{NO_THINK_INSTRUCTION}"
)


async def run_risk_agent(idea: str, industry: str | None) -> dict:
    context = await gather_research_context(
        idea, industry, "regulatory risk, lawsuits, and past failures in this space"
    )
    prompt = (
        f"Startup idea: {idea}\nIndustry: {industry or 'unspecified'}\n\n"
        f"Web research findings:\n{context}\n\n"
        "Produce the risk JSON object described."
    )
    text = await call_llm(prompt, system_prompt=SYSTEM_PROMPT, model=MODEL, max_tokens=1800)
    return parse_json_object(text, {"risk_level": "Medium", "risk_score": 0, "risks": []})
