"""Raporlar modülü — landing + alt fazların register noktası.

Faz modüller (routes_faz0..5) __init__.py'den import edilerek yüklenir.
"""
from flask import render_template
from flask_login import login_required
from app.utils.decorators import require_module

from platform_core import app_bp


@app_bp.route("/reports")
@login_required
@require_module("raporlar")
def raporlar_index():
    """Eski rapor merkezi — K-Radar hub'ı ile birleştirildi, yönlendirir."""
    from flask import redirect, url_for
    return redirect(url_for("app_bp.k_radar_hub"))
