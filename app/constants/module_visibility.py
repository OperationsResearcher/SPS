# -*- coding: utf-8 -*-
"""Merkezi modül görünürlük katmanı — rol + bağlamsal liderlik ekseni.

Tek gerçek kaynak: docs/paketler/ROL-GORUNUM-KATMANI.md

İki eksen ayrıdır ve AND'lenir (belge §3):
  - PAKET ekseni (tenant düzeyi)  → get_accessible_modules içindeki paket kapısı.
  - ROL/LİDERLİK ekseni (kullanıcı düzeyi) → bu dosyadaki can_see_module().

can_see_module() YALNIZCA rol/liderlik eksenini cevaplar; paket eksenini
cevaplamaz. Nihai görünürlük = paket_izinli AND can_see_module.

Not (belge §3): Düzenlenecek registry dosyası fiziksel olarak
micro/core/module_registry.py'dir; runtime `app_platform.core...` bir alias.
"""
from __future__ import annotations

from flask import g

from app.constants.roles import (
    ADMIN_ROLES,
    PLATFORM_ADMIN_ROLES,
    PRIVILEGED_ROLES,
)

# ── Statik rol eşlemesi (belge §4 tablosu) ──────────────────────────────────
# Bağlamsal (liderlik/üyelik) modüller AYRI ele alınır; buraya konmaz.
_CONTEXTUAL = {"surec", "proje", "k_radar"}

# Rol kapısı olmayan (paket açıksa herkese) modüller.
_ALWAYS = {"masaustu", "bireysel", "kurum", "ayarlar", "bildirim"}

# Belirli rol kümesi gerektiren modüller → izin verilen role.name seti.
_ROLE_GATED: dict[str, frozenset[str]] = {
    "sp":       PRIVILEGED_ROLES,          # Stratejik Planlama + Savaş Odası
    "analiz":   PRIVILEGED_ROLES,          # Performans Analitiği
    "k_rapor":  PRIVILEGED_ROLES,          # K-Rapor
    "raporlar": PRIVILEGED_ROLES,          # İleri raporlama
    "admin":    ADMIN_ROLES,               # Yönetim Paneli (Admin + tenant_admin)
    "api":      PLATFORM_ADMIN_ROLES,      # API Dokümantasyonu (yalnız platform Admin)
}


def _role_name(user) -> str | None:
    return user.role.name if user and user.role else None


def can_see_module(user, module_id: str) -> bool:
    """Kullanıcı bu modülü rol/liderlik ekseninde görebilir mi?

    Paket eksenini KAPSAMAZ (o get_accessible_modules'te ayrı AND'lenir).
    Platform Admin her şeyi görür (savunma amaçlı bypass, belge §8).
    """
    role = _role_name(user)
    if role in PLATFORM_ADMIN_ROLES:
        return True

    if module_id in _ALWAYS:
        return True

    gated = _ROLE_GATED.get(module_id)
    if gated is not None:
        return role in gated

    if module_id in _CONTEXTUAL:
        return _can_see_contextual(user, module_id, role)

    # Tanımsız modül → varsayılan güvenli: yalnız privileged.
    return role in PRIVILEGED_ROLES


def _can_see_contextual(user, module_id: str, role: str | None) -> bool:
    """Süreç/Proje/K-Radar: privileged VEYA bağlamsal liderlik/üyelik.

    - surec/proje: herhangi bir süreç/projeye ÜYE veya LİDER ise görünür.
    - k_radar:     yalnızca LİDER ise görünür (üye HARİÇ — belge §5).

    permissions.py fonksiyonları lazy import edilir (import döngüsü riski).
    Sidebar aynı request'te çok kez çağrılabileceğinden sonuç g'de cache'lenir.
    """
    if role in PRIVILEGED_ROLES:
        return True
    if not user or not getattr(user, "id", None):
        return False

    if module_id == "k_radar":
        return _cached(user, "leads_process", _leads_any_process) or \
               _cached(user, "leads_project", _leads_any_project)

    # surec / proje → üye veya lider
    if module_id == "surec":
        return _cached(user, "has_process", _has_any_process)
    if module_id == "proje":
        return _cached(user, "has_project", _has_any_project)
    return False


# ── Bağlamsal sinyal — lazy import sarmalayıcılar ───────────────────────────
def _has_any_process(user) -> bool:
    from micro.modules.surec.permissions import user_has_any_process
    return user_has_any_process(user)


def _leads_any_process(user) -> bool:
    from micro.modules.surec.permissions import user_leads_any_process
    return user_leads_any_process(user)


def _has_any_project(user) -> bool:
    from micro.modules.proje.permissions import user_has_any_project
    return user_has_any_project(user)


def _leads_any_project(user) -> bool:
    from micro.modules.proje.permissions import user_leads_any_project
    return user_leads_any_project(user)


def _cached(user, key: str, fn) -> bool:
    """Request-scope memoize (flask.g). Sidebar N modül × aynı sorgu → tek kez.
    g yoksa (uygulama bağlamı dışı) doğrudan hesapla."""
    try:
        store = g.setdefault("_module_vis_cache", {})
    except Exception:
        return bool(fn(user))
    ck = (getattr(user, "id", None), key)
    if ck not in store:
        store[ck] = bool(fn(user))
    return store[ck]
