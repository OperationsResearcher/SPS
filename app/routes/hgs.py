"""HGS (Hızlı Giriş) Blueprint — devre dışı.

Hızlı giriş yalnızca `/MfG_hgs` üzerinden sunulur.
Bu blueprint altında gelen yollar bilinçli olarak 404 döner.
"""

from flask import Blueprint, abort

hgs_bp = Blueprint("hgs_bp", __name__, url_prefix="/hgs")


@hgs_bp.route("/")
def index():
    abort(404)


@hgs_bp.route("/login/<int:user_id>")
def quick_login(user_id):
    abort(404)
