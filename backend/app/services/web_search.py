from __future__ import annotations

import html
import logging
import re

import httpx

logger = logging.getLogger(__name__)

_TITLE_RE = re.compile(r'class="result__a"[^>]*>(.*?)</a>', re.DOTALL)
_SNIPPET_RE = re.compile(r'class="result__snippet"[^>]*>(.*?)</a>', re.DOTALL)
_TAG_RE = re.compile(r"<[^>]+>")


def _clean(fragment: str) -> str:
    return html.unescape(_TAG_RE.sub("", fragment)).strip()


async def web_search(query: str, max_results: int = 5) -> list[dict]:
    """Best-effort live web search via DuckDuckGo's HTML endpoint (no API key required)."""
    try:
        async with httpx.AsyncClient(
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0 (compatible; MarketScoutAI/1.0)"},
        ) as client:
            response = await client.get("https://html.duckduckgo.com/html/", params={"q": query})
            response.raise_for_status()
    except Exception:
        logger.warning("Web search failed for query %r", query, exc_info=True)
        return []

    titles = _TITLE_RE.findall(response.text)
    snippets = _SNIPPET_RE.findall(response.text)

    results = []
    for title, snippet in zip(titles, snippets):
        cleaned_title = _clean(title)
        cleaned_snippet = _clean(snippet)
        if not cleaned_title:
            continue
        results.append({"title": cleaned_title, "snippet": cleaned_snippet})
        if len(results) >= max_results:
            break
    return results


async def search_context(query: str, max_results: int = 5) -> str:
    """Fetch web search results and format them as grounding context for an LLM prompt."""
    results = await web_search(query, max_results)
    if not results:
        return "No live web results were available for this query."
    return "\n".join(f"- {r['title']}: {r['snippet']}" for r in results if r["snippet"])
