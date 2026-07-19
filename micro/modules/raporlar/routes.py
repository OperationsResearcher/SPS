"""Raporlar modülü — landing + alt fazların register noktası.

Faz modüller (routes_faz0..5) __init__.py'den import edilerek yüklenir.
"""
from flask import render_template
from flask_login import login_required
from app.utils.decorators import require_module

from platform_core import app_bp


@app_bp.route("/k-report/all")
@login_required
@require_module("k_rapor")
def raporlar_index():
    """Eski rapor merkezi — K-Radar hub'ı ile birleştirildi, yönlendirir.

    Katman mimarisi Faz 4 (2026-07-17): `/k-report` kökünü `k_rapor` aldı
    (o daha yetenekli: ?tab=X ile içerik gösterir, tabsız hub'a yönlendirir).
    Bu route saf redirect'ti — kökü ona bırakıp yan adrese çekildi.
    Endpoint adı sözleşme gereği korundu; `/reports` legacy'si buraya düşmez,
    doğrudan `/k-report`'a gider.
    """
    from flask import redirect, url_for
    return redirect(url_for("app_bp.k_radar_hub"))
