from __future__ import annotations

import io
from typing import Any, Dict

from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import (
    HRFlowable,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)


def _h(text: str, level: int, styles) -> Paragraph:
    return Paragraph(text, styles[{1: "Heading1", 2: "Heading2", 3: "Heading3"}.get(level, "Heading2")])


def _make_table(data: list, col_widths: list, header_color: str = "#4f46e5") -> Table:
    t = Table(data, colWidths=col_widths)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_color)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f9fafb")),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#d1d5db")),
        ("PADDING", (0, 0), (-1, -1), 5),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def generate_pdf_report(state: Dict[str, Any]) -> bytes:
    """Generate a structured PDF market intelligence report from the complete research state."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.75 * inch,
    )
    styles = getSampleStyleSheet()
    elements = []

    idea = state.get("idea", "")
    industry = state.get("industry", "")
    report = state.get("report") or {}
    innovation = state.get("innovation_score") or {}
    swot = state.get("swot") or {}
    risks = state.get("risks") or {}
    strategy = state.get("strategy") or {}
    competitors_data = state.get("competitors") or {}
    opportunities = state.get("opportunities") or {}
    validation = state.get("validation") or {}

    title_style = ParagraphStyle(
        "ReportTitle",
        parent=styles["Title"],
        textColor=colors.HexColor("#4f46e5"),
        spaceAfter=4,
        fontSize=18,
    )
    subtitle_style = ParagraphStyle(
        "Subtitle",
        parent=styles["Normal"],
        textColor=colors.HexColor("#6b7280"),
        fontSize=9,
        spaceAfter=2,
    )

    elements.append(Paragraph("MarketScout AI — Market Intelligence Report", title_style))
    elements.append(Paragraph(f"Idea: {idea}", subtitle_style))
    if industry:
        elements.append(Paragraph(f"Industry: {industry}", subtitle_style))
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4f46e5")))
    elements.append(Spacer(1, 0.15 * inch))

    # Innovation Score Panel
    score = innovation.get("innovation_score", "N/A")
    grade = innovation.get("grade", "")
    scores = innovation.get("scores", {})
    elements.append(_h("Innovation Score", 2, styles))
    score_data = [
        ["Metric", "Score"],
        ["Overall Innovation Score", f"{score} / 100  (Grade: {grade})"],
        ["Novelty", str(scores.get("novelty", "N/A"))],
        ["Market Opportunity (vs saturation)", str(scores.get("market_saturation", "N/A"))],
        ["Funding Activity", str(scores.get("funding_activity", "N/A"))],
        ["Research Maturity", str(scores.get("research_maturity", "N/A"))],
        ["IP White Space (vs patent density)", str(scores.get("patent_density", "N/A"))],
        ["Low Competition Bonus", str(scores.get("competition_level", "N/A"))],
    ]
    elements.append(_make_table(score_data, [3.5 * inch, 3 * inch]))
    if innovation.get("score_explanation"):
        elements.append(Spacer(1, 0.08 * inch))
        elements.append(Paragraph(innovation["score_explanation"], styles["Normal"]))
    elements.append(Spacer(1, 0.15 * inch))

    # Executive Summary
    elements.append(_h("Executive Summary", 2, styles))
    elements.append(Paragraph(report.get("executive_summary", ""), styles["Normal"]))
    elements.append(Spacer(1, 0.15 * inch))

    # Key Metrics
    metrics = report.get("key_metrics", {})
    if metrics:
        elements.append(_h("Key Metrics", 2, styles))
        metric_data = [["Metric", "Value"]] + [[k.replace("_", " ").title(), str(v)] for k, v in metrics.items()]
        elements.append(_make_table(metric_data, [3 * inch, 3.5 * inch], "#7c3aed"))
        elements.append(Spacer(1, 0.15 * inch))

    # Competitor Landscape
    comp_list = competitors_data.get("competitors", [])
    if comp_list:
        elements.append(_h("Competitor Landscape", 2, styles))
        comp_data = [["Company", "Market Share", "Threat", "Revenue"]]
        for c in comp_list[:8]:
            comp_data.append([
                c.get("name", ""),
                c.get("market_share", ""),
                c.get("threat_level", ""),
                c.get("revenue", ""),
            ])
        elements.append(_make_table(comp_data, [2.2 * inch, 1.5 * inch, 1.2 * inch, 1.6 * inch], "#dc2626"))
        elements.append(Spacer(1, 0.15 * inch))

    # SWOT Analysis
    if swot:
        elements.append(_h("SWOT Analysis", 2, styles))
        swot_data = [
            ["Strengths", "Weaknesses"],
            [
                "\n".join(f"+ {s}" for s in swot.get("strengths", [])),
                "\n".join(f"- {w}" for w in swot.get("weaknesses", [])),
            ],
            ["Opportunities", "Threats"],
            [
                "\n".join(f"+ {o}" for o in swot.get("opportunities", [])),
                "\n".join(f"! {t}" for t in swot.get("threats", [])),
            ],
        ]
        t_swot = Table(swot_data, colWidths=[3.375 * inch, 3.375 * inch])
        t_swot.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#dcfce7")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#fee2e2")),
            ("BACKGROUND", (0, 2), (0, 2), colors.HexColor("#dbeafe")),
            ("BACKGROUND", (1, 2), (1, 2), colors.HexColor("#fef9c3")),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTNAME", (0, 2), (-1, 2), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#d1d5db")),
            ("PADDING", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        elements.append(t_swot)
        elements.append(Spacer(1, 0.15 * inch))

    # Strategic Recommendations
    recs = report.get("recommendations") or strategy.get("strategic_recommendations", [])
    if recs:
        elements.append(_h("Strategic Recommendations", 2, styles))
        for rec in recs:
            elements.append(Paragraph(f"• {rec}", styles["Normal"]))
        elements.append(Spacer(1, 0.12 * inch))

    # Go-to-Market
    gtm = strategy.get("go_to_market", "")
    if gtm:
        elements.append(_h("Go-to-Market Strategy", 2, styles))
        elements.append(Paragraph(gtm, styles["Normal"]))
        elements.append(Spacer(1, 0.12 * inch))

    # Roadmap
    roadmap = strategy.get("roadmap", {})
    if roadmap:
        elements.append(_h("Execution Roadmap", 2, styles))
        roadmap_data = [["Phase", "Actions"]]
        for phase, actions in roadmap.items():
            label = phase.replace("_", " ").title()
            roadmap_data.append([label, "\n".join(f"• {a}" for a in (actions or []))])
        elements.append(_make_table(roadmap_data, [2 * inch, 4.75 * inch], "#0891b2"))
        elements.append(Spacer(1, 0.12 * inch))

    # Risk Assessment
    risk_list = risks.get("risks", [])
    if risk_list:
        elements.append(_h("Risk Assessment", 2, styles))
        risk_data = [["Risk", "Severity", "Probability", "Mitigation"]]
        for r in risk_list[:7]:
            risk_data.append([
                r.get("name", ""),
                r.get("severity", ""),
                r.get("probability", ""),
                r.get("mitigation", ""),
            ])
        elements.append(_make_table(risk_data, [1.5 * inch, 1 * inch, 1 * inch, 3.25 * inch], "#b91c1c"))
        elements.append(Spacer(1, 0.12 * inch))

    # Innovation Hypotheses
    hypotheses = strategy.get("innovation_hypotheses", [])
    if hypotheses:
        elements.append(_h("Innovation Hypotheses", 2, styles))
        for h in hypotheses:
            if isinstance(h, dict):
                elements.append(Paragraph(
                    f"• <b>[{h.get('type', '').upper()}]</b> {h.get('hypothesis', '')} — "
                    f"<i>{h.get('rationale', '')}</i>",
                    styles["Normal"],
                ))
            else:
                elements.append(Paragraph(f"• {h}", styles["Normal"]))
        elements.append(Spacer(1, 0.12 * inch))

    # Validation Summary
    if validation.get("confidence_level"):
        elements.append(_h("Validation & Confidence", 2, styles))
        elements.append(Paragraph(
            f"<b>Confidence Level:</b> {validation.get('confidence_level', '').upper()}",
            styles["Normal"],
        ))
        if validation.get("recommendation"):
            elements.append(Paragraph(
                f"<b>Recommendation:</b> {validation['recommendation']}",
                styles["Normal"],
            ))
        elements.append(Spacer(1, 0.12 * inch))

    # Footer
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#9ca3af")))
    elements.append(Spacer(1, 0.06 * inch))
    elements.append(Paragraph(
        "Generated by MarketScout AI  ·  Powered by AMD Instinct GPUs via Fireworks AI",
        ParagraphStyle(
            "Footer",
            parent=styles["Normal"],
            textColor=colors.HexColor("#9ca3af"),
            fontSize=7,
            alignment=1,
        ),
    ))

    doc.build(elements)
    return buffer.getvalue()
