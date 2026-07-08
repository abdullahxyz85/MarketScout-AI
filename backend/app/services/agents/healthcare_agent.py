from __future__ import annotations

from app.schemas.LLMmodels import LLMModels
from app.services.agents._utils import NO_THINK_INSTRUCTION, parse_json_object
from app.services.agents.agentic import CRITICAL_STANCE, gather_research_context
from app.services.fireworks_client import call_llm

MODEL = LLMModels.DeepSeek_V4_Pro

SYSTEM_PROMPT = (
    "You are a healthcare market analyst. "
    f"{CRITICAL_STANCE} "
    "Ground regulatory (FDA/HIPAA/CE-mark), clinical, and reimbursement analysis in real "
    "signals from the research when available. Healthcare regulatory pathways are typically "
    "slow and costly — do not default to high readiness scores unless the evidence supports "
    "it. Respond with ONLY a JSON object: {\"regulatory_readiness\": 0-100 number, "
    '"clinical_demand": 0-100 number, "provider_adoption": "+X%", "readiness": '
    '[{"metric": "Clinical Need", "score": 0-100}, ...] with 5-6 entries covering clinical '
    "need, regulatory fit, provider adoption, reimbursement, data security, pilot "
    'feasibility, "watchlist": [{"name": "...", "focus": "...", "stage": "...", '
    '"threat": "Low|Medium|High"}] with 3 real or realistic healthcare competitors}\n\n'
    f"{NO_THINK_INSTRUCTION}"
)


async def run_healthcare_agent(idea: str) -> dict:
    context = await gather_research_context(
        idea, None, "FDA/HIPAA regulatory requirements and clinical adoption barriers"
    )
    prompt = (
        f"Startup idea: {idea}\n\n"
        f"Web research findings:\n{context}\n\n"
        "Produce the healthcare-specific JSON object described."
    )
    text = await call_llm(prompt, system_prompt=SYSTEM_PROMPT, model=MODEL, max_tokens=2000)
    return parse_json_object(
        text,
        {
            "regulatory_readiness": 0,
            "clinical_demand": 0,
            "provider_adoption": "+0%",
            "readiness": [],
            "watchlist": [],
        },
    )
