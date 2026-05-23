"""PDF export utility (Sprint 8).

Audit (PROJE-AUDIT-2026Q2.md) bulgu: k_rapor, bireysel, proje modüllerinde
PDF export hiçbir yerde yok. Sadece Excel var.

Bu modül reportlab kullanarak basit ama production-ready PDF üretir.
Daha karmaşık layout için ileride weasyprint eklenebilir (HTML → PDF).
"""
from __future__ import annotations

from io import BytesIO
from typing import Iterable, Optional

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)


def make_pdf(
    title: str,
    sections: list[dict],
    tenant_name: Optional[str] = None,
    footer: Optional[str] = None,
) -> bytes:
    """Generic PDF üreticisi.

    Args:
        title: Belge başlığı (sayfa 1 ortalı)
        sections: [{"heading": "Başlık", "body": "metin" | None,
                    "table": [["A","B"], ["1","2"]] | None}, ...]
        tenant_name: Header'da kurum adı
        footer: Sayfa altı metni

    Returns:
        PDF bytes
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm,
        title=title,
    )

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "title", parent=styles["Title"],
        fontSize=18, leading=22, alignment=TA_CENTER, spaceAfter=12,
    )
    h2 = ParagraphStyle(
        "h2", parent=styles["Heading2"],
        fontSize=14, leading=18, spaceBefore=12, spaceAfter=6,
        textColor=colors.HexColor("#1a4d80"),
    )
    body = ParagraphStyle(
        "body", parent=styles["BodyText"],
        fontSize=10, leading=14, alignment=TA_LEFT,
    )
    meta = ParagraphStyle(
        "meta", parent=styles["Normal"],
        fontSize=9, leading=12, textColor=colors.grey, alignment=TA_CENTER,
    )

    flowables = []

    # Header
    if tenant_name:
        flowables.append(Paragraph(tenant_name, meta))
        flowables.append(Spacer(1, 0.3 * cm))

    flowables.append(Paragraph(title, title_style))
    flowables.append(Spacer(1, 0.5 * cm))

    # Sections
    for sec in sections:
        heading = sec.get("heading")
        body_text = sec.get("body")
        table = sec.get("table")
        page_break = sec.get("page_break", False)

        if heading:
            flowables.append(Paragraph(heading, h2))
        if body_text:
            # Birden fazla paragraf için \n\n ayır
            for para in str(body_text).split("\n\n"):
                if para.strip():
                    flowables.append(Paragraph(para.strip().replace("\n", "<br/>"), body))
                    flowables.append(Spacer(1, 0.2 * cm))
        if table:
            tbl = _build_table(table)
            flowables.append(tbl)
            flowables.append(Spacer(1, 0.4 * cm))
        if page_break:
            flowables.append(PageBreak())

    # Footer
    if footer:
        flowables.append(Spacer(1, 1 * cm))
        flowables.append(Paragraph(footer, meta))

    doc.build(flowables)
    return buf.getvalue()


def _build_table(data: list[list]) -> Table:
    """İlk satır header olarak formatlanır."""
    tbl = Table(data, repeatRows=1)
    style = TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a4d80")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 10),
        ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ("FONTSIZE", (0, 1), (-1, -1), 9),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f0f4f8")]),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#cccccc")),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ])
    tbl.setStyle(style)
    return tbl


def kvp_table(kvp: Iterable[tuple]) -> list[list]:
    """Anahtar-değer çiftlerini tablo formatına çevir.

    Kullanım:
        rows = kvp_table([("Süreç sayısı", 14), ("KPI sayısı", 50)])
        make_pdf(..., sections=[{"heading": "Özet", "table": rows}])
    """
    return [["Alan", "Değer"]] + [[str(k), str(v)] for k, v in kvp]
