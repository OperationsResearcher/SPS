"""Demo oturumları için sunucu tarafı koruma (GUV-25).

Demo'da her ziyaretçi paylaşılan Tomofil kurumunun yöneticisi olarak girer ve Test/Yayın
ile aynı fiziksel sunucuda çalışır. Bu yüzden platform yönetimi, e-posta/SMTP, webhook ve
yedek uçları demo oturumlarında kapalıdır; süre dolumu istemci heartbeat'ine bırakılmaz.

Yalnız KOKPITIM_DEMO_MODE=1 iken kaydedilir.
"""
from __future__ import annotations

from datetime import datetime, timezone

from flask import jsonify, redirect, request, session, url_for
from flask_babel import gettext as _
from flask_login import logout_user

# (önek, yalnız_yazma)  yalnız_yazma=True → GET/HEAD/OPTIONS serbest
_BLOCKED = (
    ("/admin/araclar", False),        # yedek indir/geri yükle, hata kontrolü, kılavuz
    ("/admin/", True),                # kullanıcı/kurum/paket yönetimi yazmaları
    ("/settings/email/api/", True),   # SMTP kaydet/test/gönder
    ("/k-report/api/webhook/", True),
    ("/k-report/api/anomalies/notify-", True),
    ("/profile", True),               # paylaşılan demo hesabının e-posta/parolası
)
_SAFE_METHODS = ("GET", "HEAD", "OPTIONS")
_EXEMPT_PREFIXES = ("/demo", "/static", "/health")


def _expired() -> bool:
    exp_iso = session.get("demo_expires_at")
    if not exp_iso:
        return False
    try:
        return datetime.now(timezone.utc) >= datetime.fromisoformat(exp_iso)
    except ValueError:
        return True


def _wants_json() -> bool:
    return request.is_json or request.path.startswith("/api") or "json" in (request.headers.get("Accept") or "")


def init_demo_guard(app) -> None:
    @app.before_request
    def _demo_guard():
        if not session.get("demo_session_active"):
            return None
        path = request.path
        if path.startswith(_EXEMPT_PREFIXES):
            return None

        if _expired():
            from app.services.demo_reset_service import trigger_async_reset
            logout_user()
            session.clear()
            trigger_async_reset()
            if _wants_json():
                return jsonify({"success": False, "expired": True,
                                "message": _("Demo süresi doldu.")}), 401
            return redirect(url_for("app_bp.demo_landing"))

        for prefix, write_only in _BLOCKED:
            if path.startswith(prefix) and not (write_only and request.method in _SAFE_METHODS):
                return jsonify({"success": False,
                                "message": _("Bu işlem demo ortamında kapalıdır.")}), 403
        return None
