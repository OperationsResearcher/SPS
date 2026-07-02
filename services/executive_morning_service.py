"""Yönetici sabah özeti — KPI, faaliyet ve proje durumunu birleştirir."""

from __future__ import annotations
from datetime import date, timedelta, datetime, timezone
from sqlalchemy import func
from flask_babel import gettext as _
from app.models import db
from app.models.process import Process, ProcessKpi, KpiData, ProcessActivity
from app.models.portfolio_project import Project, Task


def get_morning_summary(tenant_id: int, user_id: int) -> dict:
    """
    Yöneticinin sabah ekranı için özet veri döner.
    Tüm hesaplamalar tek çağrıda yapılır.
    """
    today = date.today()
    week_end = today + timedelta(days=7)
    current_year = today.year

    # ── Kritik KPI'lar (son girilen değeri hedefin %80 altında) ──────────────
    kpis_below_target: list[dict] = []
    try:
        kpis = (
            ProcessKpi.query
            .join(Process, Process.id == ProcessKpi.process_id)
            .filter(
                Process.tenant_id == tenant_id,
                Process.is_active == True,
                ProcessKpi.is_active == True,
            )
            .all()
        )
        kpi_ids = [k.id for k in kpis]
        if kpi_ids:
            latest_data = (
                db.session.query(
                    KpiData.process_kpi_id,
                    func.max(KpiData.data_date).label("last_date"),
                )
                .filter(
                    KpiData.process_kpi_id.in_(kpi_ids),
                    KpiData.year == current_year,
                    KpiData.is_active == True,
                )
                .group_by(KpiData.process_kpi_id)
                .all()
            )
            date_map = {row.process_kpi_id: row.last_date for row in latest_data}
            kpi_map = {k.id: k for k in kpis}

            for kpi_id, last_date in date_map.items():
                entry = KpiData.query.filter_by(
                    process_kpi_id=kpi_id, data_date=last_date, is_active=True
                ).first()
                if not entry:
                    continue
                kpi = kpi_map.get(kpi_id)
                if not kpi:
                    continue
                try:
                    actual = float(entry.actual_value)
                    target = float(kpi.target_value or 0)
                    if target <= 0:
                        continue
                    ratio = actual / target
                    direction = (kpi.direction or "Increasing").lower()
                    is_bad = (
                        ratio < 0.8 if direction != "decreasing"
                        else ratio > 1.2
                    )
                    if is_bad:
                        proc = kpi.process
                        kpis_below_target.append({
                            "kpi_id": kpi_id,
                            "kpi_name": kpi.name,
                            "process_name": proc.name if proc else "",
                            "actual": actual,
                            "target": target,
                            "ratio_pct": round(ratio * 100, 1),
                        })
                except (TypeError, ValueError):
                    continue
    except Exception as e:
        pass

    # ── Geciken faaliyetler ───────────────────────────────────────────────────
    overdue_activities: list[dict] = []
    try:
        rows = (
            ProcessActivity.query
            .join(Process, Process.id == ProcessActivity.process_id)
            .filter(
                Process.tenant_id == tenant_id,
                Process.is_active == True,
                ProcessActivity.is_active == True,
                ProcessActivity.status.notin_(["Tamamlandı", "İptal"]),
                ProcessActivity.end_date < today,
            )
            .order_by(ProcessActivity.end_date.asc())
            .limit(10)
            .all()
        )
        for a in rows:
            overdue_activities.append({
                "id": a.id,
                "name": a.name,
                "process_id": a.process_id,
                "end_date": a.end_date.isoformat() if a.end_date else None,
                "days_overdue": (today - a.end_date).days if a.end_date else 0,
            })
    except Exception:
        pass

    # ── Bu haftaki faaliyetler ────────────────────────────────────────────────
    upcoming_activities: list[dict] = []
    try:
        rows = (
            ProcessActivity.query
            .join(Process, Process.id == ProcessActivity.process_id)
            .filter(
                Process.tenant_id == tenant_id,
                Process.is_active == True,
                ProcessActivity.is_active == True,
                ProcessActivity.status.notin_(["Tamamlandı", "İptal"]),
                ProcessActivity.end_date >= today,
                ProcessActivity.end_date <= week_end,
            )
            .order_by(ProcessActivity.end_date.asc())
            .limit(10)
            .all()
        )
        for a in rows:
            upcoming_activities.append({
                "id": a.id,
                "name": a.name,
                "process_id": a.process_id,
                "end_date": a.end_date.isoformat() if a.end_date else None,
            })
    except Exception:
        pass

    # ── Geciken projeler ──────────────────────────────────────────────────────
    overdue_projects: list[dict] = []
    try:
        rows = (
            Project.query
            .filter(
                Project.tenant_id == tenant_id,
                Project.is_active == True,
                Project.is_archived == False,
                Project.end_date < today,
            )
            .order_by(Project.end_date.asc())
            .limit(5)
            .all()
        )
        for p in rows:
            overdue_projects.append({
                "id": p.id,
                "name": p.name,
                "end_date": p.end_date.isoformat() if p.end_date else None,
                "days_overdue": (today - p.end_date).days if p.end_date else 0,
            })
    except Exception:
        pass

    # ── Özet metin ────────────────────────────────────────────────────────────
    parts = []
    if kpis_below_target:
        parts.append(_("%(n)s PG hedefin %%80 altında", n=len(kpis_below_target)))
    if overdue_activities:
        parts.append(_("%(n)s geciken faaliyet", n=len(overdue_activities)))
    if overdue_projects:
        parts.append(_("%(n)s geciken proje", n=len(overdue_projects)))

    if parts:
        summary_text = _("Dikkat: ") + ", ".join(parts) + _(". Detaylar aşağıda.")
    else:
        summary_text = _("Her şey yolunda görünüyor. Bugün iyi çalışmalar!")

    return {
        "date": today.isoformat(),
        "summary_text": summary_text,
        "kpis_below_target": kpis_below_target[:5],
        "overdue_activities": overdue_activities,
        "upcoming_activities": upcoming_activities,
        "overdue_projects": overdue_projects,
        "counts": {
            "kpis_critical": len(kpis_below_target),
            "activities_overdue": len(overdue_activities),
            "activities_upcoming": len(upcoming_activities),
            "projects_overdue": len(overdue_projects),
        },
    }
