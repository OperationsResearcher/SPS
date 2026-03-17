"""Launcher — /micro ana sayfası, modül seçim ekranı."""

from flask import render_template
from flask_login import login_required, current_user

from micro import micro_bp
from micro.core.module_registry import get_accessible_modules


@micro_bp.route("/")
@login_required
def launcher():
    """Modül launcher ekranı."""
    modules = get_accessible_modules(current_user)
    return render_template("micro/launcher.html", modules=modules)
