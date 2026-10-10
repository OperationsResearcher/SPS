# -*- coding: utf-8 -*-
"""
Zaman Takibi Servisleri
Timesheet ve time entry yönetimi
"""
from datetime import datetime, timedelta
from flask import current_app
from app.models.legacy_bridge import db, TimeEntry, Task


def start_time_entry(task_id, user_id, description=None):
    """
    Canlı zaman sayacı başlatma: TimeEntry modelinde start/end alanı yok
    (yalnız duration_minutes + date), bu yüzden çalışan sayaç tutulamaz.
    Güvenle atlanır ve loglanır.
    """
    if current_app:
        current_app.logger.warning(
            'start_time_entry atlandi: TimeEntry modelinde start_time/end_time yok (task=%s user=%s)',
            task_id, user_id)
    return None


def stop_time_entry(time_entry_id=None, user_id=None):
    """Sayaç durdurma: bkz. start_time_entry (model desteklemiyor, atlanır)."""
    if current_app:
        current_app.logger.warning(
            'stop_time_entry atlandi: TimeEntry modelinde start_time/end_time yok')
    return None


def add_manual_time_entry(task_id, user_id, duration_minutes, entry_date=None, description=None):
    """Elle süre kaydı ekle (modelin gerçek alanlarıyla)."""
    try:
        entry = TimeEntry(
            task_id=task_id,
            user_id=user_id,
            duration_minutes=int(duration_minutes),
            description=description,
            date=entry_date or datetime.utcnow().date(),
        )
        db.session.add(entry)
        db.session.commit()
        return entry
    except Exception as e:
        db.session.rollback()
        if current_app:
            current_app.logger.error(f'Manuel zaman kaydi hatasi: {e}')
        return None


def get_task_total_time(task_id):
    """
    Görevin toplam harcanan süresini hesapla (saat)
    
    Args:
        task_id: Görev ID
    
    Returns:
        float: Toplam süre (saat)
    """
    try:
        entries = TimeEntry.query.filter_by(task_id=task_id).all()
        total_minutes = sum(entry.duration_minutes or 0 for entry in entries if entry.duration_minutes)
        return total_minutes / 60.0  # Saate çevir
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Süre hesaplama hatası: {e}')
        return 0.0


def get_user_timesheet(user_id, start_date, end_date):
    """
    Kullanıcının timesheet'ini getir
    
    Args:
        user_id: Kullanıcı ID
        start_date: Başlangıç tarihi
        end_date: Bitiş tarihi
    
    Returns:
        list: Time entry listesi
    """
    try:
        entries = TimeEntry.query.filter(
            TimeEntry.user_id == user_id,
            TimeEntry.date >= start_date,
            TimeEntry.date <= end_date
        ).order_by(TimeEntry.date.desc()).all()
        
        return entries
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Timesheet getirme hatası: {e}')
        return []


def get_project_timesheet(project_id, start_date, end_date):
    """
    Projenin timesheet'ini getir (tüm görevler)
    
    Args:
        project_id: Proje ID
        start_date: Başlangıç tarihi
        end_date: Bitiş tarihi
    
    Returns:
        list: Time entry listesi
    """
    try:
        from app.models.legacy_bridge import Task
        task_ids = [t.id for t in Task.query.filter_by(project_id=project_id).all()]
        
        if not task_ids:
            return []
        
        entries = TimeEntry.query.filter(
            TimeEntry.task_id.in_(task_ids),
            TimeEntry.date >= start_date,
            TimeEntry.date <= end_date
        ).order_by(TimeEntry.date.desc()).all()
        
        return entries
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Proje timesheet hatası: {e}')
        return []



























