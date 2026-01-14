# -*- coding: utf-8 -*-
"""Haftalık e-posta/mesaj digest üretimi için özet veriler."""
from datetime import datetime, timedelta
from models import Task, Project


def project_digest(project_id: int):
    project = Project.query.get(project_id)
    tasks = Task.query.filter_by(project_id=project_id).all()
    overdue = [t for t in tasks if t.due_date and t.due_date < datetime.utcnow().date() and (t.status or '').lower() != 'tamamlandı']
    completed_last_7d = [t for t in tasks if t.completed_at and t.completed_at >= datetime.utcnow() - timedelta(days=7)]
    upcoming = [t for t in tasks if t.due_date and 0 <= (t.due_date - datetime.utcnow().date()).days <= 7]
    return {
        'project': project.name if project else None,
        'counts': {
            'total': len(tasks),
            'overdue': len(overdue),
            'completed_last_7d': len(completed_last_7d),
            'upcoming_7d': len(upcoming),
        },
        'items': {
            'overdue': [{'id': t.id, 'title': t.title, 'due_date': t.due_date.isoformat() if t.due_date else None} for t in overdue],
            'completed_last_7d': [{'id': t.id, 'title': t.title} for t in completed_last_7d],
            'upcoming_7d': [{'id': t.id, 'title': t.title, 'due_date': t.due_date.isoformat() if t.due_date else None} for t in upcoming],
        }
    }
