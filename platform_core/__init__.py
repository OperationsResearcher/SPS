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
    ("/individual", "bireysel"),
    ("/project", "proje"),
    ("/analysis", "analiz"),
    ("/k-radar", "k_radar"),
    ("/k-rapor", "k_rapor"),
]


# Rol/liderlik kapısı uygulanacak prefix'ler (Faz 2 — route sertleştirme).
# Faz 1'de sidebar'da gizlenen modüllerin route'ları da rol/liderliğe göre
# kilitlenir. Sayfa → /desktop redirect; API → JSON 403.
# docs/paketler/ROL-GORUNUM-KATMANI.md §6.
_ROLE_GATED_PREFIX_MODULE = [
    ("/k-radar", "k_radar"),
    ("/k-analiz", "k_radar"),
    ("/analysis", "analiz"),
    ("/sp", "sp"),
]


def _match_prefix(path, table):
    for prefix, mid in table:
        if path == prefix or path.startswith(prefix + "/"):
            return mid
    return None


@app_bp.before_request
def _enforce_package_module_gating():
    """Paket + rol/liderlik kapsamı dışındaki modül sayfalarını engelle.

    İki eksen (belge §3): paket (tenant) VE rol/liderlik (kullanıcı).
    Güvenli: yalnız bilinen prefix'ler; Admin bypass; çözülemezse fail-open.
    Sayfa (GET, HTML) → /desktop redirect; API/AJAX → JSON 403.
    """
    from flask import request, redirect, url_for, flash, jsonify
    from flask_login import current_user

    path = request.path or ""
    pkg_mid = _match_prefix(path, _GATED_PREFIX_MODULE)
    role_mid = _match_prefix(path, _ROLE_GATED_PREFIX_MODULE)
    if pkg_mid is None and role_mid is None:
        return None  # gate edilmeyen yol

    if not current_user.is_authenticated:
        return None  # login akışı kendi halleder
    if current_user.role and current_user.role.name == "Admin":
        return None  # platform admin bypass

    # İstek tipi: API/AJAX mı sayfa mı?
    is_api = ("/api/" in path) or \
        (request.headers.get("X-Requested-With") == "XMLHttpRequest")

    def _deny(msg):
        if is_api:
            from flask_babel import gettext as _
            return jsonify({"success": False, "message": _(msg)}), 403
        from flask_babel import gettext as _
        flash(_(msg), "warning")
        return redirect(url_for("app_bp.masaustu"))

    # ── Paket kapısı (yalnız SAYFA istekleri — mevcut davranış korunur) ──
    if pkg_mid is not None and not is_api and request.method == "GET":
        try:
            from app_platform.core.module_registry import get_accessible_modules
            allowed = {m["id"] for m in get_accessible_modules(current_user)}
        except Exception:
            allowed = None  # çözülemezse engelleme (fail-open)
        if allowed is not None and pkg_mid not in allowed:
            return _deny("Bu bölüm mevcut paketinizde yer almıyor.")

    # ── Rol/liderlik kapısı (sayfa + API) ──
    if role_mid is not None:
        try:
            from app.constants.module_visibility import can_see_module
            ok = can_see_module(current_user, role_mid)
        except Exception:
            ok = True  # çözülemezse engelleme (fail-open)
        if not ok:
            return _deny("Bu sayfaya erişim yetkiniz yok.")

    return None

