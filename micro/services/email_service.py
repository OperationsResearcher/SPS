"""
E-posta Gönderim Servisi — Micro Platform
Öncelik:
1) Kurum özel SMTP (ayarlarda açık ve eksiksiz)
2) Ortam değişkeni MAIL_* (sunucu + en az kullanıcı veya şifre)
3) Platform Admin kullanıcısının kurumunda kayıtlı özel SMTP (varsayılan çıkış)
4) Son çare: yalnızca MAIL_* (kimliksiz; çoğu sunucuda başarısız olur)
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


def _smtp_has_credentials(cfg: dict) -> bool:
    """Host dışında gönderim için genelde kullanıcı veya şifre gerekir."""
    if not cfg:
        return False
    u = (cfg.get("username") or "").strip()
    p = (cfg.get("password") or "").strip()
    return bool(u or p)


def _get_platform_admin_tenant_smtp_config():
    """
    Rolü «Admin» olan ilk aktif kullanıcının tenant'ında kayıtlı özel SMTP.
    Kurum kendi SMTP'sini kullanmak istemiyorsa / tanımlamamışsa platform çıkışı.
    """
    try:
        from app.models.core import Role, User

        admin = (
            User.query.join(Role, User.role_id == Role.id)
            .filter(Role.name == "Admin", User.is_active.is_(True))
            .order_by(User.id.asc())
            .first()
        )
        if not admin or not admin.tenant_id:
            return None
        # Aynı kurumdaysa ve özel SMTP kapalıysa zaten None; başka kurum Admin tenant'ı döner
        return _get_tenant_smtp_config(admin.tenant_id)
    except Exception as e:
        current_app.logger.warning(f"[email_service] platform admin SMTP yedek okunamadı: {e}")
        return None


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
    """Verilen SMTP config ile tek bir mail gönderir. (başarı, hata_metni)"""
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
            with smtplib.SMTP_SSL(smtp_cfg["host"], smtp_cfg["port"], context=context, timeout=30) as server:
                if smtp_cfg["username"]:
                    server.login(smtp_cfg["username"], smtp_cfg["password"])
                server.sendmail(smtp_cfg["sender_email"], to_email, msg.as_string())
        else:
            with smtplib.SMTP(smtp_cfg["host"], smtp_cfg["port"], timeout=30) as server:
                server.ehlo()
                if smtp_cfg["use_tls"]:
                    server.starttls()
                    server.ehlo()
                if smtp_cfg["username"]:
                    server.login(smtp_cfg["username"], smtp_cfg["password"])
                server.sendmail(smtp_cfg["sender_email"], to_email, msg.as_string())
        return True, ""
    except smtplib.SMTPAuthenticationError as e:
        err = "SMTP kimlik doğrulaması başarısız. Kullanıcı adı veya şifreyi kontrol edin."
        current_app.logger.error(f"[email_service._send_raw] auth {smtp_cfg['host']}:{smtp_cfg['port']} → {e}")
        return False, err
    except smtplib.SMTPRecipientsRefused as e:
        current_app.logger.error(f"[email_service._send_raw] refused → {e}")
        return False, "Alıcı e-posta adresi sunucu tarafından reddedildi."
    except (smtplib.SMTPConnectError, OSError, TimeoutError) as e:
        current_app.logger.error(f"[email_service._send_raw] connect {smtp_cfg['host']}:{smtp_cfg['port']} → {e}")
        return False, f"SMTP sunucusuna bağlanılamadı ({smtp_cfg['host']}:{smtp_cfg['port']}). Ağ / güvenlik duvarı veya adresi kontrol edin."
    except Exception as e:
        current_app.logger.error(f"[email_service._send_raw] {smtp_cfg['host']}:{smtp_cfg['port']} → {e}")
        msg = str(e).strip() or "Bilinmeyen SMTP hatası."
        if len(msg) > 400:
            msg = msg[:400] + "…"
        return False, msg


def send_notification_email(to_email, subject, html_body, tenant_id=None, text_body=None):
    """
    Bildirim e-postası gönderir (SMTP seçimi modül docstring'ine bakın).

    Returns:
        (bool, str) — (başarılı_mı, hata_metni veya boş)
    """
    smtp_cfg = None
    used_tenant_custom = False

    if tenant_id:
        smtp_cfg = _get_tenant_smtp_config(tenant_id)
        if smtp_cfg:
            used_tenant_custom = True

    if smtp_cfg is None:
        sys_cfg = _get_system_smtp_config()
        if sys_cfg.get("host") and _smtp_has_credentials(sys_cfg):
            smtp_cfg = sys_cfg
        else:
            admin_cfg = _get_platform_admin_tenant_smtp_config()
            if admin_cfg:
                smtp_cfg = admin_cfg
                current_app.logger.info(
                    "[email_service] Kurum özel SMTP yok / MAIL_* eksik — "
                    "platform Admin kurumunun SMTP'si kullanılıyor "
                    f"(istek tenant_id={tenant_id})."
                )
            else:
                smtp_cfg = sys_cfg

    if not smtp_cfg.get("host"):
        hint = (
            "E-posta sunucusu tanımlı değil. Kurumunuzda «Özel SMTP» kapalıysa: ortamda MAIL_SERVER "
            "veya platform Admin hesabının kurumunda kayıtlı özel SMTP gerekir; ayrıca bu sayfadan "
            "kurumunuza özel SMTP girebilirsiniz."
        )
        current_app.logger.warning("[email_service] SMTP host tanımlı değil, mail atlanıyor.")
        return False, hint

    if not used_tenant_custom and not _smtp_has_credentials(smtp_cfg):
        hint = (
            "Gönderim için SMTP kimlik bilgisi yok. Kurum özel SMTP kullanmıyorsanız: sunucuda MAIL_USERNAME "
            "ve MAIL_PASSWORD tanımlayın veya platform Admin kurumunda çalışan bir özel SMTP kaydı olduğundan "
            "emin olun; alternatif olarak buradan kurum SMTP'nizi açın."
        )
        current_app.logger.warning("[email_service] SMTP kimlik bilgisi yok, mail atlanıyor.")
        return False, hint

    ok, err = _send_raw(smtp_cfg, to_email, subject, html_body, text_body)
    return (True, "") if ok else (False, err)


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
