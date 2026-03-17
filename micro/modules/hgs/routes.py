"""HGS — Hızlı Giriş Sistemi modülü.

Bu modül @login_required KULLANMAZ — geliştirme/demo ortamı için hızlı giriş sağlar.
"""

from flask import render_template, redirect, url_for
from flask_login import login_user

from micro import micro_bp
from app.models.core import User, Tenant


@micro_bp.route("/hgs")
def hgs():
    """Hızlı giriş kullanıcı listesi — tenant'a göre gruplu."""
    users = (
        User.query
        .filter_by(is_active=True)
        .order_by(User.tenant_id, User.first_name, User.last_name)
        .all()
    )

    # Tenant'a göre grupla
    tenant_map: dict[int | None, dict] = {}
    for u in users:
        tid = u.tenant_id
        if tid not in tenant_map:
            tenant_name = u.tenant.name if u.tenant else "Kuruma Bağlı Değil"
            tenant_map[tid] = {"name": tenant_name, "users": []}
        tenant_map[tid]["users"].append(u)

    groups = sorted(tenant_map.values(), key=lambda g: g["name"])

    return render_template("micro/hgs/index.html", groups=groups)


@micro_bp.route("/hgs/login/<int:user_id>")
def hgs_login(user_id):
    """Seçilen kullanıcı ile oturum aç."""
    u = User.query.get(user_id)
    if not u or not u.is_active:
        return redirect(url_for("micro_bp.hgs"))

    login_user(u)
    return redirect(url_for("micro_bp.launcher"))
