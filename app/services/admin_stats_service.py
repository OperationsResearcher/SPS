"""Admin Araçları — İstatistikler servisi.

Sistemdeki kurum (tenant) bazında sayımları toplar: kullanıcı, ana/alt strateji,
süreç, PG (ProcessKpi), PG verisi (KpiData), portföy proje ve proje task'ı.

Tasarım notu: Her metrik için kurum başına ayrı sorgu (N+1) YERİNE, metrik başına
TEK `GROUP BY tenant_id` sorgusu çalışır → sabit sayıda sorgu, çok kurumda da hızlı.
Salt-okuma; hiçbir veri değiştirmez.
"""
from __future__ import annotations

from sqlalchemy import func

from extensions import db
from app.models.core import Tenant, User, Strategy, SubStrategy
from app.models.process import Process, ProcessKpi, KpiData
from app.models.portfolio_project import Project, Task


def _group_counts(query) -> dict[int, int]:
    """(tenant_id, count) satırlarını {tenant_id: count} sözlüğüne çevirir."""
    return {tid: cnt for tid, cnt in query.all() if tid is not None}


def collect_statistics() -> dict:
    """Kurum bazında istatistikleri ve sistem toplamlarını döndürür.

    Tüm sayımlar aktif kayıtlar (is_active=True) üzerinden yapılır; Task modelinde
    soft-delete alanı olmadığından task'lar olduğu gibi sayılır.
    """
    # Kurumlar (aktif) — alfabetik
    tenants = (
        Tenant.query
        .filter(Tenant.is_active.is_(True))
        .order_by(Tenant.name.asc())
        .all()
    )

    # ── Metrik başına tek GROUP BY sorgusu ──
    users = _group_counts(
        db.session.query(User.tenant_id, func.count(User.id))
        .filter(User.is_active.is_(True))
        .group_by(User.tenant_id)
    )
    strategies = _group_counts(
        db.session.query(Strategy.tenant_id, func.count(Strategy.id))
        .filter(Strategy.is_active.is_(True))
        .group_by(Strategy.tenant_id)
    )
    sub_strategies = _group_counts(
        db.session.query(Strategy.tenant_id, func.count(SubStrategy.id))
        .join(SubStrategy, SubStrategy.strategy_id == Strategy.id)
        .filter(SubStrategy.is_active.is_(True))
        .group_by(Strategy.tenant_id)
    )
    processes = _group_counts(
        db.session.query(Process.tenant_id, func.count(Process.id))
        .filter(Process.is_active.is_(True))
        .group_by(Process.tenant_id)
    )
    kpis = _group_counts(
        db.session.query(Process.tenant_id, func.count(ProcessKpi.id))
        .join(ProcessKpi, ProcessKpi.process_id == Process.id)
        .filter(Process.is_active.is_(True), ProcessKpi.is_active.is_(True))
        .group_by(Process.tenant_id)
    )
    kpi_data = _group_counts(
        db.session.query(Process.tenant_id, func.count(KpiData.id))
        .select_from(KpiData)
        .join(ProcessKpi, KpiData.process_kpi_id == ProcessKpi.id)
        .join(Process, ProcessKpi.process_id == Process.id)
        .filter(KpiData.is_active.is_(True))
        .group_by(Process.tenant_id)
    )
    projects = _group_counts(
        db.session.query(Project.tenant_id, func.count(Project.id))
        .filter(Project.is_active.is_(True))
        .group_by(Project.tenant_id)
    )
    tasks = _group_counts(
        db.session.query(Project.tenant_id, func.count(Task.id))
        .join(Task, Task.project_id == Project.id)
        .filter(Project.is_active.is_(True))
        .group_by(Project.tenant_id)
    )

    rows = []
    totals = {k: 0 for k in (
        "users", "strategies", "sub_strategies", "processes",
        "kpis", "kpi_data", "projects", "tasks",
    )}
    for t in tenants:
        row = {
            "id": t.id,
            "name": t.name,
            "short_name": getattr(t, "short_name", None),
            "is_sub": bool(getattr(t, "parent_tenant_id", None)),
            "users": users.get(t.id, 0),
            "strategies": strategies.get(t.id, 0),
            "sub_strategies": sub_strategies.get(t.id, 0),
            "processes": processes.get(t.id, 0),
            "kpis": kpis.get(t.id, 0),
            "kpi_data": kpi_data.get(t.id, 0),
            "projects": projects.get(t.id, 0),
            "tasks": tasks.get(t.id, 0),
        }
        for k in totals:
            totals[k] += row[k]
        rows.append(row)

    return {
        "tenant_count": len(rows),
        "rows": rows,
        "totals": totals,
    }
