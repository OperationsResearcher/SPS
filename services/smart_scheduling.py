# -*- coding: utf-8 -*-
"""
Akıllı Planlama Servisleri
Geciken öncül görevler için ardıl görev tarihlerini otomatik güncelleme
"""
from datetime import date, timedelta
from flask import current_app
from models import db, Task, task_predecessors


def update_dependent_tasks_due_dates(task_id, new_due_date, project_id, user_id):
    """
    Bir görevin due_date'i geciktiğinde, ona bağlı ardıl görevlerin tarihlerini günceller
    
    Args:
        task_id: Geciken görevin ID'si
        new_due_date: Yeni bitiş tarihi (gecikme sonrası)
        project_id: Proje ID'si
        user_id: İşlemi yapan kullanıcı ID'si
    
    Returns:
        dict: {
            'updated_count': int,
            'updated_tasks': [{'id': int, 'title': str, 'old_date': date, 'new_date': date}]
        }
    """
    try:
        # Bu göreve bağlı ardıl görevleri bul (predecessor_id = task_id)
        dependent_tasks = db.session.query(Task).join(
            task_predecessors, Task.id == task_predecessors.c.task_id
        ).filter(
            task_predecessors.c.predecessor_id == task_id,
            Task.project_id == project_id,
            Task.status != 'Tamamlandı'  # Sadece tamamlanmamış görevleri güncelle
        ).all()
        
        if not dependent_tasks:
            return {'updated_count': 0, 'updated_tasks': []}
        
        updated_tasks = []
        
        for dependent_task in dependent_tasks:
            if not dependent_task.due_date:
                continue
            
            # Önceki görevin yeni bitiş tarihinden sonra başlamalı
            # En az 1 gün buffer ekle
            min_start_date = new_due_date + timedelta(days=1)
            
            if dependent_task.due_date <= new_due_date:
                old_date = dependent_task.due_date
                
                # Ardıl görevin yeni tarihini hesapla
                # Önceki görevle arasındaki farkı koru (veya minimum 1 gün ekle)
                date_diff = (dependent_task.due_date - date.today()).days if dependent_task.due_date else 0
                new_dependent_date = max(min_start_date, date.today() + timedelta(days=max(1, date_diff)))
                
                dependent_task.due_date = new_dependent_date
                updated_tasks.append({
                    'id': dependent_task.id,
                    'title': dependent_task.title,
                    'old_date': old_date.isoformat(),
                    'new_date': new_dependent_date.isoformat()
                })
                
                if current_app:
                    current_app.logger.info(
                        f"Ardıl görev güncellendi: Task {dependent_task.id} "
                        f"({old_date} -> {new_dependent_date}) - "
                        f"Öncül görev: {task_id}"
                    )
        
        if updated_tasks:
            db.session.commit()
        
        return {
            'updated_count': len(updated_tasks),
            'updated_tasks': updated_tasks
        }
    
    except Exception as e:
        db.session.rollback()
        if current_app:
            current_app.logger.error(f'Akıllı planlama hatası: {e}')
        return {'updated_count': 0, 'updated_tasks': [], 'error': str(e)}


def check_and_update_delayed_predecessors(task_id, project_id, user_id):
    """
    Bir görev tamamlandığında veya güncellendiğinde, 
    öncül görevlerinin gecikme durumunu kontrol eder ve ardıl görevleri günceller
    """
    try:
        task = Task.query.get(task_id)
        if not task or not task.due_date:
            return {'updated_count': 0, 'updated_tasks': []}
        
        # Bugünün tarihi
        today = date.today()
        
        # Eğer görev geciktiyse (due_date < today) ve tamamlanmadıysa
        if task.due_date < today and task.status != 'Tamamlandı':
            # Ardıl görevleri güncelle
            return update_dependent_tasks_due_dates(
                task_id, 
                task.due_date,  # Gecikmiş tarih
                project_id, 
                user_id
            )
        
        return {'updated_count': 0, 'updated_tasks': []}
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Gecikme kontrolü hatası: {e}')
        return {'updated_count': 0, 'updated_tasks': [], 'error': str(e)}



























