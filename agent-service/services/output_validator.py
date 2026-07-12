"""
Output Validator
================
Validates agent outputs after they are produced by the LLM.

Contract
--------
- NEVER modifies the data passed in.
- Returns a ValidationResult with status "pass" or "warning".
- "warning" means the output may be degraded but the pipeline continues.
- Each warning carries a human-readable message.

Usage
-----
    from services.output_validator import validate

    result = validate("research", agent_output)
    if result.status == "warning":
        for w in result.warnings:
            logger.warning("OutputValidator [research]: %s", w)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Sequence

# Pipeline state keys that carry plain request/run metadata rather than an
# agent's LLM output (see orchestrator/pipeline.py's initial state dict).
# These must never be run through agent-output validation.
_NON_AGENT_KEYS = {
    "job_id", "idea", "industry", "healthcare_mode",
    "progress", "current_agent", "errors", "status", "done",
}


# ─── Result type ──────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class ValidationResult:
    status: Literal["pass", "warning"]
    warnings: List[str] = field(default_factory=list)

    def __bool__(self) -> bool:
        return self.status == "pass"


# ─── Per-agent schema registry ────────────────────────────────────────────────
# Each entry defines:
#   required  – top-level keys that must be present and non-empty
#   scores    – numeric keys that must be in [0, 100]
#   sources   – True if the agent is expected to populate a "sources" list
#   citations – True if any list field must contain at least one string item

_SCHEMAS: Dict[str, Dict[str, Any]] = {
    "idea_guard": {
        "required": [
            "verdict", "verdict_summary", "clarity_score", "vagueness_score",
            "is_startup_idea", "legal_status", "ethical_status",
            "technical_feasibility", "market_potential",
        ],
        "scores":   ["clarity_score", "vagueness_score"],
        "sources":  False,
        "citations": False,
    },
    "research": {
        "required": [
            "market_overview", "key_players", "market_size_estimate",
            "recent_trends", "growth_rate", "target_customers",
            "pain_points", "summary",
        ],
        "scores":   [],
        "sources":  True,
        "citations": True,   # key_players / recent_trends must be non-empty lists
    },
    "competitor": {
        "required": [
            "competitors", "competitive_landscape",
            "market_saturation_score", "differentiation_opportunities",
        ],
        "scores":   ["market_saturation_score"],
        "sources":  True,
        "citations": True,   # competitors list
    },
    "scientific": {
        "required": [
            "relevant_papers", "research_maturity", "research_maturity_score",
            "key_findings", "research_gaps", "academic_consensus",
        ],
        "scores":   ["research_maturity_score"],
        "sources":  True,
        "citations": True,   # relevant_papers
    },
    "patent": {
        "required": [
            "existing_patents", "patent_density_score",
            "white_spaces", "freedom_to_operate_risks", "ip_strategy_recommendation",
        ],
        "scores":   ["patent_density_score"],
        "sources":  True,
        "citations": False,
    },
    "funding": {
        "required": [
            "recent_funding_rounds", "funding_activity_score",
            "total_market_funding_estimate", "top_investors",
            "average_valuation_range", "funding_trend", "investor_thesis",
        ],
        "scores":   ["funding_activity_score"],
        "sources":  True,
        "citations": True,   # recent_funding_rounds
    },
    "trend": {
        "required": [
            "trends", "market_growth_rate", "emerging_technologies",
            "regulatory_trends", "market_forecast", "disruptive_forces",
        ],
        "scores":   [],
        "sources":  True,
        "citations": True,   # trends list
    },
    "research_gap": {
        "required": [
            "unexplored_opportunities", "missing_features_in_market",
            "emerging_niches", "competitor_blind_spots",
            "technology_white_spaces", "novelty_score", "differentiation_thesis",
        ],
        "scores":   ["novelty_score"],
        "sources":  True,
        "citations": True,   # unexplored_opportunities
    },
    "swot": {
        "required": ["strengths", "weaknesses", "opportunities", "threats"],
        "scores":   [],
        "sources":  False,
        "citations": True,   # all four SWOT lists
    },
    "opportunity": {
        "required": [
            "market_gaps", "target_segments",
            "opportunity_score", "blue_ocean_potential",
        ],
        "scores":   ["opportunity_score"],
        "sources":  False,
        "citations": True,   # market_gaps
    },
    "risk": {
        "required": [
            "risks", "overall_risk_level", "risk_score",
            "critical_risks", "risk_mitigation_roadmap",
        ],
        "scores":   ["risk_score"],
        "sources":  False,
        "citations": True,   # risks list
    },
    "innovation_scoring": {
        "required": ["innovation_score", "grade", "score_explanation", "score_breakdown"],
        "scores":   ["innovation_score"],
        "sources":  False,
        "citations": False,
    },
    "validation": {
        "required": [
            "challenged_assumptions", "validation_experiments",
            "confidence_level", "key_risks_identified", "recommendation",
        ],
        "scores":   [],
        "sources":  False,
        "citations": True,   # challenged_assumptions / validation_experiments
    },
    "strategy": {
        "required": [
            "strategic_recommendations", "innovation_hypotheses",
            "go_to_market", "competitive_positioning",
            "pricing_strategy", "key_partnerships",
            "success_metrics", "roadmap",
        ],
        "scores":   [],
        "sources":  False,
        "citations": True,   # strategic_recommendations
    },
    "report": {
        "required": [
            "executive_summary", "competition_level",
            "recommendations", "key_metrics", "full_report",
        ],
        # market_score and opportunity_score are injected canonically by report_agent.py
        # after the LLM call — do not require them from the LLM JSON output.
        "scores":   [],
        "sources":  False,
        "citations": True,   # recommendations
    },
}


# ─── Internal checks ──────────────────────────────────────────────────────────

def _check_parse_error(output: Dict[str, Any], warnings: List[str]) -> bool:
    """Return True (fatal) if the output itself signals an LLM parse failure."""
    if not isinstance(output, dict):
        warnings.append("Output is not a dict — LLM response could not be parsed.")
        return True
    if output.get("parse_error"):
        raw = output.get("raw_response", "")
        preview = (raw[:120] + "…") if len(raw) > 120 else raw
        warnings.append(f"LLM returned unparseable output. Raw preview: {preview!r}")
        return True
    return False


def _check_required_fields(
    output: Dict[str, Any],
    required: Sequence[str],
    warnings: List[str],
) -> None:
    for key in required:
        if key not in output:
            warnings.append(f"Missing required field: '{key}'.")
        elif output[key] is None:
            warnings.append(f"Field '{key}' is None.")
        elif isinstance(output[key], (list, str, dict)) and not output[key]:
            warnings.append(f"Field '{key}' is present but empty.")


def _check_scores(
    output: Dict[str, Any],
    score_fields: Sequence[str],
    warnings: List[str],
) -> None:
    for key in score_fields:
        value = output.get(key)
        if value is None:
            continue  # already caught by _check_required_fields
        try:
            numeric = float(value)
        except (TypeError, ValueError):
            warnings.append(f"Score field '{key}' is not numeric: {value!r}.")
            continue
        if not (0 <= numeric <= 100):
            warnings.append(
                f"Score field '{key}' out of range [0, 100]: {numeric}."
            )


def _check_sources(output: Dict[str, Any], warnings: List[str]) -> None:
    sources = output.get("sources")
    if sources is None:
        warnings.append("Expected 'sources' list is missing.")
    elif not isinstance(sources, list):
        warnings.append(f"'sources' should be a list, got {type(sources).__name__}.")
    elif len(sources) == 0:
        warnings.append("'sources' list is empty — no web citations attached.")


def _check_citations(output: Dict[str, Any], warnings: List[str]) -> None:
    """
    Check that at least one list-type field contains at least one non-empty item.
    This is a lightweight proxy for 'citations present'.
    """
    list_fields = [
        k for k, v in output.items()
        if isinstance(v, list) and k != "sources"
    ]
    if not list_fields:
        warnings.append("No list fields found — output may lack substantive citations.")
        return

    all_empty = all(len(output[k]) == 0 for k in list_fields)
    if all_empty:
        warnings.append(
            f"All list fields ({', '.join(list_fields)}) are empty — no citations or items."
        )


# ─── Public API ───────────────────────────────────────────────────────────────

def validate(agent_name: str, output: Any) -> ValidationResult:
    """
    Validate the output dict of an agent.

    Parameters
    ----------
    agent_name : str
        The pipeline key for the agent (e.g. "research", "competitor", "idea_guard").
        Unknown agent names are validated with basic checks only.
    output : Any
        The dict returned by the agent's run() function.

    Returns
    -------
    ValidationResult
        .status  → "pass" or "warning"
        .warnings → list of human-readable warning strings (empty when status="pass")
    """
    warnings: List[str] = []

    # 1. Parse-error / type check (fatal — skip further checks)
    if _check_parse_error(output, warnings):
        return ValidationResult(status="warning", warnings=warnings)

    schema = _SCHEMAS.get(agent_name)

    if schema is None:
        # Unknown agent: only basic checks
        warnings.append(
            f"No schema registered for agent '{agent_name}' — basic checks only."
        )
        _check_sources(output, warnings) if "sources" in output else None
        _check_citations(output, warnings)
    else:
        # 2. Required fields
        _check_required_fields(output, schema["required"], warnings)

        # 3. Score range validation
        _check_scores(output, schema["scores"], warnings)

        # 4. Sources (agents that do web search)
        if schema["sources"]:
            _check_sources(output, warnings)

        # 5. Citations (non-empty list fields)
        if schema["citations"]:
            _check_citations(output, warnings)

    status: Literal["pass", "warning"] = "warning" if warnings else "pass"
    return ValidationResult(status=status, warnings=warnings)


def validate_all(agent_outputs: Dict[str, Any]) -> Dict[str, ValidationResult]:
    """
    Validate every agent output in a final pipeline state dict.

    Parameters
    ----------
    agent_outputs : dict
        Keys are agent names, values are the dicts returned by each agent.
        Keys with None values are silently skipped (agent did not run).

    Returns
    -------
    dict[str, ValidationResult]
        One ValidationResult per non-None agent output.
    """
    results: Dict[str, ValidationResult] = {}
    for name, output in agent_outputs.items():
        if output is None or name in _NON_AGENT_KEYS:
            continue
        results[name] = validate(name, output)
    return results
