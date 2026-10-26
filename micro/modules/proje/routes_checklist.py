# -*- coding: utf-8 -*-
"""Proje kontrol listesi — kurum şablonu yönetimi ve proje içi kontrol listesi."""

from __future__ import annotations

from datetime import date

from flask import current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_babel import gettext as _
from flask_login import current_user, login_required

from platform_core import app_bp
from app.models import db
from app.models.project_checklist import ChecklistTemplate
from app.services import project_checklist_service as svc
from app.services.checklist_excel import parse_workbook
from app.services.date_sovereign import resolve_request_year
from app.utils.audit_logger import AuditLogger
from app_platform.modules.proje.helpers import kurum_id
from app_platform.modules.proje.permissions import can_crud_project_portfolio

MAX_EXCEL_BYTES = 2 * 1024 * 1024


def _json_error(exc: svc.ChecklistError):
    return jsonify({"success": False, "message": exc.message}), exc.status


def _year_arg(source) -> int:
    try:
        y = int(source.get("year"))
        if 2000 <= y <= 2100:
            return y
    except (TypeError, ValueError):
        current_app.logger.debug("[checklist] geçersiz year parametresi, oturum yılı kullanılıyor")
    return resolve_request_year()


def _template_years(tenant_id: int) -> list[int]:
    from app.models.plan_year import PlanYear
    years = {t.year for t in ChecklistTemplate.query.filter_by(tenant_id=tenant_id).all()}
    years |= {p.year for p in PlanYear.query.filter_by(tenant_id=tenant_id).all()}
    this = date.today().year
    years |= {this, this + 1}
    return sorted(years, reverse=True)


def _item_json(i) -> dict:
    return {
        "id": i.id, "stage": i.stage, "item_group": i.item_group, "text": i.text,
        "period_days": i.period_days,
        "evidence_required": bool(i.evidence_required), "sort_order": i.sort_order,
    }


def _template_payload(tenant_id: int, year: int) -> dict:
    tpl = svc.get_template(tenant_id, year)
    return {
        "success": True,
        "year": year,
        "years": _template_years(tenant_id),
        "template_id": tpl.id if tpl else None,
        "items": [_item_json(i) for i in svc.template_active_items(tpl)] if tpl else [],
    }


def _require_template_manager():
    """Şablonu yalnız kurum yöneticisi / üst yönetim düzenler."""
    if not can_crud_project_portfolio(current_user):
        return jsonify({"success": False, "message": _("Şablon yönetimi için yetkiniz yok.")}), 403
    if not kurum_id():
        return jsonify({"success": False, "message": _("Kurum bilgisi bulunamadı.")}), 400
    return None


@app_bp.route("/k-plan/project/checklist-template")
@login_required
def project_checklist_template_page():
    if not can_crud_project_portfolio(current_user):
        flash(_("Şablon yönetimi için yetkiniz yok."), "danger")
        return redirect(url_for("app_bp.project_list"))
    return render_template("platform/project/checklist_template.html", year=_year_arg(request.args))


@app_bp.route("/k-plan/project/api/checklist-template", methods=["GET"])
@login_required
def api_checklist_template_get():
    denied = _require_template_manager()
    if denied:
        return denied
    return jsonify(_template_payload(kurum_id(), _year_arg(request.args)))


@app_bp.route("/k-plan/project/api/checklist-template/item", methods=["POST"])
@login_required
def api_checklist_template_item_save():
    denied = _require_template_manager()
    if denied:
        return denied
    data = request.get_json(silent=True) or {}
    year = _year_arg(data)
    try:
        tpl = svc.get_template(kurum_id(), year, create=True)
        svc.template_save_item(tpl, data, data.get("id"))
        db.session.commit()
    except svc.ChecklistError as exc:
        db.session.rollback()
        return _json_error(exc)
    return jsonify(_template_payload(kurum_id(), year))


@app_bp.route("/k-plan/project/api/checklist-template/item/<int:item_id>/delete", methods=["POST"])
@login_required
def api_checklist_template_item_delete(item_id: int):
    denied = _require_template_manager()
    if denied:
        return denied
    data = request.get_json(silent=True) or {}
    year = _year_arg(data)
    try:
        tpl = svc.get_template(kurum_id(), year)
        if not tpl:
            raise svc.ChecklistError(_("Şablon bulunamadı."), 404)
        svc.template_delete_item(tpl, item_id)
        db.session.commit()
    except svc.ChecklistError as exc:
        db.session.rollback()
        return _json_error(exc)
    return jsonify(_template_payload(kurum_id(), year))


@app_bp.route("/k-plan/project/api/checklist-template/reorder", methods=["POST"])
@login_required
def api_checklist_template_reorder():
    denied = _require_template_manager()
    if denied:
        return denied
    data = request.get_json(silent=True) or {}
    year = _year_arg(data)
    ids = data.get("ids")
    if not isinstance(ids, list):
        return jsonify({"success": False, "message": _("Geçersiz istek.")}), 400
    tpl = svc.get_template(kurum_id(), year)
    if not tpl:
        return jsonify({"success": False, "message": _("Şablon bulunamadı.")}), 404
    svc.template_reorder(tpl, ids)
    db.session.commit()
    return jsonify(_template_payload(kurum_id(), year))


@app_bp.route("/k-plan/project/api/checklist-template/import", methods=["POST"])
@login_required
def api_checklist_template_import():
    denied = _require_template_manager()
    if denied:
        return denied
    year = _year_arg(request.form)
    replace = (request.form.get("mode") or "replace") != "append"
    f = request.files.get("file")
    if not f or not (f.filename or "").lower().endswith(".xlsx"):
        return jsonify({"success": False, "message": _("Bir .xlsx dosyası seçin.")}), 400
    data = f.read(MAX_EXCEL_BYTES + 1)
    if len(data) > MAX_EXCEL_BYTES:
        return jsonify({"success": False, "message": _("Dosya en çok 2 MB olabilir.")}), 413
    try:
        rows = parse_workbook(data)
        tpl = svc.get_template(kurum_id(), year, create=True)
        n = svc.template_import(tpl, rows, replace=replace)
        db.session.commit()
    except ValueError as exc:
        db.session.rollback()
        return jsonify({"success": False, "message": str(exc)}), 400
    except svc.ChecklistError as exc:
        db.session.rollback()
        return _json_error(exc)
    try:
        AuditLogger.log_create("Kontrol Listesi Şablonu", tpl.id, {"year": year, "imported": n, "replace": replace})
    except Exception as exc:
        current_app.logger.error(f"Audit log hatası: {exc}")
    payload = _template_payload(kurum_id(), year)
    payload["imported"] = n
    return jsonify(payload)


@app_bp.route("/k-plan/project/api/checklist-template/copy", methods=["POST"])
@login_required
def api_checklist_template_copy():
    denied = _require_template_manager()
    if denied:
        return denied
    data = request.get_json(silent=True) or {}
    try:
        from_year, to_year = int(data.get("from_year")), int(data.get("to_year"))
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": _("Geçersiz istek.")}), 400
    try:
        n = svc.template_copy_year(kurum_id(), from_year, to_year)
        db.session.commit()
    except svc.ChecklistError as exc:
        db.session.rollback()
        return _json_error(exc)
    payload = _template_payload(kurum_id(), to_year)
    payload["copied"] = n
    return jsonify(payload)


# ═══════════════════════════════════════════════════════════════════════════
# Proje içi kontrol listesi
# ═══════════════════════════════════════════════════════════════════════════
from flask import abort, send_file  # noqa: E402

from app.models.core import User as CoreUser  # noqa: E402
from app.models.portfolio_project import Project  # noqa: E402
from app.models.project_checklist import (  # noqa: E402
    ProjectChecklistEvidence,
    ProjectChecklistItem,
    STATUS_DONE,
)
from app_platform.modules.proje.permissions import user_can_access_project  # noqa: E402


def _project_or_error(project_id: int):
    """(proj, None) veya (None, (json, status)). Görüntüleme yetkisini denetler."""
    proj = db.session.get(Project, project_id)
    if proj is None or not proj.is_active:
        return None, (jsonify({"success": False, "message": _("Proje bulunamadı.")}), 404)
    if not user_can_access_project(current_user, proj):
        return None, (jsonify({"success": False, "message": _("Bu projeye erişim yetkiniz yok.")}), 403)
    return proj, None


def _fmt_dt(dt) -> str | None:
    return dt.strftime("%d.%m.%Y %H:%M") if dt else None


def _user_name(u) -> str | None:
    if not u:
        return None
    return f"{(u.first_name or '').strip()} {(u.last_name or '').strip()}".strip() or u.email


def _evidence_json(ev: ProjectChecklistEvidence, project_id: int) -> dict:
    return {
        "id": ev.id, "kind": ev.kind, "title": ev.title, "url": ev.url if ev.kind == "link" else None,
        "download_url": (url_for("app_bp.api_checklist_evidence_download", project_id=project_id, evidence_id=ev.id)
                         if ev.kind == "file" else None),
        "uploader": _user_name(ev.uploader), "created_at": _fmt_dt(ev.created_at),
    }


def _item_view(project, i: ProjectChecklistItem, manager: bool) -> dict:
    mine = svc.user_is_assigned(current_user, project, i)
    work = manager or mine
    approved_by_other = i.done_by is None or int(i.done_by) != int(current_user.id)
    return {
        "id": i.id, "stage": i.stage, "item_group": i.item_group, "text": i.text,
        "period_days": i.period_days,
        "evidence_required": bool(i.evidence_required), "status": i.status, "note": i.note,
        "assignments": svc.assignment_labels(project, i),
        "done_by": _user_name(i.done_user), "done_at": _fmt_dt(i.done_at),
        "approved_by": _user_name(i.approved_user), "approved_at": _fmt_dt(i.approved_at),
        "next_reminder_at": _fmt_dt(i.next_reminder_at),
        "evidences": [_evidence_json(e, project.id) for e in i.evidences if e.is_active],
        "mine": mine,
        "can_done": bool(work and i.status == "Bekliyor"),
        "can_approve": bool(manager and i.status == STATUS_DONE and approved_by_other),
        "can_reopen": bool(manager and i.status != "Bekliyor"),
        "can_edit_evidence": bool(work),
    }


def _process_options(project) -> list[dict]:
    """Atanabilecek süreçler: projenin yılındaki aktif süreçler (yıl süzgeci) + projeye bağlı süreçler."""
    from app.models.process import Process
    from app.services.plan_year_service import get_plan_year
    q = Process.query.filter(Process.tenant_id == project.kurum_id, Process.is_active.is_(True))
    py = get_plan_year(project.kurum_id, svc.project_year(project))
    rows = q.filter(db.or_(Process.plan_year_id == py.id, Process.plan_year_id.is_(None))).all() if py else q.all()
    seen = {p.id for p in rows}
    for p in (project.related_processes or []):
        if p and p.is_active and p.id not in seen:
            rows.append(p)
    rows.sort(key=lambda p: ((p.code or "~"), p.name or ""))
    return [{"id": p.id, "name": f"[{p.code}] {p.name}" if p.code else p.name} for p in rows]


def _checklist_payload(project) -> dict:
    manager = svc.can_manage(current_user, project)
    items = svc.active_items(project.id)
    users, processes = [], []
    if manager:
        users = [{"id": u.id, "name": _user_name(u)} for u in
                 CoreUser.query.filter_by(tenant_id=project.kurum_id, is_active=True)
                 .order_by(CoreUser.first_name, CoreUser.last_name).all()]
        processes = _process_options(project)
    completed_by = db.session.get(CoreUser, project.completed_by) if project.completed_by else None
    return {
        "success": True,
        "project": {"id": project.id, "name": project.name,
                    "completed_at": _fmt_dt(project.completed_at),
                    "completed_by": _user_name(completed_by),
                    "team_size": len(svc.project_team_ids(project))},
        "can_manage": manager,
        "progress": svc.progress(project.id),
        "completion": svc.completion_state(project.id),
        "items": [_item_view(project, i, manager) for i in items],
        "users": users,
        "processes": processes,
    }


def _mutate(project_id: int, action):
    """Ortak kalıp: yükle → eylemi uygula → commit → güncel durumu döndür."""
    proj, err = _project_or_error(project_id)
    if err:
        return err
    try:
        action(proj)
        db.session.commit()
    except svc.ChecklistError as exc:
        db.session.rollback()
        return _json_error(exc)
    except Exception as exc:
        db.session.rollback()
        current_app.logger.error(f"[checklist] {exc}", exc_info=True)
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400
    return jsonify(_checklist_payload(proj))


def _item_of(project, item_id: int):
    it = db.session.get(ProjectChecklistItem, item_id)
    if it is None or it.project_id != project.id or not it.is_active:
        raise svc.ChecklistError(_("Madde bulunamadı."), 404)
    return it


def _audit(action: str, project, **vals) -> None:
    try:
        AuditLogger.log_update("Proje Kontrol Listesi", project.id, {}, dict(vals, action=action), description=action)
    except Exception as exc:
        current_app.logger.error(f"Audit log hatası: {exc}")


@app_bp.route("/k-plan/project/<int:project_id>/views/checklist")
@login_required
def project_view_checklist(project_id: int):
    proj = Project.query.get_or_404(project_id)
    if not user_can_access_project(current_user, proj):
        flash(_("Bu projeye erişim yetkiniz yok."), "danger")
        return redirect(url_for("app_bp.project_list"))
    return render_template("platform/project/checklist.html", project=proj)


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist", methods=["GET"])
@login_required
def api_project_checklist(project_id: int):
    proj, err = _project_or_error(project_id)
    if err:
        return err
    return jsonify(_checklist_payload(proj))


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist/item/<int:item_id>/done", methods=["POST"])
@login_required
def api_checklist_item_done(project_id: int, item_id: int):
    def run(proj):
        it = _item_of(proj, item_id)
        svc.mark_done(proj, it, current_user)
        svc.notify_done(proj, it, current_user)
    return _mutate(project_id, run)


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist/item/<int:item_id>/approve", methods=["POST"])
@login_required
def api_checklist_item_approve(project_id: int, item_id: int):
    def run(proj):
        it = _item_of(proj, item_id)
        svc.approve(proj, it, current_user)
        svc.notify_approved(proj, it, current_user)
        _audit("approve", proj, item_id=it.id)
    return _mutate(project_id, run)


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist/item/<int:item_id>/reopen", methods=["POST"])
@login_required
def api_checklist_item_reopen(project_id: int, item_id: int):
    def run(proj):
        it = _item_of(proj, item_id)
        svc.reopen_item(proj, it, current_user)
        _audit("reopen_item", proj, item_id=it.id)
    return _mutate(project_id, run)


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist/item/<int:item_id>/note", methods=["POST"])
@login_required
def api_checklist_item_note(project_id: int, item_id: int):
    data = request.get_json(silent=True) or {}

    def run(proj):
        svc.set_note(proj, _item_of(proj, item_id), current_user, data.get("note"))
    return _mutate(project_id, run)


def _period_or_error(raw):
    try:
        return int(raw) if raw not in (None, "") else None
    except (TypeError, ValueError):
        raise svc.ChecklistError(_("Periyot gün sayısı geçersiz."), 400)


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist/item", methods=["POST"])
@login_required
def api_checklist_item_add(project_id: int):
    data = request.get_json(silent=True) or {}

    def run(proj):
        it = svc.add_item(proj, current_user, stage=data.get("stage"), text=data.get("text"),
                          item_group=data.get("item_group"),
                          period_days=_period_or_error(data.get("period_days")),
                          evidence_required=bool(data.get("evidence_required")))
        _audit("add_item", proj, item_id=it.id, text=it.text)
    return _mutate(project_id, run)


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist/item/<int:item_id>/update", methods=["POST"])
@login_required
def api_checklist_item_update(project_id: int, item_id: int):
    data = request.get_json(silent=True) or {}

    def run(proj):
        fields = {k: data[k] for k in ("stage", "item_group", "text", "period_days",
                                       "evidence_required") if k in data}
        if "period_days" in fields:
            fields["period_days"] = _period_or_error(fields["period_days"])
        svc.update_item(proj, _item_of(proj, item_id), current_user, **fields)
    return _mutate(project_id, run)


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist/item/<int:item_id>/delete", methods=["POST"])
@login_required
def api_checklist_item_delete(project_id: int, item_id: int):
    def run(proj):
        it = _item_of(proj, item_id)
        svc.remove_item(proj, it, current_user)
        _audit("remove_item", proj, item_id=it.id, text=it.text)
    return _mutate(project_id, run)


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist/assign", methods=["POST"])
@login_required
def api_checklist_assign(project_id: int):
    """Seçili maddelere atama: kişiler, süreç(ler) (tüm üyeleri) ve/veya proje ekibi."""
    data = request.get_json(silent=True) or {}
    item_ids = data.get("item_ids")
    targets = data.get("targets")
    if not isinstance(item_ids, list) or not isinstance(targets, list):
        return jsonify({"success": False, "message": _("Geçersiz istek.")}), 400

    def run(proj):
        newly = svc.set_assignments(proj, current_user, item_ids, targets, replace=(data.get("mode") != "add"))
        svc.notify_assigned(proj, newly, current_user)
        _audit("assign", proj, item_ids=item_ids, targets=targets)
    return _mutate(project_id, run)


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist/item/<int:item_id>/evidence", methods=["POST"])
@login_required
def api_checklist_evidence_add(project_id: int, item_id: int):
    is_json = request.is_json
    data = (request.get_json(silent=True) or {}) if is_json else request.form

    def run(proj):
        svc.add_evidence(proj, _item_of(proj, item_id), current_user, link_url=data.get("url"),
                         title=data.get("title"), file_storage=None if is_json else request.files.get("file"))
    return _mutate(project_id, run)


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist/evidence/<int:evidence_id>/delete", methods=["POST"])
@login_required
def api_checklist_evidence_delete(project_id: int, evidence_id: int):
    def run(proj):
        svc.remove_evidence(proj, db.session.get(ProjectChecklistEvidence, evidence_id), current_user)
    return _mutate(project_id, run)


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist/evidence/<int:evidence_id>/download")
@login_required
def api_checklist_evidence_download(project_id: int, evidence_id: int):
    import os
    proj = db.session.get(Project, project_id)
    ev = db.session.get(ProjectChecklistEvidence, evidence_id)
    if not proj or not ev or not ev.is_active or ev.kind != "file" or ev.item.project_id != proj.id:
        abort(404)
    if not user_can_access_project(current_user, proj):
        abort(403)
    base = os.path.join(current_app.instance_path, "checklist_evidence")
    full = os.path.abspath(os.path.join(base, ev.file_path or ""))
    if not full.startswith(os.path.abspath(base) + os.sep) or not os.path.isfile(full):
        abort(404)
    return send_file(full, as_attachment=True, download_name=ev.title)


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist/complete", methods=["POST"])
@login_required
def api_checklist_complete_project(project_id: int):
    def run(proj):
        svc.complete_project(proj, current_user)
        _audit("complete_project", proj)
    return _mutate(project_id, run)


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist/reopen-project", methods=["POST"])
@login_required
def api_checklist_reopen_project(project_id: int):
    def run(proj):
        svc.reopen_project(proj, current_user)
        _audit("reopen_project", proj)
    return _mutate(project_id, run)


# ── Dışa aktarma (Excel / PDF) ───────────────────────────────────────────────
def _export_filename(project, ext: str) -> str:
    import re
    base = re.sub(r"[^\w\-]+", "-", project.name or "proje", flags=re.UNICODE).strip("-") or "proje"
    return f"Kontrol-Listesi-{base}-{date.today().isoformat()}.{ext}"


@app_bp.route("/k-plan/project/<int:project_id>/api/checklist/export.<fmt>")
@login_required
def api_checklist_export(project_id: int, fmt: str):
    from flask import Response
    from app.services import checklist_export

    if fmt not in ("xlsx", "pdf"):
        abort(404)
    proj = db.session.get(Project, project_id)
    if proj is None or not proj.is_active:
        abort(404)
    if not user_can_access_project(current_user, proj):
        abort(403)
    items = svc.active_items(proj.id)
    prog = svc.progress(proj.id)
    if fmt == "xlsx":
        data = checklist_export.build_xlsx(proj, items, prog)
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    else:
        tenant = getattr(current_user, "tenant", None)
        data = checklist_export.build_pdf(proj, items, prog, tenant_name=getattr(tenant, "name", None))
        mime = "application/pdf"
    resp = Response(data, mimetype=mime)
    from urllib.parse import quote
    resp.headers["Content-Disposition"] = f"attachment; filename*=UTF-8''{quote(_export_filename(proj, fmt))}"
    resp.headers["Cache-Control"] = "private, no-store"
    return resp
