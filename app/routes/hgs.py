"""HGS (Hızlı Giriş) Blueprint - Public quick login screen."""

from flask import Blueprint, redirect, render_template, url_for
from flask_login import login_user
from sqlalchemy.orm import joinedload

from app.models.core import User

hgs_bp = Blueprint("hgs_bp", __name__, url_prefix="/hgs")


@hgs_bp.route("/")
def index():
    """Quick login screen - public, no login required."""
    users = (
        User.query.options(joinedload(User.tenant), joinedload(User.role))
        .filter_by(is_active=True)
        .order_by(User.tenant_id, User.first_name, User.email)
        .all()
    )
    tenant_groups = {}
    for u in users:
        name = (u.tenant.short_name or u.tenant.name) if u.tenant else "Diğer"
        if name not in tenant_groups:
            tenant_groups[name] = []
        tenant_groups[name].append(u)
    tenant_groups = dict(sorted(tenant_groups.items()))
    return render_template("hgs/index.html", users=users, tenant_groups=tenant_groups)


@hgs_bp.route("/login/<int:user_id>")
def quick_login(user_id):
    """Quick login as user - public, no login required."""
    user = User.query.get(user_id)
    if not user or not user.is_active:
        return redirect(url_for("hgs_bp.index"))
    login_user(user, remember=True)
    return redirect(url_for("dashboard_bp.index"))
