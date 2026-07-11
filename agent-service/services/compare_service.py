"""
Compare Service
===============
Compares two pipeline research results side-by-side.

Provides two comparison types:
  1. compare_ideas(state_a, state_b)       – overall idea comparison
  2. compare_competitors(state_a, state_b) – competitor-level comparison

Read-only — inputs are never modified.
No LLM calls — pure deterministic scoring and diff logic.

Usage
-----
    from services.compare_service import compare_ideas, compare_competitors

    result = compare_ideas(state_a, state_b)
    comp   = compare_competitors(state_a, state_b)
"""
from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _safe_float(v: Any, default: float = 0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def _safe_str(v: Any, default: str = "N/A") -> str:
    s = str(v).strip() if v is not None else ""
    return s if s else default


def _delta(a: float, b: float) -> str:
    """Return a human-readable delta string."""
    d = round(b - a, 1)
    if d > 0:
        return f"+{d}"
    if d < 0:
        return str(d)
    return "="


def _winner(score_a: float, score_b: float, label_a: str, label_b: str) -> str:
    if score_a > score_b + 2:
        return label_a
    if score_b > score_a + 2:
        return label_b
    return "tie"


def _risk_to_score(level: str) -> float:
    """Convert risk level string to a numeric score (lower risk = higher score)."""
    return {"low": 80.0, "medium": 50.0, "high": 20.0}.get(
        str(level).lower(), 50.0
    )


def _grade_to_score(grade: str) -> float:
    return {"A": 92.0, "B": 77.0, "C": 62.0, "D": 47.0, "F": 25.0}.get(
        str(grade).upper(), 50.0
    )


# ─── Idea comparison ──────────────────────────────────────────────────────────

def compare_ideas(
    state_a: Dict[str, Any],
    state_b: Dict[str, Any],
    label_a: str = "Idea A",
    label_b: str = "Idea B",
) -> Dict[str, Any]:
    """
    Compare two pipeline research states across all key dimensions.

    Parameters
    ----------
    state_a, state_b : dict
        Full pipeline state dicts.
    label_a, label_b : str
        Human-readable names for the two ideas.

    Returns
    -------
    dict with structured comparison including per-dimension scores,
    deltas, winners, and an overall recommendation.
    """
    # ── Extract scores ────────────────────────────────────────────────────────
    def _scores(s: Dict[str, Any]) -> Dict[str, float]:
        rep   = s.get("report")           or {}
        opp   = s.get("opportunities")    or {}
        risk  = s.get("risks")            or {}
        inno  = s.get("innovation_score") or {}
        comp  = s.get("competitors")      or {}
        fund  = s.get("funding")          or {}
        sci   = s.get("scientific")       or {}
        rgap  = s.get("research_gaps")    or {}
        pat   = s.get("patents")          or {}

        return {
            "market_score":        _safe_float(rep.get("market_score"),             50),
            "opportunity_score":   _safe_float(opp.get("opportunity_score"),        50),
            "innovation_score":    _safe_float(inno.get("innovation_score"),        50),
            "risk_score":          _risk_to_score(risk.get("overall_risk_level",    "medium")),
            "competition_score":   100 - _safe_float(comp.get("market_saturation_score"), 50),
            "funding_score":       _safe_float(fund.get("funding_activity_score"),  50),
            "research_maturity":   _safe_float(sci.get("research_maturity_score"),  50),
            "novelty_score":       _safe_float(rgap.get("novelty_score"),           50),
            "patent_white_space":  100 - _safe_float(pat.get("patent_density_score"), 50),
            "grade_score":         _grade_to_score(inno.get("grade",               "C")),
        }

    sc_a = _scores(state_a)
    sc_b = _scores(state_b)

    # ── Per-dimension comparison ──────────────────────────────────────────────
    dimensions = [
        ("market_score",       "Market Strength"),
        ("opportunity_score",  "Market Opportunity"),
        ("innovation_score",   "Innovation"),
        ("risk_score",         "Risk Safety"),
        ("competition_score",  "Competitive Space"),
        ("funding_score",      "Funding Climate"),
        ("research_maturity",  "Research Maturity"),
        ("novelty_score",      "Novelty"),
        ("patent_white_space", "IP White Space"),
    ]

    dimension_results = []
    wins_a = wins_b = ties = 0

    for key, label in dimensions:
        va, vb = sc_a[key], sc_b[key]
        w = _winner(va, vb, label_a, label_b)
        if w == label_a:   wins_a += 1
        elif w == label_b: wins_b += 1
        else:              ties += 1

        dimension_results.append({
            "dimension": label,
            "score_a":   round(va, 1),
            "score_b":   round(vb, 1),
            "delta":     _delta(va, vb),
            "winner":    w,
        })

    # ── Overall scores ────────────────────────────────────────────────────────
    overall_a = round(sum(sc_a[k] for k, _ in dimensions) / len(dimensions), 1)
    overall_b = round(sum(sc_b[k] for k, _ in dimensions) / len(dimensions), 1)
    overall_winner = _winner(overall_a, overall_b, label_a, label_b)

    # ── Metadata ──────────────────────────────────────────────────────────────
    def _meta(s: Dict[str, Any], label: str) -> Dict[str, Any]:
        rep  = s.get("report")           or {}
        inno = s.get("innovation_score") or {}
        risk = s.get("risks")            or {}
        res  = s.get("research")         or {}
        return {
            "label":           label,
            "idea":            _safe_str(s.get("idea")),
            "industry":        _safe_str(s.get("industry")),
            "executive_summary": _safe_str(rep.get("executive_summary"), ""),
            "innovation_grade":  _safe_str(inno.get("grade"), "N/A"),
            "risk_level":        _safe_str(risk.get("overall_risk_level"), "unknown"),
            "market_size":       _safe_str(res.get("market_size_estimate"), "Unknown"),
            "growth_rate":       _safe_str(res.get("growth_rate"), "Unknown"),
            "overall_score":     overall_a if label == label_a else overall_b,
        }

    # ── Strengths & weaknesses relative to each other ─────────────────────────
    def _advantages(winner_label: str) -> List[str]:
        return [
            d["dimension"] for d in dimension_results
            if d["winner"] == winner_label
        ]

    # ── Recommendation ────────────────────────────────────────────────────────
    if overall_winner == "tie":
        recommendation = (
            f"{label_a} and {label_b} are very close. "
            "Choose based on your team's expertise and execution capacity."
        )
    else:
        loser = label_b if overall_winner == label_a else label_a
        recommendation = (
            f"{overall_winner} scores higher overall ({max(overall_a, overall_b):.0f} vs "
            f"{min(overall_a, overall_b):.0f}). "
            f"It has a stronger position in {', '.join(_advantages(overall_winner)[:3])}."
        )

    return {
        "type":               "idea_comparison",
        "label_a":            label_a,
        "label_b":            label_b,
        "meta_a":             _meta(state_a, label_a),
        "meta_b":             _meta(state_b, label_b),
        "dimensions":         dimension_results,
        "overall_score_a":    overall_a,
        "overall_score_b":    overall_b,
        "overall_winner":     overall_winner,
        "wins_a":             wins_a,
        "wins_b":             wins_b,
        "ties":               ties,
        "advantages_a":       _advantages(label_a),
        "advantages_b":       _advantages(label_b),
        "recommendation":     recommendation,
    }


# ─── Competitor comparison ────────────────────────────────────────────────────

def compare_competitors(
    state_a: Dict[str, Any],
    state_b: Dict[str, Any],
    label_a: str = "Idea A",
    label_b: str = "Idea B",
) -> Dict[str, Any]:
    """
    Compare the competitive landscapes of two pipeline states.

    Returns a side-by-side breakdown of competitors, saturation scores,
    differentiation opportunities, and an overall competitive verdict.
    """
    comp_a = state_a.get("competitors") or {}
    comp_b = state_b.get("competitors") or {}

    sat_a  = _safe_float(comp_a.get("market_saturation_score"), 50)
    sat_b  = _safe_float(comp_b.get("market_saturation_score"), 50)

    # Lower saturation = easier to enter
    entry_ease_a = round(100 - sat_a, 1)
    entry_ease_b = round(100 - sat_b, 1)
    easier_market = _winner(entry_ease_a, entry_ease_b, label_a, label_b)

    def _comp_list(comp_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        raw = comp_dict.get("competitors", [])
        result = []
        for c in raw[:6]:
            if not isinstance(c, dict):
                continue
            result.append({
                "name":           _safe_str(c.get("name")),
                "threat_level":   _safe_str(c.get("threat_level"), "unknown"),
                "market_share":   _safe_str(c.get("market_share"), "N/A"),
                "strengths":      c.get("strengths", [])[:2] if isinstance(c.get("strengths"), list) else [],
                "weaknesses":     c.get("weaknesses", [])[:2] if isinstance(c.get("weaknesses"), list) else [],
            })
        return result

    competitors_a = _comp_list(comp_a)
    competitors_b = _comp_list(comp_b)

    # Count high-threat competitors
    high_threat_a = sum(1 for c in competitors_a if c["threat_level"] == "high")
    high_threat_b = sum(1 for c in competitors_b if c["threat_level"] == "high")

    diff_opps_a = comp_a.get("differentiation_opportunities", [])
    diff_opps_b = comp_b.get("differentiation_opportunities", [])

    landscape_a = _safe_str(comp_a.get("competitive_landscape"), "")
    landscape_b = _safe_str(comp_b.get("competitive_landscape"), "")

    # Summary verdict
    if easier_market == "tie":
        verdict = f"Both {label_a} and {label_b} face similarly competitive markets."
    else:
        harder = label_b if easier_market == label_a else label_a
        verdict = (
            f"{easier_market} operates in a less saturated market "
            f"({100-sat_a if easier_market==label_a else 100-sat_b:.0f}/100 entry ease). "
            f"{harder} faces more established competition."
        )

    return {
        "type":                   "competitor_comparison",
        "label_a":                label_a,
        "label_b":                label_b,
        "saturation_a":           round(sat_a, 1),
        "saturation_b":           round(sat_b, 1),
        "entry_ease_a":           entry_ease_a,
        "entry_ease_b":           entry_ease_b,
        "easier_market":          easier_market,
        "high_threat_count_a":    high_threat_a,
        "high_threat_count_b":    high_threat_b,
        "competitors_a":          competitors_a,
        "competitors_b":          competitors_b,
        "differentiation_opps_a": diff_opps_a,
        "differentiation_opps_b": diff_opps_b,
        "landscape_a":            landscape_a,
        "landscape_b":            landscape_b,
        "verdict":                verdict,
    }
