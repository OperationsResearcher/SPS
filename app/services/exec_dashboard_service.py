"""Executive Dashboard — KPI × Strategy × Initiative × Risk × Trigger tek bakış.

Önerilen Hamle #5. Tek bir tenant için 360° strateji sağlık özeti.
"""
from __future__ import annotations

import datetime as _dt
import logging
from sqlalchemy import text

from extensions import db

logger = logging.getLogger(__name__)


def build_exec_snapshot(tenant_id: int, year: int | None = None) -> dict:
    today = _dt.date.today()
    if year is None:
        year = today.year

    # Verilen yıl için plan_year_id'yi çöz (varsa)
    _py_row = db.session.execute(text(
        "SELECT id FROM plan_years WHERE tenant_id=:t AND year=:y LIMIT 1"
    ), {"t": tenant_id, "y": year}).fetchone()
    plan_year_id = int(_py_row.id) if _py_row else None

    # PG (yıla bağlı; plan_year_id eşleşen + legacy NULL'lar dahil)
    kpi_row = db.session.execute(text("""
        SELECT
            count(DISTINCT k.id) FILTER (WHERE k.is_active) as total,
            count(DISTINCT k.id) FILTER (
                WHERE k.is_active AND EXISTS (
                    SELECT 1 FROM kpi_data kd
                    WHERE kd.process_kpi_id=k.id AND kd.year=:y AND kd.is_active=true
                )
            ) as with_data
        FROM process_kpis k
        JOIN processes p ON k.process_id=p.id
        WHERE p.tenant_id=:t
          AND (CAST(:py_id AS INTEGER) IS NULL OR k.plan_year_id = CAST(:py_id AS INTEGER) OR k.plan_year_id IS NULL)
    """), {"t": tenant_id, "y": year, "py_id": plan_year_id}).fetchone()

    on_target_row = db.session.execute(text("""
        SELECT
            sum(CASE WHEN kd.actual_value::float >= kd.target_value::float THEN 1 ELSE 0 END) as on_target,
            count(*) as total
        FROM kpi_data kd
        JOIN process_kpis k ON kd.process_kpi_id=k.id
        JOIN processes p ON k.process_id=p.id
        WHERE p.tenant_id=:t AND kd.year=:y AND kd.is_active=true
          AND kd.actual_value ~ '^-?[0-9]+\\.?[0-9]*$'
          AND kd.target_value ~ '^-?[0-9]+\\.?[0-9]*$'
          AND (CAST(:py_id AS INTEGER) IS NULL OR k.plan_year_id = CAST(:py_id AS INTEGER) OR k.plan_year_id IS NULL)
    """), {"t": tenant_id, "y": year, "py_id": plan_year_id}).fetchone()
    on_target_pct = (
        (on_target_row.on_target / on_target_row.total) * 100
        if on_target_row and on_target_row.total else 0
    )

    # Stratejiler + alt stratejiler (sadece seçili plan yılına ait)
    strat_row = db.session.execute(text("""
        SELECT
            (SELECT count(*) FROM strategies
                WHERE tenant_id=:t AND is_active=true
                  AND (CAST(:py_id AS INTEGER) IS NULL OR plan_year_id = CAST(:py_id AS INTEGER))) as strat,
            (SELECT count(*) FROM sub_strategies ss
                JOIN strategies s ON ss.strategy_id=s.id
                WHERE s.tenant_id=:t AND ss.is_active=true
                  AND (CAST(:py_id AS INTEGER) IS NULL OR s.plan_year_id = CAST(:py_id AS INTEGER))) as sub
    """), {"t": tenant_id, "py_id": plan_year_id}).fetchone()

    # Girişimler (yıl aralığını kapsayanlar)
    init_rows = db.session.execute(text("""
        SELECT status, count(*) as c, avg(progress_pct) as avg_p
        FROM initiatives
        WHERE tenant_id=:t AND is_active=true
          AND (:y BETWEEN COALESCE(start_year, :y) AND COALESCE(end_year, :y))
        GROUP BY status
    """), {"t": tenant_id, "y": year}).fetchall()
    init_status = {r.status: {"count": r.c, "avg_progress": float(r.avg_p or 0)} for r in init_rows}
    init_total = sum(v["count"] for v in init_status.values())

    # Süreç faaliyetleri (plan_year filtresiyle)
    act_row = db.session.execute(text("""
        SELECT
            sum(CASE WHEN a.status IN ('Planlandı','Devam Ediyor') THEN 1 ELSE 0 END) as active,
            sum(CASE WHEN a.status != 'Tamamlandı' AND a.end_date < CURRENT_DATE THEN 1 ELSE 0 END) as overdue,
            count(*) as total
        FROM process_activities a
        JOIN processes p ON a.process_id=p.id
        WHERE p.tenant_id=:t AND a.is_active=true
          AND (CAST(:py_id AS INTEGER) IS NULL OR a.plan_year_id = CAST(:py_id AS INTEGER) OR a.plan_year_id IS NULL)
    """), {"t": tenant_id, "py_id": plan_year_id}).fetchone()

    # Risk (plan_year filtresiyle)
    risk_data = {"open": 0, "critical": 0}
    try:
        risk_row = db.session.execute(text("""
            SELECT
                sum(CASE WHEN status != 'Closed' THEN 1 ELSE 0 END) as open_c,
                sum(CASE WHEN (probability*impact) >= 16 THEN 1 ELSE 0 END) as crit_c
            FROM risk_heatmap_items
            WHERE tenant_id=:t AND is_active=true
              AND (CAST(:py_id AS INTEGER) IS NULL OR plan_year_id = CAST(:py_id AS INTEGER) OR plan_year_id IS NULL)
        """), {"t": tenant_id, "py_id": plan_year_id}).fetchone()
        if risk_row:
            risk_data = {"open": int(risk_row.open_c or 0), "critical": int(risk_row.crit_c or 0)}
    except Exception as _e:
        logger.error("[exec_dashboard] risk verisi alınamadı (tenant=%s): %s", tenant_id, _e)

    # Trigger
    trig_row = db.session.execute(text("""
        SELECT
            count(*) FILTER (WHERE is_active) as active,
            count(*) FILTER (WHERE last_fired_at > CURRENT_DATE - INTERVAL '7 days') as fired_week
        FROM replan_triggers WHERE tenant_id=:t
    """), {"t": tenant_id}).fetchone()

    # Senaryo
    scen_row = db.session.execute(text("""
        SELECT count(*) as c FROM plan_years
        WHERE tenant_id=:t AND scenario_of_id IS NOT NULL
    """), {"t": tenant_id}).fetchone()

    # Anomali
    anomaly_data = {"high": 0, "medium": 0}
    try:
        from app.services.kpi_anomaly_service import detect_anomalies_for_tenant
        anomalies = detect_anomalies_for_tenant(tenant_id, threshold=2.0, limit=100)
        anomaly_data["high"] = sum(1 for a in anomalies if a.severity == "high")
        anomaly_data["medium"] = sum(1 for a in anomalies if a.severity == "medium")
    except Exception as _e:
        logger.error("[exec_dashboard] anomali tespiti başarısız (tenant=%s): %s", tenant_id, _e)

    # Sağlık skoru (basit ağırlıklı)
    health = 0.0
    weights = 0
    if kpi_row and kpi_row.total:
        health += on_target_pct * 0.4
        weights += 40
        coverage = (kpi_row.with_data / max(kpi_row.total, 1)) * 100
        health += coverage * 0.2
        weights += 20
    if act_row and act_row.total:
        overdue_pct = (act_row.overdue / act_row.total) * 100
        health += max(0, 100 - overdue_pct) * 0.2
        weights += 20
    if risk_data["critical"] == 0:
        health += 10
    weights += 10
    if anomaly_data["high"] == 0:
        health += 10
    weights += 10
    health_score = round(health / max(weights / 100, 1), 1) if weights else None

    return {
        "tenant_id": tenant_id,
        "year": year,
        "generated_at": _dt.datetime.now(_dt.timezone.utc).isoformat(),
        "health_score": health_score,
        "kpi": {
            "total": int(kpi_row.total or 0) if kpi_row else 0,
            "with_data": int(kpi_row.with_data or 0) if kpi_row else 0,
            "on_target_pct": round(on_target_pct, 1),
        },
        "strategy": {
            "count": int(strat_row.strat or 0) if strat_row else 0,
            "sub_count": int(strat_row.sub or 0) if strat_row else 0,
        },
        "initiative": {
            "total": init_total,
            "by_status": init_status,
        },
        "activity": {
            "active": int(act_row.active or 0) if act_row else 0,
            "overdue": int(act_row.overdue or 0) if act_row else 0,
            "total": int(act_row.total or 0) if act_row else 0,
        },
        "risk": risk_data,
        "anomaly": anomaly_data,
        "trigger": {
            "active": int(trig_row.active or 0) if trig_row else 0,
            "fired_last_7d": int(trig_row.fired_week or 0) if trig_row else 0,
        },
        "scenario_count": int(scen_row.c or 0) if scen_row else 0,
    }
