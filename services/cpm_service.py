# -*- coding: utf-8 -*-
"""
CPM ve kritik yol hesaplamaları.
Basitleştirilmiş yaklaşım: tüm bağımlılık tiplerini start-of-successor constraint'ine indirger.
"""
from __future__ import annotations
from datetime import timedelta
from collections import defaultdict, deque
from typing import Dict, List, Tuple
from models import Task, TaskDependency, task_predecessors
from extensions import db


def _duration_days(task: Task) -> int:
    if task.start_date and task.due_date:
        return max(1, (task.due_date - task.start_date).days + 1)
    if task.estimated_time:
        return max(1, int(round(task.estimated_time)))
    return 1


def _edge_offset(dep_type: str, pred_duration: int, succ_duration: int, lag: int) -> int:
    dep_type = (dep_type or 'FS').upper()
    lag = lag or 0
    if dep_type == 'SS':
        return lag
    if dep_type == 'FF':
        return pred_duration + lag - succ_duration
    if dep_type == 'SF':
        return lag - succ_duration
    # default FS
    return pred_duration + lag


def _collect_dependencies(project_id: int):
    deps = []
    try:
        TaskDependency.__table__.create(db.engine, checkfirst=True)
    except Exception:
        pass
    dep_rows = TaskDependency.query.filter_by(project_id=project_id).all()
    if dep_rows:
        for d in dep_rows:
            deps.append((d.predecessor_id, d.successor_id, d.dependency_type or 'FS', d.lag_days or 0))
    else:
        rows = db.session.query(task_predecessors.c.predecessor_id, task_predecessors.c.task_id).\
            join(Task, Task.id == task_predecessors.c.task_id).\
            filter(Task.project_id == project_id).all()
        for pred_id, succ_id in rows:
            deps.append((pred_id, succ_id, 'FS', 0))
    return deps


def compute_cpm(project_id: int) -> Dict:
    tasks = {t.id: t for t in Task.query.filter_by(project_id=project_id).all()}
    deps = _collect_dependencies(project_id)
    duration = {tid: _duration_days(t) for tid, t in tasks.items()}

    succ_map: Dict[int, List[Tuple[int, str, int]]] = defaultdict(list)
    pred_map: Dict[int, List[Tuple[int, str, int]]] = defaultdict(list)
    indeg = defaultdict(int)

    for pred_id, succ_id, dep_type, lag in deps:
        if pred_id not in tasks or succ_id not in tasks:
            continue
        succ_map[pred_id].append((succ_id, dep_type, lag))
        pred_map[succ_id].append((pred_id, dep_type, lag))
        indeg[succ_id] += 1
        indeg.setdefault(pred_id, 0)

    es = {tid: 0 for tid in tasks}
    ef = {tid: duration[tid] for tid in tasks}

    # Topological order (Kahn)
    q = deque([tid for tid in tasks if indeg.get(tid, 0) == 0])
    topo = []
    while q:
        u = q.popleft()
        topo.append(u)
        for v, dep_type, lag in succ_map.get(u, []):
            indeg[v] -= 1
            if indeg[v] == 0:
                q.append(v)
            # forward constraint
            off = _edge_offset(dep_type, duration[u], duration[v], lag)
            es[v] = max(es[v], ef[u] + off)
            ef[v] = es[v] + duration[v]

    project_finish = max(ef.values()) if ef else 0

    ls = {tid: project_finish - duration[tid] for tid in tasks}
    lf = {tid: project_finish for tid in tasks}

    for u in reversed(topo):
        for pred_id, dep_type, lag in pred_map.get(u, []):
            off = _edge_offset(dep_type, duration[pred_id], duration[u], lag)
            lf_candidate = ls[u] - off
            if lf_candidate < lf[pred_id]:
                lf[pred_id] = lf_candidate
                ls[pred_id] = lf[pred_id] - duration[pred_id]

    result = []
    for tid, t in tasks.items():
        slack = ls[tid] - es[tid]
        result.append({
            'task_id': tid,
            'title': t.title,
            'duration': duration[tid],
            'es': es[tid],
            'ef': ef[tid],
            'ls': ls[tid],
            'lf': lf[tid],
            'slack': slack,
            'is_critical': slack == 0,
        })

    critical_ids = [r['task_id'] for r in result if r['is_critical']]
    return {
        'success': True,
        'project_finish': project_finish,
        'critical_task_ids': critical_ids,
        'schedule': result,
    }
