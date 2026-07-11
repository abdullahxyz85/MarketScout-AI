from __future__ import annotations

import asyncio
from typing import Any, Dict, List

from config import settings


def _is_mock() -> bool:
    return not bool(settings.TAVILY_API_KEY)


def _mock_results(query: str, max_results: int) -> List[Dict[str, Any]]:
    """Synthetic results when TAVILY_API_KEY is not set. Set the key in .env to enable live search."""
    templates = [
        ("Market analysis indicates strong growth potential. The sector attracts significant VC investment. "
         "Key drivers include AI adoption, increasing demand, and regulatory tailwinds."),
        ("Industry research shows major incumbents investing heavily. Startups differentiating through "
         "superior UX and niche targeting are gaining traction. TAM is in billions with CAGR above 15%."),
        ("Competitive landscape: Several Series A/B companies raised funds recently. "
         "Investors focus on unit economics and network effects. Clear opportunities for differentiation."),
    ]
    return [{"url": f"https://mock-research.example.com/report-{i+1}", "title": f"Report: {query[:50]}", "content": templates[i % 3]} for i in range(min(max_results, 3))]


async def search(query: str, max_results: int = 5, search_depth: str = "basic", include_domains=None) -> List[Dict[str, Any]]:
    """Execute web search via Tavily. Falls back to mock data when TAVILY_API_KEY is not configured."""
    if _is_mock():
        return _mock_results(query, max_results)
    from tavily import TavilyClient
    client = TavilyClient(api_key=settings.TAVILY_API_KEY)
    kwargs: Dict[str, Any] = {"query": query, "max_results": max_results, "search_depth": search_depth}
    if include_domains:
        kwargs["include_domains"] = include_domains
    response = await asyncio.to_thread(client.search, **kwargs)
    return response.get("results", [])


async def search_news(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    return await search(query=query, max_results=max_results, search_depth="basic")


async def search_advanced(query: str, max_results: int = 5) -> List[Dict[str, Any]]:
    return await search(query=query, max_results=max_results, search_depth="advanced")
