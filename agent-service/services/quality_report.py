"""
Quality Report
==============
Produces a holistic quality assessment of the full pipeline output by
combining the Output Validator, Confidence Engine, and Source Ranker.

The report contains four dimensions:

    pipeline_quality    – float 0.0–1.0   overall weighted agent quality
    hallucination_risk  – "low" | "medium" | "high"
    missing_evidence    – list of agents with incomplete / missing outputs
    consistency         – float 0.0–1.0   cross-agent score agreement

Plus top-level metadata:
    overall_grade   – "A" | "B" | "C" | "D" | "F"
    agent_scores    – per-agent confidence scores
    warnings        – all validation warnings collected
    summary         – one-sentence human-readable description

Rules
-----
- Read-only: pipeline state is never modified.
- No LLM calls: deterministic aggregation of existing services.
- Imports: output_validator, confidence, source_ranker only.

Usage
-----
    from services.quality_report import generate, QualityReport

    report = generate(pipeline_state)
    print(report.overall_grade)          # "B"
    print(report.pipeline_quality)       # 0.74
    print(report.hallucination_risk)     # "low"
    print(report.missing_evidence)       # ["scientific", "patent"]
    print(report.consistency)            # 0.81
    print(report.summary)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional

from services.confidence import assess_all
from services.output_validator import validate_all
from services.source_ranker import average_credibility, rank_all


# ─── Types ────────────────────────────────────────────────────────────────────

HallucinationRisk = Literal["low", "medium", "high"]
QualityGrade      = Literal["A", "B", "C", "D", "F"]

# Agents that carry numeric scores — keyed by ACTUAL ResearchState field name
_SCORE_FIELDS: Dict[str, str] = {
    "competitors":         "market_saturation_score",
    "scientific":         "research_maturity_score",
    "patents":            "patent_density_score",
    "funding":            "funding_activity_score",
    "research_gaps":      "novelty_score",
    "opportunities":      "opportunity_score",
    "risks":              "risk_score",
    "innovation_score":   "innovation_score",
    "report":             "market_score",
}

# Agents considered core — missing one raises hallucination risk
# Uses ACTUAL ResearchState field names
_CORE_AGENTS = {
    "research", "competitors", "scientific", "patents",
    "funding", "trends", "research_gaps", "swot",
    "opportunities", "risks", "innovation_score",
    "validation", "strategy", "report",
}

# Weight per agent for pipeline_quality
_AGENT_WEIGHTS: Dict[str, float] = {
    "research":           1.5,
    "competitors":        1.2,
    "scientific":         1.0,
    "patents":            0.8,
    "funding":            1.0,
    "trends":             0.8,
    "research_gaps":      1.0,
    "swot":               1.0,
    "opportunities":      1.2,
    "risks":              1.2,
    "innovation_score":   1.0,
    "validation":         1.0,
    "strategy":           1.0,
    "report":             1.5,
}


@dataclass(frozen=True)
class QualityReport:
    pipeline_quality:   float
    hallucination_risk: HallucinationRisk
    missing_evidence:   List[str]
    consistency:        float
    overall_grade:      QualityGrade
    agent_scores:       Dict[str, float]
    source_credibility: float
    warnings:           List[str]
    summary:            str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "pipeline_quality":   self.pipeline_quality,
            "hallucination_risk": self.hallucination_risk,
            "missing_evidence":   list(self.missing_evidence),
            "consistency":        self.consistency,
            "overall_grade":      self.overall_grade,
            "agent_scores":       dict(self.agent_scores),
            "source_credibility": self.source_credibility,
            "warnings":           list(self.warnings),
            "summary":            self.summary,
        }


# ─── Internal helpers ─────────────────────────────────────────────────────────

def _safe_float(value: Any, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _grade(score: float) -> QualityGrade:
    if score >= 0.85:
        return "A"
    if score >= 0.70:
        return "B"
    if score >= 0.55:
        return "C"
    if score >= 0.40:
        return "D"
    return "F"


def _hallucination_risk(
    missing_count: int,
    avg_confidence: float,
    avg_source_credibility: float,
    validation_warnings: int,
) -> HallucinationRisk:
    """
    Heuristic:
      - Many missing agents → high
      - Low confidence + low source credibility → high
      - Moderate gaps → medium
      - Strong coverage + credible sources → low
    """
    risk_score = 0.0

    if missing_count >= 5:
        risk_score += 0.5
    elif missing_count >= 2:
        risk_score += 0.25

    if avg_confidence < 0.40:
        risk_score += 0.35
    elif avg_confidence < 0.60:
        risk_score += 0.15

    if avg_source_credibility < 0.30:
        risk_score += 0.25
    elif avg_source_credibility < 0.50:
        risk_score += 0.10

    if validation_warnings >= 10:
        risk_score += 0.20
    elif validation_warnings >= 5:
        risk_score += 0.10

    if risk_score >= 0.50:
        return "high"
    if risk_score >= 0.20:
        return "medium"
    return "low"


def _compute_consistency(agent_outputs: Dict[str, Any]) -> float:
    """
    Cross-agent score consistency: measure the coefficient of variation
    of the numeric scores across agents (lower CV → higher consistency).

    Returns 0.0 (no data) to 1.0 (perfect agreement).
    """
    scores: List[float] = []
    for agent, field in _SCORE_FIELDS.items():
        output = agent_outputs.get(agent)
        if not isinstance(output, dict):
            continue
        val = output.get(field)
        if val is None:
            continue
        try:
            scores.append(float(val))
        except (TypeError, ValueError):
            pass

    if len(scores) < 2:
        return 1.0  # insufficient data → assume consistent

    mean = sum(scores) / len(scores)
    if mean == 0:
        return 1.0

    variance = sum((s - mean) ** 2 for s in scores) / len(scores)
    std_dev  = variance ** 0.5
    cv       = std_dev / mean   # coefficient of variation

    # CV = 0 → perfect consistency (1.0); CV ≥ 1 → very inconsistent (0.0)
    consistency = max(0.0, 1.0 - cv)
    return round(min(1.0, consistency), 4)


def _collect_sources(agent_outputs: Dict[str, Any]) -> List[str]:
    """Collect all source URLs from all agent outputs."""
    urls: List[str] = []
    for output in agent_outputs.values():
        if not isinstance(output, dict):
            continue
        sources = output.get("sources", [])
        if isinstance(sources, list):
            urls.extend(s for s in sources if isinstance(s, str))
    return urls


# ─── Public API ───────────────────────────────────────────────────────────────

def generate(agent_outputs: Dict[str, Any]) -> QualityReport:
    """
    Generate a QualityReport from the pipeline state dict.

    Parameters
    ----------
    agent_outputs : dict
        The full pipeline state keyed by agent name.
        Non-agent keys (job_id, idea, …) are silently ignored.

    Returns
    -------
    QualityReport
    """
    # ── 1. Confidence scores ─────────────────────────────────────────────────
    confidence_results = assess_all(agent_outputs)
    agent_scores: Dict[str, float] = {
        name: result.confidence
        for name, result in confidence_results.items()
    }

    # ── 2. Validation warnings ───────────────────────────────────────────────
    validation_results = validate_all(agent_outputs)
    all_warnings: List[str] = []
    for agent_name, vr in validation_results.items():
        for w in vr.warnings:
            all_warnings.append(f"[{agent_name}] {w}")

    # ── 3. Missing evidence ──────────────────────────────────────────────────
    missing: List[str] = []
    for agent in _CORE_AGENTS:
        output = agent_outputs.get(agent)
        if output is None:
            missing.append(agent)
        elif isinstance(output, dict) and output.get("parse_error"):
            missing.append(agent)

    # ── 4. Pipeline quality (weighted average confidence) ────────────────────
    weighted_sum  = 0.0
    weight_total  = 0.0
    for agent, score in agent_scores.items():
        w = _AGENT_WEIGHTS.get(agent, 1.0)
        weighted_sum  += score * w
        weight_total  += w

    pipeline_quality = round(weighted_sum / weight_total, 4) if weight_total > 0 else 0.0

    # ── 5. Source credibility ────────────────────────────────────────────────
    all_urls       = _collect_sources(agent_outputs)
    source_cred    = average_credibility(all_urls) if all_urls else 0.0

    # ── 6. Consistency ───────────────────────────────────────────────────────
    consistency = _compute_consistency(agent_outputs)

    # ── 7. Hallucination risk ────────────────────────────────────────────────
    avg_confidence = (sum(agent_scores.values()) / len(agent_scores)
                      if agent_scores else 0.0)
    hall_risk = _hallucination_risk(
        missing_count          = len(missing),
        avg_confidence         = avg_confidence,
        avg_source_credibility = source_cred,
        validation_warnings    = len(all_warnings),
    )

    # ── 8. Overall grade ─────────────────────────────────────────────────────
    # Combine quality, consistency, and penalise for missing evidence
    missing_penalty = min(0.30, len(missing) * 0.05)
    composite = pipeline_quality * 0.60 + consistency * 0.40 - missing_penalty
    grade = _grade(max(0.0, composite))

    # ── 9. Summary ───────────────────────────────────────────────────────────
    risk_label = {"low": "low hallucination risk",
                  "medium": "medium hallucination risk",
                  "high": "HIGH hallucination risk"}[hall_risk]
    summary = (
        f"Pipeline quality {pipeline_quality:.0%} (grade {grade}), "
        f"{len(missing)} missing agent(s), "
        f"{risk_label}, "
        f"source credibility {source_cred:.0%}, "
        f"cross-agent consistency {consistency:.0%}."
    )

    return QualityReport(
        pipeline_quality   = pipeline_quality,
        hallucination_risk = hall_risk,
        missing_evidence   = missing,
        consistency        = consistency,
        overall_grade      = grade,
        agent_scores       = agent_scores,
        source_credibility = source_cred,
        warnings           = all_warnings,
        summary            = summary,
    )
