from __future__ import annotations

import io
from typing import Any, Dict, Iterable
from xml.sax.saxutils import escape

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

INK = colors.HexColor("#1f2937")
MUTED = colors.HexColor("#6b7280")
BORDER = colors.HexColor("#e5e7eb")
ZEBRA = colors.HexColor("#f9fafb")


def _esc(text: Any) -> str:
    """Escape raw LLM/user text for ReportLab's mini-XML Paragraph parser."""
    return escape(str(text)) if text is not None else ""


def _cell(text: Any, style: ParagraphStyle) -> Paragraph:
    """Wrap table-cell text in a Paragraph so it word-wraps and honors line
    breaks — plain strings in a reportlab Table neither wrap nor turn "\\n"
    into real line breaks, which is what made every table in this report
    overflow its column or run all bullet points together on one line."""
    body = _esc(text).replace("\n", "<br/>")
    return Paragraph(body, style)


def _bullets(items: Iterable[str], style: ParagraphStyle, prefix: str = "•") -> Paragraph:
    lines = [f"{prefix} {_esc(item)}" for item in items if item]
    return Paragraph("<br/>".join(lines) if lines else "—", style)


def _make_table(data: list, col_widths: list, header_color: str) -> Table:
    t = Table(data, colWidths=col_widths, repeatRows=1)
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(header_color)),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, ZEBRA]),
        ("GRID", (0, 0), (-1, -1), 0.4, BORDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    return t


def generate_pdf_report(state: Dict[str, Any]) -> bytes:
    """Generate a structured, print-friendly PDF market intelligence report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=0.75 * inch,
        leftMargin=0.75 * inch,
        topMargin=0.75 * inch,
        bottomMargin=0.7 * inch,
        title="MarketScout AI — Market Intelligence Report",
    )
    styles = getSampleStyleSheet()

    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=9.5, leading=14, textColor=INK, spaceAfter=4)
    cell = ParagraphStyle("Cell", parent=styles["Normal"], fontSize=8.5, leading=12, textColor=INK)
    cell_header_label = ParagraphStyle("CellLabel", parent=cell, fontName="Helvetica-Bold")
    bullet = ParagraphStyle("Bullet", parent=body, spaceAfter=6)
    h2 = ParagraphStyle(
        "H2", parent=styles["Heading2"], fontSize=13.5, textColor=colors.HexColor("#4f46e5"),
        spaceBefore=14, spaceAfter=8, borderPadding=0,
    )
    title_style = ParagraphStyle("ReportTitle", parent=styles["Title"], textColor=colors.HexColor("#4f46e5"), fontSize=19, spaceAfter=3)
    subtitle_style = ParagraphStyle("Subtitle", parent=styles["Normal"], textColor=MUTED, fontSize=9.5, spaceAfter=2)
    score_headline = ParagraphStyle("ScoreHeadline", parent=styles["Normal"], fontSize=26, textColor=colors.HexColor("#4f46e5"), fontName="Helvetica-Bold")
    score_caption = ParagraphStyle("ScoreCaption", parent=styles["Normal"], fontSize=8.5, textColor=MUTED)

    idea = state.get("idea", "")
    industry = state.get("industry", "")
    report = state.get("report") or {}
    innovation = state.get("innovation_score") or {}
    swot = state.get("swot") or {}
    risks = state.get("risks") or {}
    strategy = state.get("strategy") or {}
    competitors_data = state.get("competitors") or {}
    validation = state.get("validation") or {}

    elements: list = []

    # ── Header ──
    elements.append(Paragraph("MarketScout AI", title_style))
    elements.append(Paragraph("Market Intelligence Report", subtitle_style))
    elements.append(Spacer(1, 0.1 * inch))
    header_rows = [[_cell(f"Idea: {idea}", body)]]
    if industry:
        header_rows.append([_cell(f"Industry: {industry}", body)])
    elements.append(Table(header_rows, colWidths=[6.5 * inch], style=TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("TOPPADDING", (0, 0), (-1, -1), 1), ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
    ])))
    elements.append(Spacer(1, 0.12 * inch))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#4f46e5")))
    elements.append(Spacer(1, 0.18 * inch))

    # ── Innovation Score Panel ──
    score = innovation.get("innovation_score", "N/A")
    grade = innovation.get("grade", "")
    scores = innovation.get("scores", {})
    elements.append(Table(
        [[
            Paragraph(f"{score}<font size=12>/100</font>", score_headline),
            _cell(f"Grade {grade}\nOverall Innovation Score", score_caption),
        ]],
        colWidths=[1.6 * inch, 5 * inch],
        style=TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LEFTPADDING", (0, 0), (-1, -1), 0)]),
    ))
    elements.append(Spacer(1, 0.1 * inch))
    score_data = [
        ["Metric", "Score"],
        ["Novelty", str(scores.get("novelty", "N/A"))],
        ["Market Opportunity (vs saturation)", str(scores.get("market_saturation", "N/A"))],
        ["Funding Activity", str(scores.get("funding_activity", "N/A"))],
        ["Research Maturity", str(scores.get("research_maturity", "N/A"))],
        ["IP White Space (vs patent density)", str(scores.get("patent_density", "N/A"))],
        ["Low Competition Bonus", str(scores.get("competition_level", "N/A"))],
    ]
    elements.append(_make_table(score_data, [4.5 * inch, 2 * inch], "#4f46e5"))
    if innovation.get("score_explanation"):
        elements.append(Spacer(1, 0.08 * inch))
        elements.append(_cell(innovation["score_explanation"], body))
    elements.append(Spacer(1, 0.1 * inch))

    # ── Executive Summary ──
    if report.get("executive_summary"):
        elements.append(Paragraph("Executive Summary", h2))
        elements.append(_cell(report["executive_summary"], body))

    # ── Key Metrics ──
    metrics = report.get("key_metrics", {})
    if metrics:
        elements.append(Paragraph("Key Metrics", h2))
        metric_data = [["Metric", "Value"]] + [
            [k.replace("_", " ").title(), _cell(v, cell)] for k, v in metrics.items()
        ]
        elements.append(_make_table(metric_data, [2.3 * inch, 4.2 * inch], "#7c3aed"))

    # ── Competitor Landscape ──
    comp_list = competitors_data.get("competitors", [])
    if comp_list:
        elements.append(Paragraph("Competitor Landscape", h2))
        comp_data = [["Company", "Market Share", "Threat", "Revenue"]]
        for c in comp_list[:8]:
            comp_data.append([
                _cell(c.get("name", ""), cell_header_label),
                _cell(c.get("market_share", ""), cell),
                _cell(c.get("threat_level", ""), cell),
                _cell(c.get("revenue", ""), cell),
            ])
        elements.append(_make_table(comp_data, [2.1 * inch, 1.5 * inch, 1.1 * inch, 1.8 * inch], "#dc2626"))

    # ── SWOT Analysis ──
    if swot and any(swot.get(k) for k in ("strengths", "weaknesses", "opportunities", "threats")):
        elements.append(Paragraph("SWOT Analysis", h2))
        swot_data = [
            [_cell("Strengths", cell_header_label), _cell("Weaknesses", cell_header_label)],
            [_bullets(swot.get("strengths", []), cell, "+"), _bullets(swot.get("weaknesses", []), cell, "−")],
            [_cell("Opportunities", cell_header_label), _cell("Threats", cell_header_label)],
            [_bullets(swot.get("opportunities", []), cell, "+"), _bullets(swot.get("threats", []), cell, "!")],
        ]
        t_swot = Table(swot_data, colWidths=[3.25 * inch, 3.25 * inch])
        t_swot.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (0, 0), colors.HexColor("#dcfce7")),
            ("BACKGROUND", (1, 0), (1, 0), colors.HexColor("#fee2e2")),
            ("BACKGROUND", (0, 2), (0, 2), colors.HexColor("#dbeafe")),
            ("BACKGROUND", (1, 2), (1, 2), colors.HexColor("#fef9c3")),
            ("GRID", (0, 0), (-1, -1), 0.5, BORDER),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 7),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        elements.append(t_swot)

    # ── Strategic Recommendations ──
    recs = report.get("recommendations") or strategy.get("strategic_recommendations", [])
    if recs:
        elements.append(Paragraph("Strategic Recommendations", h2))
        for rec in recs:
            elements.append(Paragraph(f"• {_esc(rec)}", bullet))

    # ── Go-to-Market ──
    gtm = strategy.get("go_to_market", "")
    if gtm:
        elements.append(Paragraph("Go-to-Market Strategy", h2))
        elements.append(_cell(gtm, body))

    # ── Roadmap ──
    roadmap = strategy.get("roadmap", {})
    if roadmap:
        elements.append(Paragraph("Execution Roadmap", h2))
        roadmap_data = [["Phase", "Actions"]]
        for phase, actions in roadmap.items():
            label = phase.replace("_", " ").title()
            roadmap_data.append([_cell(label, cell_header_label), _bullets(actions or [], cell)])
        elements.append(_make_table(roadmap_data, [1.6 * inch, 5 * inch], "#0891b2"))

    # ── Risk Assessment ──
    risk_list = risks.get("risks", [])
    if risk_list:
        elements.append(Paragraph("Risk Assessment", h2))
        risk_data = [["Risk", "Severity", "Probability", "Mitigation"]]
        for r in risk_list[:7]:
            risk_data.append([
                _cell(r.get("name", ""), cell_header_label),
                _cell(r.get("severity", ""), cell),
                _cell(r.get("probability", ""), cell),
                _cell(r.get("mitigation", ""), cell),
            ])
        elements.append(_make_table(risk_data, [1.4 * inch, 0.85 * inch, 0.95 * inch, 3.3 * inch], "#b91c1c"))

    # ── Innovation Hypotheses ──
    hypotheses = strategy.get("innovation_hypotheses", [])
    if hypotheses:
        elements.append(Paragraph("Innovation Hypotheses", h2))
        for h in hypotheses:
            if isinstance(h, dict):
                elements.append(Paragraph(
                    f"• <b>[{_esc(h.get('type', '').upper())}]</b> {_esc(h.get('hypothesis', ''))} — "
                    f"<i>{_esc(h.get('rationale', ''))}</i>",
                    bullet,
                ))
            else:
                elements.append(Paragraph(f"• {_esc(h)}", bullet))

    # ── Validation Summary ──
    if validation.get("confidence_level"):
        elements.append(Paragraph("Validation & Confidence", h2))
        elements.append(Paragraph(
            f"<b>Confidence Level:</b> {_esc(validation.get('confidence_level', '').upper())}",
            body,
        ))
        if validation.get("recommendation"):
            elements.append(Paragraph(
                f"<b>Recommendation:</b> {_esc(validation['recommendation'])}",
                body,
            ))

    # ── Footer ──
    elements.append(Spacer(1, 0.15 * inch))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#9ca3af")))
    elements.append(Spacer(1, 0.06 * inch))
    elements.append(Paragraph(
        "Generated by MarketScout AI &middot; Powered by AMD Instinct GPUs via Fireworks AI",
        ParagraphStyle("Footer", parent=styles["Normal"], textColor=MUTED, fontSize=7, alignment=1),
    ))

    def _footer(canvas, doc_):
        canvas.saveState()
        canvas.setFont("Helvetica", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawRightString(doc_.pagesize[0] - 0.75 * inch, 0.4 * inch, f"Page {doc_.page}")
        canvas.restoreState()

    doc.build(elements, onFirstPage=_footer, onLaterPages=_footer)
    return buffer.getvalue()
