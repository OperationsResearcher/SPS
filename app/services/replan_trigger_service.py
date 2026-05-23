"""Replan Trigger evaluation service (Sprint 57 — Ö8)."""
from __future__ import annotations

import json
import datetime as _dt
from typing import Optional

from extensions import db
from sqlalchemy import text

from app.models.replan_trigger import ReplanTrigger, ReplanTriggerEvent


_OP_MAP = {
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
    "==": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
}


def _eval_kpi_below_target(t: ReplanTrigger) -> Optional[dict]:
    """KPI consecutive_periods boyunca hedef altında mı?"""
    if not t.target_kpi_id:
        return None
    rows = db.session.execute(text("""
        SELECT data_date, actual_value, target_value
        FROM kpi_data
        WHERE process_kpi_id=:k AND is_active=true
          AND actual_value ~ '^-?[0-9]+\\.?[0-9]*$'
          AND target_value ~ '^-?[0-9]+\\.?[0-9]*$'
        ORDER BY data_date DESC
        LIMIT :n
    """), {"k": t.target_kpi_id, "n": t.consecutive_periods}).fetchall()

    if len(rows) < t.consecutive_periods:
        return None
    all_below = all(float(r.actual_value) < float(r.target_value) for r in rows)
    if not all_below:
        return None
    return {
        "kpi_id": t.target_kpi_id,
        "periods_checked": t.consecutive_periods,
        "last_actual": float(rows[0].actual_value),
        "last_target": float(rows[0].target_value),
    }


def _eval_threshold(t: ReplanTrigger, current_value: float) -> Optional[dict]:
    op = _OP_MAP.get(t.threshold_operator)
    if not op or t.threshold_value is None:
        return None
    if op(current_value, t.threshold_value):
        return {
            "current": current_value,
            "threshold": t.threshold_value,
            "operator": t.threshold_operator,
        }
    return None


def _eval_overdue_pct(t: ReplanTrigger) -> Optional[dict]:
    row = db.session.execute(text("""
        SELECT
            sum(CASE WHEN a.status!='Tamamlandı' AND a.end_date < CURRENT_DATE THEN 1 ELSE 0 END) as overdue,
            count(*) as total
        FROM process_activities a
        JOIN processes p ON a.process_id=p.id
        WHERE p.tenant_id=:t AND a.is_active=true
    """), {"t": t.tenant_id}).fetchone()
    if not row or not row.total:
        return None
    pct = (row.overdue / row.total) * 100
    return _eval_threshold(t, pct)


def evaluate_triggers(tenant_id: int, dry_run: bool = False) -> list[ReplanTriggerEvent]:
    """Tenant'a ait tüm aktif trigger'ları değerlendir; ateşlenenler için event yarat."""
    triggers = ReplanTrigger.query.filter_by(
        tenant_id=tenant_id, is_active=True
    ).all()
    fired_events = []

    for t in triggers:
        payload = None
        if t.trigger_type == "kpi_below_target":
            payload = _eval_kpi_below_target(t)
        elif t.trigger_type == "overdue_activity_pct":
            payload = _eval_overdue_pct(t)
        # diğer tipler için stub — gelecekte genişletilebilir

        if payload is None:
            continue

        event = ReplanTriggerEvent(
            trigger_id=t.id,
            tenant_id=tenant_id,
            payload=json.dumps(payload, default=str),
            action_taken=t.action,
        )
        if not dry_run:
            db.session.add(event)
            t.last_fired_at = _dt.datetime.utcnow()
            t.fire_count = (t.fire_count or 0) + 1
        fired_events.append(event)

    if not dry_run and fired_events:
        db.session.commit()
    return fired_events
