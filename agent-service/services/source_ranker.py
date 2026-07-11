"""
Source Ranker
=============
Assigns credibility stars (1–5) and a normalized score (0.0–1.0) to URLs
based on their domain's academic, journalistic, or commercial reputation.

    PubMed / Nature / Science / Lancet  →  ★★★★★  (1.00)
    Reuters / Bloomberg / WSJ / FT      →  ★★★★   (0.80)
    TechCrunch / VentureBeat / Wired    →  ★★★    (0.60)
    Wikipedia / government (.gov/.edu)  →  ★★★    (0.60)
    Crunchbase / LinkedIn / AngelList   →  ★★     (0.40)
    Unknown / personal blog             →  ★      (0.20)

Rules
-----
- Read-only: inputs are never modified.
- No LLM calls: pure domain-based lookup with regex fallback.
- Accepts URL strings, source dicts (with "url" key), or mixed lists.

Usage
-----
    from services.source_ranker import rank, rank_all, average_credibility

    r = rank("https://pubmed.ncbi.nlm.nih.gov/12345")
    r.stars     # 5
    r.score     # 1.0
    r.category  # "academic"

    ranked = rank_all(sources)
    avg    = average_credibility(sources)   # 0.74
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Dict, List, Literal, Sequence, Union


# ─── Result type ──────────────────────────────────────────────────────────────

SourceCategory = Literal[
    "academic",
    "financial_news",
    "tech_media",
    "encyclopedia",
    "government",
    "startup_data",
    "general_news",
    "social_media",
    "unknown",
]


@dataclass(frozen=True)
class RankedSource:
    url: str
    domain: str
    stars: int              # 1 – 5
    score: float            # 0.0 – 1.0  (stars / 5)
    category: SourceCategory
    label: str              # human-readable e.g. "★★★★★ Academic"


# ─── Domain registry ──────────────────────────────────────────────────────────
# Format: (domain_substring, stars, category)
# Checked in order — first match wins.

_DOMAIN_RULES: List[tuple[str, int, SourceCategory]] = [
    # ── Tier 5: Academic / Peer-reviewed ─────────────────────────────────────
    ("pubmed.ncbi.nlm.nih.gov",  5, "academic"),
    ("ncbi.nlm.nih.gov",         5, "academic"),
    ("nature.com",               5, "academic"),
    ("science.org",              5, "academic"),
    ("thelancet.com",            5, "academic"),
    ("nejm.org",                 5, "academic"),
    ("bmj.com",                  5, "academic"),
    ("cell.com",                 5, "academic"),
    ("jamanetwork.com",          5, "academic"),
    ("annals.org",               5, "academic"),
    ("arxiv.org",                5, "academic"),
    ("biorxiv.org",              5, "academic"),
    ("medrxiv.org",              5, "academic"),
    ("semanticscholar.org",      5, "academic"),
    ("scholar.google.com",       5, "academic"),
    ("researchgate.net",         4, "academic"),
    ("springer.com",             5, "academic"),
    ("wiley.com",                5, "academic"),
    ("elsevier.com",             5, "academic"),
    ("sciencedirect.com",        5, "academic"),
    ("tandfonline.com",          4, "academic"),
    ("ieee.org",                 5, "academic"),
    ("acm.org",                  5, "academic"),
    ("nih.gov",                  5, "academic"),
    ("who.int",                  5, "academic"),
    # ── Tier 4: Financial / Major news ───────────────────────────────────────
    ("reuters.com",              4, "financial_news"),
    ("bloomberg.com",            4, "financial_news"),
    ("wsj.com",                  4, "financial_news"),
    ("ft.com",                   4, "financial_news"),
    ("economist.com",            4, "financial_news"),
    ("forbes.com",               4, "financial_news"),
    ("fortune.com",              4, "financial_news"),
    ("businessinsider.com",      4, "financial_news"),
    ("cnbc.com",                 4, "financial_news"),
    ("marketwatch.com",          4, "financial_news"),
    ("statista.com",             4, "financial_news"),
    ("cbinsights.com",           4, "startup_data"),
    ("pitchbook.com",            4, "startup_data"),
    # ── Tier 3: Tech media / Encyclopedia / Government ───────────────────────
    ("techcrunch.com",           3, "tech_media"),
    ("venturebeat.com",          3, "tech_media"),
    ("wired.com",                3, "tech_media"),
    ("theverge.com",             3, "tech_media"),
    ("arstechnica.com",          3, "tech_media"),
    ("mit.edu",                  4, "academic"),
    ("stanford.edu",             4, "academic"),
    ("harvard.edu",              4, "academic"),
    ("wikipedia.org",            3, "encyclopedia"),
    ("investopedia.com",         3, "general_news"),
    ("hbr.org",                  4, "general_news"),
    # ── Tier 2: Startup data / Aggregators ───────────────────────────────────
    ("crunchbase.com",           2, "startup_data"),
    ("linkedin.com",             2, "startup_data"),
    ("angel.co",                 2, "startup_data"),
    ("producthunt.com",          2, "startup_data"),
    ("g2.com",                   2, "startup_data"),
    ("capterra.com",             2, "startup_data"),
    ("ycombinator.com",          3, "startup_data"),
    ("medium.com",               2, "general_news"),
    ("substack.com",             2, "general_news"),
    # ── Social media (Tier 1) ────────────────────────────────────────────────
    ("twitter.com",              1, "social_media"),
    ("x.com",                    1, "social_media"),
    ("reddit.com",               1, "social_media"),
    ("facebook.com",             1, "social_media"),
    ("instagram.com",            1, "social_media"),
    ("tiktok.com",               1, "social_media"),
]

# Regex-based fallback rules (applied when no domain substring matches)
_REGEX_RULES: List[tuple[re.Pattern, int, SourceCategory]] = [
    (re.compile(r"\.gov(/|$)"),   4, "government"),
    (re.compile(r"\.edu(/|$)"),   4, "academic"),
    (re.compile(r"\.ac\.\w+"),    4, "academic"),
    (re.compile(r"\.org(/|$)"),   3, "general_news"),
]

_STARS_TO_LABEL = {
    5: "★★★★★",
    4: "★★★★",
    3: "★★★",
    2: "★★",
    1: "★",
}

_CATEGORY_LABELS: Dict[SourceCategory, str] = {
    "academic":       "Academic",
    "financial_news": "Financial News",
    "tech_media":     "Tech Media",
    "encyclopedia":   "Encyclopedia",
    "government":     "Government",
    "startup_data":   "Startup Data",
    "general_news":   "General News",
    "social_media":   "Social Media",
    "unknown":        "Unknown",
}


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _extract_domain(url: str) -> str:
    """Extract lowercase domain from a URL string."""
    url = url.strip().lower()
    # Remove scheme
    url = re.sub(r"^https?://", "", url)
    # Remove path
    domain = url.split("/")[0]
    # Remove port
    domain = domain.split(":")[0]
    return domain


def _lookup(url: str) -> tuple[int, SourceCategory]:
    """Return (stars, category) for a URL. Never raises."""
    if not url or not isinstance(url, str):
        return 1, "unknown"

    domain = _extract_domain(url)
    url_lower = url.lower()

    # 1. Exact domain substring match
    for substring, stars, category in _DOMAIN_RULES:
        if substring in domain:
            return stars, category

    # 2. Regex fallback on full URL
    for pattern, stars, category in _REGEX_RULES:
        if pattern.search(url_lower):
            return stars, category

    # 3. Mock / test URLs
    if "mock" in domain or "example.com" in domain or "localhost" in domain:
        return 1, "unknown"

    return 1, "unknown"


def _url_from(source: Any) -> str:
    """Extract a URL string from a source dict or plain string."""
    if isinstance(source, str):
        return source
    if isinstance(source, dict):
        return source.get("url", "") or ""
    return ""


# ─── Public API ───────────────────────────────────────────────────────────────

def rank(url: str) -> RankedSource:
    """
    Rank a single URL by credibility.

    Parameters
    ----------
    url : str   A URL string.

    Returns
    -------
    RankedSource
    """
    url = (url or "").strip()
    domain = _extract_domain(url) if url else "unknown"
    stars, category = _lookup(url)
    score = round(stars / 5.0, 2)
    label = f"{_STARS_TO_LABEL[stars]} {_CATEGORY_LABELS[category]}"
    return RankedSource(url=url, domain=domain, stars=stars,
                        score=score, category=category, label=label)


def rank_all(
    sources: Sequence[Union[str, Dict[str, Any]]],
) -> List[RankedSource]:
    """
    Rank a list of sources (URL strings or source dicts).

    Parameters
    ----------
    sources : list of str or dict  – Each entry is a URL or a dict with a "url" key.

    Returns
    -------
    list[RankedSource]  Sorted best-first (highest stars first).
    """
    ranked = [rank(_url_from(s)) for s in sources if s]
    return sorted(ranked, key=lambda r: r.stars, reverse=True)


def average_credibility(
    sources: Sequence[Union[str, Dict[str, Any]]],
) -> float:
    """
    Compute the average credibility score (0.0–1.0) for a list of sources.
    Returns 0.0 if the list is empty.
    """
    ranked = rank_all(sources)
    if not ranked:
        return 0.0
    return round(sum(r.score for r in ranked) / len(ranked), 4)


def top_sources(
    sources: Sequence[Union[str, Dict[str, Any]]],
    n: int = 3,
) -> List[RankedSource]:
    """Return the top-n highest-credibility sources."""
    return rank_all(sources)[:n]
