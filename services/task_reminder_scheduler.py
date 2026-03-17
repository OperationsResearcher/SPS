"""
Görev Hatırlatma Scheduler Servisi

Bu servis, görevler için belirlenen reminder_date değerlerine göre
otomatik hatırlatma bildirimleri gönderir.
"""
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import current_app
from functools import partial
import logging

# Logger ayarla
logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler = None


def check_task_reminders(app=None):
    """
    Hatırlatma zamanı gelen görevleri kontrol eder ve bildirim gönderir.
    Her 5 dakikada bir çalışır.
    """
    from models.project import Task
    from services.notification_service import create_task_reminder_notification
    from utils.task_status import COMPLETED_STATUSES
    from extensions import db

    if app is None:
        try:
            app = current_app._get_current_object()
        except Exception as e:
            logger.error(f"Hatırlatma kontrolü hatası: {e}")
            return

    try:
        with app.app_context():
            now = datetime.utcnow()
            # 5 dakika öncesinden itibaren hatırlatmaları kontrol et
            check_window_start = now - timedelta(minutes=5)
            check_window_end = now + timedelta(minutes=1)

            # Hatırlatma zamanı gelen görevleri bul
            tasks_to_remind = Task.query.filter(
                Task.reminder_date.isnot(None),
                Task.reminder_date >= check_window_start,
                Task.reminder_date <= check_window_end,
                Task.status.notin_(COMPLETED_STATUSES),
                Task.is_archived == False
            ).all()

            if tasks_to_remind:
                logger.info(f"{len(tasks_to_remind)} görev için hatırlatma gönderiliyor...")

            for task in tasks_to_remind:
                try:
                    # Görev atanmışsa atanan kişiye bildirim gönder
                    if task.assigned_to_id:
                        create_task_reminder_notification(task.id, task.assigned_to_id)
                        logger.info(f"Görev #{task.id} ({task.title}) için hatırlatma gönderildi.")

                    # Hatırlatma gönderildikten sonra reminder_date'i temizle
                    # (aynı hatırlatmanın tekrar gönderilmemesi için)
                    task.reminder_date = None
                    db.session.commit()

                except Exception as e:
                    logger.error(f"Görev #{task.id} hatırlatma hatası: {e}")
                    db.session.rollback()

    except Exception as e:
        logger.error(f"Hatırlatma kontrolü hatası: {e}")


def init_scheduler(app):
    """
    Scheduler'ı başlatır ve görev hatırlatma job'ını ekler.
    
    Args:
        app: Flask application instance
    """
    global scheduler
    
    if scheduler is not None:
        logger.warning("Scheduler zaten başlatılmış.")
        return scheduler
    
    scheduler = BackgroundScheduler(daemon=True)
    
    # Her 5 dakikada bir hatırlatmaları kontrol et
    scheduler.add_job(
        func=partial(check_task_reminders, app),
        trigger=IntervalTrigger(minutes=5),
        id='task_reminder_check',
        name='Görev Hatırlatma Kontrolü',
        replace_existing=True
    )
    
    try:
        scheduler.start()
        logger.info("Görev hatırlatma scheduler başlatıldı (5 dakika interval).")
    except Exception as e:
        logger.error(f"Scheduler başlatma hatası: {e}")
    
    return scheduler


def shutdown_scheduler():
    """Scheduler'ı kapat"""
    global scheduler
    
    if scheduler is not None:
        scheduler.shutdown()
        scheduler = None
        logger.info("Scheduler kapatıldı.")
