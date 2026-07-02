"""Haftalık strateji digest — HTML + PDF üretimi (S63).

PDF üretimi için sırayla denenir:
  1. reportlab (saf Python, zengin görsel — grafikler, kurum logosu, i18n)
  2. weasyprint (HTML→PDF, fallback)
  3. düz HTML (PDF yok)
"""
from __future__ import annotations

import datetime as _dt
import io
import os

from flask import render_template_string, current_app
from flask_babel import gettext as _

from sqlalchemy import text

from extensions import db
from app.services.exec_dashboard_service import build_exec_snapshot


def _ini_status_label(code: str) -> str:
    labels = {
        "planned": _("Planlandı"),
        "in_progress": _("Devam Ediyor"),
        "completed": _("Tamamlandı"),
        "on_hold": _("Beklemede"),
        "cancelled": _("İptal"),
        "delayed": _("Gecikmiş"),
        "active": _("Aktif"),
    }
    return labels.get(code, code)


def _fetch_digest_extras(tenant_id: int) -> dict:
    """Haftalık rapor için ekstra veriler: top initiative, gecikmiş faaliyet, strateji-bazlı PG."""
    out = {"top_initiatives": [], "overdue_activities": [], "strategy_perf": []}

    # Top 5 girişim — ilerleme yüksekten düşüğe (planned/in_progress'leri öncele)
    try:
        rows = db.session.execute(text("""
            SELECT name, status, COALESCE(progress_pct, 0) as p
            FROM initiatives
            WHERE tenant_id=:t AND is_active=true AND COALESCE(status,'') != 'cancelled'
            ORDER BY (CASE status WHEN 'in_progress' THEN 0 WHEN 'planned' THEN 1 ELSE 2 END),
                     COALESCE(progress_pct, 0) DESC, id DESC
            LIMIT 5
        """), {"t": tenant_id}).fetchall()
        out["top_initiatives"] = [{"name": r.name, "status": r.status, "progress_pct": float(r.p or 0)} for r in rows]
    except Exception:
        pass

    # Top 5 gecikmiş faaliyet
    try:
        rows = db.session.execute(text("""
            SELECT a.name, a.end_date,
                   (CURRENT_DATE - a.end_date) as days_overdue,
                   p.name as process_name
            FROM process_activities a
            JOIN processes p ON p.id = a.process_id
            WHERE p.tenant_id=:t AND a.is_active=true
              AND a.status != 'Tamamlandı'
              AND a.end_date < CURRENT_DATE
            ORDER BY a.end_date ASC
            LIMIT 5
        """), {"t": tenant_id}).fetchall()
        out["overdue_activities"] = [
            {"name": r.name, "process_name": r.process_name,
             "end_date": r.end_date, "days_overdue": r.days_overdue}
            for r in rows
        ]
    except Exception:
        pass

    # Strateji bazlı PG performansı (aktif plan yıl)
    # Performans notu: önceki sürümde her PG için 2 korelasyonlu alt-sorgu vardı (N+1).
    # DISTINCT ON ile son kpi_data satırını TEK pass'ta alıyoruz (büyük tenantlarda ~30x hızlanma).
    try:
        rows = db.session.execute(text("""
            WITH latest_kd AS (
              SELECT DISTINCT ON (process_kpi_id)
                     process_kpi_id, actual_value, target_value, data_date
              FROM kpi_data
              WHERE is_active=true
              ORDER BY process_kpi_id, data_date DESC
            ),
            pgdata AS (
              SELECT s.id as strategy_id, s.code, s.title,
                     k.id as kid,
                     lkd.actual_value as last_actual,
                     lkd.target_value as last_target
              FROM strategies s
              JOIN sub_strategies ss ON ss.strategy_id = s.id AND ss.is_active=true
              JOIN process_sub_strategy_links psl ON psl.sub_strategy_id = ss.id
              JOIN processes p ON p.id = psl.process_id AND p.is_active=true
              JOIN process_kpis k ON k.process_id = p.id AND k.is_active=true
              LEFT JOIN latest_kd lkd ON lkd.process_kpi_id = k.id
              WHERE s.tenant_id=:t AND s.is_active=true
            )
            SELECT strategy_id, code, title,
                   count(DISTINCT kid) as total,
                   count(DISTINCT kid) FILTER (WHERE last_actual IS NOT NULL) as with_data,
                   sum(CASE WHEN last_actual ~ '^-?[0-9]+\\.?[0-9]*$'
                              AND last_target ~ '^-?[0-9]+\\.?[0-9]*$'
                              AND last_actual::float >= last_target::float
                            THEN 1 ELSE 0 END) as on_target,
                   sum(CASE WHEN last_actual ~ '^-?[0-9]+\\.?[0-9]*$'
                              AND last_target ~ '^-?[0-9]+\\.?[0-9]*$'
                            THEN 1 ELSE 0 END) as comparable
            FROM pgdata
            GROUP BY strategy_id, code, title
            ORDER BY code NULLS LAST, strategy_id
            LIMIT 10
        """), {"t": tenant_id}).fetchall()
        for r in rows:
            on_target_pct = (float(r.on_target) / r.comparable * 100) if r.comparable else None
            out["strategy_perf"].append({
                "code": r.code, "title": r.title,
                "total": int(r.total), "with_data": int(r.with_data),
                "on_target_pct": on_target_pct,
            })
    except Exception:
        pass

    return out


DIGEST_HTML = """
<!doctype html><html lang="{{ lang }}"><head><meta charset="utf-8">
<title>{{ _("Kokpitim Haftalık Strateji Raporu") }}</title>
<style>
  @page { size: A4; margin: 18mm; }
  body { font-family: -apple-system, Arial, sans-serif; color:#1e293b; }
  h1 { color: #0f172a; border-bottom: 3px solid #0ea5e9; padding-bottom: 8px; }
  h2 { color: #475569; margin-top: 24px; font-size: 16px; }
  .hero { background: linear-gradient(135deg,#1e293b,#334155); color:#fff; padding:18px; border-radius:8px; }
  .hero-score { font-size: 48px; font-weight: 800; }
  table { width: 100%; border-collapse: collapse; margin-top: 8px; font-size: 12px; }
  th, td { padding: 6px 10px; border-bottom: 1px solid #e2e8f0; text-align: left; }
  th { background: #f1f5f9; }
  .badge-ok { color: #059669; font-weight: 600; }
  .badge-warn { color: #d97706; font-weight: 600; }
  .badge-bad { color: #dc2626; font-weight: 600; }
  .footer { font-size: 10px; color: #94a3b8; margin-top: 30px; }
</style></head>
<body>
  <h1>{{ _("Kokpitim — Haftalık Strateji Raporu") }}</h1>
  <p style="color:#64748b;">{{ tenant_name }} • {{ generated_at }}</p>

  <div class="hero">
    <div style="font-size:11px; opacity:0.7; text-transform:uppercase;">{{ _("Strateji Sağlık Skoru") }}</div>
    <div class="hero-score">{{ snap.health_score or '—' }}</div>
    <div style="font-size:12px; opacity:0.8;">{{ _("%(year)s yılı", year=snap.year) }}</div>
  </div>

  <h2>📊 {{ _("Anahtar Göstergeler") }}</h2>
  <table>
    <tr><th>{{ _("Gösterge") }}</th><th>{{ _("Değer") }}</th><th>{{ _("Detay") }}</th></tr>
    <tr><td>{{ _("PG Hedef Üstü") }}</td>
        <td><span class="{{ 'badge-ok' if snap.kpi.on_target_pct>=70 else ('badge-warn' if snap.kpi.on_target_pct>=50 else 'badge-bad') }}">%{{ snap.kpi.on_target_pct }}</span></td>
        <td>{{ _("%(with)s / %(total)s PG'de veri", **{'with': snap.kpi.with_data, 'total': snap.kpi.total}) }}</td></tr>
    <tr><td>{{ _("Aktif Strateji / Alt") }}</td><td>{{ snap.strategy.count }} / {{ snap.strategy.sub_count }}</td><td>—</td></tr>
    <tr><td>{{ _("Toplam Girişim") }}</td><td>{{ snap.initiative.total }}</td><td>—</td></tr>
    <tr><td>{{ _("Gecikmiş Faaliyet") }}</td>
        <td><span class="{{ 'badge-bad' if snap.activity.overdue>5 else 'badge-ok' }}">{{ snap.activity.overdue }}</span></td>
        <td>{{ _("%(n)s toplam", n=snap.activity.total) }}</td></tr>
    <tr><td>{{ _("Kritik Risk") }}</td>
        <td><span class="{{ 'badge-bad' if snap.risk.critical>0 else 'badge-ok' }}">{{ snap.risk.critical }}</span></td>
        <td>{{ _("%(n)s açık risk", n=snap.risk.open) }}</td></tr>
    <tr><td>{{ _("Yüksek Anomali") }}</td>
        <td><span class="{{ 'badge-warn' if snap.anomaly.high>0 else 'badge-ok' }}">{{ snap.anomaly.high }}</span></td>
        <td>{{ _("%(n)s orta öncelikli", n=snap.anomaly.medium) }}</td></tr>
    <tr><td>{{ _("Tetikleyici Ateşlemesi (7g)") }}</td><td>{{ snap.trigger.fired_last_7d }}</td><td>{{ _("%(n)s aktif", n=snap.trigger.active) }}</td></tr>
  </table>

  <h2>🚀 {{ _("Girişim Durumu") }}</h2>
  <table>
    <tr><th>{{ _("Durum") }}</th><th>{{ _("Adet") }}</th><th>{{ _("Ortalama İlerleme") }}</th></tr>
    {% for st, info in snap.initiative.by_status.items() %}
    <tr><td>{{ status_labels.get(st, st) }}</td><td>{{ info.count }}</td><td>%{{ info.avg_progress|round(0)|int }}</td></tr>
    {% endfor %}
  </table>

  <div class="footer">
    {{ _("Bu rapor Kokpitim Stratejik Sağlık motoru tarafından otomatik üretildi.") }}
    {{ _("Sorularınız için: yönetim panelinize giriş yapın.") }}
  </div>
</body></html>
"""


def render_digest_html(tenant_id: int, tenant_name: str = None) -> str:
    if tenant_name is None:
        tenant_name = _("Kurumunuz")
    from flask_babel import get_locale
    snap = build_exec_snapshot(tenant_id)
    return render_template_string(
        DIGEST_HTML,
        snap=snap,
        tenant_name=tenant_name,
        generated_at=_dt.datetime.now().strftime("%d.%m.%Y %H:%M"),
        status_labels={k: _ini_status_label(k) for k in
                       ("planned", "in_progress", "completed", "on_hold", "cancelled", "delayed", "active")},
        lang=str(get_locale()),
    )


_FONT_REGISTERED = False
def _ensure_tr_font():
    """Türkçe karakter desteği için Arial TTF'yi kaydet (idempotent)."""
    global _FONT_REGISTERED
    if _FONT_REGISTERED:
        return ("Arial", "Arial-Bold", "Arial-Italic")
    try:
        import os
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfbase.pdfmetrics import registerFontFamily
        candidates = [
            (r"C:\Windows\Fonts\arial.ttf", r"C:\Windows\Fonts\arialbd.ttf", r"C:\Windows\Fonts\ariali.ttf"),
            ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
             "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
        ]
        for reg, bold, ital in candidates:
            if os.path.exists(reg) and os.path.exists(bold):
                pdfmetrics.registerFont(TTFont("Arial", reg))
                pdfmetrics.registerFont(TTFont("Arial-Bold", bold))
                if os.path.exists(ital):
                    pdfmetrics.registerFont(TTFont("Arial-Italic", ital))
                registerFontFamily("Arial", normal="Arial", bold="Arial-Bold",
                                   italic="Arial-Italic", boldItalic="Arial-Bold")
                _FONT_REGISTERED = True
                return ("Arial", "Arial-Bold", "Arial-Italic")
    except Exception:
        pass
    return ("Helvetica", "Helvetica-Bold", "Helvetica-Oblique")


def _tenant_logo_flowable(tenant, max_w=110, max_h=48):
    """Kurumun logo dosyasını varsa ReportLab Image flowable olarak döner, yoksa None."""
    if not tenant or not getattr(tenant, "logo_path", None):
        return None
    try:
        folder = os.path.join(current_app.instance_path, "uploads", "tenant_logos")
        path = os.path.join(folder, tenant.logo_path)
        if not os.path.isfile(path):
            return None
        from reportlab.platypus import Image
        from reportlab.lib.utils import ImageReader
        img_reader = ImageReader(path)
        iw, ih = img_reader.getSize()
        if not iw or not ih:
            return None
        scale = min(max_w / iw, max_h / ih, 1.0)
        return Image(path, width=iw * scale, height=ih * scale)
    except Exception:
        return None


def _pie_chart_drawing(data: list[tuple[str, int, str]], width=170, height=130, font_name="Helvetica"):
    """data: [(label, value, hex_color), ...] — basit pasta grafik döner (Drawing)."""
    from reportlab.graphics.shapes import Drawing, String
    from reportlab.graphics.charts.piecharts import Pie
    from reportlab.lib import colors as rl_colors

    values = [v for _lbl, v, _c in data if v > 0]
    if not values:
        return None
    labels = [lbl for lbl, v, _c in data if v > 0]
    chart_colors = [_c for _lbl, v, _c in data if v > 0]

    d = Drawing(width, height)
    pie = Pie()
    pie.x = 10
    pie.y = 15
    pie.width = 90
    pie.height = 90
    pie.data = values
    pie.labels = None
    pie.simpleLabels = False
    pie.sideLabels = False
    for i, col in enumerate(chart_colors):
        pie.slices[i].fillColor = rl_colors.HexColor(col)
        pie.slices[i].strokeColor = rl_colors.white
        pie.slices[i].strokeWidth = 1
    d.add(pie)

    # Basit sağ-yan legend
    ly = height - 18
    for i, (lbl, val) in enumerate(zip(labels, values)):
        d.add(Drawing(0, 0))
        from reportlab.graphics.shapes import Rect
        d.add(Rect(108, ly - 6, 8, 8, fillColor=rl_colors.HexColor(chart_colors[i]), strokeColor=None))
        d.add(String(120, ly - 5, f"{lbl} ({val})", fontSize=7, fontName=font_name,
                      fillColor=rl_colors.HexColor("#334155")))
        ly -= 14
    return d


def _bar_chart_drawing(categories: list[str], values: list[float], width=460, height=140,
                        bar_color="#6366f1", max_value=100, font_name="Helvetica"):
    """Yatay göstergeli basit bar chart (örn. strateji bazlı PG hedef üstü %)."""
    from reportlab.graphics.shapes import Drawing
    from reportlab.graphics.charts.barcharts import VerticalBarChart
    from reportlab.lib import colors as rl_colors

    if not values:
        return None
    d = Drawing(width, height)
    chart = VerticalBarChart()
    chart.x = 35
    chart.y = 30
    chart.width = width - 60
    chart.height = height - 50
    chart.data = [values]
    chart.categoryAxis.categoryNames = [c[:14] for c in categories]
    chart.categoryAxis.labels.fontSize = 7
    chart.categoryAxis.labels.fontName = font_name
    chart.categoryAxis.labels.angle = 20
    chart.categoryAxis.labels.dy = -8
    chart.valueAxis.valueMin = 0
    chart.valueAxis.valueMax = max_value
    chart.valueAxis.labels.fontSize = 7
    chart.valueAxis.labels.fontName = font_name
    chart.bars[0].fillColor = rl_colors.HexColor(bar_color)
    chart.barWidth = 10
    d.add(chart)
    return d


def _build_reportlab_pdf(tenant_id: int, tenant_name: str, tenant=None) -> bytes:
    """ReportLab ile zengin, çok-dilli haftalık rapor üretir (grafikler + kurum logosu)."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
    )

    FONT, FONT_BOLD, FONT_ITAL = _ensure_tr_font()

    snap = build_exec_snapshot(tenant_id)
    extras = _fetch_digest_extras(tenant_id)
    now = _dt.datetime.now()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        title=_("Kokpitim Haftalık Strateji Raporu"),
        author="Kokpitim",
    )

    styles = getSampleStyleSheet()
    h_title = ParagraphStyle("HTitle", parent=styles["Title"], fontName=FONT_BOLD, fontSize=20,
        textColor=colors.HexColor("#0f172a"), spaceAfter=4, leading=24, alignment=TA_LEFT)
    h_sub = ParagraphStyle("HSub", parent=styles["Normal"], fontName=FONT, fontSize=10,
        textColor=colors.HexColor("#64748b"), spaceAfter=16)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontName=FONT_BOLD, fontSize=13,
        textColor=colors.HexColor("#0f172a"), spaceBefore=14, spaceAfter=8)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontName=FONT, fontSize=10.5,
        textColor=colors.HexColor("#1e293b"), leading=14, spaceAfter=4)
    note = ParagraphStyle("Note", parent=styles["Normal"], fontName=FONT_ITAL, fontSize=8.5,
        textColor=colors.HexColor("#94a3b8"), spaceBefore=20, alignment=TA_CENTER)
    caption = ParagraphStyle("Caption", parent=styles["Normal"], fontName=FONT_ITAL, fontSize=8.5,
        textColor=colors.HexColor("#64748b"), alignment=TA_CENTER, spaceBefore=4)
    h2_style_no_space = ParagraphStyle("H2NoSpace", parent=h2, spaceBefore=0, spaceAfter=0)

    def section_heading(title_text, color_hex="#6366f1"):
        """Emoji yerine renkli sol-şerit ile bölüm başlığı (PDF fontlarında emoji glyph'i yok)."""
        tbl = Table([[Paragraph(title_text, h2_style_no_space)]], colWidths=[doc.width - 4])
        tbl.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 10),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("LINEBEFORE", (0, 0), (0, 0), 3, colors.HexColor(color_hex)),
        ]))
        return [Spacer(1, 14), tbl, Spacer(1, 6)]

    story = []

    # ── Başlık satırı: logo (varsa, solda) + başlık/alt-başlık ─────────────
    title_block = [
        Paragraph(_("Kokpitim — Haftalık Strateji Raporu"), h_title),
        Paragraph(f"{tenant_name} &nbsp;•&nbsp; {now.strftime('%d.%m.%Y %H:%M')}", h_sub),
    ]
    logo_flowable = _tenant_logo_flowable(tenant)
    if logo_flowable is not None:
        header_tbl = Table([[logo_flowable, title_block]], colWidths=[120, doc.width - 120])
        header_tbl.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (0, 0), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(header_tbl)
        story.append(Spacer(1, 10))
    else:
        story.extend(title_block)

    # Hero: Sağlık skoru
    score = snap.get("health_score") or 0
    score_color = colors.HexColor("#059669") if score >= 70 else \
                  colors.HexColor("#f59e0b") if score >= 50 else \
                  colors.HexColor("#dc2626")
    hero_label = ParagraphStyle("HeroLabel", parent=styles["Normal"], fontName=FONT_BOLD, fontSize=9,
        textColor=colors.white, leading=11, spaceAfter=2)
    hero_score = ParagraphStyle("HeroScore", parent=styles["Normal"], fontName=FONT_BOLD, fontSize=40,
        textColor=colors.white, leading=44, spaceAfter=2, spaceBefore=2)
    hero_note = ParagraphStyle("HeroNote", parent=styles["Normal"], fontName=FONT, fontSize=9,
        textColor=colors.HexColor("#cbd5e1"), leading=11)
    hero_tbl = Table([[
        Paragraph(f'{_("STRATEJİ SAĞLIK SKORU")} ({snap.get("year","-")})', hero_label)
    ], [
        Paragraph(str(score), hero_score)
    ], [
        Paragraph(_("100 üzerinden — yüksek skor daha sağlıklı"), hero_note)
    ]], colWidths=[doc.width])
    hero_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), score_color),
        ("LEFTPADDING", (0,0), (-1,-1), 18),
        ("RIGHTPADDING", (0,0), (-1,-1), 18),
        ("TOPPADDING", (0,0), (0,0), 14),
        ("BOTTOMPADDING", (0,0), (0,0), 0),
        ("TOPPADDING", (0,1), (0,1), 0),
        ("BOTTOMPADDING", (0,1), (0,1), 0),
        ("TOPPADDING", (0,2), (0,2), 2),
        ("BOTTOMPADDING", (0,2), (0,2), 14),
        ("BOX", (0,0), (-1,-1), 0, score_color),
    ]))
    story.append(hero_tbl)
    story.append(Spacer(1, 16))

    # ── Anahtar göstergeler ───────────────────────────────────────────────────
    story.extend(section_heading(_("Anahtar Göstergeler"), "#6366f1"))
    k = snap.get("kpi", {})
    a = snap.get("activity", {})
    r = snap.get("risk", {})
    an = snap.get("anomaly", {})
    s = snap.get("strategy", {})
    ini = snap.get("initiative", {})
    tr = snap.get("trigger", {})

    def _badge(value, good=False, warn=False, bad=False):
        col = "#059669" if good else ("#d97706" if warn else ("#dc2626" if bad else "#475569"))
        return f'<font color="{col}"><b>{value}</b></font>'

    kpi_on = k.get("on_target_pct", 0)
    overdue = a.get("overdue", 0)
    crit_r = r.get("critical", 0)
    anom_h = an.get("high", 0)

    metrik_data = [
        [_("Gösterge"), _("Değer"), _("Detay")],
        [_("PG Hedef Üstü"),
         Paragraph(_badge(f"%{kpi_on}",
                          good=kpi_on>=70, warn=50<=kpi_on<70, bad=kpi_on<50), body),
         _("%(with)s / %(total)s PG'de veri", **{"with": k.get("with_data", 0), "total": k.get("total", 0)})],
        [_("Aktif Strateji / Alt"), f"{s.get('count',0)} / {s.get('sub_count',0)}", "—"],
        [_("Toplam Girişim"), str(ini.get("total", 0)), "—"],
        [_("Gecikmiş Faaliyet"),
         Paragraph(_badge(overdue, good=overdue<=5, bad=overdue>5), body),
         _("%(n)s toplam", n=a.get("total", 0))],
        [_("Kritik Risk"),
         Paragraph(_badge(crit_r, good=crit_r==0, bad=crit_r>0), body),
         _("%(n)s açık risk", n=r.get("open", 0))],
        [_("Yüksek Anomali"),
         Paragraph(_badge(anom_h, good=anom_h==0, warn=anom_h>0), body),
         _("%(n)s orta öncelikli", n=an.get("medium", 0))],
        [_("Tetikleyici Ateşlemesi (7g)"), str(tr.get("fired_last_7d", 0)),
         _("%(n)s aktif tetikleyici", n=tr.get("active", 0))],
    ]
    mt = Table(metrik_data, colWidths=[doc.width*0.40, doc.width*0.25, doc.width*0.35])
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#0f172a")),
        ("FONTNAME", (0,0), (-1,-1), FONT), ("FONTNAME", (0,0), (-1,0), FONT_BOLD),
        ("FONTSIZE", (0,0), (-1,-1), 9.5),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#fafbfc")]),
        ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#e2e8f0")),
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("LEFTPADDING", (0,0), (-1,-1), 8),
        ("RIGHTPADDING", (0,0), (-1,-1), 8),
        ("TOPPADDING", (0,0), (-1,-1), 6),
        ("BOTTOMPADDING", (0,0), (-1,-1), 6),
    ]))
    story.append(mt)

    # ── Girişim durumu: tablo + pasta grafik yan yana ────────────────────────
    by_status = (ini.get("by_status") or {})
    if by_status:
        story.extend(section_heading(_("Girişim Durumu"), "#8b5cf6"))
        ini_data = [[_("Durum"), _("Adet"), _("Ort. İlerleme")]]
        status_colors = {
            "in_progress": "#6366f1", "planned": "#0ea5e9", "completed": "#10b981",
            "on_hold": "#f59e0b", "delayed": "#ef4444", "cancelled": "#94a3b8", "active": "#8b5cf6",
        }
        pie_data = []
        for st_key, info in by_status.items():
            avg = info.get("avg_progress", 0) or 0
            cnt = info.get("count", 0)
            ini_data.append([_ini_status_label(st_key), str(cnt), f"%{int(round(float(avg)))}"])
            pie_data.append((_ini_status_label(st_key), cnt, status_colors.get(st_key, "#64748b")))

        tbl_w = doc.width * 0.42
        pie_w = doc.width * 0.55
        it = Table(ini_data, colWidths=[tbl_w*0.52, tbl_w*0.24, tbl_w*0.24])
        it.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ("FONTNAME", (0,0), (-1,-1), FONT), ("FONTNAME", (0,0), (-1,0), FONT_BOLD),
            ("FONTSIZE", (0,0), (-1,-1), 8),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#fafbfc")]),
            ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#e2e8f0")),
            ("ALIGN", (1,0), (-1,-1), "CENTER"),
            ("LEFTPADDING", (0,0), (-1,-1), 5),
            ("RIGHTPADDING", (0,0), (-1,-1), 5),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))

        pie = _pie_chart_drawing(pie_data, width=pie_w, height=max(90, 20*len(pie_data)+30), font_name=FONT)
        if pie is not None:
            combo = Table([[it, pie]], colWidths=[tbl_w, pie_w])
            combo.setStyle(TableStyle([
                ("VALIGN", (0,0), (-1,-1), "TOP"),
                ("LEFTPADDING", (0,0), (-1,-1), 0),
                ("RIGHTPADDING", (0,0), (-1,-1), 0),
            ]))
            story.append(combo)
        else:
            story.append(it)

    # ── Strateji Bazında PG Performansı: tablo + bar chart ───────────────────
    if extras.get("strategy_perf"):
        story.extend(section_heading(_("Strateji Bazında PG Performansı"), "#4338ca"))
        rows = [[_("Strateji"), _("Toplam PG"), _("Veri Var"), _("Hedef Üstü")]]
        chart_cats, chart_vals = [], []
        for s_ in extras["strategy_perf"]:
            pct = s_.get("on_target_pct")
            rows.append([
                (s_["code"] or "")[:10] + " " + (s_["title"] or "")[:35],
                str(s_["total"]),
                str(s_["with_data"]),
                f"%{int(round(pct))}" if pct is not None else "—",
            ])
            if pct is not None:
                chart_cats.append(s_["code"] or s_["title"] or "—")
                chart_vals.append(pct)
        st_ = Table(rows, colWidths=[doc.width*0.50, doc.width*0.18, doc.width*0.16, doc.width*0.16])
        st_.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#eef2ff")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#4338ca")),
            ("FONTNAME", (0,0), (-1,-1), FONT), ("FONTNAME", (0,0), (-1,0), FONT_BOLD),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#fafbfc")]),
            ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#c7d2fe")),
            ("ALIGN", (1,0), (-1,-1), "CENTER"),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        story.append(st_)

        if chart_vals:
            story.append(Spacer(1, 6))
            bar = _bar_chart_drawing(chart_cats, chart_vals, width=doc.width, height=140,
                                      bar_color="#6366f1", max_value=100, font_name=FONT)
            if bar is not None:
                story.append(bar)
                story.append(Paragraph(_("Strateji bazında PG hedef üstü oranı (%)"), caption))

    # ── Top 5 Girişim (ilerlemeye göre) ──────────────────────────────────────
    if extras.get("top_initiatives"):
        story.extend(section_heading(_("Öncelikli Girişimler (Top 5)"), "#10b981"))
        rows = [["#", _("Girişim"), _("Durum"), _("İlerleme")]]
        for i, it_ in enumerate(extras["top_initiatives"], 1):
            rows.append([
                str(i),
                it_["name"][:50] + ("…" if len(it_["name"]) > 50 else ""),
                _ini_status_label(it_["status"]) if it_["status"] else "—",
                f"%{int(round(it_.get('progress_pct') or 0))}",
            ])
        tt = Table(rows, colWidths=[doc.width*0.06, doc.width*0.54, doc.width*0.22, doc.width*0.18])
        tt.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ("FONTNAME", (0,0), (-1,-1), FONT), ("FONTNAME", (0,0), (-1,0), FONT_BOLD),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#fafbfc")]),
            ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#e2e8f0")),
            ("ALIGN", (0,0), (0,-1), "CENTER"),
            ("ALIGN", (3,0), (3,-1), "CENTER"),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        story.append(tt)

    # ── Top 5 Gecikmiş Faaliyetler ────────────────────────────────────────────
    if extras.get("overdue_activities"):
        story.extend(section_heading(_("En Çok Gecikmiş Faaliyetler (Top 5)"), "#ef4444"))
        rows = [[_("Faaliyet"), _("Süreç"), _("Bitiş Tarihi"), _("Gecikme")]]
        for act in extras["overdue_activities"]:
            rows.append([
                (act["name"] or "—")[:40] + ("…" if act["name"] and len(act["name"]) > 40 else ""),
                (act["process_name"] or "—")[:25] + ("…" if act["process_name"] and len(act["process_name"]) > 25 else ""),
                act["end_date"].strftime("%d.%m.%Y") if act.get("end_date") else "—",
                _("%(n)s gün", n=act["days_overdue"]),
            ])
        ot = Table(rows, colWidths=[doc.width*0.40, doc.width*0.28, doc.width*0.16, doc.width*0.16])
        ot.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#fef2f2")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#991b1b")),
            ("FONTNAME", (0,0), (-1,-1), FONT), ("FONTNAME", (0,0), (-1,0), FONT_BOLD),
            ("FONTSIZE", (0,0), (-1,-1), 9),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#fafbfc")]),
            ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#fecaca")),
            ("ALIGN", (2,0), (3,-1), "CENTER"),
            ("LEFTPADDING", (0,0), (-1,-1), 6),
            ("RIGHTPADDING", (0,0), (-1,-1), 6),
            ("TOPPADDING", (0,0), (-1,-1), 5),
            ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ]))
        story.append(ot)

    # ── Heuristik aksiyon önerileri ──────────────────────────────────────────
    # (renk kodu, metin) — emoji yerine renkli madde işareti kullanılır (PDF fontlarında emoji glyph'i yok).
    actions = []
    if kpi_on < 50:
        actions.append(("#d97706", _("PG'lerin yalnız %%%(pct)s'ı hedef üstünde — stratejik öncelikleri yeniden değerlendirin.", pct=f"{kpi_on:.0f}")))
    if overdue > 5:
        actions.append(("#dc2626", _("%(n)s gecikmiş faaliyet — kapasite planlaması ve aksiyon eşleştirmesi gerekli.", n=overdue)))
    if crit_r > 0:
        actions.append(("#dc2626", _("%(n)s kritik risk var — risk azaltma planlarını gözden geçirin.", n=crit_r)))
    if anom_h > 0:
        actions.append(("#d97706", _("%(n)s yüksek öncelikli PG anomalisi — kök neden analizi başlatın.", n=anom_h)))
    if k.get("with_data", 0) < k.get("total", 0) * 0.6 and k.get("total", 0) > 0:
        actions.append(("#0ea5e9", _("PG'lerin yalnız %%%(pct)s'ında veri var — veri girişi disiplinini güçlendirin.",
                          pct=f"{(k['with_data']/max(k['total'],1))*100:.0f}")))
    if not actions:
        actions.append(("#10b981", _("Genel strateji sağlığı kabul edilebilir seviyede — mevcut ritmi sürdürün.")))

    story.extend(section_heading(_("Bu Hafta İçin Öneriler"), "#f59e0b"))
    for color_hex, ac in actions:
        story.append(Paragraph(f'<font color="{color_hex}">●</font>&nbsp;&nbsp;{ac}', body))

    # ── Yorum ────────────────────────────────────────────────────────────────
    if score >= 70:
        comment = _("Strateji uygulama disiplini güçlü. Kazanımları sürdürmek için liderlik tutarlılığı kritik.")
    elif score >= 50:
        comment = _("Strateji ivmesi orta seviyede. Hedef altında kalan göstergelere odaklanmak skor artışı sağlar.")
    else:
        comment = _("Strateji uygulamasında ciddi boşluklar var. Üst yönetim review'i ve kaynak aktarımı önerilir.")
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<i>{comment}</i>", body))

    # Footer
    story.append(Paragraph(
        _("Bu rapor Kokpitim Stratejik Sağlık motoru tarafından otomatik üretildi."),
        note
    ))

    doc.build(story)
    return buf.getvalue()


def render_digest_pdf(tenant_id: int, tenant_name: str = None, tenant=None) -> tuple[bytes, str]:
    """Returns (pdf_bytes, mime). reportlab başarısızsa HTML döner.

    tenant: Tenant modeli (opsiyonel) — verilirse kurum logosu PDF'e eklenir.
    """
    if tenant_name is None:
        tenant_name = _("Kurumunuz")
    # Tercih 1: reportlab — saf Python, her ortamda çalışır, zengin çok-dilli PDF
    try:
        pdf = _build_reportlab_pdf(tenant_id, tenant_name, tenant=tenant)
        if pdf and pdf[:4] == b"%PDF":
            return pdf, "application/pdf"
    except Exception as e:
        from flask import current_app as _ca
        import traceback
        try:
            _ca.logger.error(
                "[weekly-digest] reportlab PDF uretilemedi: %s\n%s",
                e, traceback.format_exc()
            )
        except Exception:
            pass

    # Tercih 2: WeasyPrint (Linux/Mac sunucularda kurulu olabilir)
    try:
        from weasyprint import HTML
        html = render_digest_html(tenant_id, tenant_name)
        pdf = HTML(string=html).write_pdf()
        if pdf:
            return pdf, "application/pdf"
    except Exception:
        pass

    # Fallback: HTML
    return render_digest_html(tenant_id, tenant_name).encode("utf-8"), "text/html"
