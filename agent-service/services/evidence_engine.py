"""
Evidence Engine
===============
Transforms raw agent outputs (research, patent, funding, scientific,
competitive, etc.) into structured Evidence objects.

Each Evidence captures:
    claim          – The factual assertion extracted from the agent output
    agent          – Which agent produced it
    evidence_type  – Category of evidence
    source_urls    – Supporting URLs (if available)
    strength       – "strong" | "moderate" | "weak"

Rules
-----
- Read-only: agent outputs are never modified.
- No LLM calls: deterministic extraction from known output schemas.
- Graceful on None / parse_error outputs.

Usage
-----
    from services.evidence_engine import extract, extract_all, Evidence

    evidences = extract("research", agent_output)
    all_evidences = extract_all(pipeline_state)
    for ev in all_evidences:
        print(ev.agent, ev.evidence_type, ev.strength, ev.claim[:60])
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Sequence


# ─── Types ────────────────────────────────────────────────────────────────────

EvidenceType = Literal[
    "market_data",
    "competitive_data",
    "scientific_data",
    "patent_data",
    "funding_data",
    "trend_data",
    "risk_data",
    "opportunity_data",
    "validation_data",
    "strategy_data",
    "swot_data",
    "idea_validation",
    "general",
]

EvidenceStrength = Literal["strong", "moderate", "weak"]


@dataclass(frozen=True)
class Evidence:
    claim: str
    agent: str
    evidence_type: EvidenceType
    source_urls: List[str] = field(default_factory=list)
    strength: EvidenceStrength = "moderate"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim": self.claim,
            "agent": self.agent,
            "evidence_type": self.evidence_type,
            "source_urls": list(self.source_urls),
            "strength": self.strength,
        }


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _urls(output: Dict[str, Any]) -> List[str]:
    """Extract source URLs from an agent output dict."""
    sources = output.get("sources", [])
    if isinstance(sources, list):
        return [s for s in sources if isinstance(s, str) and s.startswith("http")]
    return []


def _str(value: Any, min_len: int = 10) -> Optional[str]:
    """Return value as string if non-empty and long enough, else None."""
    if value is None:
        return None
    s = str(value).strip()
    return s if len(s) >= min_len else None


def _list_strings(value: Any, min_len: int = 5) -> List[str]:
    """Extract non-empty strings from a list or return []."""
    if not isinstance(value, list):
        return []
    return [str(item).strip() for item in value
            if isinstance(item, str) and len(str(item).strip()) >= min_len]


def _strength_from_sources(urls: List[str], has_data: bool) -> EvidenceStrength:
    if len(urls) >= 3 and has_data:
        return "strong"
    if len(urls) >= 1 or has_data:
        return "moderate"
    return "weak"


def _make(
    claim: str,
    agent: str,
    evidence_type: EvidenceType,
    urls: List[str],
    strength: Optional[EvidenceStrength] = None,
) -> Optional[Evidence]:
    """Create an Evidence if claim is non-empty, else return None."""
    claim = claim.strip()
    if not claim or len(claim) < 10:
        return None
    s: EvidenceStrength = strength or _strength_from_sources(urls, bool(claim))
    return Evidence(claim=claim, agent=agent, evidence_type=evidence_type,
                    source_urls=list(urls), strength=s)


# ─── Per-agent extractors ─────────────────────────────────────────────────────

def _extract_research(output: Dict[str, Any]) -> List[Evidence]:
    urls = _urls(output)
    strength = _strength_from_sources(urls, True)
    evidences: List[Evidence] = []

    fields: List[tuple[str, EvidenceType]] = [
        ("market_overview",       "market_data"),
        ("market_size_estimate",  "market_data"),
        ("growth_rate",           "market_data"),
        ("summary",               "market_data"),
    ]
    for key, etype in fields:
        if ev := _make(str(output.get(key, "") or ""), "research", etype, urls, strength):
            evidences.append(ev)

    for item in _list_strings(output.get("recent_trends")):
        if ev := _make(item, "research", "trend_data", urls, strength):
            evidences.append(ev)

    for item in _list_strings(output.get("pain_points")):
        if ev := _make(item, "research", "market_data", urls, strength):
            evidences.append(ev)

    return evidences


def _extract_competitor(output: Dict[str, Any]) -> List[Evidence]:
    urls = _urls(output)
    strength = _strength_from_sources(urls, True)
    evidences: List[Evidence] = []

    if ev := _make(str(output.get("competitive_landscape", "") or ""),
                   "competitor", "competitive_data", urls, strength):
        evidences.append(ev)

    for item in _list_strings(output.get("differentiation_opportunities")):
        if ev := _make(item, "competitor", "competitive_data", urls, strength):
            evidences.append(ev)

    for comp in (output.get("competitors") or []):
        if isinstance(comp, dict):
            desc = comp.get("description") or comp.get("name") or ""
            if ev := _make(str(desc), "competitor", "competitive_data", urls, "moderate"):
                evidences.append(ev)

    return evidences


def _extract_scientific(output: Dict[str, Any]) -> List[Evidence]:
    urls = _urls(output)
    strength: EvidenceStrength = "strong" if len(urls) >= 2 else "moderate"
    evidences: List[Evidence] = []

    if ev := _make(str(output.get("academic_consensus", "") or ""),
                   "scientific", "scientific_data", urls, strength):
        evidences.append(ev)

    for item in _list_strings(output.get("key_findings")):
        if ev := _make(item, "scientific", "scientific_data", urls, strength):
            evidences.append(ev)

    for item in _list_strings(output.get("research_gaps")):
        if ev := _make(item, "scientific", "scientific_data", urls, "moderate"):
            evidences.append(ev)

    for paper in _list_strings(output.get("relevant_papers")):
        if ev := _make(paper, "scientific", "scientific_data", urls, strength):
            evidences.append(ev)

    return evidences


def _extract_patent(output: Dict[str, Any]) -> List[Evidence]:
    urls = _urls(output)
    evidences: List[Evidence] = []

    if ev := _make(str(output.get("ip_strategy_recommendation", "") or ""),
                   "patent", "patent_data", urls, "strong"):
        evidences.append(ev)

    for item in _list_strings(output.get("white_spaces")):
        if ev := _make(item, "patent", "patent_data", urls, "moderate"):
            evidences.append(ev)

    for item in _list_strings(output.get("freedom_to_operate_risks")):
        if ev := _make(item, "patent", "patent_data", urls, "moderate"):
            evidences.append(ev)

    for item in _list_strings(output.get("existing_patents")):
        if ev := _make(item, "patent", "patent_data", urls, "strong"):
            evidences.append(ev)

    return evidences


def _extract_funding(output: Dict[str, Any]) -> List[Evidence]:
    urls = _urls(output)
    strength = _strength_from_sources(urls, True)
    evidences: List[Evidence] = []

    for key in ("total_market_funding_estimate", "average_valuation_range",
                "funding_trend", "investor_thesis"):
        if ev := _make(str(output.get(key, "") or ""), "funding", "funding_data", urls, strength):
            evidences.append(ev)

    for round_ in (output.get("recent_funding_rounds") or []):
        if isinstance(round_, dict):
            parts = [str(v) for v in round_.values() if v]
            claim = " | ".join(parts)
        else:
            claim = str(round_)
        if ev := _make(claim, "funding", "funding_data", urls, strength):
            evidences.append(ev)

    return evidences


def _extract_trend(output: Dict[str, Any]) -> List[Evidence]:
    urls = _urls(output)
    strength = _strength_from_sources(urls, True)
    evidences: List[Evidence] = []

    for key in ("market_growth_rate", "market_forecast"):
        if ev := _make(str(output.get(key, "") or ""), "trend", "trend_data", urls, strength):
            evidences.append(ev)

    for item in _list_strings(output.get("trends")):
        if ev := _make(item, "trend", "trend_data", urls, strength):
            evidences.append(ev)

    for item in _list_strings(output.get("emerging_technologies")):
        if ev := _make(item, "trend", "trend_data", urls, "moderate"):
            evidences.append(ev)

    for item in _list_strings(output.get("disruptive_forces")):
        if ev := _make(item, "trend", "trend_data", urls, "moderate"):
            evidences.append(ev)

    return evidences


def _extract_research_gap(output: Dict[str, Any]) -> List[Evidence]:
    urls = _urls(output)
    evidences: List[Evidence] = []

    if ev := _make(str(output.get("differentiation_thesis", "") or ""),
                   "research_gap", "opportunity_data", urls, "strong"):
        evidences.append(ev)

    for key in ("unexplored_opportunities", "missing_features_in_market",
                "technology_white_spaces", "emerging_niches"):
        for item in _list_strings(output.get(key)):
            if ev := _make(item, "research_gap", "opportunity_data", urls, "moderate"):
                evidences.append(ev)

    return evidences


def _extract_swot(output: Dict[str, Any]) -> List[Evidence]:
    evidences: List[Evidence] = []
    mapping = {
        "strengths":    ("swot", "swot_data", "strong"),
        "opportunities": ("swot", "opportunity_data", "moderate"),
        "weaknesses":   ("swot", "swot_data", "moderate"),
        "threats":      ("swot", "risk_data", "moderate"),
    }
    for key, (agent, etype, strength) in mapping.items():
        for item in _list_strings(output.get(key)):
            if ev := _make(item, agent, etype, [], strength):  # type: ignore[arg-type]
                evidences.append(ev)
    return evidences


def _extract_opportunity(output: Dict[str, Any]) -> List[Evidence]:
    evidences: List[Evidence] = []
    for item in _list_strings(output.get("market_gaps")):
        if ev := _make(item, "opportunity", "opportunity_data", [], "moderate"):
            evidences.append(ev)
    if ev := _make(str(output.get("blue_ocean_potential", "") or ""),
                   "opportunity", "opportunity_data", [], "moderate"):
        evidences.append(ev)
    return evidences


def _extract_risk(output: Dict[str, Any]) -> List[Evidence]:
    evidences: List[Evidence] = []
    for item in _list_strings(output.get("critical_risks")):
        if ev := _make(item, "risk", "risk_data", [], "strong"):
            evidences.append(ev)
    if ev := _make(str(output.get("risk_mitigation_roadmap", "") or ""),
                   "risk", "risk_data", [], "moderate"):
        evidences.append(ev)
    for risk in (output.get("risks") or []):
        if isinstance(risk, dict):
            desc = risk.get("description") or risk.get("name") or ""
            if ev := _make(str(desc), "risk", "risk_data", [], "moderate"):
                evidences.append(ev)
    return evidences


def _extract_validation(output: Dict[str, Any]) -> List[Evidence]:
    evidences: List[Evidence] = []
    if ev := _make(str(output.get("recommendation", "") or ""),
                   "validation", "validation_data", [], "strong"):
        evidences.append(ev)
    for item in _list_strings(output.get("validation_experiments")):
        if ev := _make(item, "validation", "validation_data", [], "moderate"):
            evidences.append(ev)
    for assumption in (output.get("challenged_assumptions") or []):
        if isinstance(assumption, dict):
            text = assumption.get("challenge") or assumption.get("assumption") or ""
            if ev := _make(str(text), "validation", "validation_data", [], "moderate"):
                evidences.append(ev)
    return evidences


def _extract_strategy(output: Dict[str, Any]) -> List[Evidence]:
    evidences: List[Evidence] = []
    for key in ("go_to_market", "competitive_positioning", "pricing_strategy"):
        if ev := _make(str(output.get(key, "") or ""), "strategy", "strategy_data", [], "moderate"):
            evidences.append(ev)
    for item in _list_strings(output.get("strategic_recommendations")):
        if ev := _make(item, "strategy", "strategy_data", [], "moderate"):
            evidences.append(ev)
    return evidences


def _extract_report(output: Dict[str, Any]) -> List[Evidence]:
    evidences: List[Evidence] = []
    if ev := _make(str(output.get("executive_summary", "") or ""),
                   "report", "general", [], "strong"):
        evidences.append(ev)
    for item in _list_strings(output.get("recommendations")):
        if ev := _make(item, "report", "strategy_data", [], "strong"):
            evidences.append(ev)
    return evidences


def _extract_idea_guard(output: Dict[str, Any]) -> List[Evidence]:
    evidences: List[Evidence] = []
    if ev := _make(str(output.get("verdict_summary", "") or ""),
                   "idea_guard", "idea_validation", [], "strong"):
        evidences.append(ev)
    for item in _list_strings(output.get("rejection_reasons")):
        if ev := _make(item, "idea_guard", "idea_validation", [], "strong"):
            evidences.append(ev)
    for item in _list_strings(output.get("improvement_suggestions")):
        if ev := _make(item, "idea_guard", "idea_validation", [], "moderate"):
            evidences.append(ev)
    return evidences


_EXTRACTORS = {
    "idea_guard":         _extract_idea_guard,
    "research":           _extract_research,
    "competitor":         _extract_competitor,
    "scientific":         _extract_scientific,
    "patent":             _extract_patent,
    "funding":            _extract_funding,
    "trend":              _extract_trend,
    "research_gap":       _extract_research_gap,
    "swot":               _extract_swot,
    "opportunity":        _extract_opportunity,
    "risk":               _extract_risk,
    "validation":         _extract_validation,
    "strategy":           _extract_strategy,
    "report":             _extract_report,
}


# ─── Public API ───────────────────────────────────────────────────────────────

def extract(agent_name: str, output: Any) -> List[Evidence]:
    """
    Extract structured Evidence objects from a single agent output.

    Parameters
    ----------
    agent_name : str   Pipeline key (e.g. "research", "patent").
    output     : Any   Agent output dict (or None / parse_error dict).

    Returns
    -------
    list[Evidence]  Empty list if output is None, a parse error, or unknown agent.
    """
    if not isinstance(output, dict) or output.get("parse_error"):
        return []

    extractor = _EXTRACTORS.get(agent_name)
    if extractor is None:
        # Unknown agent: extract top-level string values generically
        urls: List[str] = []
        evidences: List[Evidence] = []
        for value in output.values():
            if isinstance(value, str) and len(value) >= 10:
                if ev := _make(value, agent_name, "general", urls, "weak"):
                    evidences.append(ev)
        return evidences

    return extractor(output)


def extract_all(
    agent_outputs: Dict[str, Any],
    max_per_agent: int = 10,
) -> List[Evidence]:
    """
    Extract Evidence from every agent output in a pipeline state dict.

    Parameters
    ----------
    agent_outputs  : dict   Full pipeline state (None values are skipped).
    max_per_agent  : int    Cap per-agent evidence count (default 10).

    Returns
    -------
    list[Evidence]  Flat list ordered by agent sequence.
    """
    all_evidences: List[Evidence] = []
    for agent_name, output in agent_outputs.items():
        if output is None:
            continue
        agent_evidences = extract(agent_name, output)
        all_evidences.extend(agent_evidences[:max_per_agent])
    return all_evidences


def summarise(evidences: Sequence[Evidence]) -> Dict[str, Any]:
    """
    Produce a compact summary dict from a list of Evidence objects.

    Returns
    -------
    dict with keys:
        total          – total evidence count
        by_type        – count per evidence_type
        by_strength    – count per strength level
        by_agent       – count per agent
        strong_claims  – first 5 strong-evidence claim strings
    """
    by_type: Dict[str, int] = {}
    by_strength: Dict[str, int] = {"strong": 0, "moderate": 0, "weak": 0}
    by_agent: Dict[str, int] = {}
    strong_claims: List[str] = []

    for ev in evidences:
        by_type[ev.evidence_type] = by_type.get(ev.evidence_type, 0) + 1
        by_strength[ev.strength]  = by_strength.get(ev.strength, 0) + 1
        by_agent[ev.agent]        = by_agent.get(ev.agent, 0) + 1
        if ev.strength == "strong" and len(strong_claims) < 5:
            strong_claims.append(ev.claim[:120])

    return {
        "total":         len(evidences),
        "by_type":       by_type,
        "by_strength":   by_strength,
        "by_agent":      by_agent,
        "strong_claims": strong_claims,
    }
