# -*- coding: utf-8 -*-
"""Proje ekranlarında kullanıcı adlarını CoreUser ile çözümle (LegacyUser ilişkisi eksik kalabiliyor)."""

from __future__ import annotations

from extensions import db
from app.models.core import User as CoreUser
from app.models.portfolio_project import (
    Project,
    project_leaders,
    project_members,
    project_observers,
)


def _label_from_core(u: CoreUser) -> str:
    fn = (u.first_name or "").strip()
    ln = (u.last_name or "").strip()
    name = f"{fn} {ln}".strip()
    tail = (u.email or "").strip()
    if not name:
        return tail or f"Kullanıcı #{u.id}"
    return f"{name} ({tail})" if tail else name


def collect_project_user_ids(project: Project) -> set[int]:
    """Etiket haritası için ID'ler — ilişki tabloları / leader_user_ids (legacy ORM boş kalabiliyor)."""
    ids: set[int] = set(project.leader_user_ids())
    ids.update(project.member_user_ids())
    ids.update(project.observer_user_ids())
    return ids


def collect_projects_user_ids(projects: list) -> set[int]:
    """Liste görünümü için toplu ID toplama — proje başına 3 sorgu yerine toplam 3 sorgu (N+1 önlemi).

    Davranış `collect_project_user_ids` ile birebir: lider tablosu boşsa manager_id eklenir.
    """
    pids = [p.id for p in projects]
    if not pids:
        return set()

    leaders_by_pid: dict[int, list[int]] = {}
    for pid, uid in (
        db.session.query(project_leaders.c.project_id, project_leaders.c.user_id)
        .filter(project_leaders.c.project_id.in_(pids))
        .all()
    ):
        leaders_by_pid.setdefault(pid, []).append(uid)

    ids: set[int] = set()
    for table in (project_members, project_observers):
        ids.update(
            r[0]
            for r in db.session.query(table.c.user_id)
            .filter(table.c.project_id.in_(pids))
            .all()
        )

    for p in projects:
        lids = leaders_by_pid.get(p.id)
        if lids:
            ids.update(lids)
        elif p.manager_id:
            ids.add(p.manager_id)
    return ids


def build_user_labels_map(user_ids: set[int], tenant_id: int | None) -> dict[int, str]:
    if not user_ids or not tenant_id:
        return {}
    users = CoreUser.query.filter(
        CoreUser.id.in_(user_ids),
        CoreUser.tenant_id == tenant_id,
        CoreUser.is_active.is_(True),
    ).all()
    return {u.id: _label_from_core(u) for u in users}


def user_display(labels: dict[int, str], uid: int | None, legacy_obj=None) -> str:
    if uid is None:
        return "—"
    if uid in labels:
        return labels[uid]
    if legacy_obj is not None:
        fn = (getattr(legacy_obj, "first_name", None) or "").strip()
        ln = (getattr(legacy_obj, "last_name", None) or "").strip()
        un = (getattr(legacy_obj, "username", None) or getattr(legacy_obj, "email", None) or "").strip()
        name = f"{fn} {ln}".strip()
        if name or un:
            return f"{name} ({un})".strip() if un and name else (name or un)
    return f"#{uid}"
