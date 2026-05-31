"""'Benim Görevlerim' birleşik widget endpoint'i — proje görevleri + bireysel faaliyetler + süreç aktiviteleri."""
from datetime import date
from flask import jsonify, current_app
from flask_login import login_required, current_user
from sqlalchemy import or_

from platform_core import app_bp
from extensions import db
from app.models.portfolio_project import Task, Project
from app.models.process import IndividualActivity, ProcessActivity, ProcessActivityAssignee


_OPEN_TASK_STATUSES = ("Yapılacak", "Devam Ediyor", "Beklemede")
_OPEN_ACT_STATUSES = ("Planlandı", "Devam Ediyor", "Beklemede")
_DONE_STATUSES = ("Tamamlandı", "Done", "Closed")


def _days_until(end_date):
    if not end_date:
        return None
    return (end_date - date.today()).days


@app_bp.route("/api/my-tasks")
@login_required
def api_my_tasks():
    """Kullanıcıya atanmış aktif görevleri tek listede döner — son tarihe göre sıralı."""
    uid = current_user.id
    tid = current_user.tenant_id
    items = []
    try:
        # 1) Proje görevleri (Task.assignee_id)
        tasks = (
            Task.query.join(Project, Task.project_id == Project.id)
            .filter(
                Task.assignee_id == uid,
                Task.is_archived.is_(False),
                Project.tenant_id == tid,
                Project.is_active.is_(True),
                ~Task.status.in_(_DONE_STATUSES),
            ).order_by(Task.due_date.asc().nullslast()).limit(50).all()
        )
        for t in tasks:
            items.append({
                "kind": "project_task",
                "kind_label": "Proje Görevi",
                "icon": "fa-clipboard-check",
                "id": t.id,
                "title": t.name or "(başlıksız)",
                "subtitle": (t.project.name if getattr(t, "project", None) else ""),
                "status": t.status or "—",
                "due_date": t.due_date.isoformat() if t.due_date else None,
                "days_until": _days_until(t.due_date),
                "url": f"/project/task/{t.id}",
            })

        # 2) Bireysel faaliyetler (IndividualActivity.user_id)
        ia = (
            IndividualActivity.query.filter(
                IndividualActivity.user_id == uid,
                IndividualActivity.is_active.is_(True),
                ~IndividualActivity.status.in_(_DONE_STATUSES),
            ).order_by(IndividualActivity.end_date.asc().nullslast()).limit(50).all()
        )
        for a in ia:
            items.append({
                "kind": "individual_activity",
                "kind_label": "Bireysel Faaliyet",
                "icon": "fa-user-check",
                "id": a.id,
                "title": a.name or "(başlıksız)",
                "subtitle": a.description[:60] if a.description else (a.source or "Bireysel"),
                "status": a.status or "—",
                "due_date": a.end_date.isoformat() if a.end_date else None,
                "days_until": _days_until(a.end_date),
                "url": "/bireysel/karne",
            })

        # 3) Süreç faaliyetleri (ProcessActivityAssignee aracılığıyla)
        try:
            assigned_act_ids = [
                r.activity_id for r in
                ProcessActivityAssignee.query.filter_by(user_id=uid).limit(200).all()
            ]
            if assigned_act_ids:
                pas = (
                    ProcessActivity.query.filter(
                        ProcessActivity.id.in_(assigned_act_ids),
                        ProcessActivity.is_active.is_(True),
                        ~ProcessActivity.status.in_(_DONE_STATUSES),
                    ).order_by(ProcessActivity.end_date.asc().nullslast()).limit(50).all()
                )
                for pa in pas:
                    items.append({
                        "kind": "process_activity",
                        "kind_label": "Süreç Faaliyeti",
                        "icon": "fa-sitemap",
                        "id": pa.id,
                        "title": pa.name or "(başlıksız)",
                        "subtitle": pa.process.name if getattr(pa, "process", None) else "",
                        "status": pa.status or "—",
                        "due_date": pa.end_date.isoformat() if pa.end_date else None,
                        "days_until": _days_until(pa.end_date),
                        "url": (f"/process/{pa.process_id}/karne?tab=activities" if pa.process_id else "/process"),
                    })
        except Exception as _e:
            current_app.logger.warning(f"[my-tasks] süreç faaliyeti atlandı: {_e}")

    except Exception as e:
        current_app.logger.error(f"[api_my_tasks] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Görevler alınamadı."}), 500

    # Bitiş tarihine göre sırala (None'lar sona)
    items.sort(key=lambda x: (x["due_date"] is None, x["due_date"] or "9999-12-31"))

    # Özet
    overdue = sum(1 for it in items if it["days_until"] is not None and it["days_until"] < 0)
    today_cnt = sum(1 for it in items if it["days_until"] == 0)
    week_cnt = sum(1 for it in items if it["days_until"] is not None and 0 <= it["days_until"] <= 7)

    return jsonify({"success": True, "data": {
        "items": items,
        "total": len(items),
        "overdue": overdue,
        "due_today": today_cnt,
        "due_this_week": week_cnt,
    }})
