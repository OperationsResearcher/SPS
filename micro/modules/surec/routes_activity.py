"""Süreç modülü — Faaliyet API."""

from __future__ import annotations
from flask_babel import gettext as _

from datetime import datetime, timezone, date, timedelta
from io import BytesIO

from flask import render_template, jsonify, request, current_app, redirect, abort, send_file, url_for
from flask_login import login_required, current_user
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, selectinload

from platform_core import app_bp
from app.models import db
from sqlalchemy import or_, func as _sqla_func
from app.models.process import (
    Process,
    ProcessSubStrategyLink,
    ProcessKpi,
    ProcessActivity,
    ProcessActivityAssignee,
    ProcessActivityReminder,
    ActivityTrack,
    KpiData,
    KpiDataAudit,
    FavoriteKpi,
)
from app.models.core import User, Strategy, Tenant
from app.services.plan_year_service import (
    get_plan_year, get_kpi_configs_bulk, get_active_plan_year_for_user, list_plan_years,
    upsert_kpi_year_config,
)
from app.services.date_sovereign import (
    resolve_plan_year_for_date,
    entity_exists_in_year,
    build_existence_error,
    build_cross_year_notice,
    get_view_year,
)
from app.services.score_engine_service import compute_process_scores_internal
from app.utils.audit_logger import AuditLogger
from app.utils.db_sequence import is_pk_duplicate, sync_kpi_data_related_sequences, sync_pg_sequence_if_needed
from app.utils.process_utils import (
    validate_process_parent_id,
    last_day_of_period,
    data_date_to_period_keys,
    validate_same_tenant_sub_strategies,
)
from utils.karne_hesaplamalar import (
    hesapla_basari_puani as _hesapla_basari_puani,
    parse_basari_puani_araliklari as _parse_bpa,
)

from app_platform.modules.surec.permissions import (
    accessible_processes_filter,
    can_crud_process_entity,
    user_can_access_process,
    user_can_crud_pg_and_activity,
    user_can_edit_kpi_data_row,
    user_can_edit_process_record,
    user_can_enter_pgv,
)
from micro.modules.surec.helpers import (
    _apply_sub_strategy_links,
    _is_kpi_data_audit_pk_duplicate,
    _is_notification_pk_duplicate,
    _is_process_activity_pk_duplicate,
    _latest_delete_audit_by_kpi_data_ids,
    _latest_update_audit_by_kpi_data_ids,
    _parent_options_with_depth,
    _process_for_user,
    _user_can_add_activity,
    _user_can_manage_activity,
    _user_display_name,
    _users_pick_json,
)

@app_bp.route("/k-plan/process/api/activity/add", methods=["POST"])
@login_required
def surec_api_activity_add():
    data = request.get_json() or {}
    process_id = data.get("process_id")
    try:
        p = _process_for_user(int(process_id)) if process_id else None
    except (TypeError, ValueError):
        abort(400)
    if not p:
        abort(404)
    if not _user_can_add_activity(current_user, p):
        return jsonify({"success": False, "message": "Faaliyet ekleme yetkiniz yok."}), 403

    # ─── Tarih egemen plan year kontrolü (Faz 1) ──────────────────────────
    # Faaliyetin start_at'ı hangi yıla düşüyorsa, süreç o yılda var olmalı.
    tenant_obj = db.session.get(Tenant, current_user.tenant_id)
    cross_year_notice = None
    if tenant_obj and getattr(tenant_obj, "plan_year_enabled", False):
        raw_start = data.get("start_at") or data.get("start_date")
        target_date_for_check = None
        if raw_start:
            txt = str(raw_start).strip()
            try:
                target_date_for_check = datetime.strptime(txt[:10], "%Y-%m-%d").date()
            except ValueError:
                target_date_for_check = None
        if target_date_for_check:
            target_py = resolve_plan_year_for_date(current_user.tenant_id, target_date_for_check)
            if not entity_exists_in_year(p, target_py):
                return jsonify(build_existence_error(
                    entity=p,
                    entity_label=f"{p.code or ''} {p.name}".strip(),
                    data_date=target_date_for_check,
                    target_plan_year=target_py,
                    entity_kind="süreç",
                )), 409
            cross_year_notice = build_cross_year_notice(
                view_year=get_view_year(current_user),
                target_year=target_date_for_check.year,
            )

    try:
        def _parse_dt(v):
            if not v:
                return None
            txt = str(v).strip()
            for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.strptime(txt, fmt)
                except ValueError:
                    continue
            return None

        start_at = _parse_dt(data.get("start_at")) or _parse_dt(data.get("start_date"))
        end_at = _parse_dt(data.get("end_at")) or _parse_dt(data.get("end_date"))
        if not start_at and data.get("start_date"):
            start_at = datetime.strptime(data["start_date"], "%Y-%m-%d")
        if not end_at and data.get("end_date"):
            end_at = datetime.strptime(data["end_date"], "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        if not start_at or not end_at:
            return jsonify({"success": False, "message": _("Başlangıç ve bitiş zamanı zorunludur.")}), 400
        if end_at <= start_at:
            return jsonify({"success": False, "message": _("Bitiş başlangıçtan sonra olmalıdır.")}), 400

        can_multi = False
        try:
            can_multi = (
                (current_user.role and current_user.role.name in ("tenant_admin", "executive_manager", "Admin"))
                or any(int(u.id) == int(current_user.id) for u in (p.leaders or []))
            )
        except Exception:
            can_multi = False

        raw_assignees = data.get("assignee_ids") if data.get("assignee_ids") is not None else data.get("assigned_user_ids")
        if not isinstance(raw_assignees, list):
            raw_assignees = [raw_assignees] if raw_assignees is not None else []
        assignee_ids = []
        seen = set()
        allowed_ids = {int(u.id) for u in (p.leaders + p.members + p.owners) if u and u.is_active}
        for rid in raw_assignees:
            try:
                uid = int(rid)
            except (TypeError, ValueError):
                continue
            if uid in seen:
                continue
            seen.add(uid)
            if uid in allowed_ids:
                assignee_ids.append(uid)
        if not assignee_ids:
            assignee_ids = [int(current_user.id)]
        if not can_multi:
            assignee_ids = [int(current_user.id)]

        raw_offsets = data.get("reminder_offsets")
        if not isinstance(raw_offsets, list):
            raw_offsets = [raw_offsets] if raw_offsets is not None else []
        reminder_offsets = []
        r_seen = set()
        for rv in raw_offsets:
            try:
                m = int(rv)
            except (TypeError, ValueError):
                continue
            if m < 0 or m > 60 * 24 * 60 or m in r_seen:
                continue
            r_seen.add(m)
            reminder_offsets.append(m)

        active_py = get_active_plan_year_for_user(current_user)
        act = None
        for attempt in (1, 2):
            act = ProcessActivity(
                process_id=p.id,
                process_kpi_id=data.get("process_kpi_id") or None,
                name=data.get("name"),
                description=data.get("description"),
                status=data.get("status", "Planlandı"),
                progress=int(data.get("progress") or 0),
                start_at=start_at,
                end_at=end_at,
                start_date=start_at.date(),
                end_date=end_at.date(),
                notify_email=bool(data.get("notify_email", False)),
                plan_year_id=active_py.id if active_py else p.plan_year_id,
            )
            db.session.add(act)
            try:
                db.session.flush()
                break
            except IntegrityError as ie:
                db.session.rollback()
                if attempt == 1 and _is_process_activity_pk_duplicate(ie):
                    sync_pg_sequence_if_needed("process_activities", "id")
                    continue
                raise

        ProcessActivityAssignee.query.filter_by(activity_id=act.id).delete(synchronize_session=False)
        for idx, uid in enumerate(assignee_ids, start=1):
            db.session.add(ProcessActivityAssignee(
                activity_id=act.id,
                user_id=int(uid),
                order_no=idx,
                assigned_by=current_user.id,
                assigned_at=datetime.now(timezone.utc),
            ))

        ProcessActivityReminder.query.filter_by(activity_id=act.id).delete(synchronize_session=False)
        # PostgreSQL sequence kayması varsa reminder insert'i patlamasın.
        sync_pg_sequence_if_needed("process_activity_reminders", "id")
        for off in reminder_offsets:
            remind_at = start_at - timedelta(minutes=int(off))
            db.session.add(ProcessActivityReminder(
                activity_id=act.id,
                minutes_before=int(off),
                remind_at=remind_at,
                channel_email=bool(act.notify_email),
            ))
        db.session.commit()

        # Faaliyet ekleme bildirimi
        from sqlalchemy.orm import joinedload as _joinedload
        from app_platform.services.notification_triggers import notify_activity_assignment
        for n_attempt in (1, 2):
            try:
                p_with_users = Process.query.options(
                    _joinedload(Process.leaders), _joinedload(Process.members)
                ).get(p.id)
                notify_activity_assignment(act, p_with_users, actor=current_user)
                db.session.commit()
                break
            except Exception as notif_err:
                db.session.rollback()
                if n_attempt == 1 and _is_notification_pk_duplicate(notif_err):
                    sync_pg_sequence_if_needed("notifications", "id")
                    continue
                current_app.logger.warning(f"[surec_api_activity_add] notification: {notif_err}")
                break

        try:
            AuditLogger.log_create(
                "Süreç Faaliyeti",
                act.id,
                {"name": act.name, "process_id": act.process_id, "status": act.status},
            )
        except Exception as e:
            current_app.logger.error(f"Audit log hatası: {e}")
        resp = {"success": True, "message": "Faaliyet eklendi.", "id": act.id}
        if cross_year_notice:
            resp["notice"] = cross_year_notice
        return jsonify(resp)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_add] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


@app_bp.route("/k-plan/process/api/activity/get/<int:act_id>", methods=["GET"])
@login_required
def surec_api_activity_get(act_id):
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(act.process_id)
    if not proc or not user_can_access_process(current_user, proc):
        abort(403)
    return jsonify({
        "success": True,
        "activity": {
            "id": act.id,
            "name": act.name,
            "description": act.description,
            "status": act.status,
            "progress": act.progress,
            "start_date": str(act.start_date) if act.start_date else "",
            "end_date": str(act.end_date) if act.end_date else "",
            "start_at": act.start_at.strftime("%Y-%m-%dT%H:%M") if act.start_at else "",
            "end_at": act.end_at.strftime("%Y-%m-%dT%H:%M") if act.end_at else "",
            "notify_email": bool(act.notify_email),
            "assignee_ids": [int(x.user_id) for x in sorted(act.assignment_links, key=lambda z: z.order_no or 0)],
            "reminder_offsets": [int(r.minutes_before) for r in sorted(act.reminders, key=lambda z: z.minutes_before, reverse=True)],
            "process_kpi_id": act.process_kpi_id,
        },
    })


@app_bp.route("/k-plan/process/api/activity/update/<int:act_id>", methods=["POST"])
@login_required
def surec_api_activity_update(act_id):
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(act.process_id)
    if not proc or not _user_can_manage_activity(current_user, proc, act):
        return jsonify({"success": False, "message": _("Faaliyet güncelleme yetkiniz yok.")}), 403
    data = request.get_json() or {}
    try:
        def _parse_dt(v):
            if not v:
                return None
            txt = str(v).strip()
            for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
                try:
                    return datetime.strptime(txt, fmt)
                except ValueError:
                    continue
            return None

        act.name = data.get("name", act.name)
        act.description = data.get("description", act.description)
        act.status = data.get("status", act.status)
        act.progress = int(data.get("progress", act.progress) or 0)
        if "notify_email" in data:
            act.notify_email = bool(data.get("notify_email"))
        if "process_kpi_id" in data:
            act.process_kpi_id = data.get("process_kpi_id") or None

        parsed_start = _parse_dt(data.get("start_at")) or _parse_dt(data.get("start_date"))
        parsed_end = _parse_dt(data.get("end_at")) or _parse_dt(data.get("end_date"))
        if data.get("start_date") and not parsed_start:
            parsed_start = datetime.strptime(data["start_date"], "%Y-%m-%d")
        if data.get("end_date") and not parsed_end:
            parsed_end = datetime.strptime(data["end_date"], "%Y-%m-%d").replace(hour=23, minute=59, second=59)
        if parsed_start:
            act.start_at = parsed_start
            act.start_date = parsed_start.date()
        if parsed_end:
            act.end_at = parsed_end
            act.end_date = parsed_end.date()
        if act.start_at and act.end_at and act.end_at <= act.start_at:
            return jsonify({"success": False, "message": _("Bitiş başlangıçtan sonra olmalıdır.")}), 400

        if data.get("assignee_ids") is not None or data.get("assigned_user_ids") is not None:
            can_multi = (
                (current_user.role and current_user.role.name in ("tenant_admin", "executive_manager", "Admin"))
                or any(int(u.id) == int(current_user.id) for u in (proc.leaders or []))
            )
            raw_assignees = data.get("assignee_ids") if data.get("assignee_ids") is not None else data.get("assigned_user_ids")
            if not isinstance(raw_assignees, list):
                raw_assignees = [raw_assignees] if raw_assignees is not None else []
            allowed_ids = {int(u.id) for u in (proc.leaders + proc.members + proc.owners) if u and u.is_active}
            cleaned = []
            seen = set()
            for rid in raw_assignees:
                try:
                    uid = int(rid)
                except (TypeError, ValueError):
                    continue
                if uid in seen:
                    continue
                seen.add(uid)
                if uid in allowed_ids:
                    cleaned.append(uid)
            if not cleaned:
                cleaned = [int(current_user.id)]
            if not can_multi:
                cleaned = [int(current_user.id)]
            ProcessActivityAssignee.query.filter_by(activity_id=act.id).delete(synchronize_session=False)
            for idx, uid in enumerate(cleaned, start=1):
                db.session.add(ProcessActivityAssignee(
                    activity_id=act.id,
                    user_id=int(uid),
                    order_no=idx,
                    assigned_by=current_user.id,
                    assigned_at=datetime.now(timezone.utc),
                ))

        if "reminder_offsets" in data:
            raw_offsets = data.get("reminder_offsets")
            if not isinstance(raw_offsets, list):
                raw_offsets = [raw_offsets] if raw_offsets is not None else []
            offsets = []
            seen_r = set()
            for rv in raw_offsets:
                try:
                    mm = int(rv)
                except (TypeError, ValueError):
                    continue
                if mm < 0 or mm > 60 * 24 * 60 or mm in seen_r:
                    continue
                seen_r.add(mm)
                offsets.append(mm)
            ProcessActivityReminder.query.filter_by(activity_id=act.id).delete(synchronize_session=False)
            base_start = act.start_at or datetime.combine(act.start_date, datetime.min.time()) if act.start_date else None
            if base_start:
                for mm in offsets:
                    db.session.add(ProcessActivityReminder(
                        activity_id=act.id,
                        minutes_before=int(mm),
                        remind_at=base_start - timedelta(minutes=int(mm)),
                        channel_email=bool(act.notify_email),
                    ))
        db.session.commit()
        try:
            AuditLogger.log_update(
                "Süreç Faaliyeti",
                act.id,
                {},
                {"name": act.name, "process_id": act.process_id, "status": act.status, "progress": act.progress},
            )
        except Exception as e:
            current_app.logger.error(f"Audit log hatası: {e}")
        return jsonify({"success": True, "message": _("Faaliyet güncellendi.")})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_update] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


@app_bp.route("/k-plan/process/api/activity/delete/<int:act_id>", methods=["POST"])
@login_required
def surec_api_activity_delete(act_id):
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(act.process_id)
    if not proc or not _user_can_manage_activity(current_user, proc, act):
        return jsonify({"success": False, "message": "Faaliyet silme yetkiniz yok."}), 403
    try:
        act.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Faaliyet silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_delete] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


@app_bp.route("/k-plan/process/api/activity/cancel/<int:act_id>", methods=["POST"])
@login_required
def surec_api_activity_cancel(act_id):
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(act.process_id)
    if not proc or not _user_can_manage_activity(current_user, proc, act):
        return jsonify({"success": False, "message": "Faaliyet iptal yetkiniz yok."}), 403
    try:
        act.status = "İptal"
        act.cancelled_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"success": True, "message": "Faaliyet iptal edildi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_cancel] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


@app_bp.route("/k-plan/process/api/activity/postpone/<int:act_id>", methods=["POST"])
@login_required
def surec_api_activity_postpone(act_id):
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(act.process_id)
    if not proc or not _user_can_manage_activity(current_user, proc, act):
        return jsonify({"success": False, "message": "Faaliyet erteleme yetkiniz yok."}), 403
    data = request.get_json() or {}
    start_at_str = data.get("start_at", "")
    end_at_str = data.get("end_at", "")
    if not start_at_str or not end_at_str:
        return jsonify({"success": False, "message": _("Başlangıç ve bitiş tarihi zorunludur.")}), 400
    def _safe_parse_dt(val):
        txt = str(val).strip()
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M", "%Y-%m-%d"):
            try:
                return datetime.strptime(txt, fmt)
            except ValueError:
                continue
        return None

    new_start = _safe_parse_dt(start_at_str)
    new_end = _safe_parse_dt(end_at_str)
    if not new_start or not new_end:
        return jsonify({"success": False, "message": _("Tarih formatı geçersiz (YYYY-AA-GG veya ISO 8601).")}), 400
    if new_end <= new_start:
        return jsonify({"success": False, "message": _("Bitiş başlangıçtan sonra olmalıdır.")}), 400
    try:
        act.start_at = new_start
        act.end_at = new_end
        act.status = "Ertelendi"
        act.postponed_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"success": True, "message": "Faaliyet ertelendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_postpone] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


@app_bp.route("/k-plan/process/api/activity/complete/<int:act_id>", methods=["POST"])
@login_required
def surec_api_activity_complete(act_id):
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(act.process_id)
    if not proc or not _user_can_manage_activity(current_user, proc, act):
        return jsonify({"success": False, "message": "Faaliyet tamamlama yetkiniz yok."}), 403
    try:
        act.status = "Tamamlandı"
        act.progress = 100
        act.completed_at = datetime.now(timezone.utc)
        db.session.commit()
        return jsonify({"success": True, "message": _("Faaliyet tamamlandı.")})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_complete] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400


@app_bp.route("/k-plan/process/api/activity/track/<int:act_id>", methods=["POST"])
@login_required
def surec_api_activity_track(act_id):
    """Faaliyet aylık tamamlanma toggle (upsert)."""
    act = ProcessActivity.query.join(Process).filter(
        ProcessActivity.id == act_id,
        Process.tenant_id == current_user.tenant_id,
        Process.is_active.is_(True),
    ).first_or_404()
    proc = _process_for_user(act.process_id)
    if not proc or not _user_can_manage_activity(current_user, proc, act):
        return jsonify({"success": False, "message": _("Faaliyet takibi için yetkiniz yok.")}), 403
    data = request.get_json() or {}
    year = int(data.get("year", datetime.now().year))
    month = int(data.get("month", 1))
    completed = bool(data.get("completed", False))
    try:
        track = ActivityTrack.query.filter_by(
            activity_id=act.id, year=year, month=month
        ).first()
        if track:
            track.completed = completed
            track.user_id = current_user.id
        else:
            track = ActivityTrack(
                activity_id=act.id,
                year=year,
                month=month,
                completed=completed,
                user_id=current_user.id,
            )
            db.session.add(track)
        db.session.commit()
        return jsonify({"success": True, "completed": track.completed})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[surec_api_activity_track] {e}")
        return jsonify({"success": False, "message": _("İşlem tamamlanamadı.")}), 400

