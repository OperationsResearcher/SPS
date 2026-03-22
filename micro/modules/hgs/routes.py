"""HGS — Hızlı Giriş Sistemi modülü.

Bu modül @login_required KULLANMAZ — geliştirme/demo ortamı için hızlı giriş sağlar.

Ana URL: /Hgs_mfg (eski /hgs ve /hgs/login/... 301 ile yönlendirilir).
"""

from flask import render_template, redirect, url_for, current_app, request, flash
from flask_login import login_user

from micro import micro_bp
from app.models.core import User


def _hgs_index():
    """Hızlı giriş kullanıcı listesi — tenant'a göre gruplu."""
    selected_user_id = request.args.get("selected", type=int)
    users = (
        User.query.filter_by(is_active=True)
        .order_by(User.tenant_id, User.first_name, User.last_name)
        .all()
    )

    tenant_map: dict[int | None, dict] = {}
    for u in users:
        tid = u.tenant_id
        if tid not in tenant_map:
            tenant_name = u.tenant.name if u.tenant else "Kuruma Bağlı Değil"
            tenant_map[tid] = {"name": tenant_name, "users": []}
        tenant_map[tid]["users"].append(u)

    groups = sorted(tenant_map.values(), key=lambda g: g["name"])

    return render_template("micro/hgs/index.html", groups=groups, selected_user_id=selected_user_id)


def _hgs_login(user_id: int):
    """Seçilen kullanıcı ile oturum aç."""
    if not current_app.config.get("HGS_BYPASS_ENABLED"):
        is_local_request = request.remote_addr in {"127.0.0.1", "::1", "localhost"}
        if not (current_app.debug and is_local_request):
            current_app.logger.error("HGS bypass login attempt blocked: feature flag disabled.")
            flash("Hızlı giriş özelliği kapalı. Yöneticinizle iletişime geçin.", "warning")
            return redirect(url_for("micro_bp.hgs"))

    u = User.query.get(user_id)
    if not u or not u.is_active:
        current_app.logger.error(f"HGS login failed: invalid or inactive user_id={user_id}")
        return redirect(url_for("micro_bp.hgs"))

    login_user(u)
    flash(f"Hızlı giriş başarılı: {u.first_name or u.email}", "success")
    return redirect(url_for("micro_bp.launcher"))


@micro_bp.route("/Hgs_mfg")
def hgs():
    return _hgs_index()


@micro_bp.route("/hgs")
def hgs_legacy_redirect():
    """Eski yer imleri için kalıcı yönlendirme."""
    q = request.query_string.decode() if request.query_string else ""
    dest = url_for("micro_bp.hgs")
    if q:
        dest = dest + "?" + q
    return redirect(dest, code=301)


@micro_bp.route("/Hgs_mfg/login/<int:user_id>")
def hgs_login(user_id):
    return _hgs_login(user_id)


@micro_bp.route("/hgs/login/<int:user_id>")
def hgs_login_legacy_redirect(user_id):
    return redirect(url_for("micro_bp.hgs_login", user_id=user_id), code=301)
