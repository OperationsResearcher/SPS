# -*- coding: utf-8 -*-
"""
Görev Aktivite Log Servisleri
Görev değişikliklerini loglama ve audit trail
"""
from flask import current_app
from models import db, TaskActivity, Task
import json


def log_task_activity(task_id, user_id, action, field_name=None, old_value=None, new_value=None, description=None):
    """
    Görev aktivitesini logla
    
    Args:
        task_id: Görev ID
        user_id: İşlemi yapan kullanıcı ID
        action: İşlem tipi (created, updated, deleted, status_changed, assigned, etc.)
        field_name: Değişen alan adı (opsiyonel)
        old_value: Eski değer (opsiyonel)
        new_value: Yeni değer (opsiyonel)
        description: İnsan okunabilir açıklama (opsiyonel)
    """
    try:
        activity = TaskActivity(
            task_id=task_id,
            user_id=user_id,
            action=action,
            field_name=field_name,
            old_value=json.dumps(old_value) if old_value is not None else None,
            new_value=json.dumps(new_value) if new_value is not None else None,
            description=description
        )
        db.session.add(activity)
        db.session.commit()
        return activity
    except Exception as e:
        db.session.rollback()
        if current_app:
            current_app.logger.error(f'Görev aktivite loglama hatası: {e}')
        return None


def log_task_created(task_id, user_id, task_title):
    """Görev oluşturuldu logla"""
    return log_task_activity(
        task_id=task_id,
        user_id=user_id,
        action='created',
        description=f'Görev oluşturuldu: "{task_title}"'
    )


def log_task_updated(task_id, user_id, changes):
    """
    Görev güncellendi logla
    
    Args:
        task_id: Görev ID
        user_id: İşlemi yapan kullanıcı ID
        changes: Dict - {field_name: {'old': old_value, 'new': new_value}}
    """
    activities = []
    for field_name, values in changes.items():
        activity = log_task_activity(
            task_id=task_id,
            user_id=user_id,
            action='updated',
            field_name=field_name,
            old_value=values.get('old'),
            new_value=values.get('new'),
            description=f'"{field_name}" alanı güncellendi'
        )
        if activity:
            activities.append(activity)
    return activities


def log_task_status_changed(task_id, user_id, old_status, new_status):
    """Görev durumu değişti logla"""
    return log_task_activity(
        task_id=task_id,
        user_id=user_id,
        action='status_changed',
        field_name='status',
        old_value=old_status,
        new_value=new_status,
        description=f'Görev durumu değiştirildi: "{old_status}" → "{new_status}"'
    )


def log_task_assigned(task_id, user_id, old_assigned_user_id, new_assigned_user_id):
    """Görev atandı logla"""
    from models import User
    
    old_user_name = None
    if old_assigned_user_id:
        old_user = User.query.get(old_assigned_user_id)
        old_user_name = f"{old_user.first_name} {old_user.last_name}" if old_user else None
    
    new_user_name = None
    if new_assigned_user_id:
        new_user = User.query.get(new_assigned_user_id)
        new_user_name = f"{new_user.first_name} {new_user.last_name}" if new_user else None
    
    description = f'Görev atandı: '
    if old_user_name:
        description += f'"{old_user_name}" → '
    if new_user_name:
        description += f'"{new_user_name}"'
    else:
        description += 'Atanmadı'
    
    return log_task_activity(
        task_id=task_id,
        user_id=user_id,
        action='assigned',
        field_name='assigned_to_id',
        old_value=old_assigned_user_id,
        new_value=new_assigned_user_id,
        description=description
    )


def log_task_deleted(task_id, user_id, task_title):
    """Görev silindi logla"""
    return log_task_activity(
        task_id=task_id,
        user_id=user_id,
        action='deleted',
        description=f'Görev silindi: "{task_title}"'
    )


























