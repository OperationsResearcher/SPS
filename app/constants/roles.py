"""Merkezi rol sabitleri.

Tüm modüllerde bu modülden import edilmeli:
    from app.constants.roles import ADMIN_ROLES, PRIVILEGED_ROLES, WRITE_ROLES
"""
from __future__ import annotations

from flask_babel import lazy_gettext as _l

# Platform + kurum yöneticileri (tam yetki)
ADMIN_ROLES: frozenset[str] = frozenset({"Admin", "tenant_admin"})

# Üst yönetim dahil genişletilmiş yönetici kümesi
PRIVILEGED_ROLES: frozenset[str] = frozenset({"Admin", "tenant_admin", "executive_manager"})

# Yazma (oluşturma/düzenleme) yetkisi olan roller
WRITE_ROLES: frozenset[str] = PRIVILEGED_ROLES

# Yalnızca platform admini
PLATFORM_ADMIN_ROLES: frozenset[str] = frozenset({"Admin"})

# Standart kullanıcı rolleri (okuma ağırlıklı)
STANDARD_ROLES: frozenset[str] = frozenset({"standard_user", "User", "user"})


# ── Kanonik Türkçe rol etiketleri (tek kaynak) ───────────────────────────────
# L1 Dal 5: UI'da rol gösterimi yalnızca buradan okunur. Dağınık literal YASAK.
# Kullanıcıya görünür → KURALLAR §2 (UI-TERMINOLOJI.md). Kararlar 2026-06-19.
# Değerler lazy_gettext: template/sidebar'da aktif dile göre çevrilir.
# JS'e tojson ile gömerken str()'e çevir (lazy obje serileştirilemez) → role_labels_json().
ROLE_LABELS_TR: dict[str, object] = {
    "Admin": _l("Sistem Yöneticisi"),        # platform admini (tüm kurumlar)
    "tenant_admin": _l("Kurum Yöneticisi"),
    "executive_manager": _l("Üst Yönetim"),
    "standard_user": _l("Kurum Kullanıcısı"),
    # Legacy / atıl roller — yine de tutarlı görünsün
    "User": _l("Kurum Kullanıcısı"),
    "user": _l("Kurum Kullanıcısı"),
}

# Bilinmeyen rol için yedek etiket
ROLE_LABEL_FALLBACK_TR = _l("Kullanıcı")


def role_label_tr(role_name: str | None):
    """Rol kod adını kanonik UI etiketine çevirir (lazy — aktif dile göre)."""
    if not role_name:
        return ROLE_LABEL_FALLBACK_TR
    return ROLE_LABELS_TR.get(role_name, ROLE_LABEL_FALLBACK_TR)


def role_labels_json() -> dict[str, str]:
    """JS'e tojson ile gömmek için düz-metin (aktif dilde çözülmüş) kopya."""
    return {k: str(v) for k, v in ROLE_LABELS_TR.items()}


def is_admin(role_name: str | None) -> bool:
    """Kullanıcının admin rolünde olup olmadığını döner."""
    return bool(role_name and role_name in ADMIN_ROLES)


def is_privileged(role_name: str | None) -> bool:
    """Kullanıcının yetkili rolde olup olmadığını döner."""
    return bool(role_name and role_name in PRIVILEGED_ROLES)
