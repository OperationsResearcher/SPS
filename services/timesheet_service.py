# -*- coding: utf-8 -*-
"""
Zaman Takibi Servisleri
Timesheet ve time entry yönetimi
"""
from datetime import datetime, timedelta
from flask import current_app
from models import db, TimeEntry, Task


def start_time_entry(task_id, user_id, description=None):
    """
    Zaman takibini başlat
    
    Args:
        task_id: Görev ID
        user_id: Kullanıcı ID
        description: Açıklama (opsiyonel)
    
    Returns:
        TimeEntry: Oluşturulan time entry
    """
    try:
        # Kullanıcının başka bir aktif time entry'si var mı kontrol et
        active_entry = TimeEntry.query.filter_by(
            user_id=user_id,
            end_time=None
        ).first()
        
        if active_entry:
            # Önceki entry'yi durdur
            active_entry.end_time = datetime.utcnow()
            if active_entry.start_time:
                duration = (active_entry.end_time - active_entry.start_time).total_seconds() / 60
                active_entry.duration_minutes = int(duration)
        
        # Yeni time entry oluştur
        time_entry = TimeEntry(
            task_id=task_id,
            user_id=user_id,
            start_time=datetime.utcnow(),
            description=description
        )
        db.session.add(time_entry)
        db.session.commit()
        
        return time_entry
    except Exception as e:
        db.session.rollback()
        if current_app:
            current_app.logger.error(f'Zaman takibi başlatma hatası: {e}')
        return None


def stop_time_entry(time_entry_id=None, user_id=None):
    """
    Zaman takibini durdur
    
    Args:
        time_entry_id: Time entry ID (opsiyonel)
        user_id: Kullanıcı ID (opsiyonel - aktif entry bulmak için)
    
    Returns:
        TimeEntry: Durdurulan time entry
    """
    try:
        if time_entry_id:
            time_entry = TimeEntry.query.get(time_entry_id)
        elif user_id:
            time_entry = TimeEntry.query.filter_by(
                user_id=user_id,
                end_time=None
            ).first()
        else:
            return None
        
        if not time_entry or time_entry.end_time:
            return None
        
        time_entry.end_time = datetime.utcnow()
        if time_entry.start_time:
            duration = (time_entry.end_time - time_entry.start_time).total_seconds() / 60
            time_entry.duration_minutes = int(duration)
        
        # Task'ın actual_time'ını güncelle
        task = Task.query.get(time_entry.task_id)
        if task:
            if task.actual_time:
                task.actual_time += duration / 60  # Saate çevir
            else:
                task.actual_time = duration / 60
        
        db.session.commit()
        return time_entry
    except Exception as e:
        db.session.rollback()
        if current_app:
            current_app.logger.error(f'Zaman takibi durdurma hatası: {e}')
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
            TimeEntry.start_time >= datetime.combine(start_date, datetime.min.time()),
            TimeEntry.start_time <= datetime.combine(end_date, datetime.max.time())
        ).order_by(TimeEntry.start_time.desc()).all()
        
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
        from models import Task
        task_ids = [t.id for t in Task.query.filter_by(project_id=project_id).all()]
        
        if not task_ids:
            return []
        
        entries = TimeEntry.query.filter(
            TimeEntry.task_id.in_(task_ids),
            TimeEntry.start_time >= datetime.combine(start_date, datetime.min.time()),
            TimeEntry.start_time <= datetime.combine(end_date, datetime.max.time())
        ).order_by(TimeEntry.start_time.desc()).all()
        
        return entries
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Proje timesheet hatası: {e}')
        return []


























