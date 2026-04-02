"""Launcher — kök ana sayfa (modül seçim ekranı)."""

from flask import render_template
from flask_login import login_required, current_user

from platform_core import app_bp
from app_platform.core.module_registry import get_accessible_modules


@app_bp.route("/")
@login_required
def launcher():
    """Modül launcher ekranı."""
    modules = get_accessible_modules(current_user)
    return render_template("platform/launcher.html", modules=modules)
