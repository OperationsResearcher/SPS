# -*- coding: utf-8 -*-
"""Stratejik proje detay bağlamı — main.strategy_project_detail ile aynı mantık."""

from __future__ import annotations

from models import (
    db,
    Project,
    Process,
    SubStrategy,
    MainStrategy,
    StrategyProcessMatrix,
)


def build_strategy_detail_context(project: Project, kurum_id: int) -> dict:
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

    relations_map = {}
    for relation in matrix_relations:
        key = (relation.sub_strategy_id, relation.process_id)
        relations_map[key] = relation.relationship_score

    process_totals = {}
    for process in processes:
        total_score = 0
        for sub_strategy in sub_strategies:
            key = (sub_strategy.id, process.id)
            score = relations_map.get(key, 0)
            total_score += score
        process_totals[process.id] = total_score

    project_processes = []
    total_strategic_score = 0
    strong_relations = 0
    weak_relations = 0

    for process in project.related_processes:
        process_score = process_totals.get(process.id, 0)
        total_strategic_score += process_score

        for sub_strategy in sub_strategies:
            key = (sub_strategy.id, process.id)
            score = relations_map.get(key, 0)
            if score == 9:
                strong_relations += 1
            elif score == 3:
                weak_relations += 1

        project_processes.append({"process": process, "score": process_score})

    project_processes.sort(key=lambda x: x["score"], reverse=True)
    related_process_ids = [p.id for p in project.related_processes]

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
