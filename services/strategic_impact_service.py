# -*- coding: utf-8 -*-
"""
Strategic Impact Service
Strateji -> Proje -> Görev ilerleme etkisini hesaplar.
"""
from flask import current_app
from sqlalchemy import func, case

from extensions import cache
from models import (
    db,
    AnaStrateji,
    AltStrateji,
    StrategyProcessMatrix,
    Project,
    Task,
    project_related_processes,
)
from services.cache_service import (
    cache_key_with_org,
    CACHE_PREFIX_ORG_STATS,
    CACHE_TIMEOUT_MEDIUM,
)


def _get_project_task_completion(project_ids):
    """Projeler için görev tamamlanma oranlarını hazırlar."""
    if not project_ids:
        return {}

    rows = db.session.query(
        Task.project_id.label('project_id'),
        func.count(Task.id).label('total_tasks'),
        func.sum(
            case((Task.status == 'Tamamlandı', 1), else_=0)
        ).label('completed_tasks')
    ).filter(
        Task.project_id.in_(project_ids),
        Task.is_archived == False
    ).group_by(Task.project_id).all()

    summary = {}
    for row in rows:
        total = row.total_tasks or 0
        completed = row.completed_tasks or 0
        if total > 0:
            rate = (completed / total) * 100
        else:
            rate = 100.0
        summary[row.project_id] = {
            'total': total,
            'completed': completed,
            'rate': round(rate, 2)
        }
    return summary


def calculate_strategy_health(strategy_id, kurum_id=None):
    """
    Strateji sağlık skorunu hesapla.

    - Stratejiye bağlı süreçleri bul
    - Süreçlere bağlı projeleri al
    - Proje tamamlanma oranlarının ortalamasını döndür
    """
    try:
        strategy = AnaStrateji.query.get(strategy_id)
        if not strategy:
            return None

        if kurum_id and strategy.kurum_id != kurum_id:
            return None

        sub_ids = [
            s.id for s in AltStrateji.query.filter_by(ana_strateji_id=strategy.id).all()
        ]

        if not sub_ids:
            return {
                'strategy_id': strategy.id,
                'strategy_code': strategy.code,
                'strategy_name': strategy.ad,
                'project_count': 0,
                'health_percent': 0.0,
                'orphaned': True,
                'status': 'Orphaned'
            }

        process_ids = [
            row.process_id for row in db.session.query(
                StrategyProcessMatrix.process_id
            ).filter(
                StrategyProcessMatrix.sub_strategy_id.in_(sub_ids),
                StrategyProcessMatrix.relationship_score > 0
            ).distinct().all()
        ]

        if not process_ids:
            return {
                'strategy_id': strategy.id,
                'strategy_code': strategy.code,
                'strategy_name': strategy.ad,
                'project_count': 0,
                'health_percent': 0.0,
                'orphaned': True,
                'status': 'Orphaned'
            }

        project_ids = [
            row.project_id for row in db.session.query(
                project_related_processes.c.project_id
            ).filter(
                project_related_processes.c.surec_id.in_(process_ids)
            ).distinct().all()
        ]

        if not project_ids:
            return {
                'strategy_id': strategy.id,
                'strategy_code': strategy.code,
                'strategy_name': strategy.ad,
                'project_count': 0,
                'health_percent': 0.0,
                'orphaned': True,
                'status': 'Orphaned'
            }

        projects = Project.query.filter(
            Project.id.in_(project_ids),
            Project.kurum_id == strategy.kurum_id,
            Project.is_archived == False
        ).all()

        if not projects:
            return {
                'strategy_id': strategy.id,
                'strategy_code': strategy.code,
                'strategy_name': strategy.ad,
                'project_count': 0,
                'health_percent': 0.0,
                'orphaned': True,
                'status': 'Orphaned'
            }

        completion_map = _get_project_task_completion([p.id for p in projects])
        rates = [completion_map.get(p.id, {}).get('rate', 100.0) for p in projects]
        avg_rate = round(sum(rates) / len(rates), 2) if rates else 0.0

        status = 'On Track'
        if avg_rate < 50:
            status = 'Risk'
        elif avg_rate < 75:
            status = 'Dikkat'

        return {
            'strategy_id': strategy.id,
            'strategy_code': strategy.code,
            'strategy_name': strategy.ad,
            'project_count': len(projects),
            'health_percent': avg_rate,
            'orphaned': False,
            'status': status
        }
    except Exception as e:
        if current_app:
            current_app.logger.error(f"Strateji sağlık hesaplama hatası: {e}", exc_info=True)
        return {
            'strategy_id': strategy_id,
            'strategy_code': None,
            'strategy_name': 'Bilinmiyor',
            'project_count': 0,
            'health_percent': 0.0,
            'orphaned': True,
            'status': 'Risk'
        }


def get_strategic_impact_summary(kurum_id):
    """Tüm ana stratejiler için stratejik ilerleme özetini döndür."""
    cache_key = cache_key_with_org(f"{CACHE_PREFIX_ORG_STATS}:strategic_impact", kurum_id)
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    strategies = AnaStrateji.query.filter_by(kurum_id=kurum_id).all()
    results = []
    for strategy in strategies:
        item = calculate_strategy_health(strategy.id, kurum_id=kurum_id)
        if item:
            results.append(item)

    results.sort(key=lambda x: (x.get('health_percent', 0.0)), reverse=True)
    cache.set(cache_key, results, timeout=CACHE_TIMEOUT_MEDIUM)
    return results
