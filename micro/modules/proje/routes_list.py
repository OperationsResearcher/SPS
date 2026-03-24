# -*- coding: utf-8 -*-
"""Proje listesi ve stratejik portföy."""

from __future__ import annotations

import csv
import io
import json
from datetime import date
from types import SimpleNamespace

from flask import Response, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from sqlalchemy import func
from sqlalchemy.exc import ProgrammingError

from micro import micro_bp
from models import Project, Surec, Task, db
from app.models.process import Process as AppProcess
from micro.modules.proje.display import build_user_labels_map, collect_projects_user_ids, user_display
from micro.modules.proje.helpers import kurum_id, tenant_core_users
from micro.modules.proje.permissions import (
    accessible_projects_query,
    can_crud_project_portfolio,
    is_privileged,
)
from micro.modules.proje.portfolio_service import build_portfolio_context
from micro.modules.proje.project_list_query import (
    ProjectListFilters,
    build_filtered_projects_query,
    parse_project_list_filters,
)
from micro.modules.proje.project_overview_service import build_project_list_overview, overview_for_export_summary

_COMPLETED = ("Tamamlandı", "Done", "Completed")


def _load_filter_surecler(kid: int):
    """Proje filtreleri için süreç listesi (legacy `surec` yoksa modern `processes` fallback)."""
    try:
        return Surec.query.filter_by(kurum_id=kid, silindi=False).order_by(Surec.code).all()
    except ProgrammingError:
        # Yerel PostgreSQL'de legacy `surec` tablosu bulunmayabilir.
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


@micro_bp.route("/proje")
@login_required
def proje_legacy_redirect():
    return redirect(url_for("micro_bp.micro_project_list"))


@micro_bp.route("/project")
@login_required
def micro_project_list():
    kid = kurum_id()
    if not kid:
        flash("Kurum bilgisi bulunamadı.", "danger")
        return redirect(url_for("micro_bp.launcher"))

    privileged = is_privileged(current_user)
    flt = parse_project_list_filters(request, privileged)
    page = request.args.get("page", 1, type=int)
    per_page = 20

    q = build_filtered_projects_query(current_user, kid, flt)
    pagination = q.paginate(page=page, per_page=per_page, error_out=False)

    uids = collect_projects_user_ids(pagination.items)
    user_labels = build_user_labels_map(uids, kid)
    overview = build_project_list_overview(current_user, kid, flt)
    show_portfolio = can_crud_project_portfolio(current_user)

    surecler = _load_filter_surecler(kid)
    filter_leaders = tenant_core_users(kid)

    def _page_url(pnum: int) -> str:
        args = flt.query_args()
        if pnum > 1:
            args["page"] = pnum
        return url_for("micro_bp.micro_project_list", **args)

    return render_template(
        "micro/project/list.html",
        projects=pagination.items,
        pagination=pagination,
        user_labels=user_labels,
        user_display=user_display,
        filters=flt,
        filter_args=flt.query_args(),
        list_url_prev=_page_url(pagination.prev_num) if pagination.has_prev else None,
        list_url_next=_page_url(pagination.next_num) if pagination.has_next else None,
        export_url=url_for("micro_bp.micro_project_export_csv", **flt.query_args()),
        ics_url=url_for("micro_bp.micro_project_deadlines_ics", **flt.query_args()),
        overview=overview,
        show_portfolio=show_portfolio,
        privileged=privileged,
        surecler=surecler,
        filter_leaders=filter_leaders,
        bulk_allowed=privileged,
    )


@micro_bp.route("/project/export.csv")
@login_required
def micro_project_export_csv():
    kid = kurum_id()
    if not kid:
        flash("Kurum bilgisi bulunamadı.", "danger")
        return redirect(url_for("micro_bp.launcher"))

    privileged = is_privileged(current_user)
    flt = parse_project_list_filters(request, privileged)
    q = build_filtered_projects_query(current_user, kid, flt)
    projects = q.all()
    pids = [p.id for p in projects]

    overdue_by_pid: dict[int, int] = {}
    if pids:
        today = date.today()
        rows = (
            db.session.query(Task.project_id, func.count(Task.id))
            .filter(
                Task.project_id.in_(pids),
                Task.is_archived.is_(False),
                Task.due_date.isnot(None),
                Task.due_date < today,
                Task.status.notin_(_COMPLETED),
            )
            .group_by(Task.project_id)
            .all()
        )
        overdue_by_pid = {int(r[0]): int(r[1]) for r in rows}

    summary = overview_for_export_summary(current_user, kid, flt)
    buf = io.StringIO()
    w = csv.writer(buf, delimiter=";", lineterminator="\n")
    w.writerow(["Kokpitim — Proje listesi dışa aktarım"])
    w.writerow(
        [
            "Özet: projeler",
            summary["total_projects"],
            "görevler",
            summary["total_tasks"],
            "geciken_görev",
            summary["overdue_tasks"],
            "plan_gecen_proje",
            summary["overdue_projects"],
            "acik_raid",
            summary["raid_open_total"],
            "ort_saglik",
            summary["avg_health_score"] if summary["avg_health_score"] is not None else "",
        ]
    )
    w.writerow([])
    w.writerow(
        [
            "id",
            "ad",
            "oncelik",
            "baslangic",
            "bitis",
            "saglik",
            "geciken_gorev_sayisi",
            "guncelleme",
        ]
    )
    for p in projects:
        w.writerow(
            [
                p.id,
                p.name or "",
                p.priority or "",
                p.start_date.isoformat() if p.start_date else "",
                p.end_date.isoformat() if p.end_date else "",
                p.health_score if p.health_score is not None else "",
                overdue_by_pid.get(p.id, 0),
                p.updated_at.isoformat() if p.updated_at else "",
            ]
        )

    data = "\ufeff" + buf.getvalue()
    return Response(
        data.encode("utf-8"),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": 'attachment; filename="kokpitim_projeler.csv"',
        },
    )


@micro_bp.route("/project/deadlines.ics")
@login_required
def micro_project_deadlines_ics():
    kid = kurum_id()
    if not kid:
        return Response("Forbidden", status=403)

    privileged = is_privileged(current_user)
    flt = parse_project_list_filters(request, privileged)
    q = build_filtered_projects_query(current_user, kid, flt)
    projects = q.limit(400).all()

    def esc(s: str) -> str:
        return (
            (s or "")
            .replace("\\", "\\\\")
            .replace(",", "\\,")
            .replace(";", "\\;")
            .replace("\n", "\\n")
            .replace("\r", "")
        )

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Kokpitim//Project deadlines//TR",
        "CALSCALE:GREGORIAN",
    ]
    for p in projects:
        if p.end_date:
            dt = p.end_date.strftime("%Y%m%d")
            lines.append("BEGIN:VEVENT")
            lines.append(f"UID:kokpitim-proj-{p.id}-end@local")
            lines.append(f"DTSTART;VALUE=DATE:{dt}")
            lines.append(f"DTEND;VALUE=DATE:{dt}")
            lines.append(f"SUMMARY:{esc(p.name)} — proje bitiş")
            lines.append("END:VEVENT")
    lines.append("END:VCALENDAR")
    body = "\r\n".join(lines)
    return Response(
        body,
        mimetype="text/calendar; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="proje_bitisleri.ics"'},
    )


@micro_bp.route("/project/bulk-notifications", methods=["POST"])
@login_required
def micro_project_bulk_notifications():
    if not is_privileged(current_user):
        flash("Bu işlem için yetkiniz yok.", "danger")
        return redirect(url_for("micro_bp.micro_project_list"))

    kid = kurum_id()
    if not kid:
        flash("Kurum bilgisi bulunamadı.", "danger")
        return redirect(url_for("micro_bp.launcher"))

    action = (request.form.get("action") or "").strip().lower()
    if action not in ("email_on", "email_off"):
        flash("Geçersiz işlem.", "warning")
        return redirect(url_for("micro_bp.micro_project_list"))

    raw_ids = request.form.getlist("project_ids")
    ids: list[int] = []
    for x in raw_ids:
        s = str(x).strip()
        if s.isdigit():
            ids.append(int(s))
    ids = list(dict.fromkeys(ids))
    if not ids:
        flash("Proje seçilmedi.", "warning")
        return redirect(url_for("micro_bp.micro_project_list"))

    q = accessible_projects_query(Project.query.filter(Project.id.in_(ids)), current_user, kid)
    allowed = {p.id for p in q.all()}
    email_on = action == "email_on"
    updated = 0
    for pid in ids:
        if pid not in allowed:
            continue
        proj = Project.query.get(pid)
        if not proj or proj.kurum_id != kid:
            continue
        try:
            settings = proj.get_notification_settings()
            if "channels" not in settings or not isinstance(settings["channels"], dict):
                settings["channels"] = {"in_app": True, "email": False}
            settings["channels"]["email"] = bool(email_on)
            proj.notification_settings = json.dumps(settings, ensure_ascii=False)
            updated += 1
        except Exception:
            continue

    db.session.commit()
    flash(
        f"{updated} projede e-posta bildirim kanalı {'açıldı' if email_on else 'kapatıldı'}.",
        "success",
    )
    return redirect(url_for("micro_bp.micro_project_list"))


@micro_bp.route("/project/portfolio")
@login_required
def micro_project_portfolio():
    if not can_crud_project_portfolio(current_user):
        flash("Bu sayfaya erişim yetkiniz yok.", "danger")
        return redirect(url_for("micro_bp.micro_project_list"))

    kid = kurum_id()
    if not kid:
        flash("Kurum bilgisi bulunamadı.", "danger")
        return redirect(url_for("micro_bp.launcher"))

    ctx = build_portfolio_context(kid)
    return render_template(
        "micro/project/portfolio.html",
        projects_with_scores=ctx["projects_with_scores"],
        process_totals=ctx["process_totals"],
        portfolio_source=ctx.get("portfolio_source", "legacy_matrix"),
    )
