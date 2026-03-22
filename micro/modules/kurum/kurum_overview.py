# -*- coding: utf-8 -*-
"""Kurum paneli — süreç ve proje özet metrikleri (erişim kapsamına göre)."""

from __future__ import annotations

from datetime import date, timedelta

from sqlalchemy import func, or_

from app.models import db
from app.models.process import (
    ActivityTrack,
    KpiData,
    Process,
    ProcessActivity,
    ProcessKpi,
    ProcessSubStrategyLink,
)
from micro.modules.proje.permissions import accessible_projects_query
from micro.modules.surec.permissions import accessible_processes_filter, is_privileged
from models import Project, RaidItem, Task

# PG veri girişi uyarısı: bu günden eski son veri = "bayat" (kurum standardı)
STALE_KPI_DATA_DAYS = 60

# Tamamlanmış sayılacak görev durumları
_TASK_DONE_STATUSES = frozenset(
    {"Tamamlandı", "Tamamlandi", "Done", "Completed", "Closed", "Kapalı"}
)

# Kapalı sayılacak süreç faaliyeti durumları
_ACTIVITY_CLOSED_STATUSES = frozenset(
    {"Tamamlandı", "Tamamlandi", "Kapalı", "İptal", "Closed", "Cancelled", "Done", "Completed"}
)

# Kapalı RAID kayıtları
_RAID_CLOSED_STATUSES = frozenset(
    {"Closed", "Kapalı", "Tamamlandı", "Resolved", "Done", "Cancelled", "İptal"}
)


def _build_process_metrics(pid_query, today: date) -> dict:
    """
    Yalnızca yeni Process modeli (tenant aktif süreç filtresi pid_query ile verilir).
    """
    process_count = (
        db.session.query(func.count(Process.id))
        .filter(Process.id.in_(pid_query))
        .scalar()
        or 0
    )

    processes_with_pg = (
        db.session.query(func.count(func.distinct(Process.id)))
        .select_from(Process)
        .join(ProcessKpi, Process.id == ProcessKpi.process_id)
        .filter(Process.id.in_(pid_query), ProcessKpi.is_active.is_(True))
        .scalar()
        or 0
    )

    processes_without_strategy = (
        db.session.query(func.count(func.distinct(Process.id)))
        .select_from(Process)
        .outerjoin(ProcessSubStrategyLink, Process.id == ProcessSubStrategyLink.process_id)
        .filter(Process.id.in_(pid_query), ProcessSubStrategyLink.process_id.is_(None))
        .scalar()
        or 0
    )

    active_pg_count = (
        db.session.query(func.count(ProcessKpi.id))
        .filter(
            ProcessKpi.process_id.in_(pid_query),
            ProcessKpi.is_active.is_(True),
        )
        .scalar()
        or 0
    )

    cutoff30 = today - timedelta(days=30)
    kpi_data_rows_30d = (
        db.session.query(func.count(KpiData.id))
        .filter(
            KpiData.process_kpi_id.in_(
                db.session.query(ProcessKpi.id).filter(
                    ProcessKpi.process_id.in_(pid_query),
                    ProcessKpi.is_active.is_(True),
                )
            ),
            KpiData.is_active.is_(True),
            KpiData.data_date >= cutoff30,
        )
        .scalar()
        or 0
    )

    processes_with_kpi_data_30d = (
        db.session.query(func.count(func.distinct(ProcessKpi.process_id)))
        .select_from(ProcessKpi)
        .join(KpiData, KpiData.process_kpi_id == ProcessKpi.id)
        .filter(
            ProcessKpi.process_id.in_(pid_query),
            ProcessKpi.is_active.is_(True),
            KpiData.is_active.is_(True),
            KpiData.data_date >= cutoff30,
        )
        .scalar()
        or 0
    )

    open_process_activities = (
        db.session.query(func.count(ProcessActivity.id))
        .filter(
            ProcessActivity.process_id.in_(pid_query),
            ProcessActivity.is_active.is_(True),
            ~ProcessActivity.status.in_(_ACTIVITY_CLOSED_STATUSES),
        )
        .scalar()
        or 0
    )

    activity_tracks_done_this_month = (
        db.session.query(func.count(ActivityTrack.id))
        .join(ProcessActivity, ActivityTrack.activity_id == ProcessActivity.id)
        .filter(
            ProcessActivity.process_id.in_(pid_query),
            ActivityTrack.year == today.year,
            ActivityTrack.month == today.month,
            ActivityTrack.completed.is_(True),
        )
        .scalar()
        or 0
    )

    # ── Risk / uyarı ─────────────────────────────────────────────────────
    stale_cutoff = today - timedelta(days=STALE_KPI_DATA_DAYS)
    recent_kpi_subq = (
        db.session.query(KpiData.process_kpi_id.label("kpi_id"))
        .filter(
            KpiData.is_active.is_(True),
            KpiData.data_date >= stale_cutoff,
        )
        .distinct()
        .subquery()
    )
    stale_pg_count = (
        db.session.query(func.count(ProcessKpi.id))
        .filter(
            ProcessKpi.process_id.in_(pid_query),
            ProcessKpi.is_active.is_(True),
            ~ProcessKpi.id.in_(db.session.query(recent_kpi_subq.c.kpi_id)),
        )
        .scalar()
        or 0
    )

    overdue_activities = (
        db.session.query(func.count(ProcessActivity.id))
        .filter(
            ProcessActivity.process_id.in_(pid_query),
            ProcessActivity.is_active.is_(True),
            ~ProcessActivity.status.in_(_ACTIVITY_CLOSED_STATUSES),
            ProcessActivity.end_date.isnot(None),
            ProcessActivity.end_date < today,
        )
        .scalar()
        or 0
    )

    pg_incomplete_definition = (
        db.session.query(func.count(ProcessKpi.id))
        .filter(
            ProcessKpi.process_id.in_(pid_query),
            ProcessKpi.is_active.is_(True),
            or_(
                ProcessKpi.period.is_(None),
                ProcessKpi.period == "",
                ProcessKpi.target_value.is_(None),
                ProcessKpi.target_value == "",
            ),
        )
        .scalar()
        or 0
    )

    # ── Performans (ProcessKpi.calculated_score) ──────────────────────────
    pg_scored_count = (
        db.session.query(func.count(ProcessKpi.id))
        .filter(
            ProcessKpi.process_id.in_(pid_query),
            ProcessKpi.is_active.is_(True),
            ProcessKpi.calculated_score.isnot(None),
        )
        .scalar()
        or 0
    )

    pg_low_score_count = (
        db.session.query(func.count(ProcessKpi.id))
        .filter(
            ProcessKpi.process_id.in_(pid_query),
            ProcessKpi.is_active.is_(True),
            ProcessKpi.calculated_score.isnot(None),
            ProcessKpi.calculated_score < 50,
        )
        .scalar()
        or 0
    )

    avg_row = (
        db.session.query(func.avg(ProcessKpi.calculated_score))
        .filter(
            ProcessKpi.process_id.in_(pid_query),
            ProcessKpi.is_active.is_(True),
            ProcessKpi.calculated_score.isnot(None),
        )
        .scalar()
    )
    pg_avg_calculated_score = round(float(avg_row), 1) if avg_row is not None else None

    return {
        "process_count": process_count,
        "processes_with_pg": processes_with_pg,
        "processes_without_strategy": processes_without_strategy,
        "active_pg_count": active_pg_count,
        "kpi_data_rows_30d": kpi_data_rows_30d,
        "processes_with_kpi_data_30d": processes_with_kpi_data_30d,
        "open_process_activities": open_process_activities,
        "activity_tracks_done_this_month": activity_tracks_done_this_month,
        "stale_pg_count": stale_pg_count,
        "overdue_activities": overdue_activities,
        "pg_incomplete_definition": pg_incomplete_definition,
        "pg_scored_count": pg_scored_count,
        "pg_low_score_count": pg_low_score_count,
        "pg_avg_calculated_score": pg_avg_calculated_score,
        "stale_kpi_data_days": STALE_KPI_DATA_DAYS,
    }


def build_kurum_overview(user, tenant_id: int, kurum_id: int | None) -> dict:
    """
    tenant_id: süreç (Process.tenant_id)
    kurum_id: proje (Project.kurum_id); yoksa proje metrikleri 0
    """
    scoped = not is_privileged(user)
    today = date.today()

    pid_scoped = accessible_processes_filter(db.session.query(Process.id), user, tenant_id)
    process_block = _build_process_metrics(pid_scoped, today)

    process_tenant = None
    if is_privileged(user):
        pid_tenant = db.session.query(Process.id).filter(
            Process.tenant_id == tenant_id,
            Process.is_active.is_(True),
        )
        process_tenant = _build_process_metrics(pid_tenant, today)

    # ── Proje (kurum_id yoksa sıfır) ───────────────────────────────────────
    _ZERO_PROJ = {
        "project_count": 0,
        "projects_end_soon": 0,
        "projects_overdue_end": 0,
        "open_tasks": 0,
        "overdue_tasks": 0,
        "tasks_due_next_7_days": 0,
        "open_raid_items": 0,
        "low_health_projects": 0,
    }

    def _build_project_block(*, tenant_wide: bool) -> dict:
        if not kurum_id:
            return dict(_ZERO_PROJ)
        soon = today + timedelta(days=30)
        week = today + timedelta(days=7)

        def _projects():
            if tenant_wide:
                return Project.query.filter(
                    Project.kurum_id == kurum_id,
                    Project.is_archived.is_(False),
                )
            return accessible_projects_query(Project.query, user, kurum_id)

        if tenant_wide:
            proj_ids_q = db.session.query(Project.id).filter(
                Project.kurum_id == kurum_id,
                Project.is_archived.is_(False),
            )
        else:
            proj_ids_q = accessible_projects_query(db.session.query(Project.id), user, kurum_id)

        project_count = _projects().count()
        projects_end_soon = (
            _projects()
            .filter(
                Project.end_date.isnot(None),
                Project.end_date >= today,
                Project.end_date <= soon,
            )
            .count()
        )
        projects_overdue_end = (
            _projects()
            .filter(
                Project.end_date.isnot(None),
                Project.end_date < today,
            )
            .count()
        )
        low_health_projects = (
            _projects()
            .filter(
                Project.health_score.isnot(None),
                Project.health_score < 50,
            )
            .count()
        )

        open_tasks = (
            db.session.query(func.count(Task.id))
            .filter(
                Task.project_id.in_(proj_ids_q),
                Task.is_archived.is_(False),
                ~Task.status.in_(_TASK_DONE_STATUSES),
            )
            .scalar()
            or 0
        )
        overdue_tasks = (
            db.session.query(func.count(Task.id))
            .filter(
                Task.project_id.in_(proj_ids_q),
                Task.is_archived.is_(False),
                ~Task.status.in_(_TASK_DONE_STATUSES),
                Task.due_date.isnot(None),
                Task.due_date < today,
            )
            .scalar()
            or 0
        )
        tasks_due_next_7_days = (
            db.session.query(func.count(Task.id))
            .filter(
                Task.project_id.in_(proj_ids_q),
                Task.is_archived.is_(False),
                ~Task.status.in_(_TASK_DONE_STATUSES),
                Task.due_date.isnot(None),
                Task.due_date >= today,
                Task.due_date <= week,
            )
            .scalar()
            or 0
        )
        open_raid_items = (
            db.session.query(func.count(RaidItem.id))
            .filter(
                RaidItem.project_id.in_(proj_ids_q),
                ~RaidItem.status.in_(_RAID_CLOSED_STATUSES),
            )
            .scalar()
            or 0
        )

        return {
            "project_count": project_count,
            "projects_end_soon": projects_end_soon,
            "projects_overdue_end": projects_overdue_end,
            "open_tasks": open_tasks,
            "overdue_tasks": overdue_tasks,
            "tasks_due_next_7_days": tasks_due_next_7_days,
            "open_raid_items": open_raid_items,
            "low_health_projects": low_health_projects,
        }

    project_block = _build_project_block(tenant_wide=False)
    project_tenant = None
    if kurum_id and is_privileged(user):
        project_tenant = _build_project_block(tenant_wide=True)

    return {
        "scoped": scoped,
        "process": process_block,
        "process_tenant": process_tenant,
        "project": project_block,
        "project_tenant": project_tenant,
    }
