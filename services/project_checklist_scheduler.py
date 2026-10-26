# -*- coding: utf-8 -*-
"""Proje kontrol listesi periyodik hatırlatma zamanlayıcısı (saatlik)."""

import logging

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

from app.models import db

logger = logging.getLogger(__name__)
scheduler = None


def check_checklist_reminders(app):
    """Zamanı gelen periyodik kontrol listesi hatırlatmalarını gönderir."""
    with app.app_context():
        try:
            from app.services.project_checklist_service import run_due_reminders
            n = run_due_reminders()
            db.session.commit()
            if n:
                logger.info("[checklist] %s periyodik hatırlatma gönderildi", n)
        except Exception as exc:
            db.session.rollback()
            logger.error("Kontrol listesi hatırlatma hatası: %s", exc)


def init_checklist_scheduler(app):
    global scheduler
    if scheduler is not None:
        return scheduler
    scheduler = BackgroundScheduler(daemon=True, timezone="Europe/Istanbul")
    scheduler.add_job(
        func=check_checklist_reminders,
        args=[app],
        trigger=IntervalTrigger(hours=1),
        id="project_checklist_reminders",
        replace_existing=True,
        misfire_grace_time=1800,
        coalesce=True,
    )
    scheduler.start()
    return scheduler
