"""
In-memory sliding-window rate limiter.

Keys are arbitrary strings (typically ``f"{user_id}:{route}"``) so limits are
enforced per-user per-route independently of each other.

All operations are protected by an asyncio.Lock so the limiter is safe to use
from concurrent FastAPI request handlers without data races.
"""
from __future__ import annotations

import asyncio
import logging
from collections import defaultdict, deque
from time import monotonic
from typing import Deque, Dict

from fastapi import HTTPException, status

logger = logging.getLogger("agent-service.rate_limiter")


class _SlidingWindow:
    __slots__ = ("_windows", "_lock")

    def __init__(self) -> None:
        self._windows: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock: asyncio.Lock = asyncio.Lock()

    async def check(self, key: str, limit: int, window_seconds: int) -> None:
        """
        Allow the request if the caller has made fewer than *limit* requests
        in the last *window_seconds* seconds. Raise ``HTTP 429`` otherwise.
        """
        async with self._lock:
            now = monotonic()
            q = self._windows[key]
            cutoff = now - window_seconds
            # Evict timestamps outside the window
            while q and q[0] < cutoff:
                q.popleft()
            if len(q) >= limit:
                logger.warning("rate_limit exceeded key=%r limit=%d window=%ds", key, limit, window_seconds)
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail=(
                        f"Rate limit exceeded: maximum {limit} requests "
                        f"per {window_seconds // 60} minute(s). Please wait before retrying."
                    ),
                    headers={"Retry-After": str(window_seconds)},
                )
            q.append(now)

    def reset(self) -> None:
        """Clear all rate-limit windows. Used in tests to avoid cross-test contamination."""
        self._windows.clear()


# Module-level singleton shared across all requests
limiter = _SlidingWindow()


# ── Convenience helpers ────────────────────────────────────────────────────────

async def check_research_start(user_id: str) -> None:
    """5 research jobs per hour per user."""
    await limiter.check(f"{user_id}:research_start", limit=5, window_seconds=3600)


async def check_scenario(user_id: str) -> None:
    """10 scenario simulations per hour per user."""
    await limiter.check(f"{user_id}:scenario", limit=10, window_seconds=3600)


async def check_ask(user_id: str) -> None:
    """30 Q&A questions per hour per user."""
    await limiter.check(f"{user_id}:ask", limit=30, window_seconds=3600)


async def check_pdf(user_id: str) -> None:
    """20 PDF downloads per hour per user."""
    await limiter.check(f"{user_id}:pdf", limit=20, window_seconds=3600)


async def check_llm_doc(user_id: str, doc_type: str) -> None:
    """10 LLM-generated documents (business plan / memo / pitch) per hour per user."""
    await limiter.check(f"{user_id}:llm_doc:{doc_type}", limit=10, window_seconds=3600)
