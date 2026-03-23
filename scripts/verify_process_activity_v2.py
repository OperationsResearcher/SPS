"""Süreç Faaliyetleri V2 backend doğrulama scripti.

Çalıştırma:
  python scripts/verify_process_activity_v2.py
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app import create_app
from app.models import db
from app.models.core import Notification, User
from app.models.process import (
    KpiData,
    Process,
    ProcessActivity,
    ProcessActivityAssignee,
    ProcessActivityReminder,
    ProcessKpi,
)
from services.process_activity_scheduler import (
    check_activity_auto_completion,
    check_activity_reminders,
)


def _full_name(user: User) -> str:
    return f"{(user.first_name or '').strip()} {(user.last_name or '').strip()}".strip() or user.email


def main() -> int:
    app = create_app()
    token = f"V2-TEST-{int(datetime.utcnow().timestamp())}"

    with app.app_context():
        salih = User.query.filter_by(email="salih@kayserimodelfabrika.com", is_active=True).first()
        if not salih:
            salih = (
                User.query.filter_by(is_active=True)
                .filter(User.tenant_id.isnot(None))
                .order_by(User.id.asc())
                .first()
            )
        if not salih:
            print("FAIL: aktif tenant kullanıcısı bulunamadı.")
            return 1

        process = (
            Process.query.filter_by(tenant_id=salih.tenant_id, is_active=True)
            .order_by(Process.id.asc())
            .first()
        )
        if not process:
            print("FAIL: tenant için süreç bulunamadı.")
            return 1

        candidates = [u for u in (process.leaders + process.members + process.owners) if u and u.is_active]
        seen = set()
        assignees = []
        for u in candidates:
            if u.id not in seen:
                seen.add(u.id)
                assignees.append(u)
        if salih.id not in seen:
            assignees.insert(0, salih)
        if not assignees:
            assignees = [salih]

        start_at = datetime.utcnow() + timedelta(minutes=2)
        end_at = datetime.utcnow() + timedelta(minutes=3)

        kpi = (
            ProcessKpi.query.filter_by(process_id=process.id, is_active=True)
            .order_by(ProcessKpi.id.asc())
            .first()
        )
        created_kpi = None
        if not kpi:
            created_kpi = ProcessKpi(
                process_id=process.id,
                name=f"{token} KPI",
                code=f"{token[:10]}-KPI",
                period="Aylık",
                direction="Increasing",
                is_active=True,
            )
            db.session.add(created_kpi)
            db.session.flush()
            kpi = created_kpi

        activity = ProcessActivity(
            process_id=process.id,
            process_kpi_id=kpi.id if kpi else None,
            name=f"{token} Faaliyet",
            description="V2 test activity",
            status="Planlandı",
            progress=0,
            start_at=start_at,
            end_at=end_at,
            start_date=start_at.date(),
            end_date=end_at.date(),
            notify_email=False,
            auto_complete_enabled=True,
            is_active=True,
        )
        db.session.add(activity)
        db.session.flush()

        for idx, u in enumerate(assignees, start=1):
            db.session.add(
                ProcessActivityAssignee(
                    activity_id=activity.id,
                    user_id=u.id,
                    order_no=idx,
                    assigned_by=salih.id,
                    assigned_at=datetime.utcnow(),
                )
            )

        reminder = ProcessActivityReminder(
            activity_id=activity.id,
            minutes_before=1,
            remind_at=datetime.utcnow() - timedelta(seconds=10),
            channel_email=False,
        )
        db.session.add(reminder)
        db.session.commit()

        # 1) Reminder test
        check_activity_reminders(app)
        db.session.refresh(reminder)
        if reminder.sent_at is None:
            print("FAIL: reminder sent_at boş kaldı.")
            return 1

        rem_notifs = Notification.query.filter(
            Notification.notification_type == "activity_reminder",
            Notification.title.like(f"%{process.name}%"),
            Notification.message.like(f"%{token}%"),
        ).count()
        if rem_notifs < 1:
            print("FAIL: activity_reminder bildirimi oluşmadı.")
            return 1

        # 2) Auto-complete + auto PGV test
        activity.end_at = datetime.utcnow() - timedelta(minutes=1)
        activity.end_date = activity.end_at.date()
        activity.status = "Planlandı"
        db.session.commit()

        check_activity_auto_completion(app)
        db.session.refresh(activity)
        if activity.status != "Gerçekleşti":
            print(f"FAIL: activity status beklenen 'Gerçekleşti', gelen: {activity.status}")
            return 1
        if not activity.completed_at:
            print("FAIL: completed_at set edilmedi.")
            return 1
        if not activity.auto_pgv_created:
            print("FAIL: auto_pgv_created False kaldı.")
            return 1
        if not activity.auto_pgv_kpi_data_id:
            print("FAIL: auto_pgv_kpi_data_id boş.")
            return 1

        pgv = KpiData.query.get(activity.auto_pgv_kpi_data_id)
        if not pgv:
            print("FAIL: oluşturulan KpiData bulunamadı.")
            return 1
        if str(pgv.actual_value) != "1":
            print(f"FAIL: KpiData.actual_value beklenen '1', gelen: {pgv.actual_value!r}")
            return 1
        if pgv.data_date != activity.end_at.date():
            print(f"FAIL: KpiData.data_date beklenen {activity.end_at.date()}, gelen {pgv.data_date}")
            return 1
        if pgv.user_id != activity.first_assignee_id:
            print(f"FAIL: KpiData.user_id beklenen {activity.first_assignee_id}, gelen {pgv.user_id}")
            return 1

        # 3) Cleanup
        Notification.query.filter(
            Notification.message.like(f"%{token}%")
        ).delete(synchronize_session=False)
        ProcessActivity.query.filter_by(id=activity.id).delete(synchronize_session=False)
        if created_kpi is not None:
            ProcessKpi.query.filter_by(id=created_kpi.id).delete(synchronize_session=False)
        db.session.commit()

    print("OK: Süreç Faaliyetleri V2 backend doğrulaması başarılı.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
