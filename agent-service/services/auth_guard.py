"""
JWT authentication guard for the agent-service.

Validates the same ``access_token`` httpOnly cookie that the backend issues.
Both services share the same ``JWT_SECRET`` so no extra token exchange is needed.

Behaviour controlled by ``AGENT_AUTH_ENABLED`` (default: False):
  - False  → dev/demo bypass: all requests are accepted as ``"dev_anonymous"``.
             This preserves the existing behaviour while the frontend may not yet
             always carry a valid session cookie (e.g. DEMO_MODE layout bypass).
  - True   → strict mode: missing / expired / invalid tokens are rejected 401.
             Enable this in production via the .env file.
"""
from __future__ import annotations

import logging

import jwt
from fastapi import HTTPException, Request, status

from config import settings

logger = logging.getLogger("agent-service.auth")

_DEV_USER = "dev_anonymous"


async def require_auth(request: Request) -> str:
    """
    FastAPI dependency — returns the authenticated ``user_id`` (JWT ``sub`` claim).

    * When ``AGENT_AUTH_ENABLED=false``: returns ``"dev_anonymous"`` without
      any token validation (development / demo mode).
    * When ``AGENT_AUTH_ENABLED=true``: reads the ``access_token`` cookie,
      validates signature + expiry with ``JWT_SECRET``, returns ``sub``.
      Raises ``HTTP 401`` on any failure.

    Usage::

        @router.post("/research/start")
        async def start(req: ResearchRequest, user_id: str = Depends(require_auth)):
            ...
    """
    if not settings.AGENT_AUTH_ENABLED:
        # Development / demo mode — bypass auth entirely.
        return _DEV_USER

    # ── Strict mode ────────────────────────────────────────────────────────────
    token: str | None = request.cookies.get("access_token")

    if not token:
        logger.warning("auth: missing access_token cookie from %s", request.client)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated — missing access_token cookie.",
        )

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        logger.warning("auth: expired token from %s", request.client)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired. Please log in again.",
        )
    except jwt.InvalidTokenError as exc:
        logger.warning("auth: invalid token from %s — %s", request.client, exc)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token.",
        )

    user_id: str | None = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing subject.",
        )

    return user_id
