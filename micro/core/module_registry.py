"""Modül kayıt sistemi — erişim kontrolü ve modül tanımları.

URL'ler Micro kökündedir (önceden /micro öneki vardı).
"""

# Her modül: id, ad, url, ikon, açıklama
MODULES = [
    {
        "id": "masaustu",
        "name": "Masaüstüm",
        "url": "/masaustu",
        "icon": "🏠",
        "description": "Kişisel özet — tüm modüllerden gelen görevler, KPI'lar ve iş planları",
    },
    {
        "id": "sp",
        "name": "Stratejik Planlama",
        "url": "/sp",
        "icon": "🎯",
        "description": "Stratejiler, alt stratejiler ve hedef takibi",
    },
    {
        "id": "surec",
        "name": "Süreç Yönetimi",
        "url": "/process",
        "icon": "⚙️",
        "description": "Süreçler, KPI'lar ve faaliyet takibi",
    },
    {
        "id": "kurum",
        "name": "Kurum Paneli",
        "url": "/kurum",
        "icon": "🏢",
        "description": "Stratejik kimlik, kurum bilgileri ve strateji yönetimi",
    },
    {
        "id": "bireysel",
        "name": "Bireysel Performans",
        "url": "/bireysel/karne",
        "icon": "👤",
        "description": "Bireysel PG'ler, faaliyetler ve kişisel karne",
    },
    {
        "id": "proje",
        "name": "Proje Yönetimi",
        "url": "/project",
        "icon": "📋",
        "description": "Projeler, görevler, Kanban ve stratejik portföy",
    },
    {
        "id": "analiz",
        "name": "Analiz Merkezi",
        "url": "/analiz",
        "icon": "📊",
        "description": "Raporlar, grafikler ve performans analizleri",
    },
    {
        "id": "admin",
        "name": "Yönetim Paneli",
        "url": "/admin/users",
        "icon": "🛡️",
        "description": "Kullanıcı, kurum ve paket yönetimi",
    },
    {
        "id": "hgs",
        "name": "Hızlı Giriş",
        "url": "/MfG_hgs",
        "icon": "⚡",
        "description": "Demo/geliştirme ortamı için hızlı kullanıcı girişi",
    },
    {
        "id": "api",
        "name": "API Dokümantasyonu",
        "url": "/api/docs",
        "icon": "📡",
        "description": "REST API v1 endpoint referansı",
    },
    {
        "id": "ayarlar",
        "name": "Ayarlar",
        "url": "/ayarlar",
        "icon": "⚙️",
        "description": "Kurum ve kullanıcı ayarları",
    },
    {
        "id": "bildirim",
        "name": "Bildirim Merkezi",
        "url": "/bildirim",
        "icon": "🔔",
        "description": "Sistem bildirimleri ve uyarılar",
    },
]

# Minimum modül seti — paketsiz + standart kullanıcı için (launcher kartları)
_MINIMUM_MODULE_IDS = {"masaustu", "bildirim", "ayarlar"}

# Kurum yöneticisi / üst yönetim: sidebar ile uyum — paket yokken tüm modülleri göster
_PRIVILEGED_ROLES_FULL_LAUNCHER = frozenset(
    {"tenant_admin", "executive_manager", "Admin"}
)

# system_modules.code (seed / Excel `turkish_to_slug` çıktısı) → launcher modül id
# Launcher id'leri MODULES["id"] ile aynı olmalı.
_SYSTEM_CODE_TO_LAUNCHER_ID = {
    # Doğrudan eşleşme (elle girilmiş kısa kodlar)
    "sp": "sp",
    "surec": "surec",
    "kurum": "kurum",
    "bireysel": "bireysel",
    "proje": "proje",
    "analiz": "analiz",
    "masaustu": "masaustu",
    "ayarlar": "ayarlar",
    "bildirim": "bildirim",
    # Modülleşme_V2 / seed.py `turkish_to_slug` tipik çıktılar
    "stratejik_planlama": "sp",
    "strategic_planlama": "sp",
    "strategic_planning": "sp",
    "surec_yonetimi": "surec",
    "process_yonetimi": "surec",
    "kurum_paneli": "kurum",
    "kurumsal_kimlik": "kurum",
    "bireysel_performans": "bireysel",
    "proje_yonetimi": "proje",
    "project_yonetimi": "proje",
    "analiz_merkezi": "analiz",
    "analysis_merkezi": "analiz",
}

_LAUNCHER_MODULE_IDS = frozenset(m["id"] for m in MODULES)

# Rol bazlı kısıtlamalar
_ROLE_RESTRICTED = {
    "admin":    {"tenant_admin", "executive_manager", "Admin"},
    "hgs":      {"Admin"},
    # Home sayfasındaki "API Dokümantasyonu" kartı yalnızca Admin'de görünsün.
    "api":      {"Admin"},
}


def _map_system_code_to_launcher_id(code: str) -> str | None:
    c = (code or "").strip().lower()
    if not c:
        return None
    if c in _LAUNCHER_MODULE_IDS:
        return c
    return _SYSTEM_CODE_TO_LAUNCHER_ID.get(c)


def _package_modules_to_launcher_ids(package) -> set[str] | None:
    """SubscriptionPackage.modules → launcher id kümesi. Tanınmayan kodlar yok sayılır."""
    try:
        mods = list(package.modules) if package.modules else []
    except Exception:
        return None
    if not mods:
        return None
    out: set[str] = set()
    for sm in mods:
        lid = _map_system_code_to_launcher_id(getattr(sm, "code", "") or "")
        if lid:
            out.add(lid)
    # Pakette modül var ama hiçbiri launcher ile eşleşmediyse filtreyi devre dışı bırak
    if not out:
        return None
    return out


def get_accessible_modules(user):
    """Kullanıcının erişebileceği modülleri döndür.

    Kontrol sırası:
    1. Tenant paketi → SubscriptionPackage.modules (SystemModule.code) → launcher id
    2. Rol kısıtlamaları
    3. Paketsiz tenant → standart kullanıcıya yalnızca minimum set; kurum yöneticisi vb. tam liste
    """
    if user is None:
        return []

    role_name = user.role.name if user.role else None

    # Admin her şeyi görür
    if role_name == "Admin":
        return MODULES

    # Paket → modül kodları (doğru ilişki adı: `modules`, alan: `code`)
    allowed_module_ids = None
    try:
        tenant = user.tenant
        if tenant and tenant.package:
            allowed_module_ids = _package_modules_to_launcher_ids(tenant.package)
    except Exception:
        allowed_module_ids = None

    result = []
    for mod in MODULES:
        mid = mod["id"]

        # Paket kısıtlaması
        if allowed_module_ids is not None:
            if mid not in allowed_module_ids and mid not in _MINIMUM_MODULE_IDS:
                continue

        # Rol kısıtlaması
        restricted_roles = _ROLE_RESTRICTED.get(mid)
        if restricted_roles and role_name not in restricted_roles:
            continue

        result.append(mod)

    # Paketsiz tenant → yalnızca minimum set (kurum yöneticisi / üst yönetim hariç)
    has_package = bool(user.tenant and getattr(user.tenant, "package_id", None))
    if (
        allowed_module_ids is None
        and not has_package
        and role_name not in _PRIVILEGED_ROLES_FULL_LAUNCHER
    ):
        result = [m for m in result if m["id"] in _MINIMUM_MODULE_IDS]

    return result
