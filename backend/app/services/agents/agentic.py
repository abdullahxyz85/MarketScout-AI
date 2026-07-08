from __future__ import annotations

import asyncio
import logging

from app.schemas.LLMmodels import LLMModels
from app.services.agents._utils import NO_THINK_INSTRUCTION, parse_json_response
from app.services.fireworks_client import call_llm
from app.services.web_search import search_context

logger = logging.getLogger(__name__)

# A small, fast model is enough for query planning — the heavy lifting happens in the
# agent's own synthesis call with its dedicated model. Avoid the gpt-oss family here:
# it emits an internal "harmony" reasoning-channel format that can leak into content.
QUERY_PLANNER_MODEL = LLMModels.DeepSeek_V4_Flash

CRITICAL_STANCE = (
    "You are a skeptical, independent analyst, not a hype machine or a pitch-deck writer. "
    "Never flatter the founder or the idea. Do not describe it as \"exciting\", \"innovative\", "
    "\"game-changing\", \"disruptive\", \"well-positioned\", or similar promotional language "
    "unless you are directly quoting a named source. Do not tell the user their idea is great, "
    "unique, or destined to win — most startup ideas are not. If the web evidence suggests the "
    "market is crowded, the idea is derivative, competitors already dominate, or the odds are "
    "weak, say that plainly and without hedging. Write like a due-diligence memo for an "
    "investor who is inclined to pass, not a cheerleader. Numbers and claims should be "
    "defensible from the provided context or clearly flagged as an estimate — never invent "
    "specific statistics to sound authoritative."
)


async def plan_search_queries(idea: str, industry: str | None, focus: str, max_queries: int = 3) -> list[str]:
    """Let the model plan its own research queries instead of using one fixed template —
    this is the 'planning' step of the agent's search loop."""
    prompt = (
        f"Startup idea: {idea}\nIndustry: {industry or 'unspecified'}\n"
        f"Research focus: {focus}\n\n"
        f"Propose {max_queries} web search queries (each under 8 words, like something typed "
        "into a search engine, not a sentence) that would surface real, current evidence about "
        "this idea's market — including evidence that could disconfirm or complicate an "
        "optimistic read (existing competitors, past failures, regulatory friction), not only "
        f"supportive evidence. Respond with ONLY a JSON array of exactly {max_queries} short "
        "query strings, nothing else."
    )
    try:
        text = await call_llm(
            prompt,
            system_prompt=f"You are a research query planner. {NO_THINK_INSTRUCTION}",
            model=QUERY_PLANNER_MODEL,
            max_tokens=1000,
        )
        queries = parse_json_response(text)
        if isinstance(queries, list) and queries:
            return [str(q) for q in queries[:max_queries] if str(q).strip()]
    except Exception:
        logger.warning("Query planning failed for idea=%r focus=%r", idea, focus, exc_info=True)
    return [f"{idea} {industry or ''} {focus}".strip()]


async def gather_research_context(idea: str, industry: str | None, focus: str, max_queries: int = 3) -> str:
    """Agentic research loop: plan queries -> run them concurrently -> return combined
    findings as grounding context for the synthesis call."""
    queries = await plan_search_queries(idea, industry, focus, max_queries)
    results = await asyncio.gather(*(search_context(q) for q in queries))
    blocks = [f"Search query: {q}\nFindings:\n{r}" for q, r in zip(queries, results)]
    return "\n\n".join(blocks) if blocks else "No live web results were available."
