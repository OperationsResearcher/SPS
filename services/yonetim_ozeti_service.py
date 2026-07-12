# -*- coding: utf-8 -*-
"""Yönetim Özeti (Faz 4) — üst yönetim için '5 saniyede durum' verisi.

Sıfırdan hesaplama YOK: mevcut servisleri birleştirir.
  - get_hub_summary        → kurum skoru + band + bileşen skorları
  - build_kurum_overview   → geciken görev/faaliyet/proje, düşük sağlık
  - build_exec_snapshot    → KPI hedef-üstü %, risk, anomali
  - strateji skorları (SQL)→ en düşük 5 strateji (bottom-5)

docs/paketler/ROL-GORUNUM-KATMANI.md — Faz 4.
"""
from __future__ import annotations

import datetime as _dt
from typing import Any


def build_yonetim_ozeti(user, tenant_id: int) -> dict[str, Any]:
    """Üst yönetim özet dashboard'u için birleşik veri.

    Privileged kullanıcı varsayılır (kurum geneli). scope=None → tüm kurum.
    Her blok kendi hatasına dayanıklı: bir servis patlarsa o blok boş döner,
    dashboard yine render olur.
    """
    out: dict[str, Any] = {
        "kurum_skoru": _kurum_skoru(tenant_id),
        "geciken": _geciken(user, tenant_id),
        "kpi_ozet": _kpi_ozet(tenant_id),
        "en_dusuk_5": _en_dusuk_5(tenant_id),
    }
    return out


def _kurum_skoru(tenant_id: int) -> dict[str, Any]:
    try:
        from services.k_radar_service import get_hub_summary
        hub = get_hub_summary(tenant_id, None, None)  # kurum geneli
        return {
            "total_score": round(float(hub.get("total_score") or 0.0), 1),
            "total_band": hub.get("total_band", "red"),
            "ks": _band_only(hub.get("ks")),
            "kp": _band_only(hub.get("kp")),
            "kpr": _band_only(hub.get("kpr")),
            "individual": _band_only(hub.get("individual")),
        }
    except Exception:
        return {}


def _band_only(comp) -> dict[str, Any]:
    if not isinstance(comp, dict):
        return {}
    return {
        "score": round(float(comp.get("score") or 0.0), 1),
        "band": comp.get("band", "red"),
        "critical_count": int(comp.get("critical_count") or 0),
    }


def _geciken(user, tenant_id: int) -> dict[str, Any]:
    try:
        from micro.modules.kurum.kurum_overview import build_kurum_overview
        ov = build_kurum_overview(user, tenant_id, tenant_id)
        proj = ov.get("project") or {}
        proc = ov.get("process") or {}
        return {
            "overdue_tasks": int(proj.get("overdue_tasks") or 0),
            "projects_overdue_end": int(proj.get("projects_overdue_end") or 0),
            "low_health_projects": int(proj.get("low_health_projects") or 0),
            "open_raid_items": int(proj.get("open_raid_items") or 0),
            "overdue_activities": int(proc.get("overdue_activities") or 0),
            "tasks_due_next_7_days": int(proj.get("tasks_due_next_7_days") or 0),
        }
    except Exception:
        return {}


def _kpi_ozet(tenant_id: int) -> dict[str, Any]:
    try:
        from app.services.exec_dashboard_service import build_exec_snapshot
        snap = build_exec_snapshot(tenant_id)
        kpi = snap.get("kpi") or {}
        risk = snap.get("risk") or {}
        act = snap.get("activity") or {}
        return {
            "kpi_total": int(kpi.get("total") or 0),
            "kpi_with_data": int(kpi.get("with_data") or 0),
            "on_target_pct": kpi.get("on_target_pct"),
            "risk_count": int(risk.get("total") or 0) if isinstance(risk, dict) else 0,
            "activity_overdue": int(act.get("overdue") or 0) if isinstance(act, dict) else 0,
        }
    except Exception:
        return {}


def _en_dusuk_5(tenant_id: int) -> list[dict[str, Any]]:
    """En düşük performanslı 5 strateji (hedef-üstü % en düşük).
    routes_exec_advisor.py::sp_api_exec_strategy_scores ile aynı SQL mantığı."""
    try:
        from sqlalchemy import text as _t
        from app.extensions import db
        year = _dt.date.today().year
        rows = db.session.execute(_t("""
            SELECT s.code, s.title,
                   sum(CASE
                        WHEN kd.actual_value ~ '^-?[0-9]+\\.?[0-9]*$'
                         AND kd.target_value ~ '^-?[0-9]+\\.?[0-9]*$'
                         AND kd.actual_value::float >= kd.target_value::float
                       THEN 1 ELSE 0 END) AS on_target,
                   sum(CASE
                        WHEN kd.actual_value ~ '^-?[0-9]+\\.?[0-9]*$'
                         AND kd.target_value ~ '^-?[0-9]+\\.?[0-9]*$'
                       THEN 1 ELSE 0 END) AS comparable
            FROM strategies s
            JOIN sub_strategies ss ON ss.strategy_id = s.id AND ss.is_active=true
            JOIN process_sub_strategy_links psl ON psl.sub_strategy_id = ss.id
            JOIN processes p ON p.id = psl.process_id AND p.is_active=true
            JOIN process_kpis k ON k.process_id = p.id AND k.is_active=true
            LEFT JOIN kpi_data kd ON kd.process_kpi_id = k.id AND kd.year=:y AND kd.is_active=true
            WHERE s.tenant_id=:t AND s.is_active=true
            GROUP BY s.id, s.code, s.title
        """), {"t": tenant_id, "y": year}).fetchall()
        items = []
        for r in rows:
            comp = int(r.comparable or 0)
            if not comp:
                continue
            pct = round((int(r.on_target or 0) / comp) * 100, 1)
            items.append({"code": r.code or "", "title": r.title or "", "on_target_pct": pct})
        return sorted(items, key=lambda x: x["on_target_pct"])[:5]
    except Exception:
        return []
