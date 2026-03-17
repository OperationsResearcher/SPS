"""
E-posta Gönderim Servisi — Micro Platform
Tenant'ın özel SMTP'si varsa onu, yoksa sistem SMTP'sini kullanır.
"""

import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask import current_app


def _get_system_smtp_config():
    """Sistem varsayılan SMTP ayarlarını config'den döner."""
    return {
        "host": current_app.config.get("MAIL_SERVER", "smtp.gmail.com"),
        "port": int(current_app.config.get("MAIL_PORT", 587)),
        "use_tls": current_app.config.get("MAIL_USE_TLS", True),
        "use_ssl": current_app.config.get("MAIL_USE_SSL", False),
        "username": current_app.config.get("MAIL_USERNAME", ""),
        "password": current_app.config.get("MAIL_PASSWORD", ""),
        "sender_name": current_app.config.get("MAIL_SENDER_NAME", "Kokpitim"),
        "sender_email": current_app.config.get("MAIL_SENDER_EMAIL", "bildirim@kokpitim.com"),
    }


def _get_tenant_smtp_config(tenant_id):
    """
    Tenant'ın özel SMTP ayarlarını döner.
    use_custom_smtp=False ise None döner → sistem SMTP kullanılır.
    """
    try:
        from app.models.email_config import TenantEmailConfig
        cfg = TenantEmailConfig.query.filter_by(tenant_id=tenant_id).first()
        if not cfg or not cfg.use_custom_smtp:
            return None
        if not cfg.smtp_host or not cfg.smtp_username:
            return None
        return {
            "host": cfg.smtp_host,
            "port": cfg.smtp_port or 587,
            "use_tls": cfg.smtp_use_tls,
            "use_ssl": cfg.smtp_use_ssl,
            "username": cfg.smtp_username,
            "password": cfg.smtp_password or "",
            "sender_name": cfg.sender_name or "Kokpitim",
            "sender_email": cfg.sender_email or cfg.smtp_username,
        }
    except Exception as e:
        current_app.logger.warning(f"[email_service] tenant smtp config error: {e}")
        return None


def _send_raw(smtp_cfg, to_email, subject, html_body, text_body=None):
    """Verilen SMTP config ile tek bir mail gönderir."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = f"{smtp_cfg['sender_name']} <{smtp_cfg['sender_email']}>"
    msg["To"] = to_email

    if text_body:
        msg.attach(MIMEText(text_body, "plain", "utf-8"))
    msg.attach(MIMEText(html_body, "html", "utf-8"))

    try:
        if smtp_cfg["use_ssl"]:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(smtp_cfg["host"], smtp_cfg["port"], context=context) as server:
                server.login(smtp_cfg["username"], smtp_cfg["password"])
                server.sendmail(smtp_cfg["sender_email"], to_email, msg.as_string())
        else:
            with smtplib.SMTP(smtp_cfg["host"], smtp_cfg["port"]) as server:
                server.ehlo()
                if smtp_cfg["use_tls"]:
                    server.starttls()
                    server.ehlo()
                if smtp_cfg["username"]:
                    server.login(smtp_cfg["username"], smtp_cfg["password"])
                server.sendmail(smtp_cfg["sender_email"], to_email, msg.as_string())
        return True
    except Exception as e:
        current_app.logger.error(f"[email_service._send_raw] {smtp_cfg['host']}:{smtp_cfg['port']} → {e}")
        return False


def send_notification_email(to_email, subject, html_body, tenant_id=None, text_body=None):
    """
    Bildirim e-postası gönderir.
    tenant_id verilirse önce tenant SMTP'sini dener, yoksa sistem SMTP'sini kullanır.

    Returns:
        bool — başarılı mı?
    """
    smtp_cfg = None
    if tenant_id:
        smtp_cfg = _get_tenant_smtp_config(tenant_id)

    if smtp_cfg is None:
        smtp_cfg = _get_system_smtp_config()

    if not smtp_cfg.get("host"):
        current_app.logger.warning("[email_service] SMTP host tanımlı değil, mail atlanıyor.")
        return False

    return _send_raw(smtp_cfg, to_email, subject, html_body, text_body)


def test_smtp_connection(host, port, use_tls, use_ssl, username, password):
    """
    SMTP bağlantısını test eder — ayarlar sayfasından çağrılır.
    Returns: (success: bool, message: str)
    """
    try:
        if use_ssl:
            context = ssl.create_default_context()
            with smtplib.SMTP_SSL(host, int(port), context=context, timeout=10) as server:
                if username:
                    server.login(username, password)
        else:
            with smtplib.SMTP(host, int(port), timeout=10) as server:
                server.ehlo()
                if use_tls:
                    server.starttls()
                    server.ehlo()
                if username:
                    server.login(username, password)
        return True, "Bağlantı başarılı."
    except smtplib.SMTPAuthenticationError:
        return False, "Kimlik doğrulama hatası. Kullanıcı adı veya şifre yanlış."
    except smtplib.SMTPConnectError:
        return False, f"Sunucuya bağlanılamadı: {host}:{port}"
    except Exception as e:
        return False, str(e)
