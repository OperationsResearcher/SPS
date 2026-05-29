"""Raporlar modülü — landing + alt fazların register noktası.

Faz modüller (routes_faz0..5) __init__.py'den import edilerek yüklenir.
"""
from flask import render_template
from flask_login import login_required

from platform_core import app_bp


@app_bp.route("/raporlar")
@login_required
def raporlar_index():
    """Yeni rapor önerileri için landing — kart grid."""
    return render_template("platform/raporlar/index.html")
