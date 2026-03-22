# -*- coding: utf-8 -*-
"""
Kök URL: /projeler/<id>/... proje analiz araçları — Micro şablonları (Tailwind / mc-*).
"""
from __future__ import annotations

from flask import flash, redirect, render_template, url_for
from flask_login import current_user, login_required

from micro import micro_bp
from micro.modules.proje.helpers import load_project
from micro.modules.proje.permissions import user_can_access_project


def _project_tool_or_redirect(project_id: int):
    proj = load_project(project_id)
    if not user_can_access_project(current_user, proj):
        flash("Bu projeye erişim yetkiniz yok.", "danger")
        return None, redirect(url_for("micro_bp.micro_project_list"))
    return proj, None


@micro_bp.route("/projeler/<int:project_id>/cpm")
@login_required
def micro_proj_root_cpm(project_id: int):
    proj, redir = _project_tool_or_redirect(project_id)
    if redir:
        return redir
    return render_template("micro/project/tools/cpm.html", project=proj)


@micro_bp.route("/projeler/<int:project_id>/sla")
@login_required
def micro_proj_root_sla(project_id: int):
    proj, redir = _project_tool_or_redirect(project_id)
    if redir:
        return redir
    return render_template("micro/project/tools/sla.html", project=proj)


@micro_bp.route("/projeler/<int:project_id>/kapasite")
@login_required
def micro_proj_root_kapasite(project_id: int):
    proj, redir = _project_tool_or_redirect(project_id)
    if redir:
        return redir
    return render_template("micro/project/tools/capacity.html", project=proj)


@micro_bp.route("/projeler/<int:project_id>/baseline")
@login_required
def micro_proj_root_baseline(project_id: int):
    proj, redir = _project_tool_or_redirect(project_id)
    if redir:
        return redir
    return render_template("micro/project/tools/baseline.html", project=proj)


@micro_bp.route("/projeler/<int:project_id>/bagimlilik-matrisi")
@login_required
def micro_proj_root_bagimlilik_matrisi(project_id: int):
    proj, redir = _project_tool_or_redirect(project_id)
    if redir:
        return redir
    return render_template("micro/project/tools/dependency_matrix.html", project=proj)


@micro_bp.route("/projeler/<int:project_id>/kurallar")
@login_required
def micro_proj_root_kurallar(project_id: int):
    proj, redir = _project_tool_or_redirect(project_id)
    if redir:
        return redir
    return render_template("micro/project/tools/rules.html", project=proj)


@micro_bp.route("/projeler/<int:project_id>/integrations")
@login_required
def micro_proj_root_integrations(project_id: int):
    proj, redir = _project_tool_or_redirect(project_id)
    if redir:
        return redir
    return render_template("micro/project/tools/integrations.html", project=proj)


@micro_bp.route("/projeler/<int:project_id>/tekrarlayan")
@login_required
def micro_proj_root_tekrarlayan(project_id: int):
    proj, redir = _project_tool_or_redirect(project_id)
    if redir:
        return redir
    return render_template("micro/project/tools/recurring.html", project=proj)


@micro_bp.route("/projeler/<int:project_id>/calisma-gunleri")
@login_required
def micro_proj_root_calisma_gunleri(project_id: int):
    proj, redir = _project_tool_or_redirect(project_id)
    if redir:
        return redir
    return render_template("micro/project/tools/workdays.html", project=proj)
