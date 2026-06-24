"""Email Digest Servisi (Sprint 18).

Periyodik (haftalık/aylık) KPI özet maili gönderir.
Yönetici rollerine: kritik anomali + bekleyen risk + plan_year özet.

Trigger:
1. Manuel: `/k-rapor/api/digest/send` endpoint'i
2. Otomatik: APScheduler ile (uygulamayla başlar, Pazartesi 09:00)

Hedef alıcılar:
- Default: tenant_admin + executive_manager rolleri
- Override: payload'da specific email listesi
"""
from __future__ import annotations

import datetime as _dt
from typing import Optional

from flask import current_app, render_template_string
from flask_babel import gettext as _


_DIGEST_TEMPLATE = """
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>{{ subject }}</title></head>
<body style="font-family: Arial, sans-serif; color: #333; max-width: 700px; margin: 0 auto;">
  <div style="background: #1a4d80; color: white; padding: 20px;">
    <h1 style="margin: 0;">Kokpitim — Haftalık Özet</h1>
    <p style="margin: 8px 0 0;">{{ tenant_name }} · {{ date_str }}</p>
  </div>

  <div style="padding: 20px;">
    <h2 style="color: #1a4d80;">📊 Genel Durum</h2>
    <table style="width: 100%; border-collapse: collapse;">
      <tr><td style="padding: 8px; border-bottom: 1px solid #eee;">Aktif Strateji</td><td style="text-align: right; font-weight: bold;">{{ strategy_count }}</td></tr>
      <tr><td style="padding: 8px; border-bottom: 1px solid #eee;">Aktif Süreç</td><td style="text-align: right; font-weight: bold;">{{ process_count }}</td></tr>
      <tr><td style="padding: 8px; border-bottom: 1px solid #eee;">Toplam KPI</td><td style="text-align: right; font-weight: bold;">{{ kpi_count }}</td></tr>
      <tr><td style="padding: 8px;">Plan Yılı</td><td style="text-align: right; font-weight: bold;">{{ plan_year }}</td></tr>
    </table>

    {% if anomalies %}
    <h2 style="color: #dc3545; margin-top: 24px;">⚠️ KPI Anomalileri ({{ anomalies|length }})</h2>
    <p style="color: #666;">Tarihsel ortalamadan ≥2σ uzaktaki ölçümler:</p>
    <table style="width: 100%; border-collapse: collapse;">
      <thead><tr style="background: #f5f5f5;">
        <th style="padding: 8px; text-align: left;">Süreç</th>
        <th style="padding: 8px; text-align: left;">KPI</th>
        <th style="padding: 8px; text-align: right;">Son</th>
        <th style="padding: 8px; text-align: right;">Ort</th>
        <th style="padding: 8px;">Önem</th>
      </tr></thead>
      <tbody>
      {% for a in anomalies %}
      <tr style="border-top: 1px solid #eee;">
        <td style="padding: 6px;"><code>{{ a.process_code }}</code></td>
        <td style="padding: 6px;">{{ a.kpi_name }}</td>
        <td style="padding: 6px; text-align: right; font-weight: bold;">{{ a.latest_value }}</td>
        <td style="padding: 6px; text-align: right; color: #666;">{{ a.mean }}</td>
        <td style="padding: 6px;">
          {% if a.severity == 'high' %}<span style="color: #dc3545;">⬤ Yüksek</span>
          {% elif a.severity == 'medium' %}<span style="color: #fd7e14;">⬤ Orta</span>
          {% else %}<span style="color: #0d6efd;">⬤ Düşük</span>{% endif %}
        </td>
      </tr>
      {% endfor %}
      </tbody>
    </table>
    {% else %}
    <h2 style="color: #28a745; margin-top: 24px;">✅ Anomali Yok</h2>
    <p style="color: #666;">Tüm KPI'lar tarihsel ortalamalar civarında.</p>
    {% endif %}

    <p style="margin-top: 32px; padding: 16px; background: #f5f5f5; border-radius: 6px; color: #666; font-size: 12px;">
      Bu özet Kokpitim platformu tarafından otomatik üretilmiştir. Detaylı analiz için
      <a href="{{ app_url }}/k-rapor" style="color: #1a4d80;">K-Rapor</a> sayfasına gidin.
    </p>
  </div>
</body>
</html>
"""


def build_digest_content(tenant_id: int) -> dict:
    """Tenant için digest verisini hazırla."""
    from app.models.core import Tenant, Strategy
    from app.models.process import Process, ProcessKpi
    from app.services.kpi_anomaly_service import detect_anomalies_for_tenant

    tenant = Tenant.query.get(tenant_id)
    if not tenant:
        return {}

    strategy_count = Strategy.query.filter_by(tenant_id=tenant_id, is_active=True).count()
    process_count = Process.query.filter_by(tenant_id=tenant_id, is_active=True).count()
    kpi_count = (
        ProcessKpi.query.join(Process)
        .filter(Process.tenant_id == tenant_id, ProcessKpi.is_active.is_(True))
        .count()
    )

    anomalies = detect_anomalies_for_tenant(tenant_id, threshold=2.0, limit=10)

    today = _dt.date.today()
    return {
        "tenant_name": tenant.name,
        "subject": f"Kokpitim Haftalık Özet — {tenant.name} — {today.strftime('%d.%m.%Y')}",
        "date_str": today.strftime("%d %B %Y").replace(
            "January", "Ocak").replace("February", "Şubat").replace("March", "Mart")
            .replace("April", "Nisan").replace("May", "Mayıs").replace("June", "Haziran")
            .replace("July", "Temmuz").replace("August", "Ağustos").replace("September", "Eylül")
            .replace("October", "Ekim").replace("November", "Kasım").replace("December", "Aralık"),
        "strategy_count": strategy_count,
        "process_count": process_count,
        "kpi_count": kpi_count,
        "plan_year": today.year,
        "anomalies": [a.to_dict() for a in anomalies],
        "app_url": current_app.config.get("BASE_URL", "http://localhost:5001"),
    }


def render_digest_html(tenant_id: int) -> str:
    """Digest HTML'i üret."""
    data = build_digest_content(tenant_id)
    if not data:
        return ""
    return render_template_string(_DIGEST_TEMPLATE, **data)


def get_digest_recipients(tenant_id: int) -> list[str]:
    """Tenant'taki yönetici e-postalarını döner."""
    from app.models.core import User, Role
    role_names = ("tenant_admin", "executive_manager", "Admin")
    roles = Role.query.filter(Role.name.in_(role_names)).all()
    role_ids = [r.id for r in roles]
    if not role_ids:
        return []
    users = (
        User.query
        .filter(User.tenant_id == tenant_id, User.is_active.is_(True), User.role_id.in_(role_ids))
        .all()
    )
    return [u.email for u in users if u.email and not u.email.startswith("deleted_")]


def send_digest(tenant_id: int, recipients: Optional[list[str]] = None) -> dict:
    """Digest mail gönder.

    Returns:
        {"success": bool, "sent_to": int, "subject": str, "message": str}
    """
    try:
        data = build_digest_content(tenant_id)
        if not data:
            return {"success": False, "message": _("Tenant bulunamadı")}

        if recipients is None:
            recipients = get_digest_recipients(tenant_id)

        if not recipients:
            return {"success": False, "message": _("Alıcı yönetici bulunamadı")}

        html = render_template_string(_DIGEST_TEMPLATE, **data)

        # E-posta gönderim: SMTP doğrudan, tenant_email_configs varsa onu kullan
        ok_count = _send_via_smtp(tenant_id, recipients, data["subject"], html)

        return {
            "success": ok_count > 0,
            "sent_to": ok_count,
            "total_recipients": len(recipients),
            "subject": data["subject"],
            "message": f"{ok_count}/{len(recipients)} alıcıya gönderildi",
        }
    except Exception as e:
        current_app.logger.error(f"[send_digest] {e}", exc_info=True)
        return {"success": False, "message": _("Özet e-postası gönderilemedi.")}


def _send_via_smtp(tenant_id: int, recipients: list[str], subject: str, html: str) -> int:
    """Tenant SMTP config'i (varsa) veya app config'den SMTP gönderim.

    Returns: başarılı gönderim sayısı.
    """
    import smtplib
    from email.mime.multipart import MIMEMultipart
    from email.mime.text import MIMEText

    # Tenant config öncelikli
    from app.models.email_config import TenantEmailConfig
    cfg = TenantEmailConfig.query.filter_by(tenant_id=tenant_id, use_custom_smtp=True).first()
    if cfg and cfg.smtp_host:
        host = cfg.smtp_host
        port = cfg.smtp_port or 587
        username = cfg.smtp_username
        password = cfg.smtp_password  # NOT: production'da şifreli saklanmalı
        use_tls = cfg.smtp_use_tls
        use_ssl = cfg.smtp_use_ssl
        sender_name = cfg.sender_name or "Kokpitim"
        sender_email = cfg.sender_email or username
    else:
        # App config fallback
        host = current_app.config.get("MAIL_HOST")
        port = current_app.config.get("MAIL_PORT", 587)
        username = current_app.config.get("MAIL_USERNAME")
        password = current_app.config.get("MAIL_PASSWORD")
        use_tls = current_app.config.get("MAIL_USE_TLS", True)
        use_ssl = current_app.config.get("MAIL_USE_SSL", False)
        sender_name = current_app.config.get("MAIL_SENDER_NAME", "Kokpitim")
        sender_email = current_app.config.get("MAIL_SENDER", username)

    if not host or not sender_email:
        current_app.logger.warning("[digest] SMTP config eksik — mail gönderilemiyor")
        return 0

    ok = 0
    try:
        if use_ssl:
            server = smtplib.SMTP_SSL(host, port, timeout=15)
        else:
            server = smtplib.SMTP(host, port, timeout=15)
            if use_tls:
                server.starttls()
        if username and password:
            server.login(username, password)

        for to in recipients:
            try:
                msg = MIMEMultipart("alternative")
                msg["Subject"] = subject
                msg["From"] = f"{sender_name} <{sender_email}>"
                msg["To"] = to
                msg.attach(MIMEText(html, "html", "utf-8"))
                server.sendmail(sender_email, [to], msg.as_string())
                ok += 1
            except Exception as e:
                current_app.logger.warning(f"[digest] {to} gönderim hatası: {e}")
        server.quit()
    except Exception as e:
        current_app.logger.error(f"[digest] SMTP bağlantı hatası: {e}")
    return ok


def schedule_digest_for_all_tenants():
    """APScheduler hook — her tenant için digest gönder.

    Pazartesi 09:00 tetiklenir (init'te kayıt).
    """
    from app.models.core import Tenant
    tenants = Tenant.query.filter_by(is_active=True).all()
    results = []
    for t in tenants:
        try:
            r = send_digest(t.id)
            results.append({"tenant_id": t.id, **r})
        except Exception as e:
            current_app.logger.error(f"[scheduled_digest] tenant={t.id} {e}")
    return results
