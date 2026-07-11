"""
Tests for services/source_ranker.py
"""
from __future__ import annotations

import copy

import pytest

from services.source_ranker import RankedSource, average_credibility, rank, rank_all, top_sources


# ─── RankedSource contract ────────────────────────────────────────────────────

def test_ranked_source_is_immutable():
    r = rank("https://pubmed.ncbi.nlm.nih.gov/12345")
    with pytest.raises((AttributeError, TypeError)):
        r.stars = 1  # type: ignore[misc]


def test_ranked_source_score_equals_stars_over_five():
    r = rank("https://nature.com/article/123")
    assert r.score == round(r.stars / 5.0, 2)


def test_ranked_source_label_contains_stars_and_category():
    r = rank("https://pubmed.ncbi.nlm.nih.gov/12345")
    assert "★" in r.label
    assert len(r.label) > 3


# ─── Tier 5 — Academic ────────────────────────────────────────────────────────

@pytest.mark.parametrize("url", [
    "https://pubmed.ncbi.nlm.nih.gov/12345",
    "https://www.nature.com/articles/s41586-021",
    "https://science.org/doi/10.1126/science.abf9346",
    "https://arxiv.org/abs/2301.00001",
    "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC123/",
    "https://www.thelancet.com/article/S0140-6736",
    "https://ieee.org/document/12345",
    "https://sciencedirect.com/science/article",
    "https://scholar.google.com/scholar?q=ai",
])
def test_tier5_academic_sources(url):
    r = rank(url)
    assert r.stars == 5, f"Expected 5 stars for {url}, got {r.stars}"
    assert r.score == 1.0
    assert r.category == "academic"


# ─── Tier 4 — Financial / Major news ─────────────────────────────────────────

@pytest.mark.parametrize("url", [
    "https://www.reuters.com/business/healthcare",
    "https://www.bloomberg.com/news/articles",
    "https://www.wsj.com/articles/ai-market",
    "https://www.ft.com/content/123",
    "https://www.forbes.com/sites/ai-market",
    "https://cbinsights.com/research/report",
    "https://www.hbr.org/2024/01/article",
])
def test_tier4_financial_news(url):
    r = rank(url)
    assert r.stars == 4, f"Expected 4 stars for {url}, got {r.stars}"
    assert r.score == 0.80


# ─── Tier 3 — Tech media / Encyclopedia ──────────────────────────────────────

@pytest.mark.parametrize("url", [
    "https://techcrunch.com/2024/01/startup",
    "https://venturebeat.com/ai/article",
    "https://www.wired.com/story/ai-market",
    "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "https://www.theverge.com/2024/article",
])
def test_tier3_tech_and_encyclopedia(url):
    r = rank(url)
    assert r.stars == 3, f"Expected 3 stars for {url}, got {r.stars}"
    assert r.score == 0.60


# ─── Tier 2 — Startup data ───────────────────────────────────────────────────

@pytest.mark.parametrize("url", [
    "https://www.crunchbase.com/organization/openai",
    "https://www.linkedin.com/company/openai",
    "https://medium.com/@author/article",
])
def test_tier2_startup_data(url):
    r = rank(url)
    assert r.stars == 2, f"Expected 2 stars for {url}, got {r.stars}"
    assert r.score == 0.40


# ─── Tier 1 — Social media / Unknown ─────────────────────────────────────────

@pytest.mark.parametrize("url", [
    "https://twitter.com/openai/status/123",
    "https://x.com/openai/status/123",
    "https://www.reddit.com/r/MachineLearning",
    "https://randomblog.io/my-startup-opinion",
    "https://example.com/page",
    "https://mock-research.example.com/report-1",
])
def test_tier1_unknown_or_social(url):
    r = rank(url)
    assert r.stars == 1, f"Expected 1 star for {url}, got {r.stars}"
    assert r.score == 0.20


# ─── Government / .edu fallback ──────────────────────────────────────────────

@pytest.mark.parametrize("url", [
    "https://www.fda.gov/medical-devices",
    "https://www.nih.gov/research",
    "https://cms.gov/medicare",
])
def test_gov_domains_rank_high(url):
    r = rank(url)
    assert r.stars >= 4, f"Expected >= 4 stars for {url}, got {r.stars}"


@pytest.mark.parametrize("url", [
    "https://www.mit.edu/research/ai",
    "https://www.stanford.edu/group/ailab",
    "https://www.harvard.edu/research",
])
def test_edu_domains_rank_high(url):
    r = rank(url)
    assert r.stars >= 4, f"Expected >= 4 stars for {url}, got {r.stars}"


# ─── Edge cases ───────────────────────────────────────────────────────────────

def test_empty_url_returns_one_star():
    r = rank("")
    assert r.stars == 1
    assert r.score == 0.20


def test_rank_does_not_mutate_input():
    url = "https://pubmed.ncbi.nlm.nih.gov/12345"
    original = url
    rank(url)
    assert url == original


def test_rank_handles_url_with_path_and_query():
    r = rank("https://pubmed.ncbi.nlm.nih.gov/12345?term=ai&format=abstract")
    assert r.stars == 5


def test_rank_handles_http_not_just_https():
    r = rank("http://arxiv.org/abs/2301.00001")
    assert r.stars == 5


# ─── rank_all() ──────────────────────────────────────────────────────────────

def test_rank_all_returns_list_of_ranked_sources():
    sources = [
        "https://pubmed.ncbi.nlm.nih.gov/1",
        "https://techcrunch.com/article",
        "https://example.com/blog",
    ]
    ranked = rank_all(sources)
    assert len(ranked) == 3
    assert all(isinstance(r, RankedSource) for r in ranked)


def test_rank_all_sorted_best_first():
    sources = [
        "https://example.com/blog",         # 1 star
        "https://pubmed.ncbi.nlm.nih.gov/1", # 5 stars
        "https://techcrunch.com/article",    # 3 stars
    ]
    ranked = rank_all(sources)
    assert ranked[0].stars >= ranked[1].stars >= ranked[2].stars


def test_rank_all_accepts_source_dicts():
    sources = [
        {"url": "https://pubmed.ncbi.nlm.nih.gov/1", "title": "Paper A"},
        {"url": "https://example.com/blog", "title": "Blog post"},
    ]
    ranked = rank_all(sources)
    assert ranked[0].stars == 5
    assert ranked[1].stars == 1


def test_rank_all_handles_mixed_strings_and_dicts():
    sources = [
        "https://arxiv.org/abs/123",
        {"url": "https://techcrunch.com/post", "title": "TC"},
        "https://reddit.com/r/ml",
    ]
    ranked = rank_all(sources)
    assert len(ranked) == 3


def test_rank_all_empty_list_returns_empty():
    assert rank_all([]) == []


def test_rank_all_does_not_mutate_input():
    sources = [
        {"url": "https://pubmed.ncbi.nlm.nih.gov/1"},
        "https://techcrunch.com/article",
    ]
    snapshot = copy.deepcopy(sources)
    rank_all(sources)
    assert sources == snapshot


# ─── average_credibility() ───────────────────────────────────────────────────

def test_average_credibility_all_academic():
    sources = [
        "https://pubmed.ncbi.nlm.nih.gov/1",
        "https://arxiv.org/abs/123",
        "https://nature.com/article",
    ]
    avg = average_credibility(sources)
    assert avg == 1.0


def test_average_credibility_mixed():
    sources = [
        "https://pubmed.ncbi.nlm.nih.gov/1",  # 5 stars → 1.0
        "https://techcrunch.com/article",       # 3 stars → 0.6
        "https://example.com/blog",              # 1 star  → 0.2
    ]
    avg = average_credibility(sources)
    expected = round((1.0 + 0.6 + 0.2) / 3, 4)
    assert avg == expected


def test_average_credibility_empty_returns_zero():
    assert average_credibility([]) == 0.0


# ─── top_sources() ───────────────────────────────────────────────────────────

def test_top_sources_returns_n_best():
    sources = [
        "https://example.com/blog",
        "https://pubmed.ncbi.nlm.nih.gov/1",
        "https://techcrunch.com/article",
        "https://arxiv.org/abs/123",
    ]
    top = top_sources(sources, n=2)
    assert len(top) == 2
    assert all(r.stars >= 4 for r in top)


def test_top_sources_default_n_is_3():
    sources = ["https://pubmed.ncbi.nlm.nih.gov/1",
               "https://nature.com/a", "https://arxiv.org/1",
               "https://techcrunch.com/a", "https://example.com/b"]
    top = top_sources(sources)
    assert len(top) == 3
