# -*- coding: utf-8 -*-
"""
Kaynak ve Kapasite Planlama Servisleri
Kullanıcı kapasite analizi ve aşırı yükleme uyarıları
"""
from datetime import datetime, date, timedelta
from flask import current_app
from models import (
    db, User, Project, Task, TimeEntry
)
from sqlalchemy import func, and_, or_
from collections import defaultdict


def calculate_user_capacity(user_id, start_date, end_date):
    """
    Kullanıcının belirli tarih aralığındaki kapasitesini hesaplar
    
    Args:
        user_id: Kullanıcı ID
        start_date: Başlangıç tarihi
        end_date: Bitiş tarihi
    
    Returns:
        dict: {
            'total_hours': float,
            'allocated_hours': float,
            'available_hours': float,
            'utilization_rate': float (0-100),
            'overload_days': list,
            'daily_breakdown': list
        }
    """
    try:
        # Günlük çalışma saati (varsayılan 8 saat)
        daily_capacity = 8.0
        
        # Tarih aralığındaki toplam iş günü sayısı
        current_date = start_date
        total_days = 0
        work_days = 0
        
        while current_date <= end_date:
            total_days += 1
            # Hafta sonu kontrolü (Cumartesi=5, Pazar=6)
            if current_date.weekday() < 5:  # Pazartesi-Cuma
                work_days += 1
            current_date += timedelta(days=1)
        
        total_capacity_hours = work_days * daily_capacity
        
        # Kullanıcının bu tarih aralığındaki görevlerini bul
        user_tasks = Task.query.filter(
            Task.assigned_to_id == user_id,
            Task.status != 'Tamamlandı',
            or_(
                and_(Task.due_date >= start_date, Task.due_date <= end_date),
                Task.due_date.is_(None)
            )
        ).all()
        
        # Günlük dağılım hesaplama
        daily_breakdown = defaultdict(float)
        allocated_hours = 0
        
        for task in user_tasks:
            if task.estimated_time:
                # Görevin başlangıç ve bitiş tarihleri
                task_start = task.created_at.date() if task.created_at else start_date
                task_end = task.due_date if task.due_date else end_date
                
                # Tarih aralığı içindeki günleri bul
                task_days = []
                current = max(task_start, start_date)
                while current <= min(task_end, end_date):
                    if current.weekday() < 5:  # İş günü
                        task_days.append(current)
                    current += timedelta(days=1)
                
                # Görev süresini günlere eşit dağıt
                if task_days:
                    hours_per_day = task.estimated_time / len(task_days)
                    for day in task_days:
                        daily_breakdown[day.isoformat()] += hours_per_day
                    allocated_hours += task.estimated_time
        
        # Günlük breakdown listesi oluştur
        daily_list = []
        overload_days = []
        current_date = start_date
        
        while current_date <= end_date:
            if current_date.weekday() < 5:  # İş günü
                day_hours = daily_breakdown.get(current_date.isoformat(), 0)
                utilization = (day_hours / daily_capacity) * 100
                
                daily_list.append({
                    'date': current_date.isoformat(),
                    'allocated_hours': round(day_hours, 2),
                    'capacity_hours': daily_capacity,
                    'utilization_rate': round(utilization, 1),
                    'is_overloaded': day_hours > daily_capacity
                })
                
                if day_hours > daily_capacity:
                    overload_days.append(current_date.isoformat())
            
            current_date += timedelta(days=1)
        
        utilization_rate = (allocated_hours / total_capacity_hours * 100) if total_capacity_hours > 0 else 0
        
        return {
            'total_hours': round(total_capacity_hours, 2),
            'allocated_hours': round(allocated_hours, 2),
            'available_hours': round(total_capacity_hours - allocated_hours, 2),
            'utilization_rate': round(utilization_rate, 1),
            'overload_days': overload_days,
            'daily_breakdown': daily_list,
            'work_days': work_days
        }
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Kullanıcı kapasite hesaplama hatası: {e}')
        return None


def check_task_overload(task_id, assigned_user_id, due_date):
    """
    Görev atamasının kullanıcı kapasitesini aşıp aşmadığını kontrol eder
    
    Args:
        task_id: Görev ID (yeni görev için None olabilir)
        assigned_user_id: Atanan kullanıcı ID
        due_date: Görev bitiş tarihi
        estimated_time: Tahmini süre (saat)
    
    Returns:
        dict: {
            'is_overloaded': bool,
            'overload_percentage': float,
            'conflicting_tasks': list,
            'warning_message': str
        }
    """
    try:
        if not assigned_user_id or not due_date:
            return {
                'is_overloaded': False,
                'overload_percentage': 0,
                'conflicting_tasks': [],
                'warning_message': None
            }
        
        # Görevin tahmini süresini al
        task = Task.query.get(task_id) if task_id else None
        estimated_time = task.estimated_time if task and task.estimated_time else 8.0
        
        # Görev tarihi için kapasite kontrolü
        # Görevin başlangıç tarihini tahmin et (due_date'den geriye doğru)
        # Basit varsayım: Görev 1 hafta sürüyor
        start_date = due_date - timedelta(days=7)
        capacity_data = calculate_user_capacity(assigned_user_id, start_date, due_date)
        
        if not capacity_data:
            return {
                'is_overloaded': False,
                'overload_percentage': 0,
                'conflicting_tasks': [],
                'warning_message': None
            }
        
        # Görevin tarih aralığındaki günlük dağılımını kontrol et
        daily_capacity = 8.0
        hours_per_day = estimated_time / 7  # 1 haftaya eşit dağıt
        
        # Çakışan görevleri bul
        conflicting_tasks = Task.query.filter(
            Task.assigned_to_id == assigned_user_id,
            Task.status != 'Tamamlandı',
            Task.id != task_id if task_id else True,
            Task.due_date >= start_date,
            Task.due_date <= due_date
        ).all()
        
        # Günlük yük kontrolü
        overload_days = []
        current_date = start_date
        while current_date <= due_date:
            if current_date.weekday() < 5:  # İş günü
                day_key = current_date.isoformat()
                existing_hours = sum(
                    t.estimated_time / 7 for t in conflicting_tasks
                    if t.due_date and start_date <= t.due_date <= due_date
                )
                total_hours = existing_hours + hours_per_day
                
                if total_hours > daily_capacity:
                    overload_days.append(current_date.isoformat())
            
            current_date += timedelta(days=1)
        
        is_overloaded = len(overload_days) > 0
        overload_percentage = (len(overload_days) / max(1, len([d for d in range((due_date - start_date).days + 1) if (start_date + timedelta(days=d)).weekday() < 5]))) * 100
        
        warning_message = None
        if is_overloaded:
            warning_message = f"Bu görev ataması kullanıcının kapasitesini aşıyor. {len(overload_days)} iş gününde aşırı yükleme var."
        
        return {
            'is_overloaded': is_overloaded,
            'overload_percentage': round(overload_percentage, 1),
            'conflicting_tasks': [{'id': t.id, 'title': t.title, 'due_date': t.due_date.isoformat() if t.due_date else None} for t in conflicting_tasks],
            'warning_message': warning_message,
            'overload_days': overload_days
        }
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Görev aşırı yükleme kontrolü hatası: {e}')
        return {
            'is_overloaded': False,
            'overload_percentage': 0,
            'conflicting_tasks': [],
            'warning_message': None
        }


def get_resource_heatmap(project_id, start_date, end_date):
    """
    Proje için kaynak ısı haritası oluşturur
    
    Returns:
        dict: {
            'users': [
                {
                    'user_id': int,
                    'user_name': str,
                    'daily_utilization': list,
                    'average_utilization': float,
                    'overload_days': int
                }
            ],
            'date_range': list
        }
    """
    try:
        project = Project.query.get(project_id)
        if not project:
            return None
        
        # Proje üyelerini al
        project_members = project.members if project.members else []
        if project.manager and project.manager not in project_members:
            project_members.append(project.manager)
        
        users_data = []
        date_range = []
        
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # İş günü
                date_range.append(current_date.isoformat())
            current_date += timedelta(days=1)
        
        for user in project_members:
            capacity_data = calculate_user_capacity(user.id, start_date, end_date)
            
            if capacity_data:
                daily_utilization = {}
                for day_data in capacity_data.get('daily_breakdown', []):
                    daily_utilization[day_data['date']] = day_data['utilization_rate']
                
                users_data.append({
                    'user_id': user.id,
                    'user_name': f"{user.first_name} {user.last_name}",
                    'daily_utilization': daily_utilization,
                    'average_utilization': capacity_data['utilization_rate'],
                    'overload_days': len(capacity_data['overload_days']),
                    'total_hours': capacity_data['total_hours'],
                    'allocated_hours': capacity_data['allocated_hours']
                })
        
        return {
            'users': users_data,
            'date_range': date_range,
            'start_date': start_date.isoformat(),
            'end_date': end_date.isoformat()
        }
    
    except Exception as e:
        if current_app:
            current_app.logger.error(f'Kaynak ısı haritası oluşturma hatası: {e}')
        return None
























