# -*- coding: utf-8 -*-
"""Stratejik proje portföyü — önce legacy matris (kurum), yoksa App süreç + tenant stratejisi."""

from __future__ import annotations

from sqlalchemy import func

from app.models.core import Strategy, SubStrategy as AppSubStrategy
from app.models.process import Process as AppProcess, ProcessSubStrategyLink
from models import (
    db,
    Project,
    Process,
    SubStrategy,
    MainStrategy,
    StrategyProcessMatrix,
)


def _legacy_sub_strategy_count(kurum_id: int) -> int:
    return (
        db.session.query(SubStrategy)
        .join(MainStrategy)
        .filter(MainStrategy.kurum_id == kurum_id)
        .count()
    )


def _build_portfolio_legacy(kurum_id: int) -> dict:
    sub_strategies = (
        db.session.query(SubStrategy)
        .join(MainStrategy)
        .filter(MainStrategy.kurum_id == kurum_id)
        .all()
    )

    processes = Process.query.filter_by(kurum_id=kurum_id).all()

    matrix_relations = (
        StrategyProcessMatrix.query.join(SubStrategy)
        .join(MainStrategy)
        .filter(MainStrategy.kurum_id == kurum_id)
        .all()
    )

    relations_map: dict[tuple[int, int], int] = {}
    for relation in matrix_relations:
        key = (relation.sub_strategy_id, relation.process_id)
        relations_map[key] = relation.relationship_score

    process_totals: dict[int, int] = {}
    for process in processes:
        total_score = 0
        for sub_strategy in sub_strategies:
            key = (sub_strategy.id, process.id)
            score = relations_map.get(key, 0)
            total_score += score
        process_totals[process.id] = total_score

    projects = Project.query.filter_by(kurum_id=kurum_id, is_archived=False).all()

    projects_with_scores = []
    for project in projects:
        project_score = 0
        related_process_names = []
        for process in project.related_processes:
            process_score = process_totals.get(process.id, 0)
            project_score += process_score
            related_process_names.append(
                {
                    "name": process.ad,
                    "code": process.code,
                    "score": process_score,
                }
            )

        projects_with_scores.append(
            {
                "project": project,
                "strategic_score": project_score,
                "related_processes": related_process_names,
            }
        )

    projects_with_scores.sort(key=lambda x: x["strategic_score"], reverse=True)

    return {
        "projects_with_scores": projects_with_scores,
        "process_totals": process_totals,
        "portfolio_source": "legacy_matrix",
    }


def _resolve_app_process_for_surec(surec, tenant_id: int) -> AppProcess | None:
    """Bağlı süreç (Surec) ile App sürecini kod veya ada göre eşle."""
    if not surec:
        return None
    q = AppProcess.query.filter_by(tenant_id=tenant_id, is_active=True)
    if getattr(surec, "code", None):
        p = q.filter(AppProcess.code == surec.code).first()
        if p:
            return p
    ad = (getattr(surec, "ad", None) or "").strip()
    if ad:
        p = q.filter(func.lower(AppProcess.name) == func.lower(ad)).first()
        if p:
            return p
    return None


def _build_portfolio_app_tenant(tenant_id: int) -> dict:
    sub_strategies = (
        AppSubStrategy.query.join(Strategy)
        .filter(
            Strategy.tenant_id == tenant_id,
            Strategy.is_active.is_(True),
            AppSubStrategy.is_active.is_(True),
        )
        .all()
    )

    processes = (
        AppProcess.query.filter_by(tenant_id=tenant_id, is_active=True).order_by(AppProcess.code, AppProcess.name).all()
    )
    proc_ids = [p.id for p in processes]
    relations_map: dict[tuple[int, int], int] = {}
    links = []
    if proc_ids:
        links = ProcessSubStrategyLink.query.filter(ProcessSubStrategyLink.process_id.in_(proc_ids)).all()
    for link in links:
        key = (link.sub_strategy_id, link.process_id)
        pct = link.contribution_pct
        relations_map[key] = int(round(pct)) if pct is not None else 0

    process_totals: dict[int, int] = {}
    for process in processes:
        total_score = 0
        for sub_strategy in sub_strategies:
            key = (sub_strategy.id, process.id)
            total_score += relations_map.get(key, 0)
        process_totals[process.id] = total_score

    projects = Project.query.filter_by(kurum_id=tenant_id, is_archived=False).all()

    projects_with_scores = []
    for project in projects:
        project_score = 0
        related_process_names = []
        for surec in project.related_processes:
            app_p = _resolve_app_process_for_surec(surec, tenant_id)
            process_score = process_totals.get(app_p.id, 0) if app_p else 0
            project_score += process_score
            related_process_names.append(
                {
                    "name": surec.ad,
                    "code": surec.code,
                    "score": process_score,
                }
            )

        projects_with_scores.append(
            {
                "project": project,
                "strategic_score": project_score,
                "related_processes": related_process_names,
            }
        )

    projects_with_scores.sort(key=lambda x: x["strategic_score"], reverse=True)

    return {
        "projects_with_scores": projects_with_scores,
        "process_totals": process_totals,
        "portfolio_source": "app_tenant",
    }


def build_portfolio_context(tenant_id: int) -> dict:
    """Legacy ana/alt strateji + matris varsa onu kullan; yoksa App Strategy + processes + linkler."""
    if _legacy_sub_strategy_count(tenant_id) > 0:
        return _build_portfolio_legacy(tenant_id)
    return _build_portfolio_app_tenant(tenant_id)
