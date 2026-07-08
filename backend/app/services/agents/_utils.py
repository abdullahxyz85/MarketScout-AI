from __future__ import annotations

import json
import re

NO_THINK_INSTRUCTION = (
    "Do not show your reasoning, chain of thought, or a \"Thinking Process\" preamble. "
    "Do not wrap the answer in markdown code fences. Output ONLY the raw JSON value described "
    "below, and nothing else before or after it."
)


def _last_top_level_span(text: str) -> tuple[int, int] | None:
    """Bracket-match to find the start index of the span whose closing bracket is the
    last one in the text — i.e. the outermost bracket enclosing the final JSON value."""
    stack: list[int] = []
    last_match: tuple[int, int] | None = None
    for i, ch in enumerate(text):
        if ch in "{[":
            stack.append(i)
        elif ch in "}]":
            if stack:
                start = stack.pop()
                last_match = (start, i)
    return last_match


def parse_json_response(text: str | None) -> dict | list:
    if not text or not text.strip():
        raise ValueError(
            "LLM returned an empty response (likely truncated before producing any output — "
            "try increasing max_tokens or lowering reasoning effort)."
        )

    # Reasoning models often wrap or precede their answer with a <think>...</think>
    # block or a "Thinking Process:" preamble — drop it before looking for JSON.
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)

    # gpt-oss "harmony" models can leak their raw channel-formatted transcript
    # (e.g. "<|channel|>analysis<|message|>...<|end|>") instead of clean content.
    # Keep only the final-channel message if present, otherwise strip the analysis
    # channel and any leftover control tokens.
    final_match = re.search(r"<\|channel\|>final<\|message\|>(.*?)(?:<\|.*?\|>|$)", cleaned, re.DOTALL)
    if final_match:
        cleaned = final_match.group(1)
    else:
        cleaned = re.sub(r"<\|channel\|>analysis<\|message\|>.*?(?=<\|channel\|>|$)", "", cleaned, flags=re.DOTALL)
        cleaned = re.sub(r"<\|[^|]*\|>", "", cleaned)

    cleaned = re.sub(r"^```(?:json)?|```$", "", cleaned.strip(), flags=re.MULTILINE).strip()

    decoder = json.JSONDecoder()

    # Reasoning preambles can contain decoy braces/brackets (code snippets, examples).
    # The real answer is almost always the LAST complete top-level JSON value in the
    # text, so bracket-match from the final closing bracket first.
    span = _last_top_level_span(cleaned)
    if span is not None:
        start, _ = span
        try:
            obj, _ = decoder.raw_decode(cleaned, start)
            return obj
        except json.JSONDecodeError:
            pass

    candidates = [i for i, ch in enumerate(cleaned) if ch in "{["]
    if not candidates:
        raise ValueError(f"No JSON object found in LLM response: {text[:200]}")

    # Fallback: try every candidate start position, keeping the LAST one that parses
    # successfully (favoring content later in the response over early decoys).
    result = None
    last_error: json.JSONDecodeError | None = None
    for start in candidates:
        try:
            obj, _ = decoder.raw_decode(cleaned, start)
            result = obj
        except json.JSONDecodeError as exc:
            last_error = exc
            continue

    if result is not None:
        return result
    raise ValueError(f"Could not parse JSON from LLM response: {text[:200]}") from last_error


def parse_json_object(text: str | None, defaults: dict) -> dict:
    """Like parse_json_response, but guarantees a dict with exactly `defaults`' keys —
    the model can return a list or a differently-shaped object, and callers should never
    have to guard against that downstream (e.g. `.get()` on a list). Genuine parse failures
    (empty response, no JSON found at all) still raise, since those indicate a real LLM
    error worth surfacing rather than silently producing an empty report."""
    result = parse_json_response(text)
    if not isinstance(result, dict):
        result = {}
    return {key: result.get(key, default) for key, default in defaults.items()}
