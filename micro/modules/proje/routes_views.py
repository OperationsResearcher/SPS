# -*- coding: utf-8 -*-
"""Takvim, Gantt, RAID, Kanban görünümleri."""

from __future__ import annotations

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from platform_core import app_bp
from app.models.portfolio_project import Project, Task
from app_platform.modules.proje.helpers import kanban_task_buckets
from app_platform.modules.proje.permissions import user_can_access_project
from flask_babel import gettext as _


@app_bp.route("/project/<int:project_id>/views/calendar")
@login_required
def project_view_calendar(project_id: int):
    proj = Project.query.get_or_404(project_id)
    if not user_can_access_project(current_user, proj):
        flash(_("Bu projeye erişim yetkiniz yok."), "danger")
        return redirect(url_for("app_bp.project_list"))
    return render_template("platform/project/calendar.html", project=proj)


@app_bp.route("/project/<int:project_id>/views/gantt")
@login_required
def project_view_gantt(project_id: int):
    proj = Project.query.get_or_404(project_id)
    if not user_can_access_project(current_user, proj):
        flash(_("Bu projeye erişim yetkiniz yok."), "danger")
        return redirect(url_for("app_bp.project_list"))
    tasks = Task.query.filter_by(project_id=project_id).all()
    return render_template("platform/project/gantt.html", project=proj, tasks=tasks)


@app_bp.route("/project/<int:project_id>/views/raid")
@login_required
def project_view_raid(project_id: int):
    proj = Project.query.get_or_404(project_id)
    if not user_can_access_project(current_user, proj):
        flash(_("Bu projeye erişim yetkiniz yok."), "danger")
        return redirect(url_for("app_bp.project_list"))
    return render_template("platform/project/raid.html", project=proj)


@app_bp.route("/project/<int:project_id>/views/kapasite")
@login_required
def project_view_kapasite(project_id: int):
    """Kapasite planlama — proje ekibine haftalık saat ayır (L3 eksik tamamlama).

    API (/api/projeler/<id>/kapasite) vardı, UI yoktu.
    """
    proj = Project.query.get_or_404(project_id)
    if not user_can_access_project(current_user, proj):
        flash(_("Bu projeye erişim yetkiniz yok."), "danger")
        return redirect(url_for("app_bp.project_list"))
    # Kapasite atanabilecek ekip: lider + üye (tekilleştir)
    ekip = {}
    for u in list(proj.leaders or []) + list(proj.members or []):
        if u and u.id not in ekip:
            ad = ((u.first_name or "") + " " + (u.last_name or "")).strip() or u.email
            ekip[u.id] = {"id": u.id, "name": ad}
    return render_template(
        "platform/project/kapasite.html",
        project=proj, ekip=list(ekip.values()),
    )


@app_bp.route("/project/<int:project_id>/views/kanban")
@login_required
def project_view_kanban(project_id: int):
    proj = Project.query.get_or_404(project_id)
    if not user_can_access_project(current_user, proj):
        flash(_("Bu projeye erişim yetkiniz yok."), "danger")
        return redirect(url_for("app_bp.project_list"))
    tasks = Task.query.filter_by(project_id=project_id).all()
    tasks_todo, tasks_inprogress, tasks_done = kanban_task_buckets(tasks)
    return render_template(
        "platform/project/kanban.html",
        project=proj,
        tasks_todo=tasks_todo,
        tasks_inprogress=tasks_inprogress,
        tasks_done=tasks_done,
    )

