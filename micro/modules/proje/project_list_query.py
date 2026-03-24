# -*- coding: utf-8 -*-
"""Proje listesi — filtre, sıralama, sorgu oluşturma."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Any

from flask import Request
from sqlalchemy import and_, exists, func, or_
from sqlalchemy.orm import Query

from models import Project, Task, db, project_leaders, project_members, project_observers, project_related_processes
from micro.modules.proje.permissions import accessible_projects_query, is_privileged

_COMPLETED = ("Tamamlandı", "Done", "Completed")


@dataclass
class ProjectListFilters:
    scope: str = "all"  # all | my (yalnızca ayrıcalıklı)
    q: str = ""
    priority: str = ""
    end_from: date | None = None
    end_to: date | None = None
    start_from: date | None = None
    start_to: date | None = None
    leader_id: int | None = None
    surec_id: int | None = None
    overdue_only: bool = False
    due_soon_only: bool = False
    sort: str = "updated"  # updated | end_date | name | overdue

    def query_args(self) -> dict[str, Any]:
        """url_for / export için GET parametreleri (boşlar atlanır)."""
        d: dict[str, Any] = {}
        if self.scope == "my":
            d["scope"] = "my"
        if self.q:
            d["q"] = self.q
        if self.priority:
            d["priority"] = self.priority
        if self.end_from:
            d["end_from"] = self.end_from.isoformat()
        if self.end_to:
            d["end_to"] = self.end_to.isoformat()
        if self.start_from:
            d["start_from"] = self.start_from.isoformat()
        if self.start_to:
            d["start_to"] = self.start_to.isoformat()
        if self.leader_id is not None:
            d["leader_id"] = self.leader_id
        if self.surec_id is not None:
            d["surec_id"] = self.surec_id
        if self.overdue_only:
            d["overdue_only"] = "1"
        if self.due_soon_only:
            d["due_soon"] = "1"
        if self.sort and self.sort != "updated":
            d["sort"] = self.sort
        return d


def parse_project_list_filters(request: Request, privileged: bool) -> ProjectListFilters:
    scope = (request.args.get("scope") or "all").strip().lower()
    if scope not in ("all", "my"):
        scope = "all"
    if not privileged:
        scope = "all"

    def _d(name: str) -> date | None:
        raw = request.args.get(name)
        if not raw:
            return None
        try:
            return datetime.strptime(raw.strip(), "%Y-%m-%d").date()
        except ValueError:
            return None

    leader_id = request.args.get("leader_id", type=int)
    surec_id = request.args.get("surec_id", type=int)
    sort = (request.args.get("sort") or "updated").strip().lower()
    if sort not in ("updated", "end_date", "name", "overdue"):
        sort = "updated"

    return ProjectListFilters(
        scope=scope,
        q=(request.args.get("q") or "").strip(),
        priority=(request.args.get("priority") or "").strip(),
        end_from=_d("end_from"),
        end_to=_d("end_to"),
        start_from=_d("start_from"),
        start_to=_d("start_to"),
        leader_id=leader_id,
        surec_id=surec_id,
        overdue_only=request.args.get("overdue_only") in ("1", "true", "on", "yes"),
        due_soon_only=request.args.get("due_soon") in ("1", "true", "on", "yes"),
        sort=sort,
    )


def _base_projects_query(user, kid: int, scope: str) -> Query:
    if not is_privileged(user):
        return accessible_projects_query(Project.query, user, kid)

    q = Project.query.filter(Project.kurum_id == kid, Project.is_archived.is_(False))
    if scope != "my":
        return q

    uid = getattr(user, "id", None)
    if uid is None:
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


def build_filtered_projects_query(user, kid: int, filters: ProjectListFilters) -> Query:
    today = date.today()
    week_end = today + timedelta(days=7)

    q = _base_projects_query(user, kid, filters.scope)

    if filters.q:
        pat = f"%{filters.q}%"
        q = q.filter(or_(Project.name.ilike(pat), Project.description.ilike(pat)))
    if filters.priority:
        q = q.filter(Project.priority == filters.priority)

    if filters.end_from is not None:
        q = q.filter(Project.end_date.isnot(None), Project.end_date >= filters.end_from)
    if filters.end_to is not None:
        q = q.filter(Project.end_date.isnot(None), Project.end_date <= filters.end_to)

    if filters.start_from is not None:
        q = q.filter(Project.start_date.isnot(None), Project.start_date >= filters.start_from)
    if filters.start_to is not None:
        q = q.filter(Project.start_date.isnot(None), Project.start_date <= filters.start_to)

    if filters.leader_id is not None:
        lid = filters.leader_id
        q = q.filter(
            or_(
                Project.manager_id == lid,
                Project.id.in_(
                    db.session.query(project_leaders.c.project_id).filter(project_leaders.c.user_id == lid)
                ),
            )
        )

    if filters.surec_id is not None:
        sid = filters.surec_id
        q = q.filter(
            Project.id.in_(
                db.session.query(project_related_processes.c.project_id).filter(
                    project_related_processes.c.surec_id == sid
                )
            )
        )

    task_overdue_exists = exists().where(
        Task.project_id == Project.id,
        Task.is_archived.is_(False),
        Task.due_date.isnot(None),
        Task.due_date < today,
        Task.status.notin_(_COMPLETED),
    )
    proj_end_overdue = and_(Project.end_date.isnot(None), Project.end_date < today)

    task_soon_exists = exists().where(
        Task.project_id == Project.id,
        Task.is_archived.is_(False),
        Task.due_date.isnot(None),
        Task.due_date >= today,
        Task.due_date <= week_end,
        Task.status.notin_(_COMPLETED),
    )
    proj_end_soon = and_(
        Project.end_date.isnot(None),
        Project.end_date >= today,
        Project.end_date <= week_end,
    )

    if filters.overdue_only:
        q = q.filter(or_(task_overdue_exists, proj_end_overdue))
    if filters.due_soon_only:
        q = q.filter(or_(task_soon_exists, proj_end_soon))

    # — Sıralama —
    if filters.sort == "name":
        q = q.order_by(Project.name.asc())
    elif filters.sort == "end_date":
        q = q.order_by(Project.end_date.asc().nullslast(), Project.name.asc())
    elif filters.sort == "overdue":
        overdue_sub = (
            db.session.query(
                Task.project_id.label("pid"),
                func.count(Task.id).label("oc"),
            )
            .filter(
                Task.is_archived.is_(False),
                Task.due_date.isnot(None),
                Task.due_date < today,
                Task.status.notin_(_COMPLETED),
            )
            .group_by(Task.project_id)
            .subquery()
        )
        q = q.outerjoin(overdue_sub, overdue_sub.c.pid == Project.id)
        q = q.order_by(func.coalesce(overdue_sub.c.oc, 0).desc(), Project.name.asc())
    else:
        q = q.order_by(Project.updated_at.desc().nullslast(), Project.created_at.desc())

    return q


def filtered_project_ids(user, kid: int, filters: ProjectListFilters) -> list[int]:
    q = build_filtered_projects_query(user, kid, filters)
    # overdue sıralamasında outer join tekrar satır üretebilir
    # PostgreSQL: DISTINCT sorgusunda ORDER BY kolonları select listede olmalı.
    # Burada yalnızca ID kümesi gerektiği için sıralamayı temizleyip distinct alıyoruz.
    rows = q.order_by(None).with_entities(Project.id).distinct().all()
    return sorted({int(r[0]) for r in rows})
