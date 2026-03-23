"""Süreç faaliyeti otomatik gerçekleşme ve otomatik PGV servisleri."""

from __future__ import annotations

from datetime import datetime

from app.models import db
from app.models.process import KpiData, KpiDataAudit, ProcessActivity


def _get_activity_period_fields(kpi, data_date):
    period_type = (kpi.period or '').strip().lower()
    if period_type in ('aylik', 'aylık'):
        return 'aylik', 1, int(data_date.month)
    if period_type in ('ceyreklik', 'çeyreklik'):
        quarter = ((data_date.month - 1) // 3) + 1
        return 'ceyrek', int(quarter), None
    if period_type in ('haftalik', 'haftalık'):
        week_no = int(data_date.isocalendar().week)
        return 'haftalik', week_no, int(data_date.month)
    if period_type in ('gunluk', 'günlük'):
        return 'gunluk', int(data_date.day), int(data_date.month)
    return 'yillik', 1, None


def create_auto_pgv_for_activity(activity: ProcessActivity) -> KpiData | None:
    """Faaliyet bağlı PG ise otomatik KpiData(actual=1) üretir."""
    if not activity or not activity.process_kpi_id or activity.auto_pgv_created:
        return None
    user_id = activity.first_assignee_id
    if not user_id:
        return None
    data_date = (activity.end_at.date() if activity.end_at else activity.end_date)
    if data_date is None:
        return None

    kpi = activity.process_kpi
    period_type, period_no, period_month = _get_activity_period_fields(kpi, data_date)
    entry = KpiData(
        process_kpi_id=int(activity.process_kpi_id),
        year=int(data_date.year),
        data_date=data_date,
        period_type=period_type,
        period_no=period_no,
        period_month=period_month,
        actual_value='1',
        description=f'Otomatik faaliyet gerçekleşmesi: {activity.name}',
        user_id=int(user_id),
    )
    db.session.add(entry)
    db.session.flush()
    db.session.add(
        KpiDataAudit(
            kpi_data_id=entry.id,
            action_type='CREATE',
            new_value='1',
            action_detail=f'Faaliyet otomatik gerçekleşme ile üretildi (activity_id={activity.id})',
            user_id=int(user_id),
        )
    )
    activity.auto_pgv_created = True
    activity.auto_pgv_kpi_data_id = entry.id
    return entry


def auto_complete_due_activities(now: datetime | None = None) -> int:
    """Bitiş zamanı gelen planlı faaliyetleri otomatik gerçekleşmişe çevirir."""
    if now is None:
        # DB'deki end_at alanı naive local datetime tutuluyor.
        # UTC ile kıyaslamak 3 saat kaymaya neden olduğu için local now kullan.
        now = datetime.now()
    due_activities = (
        ProcessActivity.query.filter(
            ProcessActivity.is_active.is_(True),
            ProcessActivity.auto_complete_enabled.is_(True),
            ProcessActivity.end_at.isnot(None),
            ProcessActivity.end_at <= now,
            ProcessActivity.status.in_(('Planlandı', 'Ertelendi')),
        )
        .all()
    )
    changed = 0
    for act in due_activities:
        act.status = 'Gerçekleşti'
        act.completed_at = now
        create_auto_pgv_for_activity(act)
        changed += 1
    if changed:
        db.session.commit()
    return changed
