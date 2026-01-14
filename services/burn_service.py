# -*- coding: utf-8 -*-
"""Burnup/Burndown hesapları (basitleştirilmiş)."""
from datetime import date, timedelta
from models import Task


def _task_effort(t: Task) -> float:
    return float(t.estimated_time or 1.0)


def _date_or_today(d):
    return d if isinstance(d, date) else date.today()


def _date_range(start: date, end: date):
    cur = start
    while cur <= end:
        yield cur
        cur += timedelta(days=1)


def burn_charts(project_id: int):
    tasks = Task.query.filter_by(project_id=project_id).all()
    if not tasks:
        today = date.today()
        return {
            'success': True,
            'burnup': [{'date': today.isoformat(), 'done': 0, 'scope': 0}],
            'burndown': [{'date': today.isoformat(), 'remaining': 0, 'scope': 0}],
        }

    start_candidates = [t.start_date for t in tasks if t.start_date]
    due_candidates = [t.due_date for t in tasks if t.due_date]
    start_day = min(start_candidates) if start_candidates else date.today()
    end_day = max(due_candidates) if due_candidates else date.today() + timedelta(days=14)

    scope = sum(_task_effort(t) for t in tasks)
    burnup = []
    burndown = []

    for d in _date_range(start_day, end_day):
        done = 0.0
        remaining = 0.0
        for t in tasks:
            effort = _task_effort(t)
            if t.completed_at and t.completed_at.date() <= d:
                done += effort
            else:
                progress = float(t.progress or 0.0) / 100.0
                partial = min(effort, effort * progress)
                done += partial
                remaining += max(0.0, effort - partial)
        burnup.append({'date': d.isoformat(), 'done': done, 'scope': scope})
        burndown.append({'date': d.isoformat(), 'remaining': remaining, 'scope': scope})

    return {'success': True, 'burnup': burnup, 'burndown': burndown}
