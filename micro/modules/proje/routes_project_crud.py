# -*- coding: utf-8 -*-
"""Proje oluşturma, detay, düzenleme, silme, strateji."""

from __future__ import annotations

import json
from datetime import date, datetime
from types import SimpleNamespace

from flask import abort, flash, redirect, render_template, request, url_for, current_app
from flask_login import current_user, login_required
from sqlalchemy import text
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import joinedload

from platform_core import app_bp
from app.models.core import User as CoreUser
from app.models.process import Process as AppProcess
from models import Project, Surec, Task, db
from utils.task_status import normalize_task_status

from app_platform.modules.proje.display import build_user_labels_map, collect_project_user_ids, user_display
from app_platform.modules.proje.helpers import (
    form_users_payload,
    kurum_id,
    load_project,
    project_form_init,
    resolve_leader_ids_from_form,
    sync_project_leaders,
    sync_project_members_observers,
    tenant_core_users,
)
from app_platform.modules.proje.permissions import (
    can_crud_project_portfolio,
    user_can_access_project,
    user_can_edit_tasks,
    user_is_project_leader,
)
from app_platform.modules.proje.strategy_detail_service import build_strategy_detail_context
from app_platform.services.notification_triggers import (
    notify_project_leaders_added,
    notify_project_members_added,
)
from app.utils.audit_logger import AuditLogger


def _notify_new_project_team(proj: Project, kid: int, old_leader_ids: set, old_member_ids: set) -> None:
    """Lider/üye diff — yeni atananlara bildirim + e-posta (atayan hariç)."""
    actor = CoreUser.query.get(current_user.id)
    if not actor:
        return
    new_l = set(proj.leader_user_ids())
    new_m = set(proj.member_user_ids())
    notify_project_leaders_added(proj, list(new_l - old_leader_ids), actor, kid)
    notify_project_members_added(proj, list(new_m - old_member_ids), actor, kid)


def _load_project_form_surecler(kid: int):
    """Proje formu için süreç listesi (legacy `surec` yoksa modern `processes` fallback)."""
    try:
        return Surec.query.filter_by(kurum_id=kid, silindi=False).order_by(Surec.code).all()
    except ProgrammingError:
        db.session.rollback()
        rows = (
            AppProcess.query.filter_by(tenant_id=kid, is_active=True)
            .order_by(AppProcess.code)
            .all()
        )
        return [
            SimpleNamespace(id=r.id, code=r.code, ad=(r.name or r.english_name or ""))
            for r in rows
        ]


def _legacy_project_process_links_available() -> bool:
    """Legacy proje-süreç ilişki tabloları mevcut mu?"""
    try:
        row = db.session.execute(
            text(
                "SELECT to_regclass('public.surec') AS surec_tbl, "
                "to_regclass('public.project_related_processes') AS rel_tbl"
            )
        ).first()
        if not row:
            return False
        return bool(row[0] and row[1])
    except Exception:
        db.session.rollback()
        return False


def _sync_project_process_links_legacy(proj: Project, kid: int, selected_ids: list[str]) -> None:
    """Legacy `surec` / `project_related_processes` varsa proje-süreç ilişkilerini günceller."""
    if not _legacy_project_process_links_available():
        return
    proj.related_processes.clear()
    for sid in selected_ids:
        try:
            sid_int = int(sid)
        except ValueError:
            continue
        sc = Surec.query.filter_by(id=sid_int, kurum_id=kid).first()
        if sc:
            proj.related_processes.append(sc)


@app_bp.route("/project/new", methods=["GET", "POST"])
@login_required
def project_new():
    kid = kurum_id()
    if not kid:
        flash("Kurum bilgisi bulunamadı.", "danger")
        return redirect(url_for("app_bp.launcher"))
    if not can_crud_project_portfolio(current_user):
        flash("Yeni proje oluşturma yetkiniz yok.", "danger")
        return redirect(url_for("app_bp.project_list"))

    if request.method == "GET":
        surecler = _load_project_form_surecler(kid)
        kullanicilar = tenant_core_users(kid)
        sablon_projeler = (
            Project.query.filter_by(kurum_id=kid).order_by(Project.created_at.desc()).limit(20).all()
        )
        clone_from_id = request.args.get("clone_from", type=int)
        clone_src = None
        if clone_from_id:
            cand = (
                Project.query.options(joinedload(Project.related_processes))
                .filter_by(id=clone_from_id, kurum_id=kid)
                .first()
            )
            if cand and user_can_access_project(current_user, cand):
                clone_src = cand
        return render_template(
            "platform/project/form.html",
            project=None,
            clone_src=clone_src,
            surecler=surecler,
            kullanicilar=kullanicilar,
            form_users=form_users_payload(kullanicilar),
            form_init=project_form_init(clone_src) if clone_src else project_form_init(None),
            sablon_projeler=sablon_projeler,
        )

    name = (request.form.get("name") or "").strip()
    if not name:
        flash("Proje adı zorunludur.", "danger")
        return redirect(url_for("app_bp.project_new"))

    description = (request.form.get("description") or "").strip() or None
    priority = request.form.get("priority") or "Orta"
    try:
        leader_ids = resolve_leader_ids_from_form(kid, project=None)
    except ValueError as e:
        flash(str(e) or "Geçerli proje lideri seçilemedi.", "danger")
        return redirect(url_for("app_bp.project_new"))

    start_date = end_date = None
    if request.form.get("start_date"):
        try:
            start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
        except ValueError:
            pass
    if request.form.get("end_date"):
        try:
            end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()
        except ValueError:
            pass

    notification_settings = {
        "reminder_days": [7, 3, 1],
        "overdue_frequency": "daily",
        "channels": {"in_app": True, "email": request.form.get("notification_channel_email") is not None},
        "notify_manager": request.form.get("notification_notify_manager") is not None,
        "notify_observers": request.form.get("notification_notify_observers") is not None,
    }

    proj = Project(
        name=name,
        description=description,
        start_date=start_date,
        end_date=end_date,
        priority=priority,
        kurum_id=kid,
        manager_id=leader_ids[0],
    )
    try:
        proj.notification_settings = json.dumps(notification_settings, ensure_ascii=False)
    except Exception:
        pass

    db.session.add(proj)
    db.session.flush()
    try:
        sync_project_leaders(proj, kid, leader_ids)
    except ValueError as e:
        db.session.rollback()
        flash(str(e) or "Lider kaydı oluşturulamadı.", "danger")
        return redirect(url_for("app_bp.project_new"))

    _sync_project_process_links_legacy(proj, kid, request.form.getlist("surec_ids"))

    sync_project_members_observers(proj, kid)
    _notify_new_project_team(proj, kid, set(), set())
    db.session.commit()
    try:
        AuditLogger.log_create("Proje Yönetimi", proj.id, {"name": proj.name, "kurum_id": proj.kurum_id})
    except Exception as e:
        current_app.logger.error(f"Audit log hatası: {e}")
    flash("Proje oluşturuldu.", "success")
    return redirect(url_for("app_bp.project_detail", project_id=proj.id))


@app_bp.route("/project/<int:project_id>")
@login_required
def project_detail(project_id: int):
    proj = load_project(project_id)
    if not user_can_access_project(current_user, proj):
        flash("Bu projeye erişim yetkiniz yok.", "danger")
        return redirect(url_for("app_bp.project_list"))

    kid = kurum_id()
    user_labels = build_user_labels_map(collect_project_user_ids(proj), kid)

    tasks = (
        Task.query.options(joinedload(Task.assignee), joinedload(Task.reporter))
        .filter_by(project_id=project_id, is_archived=False)
        .order_by(Task.created_at.desc())
        .all()
    )

    def _nst(t):
        return normalize_task_status(t.status) or t.status

    # Görev özeti kanban sütun sırası: Tamamlandı → Devam Ediyor → Beklemede → Yapılacak
    tasks_by_status = {
        "Tamamlandı": [t for t in tasks if _nst(t) == "Tamamlandı"],
        "Devam Ediyor": [t for t in tasks if _nst(t) == "Devam Ediyor"],
        "Beklemede": [t for t in tasks if _nst(t) == "Beklemede"],
        "Yapılacak": [t for t in tasks if _nst(t) == "Yapılacak"],
    }
    today = date.today()
    geciken = [t for t in tasks if t.due_date and t.due_date < today and _nst(t) != "Tamamlandı"]

    return render_template(
        "platform/project/detail.html",
        project=proj,
        tasks=tasks,
        tasks_by_status=tasks_by_status,
        today=today,
        geciken_gorevler=geciken,
        can_edit_tasks=user_can_edit_tasks(current_user, proj),
        is_leader=user_is_project_leader(current_user, proj),
        show_strategy=can_crud_project_portfolio(current_user),
        user_labels=user_labels,
        user_display=user_display,
    )


@app_bp.route("/project/<int:project_id>/edit", methods=["GET", "POST"])
@login_required
def project_edit(project_id: int):
    proj = load_project(project_id)
    if not user_is_project_leader(current_user, proj):
        flash("Bu projeyi düzenleme yetkiniz yok.", "danger")
        return redirect(url_for("app_bp.project_detail", project_id=project_id))

    kid = kurum_id()
    if request.method == "GET":
        surecler = _load_project_form_surecler(kid)
        kullanicilar = tenant_core_users(kid)
        sablon_projeler = Project.query.filter_by(kurum_id=kid).order_by(Project.created_at.desc()).limit(20).all()
        return render_template(
            "platform/project/form.html",
            project=proj,
            clone_src=None,
            surecler=surecler,
            kullanicilar=kullanicilar,
            form_users=form_users_payload(kullanicilar),
            form_init=project_form_init(proj),
            sablon_projeler=sablon_projeler,
        )

    proj.name = (request.form.get("name") or "").strip() or proj.name
    proj.description = (request.form.get("description") or "").strip() or None
    proj.priority = request.form.get("priority") or proj.priority
    old_leader_ids = set(proj.leader_user_ids())
    old_member_ids = set(proj.member_user_ids())
    try:
        leader_ids = resolve_leader_ids_from_form(kid, project=proj)
        sync_project_leaders(proj, kid, leader_ids)
    except ValueError as e:
        flash(str(e) or "Geçerli proje lideri seçilemedi.", "danger")
        return redirect(url_for("app_bp.project_edit", project_id=project_id))

    if request.form.get("start_date"):
        try:
            proj.start_date = datetime.strptime(request.form.get("start_date"), "%Y-%m-%d").date()
        except ValueError:
            pass
    else:
        proj.start_date = None
    if request.form.get("end_date"):
        try:
            proj.end_date = datetime.strptime(request.form.get("end_date"), "%Y-%m-%d").date()
        except ValueError:
            pass
    else:
        proj.end_date = None

    notify_manager = request.form.get("notification_notify_manager") is not None
    notify_observers = request.form.get("notification_notify_observers") is not None
    channel_email = request.form.get("notification_channel_email") is not None
    try:
        settings = proj.get_notification_settings()
        settings["notify_manager"] = notify_manager
        settings["notify_observers"] = notify_observers
        if "channels" not in settings or not isinstance(settings["channels"], dict):
            settings["channels"] = {"in_app": True, "email": False}
        settings["channels"]["email"] = channel_email
        proj.notification_settings = json.dumps(settings, ensure_ascii=False)
    except Exception:
        pass

    _sync_project_process_links_legacy(proj, kid, request.form.getlist("surec_ids"))

    sync_project_members_observers(proj, kid)
    _notify_new_project_team(proj, kid, old_leader_ids, old_member_ids)
    db.session.commit()
    try:
        AuditLogger.log_update(
            "Proje Yönetimi",
            proj.id,
            {},
            {"name": proj.name, "priority": proj.priority, "start_date": str(proj.start_date), "end_date": str(proj.end_date)},
        )
    except Exception as e:
        current_app.logger.error(f"Audit log hatası: {e}")
    flash("Proje güncellendi.", "success")
    return redirect(url_for("app_bp.project_detail", project_id=proj.id))


@app_bp.route("/project/<int:project_id>/strategy")
@login_required
def project_strategy(project_id: int):
    if not can_crud_project_portfolio(current_user):
        flash("Bu sayfaya erişim yetkiniz yok.", "danger")
        return redirect(url_for("app_bp.project_detail", project_id=project_id))

    kid = kurum_id()
    proj = Project.query.filter_by(id=project_id, kurum_id=kid).first_or_404()
    ctx = build_strategy_detail_context(proj, kid)
    return render_template("platform/project/strategy_detail.html", **ctx)


@app_bp.route("/project/<int:project_id>/strategy/processes", methods=["POST"])
@login_required
def project_strategy_processes(project_id: int):
    if not can_crud_project_portfolio(current_user):
        abort(403)
    kid = kurum_id()
    proj = Project.query.filter_by(id=project_id, kurum_id=kid).first_or_404()

    sel = [int(x) for x in request.form.getlist("process_ids") if x.isdigit()]
    valid = Surec.query.filter_by(kurum_id=kid).filter(Surec.id.in_(sel)).all()
    proj.related_processes.clear()
    for p in valid:
        proj.related_processes.append(p)
    db.session.commit()
    flash("Süreç bağlantıları güncellendi.", "success")
    return redirect(url_for("app_bp.project_strategy", project_id=project_id))


@app_bp.route("/project/<int:project_id>/delete", methods=["POST"])
@login_required
def project_delete(project_id: int):
    if not can_crud_project_portfolio(current_user):
        flash("Proje silme yetkiniz yok.", "danger")
        return redirect(url_for("app_bp.project_detail", project_id=project_id))

    kid = kurum_id()
    proj = Project.query.filter_by(id=project_id, kurum_id=kid).first_or_404()
    name = proj.name
    proj.related_processes.clear()
    db.session.delete(proj)
    db.session.commit()
    flash(f'"{name}" silindi.', "success")
    return redirect(url_for("app_bp.project_list"))

