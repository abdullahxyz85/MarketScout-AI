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
    scores = innovation.get("scores") or {}
    breakdown_map = {d["dimension"]: d for d in (innovation.get("score_breakdown") or [])}

    def _fmt_score(key: str) -> str:
        """Format a score value: show adjusted value or NULL/N/A with evidence quality."""
        val = scores.get(key)
        dim = breakdown_map.get(key, {})
        status = dim.get("status", "")
        raw = dim.get("raw_value")
        eq = dim.get("evidence_quality", "")
        if val is not None:
            label = f"{val:.0f}/100"
            if eq and eq not in ("high", ""):
                label += f" ({eq})"
            return label
        if status == "agent_failed":
            return "Agent failed"
        if raw is None:
            return "N/A"
        return f"NULL ({status})"

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
        ["Novelty",                             _fmt_score("novelty")],
        ["Market Opportunity (vs saturation)",  _fmt_score("market_opp")],
        ["Funding Activity",                    _fmt_score("funding")],
        ["Research Maturity",                   _fmt_score("research_maturity")],
        ["IP White Space (vs patent density)",  _fmt_score("ip_space")],
        ["Low Competition Bonus",               _fmt_score("opportunity_boost")],
    ]
    elements.append(_make_table(score_data, [4.5 * inch, 2 * inch], "#4f46e5"))
    if innovation.get("score_explanation"):
        elements.append(Spacer(1, 0.08 * inch))
        elements.append(_cell(innovation["score_explanation"], body))
    is_prov = innovation.get("is_provisional", False)
    coverage = innovation.get("score_coverage", 1.0)
    if is_prov or coverage < 1.0:
        elements.append(Spacer(1, 0.04 * inch))
        prov_note = f"Coverage: {coverage:.0%}"
        if is_prov:
            prov_note += " — PROVISIONAL (insufficient data for full assessment)"
        elements.append(_cell(prov_note, ParagraphStyle("Prov", parent=body, textColor=MUTED, fontSize=8)))
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
    comp_list = competitors_data.get("competitors") or []
    if comp_list:
        elements.append(Paragraph("Competitor Landscape", h2))
        comp_data = [["Company", "Description", "Threat", "Market Share / Revenue"]]
        for c in comp_list[:8]:
            name = c.get("name") or "—"
            desc = c.get("description") or "—"
            threat = c.get("threat_level") or "—"
            ms = c.get("market_share") or "N/A"
            rev = c.get("revenue") or "N/A"
            ms_rev = f"Share: {ms}\nRev: {rev}"
            comp_data.append([
                _cell(name, cell_header_label),
                _cell(desc, cell),
                _cell(threat, cell),
                _cell(ms_rev, cell),
            ])
        elements.append(_make_table(comp_data, [1.6 * inch, 2.6 * inch, 0.9 * inch, 1.4 * inch], "#dc2626"))

    # ── SWOT Analysis ──
    if swot and any((swot.get(k) or []) for k in ("strengths", "weaknesses", "opportunities", "threats")):
        elements.append(Paragraph("SWOT Analysis", h2))
        swot_data = [
            [_cell("Strengths", cell_header_label), _cell("Weaknesses", cell_header_label)],
            [_bullets(swot.get("strengths") or [], cell, "+"), _bullets(swot.get("weaknesses") or [], cell, "−")],
            [_cell("Opportunities", cell_header_label), _cell("Threats", cell_header_label)],
            [_bullets(swot.get("opportunities") or [], cell, "+"), _bullets(swot.get("threats") or [], cell, "!")],
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

    # ── Sources & References ──
    source_sections = [
        ("Market Research",   (state.get("research")       or {}).get("sources") or []),
        ("Competitors",       (state.get("competitors")     or {}).get("sources") or []),
        ("Scientific Papers", (state.get("scientific")      or {}).get("sources") or []),
        ("Patents",           (state.get("patents")         or {}).get("sources") or []),
        ("Funding",           (state.get("funding")         or {}).get("sources") or []),
        ("Trends",            (state.get("trends")          or {}).get("sources") or []),
        ("Market Gaps",       (state.get("research_gaps")   or {}).get("sources") or []),
    ]
    all_sources = [(label, url) for label, urls in source_sections for url in urls
                   if url and not url.startswith("https://mock-research.example.com")]
    if all_sources:
        elements.append(Paragraph("Sources &amp; References", h2))
        seen_urls: set = set()
        for label, url in all_sources:
            if url in seen_urls:
                continue
            seen_urls.add(url)
            elements.append(Paragraph(
                f'<font color="#6b7280">[{_esc(label)}]</font> '
                f'<a href="{_esc(url)}" color="#4f46e5">{_esc(url)}</a>',
                ParagraphStyle("SourceLink", parent=body, fontSize=8, leading=11, spaceAfter=2),
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
