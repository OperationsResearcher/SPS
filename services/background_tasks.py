# -*- coding: utf-8 -*-
"""
Background Task Servisleri
PG hesaplamaları ve ağır işlemler için asenkron yapı hazırlığı
"""
from flask import current_app
from models import db
import threading
from queue import Queue
import time
from datetime import datetime


# Basit task queue (production'da Celery/RQ kullanılabilir)
task_queue = Queue()


class BackgroundTaskExecutor:
    """
    Basit background task executor
    Production'da Celery veya RQ ile değiştirilebilir
    """
    
    def __init__(self):
        self.worker_thread = None
        self.is_running = False
    
    def start(self):
        """Worker thread'i başlat"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker, daemon=True)
            self.worker_thread.start()
            if current_app:
                current_app.logger.info("Background task executor başlatıldı")
    
    def _worker(self):
        """Worker thread - task'ları işler"""
        while self.is_running:
            try:
                # Queue'dan task al (timeout ile)
                try:
                    task_func, args, kwargs = task_queue.get(timeout=1)
                except:
                    continue
                
                # Task'ı çalıştır
                try:
                    task_func(*args, **kwargs)
                except Exception as e:
                    if current_app:
                        current_app.logger.error(f"Background task hatası: {e}")
                finally:
                    task_queue.task_done()
            
            except Exception as e:
                if current_app:
                    current_app.logger.error(f"Background worker hatası: {e}")
                time.sleep(1)
    
    def stop(self):
        """Worker thread'i durdur"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        if current_app:
            current_app.logger.info("Background task executor durduruldu")


# Global executor instance
executor = BackgroundTaskExecutor()


_notification_scheduler_thread = None
_notification_scheduler_stop = threading.Event()


def _notification_scheduler_loop(app, interval_seconds: int):
    """Runs notification checks periodically inside Flask app context."""
    # Small delay to let app boot
    time.sleep(2)
    while not _notification_scheduler_stop.is_set():
        try:
            with app.app_context():
                from services.notification_service import (
                    check_and_send_deadline_reminders,
                    check_and_send_overdue_notifications,
                )
                check_and_send_deadline_reminders()
                check_and_send_overdue_notifications()
        except Exception as e:
            try:
                if current_app:
                    current_app.logger.error(f"Notification scheduler hatası: {e}")
            except Exception:
                pass

        # Sleep with stop support
        _notification_scheduler_stop.wait(interval_seconds)


def init_notification_scheduler(app):
    """Start periodic notification checks (development/simple deployments)."""
    global _notification_scheduler_thread

    # Don't run during tests
    if getattr(app, 'testing', False):
        return

    # Prevent double start
    if _notification_scheduler_thread and _notification_scheduler_thread.is_alive():
        return

    # Interval config (minutes)
    try:
        interval_minutes = int(app.config.get('NOTIFICATION_CHECK_INTERVAL_MINUTES', 60))
    except Exception:
        interval_minutes = 60
    interval_seconds = max(60, interval_minutes * 60)

    _notification_scheduler_stop.clear()
    _notification_scheduler_thread = threading.Thread(
        target=_notification_scheduler_loop,
        args=(app, interval_seconds),
        daemon=True,
        name='notification-scheduler'
    )
    _notification_scheduler_thread.start()
    try:
        app.logger.info(f"Notification scheduler başlatıldı (interval={interval_minutes} dk)")
    except Exception:
        pass


def execute_async(task_func, *args, **kwargs):
    """
    Bir fonksiyonu asenkron olarak çalıştırır
    
    Args:
        task_func: Çalıştırılacak fonksiyon
        *args, **kwargs: Fonksiyon argümanları
    
    Usage:
        execute_async(calculate_pg_data, pg_id, yil)
    """
    task_queue.put((task_func, args, kwargs))
    
    # Executor başlatılmamışsa başlat
    if not executor.is_running:
        executor.start()


def calculate_pg_data_async(bireysel_pg_id, yil, task_id=None):
    """
    PG verisi hesaplamasını asenkron olarak yapar
    (Örnek kullanım - gerçek implementasyon gerekebilir)
    """
    try:
        # Flask app context'i gerekiyorsa
        from flask import current_app
        
        with current_app.app_context():
            from models import BireyselPerformansGostergesi, PerformansGostergeVeri
            
            bireysel_pg = BireyselPerformansGostergesi.query.get(bireysel_pg_id)
            if not bireysel_pg:
                return
            
            # Ağır hesaplamalar burada yapılabilir
            # Örnek: Toplu veri işleme, karmaşık hesaplamalar vb.
            
            if current_app:
                current_app.logger.info(
                    f"Background task: PG {bireysel_pg_id} için {yil} yılı verileri hesaplandı"
                )
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Async PG hesaplama hatası: {e}")


# Flask app başladığında executor'ı başlat
def init_background_executor(app):
    """Flask app başlatıldığında çağrılır"""
    executor.start()

    # Periodic notification checks (simple scheduler)
    init_notification_scheduler(app)
    
    # App kapanırken executor'ı durdur
    @app.teardown_appcontext
    def shutdown_executor(error):
        if error:
            executor.stop()



























