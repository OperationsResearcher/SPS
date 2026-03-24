from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer


SRC = Path("c:/kokpitim/docs/yetki-smoke-test-checklist.md")
DST = Path("c:/kokpitim/docs/yetki-smoke-test-checklist.pdf")


def _parse_markdown_lines(text: str):
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            yield ("blank", "")
            continue
        if line.startswith("# "):
            yield ("h1", line[2:].strip())
        elif line.startswith("## "):
            yield ("h2", line[3:].strip())
        elif line.startswith("- [ ] "):
            yield ("check", line[6:].strip())
        elif line.startswith("- "):
            yield ("bullet", line[2:].strip())
        else:
            yield ("p", line)


def build_pdf():
    text = SRC.read_text(encoding="utf-8")

    doc = SimpleDocTemplate(
        str(DST),
        pagesize=A4,
        leftMargin=2.0 * cm,
        rightMargin=2.0 * cm,
        topMargin=1.8 * cm,
        bottomMargin=1.8 * cm,
        title="Yetki Smoke Test Checklist",
    )

    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(
        "H1",
        parent=styles["Heading1"],
        fontName="Helvetica-Bold",
        fontSize=18,
        leading=22,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=10,
    )
    h2 = ParagraphStyle(
        "H2",
        parent=styles["Heading2"],
        fontName="Helvetica-Bold",
        fontSize=13,
        leading=16,
        textColor=colors.HexColor("#1e293b"),
        spaceBefore=10,
        spaceAfter=6,
    )
    p = ParagraphStyle(
        "P",
        parent=styles["BodyText"],
        fontName="Helvetica",
        fontSize=10.5,
        leading=14.5,
        alignment=TA_LEFT,
        textColor=colors.HexColor("#334155"),
        spaceAfter=4,
    )
    bullet = ParagraphStyle(
        "B",
        parent=p,
        leftIndent=14,
        bulletIndent=2,
        spaceAfter=2,
    )
    check = ParagraphStyle(
        "C",
        parent=p,
        leftIndent=14,
        bulletIndent=2,
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=2,
    )
    cover_sub = ParagraphStyle(
        "CoverSub",
        parent=p,
        fontSize=11,
        leading=15,
        textColor=colors.HexColor("#64748b"),
        spaceAfter=0,
    )

    flow = []
    flow.append(Paragraph("Yetki Smoke Test Checklist", h1))
    flow.append(
        Paragraph(
            "Süreçler, PG, PGV, Süreç Faaliyetleri ve Projeler için "
            "rol bazlı hızlı doğrulama dokümanı.",
            cover_sub,
        )
    )
    flow.append(Spacer(1, 12))

    first_h1_skipped = False
    for kind, val in _parse_markdown_lines(text):
        if kind == "h1":
            if not first_h1_skipped:
                first_h1_skipped = True
                continue
            flow.append(Paragraph(val, h1))
        elif kind == "h2":
            flow.append(Paragraph(val, h2))
        elif kind == "bullet":
            flow.append(Paragraph(val, bullet, bulletText="\u2022"))
        elif kind == "check":
            flow.append(Paragraph(val, check, bulletText="\u2610"))
        elif kind == "p":
            flow.append(Paragraph(val, p))
        elif kind == "blank":
            flow.append(Spacer(1, 4))

    doc.build(flow)


if __name__ == "__main__":
    build_pdf()
