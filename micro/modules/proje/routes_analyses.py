# -*- coding: utf-8 -*-
"""Proje analizleri / araçlar hub sayfası (eski Proje Araçları benzeri)."""

from __future__ import annotations

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from micro import micro_bp
from models import Task
from micro.modules.proje.helpers import load_project
from micro.modules.proje.permissions import user_can_access_project
from utils.task_status import normalize_task_status


def _project_progress_percent(project_id: int) -> int:
    tasks = (
        Task.query.filter_by(project_id=project_id, is_archived=False)
        .with_entities(Task.status)
        .all()
    )
    if not tasks:
        return 0
    done = 0
    for (st,) in tasks:
        n = normalize_task_status(st) or (st or "")
        if n == "Tamamlandı":
            done += 1
    return int(round(100 * done / len(tasks)))


@micro_bp.route("/project/<int:project_id>/analizler")
@login_required
def micro_project_analyses(project_id: int):
    proj = load_project(project_id)
    if not user_can_access_project(current_user, proj):
        flash("Bu projeye erişim yetkiniz yok.", "danger")
        return redirect(url_for("micro_bp.micro_project_list"))

    progress_pct = _project_progress_percent(project_id)

    return render_template(
        "micro/project/analyses.html",
        project=proj,
        progress_pct=progress_pct,
    )
