"""Bayi/Holding alt-tenant konsolide kullanım & faturalama raporu (K).

Parent tenant'ın tüm alt-tenantlarının paket + kullanım özetini üretir.
Bayi/Holding bu rapor üzerinden müşterilerine fatura kesebilir veya
Kokpitim'e karşı kullanım durumunu görebilir.
"""
from __future__ import annotations

import datetime as _dt

from sqlalchemy import func, text

from extensions import db
from app.models.core import Tenant, User


def build_consolidated_usage(parent_tenant_id: int) -> dict:
    """Parent'ın tüm alt-tenant'ları için kullanım özeti."""
    parent = Tenant.query.get(parent_tenant_id)
    if not parent:
        return {"error": "Parent tenant bulunamadı."}
    if parent.tenant_type not in ("dealer", "holding"):
        return {"error": "Bu tenant alt-tenant'lara sahip değil."}

    subs = Tenant.query.filter_by(parent_tenant_id=parent.id).order_by(Tenant.name).all()
    sub_ids = [s.id for s in subs]

    # ─── LLM kullanım (varsa) ─────────────────────────────────────────────
    llm_by_tenant = {}
    if sub_ids:
        try:
            month_start = _dt.datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            rows = db.session.execute(text("""
                SELECT tenant_id,
                       count(*) FILTER (WHERE status='ok') as calls,
                       COALESCE(sum(total_tokens) FILTER (WHERE status='ok'), 0) as tokens,
                       COALESCE(sum(cost_usd) FILTER (WHERE status='ok'), 0) as cost
                FROM llm_usage_logs
                WHERE tenant_id = ANY(:ids) AND created_at >= :start
                GROUP BY tenant_id
            """), {"ids": sub_ids, "start": month_start}).fetchall()
            for r in rows:
                llm_by_tenant[r.tenant_id] = {
                    "calls": int(r.calls or 0),
                    "tokens": int(r.tokens or 0),
                    "cost_usd": float(r.cost or 0),
                }
        except Exception:
            pass

    # ─── KPI sayıları ──────────────────────────────────────────────────────
    kpi_by_tenant = {}
    if sub_ids:
        try:
            rows = db.session.execute(text("""
                SELECT p.tenant_id,
                       count(DISTINCT k.id) FILTER (WHERE k.is_active) as kpi_count
                FROM process_kpis k
                JOIN processes p ON k.process_id = p.id
                WHERE p.tenant_id = ANY(:ids)
                GROUP BY p.tenant_id
            """), {"ids": sub_ids}).fetchall()
            for r in rows:
                kpi_by_tenant[r.tenant_id] = int(r.kpi_count or 0)
        except Exception:
            pass

    # ─── Kullanıcı sayıları (tek query) ────────────────────────────────────
    user_by_tenant = {}
    if sub_ids:
        rows = db.session.query(
            User.tenant_id, func.count(User.id)
        ).filter(
            User.tenant_id.in_(sub_ids), User.is_active == True
        ).group_by(User.tenant_id).all()
        for tid, count in rows:
            user_by_tenant[tid] = int(count)

    # ─── Initiative sayıları ───────────────────────────────────────────────
    init_by_tenant = {}
    if sub_ids:
        try:
            from app.models.initiative import Initiative
            rows = db.session.query(
                Initiative.tenant_id, func.count(Initiative.id)
            ).filter(
                Initiative.tenant_id.in_(sub_ids), Initiative.is_active == True
            ).group_by(Initiative.tenant_id).all()
            for tid, count in rows:
                init_by_tenant[tid] = int(count)
        except Exception:
            pass

    # ─── Plan year sayıları ────────────────────────────────────────────────
    py_by_tenant = {}
    if sub_ids:
        try:
            from app.models.plan_year import PlanYear
            rows = db.session.query(
                PlanYear.tenant_id, func.count(PlanYear.id)
            ).filter(PlanYear.tenant_id.in_(sub_ids)).group_by(PlanYear.tenant_id).all()
            for tid, count in rows:
                py_by_tenant[tid] = int(count)
        except Exception:
            pass

    # ─── Satır satır birleştir ─────────────────────────────────────────────
    rows_out = []
    for s in subs:
        users = user_by_tenant.get(s.id, 0)
        max_u = s.max_user_count or 0
        util_pct = round((users / max_u) * 100, 1) if max_u else None
        llm = llm_by_tenant.get(s.id, {"calls": 0, "tokens": 0, "cost_usd": 0.0})
        rows_out.append({
            "id": s.id,
            "name": s.name,
            "short_name": s.short_name,
            "is_active": s.is_active,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "license_end_date": s.license_end_date.isoformat() if s.license_end_date else None,
            "package": {"id": s.package.id, "name": s.package.name} if s.package else None,
            "users_count": users,
            "max_user_count": max_u or None,
            "user_utilization_pct": util_pct,
            "kpi_count": kpi_by_tenant.get(s.id, 0),
            "initiative_count": init_by_tenant.get(s.id, 0),
            "plan_year_count": py_by_tenant.get(s.id, 0),
            "llm_calls_this_month": llm["calls"],
            "llm_tokens_this_month": llm["tokens"],
            "llm_cost_usd_this_month": round(llm["cost_usd"], 6),
        })

    # ─── Toplamlar ─────────────────────────────────────────────────────────
    totals = {
        "tenant_count": len(rows_out),
        "active_count": sum(1 for r in rows_out if r["is_active"]),
        "users_total": sum(r["users_count"] for r in rows_out),
        "max_users_total": sum(r["max_user_count"] or 0 for r in rows_out),
        "kpi_total": sum(r["kpi_count"] for r in rows_out),
        "initiative_total": sum(r["initiative_count"] for r in rows_out),
        "llm_calls_month_total": sum(r["llm_calls_this_month"] for r in rows_out),
        "llm_tokens_month_total": sum(r["llm_tokens_this_month"] for r in rows_out),
        "llm_cost_usd_month_total": round(sum(r["llm_cost_usd_this_month"] for r in rows_out), 6),
    }

    # Paket dağılımı (kaç tenant hangi pakette)
    package_dist = {}
    for r in rows_out:
        key = r["package"]["name"] if r["package"] else "(paket yok)"
        package_dist[key] = package_dist.get(key, 0) + 1

    return {
        "parent": {
            "id": parent.id, "name": parent.name,
            "tenant_type": parent.tenant_type,
        },
        "period": {
            "month_start": _dt.datetime.utcnow().replace(day=1).strftime("%Y-%m-01"),
            "now": _dt.datetime.utcnow().isoformat(),
        },
        "sub_tenants": rows_out,
        "totals": totals,
        "package_distribution": package_dist,
    }
