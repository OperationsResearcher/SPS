"""Kurum E-posta Ayarları modülü.

Sadece tenant_admin ve executive_manager rollerine açıktır.
"""

from flask import jsonify, render_template, request, current_app
from flask_login import login_required, current_user

from micro import micro_bp
from app.models import db
from app.models.email_config import TenantEmailConfig

# Erişime izin verilen roller
_ALLOWED_ROLES = {"tenant_admin", "executive_manager", "Admin"}


def _check_access():
    """Yetki kontrolü — yetkisizse 403 JSON veya render döner."""
    role_name = current_user.role.name if current_user.role else ""
    return role_name in _ALLOWED_ROLES


@micro_bp.route("/ayarlar/eposta")
@login_required
def ayarlar_eposta():
    """Kurum e-posta ayarları sayfası."""
    if not _check_access():
        return render_template("micro/errors/403.html"), 403

    cfg = TenantEmailConfig.query.filter_by(
        tenant_id=current_user.tenant_id
    ).first()

    return render_template("micro/ayarlar/eposta.html", cfg=cfg)


@micro_bp.route("/ayarlar/eposta/api/save", methods=["POST"])
@login_required
def ayarlar_eposta_save():
    """Kurum e-posta ayarlarını kaydet."""
    if not _check_access():
        return jsonify({"success": False, "message": "Bu işlem için yetkiniz yok."}), 403

    data = request.get_json() or {}
    try:
        cfg = TenantEmailConfig.query.filter_by(
            tenant_id=current_user.tenant_id
        ).first()

        if cfg is None:
            cfg = TenantEmailConfig(tenant_id=current_user.tenant_id)
            db.session.add(cfg)

        cfg.use_custom_smtp          = bool(data.get("use_custom_smtp", False))
        cfg.smtp_host                = (data.get("smtp_host") or "").strip() or None
        cfg.smtp_port                = int(data.get("smtp_port") or 587)
        cfg.smtp_use_tls             = bool(data.get("smtp_use_tls", True))
        cfg.smtp_use_ssl             = bool(data.get("smtp_use_ssl", False))
        cfg.smtp_username            = (data.get("smtp_username") or "").strip() or None
        cfg.sender_name              = (data.get("sender_name") or "").strip() or None
        cfg.sender_email             = (data.get("sender_email") or "").strip() or None
        cfg.notify_on_process_assign = bool(data.get("notify_on_process_assign", True))
        cfg.notify_on_kpi_change     = bool(data.get("notify_on_kpi_change", True))
        cfg.notify_on_activity_add   = bool(data.get("notify_on_activity_add", True))
        cfg.notify_on_task_assign    = bool(data.get("notify_on_task_assign", True))
        cfg.updated_by               = current_user.id

        # Şifre — boş gönderilirse mevcut değeri koru
        new_password = (data.get("smtp_password") or "").strip()
        if new_password:
            cfg.smtp_password = new_password

        db.session.commit()
        return jsonify({"success": True, "message": "E-posta ayarları kaydedildi."})

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[ayarlar_eposta_save] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/ayarlar/eposta/api/test", methods=["POST"])
@login_required
def ayarlar_eposta_test():
    """SMTP bağlantısını test et."""
    if not _check_access():
        return jsonify({"success": False, "message": "Bu işlem için yetkiniz yok."}), 403

    data = request.get_json() or {}
    try:
        from micro.services.email_service import test_smtp_connection
        ok, msg = test_smtp_connection(
            host=data.get("smtp_host", ""),
            port=data.get("smtp_port", 587),
            use_tls=bool(data.get("smtp_use_tls", True)),
            use_ssl=bool(data.get("smtp_use_ssl", False)),
            username=data.get("smtp_username", ""),
            password=data.get("smtp_password", ""),
        )
        return jsonify({"success": ok, "message": msg})
    except Exception as e:
        current_app.logger.error(f"[ayarlar_eposta_test] {e}")
        return jsonify({"success": False, "message": str(e)}), 400


@micro_bp.route("/ayarlar/eposta/api/send-test", methods=["POST"])
@login_required
def ayarlar_eposta_send_test():
    """Kayıtlı ayarlarla test maili gönder."""
    if not _check_access():
        return jsonify({"success": False, "message": "Bu işlem için yetkiniz yok."}), 403

    try:
        from micro.services.email_service import send_notification_email
        html = """\
<h2>Test E-postası</h2>
<p>Kokpitim e-posta ayarlarınız başarıyla yapılandırılmıştır.</p>
"""
        ok = send_notification_email(
            to_email=current_user.email,
            subject="Kokpitim — Test E-postası",
            html_body=html,
            tenant_id=current_user.tenant_id,
        )
        if ok:
            return jsonify({"success": True, "message": f"Test maili {current_user.email} adresine gönderildi."})
        return jsonify({"success": False, "message": "Mail gönderilemedi. SMTP ayarlarını kontrol edin."})
    except Exception as e:
        current_app.logger.error(f"[ayarlar_eposta_send_test] {e}")
        return jsonify({"success": False, "message": str(e)}), 400
