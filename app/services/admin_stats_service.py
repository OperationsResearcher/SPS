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

    METRICS = (
        "users", "strategies", "sub_strategies", "processes",
        "kpis", "kpi_data", "projects", "tasks",
    )
    SRC = {
        "users": users, "strategies": strategies, "sub_strategies": sub_strategies,
        "processes": processes, "kpis": kpis, "kpi_data": kpi_data,
        "projects": projects, "tasks": tasks,
    }
    TYPE_LABEL = {"dealer": "Bayi", "holding": "Holding"}

    # Kurum başına ham sayım kaydı
    by_id: dict[int, dict] = {}
    for t in tenants:
        rec = {
            "id": t.id,
            "name": t.name,
            "short_name": getattr(t, "short_name", None),
            "tenant_type": getattr(t, "tenant_type", "normal") or "normal",
            "type_label": TYPE_LABEL.get(getattr(t, "tenant_type", "normal"), ""),
            "parent_id": getattr(t, "parent_tenant_id", None),
        }
        for k in METRICS:
            rec[k] = SRC[k].get(t.id, 0)
        by_id[t.id] = rec

    # Hiyerarşi: parent_tenant_id → çocuklar. Üst kurumu aktif-set dışındaysa kök say.
    children: dict[int, list] = {}
    roots: list[dict] = []
    for rec in by_id.values():
        pid = rec["parent_id"]
        if pid and pid in by_id:
            children.setdefault(pid, []).append(rec)
        else:
            roots.append(rec)

    def _sort(recs):
        return sorted(recs, key=lambda r: (r["name"] or "").lower())

    # Görüntüleme satırları: kök → (girintili) alt kurumlar → grubun ara toplamı
    display: list[dict] = []
    grand = {k: 0 for k in METRICS}

    def walk(rec, depth, acc):
        node = dict(rec)
        node["depth"] = depth
        node["kind"] = "tenant"
        node["has_children"] = bool(children.get(rec["id"]))
        display.append(node)
        for k in METRICS:
            acc[k] += rec[k]
            grand[k] += rec[k]
        for ch in _sort(children.get(rec["id"], [])):
            walk(ch, depth + 1, acc)

    for root in _sort(roots):
        kids = children.get(root["id"])
        if kids:
            acc = {k: 0 for k in METRICS}
            walk(root, 0, acc)
            sub = {"kind": "subtotal", "depth": 0,
                   "name": f"{root['name']} — grup toplamı (kendisi + alt kurumlar)"}
            sub.update(acc)
            display.append(sub)
        else:
            walk(root, 0, {k: 0 for k in METRICS})

    return {
        "tenant_count": len(by_id),
        "rows": display,
        "totals": grand,
        "metrics": list(METRICS),
    }
