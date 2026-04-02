"""Uygulama blueprint erişimi için nötr katman."""

from flask import Blueprint

# Kök URL: tek yapı "/" altında. Statik dosyalar /m/... altında servis edilir.
# Şablon ve statik varlıklar `ui/` altında; platform blueprint burada tanımlanır.
app_bp = Blueprint(
    "app_bp",
    __name__,
    url_prefix="",
    template_folder="../ui/templates",
    static_folder="../ui/static",
    static_url_path="m",
)

# Modül route kayıtları (yan etki importları)
from app_platform.core import launcher  # noqa: E402, F401
from app_platform.modules.shared.auth import routes as auth_routes  # noqa: E402, F401
from app_platform.modules.masaustu import routes as masaustu_routes  # noqa: E402, F401
from app_platform.modules.sp import routes as sp_routes  # noqa: E402, F401
from app_platform.modules.surec import routes as surec_routes  # noqa: E402, F401
from app_platform.modules.proje import routes as proje_routes  # noqa: E402, F401
from app_platform.modules.analiz import routes as analiz_routes  # noqa: E402, F401
from app_platform.modules.k_radar import routes as k_radar_routes  # noqa: E402, F401
from app_platform.modules.shared.ayarlar import routes as ayarlar_routes  # noqa: E402, F401
from app_platform.modules.shared.bildirim import routes as bildirim_routes  # noqa: E402, F401
from app_platform.modules.kurum import routes as kurum_routes  # noqa: E402, F401
from app_platform.modules.bireysel import routes as bireysel_routes  # noqa: E402, F401
from app_platform.modules.admin import routes as admin_routes  # noqa: E402, F401
from app_platform.modules.hgs import routes as hgs_routes  # noqa: E402, F401
from app_platform.modules.api import routes as api_routes  # noqa: E402, F401

