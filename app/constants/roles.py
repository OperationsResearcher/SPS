"""Merkezi rol sabitleri.

Tüm modüllerde bu modülden import edilmeli:
    from app.constants.roles import ADMIN_ROLES, PRIVILEGED_ROLES, WRITE_ROLES
"""
from __future__ import annotations

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


def is_admin(role_name: str | None) -> bool:
    """Kullanıcının admin rolünde olup olmadığını döner."""
    return bool(role_name and role_name in ADMIN_ROLES)


def is_privileged(role_name: str | None) -> bool:
    """Kullanıcının yetkili rolde olup olmadığını döner."""
    return bool(role_name and role_name in PRIVILEGED_ROLES)
