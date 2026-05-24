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
    <tr><td>KPI Hedef Üstü</td>
        <td><span class="{{ 'badge-ok' if snap.kpi.on_target_pct>=70 else ('badge-warn' if snap.kpi.on_target_pct>=50 else 'badge-bad') }}">%{{ snap.kpi.on_target_pct }}</span></td>
        <td>{{ snap.kpi.with_data }} / {{ snap.kpi.total }} KPI'da veri</td></tr>
    <tr><td>Aktif Strateji / Alt</td><td>{{ snap.strategy.count }} / {{ snap.strategy.sub_count }}</td><td>—</td></tr>
    <tr><td>Toplam Initiative</td><td>{{ snap.initiative.total }}</td><td>—</td></tr>
    <tr><td>Gecikmiş Faaliyet</td>
        <td><span class="{{ 'badge-bad' if snap.activity.overdue>5 else 'badge-ok' }}">{{ snap.activity.overdue }}</span></td>
        <td>{{ snap.activity.total }} toplam</td></tr>
    <tr><td>Kritik Risk</td>
        <td><span class="{{ 'badge-bad' if snap.risk.critical>0 else 'badge-ok' }}">{{ snap.risk.critical }}</span></td>
        <td>{{ snap.risk.open }} açık risk</td></tr>
    <tr><td>Yüksek Anomali</td>
        <td><span class="{{ 'badge-warn' if snap.anomaly.high>0 else 'badge-ok' }}">{{ snap.anomaly.high }}</span></td>
        <td>{{ snap.anomaly.medium }} orta</td></tr>
    <tr><td>Trigger Ateşlemesi (7g)</td><td>{{ snap.trigger.fired_last_7d }}</td><td>{{ snap.trigger.active }} aktif</td></tr>
  </table>

  <h2>🚀 Initiative Durumu</h2>
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


def render_digest_pdf(tenant_id: int, tenant_name: str = "Kurumunuz") -> tuple[bytes, str]:
    """Returns (pdf_bytes, mime). PDF üretilemezse HTML döner."""
    html = render_digest_html(tenant_id, tenant_name)

    # Tercih 1: WeasyPrint
    try:
        from weasyprint import HTML
        pdf = HTML(string=html).write_pdf()
        return pdf, "application/pdf"
    except Exception:
        pass

    # Tercih 2: reportlab basit fallback
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
        from reportlab.lib.styles import getSampleStyleSheet
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
        snap = build_exec_snapshot(tenant_id)
        buf = io.BytesIO()
        doc = SimpleDocTemplate(buf, pagesize=A4)
        styles = getSampleStyleSheet()
        story = [
            Paragraph(f"<b>Kokpitim — Haftalık Strateji Raporu</b>", styles["Title"]),
            Paragraph(f"{tenant_name} • {_dt.datetime.now().strftime('%d.%m.%Y %H:%M')}", styles["Normal"]),
            Spacer(1, 20),
            Paragraph(f"<b>Strateji Sağlık Skoru:</b> {snap.get('health_score', '—')}", styles["Heading2"]),
            Paragraph(f"KPI Hedef Üstü: %{snap['kpi']['on_target_pct']}<br/>"
                      f"Aktif KPI: {snap['kpi']['total']}<br/>"
                      f"Initiative: {snap['initiative']['total']}<br/>"
                      f"Gecikmiş Faaliyet: {snap['activity']['overdue']}<br/>"
                      f"Kritik Risk: {snap['risk']['critical']}<br/>"
                      f"Yüksek Anomali: {snap['anomaly']['high']}",
                      styles["Normal"]),
        ]
        doc.build(story)
        return buf.getvalue(), "application/pdf"
    except Exception:
        pass

    # Fallback: HTML
    return html.encode("utf-8"), "text/html"
