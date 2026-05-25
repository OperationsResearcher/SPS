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


def build_sub_tenant_drilldown(holding_tenant_id: int, sub_tenant_id: int) -> dict:
    """Bir holding'in belirli alt-tenant'ı için detay drill-down.

    Yetki: ÇAĞIRAN tarafından doğrulanmalı — bu fonksiyon sadece veri toplar.
    Caller sub_tenant.parent_tenant_id == holding_tenant_id olduğunu kontrol etmeli.

    Dönen:
        {
          "sub_tenant": {id, name, ...},
          "snapshot": <exec_dashboard.build_exec_snapshot çıktısı>,
          "initiatives": [...],
          "risks": [...],
          "scenarios_count": int,
        }
    """
    sub = Tenant.query.get(sub_tenant_id)
    if not sub:
        return {"error": "Alt-tenant bulunamadı."}
    if sub.parent_tenant_id != holding_tenant_id:
        return {"error": "Bu alt-tenant başka bir holding'e ait."}

    try:
        snap = build_exec_snapshot(sub.id)
    except Exception as e:
        snap = {"error": str(e)}

    # Initiative'ler
    initiatives = []
    try:
        from app.models.initiative import Initiative
        items = Initiative.query.filter_by(
            tenant_id=sub.id, is_active=True
        ).order_by(Initiative.priority.desc(), Initiative.id.desc()).limit(20).all()
        initiatives = [i.to_dict() for i in items]
    except Exception:
        pass

    # Risk listesi
    risks = []
    try:
        from app.models.k_radar_domain import RiskHeatmapItem
        items = RiskHeatmapItem.query.filter_by(
            tenant_id=sub.id, is_active=True
        ).order_by(
            (RiskHeatmapItem.probability * RiskHeatmapItem.impact).desc()
        ).limit(20).all()
        risks = [{
            "id": r.id,
            "title": getattr(r, "title", None) or getattr(r, "name", "—"),
            "probability": r.probability,
            "impact": r.impact,
            "score": (r.probability or 0) * (r.impact or 0),
            "status": getattr(r, "status", "—"),
            "owner": getattr(r, "owner_name", None) or getattr(r, "owner", None),
        } for r in items]
    except Exception:
        pass

    # Senaryo sayısı
    scenarios_count = 0
    try:
        from app.models.plan_year import PlanYear
        scenarios_count = PlanYear.query.filter(
            PlanYear.tenant_id == sub.id,
            PlanYear.scenario_of_id.isnot(None),
        ).count()
    except Exception:
        pass

    # Kullanıcı sayısı
    users_count = User.query.filter_by(tenant_id=sub.id, is_active=True).count()

    return {
        "sub_tenant": {
            "id": sub.id,
            "name": sub.name,
            "short_name": sub.short_name,
            "sector": sub.sector,
            "is_active": sub.is_active,
            "created_at": sub.created_at.isoformat() if sub.created_at else None,
            "users_count": users_count,
        },
        "snapshot": snap,
        "initiatives": initiatives,
        "risks": risks,
        "scenarios_count": scenarios_count,
        "generated_at": _dt.datetime.utcnow().isoformat(),
    }


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
