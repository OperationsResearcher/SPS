"""Modül kayıt sistemi — erişim kontrolü ve modül tanımları."""

# Her modül: id, ad, url, ikon, açıklama
MODULES = [
    {
        "id": "masaustu",
        "name": "Masaüstüm",
        "url": "/micro/masaustu",
        "icon": "🏠",
        "description": "Kişisel özet — tüm modüllerden gelen görevler, KPI'lar ve iş planları",
    },
    {
        "id": "sp",
        "name": "Stratejik Planlama",
        "url": "/micro/sp",
        "icon": "🎯",
        "description": "Stratejiler, alt stratejiler ve hedef takibi",
    },
    {
        "id": "surec",
        "name": "Süreç Yönetimi",
        "url": "/micro/surec",
        "icon": "⚙️",
        "description": "Süreçler, KPI'lar ve faaliyet takibi",
    },
    {
        "id": "kurum",
        "name": "Kurum Paneli",
        "url": "/micro/kurum",
        "icon": "🏢",
        "description": "Stratejik kimlik, kurum bilgileri ve strateji yönetimi",
    },
    {
        "id": "bireysel",
        "name": "Bireysel Performans",
        "url": "/micro/bireysel/karne",
        "icon": "👤",
        "description": "Bireysel PG'ler, faaliyetler ve kişisel karne",
    },
    {
        "id": "proje",
        "name": "Proje Yönetimi",
        "url": "/micro/proje",
        "icon": "📋",
        "description": "Projeler, görevler ve zaman çizelgesi",
    },
    {
        "id": "analiz",
        "name": "Analiz Merkezi",
        "url": "/micro/analiz",
        "icon": "📊",
        "description": "Raporlar, grafikler ve performans analizleri",
    },
    {
        "id": "admin",
        "name": "Yönetim Paneli",
        "url": "/micro/admin/users",
        "icon": "🛡️",
        "description": "Kullanıcı, kurum ve paket yönetimi",
    },
    {
        "id": "hgs",
        "name": "Hızlı Giriş",
        "url": "/micro/hgs",
        "icon": "⚡",
        "description": "Demo/geliştirme ortamı için hızlı kullanıcı girişi",
    },
    {
        "id": "api",
        "name": "API Dokümantasyonu",
        "url": "/micro/api/docs",
        "icon": "📡",
        "description": "REST API v1 endpoint referansı",
    },
    {
        "id": "ayarlar",
        "name": "Ayarlar",
        "url": "/micro/ayarlar",
        "icon": "⚙️",
        "description": "Kurum ve kullanıcı ayarları",
    },
    {
        "id": "bildirim",
        "name": "Bildirim Merkezi",
        "url": "/micro/bildirim",
        "icon": "🔔",
        "description": "Sistem bildirimleri ve uyarılar",
    },
]

# Minimum modül seti — paketsiz tenant'lar için
_MINIMUM_MODULE_IDS = {"masaustu", "bildirim", "ayarlar"}

# Rol bazlı kısıtlamalar
_ROLE_RESTRICTED = {
    "kurum":    {"tenant_admin", "executive_manager", "Admin"},
    "admin":    {"tenant_admin", "executive_manager", "Admin"},
    "hgs":      {"Admin"},
    "api":      {"tenant_admin", "executive_manager", "Admin"},
}


def get_accessible_modules(user):
    """Kullanıcının erişebileceği modülleri döndür.

    Kontrol sırası:
    1. Tenant paketi → SystemModule → ModuleComponentSlug zinciri
    2. Rol kısıtlamaları
    3. Paketsiz tenant → minimum set
    """
    if user is None:
        return []

    role_name = user.role.name if user.role else None

    # Admin her şeyi görür
    if role_name == "Admin":
        return MODULES

    # Paket kontrolü
    allowed_module_ids = None
    try:
        tenant = user.tenant
        if tenant and tenant.package:
            pkg = tenant.package
            # SubscriptionPackage → SystemModule ilişkisi varsa kullan
            if hasattr(pkg, "system_modules") and pkg.system_modules:
                allowed_module_ids = {m.slug for m in pkg.system_modules if m.slug}
    except Exception:
        pass

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

    # Paketsiz tenant → yalnızca minimum set
    if allowed_module_ids is None and not (user.tenant and getattr(user.tenant, "package", None)):
        result = [m for m in result if m["id"] in _MINIMUM_MODULE_IDS]

    return result
