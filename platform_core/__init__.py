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
from app_platform.modules.shared.kule import routes as kule_routes  # noqa: E402, F401
from app_platform.modules.shared.search import routes as search_routes  # noqa: E402, F401
from app_platform.modules.shared.my_tasks import routes as my_tasks_routes  # noqa: E402, F401
from app_platform.modules.shared.scheduled_reports import routes as scheduled_reports_routes  # noqa: E402, F401
from app_platform.modules.kurum import routes as kurum_routes  # noqa: E402, F401
from app_platform.modules.bireysel import routes as bireysel_routes  # noqa: E402, F401
from app_platform.modules.admin import routes as admin_routes  # noqa: E402, F401
from app_platform.modules.api import routes as api_routes  # noqa: E402, F401
from app_platform.modules.k_rapor import routes as k_rapor_routes  # noqa: E402, F401
from app_platform.modules.demo import routes as demo_routes  # noqa: E402, F401
from app_platform.modules.raporlar import routes as raporlar_routes  # noqa: E402, F401


# ── Paket gating (blueprint-bazlı toplu kapı) ─────────────────────────────────
# URL prefix → launcher modül id. Paket'te modül yoksa o prefix'teki sayfalar
# açılmaz. Yalnızca SAYFA (GET, HTML) istekleri; API/AJAX kendi 403'ünü verir.
# sp/kurum/masaustu/ayarlar/bildirim → her zaman erişilebilir (gate edilmez).
_GATED_PREFIX_MODULE = [
    ("/process", "surec"),
    ("/bireysel", "bireysel"),
    ("/project", "proje"),
    ("/analiz", "analiz"),
    ("/k-radar", "k_radar"),
    ("/k-rapor", "k_rapor"),
]


@app_bp.before_request
def _enforce_package_module_gating():
    """Paket kapsamı dışındaki modül sayfalarını engelle (sayfa düzeyinde).

    Güvenli: yalnız bilinen prefix'ler; Admin bypass; çözülemezse fail-open.
    API/statik/AJAX'a dokunmaz (onlar kendi yetki kontrolünü yapar).
    """
    from flask import request, redirect, url_for, flash
    from flask_login import current_user

    path = request.path or ""
    # Hangi modüle ait? (bilinen prefix değilse dokunma)
    module_id = None
    for prefix, mid in _GATED_PREFIX_MODULE:
        if path == prefix or path.startswith(prefix + "/"):
            module_id = mid
            break
    if module_id is None:
        return None  # gate edilmeyen yol

    # Statik/AJAX/API isteklerine dokunma (yalnız sayfa GET)
    if request.method != "GET" or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return None
    if "/api/" in path:
        return None

    if not current_user.is_authenticated:
        return None  # login akışı kendi halleder
    if current_user.role and current_user.role.name == "Admin":
        return None  # platform admin bypass

    try:
        from app_platform.core.module_registry import get_accessible_modules
        allowed = {m["id"] for m in get_accessible_modules(current_user)}
    except Exception:
        return None  # gating çözülemezse engelleme (fail-open)

    if module_id not in allowed:
        flash("Bu bölüm mevcut paketinizde yer almıyor.", "warning")
        return redirect(url_for("app_bp.masaustu"))
    return None

