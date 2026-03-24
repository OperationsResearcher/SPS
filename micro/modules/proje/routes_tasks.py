# -*- coding: utf-8 -*-
"""Proje görevleri CRUD."""

from __future__ import annotations

from datetime import datetime

from flask import flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.models.process import ProcessKpi
from app.models.core import User as CoreUser
from micro import micro_bp
from models import Task, db
from micro.modules.proje.helpers import kurum_id, load_project, tenant_core_users, kpis_for_tenant
from micro.modules.proje.permissions import (
    can_crud_project_portfolio,
    user_can_access_project,
    user_can_edit_tasks,
    user_can_manage_task,
)
from micro.services.notification_triggers import (
    notify_project_task_status_change,
    notify_task_assignment,
)


@micro_bp.route("/project/<int:project_id>/task/new", methods=["GET", "POST"])
@login_required
def micro_project_task_new(project_id: int):
    proj = load_project(project_id)
    if not user_can_edit_tasks(current_user, proj):
        flash("Görev ekleyemezsiniz.", "danger")
        return redirect(url_for("micro_bp.micro_project_detail", project_id=project_id))

    kpis = kpis_for_tenant()

    if request.method == "GET":
        return render_template(
            "micro/project/task_form.html",
            project=proj,
            task=None,
            kpis=kpis,
            users=tenant_core_users(kurum_id()),
        )

    title = (request.form.get("title") or "").strip()
    if not title:
        flash("Görev başlığı zorunludur.", "danger")
        return redirect(url_for("micro_bp.micro_project_task_new", project_id=project_id))

    pk_raw = request.form.get("process_kpi_id")
    process_kpi_id = int(pk_raw) if pk_raw and pk_raw.isdigit() else None
    if process_kpi_id:
        kpi = ProcessKpi.query.get(process_kpi_id)
        if not kpi or kpi.process.tenant_id != current_user.tenant_id:
            process_kpi_id = None

    assignee_id = request.form.get("assignee_id", type=int) or None
    if assignee_id:
        assignee_user = CoreUser.query.get(assignee_id)
        if not assignee_user or assignee_user.tenant_id != current_user.tenant_id:
            flash("Geçersiz görev ataması.", "danger")
            return redirect(url_for("micro_bp.micro_project_task_new", project_id=project_id))

    due = None
    if request.form.get("due_date"):
        try:
            due = datetime.strptime(request.form.get("due_date"), "%Y-%m-%d").date()
        except ValueError:
            pass

    task = Task(
        project_id=project_id,
        title=title,
        description=(request.form.get("description") or "").strip() or None,
        status=request.form.get("status") or "Yapılacak",
        priority=request.form.get("priority") or "Medium",
        assignee_id=assignee_id,
        reporter_id=current_user.id,
        due_date=due,
        process_kpi_id=process_kpi_id,
    )
    db.session.add(task)
    db.session.flush()
    if assignee_id:
        assignee_user = CoreUser.query.get(assignee_id)
        if assignee_user and assignee_user.tenant_id == current_user.tenant_id:
            actor = CoreUser.query.get(current_user.id)
            notify_task_assignment(
                task.title,
                assignee_user,
                proj.kurum_id,
                actor=actor,
                task_link=f"/project/{project_id}/task/{task.id}",
                project=proj,
            )
    db.session.commit()
    flash("Görev eklendi.", "success")
    return redirect(url_for("micro_bp.micro_project_detail", project_id=project_id))


@micro_bp.route("/project/api/task/quick-add", methods=["POST"])
@login_required
def micro_project_task_quick_add():
    """Takvim vb. için JSON ile hızlı proje görevi oluşturma."""
    data = request.get_json() or {}
    try:
        project_id = int(data.get("project_id"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Geçersiz proje."}), 400

    proj = load_project(project_id)
    if not user_can_edit_tasks(current_user, proj):
        return jsonify({"success": False, "message": "Bu projede görev oluşturma yetkiniz yok."}), 403

    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"success": False, "message": "Görev başlığı zorunludur."}), 400

    start_d = None
    due_d = None
    raw_start = data.get("start_date")
    raw_due = data.get("due_date")
    if raw_start:
        try:
            start_d = datetime.strptime(str(raw_start)[:10], "%Y-%m-%d").date()
        except ValueError:
            pass
    if raw_due:
        try:
            due_d = datetime.strptime(str(raw_due)[:10], "%Y-%m-%d").date()
        except ValueError:
            pass
    if start_d is None and due_d is not None:
        start_d = due_d
    if due_d is None and start_d is not None:
        due_d = start_d

    process_kpi_id = None
    pk_raw = data.get("process_kpi_id")
    if pk_raw is not None and str(pk_raw).strip() != "":
        try:
            pk_int = int(pk_raw)
            kpi = ProcessKpi.query.get(pk_int)
            if kpi and kpi.process.tenant_id == current_user.tenant_id:
                process_kpi_id = pk_int
        except (TypeError, ValueError):
            pass

    aid = int(current_user.id)
    raw_aid = data.get("assignee_id")
    if raw_aid is not None and str(raw_aid).strip() != "":
        try:
            tmp = int(raw_aid)
            assignee_user = CoreUser.query.get(tmp)
            if assignee_user and assignee_user.tenant_id == current_user.tenant_id:
                aid = tmp
        except (TypeError, ValueError):
            pass

    task = Task(
        project_id=project_id,
        title=title,
        description=(data.get("description") or "").strip() or None,
        status=data.get("status") or "Yapılacak",
        priority=data.get("priority") or "Medium",
        assignee_id=aid,
        reporter_id=current_user.id,
        due_date=due_d,
        start_date=start_d,
        process_kpi_id=process_kpi_id,
    )
    db.session.add(task)
    db.session.flush()
    if aid and int(aid) != int(current_user.id):
        assignee_user = CoreUser.query.get(aid)
        if assignee_user and assignee_user.tenant_id == current_user.tenant_id:
            actor = CoreUser.query.get(current_user.id)
            notify_task_assignment(
                task.title,
                assignee_user,
                proj.kurum_id,
                actor=actor,
                task_link=f"/project/{project_id}/task/{task.id}",
                project=proj,
            )
    db.session.commit()
    return jsonify(
        {
            "success": True,
            "message": "Görev eklendi.",
            "id": task.id,
            "url": url_for("micro_bp.micro_project_task_detail", project_id=project_id, task_id=task.id),
        }
    )


@micro_bp.route("/project/<int:project_id>/task/<int:task_id>")
@login_required
def micro_project_task_detail(project_id: int, task_id: int):
    proj = load_project(project_id)
    if not user_can_access_project(current_user, proj):
        flash("Erişim yok.", "danger")
        return redirect(url_for("micro_bp.micro_project_list"))

    task = Task.query.filter_by(id=task_id, project_id=project_id).first_or_404()
    kpi = None
    if task.process_kpi_id:
        kpi = ProcessKpi.query.get(task.process_kpi_id)

    return render_template(
        "micro/project/task_detail.html",
        project=proj,
        task=task,
        linked_kpi=kpi,
        can_edit=user_can_manage_task(current_user, proj, task),
    )


@micro_bp.route("/project/<int:project_id>/task/<int:task_id>/edit", methods=["GET", "POST"])
@login_required
def micro_project_task_edit(project_id: int, task_id: int):
    proj = load_project(project_id)
    task = Task.query.filter_by(id=task_id, project_id=project_id).first_or_404()
    if not user_can_manage_task(current_user, proj, task):
        flash("Düzenleyemezsiniz.", "danger")
        return redirect(url_for("micro_bp.micro_project_task_detail", project_id=project_id, task_id=task_id))
    kpis = kpis_for_tenant()

    if request.method == "GET":
        return render_template(
            "micro/project/task_form.html",
            project=proj,
            task=task,
            kpis=kpis,
            users=tenant_core_users(kurum_id()),
        )

    old_assignee_id = task.assignee_id
    old_status = (task.status or "").strip()

    task.title = (request.form.get("title") or "").strip() or task.title
    task.description = (request.form.get("description") or "").strip() or None
    task.status = request.form.get("status") or task.status
    task.priority = request.form.get("priority") or task.priority
    next_assignee_id = request.form.get("assignee_id", type=int) or None
    if next_assignee_id:
        assignee_user = CoreUser.query.get(next_assignee_id)
        if not assignee_user or assignee_user.tenant_id != current_user.tenant_id:
            flash("Geçersiz görev ataması.", "danger")
            return redirect(url_for("micro_bp.micro_project_task_edit", project_id=project_id, task_id=task_id))
    task.assignee_id = next_assignee_id

    pk_raw = request.form.get("process_kpi_id")
    if pk_raw == "" or pk_raw is None:
        task.process_kpi_id = None
    elif pk_raw.isdigit():
        kpi = ProcessKpi.query.get(int(pk_raw))
        if kpi and kpi.process.tenant_id == current_user.tenant_id:
            task.process_kpi_id = int(pk_raw)
        else:
            task.process_kpi_id = None

    if request.form.get("due_date"):
        try:
            task.due_date = datetime.strptime(request.form.get("due_date"), "%Y-%m-%d").date()
        except ValueError:
            pass
    else:
        task.due_date = None

    new_status = (task.status or "").strip()
    db.session.flush()

    if task.assignee_id and task.assignee_id != old_assignee_id:
        assignee_user = CoreUser.query.get(task.assignee_id)
        if assignee_user and assignee_user.tenant_id == current_user.tenant_id:
            actor = CoreUser.query.get(current_user.id)
            notify_task_assignment(
                task.title,
                assignee_user,
                proj.kurum_id,
                actor=actor,
                task_link=f"/project/{project_id}/task/{task.id}",
                project=proj,
            )

    if new_status != old_status:
        actor = CoreUser.query.get(current_user.id)
        if actor:
            notify_project_task_status_change(proj, task, old_status, new_status, actor)

    db.session.commit()
    flash("Görev güncellendi.", "success")
    return redirect(url_for("micro_bp.micro_project_task_detail", project_id=project_id, task_id=task_id))


@micro_bp.route("/project/<int:project_id>/task/<int:task_id>/delete", methods=["POST"])
@login_required
def micro_project_task_delete(project_id: int, task_id: int):
    proj = load_project(project_id)
    if not can_crud_project_portfolio(current_user):
        flash("Görev silme yetkiniz yok.", "danger")
        return redirect(url_for("micro_bp.micro_project_task_detail", project_id=project_id, task_id=task_id))
    task = Task.query.filter_by(id=task_id, project_id=project_id).first_or_404()
    task.is_archived = True
    db.session.commit()
    flash("Görev silindi.", "success")
    return redirect(url_for("micro_bp.micro_project_detail", project_id=project_id))
