from __future__ import annotations

import json
import re
from typing import Any, Dict, List


def parse_json_response(text: str) -> Dict[str, Any]:
    """Parse a JSON response from an LLM, handling markdown code blocks, extra text,
    and truncated responses caused by max_tokens limits."""
    if not text:
        return {"parse_error": True, "raw_response": ""}

    cleaned = text.strip()

    # 1. Direct parse
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # 2. Extract from markdown code block
    match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", cleaned, re.DOTALL)
    if match:
        try:
            return json.loads(match.group(1))
        except json.JSONDecodeError:
            pass

    # 3. Extract largest {…} block
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        candidate = match.group(0)
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            # 4. Try to repair truncated JSON (LLM cut off by max_tokens)
            repaired = _repair_truncated_json(candidate)
            if repaired is not None:
                return repaired

    return {"raw_response": text, "parse_error": True}


def _repair_truncated_json(text: str) -> Dict[str, Any] | None:
    """Close open strings, arrays, and objects to recover a truncated JSON response."""
    depth_curly = 0
    depth_square = 0
    in_string = False
    escape_next = False

    for ch in text:
        if escape_next:
            escape_next = False
            continue
        if ch == "\\" and in_string:
            escape_next = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if not in_string:
            if ch == "{":
                depth_curly += 1
            elif ch == "}":
                depth_curly -= 1
            elif ch == "[":
                depth_square += 1
            elif ch == "]":
                depth_square -= 1

    # Build the closing suffix
    closing = ""
    if in_string:
        closing += '"'
    closing += "]" * max(0, depth_square)
    closing += "}" * max(0, depth_curly)

    if closing:
        try:
            return json.loads(text + closing)
        except json.JSONDecodeError:
            pass
    return None


def truncate_for_search(text: str, max_length: int = 200) -> str:
    """Truncate free-form text before folding it into a Tavily query (400-char query limit)."""
    return text[:max_length].rsplit(" ", 1)[0] if len(text) > max_length else text


def truncate_sources(results: List[Dict[str, Any]], max_content: int = 500) -> List[Dict[str, Any]]:
    """Truncate web search result content to avoid excessive token usage."""
    return [
        {
            "url": r.get("url", ""),
            "title": r.get("title", ""),
            "content": r.get("content", "")[:max_content],
        }
        for r in results
    ]


def format_sources_for_prompt(results: List[Dict[str, Any]]) -> str:
    """Format web search results as a readable string for LLM prompts."""
    parts = []
    for i, r in enumerate(results, 1):
        parts.append(
            f"[{i}] {r.get('title', 'No title')}\n"
            f"URL: {r.get('url', '')}\n"
            f"{r.get('content', '')[:400]}"
        )
    return "\n\n".join(parts) if parts else "No web data available."


def extract_source_urls(results: List[Dict[str, Any]], limit: int = 5) -> List[str]:
    """Extract URLs from search results."""
    return [r.get("url", "") for r in results[:limit] if r.get("url")]


# ─── Anti-hallucination prompt suffix ────────────────────────────────────────
# Append to the user prompt of every web-search agent to enforce grounded output.
ANTI_HALLUCINATION_SUFFIX = """
CRITICAL EVIDENCE RULES — you MUST follow these exactly:
1. Use ONLY information explicitly found in the numbered sources [1], [2], … above.
2. Do NOT invent company names, funding amounts, market sizes, paper titles, patent numbers, or regulatory facts.
3. When a field has no supporting evidence in the sources, set its value to null (not a made-up estimate).
4. For every quantitative claim (market size, growth rate, revenue, funding amount) set "evidence_quality" accordingly:
   - "high"   → the exact figure appears verbatim in a source
   - "medium" → the figure was calculated or derived from source data
   - "low"    → the figure is an inference with weak source support
   - "insufficient_evidence" → no relevant source mentions it at all
5. "unsupported_claims" must list the JSON keys whose values you could NOT find in the sources.
6. Do NOT use general model knowledge that contradicts or supplements what is in the sources.
"""
