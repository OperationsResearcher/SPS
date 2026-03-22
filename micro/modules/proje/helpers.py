# -*- coding: utf-8 -*-
"""Micro Proje modülü — ortak yardımcılar (rotalar ince kalsın)."""

from __future__ import annotations

from datetime import datetime

from flask import request
from flask_login import current_user
from sqlalchemy import delete, insert
from sqlalchemy.orm import joinedload

from app.models.core import User as CoreUser
from app.models.process import Process as AppProcess, ProcessKpi
from models import Project, Task, Surec, db, project_members, project_observers, project_leaders
from utils.task_status import normalize_task_status


def kanban_task_buckets(tasks: list) -> tuple[list, list, list]:
    todo: list = []
    inprog: list = []
    done: list = []
    for t in tasks:
        s = normalize_task_status(t.status) or (t.status or "")
        if s in ("Tamamlandı", "Done", "Tamamlandi"):
            done.append(t)
        elif s in ("Devam Ediyor", "In Progress", "Beklemede"):
            inprog.append(t)
        else:
            todo.append(t)
    return todo, inprog, done


def kurum_id():
    return getattr(current_user, "kurum_id", None) or getattr(current_user, "tenant_id", None)


def tenant_core_users(kid: int | None) -> list[CoreUser]:
    if not kid:
        return []
    return (
        CoreUser.query.filter_by(tenant_id=kid, is_active=True)
        .order_by(CoreUser.first_name, CoreUser.last_name, CoreUser.email)
        .all()
    )


def form_users_payload(users: list) -> list[dict]:
    out: list[dict] = []
    for u in users:
        fn = (getattr(u, "first_name", None) or "").strip()
        ln = (getattr(u, "last_name", None) or "").strip()
        name = f"{fn} {ln}".strip()
        tail = (getattr(u, "username", None) or getattr(u, "email", None) or "").strip()
        if not name:
            name = tail or f"Kullanıcı #{u.id}"
        label = f"{name} ({tail})" if tail else name
        out.append({"id": u.id, "label": label})
    return out


def resolve_manager_id(requested: int | None, kid: int) -> int:
    for uid in (requested, getattr(current_user, "id", None)):
        if uid is None:
            continue
        u = CoreUser.query.filter_by(id=uid, tenant_id=kid, is_active=True).first()
        if u:
            return u.id
    u = CoreUser.query.filter_by(tenant_id=kid, is_active=True).order_by(CoreUser.id).first()
    if u:
        return u.id
    raise ValueError("Kurumda aktif kullanıcı yok")


def _leader_ids_from_assoc_table(project: Project) -> list[int]:
    """project_leaders satırları (ORM `leaders` yerine — legacy user tablosu uyumsuzluğu)."""
    rows = (
        db.session.query(project_leaders.c.user_id)
        .filter(project_leaders.c.project_id == project.id)
        .all()
    )
    ids = [r[0] for r in rows]
    mid = project.manager_id
    if mid and mid in ids:
        return [mid] + [i for i in ids if i != mid]
    return ids or ([mid] if mid else [])


def _member_ids_from_assoc_table(project: Project) -> list[int]:
    return [
        r[0]
        for r in db.session.query(project_members.c.user_id)
        .filter(project_members.c.project_id == project.id)
        .all()
    ]


def _observer_ids_from_assoc_table(project: Project) -> list[int]:
    return [
        r[0]
        for r in db.session.query(project_observers.c.user_id)
        .filter(project_observers.c.project_id == project.id)
        .all()
    ]


def resolve_leader_ids_from_form(kid: int, project: Project | None = None) -> list[int]:
    """Formdan `leaders` (çoklu) veya geriye dönük `manager_id`; düzenlemede form boşsa DB'deki liderler korunur."""
    raw: list[int] = []
    for x in request.form.getlist("leaders"):
        s = str(x).strip()
        if s.isdigit():
            raw.append(int(s))
    if not raw:
        mid = request.form.get("manager_id", type=int)
        if mid:
            raw.append(mid)
    seen: set[int] = set()
    out: list[int] = []
    for uid in raw:
        if uid in seen:
            continue
        u = CoreUser.query.filter_by(id=uid, tenant_id=kid, is_active=True).first()
        if u:
            seen.add(uid)
            out.append(uid)
    if out:
        return out
    if project is not None:
        preserved = _leader_ids_from_assoc_table(project)
        seen2: set[int] = set()
        out2: list[int] = []
        for uid in preserved:
            if uid in seen2:
                continue
            u = CoreUser.query.filter_by(id=uid, tenant_id=kid, is_active=True).first()
            if u:
                seen2.add(uid)
                out2.append(uid)
        if out2:
            return out2
    return [resolve_manager_id(None, kid)]


def sync_project_leaders(project: Project, kid: int, leader_ids: list[int]) -> None:
    """project_leaders tablosunu yazar; `manager_id` ilk lider olarak kalır (API/rapor uyumu)."""
    if not leader_ids:
        raise ValueError("En az bir proje lideri gerekli")
    valid: list[int] = []
    seen: set[int] = set()
    for uid in leader_ids:
        if uid in seen:
            continue
        u = CoreUser.query.filter_by(id=uid, tenant_id=kid, is_active=True).first()
        if u:
            seen.add(u.id)
            valid.append(u.id)
    if not valid:
        raise ValueError("Geçerli lider kullanıcısı yok")
    project.manager_id = valid[0]
    db.session.execute(delete(project_leaders).where(project_leaders.c.project_id == project.id))
    for uid in valid:
        db.session.execute(insert(project_leaders).values(project_id=project.id, user_id=uid))


def project_form_init(project: Project | None) -> dict:
    if not project:
        mid = getattr(current_user, "id", None)
        return {
            "leaderIds": [mid] if mid else [],
            "memberIds": [],
            "observerIds": [],
        }
    return {
        "leaderIds": _leader_ids_from_assoc_table(project),
        "memberIds": _member_ids_from_assoc_table(project),
        "observerIds": _observer_ids_from_assoc_table(project),
    }


def user_ids_from_form(field: str) -> list[int]:
    out: list[int] = []
    for x in request.form.getlist(field):
        s = str(x).strip()
        if s.isdigit():
            out.append(int(s))
    return out


def sync_project_members_observers(project: Project, kid: int) -> None:
    member_ids = user_ids_from_form("members")
    observer_ids = user_ids_from_form("observers")
    uid_set = set(member_ids) | set(observer_ids)

    valid: set[int] = set()
    if uid_set:
        valid = {
            u.id
            for u in CoreUser.query.filter(
                CoreUser.tenant_id == kid,
                CoreUser.is_active.is_(True),
                CoreUser.id.in_(uid_set),
            ).all()
        }

    db.session.execute(delete(project_members).where(project_members.c.project_id == project.id))
    db.session.execute(delete(project_observers).where(project_observers.c.project_id == project.id))

    seen_members: set[int] = set()
    for uid in member_ids:
        if uid not in valid or uid in seen_members:
            continue
        seen_members.add(uid)
        db.session.execute(insert(project_members).values(project_id=project.id, user_id=uid))

    for uid in observer_ids:
        if uid not in valid or uid in seen_members:
            continue
        db.session.execute(insert(project_observers).values(project_id=project.id, user_id=uid))


def load_project(project_id: int) -> Project:
    return Project.query.options(
        joinedload(Project.manager),
        joinedload(Project.leaders),
        joinedload(Project.members),
        joinedload(Project.observers),
    ).get_or_404(project_id)


def kpis_for_tenant():
    tid = getattr(current_user, "tenant_id", None)
    if not tid:
        return []
    return (
        ProcessKpi.query.join(AppProcess)
        .filter(AppProcess.tenant_id == tid, AppProcess.is_active.is_(True), ProcessKpi.is_active.is_(True))
        .order_by(AppProcess.code, ProcessKpi.code, ProcessKpi.id)
        .all()
    )


def parse_date_field(name: str):
    raw = request.form.get(name)
    if not raw:
        return None
    try:
        return datetime.strptime(raw, "%Y-%m-%d").date()
    except ValueError:
        return None
