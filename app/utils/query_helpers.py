"""Tekrar eden DB sorgu kalıpları için yardımcılar.

Kullanım:
    from app.utils.query_helpers import get_tenant_user, get_tenant_process

    user = get_tenant_user(user_id, tenant_id)          # None veya User
    proc = get_tenant_process(process_id, tenant_id)    # None veya Process
"""
from __future__ import annotations

from typing import Optional


def get_tenant_user(user_id: int, tenant_id: int) -> Optional["User"]:
    """Aynı tenant'a ait aktif kullanıcıyı döner; yoksa None."""
    from app.models.core import User
    return User.query.filter_by(id=user_id, tenant_id=tenant_id, is_active=True).first()


def get_tenant_process(process_id: int, tenant_id: int) -> Optional["Process"]:
    """Aynı tenant'a ait aktif süreci döner; yoksa None."""
    from app.models.process import Process
    return Process.query.filter_by(id=process_id, tenant_id=tenant_id, is_active=True).first()


def require_tenant_user(user_id: int, tenant_id: int) -> "User":
    """get_tenant_user — bulunamazsa 404 döner (Flask abort)."""
    from flask import abort
    u = get_tenant_user(user_id, tenant_id)
    if not u:
        abort(404)
    return u


def require_tenant_process(process_id: int, tenant_id: int) -> "Process":
    """get_tenant_process — bulunamazsa 404 döner (Flask abort)."""
    from flask import abort
    p = get_tenant_process(process_id, tenant_id)
    if not p:
        abort(404)
    return p
