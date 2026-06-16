# -*- coding: utf-8 -*-
"""Stratejik proje detay bağlamı — modern Strategy + ProcessSubStrategyLink üzerinden.

DALGA 3 (2026-06-16): Eskiden legacy MainStrategy/StrategyProcessMatrix (boş tablolar,
ana_strateji/alt_strateji/strategy_process_matrix = 0 satır) okuyordu → stratejik skorlar
hep 0 dönüyordu (bug). portfolio_service._build_portfolio_app_tenant ile aynı modern
desene taşındı: Strategy/SubStrategy + ProcessSubStrategyLink.contribution_pct.
Çıktı sözleşmesi (return dict anahtarları) template uyumu için AYNEN korundu.
"""

from __future__ import annotations

from app.models.core import Strategy, SubStrategy
from app.models.process import Process, ProcessSubStrategyLink
from app.models.portfolio_project import Project
from app_platform.modules.proje.portfolio_service import _resolve_app_process_for_surec


def build_strategy_detail_context(project: Project, tenant_id: int) -> dict:
    # Modern alt stratejiler (aktif, tenant'a ait)
    sub_strategies = (
        SubStrategy.query.join(Strategy)
        .filter(
            Strategy.tenant_id == tenant_id,
            Strategy.is_active.is_(True),
            SubStrategy.is_active.is_(True),
        )
        .all()
    )

    processes = (
        Process.query.filter_by(tenant_id=tenant_id, is_active=True)
        .order_by(Process.code, Process.name)
        .all()
    )

    # Süreç ↔ alt strateji katkı yüzdeleri (modern link tablosu)
    proc_ids = [p.id for p in processes]
    relations_map: dict[tuple[int, int], int] = {}
    if proc_ids:
        links = ProcessSubStrategyLink.query.filter(
            ProcessSubStrategyLink.process_id.in_(proc_ids)
        ).all()
        for link in links:
            pct = link.contribution_pct
            relations_map[(link.sub_strategy_id, link.process_id)] = (
                int(round(pct)) if pct is not None else 0
            )

    process_totals: dict[int, int] = {}
    for process in processes:
        total_score = 0
        for sub_strategy in sub_strategies:
            total_score += relations_map.get((sub_strategy.id, process.id), 0)
        process_totals[process.id] = total_score

    # Projenin ilişkili süreçleri → modern Process'e çözümle, skorla
    project_processes = []
    total_strategic_score = 0
    strong_relations = 0
    weak_relations = 0

    for surec in project.related_processes:
        app_p = _resolve_app_process_for_surec(surec, tenant_id)
        if not app_p:
            continue
        process_score = process_totals.get(app_p.id, 0)
        total_strategic_score += process_score

        for sub_strategy in sub_strategies:
            score = relations_map.get((sub_strategy.id, app_p.id), 0)
            if score >= 9:
                strong_relations += 1
            elif score >= 3:
                weak_relations += 1

        project_processes.append({"process": app_p, "score": process_score})

    project_processes.sort(key=lambda x: x["score"], reverse=True)

    related_process_ids = []
    for surec in project.related_processes:
        app_p = _resolve_app_process_for_surec(surec, tenant_id)
        if app_p:
            related_process_ids.append(app_p.id)

    return {
        "project": project,
        "project_processes": project_processes,
        "total_strategic_score": total_strategic_score,
        "strong_relations": strong_relations,
        "weak_relations": weak_relations,
        "processes": processes,
        "process_totals": process_totals,
        "related_process_ids": related_process_ids,
    }
