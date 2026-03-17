"""
Celery Tasks
Sprint 16-18: AI ve Otomasyon
Background tasks for automated reporting and monitoring
"""

from celery import Celery
from celery.schedules import crontab
from app.services.automated_reporting_service import AutomatedReportingService
from app.services.anomaly_service import AnomalyService
from app.models.core import User
from app.models.process import ProcessKpi
import os

# Celery configuration
celery = Celery(
    'kokpitim',
    broker=os.getenv('CELERY_BROKER_URL', 'redis://localhost:6379/1'),
    backend=os.getenv('CELERY_RESULT_BACKEND', 'redis://localhost:6379/2')
)

celery.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='Europe/Istanbul',
    enable_utc=True,
)

# Services
reporting_service = AutomatedReportingService()
anomaly_service = AnomalyService()


@celery.task(name='tasks.send_daily_digest')
def send_daily_digest():
    """Günlük özet raporlarını gönder"""
    # Tüm tenant'lar için
    tenants = User.query.with_entities(User.tenant_id).distinct().all()
    
    for (tenant_id,) in tenants:
        try:
            reporting_service.schedule_and_send_reports(tenant_id, 'daily')
        except Exception as e:
            print(f"Daily digest failed for tenant {tenant_id}: {str(e)}")


@celery.task(name='tasks.send_weekly_summary')
def send_weekly_summary():
    """Haftalık özet raporlarını gönder"""
    tenants = User.query.with_entities(User.tenant_id).distinct().all()
    
    for (tenant_id,) in tenants:
        try:
            reporting_service.schedule_and_send_reports(tenant_id, 'weekly')
        except Exception as e:
            print(f"Weekly summary failed for tenant {tenant_id}: {str(e)}")


@celery.task(name='tasks.send_monthly_report')
def send_monthly_report():
    """Aylık raporları gönder"""
    tenants = User.query.with_entities(User.tenant_id).distinct().all()
    
    for (tenant_id,) in tenants:
        try:
            reporting_service.schedule_and_send_reports(tenant_id, 'monthly')
        except Exception as e:
            print(f"Monthly report failed for tenant {tenant_id}: {str(e)}")


@celery.task(name='tasks.monitor_anomalies')
def monitor_anomalies():
    """Tüm KPI'ları anomali için izle"""
    kpis = ProcessKpi.query.filter_by(is_active=True).all()
    
    for kpi in kpis:
        try:
            # KPI sahibini bul
            if kpi.process and kpi.process.leaders:
                for leader in kpi.process.leaders:
                    anomaly_service.monitor_and_alert(kpi.id, leader.id)
        except Exception as e:
            print(f"Anomaly monitoring failed for KPI {kpi.id}: {str(e)}")


# Celery Beat Schedule
celery.conf.beat_schedule = {
    'daily-digest': {
        'task': 'tasks.send_daily_digest',
        'schedule': crontab(hour=9, minute=0),  # Her gün 09:00
    },
    'weekly-summary': {
        'task': 'tasks.send_weekly_summary',
        'schedule': crontab(day_of_week=1, hour=9, minute=0),  # Pazartesi 09:00
    },
    'monthly-report': {
        'task': 'tasks.send_monthly_report',
        'schedule': crontab(day_of_month=1, hour=9, minute=0),  # Ayın 1'i 09:00
    },
    'monitor-anomalies': {
        'task': 'tasks.monitor_anomalies',
        'schedule': crontab(hour='*/6'),  # Her 6 saatte bir
    },
}
