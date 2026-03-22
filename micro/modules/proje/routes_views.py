# -*- coding: utf-8 -*-
"""Takvim, Gantt, RAID, Kanban görünümleri."""

from __future__ import annotations

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from micro import micro_bp
from models import Project, Task
from micro.modules.proje.helpers import kanban_task_buckets
from micro.modules.proje.permissions import user_can_access_project


@micro_bp.route("/project/<int:project_id>/views/calendar")
@login_required
def micro_project_view_calendar(project_id: int):
    proj = Project.query.get_or_404(project_id)
    if not user_can_access_project(current_user, proj):
        flash("Bu projeye erişim yetkiniz yok.", "danger")
        return redirect(url_for("micro_bp.micro_project_list"))
    return render_template("micro/project/calendar.html", project=proj)


@micro_bp.route("/project/<int:project_id>/views/gantt")
@login_required
def micro_project_view_gantt(project_id: int):
    proj = Project.query.get_or_404(project_id)
    if not user_can_access_project(current_user, proj):
        flash("Bu projeye erişim yetkiniz yok.", "danger")
        return redirect(url_for("micro_bp.micro_project_list"))
    tasks = Task.query.filter_by(project_id=project_id).all()
    return render_template("micro/project/gantt.html", project=proj, tasks=tasks)


@micro_bp.route("/project/<int:project_id>/views/raid")
@login_required
def micro_project_view_raid(project_id: int):
    proj = Project.query.get_or_404(project_id)
    if not user_can_access_project(current_user, proj):
        flash("Bu projeye erişim yetkiniz yok.", "danger")
        return redirect(url_for("micro_bp.micro_project_list"))
    return render_template("micro/project/raid.html", project=proj)


@micro_bp.route("/project/<int:project_id>/views/kanban")
@login_required
def micro_project_view_kanban(project_id: int):
    proj = Project.query.get_or_404(project_id)
    if not user_can_access_project(current_user, proj):
        flash("Bu projeye erişim yetkiniz yok.", "danger")
        return redirect(url_for("micro_bp.micro_project_list"))
    tasks = Task.query.filter_by(project_id=project_id).all()
    tasks_todo, tasks_inprogress, tasks_done = kanban_task_buckets(tasks)
    return render_template(
        "micro/project/kanban.html",
        project=proj,
        tasks_todo=tasks_todo,
        tasks_inprogress=tasks_inprogress,
        tasks_done=tasks_done,
    )
