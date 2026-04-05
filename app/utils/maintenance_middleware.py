"""Bakim modu: Admin haric (ve acil erisim) engeli."""

from __future__ import annotations

import secrets

from flask import Flask, current_app, redirect, render_template, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

from app.services.maintenance_service import maintenance_active

COOKIE_NAME = "kokpitim_maint_bypass"
COOKIE_MAX_AGE = 86400 * 7
QUERY_PARAM = "bakim_erisim"


def _path_ok(path: str) -> bool:
    if path == "/health":
        return True
    if path in ("/login", "/logout"):
        return True
    if path.startswith("/m/"):
        return True
    if path.startswith("/static/"):
        return True
    if path == "/favicon.ico":
        return True
    if path.startswith("/micro/admin/bakim-modu"):
        return True
    return False


def _admin_bypass(user) -> bool:
    if not user or not user.is_authenticated:
        return False
    role = getattr(user, "role", None)
    return bool(role and role.name == "Admin")


def _verify_bypass_cookie(app: Flask, raw: str | None) -> bool:
    if not raw:
        return False
    ser = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="kokpitim-maintenance-bypass")
    try:
        data = ser.loads(raw, max_age=COOKIE_MAX_AGE)
        return data == {"ok": True}
    except (BadSignature, SignatureExpired, TypeError, ValueError):
        return False


def _set_bypass_cookie(app: Flask, resp):
    ser = URLSafeTimedSerializer(app.config["SECRET_KEY"], salt="kokpitim-maintenance-bypass")
    token = ser.dumps({"ok": True})
    secure = bool(app.config.get("SESSION_COOKIE_SECURE"))
    resp.set_cookie(
        COOKIE_NAME,
        token,
        max_age=COOKIE_MAX_AGE,
        httponly=True,
        secure=secure,
        samesite="Lax",
        path="/",
    )
    return resp


def register_maintenance_middleware(app: Flask) -> None:
    def _maintenance_gate():
        if not maintenance_active(app):
            return None
        path = request.path or ""
        if _path_ok(path):
            return None

        bypass_secret = app.config.get("MAINTENANCE_BYPASS_SECRET")
        if bypass_secret:
            qp = request.args.get(QUERY_PARAM)
            if qp and secrets.compare_digest(str(qp), str(bypass_secret)):
                resp = redirect(request.path or "/")
                return _set_bypass_cookie(app, resp)

            raw = request.cookies.get(COOKIE_NAME)
            if _verify_bypass_cookie(app, raw):
                return None

        from flask_login import current_user

        if _admin_bypass(current_user):
            return None

        return (
            render_template(
                "platform/maintenance.html",
                acil_erisim_tanimli=bool(bypass_secret),
            ),
            503,
        )

    app.before_request_funcs.setdefault(None, []).insert(0, _maintenance_gate)
