"""EVM (Earned Value Management) + CPM (Critical Path) servisi (S62).

PMI/EVM standartları:
  PV  = Planned Value   — Plan + zaman: BAC × (geçen zaman / toplam zaman)
  EV  = Earned Value    — Plan + ilerleme: BAC × (gerçek ilerleme)
  AC  = Actual Cost     — Harcanan gerçek bütçe
  CV  = EV - AC         (>0 bütçe altında)
  SV  = EV - PV         (>0 plandan önde)
  CPI = EV / AC         (>1 bütçe verimli)
  SPI = EV / PV         (>1 zaman verimli)
  EAC = BAC / CPI       — tahmini tamamlanma maliyeti
  ETC = EAC - AC        — tamamlamak için kalan tahmin
  VAC = BAC - EAC       — tamamlanma bütçe sapması

CPM: depends_on_task_id zinciri üzerinden en uzun yol.
"""
from __future__ import annotations

import datetime as _dt
from typing import Optional

from app.models.project import PlanProject, PlanProjectTask


def _task_duration_days(t: PlanProjectTask) -> int:
    if t.start_date and t.end_date:
        return max(1, (t.end_date - t.start_date).days + 1)
    return 1


def _task_pv(t: PlanProjectTask, today: _dt.date, bac: float) -> float:
    if not t.start_date or not t.end_date or bac == 0:
        return 0.0
    if today < t.start_date:
        return 0.0
    if today >= t.end_date:
        return bac
    elapsed = (today - t.start_date).days
    total = (t.end_date - t.start_date).days
    return bac * (elapsed / total) if total > 0 else bac


def compute_project_evm(project_id: int) -> dict:
    """Bir projenin EVM özet metriklerini hesaplar."""
    project = PlanProject.query.get(project_id)
    if not project:
        raise ValueError(f"Proje bulunamadı: {project_id}")

    tasks = (
        PlanProjectTask.query.filter_by(project_id=project_id, is_active=True).all()
    )
    today = _dt.date.today()

    bac_total = 0.0  # Budget At Completion
    pv_total = 0.0
    ev_total = 0.0
    ac_total = 0.0
    task_rows = []

    for t in tasks:
        bac = float(t.planned_budget) if t.planned_budget else 0.0
        ac = float(t.actual_cost) if t.actual_cost else 0.0
        progress = (t.progress_pct or 0) / 100.0
        ev = bac * progress
        pv = _task_pv(t, today, bac)
        bac_total += bac
        pv_total += pv
        ev_total += ev
        ac_total += ac
        task_rows.append({
            "id": t.id, "name": t.name, "status": t.status,
            "start_date": t.start_date.isoformat() if t.start_date else None,
            "end_date": t.end_date.isoformat() if t.end_date else None,
            "progress_pct": t.progress_pct or 0,
            "bac": bac, "pv": round(pv, 2), "ev": round(ev, 2), "ac": ac,
            "cv": round(ev - ac, 2),
            "sv": round(ev - pv, 2),
            "cpi": round(ev / ac, 3) if ac > 0 else None,
            "spi": round(ev / pv, 3) if pv > 0 else None,
            "depends_on_task_id": t.depends_on_task_id,
            "duration_days": _task_duration_days(t),
        })

    cpi = ev_total / ac_total if ac_total > 0 else None
    spi = ev_total / pv_total if pv_total > 0 else None
    eac = (bac_total / cpi) if cpi and cpi > 0 else None

    return {
        "project_id": project.id,
        "project_name": project.name,
        "computed_at": _dt.datetime.utcnow().isoformat(),
        "bac": round(bac_total, 2),
        "pv": round(pv_total, 2),
        "ev": round(ev_total, 2),
        "ac": round(ac_total, 2),
        "cv": round(ev_total - ac_total, 2),
        "sv": round(ev_total - pv_total, 2),
        "cpi": round(cpi, 3) if cpi else None,
        "spi": round(spi, 3) if spi else None,
        "eac": round(eac, 2) if eac else None,
        "etc": round(eac - ac_total, 2) if eac else None,
        "vac": round(bac_total - eac, 2) if eac else None,
        "tasks": task_rows,
        "critical_path": compute_critical_path(tasks),
    }


def compute_critical_path(tasks: list[PlanProjectTask]) -> list[int]:
    """CPM (Critical Path Method) — en uzun süreli görev zincirini bulur.

    depends_on_task_id ile kurulan DAG üzerinde topological sort + dinamik
    programlama. Dönen: kritik yoldaki task id'lerin sıralı listesi.
    """
    if not tasks:
        return []
    by_id = {t.id: t for t in tasks}
    duration = {t.id: _task_duration_days(t) for t in tasks}

    # earliest_finish[t] = max(earliest_finish[pred]) + duration[t]
    memo = {}

    def ef(tid: int, stack: tuple = ()) -> tuple[int, list[int]]:
        if tid in stack:  # döngü
            return (0, [])
        if tid in memo:
            return memo[tid]
        t = by_id.get(tid)
        if not t:
            return (0, [])
        if t.depends_on_task_id and t.depends_on_task_id in by_id:
            pred_d, pred_path = ef(t.depends_on_task_id, stack + (tid,))
            result = (pred_d + duration[tid], pred_path + [tid])
        else:
            result = (duration[tid], [tid])
        memo[tid] = result
        return result

    best = (0, [])
    for t in tasks:
        d, path = ef(t.id)
        if d > best[0]:
            best = (d, path)
    return best[1]
