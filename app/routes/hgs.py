"""HGS (Hızlı Giriş) Blueprint — devre dışı.

Hızlı giriş yalnızca micro kökte `/MfG_hgs` üzerinden sunulur.
Legacy `/kok/hgs` bilinçli olarak 404 döner (yer imi / tarama ile erişimi kesmek için).
"""

from flask import Blueprint, abort

hgs_bp = Blueprint("hgs_bp", __name__, url_prefix="/hgs")


@hgs_bp.route("/")
def index():
    abort(404)


@hgs_bp.route("/login/<int:user_id>")
def quick_login(user_id):
    abort(404)
