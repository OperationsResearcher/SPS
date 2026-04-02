# -*- coding: utf-8 -*-
"""Süreç Faaliyeti Scheduler (hatırlatma + otomatik gerçekleşme)."""

from datetime import datetime, timedelta
from functools import partial
import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import current_app

from app.models import db
from app.models.core import User
from app.models.process import ProcessActivity, ProcessActivityReminder
from app.services.process_activity_service import auto_complete_due_activities
from app_platform.services.notification_triggers import (
    notify_activity_auto_completed,
    notify_activity_reminder,
)

logger = logging.getLogger(__name__)
scheduler = None


def check_activity_reminders(app=None):
    """Zamanı gelen faaliyet hatırlatmalarını gönderir."""
    if app is None:
        try:
            app = current_app._get_current_object()
        except Exception:
            return
    with app.app_context():
        # DB'de remind_at/end_at naive local datetime tutuluyor.
        # UTC karşılaştırması tetiklemeleri geciktirir.
        now = datetime.now()
        window_start = now - timedelta(minutes=5)
        due = (
            ProcessActivityReminder.query.join(ProcessActivity)
            .filter(
                ProcessActivityReminder.sent_at.is_(None),
                ProcessActivityReminder.remind_at >= window_start,
                ProcessActivityReminder.remind_at <= now,
                ProcessActivity.is_active.is_(True),
                ProcessActivity.status.in_(('Planlandı', 'Ertelendi')),
            )
            .all()
        )
        for r in due:
            try:
                activity = r.activity
                if not activity:
                    continue
                if not activity.assignees:
                    r.sent_at = now
                    continue
                for user in activity.assignees:
                    notify_activity_reminder(
                        activity=activity,
                        process=activity.process,
                        user=user,
                        minutes_before=int(r.minutes_before or 0),
                        send_email=bool(activity.notify_email and r.channel_email),
                    )
                r.sent_at = now
                db.session.commit()
            except Exception as exc:
                db.session.rollback()
                logger.error("Faaliyet reminder hatası: %s", exc)


def check_activity_auto_completion(app=None):
    """Bitişi gelen faaliyetleri otomatik gerçekleştirir."""
    if app is None:
        try:
            app = current_app._get_current_object()
        except Exception:
            return
    with app.app_context():
        # DB'de remind_at/end_at naive local datetime tutuluyor.
        # UTC karşılaştırması tetiklemeleri geciktirir.
        now = datetime.now()
        before = (
            ProcessActivity.query.filter(
                ProcessActivity.is_active.is_(True),
                ProcessActivity.auto_complete_enabled.is_(True),
                ProcessActivity.end_at.isnot(None),
                ProcessActivity.end_at <= now,
                ProcessActivity.status.in_(('Planlandı', 'Ertelendi')),
            )
            .all()
        )
        changed = auto_complete_due_activities(now=now)
        if not changed:
            return
        # Otomatik tamamlananlar için bildirim
        for act in before:
            try:
                users = act.assignees or []
                if not users and act.first_assignee_id:
                    u = User.query.get(act.first_assignee_id)
                    if u:
                        users = [u]
                for user in users:
                    notify_activity_auto_completed(
                        activity=act,
                        process=act.process,
                        user=user,
                        send_email=bool(act.notify_email),
                    )
                db.session.commit()
            except Exception as exc:
                db.session.rollback()
                logger.error("Faaliyet auto-complete bildirim hatası: %s", exc)


def init_process_activity_scheduler(app):
    global scheduler
    if scheduler is not None:
        return scheduler
    scheduler = BackgroundScheduler(daemon=True)
    scheduler.add_job(
        func=partial(check_activity_reminders, app),
        trigger=IntervalTrigger(minutes=5),
        id='process_activity_reminder_check',
        name='Süreç faaliyet hatırlatma kontrolü',
        replace_existing=True,
    )
    scheduler.add_job(
        func=partial(check_activity_auto_completion, app),
        trigger=IntervalTrigger(minutes=5),
        id='process_activity_auto_complete_check',
        name='Süreç faaliyet otomatik gerçekleşme kontrolü',
        replace_existing=True,
    )
    try:
        scheduler.start()
        logger.info("Süreç faaliyet scheduler başlatıldı")
    except Exception as exc:
        logger.error("Süreç faaliyet scheduler başlatılamadı: %s", exc)
    return scheduler


def shutdown_process_activity_scheduler():
    global scheduler
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
