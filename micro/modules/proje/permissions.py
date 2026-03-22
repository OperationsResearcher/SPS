# -*- coding: utf-8 -*-
"""Proje Yönetimi — süreç yönetimi ile paralel yetki modeli."""

from __future__ import annotations

from sqlalchemy import or_

from app.models.core import User
from models import Project, db, project_members, project_observers, project_leaders


# Kurum / platform yöneticileri (süreç modülüyle aynı)
PRIVILEGED_ROLES = frozenset({"Admin", "tenant_admin", "executive_manager"})


def role_name(user) -> str | None:
    return user.role.name if user and user.role else None


def is_privileged(user) -> bool:
    rn = role_name(user)
    return rn in PRIVILEGED_ROLES if rn else False


def _uid(user) -> int | None:
    return user.id if user else None


def user_is_project_manager(user, project: Project) -> bool:
    """Proje yöneticisi / lideri (çoklu lider tablosu + geriye dönük manager_id)."""
    if not user or not project:
        return False
    uid = _uid(user)
    if uid is None:
        return False
    if project.manager_id == uid:
        return True
    ex = (
        db.session.query(project_leaders)
        .filter(project_leaders.c.project_id == project.id, project_leaders.c.user_id == uid)
        .first()
    )
    return ex is not None


def user_is_project_member(user, project: Project) -> bool:
    """Üye tablosunda kayıtlı mı?"""
    if not user or not project:
        return False
    uid = _uid(user)
    exists = (
        db.session.query(project_members)
        .filter(project_members.c.project_id == project.id, project_members.c.user_id == uid)
        .first()
    )
    return exists is not None


def user_is_project_observer(user, project: Project) -> bool:
    if not user or not project:
        return False
    uid = _uid(user)
    exists = (
        db.session.query(project_observers)
        .filter(project_observers.c.project_id == project.id, project_observers.c.user_id == uid)
        .first()
    )
    return exists is not None


def user_assigned_to_project(user, project: Project) -> bool:
    """Yönetici, üye veya gözlemci mi? (süreç: lider+üye+sahip)"""
    if not user or not project:
        return False
    if user_is_project_manager(user, project):
        return True
    if user_is_project_member(user, project):
        return True
    if user_is_project_observer(user, project):
        return True
    return False


def user_can_access_project(user, project: Project) -> bool:
    """Projeyi görüntüleme (detay, liste filtre)."""
    if is_privileged(user):
        return True
    if not user or not project:
        return False
    kurum_id = getattr(user, "kurum_id", None) or getattr(user, "tenant_id", None)
    if project.kurum_id != kurum_id:
        return False
    return user_assigned_to_project(user, project)


def user_is_project_leader(user, project: Project) -> bool:
    """Yapılandırma / proje düzenleme / görev CRUD eşiği (süreç lideri + sahip).

    Birden fazla proje lideri `project_leaders` ile; `manager_id` birincil lider kaydıdır.
    """
    if is_privileged(user):
        return True
    return user_is_project_manager(user, project)


def user_can_edit_tasks(user, project: Project) -> bool:
    """Görev oluşturma/düzenleme: yönetici veya üye (gözlemci değil)."""
    if is_privileged(user):
        return True
    if not user or not project:
        return False
    kurum_id = getattr(user, "kurum_id", None) or getattr(user, "tenant_id", None)
    if project.kurum_id != kurum_id:
        return False
    if user_is_project_manager(user, project):
        return True
    if user_is_project_member(user, project):
        return True
    return False


def can_crud_project_portfolio(user) -> bool:
    """Stratejik portföy ve kurumsal proje oluşturma (üst yönetim)."""
    return is_privileged(user)


def accessible_projects_query(base_query, user, kurum_id: int):
    """Tenant/kurum projeleri; ayrıcalıksız kullanıcıda yalnızca atananlar."""
    q = base_query.filter(Project.kurum_id == kurum_id, Project.is_archived.is_(False))
    if is_privileged(user):
        return q
    uid = _uid(user)
    if not uid:
        return q.filter(False)
    return q.filter(
        or_(
            Project.manager_id == uid,
            Project.id.in_(
                db.session.query(project_leaders.c.project_id).filter(project_leaders.c.user_id == uid)
            ),
            Project.id.in_(
                db.session.query(project_members.c.project_id).filter(project_members.c.user_id == uid)
            ),
            Project.id.in_(
                db.session.query(project_observers.c.project_id).filter(project_observers.c.user_id == uid)
            ),
        )
    )
