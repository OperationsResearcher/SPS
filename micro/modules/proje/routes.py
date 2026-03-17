"""Proje Yönetimi modülü (iskelet — ilerleyen sprintlerde geliştirilecek)."""

from flask import render_template
from flask_login import login_required

from micro import micro_bp


@micro_bp.route("/proje")
@login_required
def proje():
    """Proje Yönetimi ana sayfası."""
    return render_template("micro/proje/index.html")
