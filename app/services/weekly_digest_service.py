"""Haftalık strateji digest — HTML + PDF üretimi (S63).

PDF üretimi için sırayla denenir:
  1. weasyprint (HTML→PDF, yüksek kalite)
  2. reportlab (saf Python, fallback)
  3. düz HTML (PDF yok)
"""
from __future__ import annotations

import datetime as _dt
import io

from flask import render_template_string

from app.services.exec_dashboard_service import build_exec_snapshot


DIGEST_HTML = """
<!doctype html><html lang="tr"><head><meta charset="utf-8">
<title>Kokpitim Haftalık Strateji Raporu</title>
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
  <h1>Kokpitim — Haftalık Strateji Raporu</h1>
  <p style="color:#64748b;">{{ tenant_name }} • {{ generated_at }}</p>

  <div class="hero">
    <div style="font-size:11px; opacity:0.7; text-transform:uppercase;">Strateji Sağlık Skoru</div>
    <div class="hero-score">{{ snap.health_score or '—' }}</div>
    <div style="font-size:12px; opacity:0.8;">{{ snap.year }} yılı</div>
  </div>

  <h2>📊 Anahtar Göstergeler</h2>
  <table>
    <tr><th>Gösterge</th><th>Değer</th><th>Detay</th></tr>
    <tr><td>PG Hedef Üstü</td>
        <td><span class="{{ 'badge-ok' if snap.kpi.on_target_pct>=70 else ('badge-warn' if snap.kpi.on_target_pct>=50 else 'badge-bad') }}">%{{ snap.kpi.on_target_pct }}</span></td>
        <td>{{ snap.kpi.with_data }} / {{ snap.kpi.total }} PG'de veri</td></tr>
    <tr><td>Aktif Strateji / Alt</td><td>{{ snap.strategy.count }} / {{ snap.strategy.sub_count }}</td><td>—</td></tr>
    <tr><td>Toplam Girişim</td><td>{{ snap.initiative.total }}</td><td>—</td></tr>
    <tr><td>Gecikmiş Faaliyet</td>
        <td><span class="{{ 'badge-bad' if snap.activity.overdue>5 else 'badge-ok' }}">{{ snap.activity.overdue }}</span></td>
        <td>{{ snap.activity.total }} toplam</td></tr>
    <tr><td>Kritik Risk</td>
        <td><span class="{{ 'badge-bad' if snap.risk.critical>0 else 'badge-ok' }}">{{ snap.risk.critical }}</span></td>
        <td>{{ snap.risk.open }} açık risk</td></tr>
    <tr><td>Yüksek Anomali</td>
        <td><span class="{{ 'badge-warn' if snap.anomaly.high>0 else 'badge-ok' }}">{{ snap.anomaly.high }}</span></td>
        <td>{{ snap.anomaly.medium }} orta öncelikli</td></tr>
    <tr><td>Tetikleyici Ateşlemesi (7g)</td><td>{{ snap.trigger.fired_last_7d }}</td><td>{{ snap.trigger.active }} aktif</td></tr>
  </table>

  <h2>🚀 Girişim Durumu</h2>
  <table>
    <tr><th>Durum</th><th>Adet</th><th>Ortalama İlerleme</th></tr>
    {% for st, info in snap.initiative.by_status.items() %}
    <tr><td>{{ st }}</td><td>{{ info.count }}</td><td>%{{ info.avg_progress|round(0)|int }}</td></tr>
    {% endfor %}
  </table>

  <div class="footer">
    Bu rapor Kokpitim Stratejik Sağlık motoru tarafından otomatik üretildi.
    Sorularınız için: yönetim panelinize giriş yapın.
  </div>
</body></html>
"""


def render_digest_html(tenant_id: int, tenant_name: str = "Kurumunuz") -> str:
    snap = build_exec_snapshot(tenant_id)
    return render_template_string(
        DIGEST_HTML,
        snap=snap,
        tenant_name=tenant_name,
        generated_at=_dt.datetime.now().strftime("%d.%m.%Y %H:%M"),
    )


def _build_reportlab_pdf(tenant_id: int, tenant_name: str) -> bytes:
    """ReportLab ile zengin Türkçe haftalık rapor üretir."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
    )

    snap = build_exec_snapshot(tenant_id)
    now = _dt.datetime.now()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm,
        title="Kokpitim Haftalık Strateji Raporu",
        author="Kokpitim",
    )

    styles = getSampleStyleSheet()
    h_title = ParagraphStyle("HTitle", parent=styles["Title"], fontSize=20,
        textColor=colors.HexColor("#0f172a"), spaceAfter=4, leading=24)
    h_sub = ParagraphStyle("HSub", parent=styles["Normal"], fontSize=10,
        textColor=colors.HexColor("#64748b"), spaceAfter=16)
    h2 = ParagraphStyle("H2", parent=styles["Heading2"], fontSize=13,
        textColor=colors.HexColor("#0f172a"), spaceBefore=14, spaceAfter=8)
    body = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10.5,
        textColor=colors.HexColor("#1e293b"), leading=14, spaceAfter=4)
    note = ParagraphStyle("Note", parent=styles["Normal"], fontSize=8.5,
        textColor=colors.HexColor("#94a3b8"), spaceBefore=20, alignment=TA_CENTER)

    story = []

    # Başlık
    story.append(Paragraph("Kokpitim — Haftalık Strateji Raporu", h_title))
    story.append(Paragraph(
        f"{tenant_name} &nbsp;•&nbsp; {now.strftime('%d.%m.%Y %H:%M')}", h_sub
    ))

    # Hero: Sağlık skoru
    score = snap.get("health_score") or 0
    score_color = colors.HexColor("#059669") if score >= 70 else \
                  colors.HexColor("#f59e0b") if score >= 50 else \
                  colors.HexColor("#dc2626")
    hero_tbl = Table([[
        Paragraph(f'<font size="9" color="white">STRATEJİ SAĞLIK SKORU ({snap.get("year","-")})</font><br/>'
                  f'<font size="36" color="white"><b>{score}</b></font><br/>'
                  f'<font size="9" color="#cbd5e1">100 üzerinden — yüksek skor daha sağlıklı</font>',
                  body)
    ]], colWidths=[doc.width])
    hero_tbl.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), score_color),
        ("LEFTPADDING", (0,0), (-1,-1), 18),
        ("RIGHTPADDING", (0,0), (-1,-1), 18),
        ("TOPPADDING", (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("BOX", (0,0), (-1,-1), 0, score_color),
    ]))
    story.append(hero_tbl)
    story.append(Spacer(1, 16))

    # ── Anahtar göstergeler ───────────────────────────────────────────────────
    story.append(Paragraph("📊 Anahtar Göstergeler", h2))
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
        ["Gösterge", "Değer", "Detay"],
        ["PG Hedef Üstü",
         Paragraph(_badge(f"%{kpi_on}",
                          good=kpi_on>=70, warn=50<=kpi_on<70, bad=kpi_on<50), body),
         f"{k.get('with_data',0)} / {k.get('total',0)} PG'de veri"],
        ["Aktif Strateji / Alt", f"{s.get('count',0)} / {s.get('sub_count',0)}", "—"],
        ["Toplam Girişim", str(ini.get("total", 0)), "—"],
        ["Gecikmiş Faaliyet",
         Paragraph(_badge(overdue, good=overdue<=5, bad=overdue>5), body),
         f"{a.get('total', 0)} toplam"],
        ["Kritik Risk",
         Paragraph(_badge(crit_r, good=crit_r==0, bad=crit_r>0), body),
         f"{r.get('open', 0)} açık risk"],
        ["Yüksek Anomali",
         Paragraph(_badge(anom_h, good=anom_h==0, warn=anom_h>0), body),
         f"{an.get('medium', 0)} orta öncelikli"],
        ["Tetikleyici Ateşlemesi (7g)", str(tr.get("fired_last_7d", 0)),
         f"{tr.get('active', 0)} aktif tetikleyici"],
    ]
    mt = Table(metrik_data, colWidths=[doc.width*0.40, doc.width*0.25, doc.width*0.35])
    mt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f1f5f9")),
        ("TEXTCOLOR", (0,0), (-1,0), colors.HexColor("#0f172a")),
        ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
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

    # ── Girişim durumu ────────────────────────────────────────────────────────
    by_status = (ini.get("by_status") or {})
    if by_status:
        story.append(Paragraph("🚀 Girişim Durumu", h2))
        ini_data = [["Durum", "Adet", "Ortalama İlerleme"]]
        for st_key, info in by_status.items():
            avg = info.get("avg_progress", 0)
            ini_data.append([st_key, str(info.get("count", 0)), f"%{int(round(avg))}"])
        it = Table(ini_data, colWidths=[doc.width*0.5, doc.width*0.25, doc.width*0.25])
        it.setStyle(TableStyle([
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#f1f5f9")),
            ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
            ("FONTSIZE", (0,0), (-1,-1), 9.5),
            ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, colors.HexColor("#fafbfc")]),
            ("GRID", (0,0), (-1,-1), 0.25, colors.HexColor("#e2e8f0")),
            ("ALIGN", (1,0), (-1,-1), "CENTER"),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("RIGHTPADDING", (0,0), (-1,-1), 8),
            ("TOPPADDING", (0,0), (-1,-1), 6),
            ("BOTTOMPADDING", (0,0), (-1,-1), 6),
        ]))
        story.append(it)

    # ── Heuristik aksiyon önerileri ──────────────────────────────────────────
    actions = []
    if kpi_on < 50:
        actions.append(f"⚠️ PG'lerin yalnız %{kpi_on:.0f}'ı hedef üstünde — stratejik öncelikleri yeniden değerlendirin.")
    if overdue > 5:
        actions.append(f"🔴 {overdue} gecikmiş faaliyet — kapasite planlaması ve aksiyon eşleştirmesi gerekli.")
    if crit_r > 0:
        actions.append(f"🛡️ {crit_r} kritik risk var — risk azaltma planlarını gözden geçirin.")
    if anom_h > 0:
        actions.append(f"📊 {anom_h} yüksek öncelikli PG anomalisi — kök neden analizi başlatın.")
    if k.get("with_data", 0) < k.get("total", 0) * 0.6 and k.get("total", 0) > 0:
        actions.append(f"📥 PG'lerin yalnız %{(k['with_data']/max(k['total'],1))*100:.0f}'ında veri var — veri girişi disiplinini güçlendirin.")
    if not actions:
        actions.append("✅ Genel strateji sağlığı kabul edilebilir seviyede — mevcut ritmi sürdürün.")

    story.append(Paragraph("💡 Bu Hafta İçin Öneriler", h2))
    for ac in actions:
        story.append(Paragraph(f"• {ac}", body))

    # ── Yorum ────────────────────────────────────────────────────────────────
    if score >= 70:
        comment = "Strateji uygulama disiplini güçlü. Kazanımları sürdürmek için liderlik tutarlılığı kritik."
    elif score >= 50:
        comment = "Strateji ivmesi orta seviyede. Hedef altında kalan göstergelere odaklanmak skor artışı sağlar."
    else:
        comment = "Strateji uygulamasında ciddi boşluklar var. Üst yönetim review'i ve kaynak aktarımı önerilir."
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"<i>{comment}</i>", body))

    # Footer
    story.append(Paragraph(
        "Bu rapor Kokpitim Stratejik Sağlık motoru tarafından otomatik üretildi.",
        note
    ))

    doc.build(story)
    return buf.getvalue()


def render_digest_pdf(tenant_id: int, tenant_name: str = "Kurumunuz") -> tuple[bytes, str]:
    """Returns (pdf_bytes, mime). reportlab başarısızsa HTML döner."""
    # Tercih 1: WeasyPrint (Linux/Mac sunucularda)
    try:
        from weasyprint import HTML
        html = render_digest_html(tenant_id, tenant_name)
        pdf = HTML(string=html).write_pdf()
        return pdf, "application/pdf"
    except Exception:
        pass

    # Tercih 2: reportlab — zengin Türkçe PDF
    try:
        return _build_reportlab_pdf(tenant_id, tenant_name), "application/pdf"
    except Exception as e:
        from flask import current_app as _ca
        try:
            _ca.logger.warning(f"[weekly-digest] reportlab PDF üretilemedi: {e}")
        except Exception:
            pass

    # Fallback: HTML
    return render_digest_html(tenant_id, tenant_name).encode("utf-8"), "text/html"
