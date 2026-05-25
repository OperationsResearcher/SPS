"""Holding konsolide dashboard servisi (Sprint D).

Bir holding'in TÜM alt-tenant'larının özetini tek tabloda toplar.
Kullanıcıya gösterilen veriler salt-okur (Holding policy).

Kullanım:
    from app.services.holding_consolidated_service import build_holding_snapshot
    data = build_holding_snapshot(holding_tenant_id)
"""
from __future__ import annotations

import datetime as _dt
from typing import Optional

from extensions import db
from app.models.core import Tenant, User
from app.services.exec_dashboard_service import build_exec_snapshot


def build_holding_snapshot(holding_tenant_id: int) -> dict:
    """Holding ve tüm alt-tenant'ları için konsolide snapshot.

    Dönen:
        {
          "holding": {id, name},
          "sub_tenants": [
            {id, name, is_active, health_score, kpi_total, kpi_on_target_pct,
             initiative_total, risk_critical, anomaly_high, users_count,
             last_activity}
          ],
          "totals": {
            "tenant_count", "active_count", "users_total", "kpi_total",
            "initiative_total", "avg_health", "risk_critical_sum",
            "anomaly_high_sum"
          }
        }
    """
    holding = Tenant.query.get(holding_tenant_id)
    if not holding:
        return {"error": "Holding tenant bulunamadı."}
    if holding.tenant_type != "holding":
        return {"error": "Bu tenant bir holding değil."}

    subs = Tenant.query.filter_by(parent_tenant_id=holding.id).order_by(Tenant.name).all()

    sub_data = []
    for sub in subs:
        snap = None
        try:
            snap = build_exec_snapshot(sub.id)
        except Exception:
            snap = None

        users_count = User.query.filter_by(tenant_id=sub.id, is_active=True).count()

        # Son aktivite — basit yaklaşım: en son kpi_data tarihi (lazy import edilen tablodan)
        try:
            from app.models.process import KpiData, ProcessKpi, Process
            last_dt = (
                db.session.query(db.func.max(KpiData.created_at))
                .join(ProcessKpi, KpiData.process_kpi_id == ProcessKpi.id)
                .join(Process, ProcessKpi.process_id == Process.id)
                .filter(Process.tenant_id == sub.id)
                .scalar()
            )
        except Exception:
            last_dt = None

        sub_data.append({
            "id": sub.id,
            "name": sub.name,
            "short_name": sub.short_name,
            "is_active": sub.is_active,
            "users_count": users_count,
            "last_activity": last_dt.isoformat() if last_dt else None,
            "health_score": (snap or {}).get("health_score"),
            "kpi_total": ((snap or {}).get("kpi") or {}).get("total", 0),
            "kpi_with_data": ((snap or {}).get("kpi") or {}).get("with_data", 0),
            "kpi_on_target_pct": ((snap or {}).get("kpi") or {}).get("on_target_pct", 0),
            "strategy_count": ((snap or {}).get("strategy") or {}).get("count", 0),
            "initiative_total": ((snap or {}).get("initiative") or {}).get("total", 0),
            "risk_critical": ((snap or {}).get("risk") or {}).get("critical", 0),
            "anomaly_high": ((snap or {}).get("anomaly") or {}).get("high", 0),
            "activity_overdue": ((snap or {}).get("activity") or {}).get("overdue", 0),
        })

    # Aggregate
    active_subs = [s for s in sub_data if s["is_active"]]
    health_scores = [s["health_score"] for s in active_subs if s["health_score"] is not None]
    avg_health = round(sum(health_scores) / len(health_scores), 1) if health_scores else None

    return {
        "holding": {
            "id": holding.id,
            "name": holding.name,
            "short_name": holding.short_name,
        },
        "sub_tenants": sub_data,
        "totals": {
            "tenant_count": len(sub_data),
            "active_count": len(active_subs),
            "users_total": sum(s["users_count"] for s in sub_data),
            "kpi_total": sum(s["kpi_total"] for s in sub_data),
            "initiative_total": sum(s["initiative_total"] for s in sub_data),
            "avg_health": avg_health,
            "risk_critical_sum": sum(s["risk_critical"] for s in sub_data),
            "anomaly_high_sum": sum(s["anomaly_high"] for s in sub_data),
            "activity_overdue_sum": sum(s["activity_overdue"] for s in sub_data),
        },
        "generated_at": _dt.datetime.utcnow().isoformat(),
    }
