"""K-Radar gunluk ozet ve bildirim tetikleyicisi."""

from __future__ import annotations

import datetime
import json
import logging
import os
from functools import partial

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.models import db
from app.models.core import Notification, Tenant, User
from services.k_radar_service import get_hub_summary, get_recommendations_from_summary

logger = logging.getLogger(__name__)
_scheduler = None
_job_id = "k_radar_daily_digest"
_MANAGER_ROLES = {"Admin", "tenant_admin", "executive_manager"}
_default_cfg = {
    "enabled": True,
    "time": "08:30",
}


def _cfg_path(app) -> str:
    os.makedirs(app.instance_path, exist_ok=True)
    return os.path.join(app.instance_path, "k_radar_schedule.json")


def _normalize(cfg: dict | None) -> dict:
    out = dict(_default_cfg)
    if isinstance(cfg, dict):
        out.update(cfg)
    out["enabled"] = bool(out.get("enabled", True))
    time_raw = str(out.get("time", "08:30")).strip()
    try:
        hh, mm = time_raw.split(":", 1)
        hh_i = max(0, min(23, int(hh)))
        mm_i = max(0, min(59, int(mm)))
    except Exception:
        hh_i, mm_i = 8, 30
    out["time"] = f"{hh_i:02d}:{mm_i:02d}"
    return out


def load_schedule(app) -> dict:
    p = _cfg_path(app)
    if not os.path.isfile(p):
        return dict(_default_cfg)
    try:
        with open(p, "r", encoding="utf-8") as f:
            return _normalize(json.load(f))
    except Exception:
        return dict(_default_cfg)


def save_schedule(app, cfg: dict) -> dict:
    norm = _normalize(cfg)
    with open(_cfg_path(app), "w", encoding="utf-8") as f:
        json.dump(norm, f, ensure_ascii=False, indent=2)
    return norm


def _manager_users_for_tenant(tenant_id: int) -> list[User]:
    users = User.query.filter_by(tenant_id=tenant_id, is_active=True).all()
    out: list[User] = []
    for u in users:
        role_name = u.role.name if u.role else ""
        if role_name in _MANAGER_ROLES:
            out.append(u)
    return out


def _already_sent_today(user_id: int, tenant_id: int) -> bool:
    today_start = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
    row = (
        Notification.query.filter_by(
            user_id=user_id,
            tenant_id=tenant_id,
            notification_type="k_radar_daily_digest",
        )
        .filter(Notification.created_at >= today_start)
        .first()
    )
    return row is not None


def _create_digest_notification(user_id: int, tenant_id: int, summary: dict) -> None:
    if _already_sent_today(user_id, tenant_id):
        return
    recs = get_recommendations_from_summary(summary)
    msg = f"Toplam skor: {summary.get('total_score', 0)} ({summary.get('total_band', '-').upper()}). "
    msg += " | ".join(recs[:2])
    n = Notification(
        user_id=user_id,
        tenant_id=tenant_id,
        notification_type="k_radar_daily_digest",
        title="K-Radar Gunluk Ozet",
        message=msg,
        link="/k-radar",
        is_read=False,
    )
    db.session.add(n)


def _run_job(app) -> None:
    with app.app_context():
        try:
            tenants = Tenant.query.filter_by(is_active=True).all()
            for tenant in tenants:
                summary = get_hub_summary(tenant.id)
                managers = _manager_users_for_tenant(tenant.id)
                for manager in managers:
                    _create_digest_notification(manager.id, tenant.id, summary)
            db.session.commit()
            logger.info("K-Radar daily digest tamamlandi.")
        except Exception as e:
            db.session.rollback()
            logger.exception("K-Radar daily digest hatasi: %s", e)


def apply_schedule(app) -> dict:
    global _scheduler
    cfg = load_schedule(app)
    if _scheduler is None:
        _scheduler = BackgroundScheduler(daemon=True)
        _scheduler.start()
    if _scheduler.get_job(_job_id):
        _scheduler.remove_job(_job_id)
    if not cfg.get("enabled"):
        return cfg
    hh, mm = cfg["time"].split(":")
    trigger = CronTrigger(hour=int(hh), minute=int(mm))
    _scheduler.add_job(
        func=partial(_run_job, app),
        trigger=trigger,
        id=_job_id,
        name="K-Radar gunluk ozet",
        replace_existing=True,
    )
    return cfg


def init_k_radar_scheduler(app) -> dict:
    return apply_schedule(app)
