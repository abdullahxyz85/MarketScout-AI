"""
Hallucination Checker
=====================
Checks whether a textual claim is supported by web source content.

For each claim it returns a CheckResult:

    status          – "Supported" | "Weak" | "Unknown"
    score           – float 0.0–1.0  (overlap strength)
    matched_sources – list of 0-based source indices that support the claim
    reason          – human-readable explanation

Rules
-----
- Read-only: sources and claims are never modified.
- No LLM calls: purely deterministic keyword-overlap logic.
- Works on any string claim + any list of source dicts or raw strings.
- Graceful on empty / None inputs.

Thresholds
----------
    score >= 0.60  →  "Supported"   (strong keyword evidence in ≥1 source)
    score >= 0.25  →  "Weak"        (partial evidence, may be hallucinated)
    score <  0.25  →  "Unknown"     (no meaningful overlap found)

Usage
-----
    from services.hallucination_checker import check, check_claims, extract_claims

    # Single claim vs sources
    result = check("Market size is $45B", sources)
    print(result.status)          # "Supported"
    print(result.score)           # 0.73
    print(result.matched_sources) # [0, 2]
    print(result.reason)          # "3 keyword(s) matched in 2 source(s)."

    # Batch
    results = check_claims(["claim A", "claim B"], sources)

    # Extract checkable string claims from an agent output dict
    claims = extract_claims(agent_output, max_claims=10)
    results = check_claims(claims, sources)
"""
from __future__ import annotations

import re
import string
from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Sequence, Union


# ─── Result type ──────────────────────────────────────────────────────────────

SupportStatus = Literal["Supported", "Weak", "Unknown"]

SUPPORTED = "Supported"
WEAK      = "Weak"
UNKNOWN   = "Unknown"

_THRESHOLD_SUPPORTED = 0.60
_THRESHOLD_WEAK      = 0.25


@dataclass(frozen=True)
class CheckResult:
    status: SupportStatus
    score: float                     # 0.0 – 1.0
    matched_sources: List[int]       # 0-based indices of supporting sources
    reason: str


# ─── Stop-words ───────────────────────────────────────────────────────────────

_STOP_WORDS = frozenset({
    "a", "an", "the", "is", "are", "was", "were", "be", "been", "being",
    "have", "has", "had", "do", "does", "did", "will", "would", "shall",
    "should", "may", "might", "must", "can", "could",
    "i", "we", "you", "he", "she", "it", "they", "them", "their", "our",
    "in", "on", "at", "to", "for", "of", "with", "by", "from", "up", "about",
    "into", "through", "during", "before", "after", "above", "below",
    "between", "out", "off", "over", "under", "again", "further",
    "then", "once", "and", "but", "or", "nor", "so", "yet", "both",
    "either", "neither", "not", "no", "only", "own", "same", "than",
    "too", "very", "just", "because", "as", "until", "while",
    "this", "that", "these", "those", "what", "which", "who", "whom",
    "when", "where", "why", "how", "all", "each", "every", "any", "few",
    "more", "most", "other", "some", "such", "also", "well",
})

# Tokens that look like strong factual signals (numbers, %, $, acronyms)
_FACTUAL_PATTERN = re.compile(
    r"""
    \$[\d,\.]+[BMbmkK]?  |  # dollar amounts:  $45B, $1.2M
    \d+[\.,]?\d*\s*%     |  # percentages:     18%, 18.5%
    \d{4}                |  # years:           2024, 2025
    [A-Z]{2,}            |  # acronyms:        FDA, CAGR, AI, SaaS
    \d+[\.,]\d+[BMbmkK]? |  # numbers with unit: 1.2B
    \d+                     # plain integers
    """,
    re.VERBOSE,
)


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _tokenize(text: str) -> List[str]:
    """Lower-case, strip punctuation, remove stop-words. Returns meaningful tokens."""
    text = text.lower()
    text = text.translate(str.maketrans("", "", string.punctuation.replace("$", "").replace("%", "")))
    tokens = text.split()
    return [t for t in tokens if t not in _STOP_WORDS and len(t) >= 3]


def _factual_tokens(text: str) -> List[str]:
    """Extract high-value factual tokens (numbers, %, $, acronyms)."""
    return _FACTUAL_PATTERN.findall(text)


def _content_of(source: Any) -> str:
    """Extract searchable text from a source entry (dict or string URL)."""
    if isinstance(source, dict):
        parts = [
            source.get("content", ""),
            source.get("title", ""),
            source.get("url", ""),
        ]
        return " ".join(str(p) for p in parts if p)
    return str(source)


def _overlap_score(claim_tokens: List[str], factual_tokens: List[str], source_text: str) -> float:
    """
    Compute a [0, 1] overlap score between a claim and one source text.

    Strategy:
      1. Keyword overlap (regular tokens) – base weight 0.6
      2. Factual token matches (numbers, $, %)  – bonus weight 0.4
         Factual tokens are rare and hard to hallucinate coincidentally,
         so they carry a higher signal per match.
    """
    if not claim_tokens and not factual_tokens:
        return 0.0

    source_lower = source_text.lower()

    # ── Keyword overlap ──────────────────────────────────────────────────────
    if claim_tokens:
        kw_hits = sum(1 for t in claim_tokens if t in source_lower)
        kw_ratio = kw_hits / len(claim_tokens)
    else:
        kw_ratio = 0.0

    # ── Factual token overlap ────────────────────────────────────────────────
    if factual_tokens:
        # Normalise factual tokens (remove separators) for fuzzy matching
        fact_hits = sum(
            1 for t in factual_tokens
            if t.lower().replace(",", "").replace(".", "") in
               source_lower.replace(",", "").replace(".", "")
        )
        fact_ratio = fact_hits / len(factual_tokens)
    else:
        fact_ratio = 0.0

    # Weighted combination
    weight_kw   = 0.6 if claim_tokens else 0.0
    weight_fact = 0.4 if factual_tokens else 0.0
    total_weight = weight_kw + weight_fact

    if total_weight == 0:
        return 0.0

    score = (kw_ratio * weight_kw + fact_ratio * weight_fact) / total_weight
    return min(1.0, score)


def _status_from_score(score: float) -> SupportStatus:
    if score >= _THRESHOLD_SUPPORTED:
        return SUPPORTED
    if score >= _THRESHOLD_WEAK:
        return WEAK
    return UNKNOWN


# ─── Public API ───────────────────────────────────────────────────────────────

def check(
    claim: str,
    sources: Sequence[Union[Dict[str, Any], str]],
) -> CheckResult:
    """
    Check whether a single claim is supported by the provided sources.

    Parameters
    ----------
    claim : str
        A sentence or short phrase to verify (e.g. "Market size is $45B").
    sources : list of dicts or strings
        Each entry should be a Tavily search result dict
        (with 'content', 'title', 'url' keys) or a plain string.
        URL-only strings yield Unknown since there is no text to match against.

    Returns
    -------
    CheckResult
    """
    # ── Guard: empty claim ───────────────────────────────────────────────────
    if not claim or not claim.strip():
        return CheckResult(
            status=UNKNOWN,
            score=0.0,
            matched_sources=[],
            reason="Empty claim — nothing to verify.",
        )

    # ── Guard: no sources ────────────────────────────────────────────────────
    if not sources:
        return CheckResult(
            status=UNKNOWN,
            score=0.0,
            matched_sources=[],
            reason="No sources provided — cannot verify claim.",
        )

    # ── Tokenise the claim ────────────────────────────────────────────────────
    kw_tokens  = _tokenize(claim)
    fact_tokens = _factual_tokens(claim)

    if not kw_tokens and not fact_tokens:
        return CheckResult(
            status=UNKNOWN,
            score=0.0,
            matched_sources=[],
            reason="Claim contains no verifiable keywords or factual tokens.",
        )

    # ── Score each source ─────────────────────────────────────────────────────
    per_source: List[float] = []
    for src in sources:
        text = _content_of(src)
        per_source.append(_overlap_score(kw_tokens, fact_tokens, text))

    # Best-source score drives the verdict
    best_score     = max(per_source)
    matched        = [i for i, s in enumerate(per_source) if s >= _THRESHOLD_WEAK]
    matched_strong = [i for i, s in enumerate(per_source) if s >= _THRESHOLD_SUPPORTED]

    # Use the strongest single-source score as the final score
    final_score = round(best_score, 4)
    status      = _status_from_score(final_score)

    # ── Build reason ─────────────────────────────────────────────────────────
    kw_count   = len(kw_tokens)
    fact_count = len(fact_tokens)
    tokens_desc = []
    if kw_count:
        tokens_desc.append(f"{kw_count} keyword(s)")
    if fact_count:
        tokens_desc.append(f"{fact_count} factual token(s)")

    if status == SUPPORTED:
        reason = (
            f"{', '.join(tokens_desc)} matched strongly in "
            f"{len(matched_strong)} source(s) (best score: {final_score:.2f})."
        )
    elif status == WEAK:
        reason = (
            f"Partial match — {', '.join(tokens_desc)} found in "
            f"{len(matched)} source(s) (best score: {final_score:.2f}). "
            "Evidence is insufficient for full support."
        )
    else:
        reason = (
            f"No meaningful overlap found for {', '.join(tokens_desc) or 'this claim'} "
            f"across {len(sources)} source(s) (best score: {final_score:.2f})."
        )

    return CheckResult(
        status=status,
        score=final_score,
        matched_sources=matched,
        reason=reason,
    )


def check_claims(
    claims: Sequence[str],
    sources: Sequence[Union[Dict[str, Any], str]],
) -> List[CheckResult]:
    """
    Check a list of claims against the same set of sources.

    Parameters
    ----------
    claims  : list[str]  – Claims to verify.
    sources : list       – Source dicts or strings (shared for all claims).

    Returns
    -------
    list[CheckResult]  – One result per claim, in the same order.
    """
    return [check(c, sources) for c in claims]


def extract_claims(
    agent_output: Dict[str, Any],
    max_claims: int = 10,
) -> List[str]:
    """
    Extract verifiable string claims from an agent output dict.

    Looks for:
    - Top-level string values (short narrative fields)
    - Items inside top-level lists that are strings
    - Nested string values one level deep

    Parameters
    ----------
    agent_output : dict  – The dict returned by an agent's run().
    max_claims   : int   – Maximum number of claims to return (default 10).

    Returns
    -------
    list[str]  – De-duplicated, non-empty string claims.
    """
    if not isinstance(agent_output, dict):
        return []

    # Keys that are narrative / factual claims worth checking
    _SKIP_KEYS = {"sources", "parse_error", "raw_response", "job_id", "verdict"}

    claims: List[str] = []
    seen: set = set()

    def _add(s: str) -> None:
        s = s.strip()
        if s and s not in seen and len(s) >= 10:
            seen.add(s)
            claims.append(s)

    for key, value in agent_output.items():
        if key in _SKIP_KEYS:
            continue
        if len(claims) >= max_claims:
            break

        if isinstance(value, str):
            _add(value)

        elif isinstance(value, list):
            for item in value:
                if len(claims) >= max_claims:
                    break
                if isinstance(item, str):
                    _add(item)
                elif isinstance(item, dict):
                    # One level deep — grab short string fields
                    for v in item.values():
                        if isinstance(v, str) and len(v) >= 10:
                            _add(v)
                            break  # one claim per nested dict

        elif isinstance(value, dict):
            for v in value.values():
                if isinstance(v, str) and len(v) >= 10:
                    _add(v)

    return claims[:max_claims]
