# -*- coding: utf-8 -*-
"""Proje listesi sayfası için kurum/lider özet KPI ve grafik verileri."""

from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Any

from sqlalchemy import func, or_
from sqlalchemy.exc import ProgrammingError

from models import Project, RaidItem, Task, db
from app_platform.modules.proje.project_list_query import ProjectListFilters, filtered_project_ids

_COMPLETED = ("Tamamlandı", "Done", "Completed")
_RAID_CLOSED = ("Closed", "Kapalı", "Done", "Resolved", "Kapatıldı")

# Grafikte sabit sıra (eksik olanlar 0 ile tamamlanır)
_TASK_STATUS_ORDER = ("Yapılacak", "Devam Ediyor", "Beklemede", "Tamamlandı")
_PRIORITY_ORDER = ("Kritik", "Yüksek", "Orta", "Düşük")
_RAID_TYPES = ("Risk", "Assumption", "Issue", "Dependency")


def _week_start(d: date) -> date:
    return d - timedelta(days=d.weekday())


def build_project_list_overview(
    user,
    kid: int,
    filters: ProjectListFilters | None = None,
) -> dict[str, Any]:
    """
    Filtrelerle eşleşen projeler için toplu metrikler + trend / RAID / sağlık.
    """
    flt = filters or ProjectListFilters()
    today = date.today()
    week_end = today + timedelta(days=7)
    pids = filtered_project_ids(user, kid, flt)

    empty_charts = {
        "task_status": {"labels": list(_TASK_STATUS_ORDER), "data": [0, 0, 0, 0]},
        "project_priority": {"labels": list(_PRIORITY_ORDER), "data": [0, 0, 0, 0]},
        "raid_by_type": {"labels": list(_RAID_TYPES), "data": [0, 0, 0, 0]},
    }

    empty: dict[str, Any] = {
        "total_projects": 0,
        "total_tasks": 0,
        "open_tasks": 0,
        "overdue_tasks": 0,
        "tasks_due_7d": 0,
        "overdue_projects": 0,
        "projects_end_7d": 0,
        "attention": [],
        "charts": empty_charts,
        "weekly_completed": [0, 0, 0, 0],
        "weekly_labels": ["—", "—", "—", "—"],
        "heatmap_weeks": [[None] * 7 for _ in range(4)],
        "raid_open_total": 0,
        "avg_health_score": None,
        "low_health_projects": 0,
    }

    if not pids:
        return empty

    # — Son 4 Pazartesi haftası etiketleri + heatmap (7 gün) —
    week_starts = [_week_start(today - timedelta(weeks=k)) for k in range(3, -1, -1)]
    weekly_labels = [ws.strftime("%d.%m") for ws in week_starts]
    heatmap_weeks: list[list[int | None]] = []
    for ws in week_starts:
        row: list[int | None] = []
        for dweek in range(7):
            day = ws + timedelta(days=dweek)
            if day > today:
                row.append(None)
                continue
            d0 = datetime.combine(day, datetime.min.time())
            d1 = datetime.combine(day + timedelta(days=1), datetime.min.time())
            cnt = (
                db.session.query(func.count(Task.id))
                .filter(
                    Task.project_id.in_(pids),
                    Task.is_archived.is_(False),
                    Task.status.in_(("Tamamlandı", "Done", "Completed")),
                    Task.completed_at.isnot(None),
                    Task.completed_at >= d0,
                    Task.completed_at < d1,
                )
                .scalar()
                or 0
            )
            row.append(int(cnt))
        heatmap_weeks.append(row)
    weekly_completed = [sum(x for x in r if x is not None) for r in heatmap_weeks]

    # — Görev sayıları —
    total_tasks = (
        db.session.query(func.count(Task.id))
        .filter(Task.project_id.in_(pids), Task.is_archived.is_(False))
        .scalar()
        or 0
    )

    open_tasks = (
        db.session.query(func.count(Task.id))
        .filter(
            Task.project_id.in_(pids),
            Task.is_archived.is_(False),
            Task.status.notin_(_COMPLETED),
        )
        .scalar()
        or 0
    )

    overdue_tasks = (
        db.session.query(func.count(Task.id))
        .filter(
            Task.project_id.in_(pids),
            Task.is_archived.is_(False),
            Task.due_date.isnot(None),
            Task.due_date < today,
            Task.status.notin_(_COMPLETED),
        )
        .scalar()
        or 0
    )

    tasks_due_7d = (
        db.session.query(func.count(Task.id))
        .filter(
            Task.project_id.in_(pids),
            Task.is_archived.is_(False),
            Task.due_date.isnot(None),
            Task.due_date >= today,
            Task.due_date <= week_end,
            Task.status.notin_(_COMPLETED),
        )
        .scalar()
        or 0
    )

    overdue_projects = (
        db.session.query(func.count(Project.id))
        .filter(
            Project.id.in_(pids),
            Project.end_date.isnot(None),
            Project.end_date < today,
        )
        .scalar()
        or 0
    )

    projects_end_7d = (
        db.session.query(func.count(Project.id))
        .filter(
            Project.id.in_(pids),
            Project.end_date.isnot(None),
            Project.end_date >= today,
            Project.end_date <= week_end,
        )
        .scalar()
        or 0
    )

    # — Görev durum dağılımı —
    status_rows = (
        db.session.query(Task.status, func.count(Task.id))
        .filter(Task.project_id.in_(pids), Task.is_archived.is_(False))
        .group_by(Task.status)
        .all()
    )
    status_map: dict[str, int] = {}
    for st, cnt in status_rows:
        key = (st or "—").strip() or "—"
        status_map[key] = status_map.get(key, 0) + int(cnt)

    task_labels: list[str] = []
    task_data: list[int] = []
    other_task = 0
    for label in _TASK_STATUS_ORDER:
        task_labels.append(label)
        task_data.append(status_map.pop(label, 0))
    for k, v in sorted(status_map.items(), key=lambda x: -x[1]):
        if k in _TASK_STATUS_ORDER:
            continue
        other_task += v
    if other_task:
        task_labels.append("Diğer")
        task_data.append(other_task)

    # — Proje öncelik dağılımı —
    pri_rows = (
        db.session.query(Project.priority, func.count(Project.id))
        .filter(Project.id.in_(pids))
        .group_by(Project.priority)
        .all()
    )
    pri_map: dict[str, int] = {}
    for pr, cnt in pri_rows:
        key = (pr or "Orta").strip() or "Orta"
        pri_map[key] = pri_map.get(key, 0) + int(cnt)

    pri_labels: list[str] = []
    pri_data: list[int] = []
    other_pri = 0
    for label in _PRIORITY_ORDER:
        pri_labels.append(label)
        pri_data.append(pri_map.pop(label, 0))
    for k, v in sorted(pri_map.items(), key=lambda x: -x[1]):
        if k in _PRIORITY_ORDER:
            continue
        other_pri += v
    if other_pri:
        pri_labels.append("Diğer")
        pri_data.append(other_pri)

    # — RAID (açık); tablo yoksa (PG şeması) grafik/sayaç 0 —
    raid_labels: list[str] = list(_RAID_TYPES)
    raid_data: list[int] = [0, 0, 0, 0]
    raid_open_total = 0
    try:
        raid_open_q = db.session.query(func.count(RaidItem.id)).filter(
            RaidItem.project_id.in_(pids),
            or_(RaidItem.status.is_(None), ~RaidItem.status.in_(_RAID_CLOSED)),
        )
        raid_open_total = int(raid_open_q.scalar() or 0)

        raid_rows = (
            db.session.query(RaidItem.item_type, func.count(RaidItem.id))
            .filter(
                RaidItem.project_id.in_(pids),
                or_(RaidItem.status.is_(None), RaidItem.status.notin_(_RAID_CLOSED)),
            )
            .group_by(RaidItem.item_type)
            .all()
        )
        rmap: dict[str, int] = {}
        for typ, cnt in raid_rows:
            k = (typ or "").strip() or "Diğer"
            rmap[k] = rmap.get(k, 0) + int(cnt)
        raid_labels = []
        raid_data = []
        other_raid = 0
        for label in _RAID_TYPES:
            raid_labels.append(label)
            raid_data.append(rmap.pop(label, 0))
        for k, v in sorted(rmap.items(), key=lambda x: -x[1]):
            other_raid += v
        if other_raid:
            raid_labels.append("Diğer")
            raid_data.append(other_raid)
    except ProgrammingError:
        db.session.rollback()
        raid_open_total = 0
        raid_labels = list(_RAID_TYPES)
        raid_data = [0, 0, 0, 0]

    # — Sağlık skoru —
    avg_health = db.session.query(func.avg(Project.health_score)).filter(Project.id.in_(pids)).scalar()
    low_health = (
        db.session.query(func.count(Project.id))
        .filter(Project.id.in_(pids), Project.health_score.isnot(None), Project.health_score < 50)
        .scalar()
        or 0
    )

    # — Dikkat listesi —
    ot_rows = (
        db.session.query(Task.project_id, func.count(Task.id))
        .filter(
            Task.project_id.in_(pids),
            Task.is_archived.is_(False),
            Task.due_date.isnot(None),
            Task.due_date < today,
            Task.status.notin_(_COMPLETED),
        )
        .group_by(Task.project_id)
        .all()
    )
    overdue_task_by_pid = {int(r[0]): int(r[1]) for r in ot_rows}

    proj_overdue_rows = (
        db.session.query(Project.id, Project.name)
        .filter(
            Project.id.in_(pids),
            Project.end_date.isnot(None),
            Project.end_date < today,
        )
        .all()
    )
    proj_overdue_set = {int(r[0]) for r in proj_overdue_rows}
    names = dict(
        (int(r[0]), r[1])
        for r in db.session.query(Project.id, Project.name).filter(Project.id.in_(pids)).all()
    )

    attention_pids = set(overdue_task_by_pid) | proj_overdue_set
    attention: list[dict[str, Any]] = []
    for pid in attention_pids:
        attention.append(
            {
                "id": pid,
                "name": names.get(pid) or f"Proje #{pid}",
                "overdue_tasks": overdue_task_by_pid.get(pid, 0),
                "project_deadline_overdue": pid in proj_overdue_set,
            }
        )
    attention.sort(
        key=lambda x: (x["project_deadline_overdue"], x["overdue_tasks"]),
        reverse=True,
    )
    attention = attention[:12]

    return {
        "total_projects": len(pids),
        "total_tasks": int(total_tasks),
        "open_tasks": int(open_tasks),
        "overdue_tasks": int(overdue_tasks),
        "tasks_due_7d": int(tasks_due_7d),
        "overdue_projects": int(overdue_projects),
        "projects_end_7d": int(projects_end_7d),
        "attention": attention,
        "charts": {
            "task_status": {"labels": task_labels, "data": task_data},
            "project_priority": {"labels": pri_labels, "data": pri_data},
            "raid_by_type": {"labels": raid_labels, "data": raid_data},
        },
        "weekly_completed": weekly_completed,
        "weekly_labels": weekly_labels,
        "heatmap_weeks": heatmap_weeks,
        "raid_open_total": raid_open_total,
        "avg_health_score": float(avg_health) if avg_health is not None else None,
        "low_health_projects": int(low_health),
    }


def overview_for_export_summary(user, kid: int, filters: ProjectListFilters) -> dict[str, Any]:
    """CSV üst bilgi satırı için hafif özet (aynı filtre)."""
    ov = build_project_list_overview(user, kid, filters)
    return {
        "total_projects": ov["total_projects"],
        "total_tasks": ov["total_tasks"],
        "overdue_tasks": ov["overdue_tasks"],
        "overdue_projects": ov["overdue_projects"],
        "raid_open_total": ov["raid_open_total"],
        "avg_health_score": ov["avg_health_score"],
    }
