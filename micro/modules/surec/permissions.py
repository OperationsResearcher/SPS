# -*- coding: utf-8 -*-
"""Süreç Yönetimi — rol ve süreç bazlı yetkiler."""

from __future__ import annotations

from sqlalchemy import or_

from app.models.core import User
from app.models.process import Process


# Kurum / platform yöneticileri (süreç oluşturma-silme dahil tam CRUD)
PRIVILEGED_ROLES = frozenset({"Admin", "tenant_admin", "executive_manager"})


def role_name(user) -> str | None:
    return user.role.name if user and user.role else None


def is_privileged(user) -> bool:
    rn = role_name(user)
    return rn in PRIVILEGED_ROLES if rn else False


def user_assigned_to_process(user, process: Process) -> bool:
    """Süreç lideri, üyesi veya sahibi mi?"""
    if not user or not process:
        return False
    uid = user.id
    if any(u.id == uid for u in (process.leaders or [])):
        return True
    if any(u.id == uid for u in (process.members or [])):
        return True
    if any(u.id == uid for u in (process.owners or [])):
        return True
    return False


def user_can_access_process(user, process: Process) -> bool:
    """Panel / karne / faaliyet sayfalarını görebilir mi?"""
    if is_privileged(user):
        return True
    return user_assigned_to_process(user, process)


def user_is_process_leader(user, process: Process) -> bool:
    """PG / faaliyet CRUD ve (yönetici olmayan) süreç bilgisi düzenleme."""
    if is_privileged(user):
        return True
    if not user or not process:
        return False
    uid = user.id
    if any(u.id == uid for u in (process.leaders or [])):
        return True
    if any(u.id == uid for u in (process.owners or [])):
        return True
    return False


def can_crud_process_entity(user) -> bool:
    """Yeni süreç oluşturma ve süreç silme (soft delete)."""
    return is_privileged(user)


def user_can_edit_process_record(user, process: Process) -> bool:
    """Süreç kartı / API güncelleme (en az bir alt strateji zorunlu)."""
    return user_is_process_leader(user, process)


def user_can_crud_pg_and_activity(user, process: Process) -> bool:
    """Performans göstergesi ve süreç faaliyeti CRUD."""
    return user_is_process_leader(user, process)


def user_can_enter_pgv(user, process: Process) -> bool:
    """PG verisi girişi ve faaliyet aylık takip."""
    return user_can_access_process(user, process)


def user_can_edit_kpi_data_row(user, entry, process: Process) -> bool:
    """PGV satırı güncelleme / silme."""
    if is_privileged(user):
        return True
    if user_is_process_leader(user, process):
        return True
    return entry.user_id == user.id if user and entry else False


def accessible_processes_filter(query, user, tenant_id: int):
    """Tenant aktif süreçleri; ayrıcalıksız kullanıcıda yalnızca atanan süreçler."""
    q = query.filter(Process.tenant_id == tenant_id, Process.is_active.is_(True))
    if is_privileged(user):
        return q
    uid = user.id
    return q.filter(
        or_(
            Process.leaders.any(User.id == uid),
            Process.members.any(User.id == uid),
            Process.owners.any(User.id == uid),
        )
    )
