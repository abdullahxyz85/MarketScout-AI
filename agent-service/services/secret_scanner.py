"""
Output secret scanner.

Scans LLM-generated text for patterns that look like leaked credentials or
private keys before the output is returned to the caller or persisted.

Design goals:
- Low false-positive rate (patterns are specific to known secret formats).
- Block on detection — never return or store a matched output.
- Log only the detection event (not the matched secret itself).
"""
from __future__ import annotations

import logging
import re
from typing import Sequence

logger = logging.getLogger("agent-service.secret_scanner")

# Each tuple: (name, compiled pattern)
_PATTERNS: Sequence[tuple[str, re.Pattern[str]]] = [
    ("fireworks_key",      re.compile(r'fw_[A-Za-z0-9]{20,}')),
    ("openai_key",         re.compile(r'sk-[A-Za-z0-9]{20,}')),
    ("bearer_token",       re.compile(r'Bearer\s+[A-Za-z0-9\-._~+/]{20,}')),
    ("jwt_token",          re.compile(r'eyJ[A-Za-z0-9+/]{30,}\.eyJ')),
    ("private_key_pem",    re.compile(r'-----BEGIN (?:PRIVATE|RSA|EC) KEY-----')),
    ("supabase_service",   re.compile(r'SUPABASE_SERVICE(?:_KEY)?\s*[=:]\s*\S{20,}', re.I)),
    ("fireworks_env",      re.compile(r'FIREWORKS_API_KEY\s*[=:]\s*\S{10,}', re.I)),
    ("tavily_env",         re.compile(r'TAVILY_API_KEY\s*[=:]\s*\S{10,}', re.I)),
    ("google_secret",      re.compile(r'GOOGLE_CLIENT_SECRET\s*[=:]\s*\S{10,}', re.I)),
    ("github_secret",      re.compile(r'GITHUB_CLIENT_SECRET\s*[=:]\s*\S{10,}', re.I)),
    ("aws_key",            re.compile(r'AKIA[0-9A-Z]{16}')),
]


def scan(text: str) -> str | None:
    """
    Return the *name* of the first matching secret pattern, or ``None`` if clean.

    The caller must never log or return the matching text itself.
    """
    if not text:
        return None
    for name, pattern in _PATTERNS:
        if pattern.search(text):
            return name
    return None


def assert_clean(text: str, context: str = "") -> None:
    """
    Raise ``ValueError`` if a secret pattern is detected in *text*.

    Parameters
    ----------
    text:
        The LLM output string to scan.
    context:
        A safe label (e.g. ``"business_plan_agent"``) included in the log
        entry but **never** the matched text.
    """
    match = scan(text)
    if match is not None:
        logger.error(
            "secret_scanner: potential secret detected pattern=%r context=%r — output blocked",
            match, context,
        )
        raise ValueError(f"Output blocked: potential secret detected ({match}).")
