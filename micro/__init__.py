"""Micro — Modüler uygulama platformu blueprint factory."""

from flask import Blueprint

# Kök URL: Micro "/" altında. Statik dosyalar uygulama /static ile çakışmasın diye /m/...
micro_bp = Blueprint(
    "micro_bp",
    __name__,
    url_prefix="",
    template_folder="templates",
    static_folder="static",
    static_url_path="m",
)

# ── Mevcut modüller ───────────────────────────────────────────────────────────
from micro.core import launcher                          # noqa: E402, F401
from micro.modules.shared.auth import routes as auth_routes          # noqa: E402, F401
from micro.modules.masaustu import routes as masaustu_routes         # noqa: E402, F401
from micro.modules.sp import routes as sp_routes                     # noqa: E402, F401
from micro.modules.surec import routes as surec_routes               # noqa: E402, F401
from micro.modules.proje import routes as proje_routes               # noqa: E402, F401
from micro.modules.analiz import routes as analiz_routes             # noqa: E402, F401
from micro.modules.shared.ayarlar import routes as ayarlar_routes    # noqa: E402, F401
from micro.modules.shared.bildirim import routes as bildirim_routes  # noqa: E402, F401

# ── Yeni modüller ─────────────────────────────────────────────────────────────
from micro.modules.kurum import routes as kurum_routes               # noqa: E402, F401
from micro.modules.bireysel import routes as bireysel_routes         # noqa: E402, F401
from micro.modules.admin import routes as admin_routes               # noqa: E402, F401
from micro.modules.hgs import routes as hgs_routes                   # noqa: E402, F401
from micro.modules.api import routes as api_routes                   # noqa: E402, F401
