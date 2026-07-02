"""Admin Blueprint - SaaS management (packages, modules, tenants)."""

import io
import re
import secrets
from datetime import datetime

import pandas as pd
from flask import Blueprint, abort, current_app, flash, jsonify, redirect, render_template, request, send_file, url_for
from flask_login import current_user, login_required

from sqlalchemy.orm import joinedload, selectinload

from werkzeug.security import generate_password_hash

from app.models import db
from app.models.core import Role, Tenant, User, Ticket, Strategy, SubStrategy
from app.models.saas import ModuleComponentSlug, RouteRegistry, SystemModule, SubscriptionPackage
from app.models.process import Process, ProcessKpi, ProcessSubStrategyLink
from app.utils.process_utils import validate_process_parent_id, validate_same_tenant_user_ids, validate_same_tenant_sub_strategies, ensure_int_list, parse_optional_date
from app.constants.roles import PLATFORM_ADMIN_ROLES
from flask_babel import gettext as _

# Privilege escalation guard: non-Admin roller yalnızca bu whitelist'teki rolleri atayabilir.
_ASSIGNABLE_ROLES = {
    'tenant_admin': {'executive_manager', 'standard_user'},
    'executive_manager': {'standard_user'},
}

admin_bp = Blueprint("admin_bp", __name__)


def _require_admin():
    """Ensure current user has Admin role."""
    if not current_user.is_authenticated:
        abort(401)
    if not current_user.role or current_user.role.name != "Admin":
        abort(403)


def _require_process_admin():
    """Ensure current user can manage processes (Admin, tenant_admin, executive_manager)."""
    if not current_user.is_authenticated:
        abort(401)
    if not current_user.role or current_user.role.name not in ("Admin", "tenant_admin", "executive_manager"):
        abort(403)


def _slugify(text):
    """Convert name to code (snake_case)."""
    if not text:
        return ""
    tr_map = {"ç": "c", "ğ": "g", "ı": "i", "ö": "o", "ş": "s", "ü": "u", "Ç": "c", "Ğ": "g", "İ": "i", "Ö": "o", "Ş": "s", "Ü": "u"}
    s = str(text).strip()
    for tr, en in tr_map.items():
        s = s.replace(tr, en)
    s = re.sub(r"[^\w]+", "_", s.lower()).strip("_")
    return s or "unnamed"


@admin_bp.route("/")
@login_required
def index():
    """Admin dashboard - summary stats and tenants overview."""
    _require_admin()
    tenants_list = (
        Tenant.query.options(joinedload(Tenant.package))
        .order_by(Tenant.name)
        .all()
    )
    users_count = User.query.filter_by(is_active=True).count()
    packages_count = SubscriptionPackage.query.filter_by(is_active=True).count()
    modules_count = SystemModule.query.filter_by(is_active=True).count()
    return render_template(
        "admin/index.html",
        tenants_list=tenants_list,
        tenants_count=len(tenants_list),
        users_count=users_count,
        packages_count=packages_count,
        modules_count=modules_count,
    )


def _require_admin_or_tenant_admin():
    """Admin, tenant_admin veya executive_manager erişebilir."""
    if not current_user.is_authenticated:
        abort(401)
    if not current_user.role or current_user.role.name not in ("Admin", "tenant_admin", "executive_manager"):
        abort(403)


@admin_bp.route("/strategy-management")
@login_required
def strategy_management():
    """Stratejik planlama akış yapısı - Admin tüm kurumları, tenant_admin/executive_manager sadece kendi kurumunu görür."""
    _require_admin_or_tenant_admin()
    tenant_id = request.args.get("tenant_id", type=int)
    tenants_q = Tenant.query.filter_by(is_active=True).order_by(Tenant.name)
    if current_user.role and current_user.role.name != "Admin":
        if not current_user.tenant_id:
            abort(403)
        tenants_q = tenants_q.filter_by(id=current_user.tenant_id)
    tenants_list = tenants_q.all()
    selected_tenant = None
    strategies = []
    processes = []
    if current_user.role and current_user.role.name != "Admin" and current_user.tenant_id:
        tenant_id = current_user.tenant_id
    if tenant_id:
        selected_tenant = Tenant.query.get(tenant_id)
        if selected_tenant:
            strategies = (
                Strategy.query.filter_by(tenant_id=tenant_id, is_active=True)
                .options(selectinload(Strategy.sub_strategies))
                .order_by(Strategy.code)
                .all()
            )
            processes = (
                Process.query.filter_by(tenant_id=tenant_id, is_active=True)
                .order_by(Process.code)
                .all()
            )
    return render_template(
        "admin/strategy_mgmt.html",
        tenants_list=tenants_list,
        selected_tenant=selected_tenant,
        strategies=strategies,
        processes=processes,
        active_tab="strategy_mgmt"
    )


def _parse_tenant_form():
    """Ortak form alanlarını parse et."""
    return {
        "name": (request.form.get("name") or "").strip(),
        "short_name": (request.form.get("short_name") or "").strip(),
        "activity_area": (request.form.get("activity_area") or "").strip() or None,
        "sector": (request.form.get("sector") or "").strip() or None,
        "employee_count": int(x) if (x := request.form.get("employee_count")) and x.strip().isdigit() else None,
        "contact_email": (request.form.get("contact_email") or "").strip() or None,
        "phone_number": (request.form.get("phone_number") or "").strip() or None,
        "website_url": (request.form.get("website_url") or "").strip() or None,
        "tax_office": (request.form.get("tax_office") or "").strip() or None,
        "tax_number": (request.form.get("tax_number") or "").strip() or None,
        "package_id": request.form.get("package_id") or None,
        "max_user_count": int(x) if (x := request.form.get("max_user_count")) and x.strip().isdigit() else 5,
        "license_end_date": _parse_date(request.form.get("license_end_date")),
    }


def _parse_date(val):
    """YYYY-MM-DD string'den date objesi."""
    if not val or not isinstance(val, str):
        return None
    try:
        return datetime.strptime(val.strip()[:10], "%Y-%m-%d").date()
    except (ValueError, TypeError):
        return None


@admin_bp.route("/tenants/archive/<int:tenant_id>", methods=["POST"])
@login_required
def tenants_archive(tenant_id):
    """Archive tenant (soft delete - set is_active=False)."""
    _require_admin()
    t = Tenant.query.get(tenant_id)
    if not t:
        flash(_("Kurum bulunamadı."), "danger")
        return redirect(url_for("admin_bp.tenants"))
    t.is_active = False
    db.session.commit()
    flash(_("Kurum arşivlendi."), "success")
    return redirect(url_for("admin_bp.tenants"))


# ---------------------------------------------------------------------------
# Users (Kullanıcı Yönetimi)
# ---------------------------------------------------------------------------

def _require_user_management():
    if not current_user.is_authenticated:
        abort(401)
    if not current_user.role:
        abort(403)
    allowed_roles = {'Admin', 'tenant_admin', 'executive_manager'}
    if current_user.role.name not in allowed_roles:
        abort(403)

def _parse_user_form():
    """Kullanıcı form alanlarını parse et."""
    return {
        "email": (request.form.get("email") or "").strip().lower(),
        "first_name": (request.form.get("first_name") or "").strip() or None,
        "last_name": (request.form.get("last_name") or "").strip() or None,
        "phone_number": (request.form.get("phone_number") or "").strip() or None,
        "job_title": (request.form.get("job_title") or "").strip() or None,
        "department": (request.form.get("department") or "").strip() or None,
        "profile_picture": (request.form.get("profile_picture") or "").strip() or None,
        "tenant_id": request.form.get("tenant_id") or None,
        "role_id": request.form.get("role_id") or None,
        "password": request.form.get("password") or "",
    }


@admin_bp.route("/users/bulk-template")
@login_required
def users_bulk_template():
    """Download template for bulk user import."""
    _require_user_management()
    
    if current_user.role.name == "standard_user":
        abort(403)
        
    output = io.BytesIO()
    data = [{
        "Ad": "Ahmet",
        "Soyad": "Yılmaz",
        "E-posta": "ahmet@ornek.com",
        "Şifre": "123456",
        "Unvan": "Mühendis",
        "Telefon": "5551234567"
    }]
    df = pd.DataFrame(data)
    df.to_excel(output, index=False, engine='openpyxl')
    output.seek(0)
    
    return send_file(
        output,
        download_name="kullanici_sablonu.xlsx",
        as_attachment=True,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

@admin_bp.route("/kule-iletisim")
@login_required
def kule_iletisim():
    """Kule İletişim yönetim paneli (Admin ve Yönetici erişimi)."""
    if (current_user.role.name if current_user.role else "") not in ['Admin', 'tenant_admin', 'executive_manager']:
        flash(_("Bu sayfayı görüntüleme yetkiniz yok."), "warning")
        return redirect(url_for('app_bp.masaustu'))  # Sprint 9: dashboard_bp → masaustu

    # Filter by tenant if not Admin
    query = Ticket.query
    if (current_user.role.name if current_user.role else "") != 'Admin':
        query = query.filter_by(tenant_id=current_user.tenant_id)
        
    tickets = query.order_by(Ticket.created_at.desc()).all()
    
    total = len(tickets)
    pending = sum(1 for t in tickets if t.status == 'Bekliyor')
    in_progress = sum(1 for t in tickets if t.status == 'İnceleniyor')
    resolved = sum(1 for t in tickets if t.status == 'Çözüldü')
    
    return render_template(
        "admin/kule_iletisim.html",
        active_tab="kule",
        tickets=tickets,
        total_count=total,
        pending_count=pending,
        in_progress_count=in_progress,
        resolved_count=resolved
    )


@admin_bp.route("/kule-iletisim/<int:ticket_id>/detail")
@login_required
def kule_ticket_detail(ticket_id):
    if (current_user.role.name if current_user.role else "") not in ['Admin', 'tenant_admin', 'executive_manager']:
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403

    ticket = Ticket.query.get_or_404(ticket_id)
    if (current_user.role.name if current_user.role else "") != 'Admin' and ticket.tenant_id != current_user.tenant_id:
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403

    return jsonify({
        "success": True,
        "ticket": {
            "id": ticket.id,
            "user_name": f"{ticket.user.first_name or ''} {ticket.user.last_name or ''}".strip(),
            "tenant_name": ticket.tenant.name if ticket.tenant else 'Bireysel',
            "subject": ticket.subject,
            "message": ticket.message,
            "page_url": ticket.page_url,
            "screenshot_path": ticket.screenshot_path,
            "status": ticket.status,
            "admin_note": ticket.admin_note,
            "created_at": ticket.created_at.strftime('%d.%m.%Y %H:%M')
        }
    })


@admin_bp.route("/kule-iletisim/<int:ticket_id>/update", methods=["POST"])
@login_required
def kule_ticket_update(ticket_id):
    if (current_user.role.name if current_user.role else "") not in ['Admin', 'tenant_admin', 'executive_manager']:
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403

    ticket = Ticket.query.get_or_404(ticket_id)
    if (current_user.role.name if current_user.role else "") != 'Admin' and ticket.tenant_id != current_user.tenant_id:
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403

    data = request.get_json()
    new_status = data.get("status")
    admin_note = data.get("admin_note")
    
    if new_status:
        ticket.status = new_status
    if admin_note is not None:
        ticket.admin_note = admin_note
        
    db.session.commit()
    return jsonify({"success": True})


# ──────────────────────────────────────────────────
# Admin Süreç CRUD (Plan Faz 3)
# ──────────────────────────────────────────────────

@admin_bp.route("/get-process/<int:process_id>")
@login_required
def admin_get_process(process_id):
    """Süreç bilgilerini getir - admin/edit için."""
    _require_process_admin()
    p = Process.query.options(
        joinedload(Process.leaders),
        joinedload(Process.members),
        joinedload(Process.owners),
        selectinload(Process.process_sub_strategy_links).joinedload(ProcessSubStrategyLink.sub_strategy)
    ).filter_by(id=process_id, is_active=True).first_or_404()
    if p.tenant_id != current_user.tenant_id and current_user.role.name != "Admin":
        abort(403)
    return jsonify({
        "success": True,
        "process": {
            "id": p.id,
            "code": p.code,
            "name": p.name,
            "english_name": p.english_name,
            "description": p.description,
            "document_no": p.document_no,
            "revision_no": p.revision_no,
            "revision_date": str(p.revision_date) if p.revision_date else "",
            "first_publish_date": str(p.first_publish_date) if p.first_publish_date else "",
            "start_date": str(p.start_date) if p.start_date else "",
            "end_date": str(p.end_date) if p.end_date else "",
            "status": p.status,
            "progress": p.progress,
            "parent_id": p.parent_id,
            "start_boundary": p.start_boundary,
            "end_boundary": p.end_boundary,
            "weight": p.weight,
            "leader_ids": [u.id for u in p.leaders],
            "member_ids": [u.id for u in p.members],
            "owner_ids": [u.id for u in p.owners],
            "sub_strategy_ids": [s.id for s in p.sub_strategies],
        }
    })


@admin_bp.route("/create-process", methods=["POST"])
@login_required
def admin_create_process():
    """Admin süreç oluştur."""
    _require_process_admin()
    if not request.is_json:
        return jsonify({"success": False, "message": _("Content-Type application/json olmalı")}), 400
    data = request.get_json() or {}
    name = (data.get("name") or data.get("ad") or "").strip()
    if not name:
        return jsonify({"success": False, "message": _("Süreç adı zorunludur")}), 400

    tenant_id = current_user.tenant_id
    parent_id_raw = data.get("parent_id")
    parent_id = validate_process_parent_id(None, parent_id_raw, tenant_id)

    new_process = Process(
        tenant_id=tenant_id,
        parent_id=parent_id,
        code=data.get("code") or None,
        name=name,
        english_name=data.get("english_name") or None,
        description=(data.get("description") or "").strip() or None,
        document_no=(data.get("document_no") or "").strip() or None,
        revision_no=(data.get("revision_no") or "").strip() or None,
        status=data.get("status", "Aktif"),
        progress=int(data.get("progress", 0) or 0),
        start_boundary=(data.get("start_boundary") or "").strip() or None,
        end_boundary=(data.get("end_boundary") or "").strip() or None,
    )
    for field, attr in [
        ("revision_date", "revision_date"),
        ("first_publish_date", "first_publish_date"),
        ("start_date", "start_date"),
        ("end_date", "end_date"),
    ]:
        if data.get(field):
            val = parse_optional_date(data.get(field))
            if val:
                setattr(new_process, attr, val)
    if data.get("weight") is not None and str(data.get("weight", "")).strip() != "":
        try:
            new_process.weight = min(100.0, max(0.0, float(data.get("weight"))))
        except (ValueError, TypeError):
            pass

    db.session.add(new_process)
    db.session.flush()

    leader_ids = ensure_int_list(data.get("leader_ids"))
    member_ids = ensure_int_list(data.get("member_ids"))
    sub_strategy_ids = ensure_int_list(data.get("sub_strategy_ids") or data.get("strateji_ids"))
    if leader_ids:
        new_process.leaders = validate_same_tenant_user_ids(tenant_id, leader_ids)
    if member_ids:
        new_process.members = validate_same_tenant_user_ids(tenant_id, member_ids)
    if sub_strategy_ids:
        new_process.sub_strategies = validate_same_tenant_sub_strategies(tenant_id, sub_strategy_ids)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_create_process] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Süreç oluşturulamadı.")}), 500
    return jsonify({"success": True, "message": _("Süreç başarıyla oluşturuldu"), "id": new_process.id})


@admin_bp.route("/add-process", methods=["POST"])
@login_required
def admin_add_process():
    """Admin panel hiyerarşik ekleme - create ile aynı."""
    return admin_create_process()


@admin_bp.route("/update-process/<int:process_id>", methods=["PUT", "POST"])
@login_required
def admin_update_process(process_id):
    """Admin süreç güncelle."""
    _require_process_admin()
    if not request.is_json:
        return jsonify({"success": False, "message": _("Content-Type application/json olmalı")}), 400
    p = Process.query.filter_by(id=process_id, is_active=True).first_or_404()
    if p.tenant_id != current_user.tenant_id and current_user.role.name not in PLATFORM_ADMIN_ROLES:
        abort(403)

    data = request.get_json() or {}
    p.code = data.get("code", p.code)
    p.name = data.get("name", p.name)
    p.english_name = data.get("english_name", p.english_name)
    p.description = data.get("description", p.description)
    p.document_no = data.get("document_no", p.document_no)
    p.revision_no = data.get("revision_no", p.revision_no)
    p.status = data.get("status", p.status)
    p.progress = int(data.get("progress", p.progress) or 0)
    p.start_boundary = data.get("start_boundary", p.start_boundary)
    p.end_boundary = data.get("end_boundary", p.end_boundary)
    parent_id_raw = data.get("parent_id")
    p.parent_id = validate_process_parent_id(p.id, parent_id_raw, p.tenant_id)

    for field, attr in [
        ("revision_date", "revision_date"),
        ("first_publish_date", "first_publish_date"),
        ("start_date", "start_date"),
        ("end_date", "end_date"),
    ]:
        if data.get(field):
            val = parse_optional_date(data.get(field))
            if val:
                setattr(p, attr, val)
    if data.get("weight") is not None and str(data.get("weight", "")).strip() != "":
        try:
            p.weight = min(100.0, max(0.0, float(data.get("weight"))))
        except (ValueError, TypeError):
            pass

    if "leader_ids" in data:
        ids = ensure_int_list(data.get("leader_ids"))
        p.leaders = validate_same_tenant_user_ids(p.tenant_id, ids) if ids else []
    if "member_ids" in data:
        ids = ensure_int_list(data.get("member_ids"))
        p.members = validate_same_tenant_user_ids(p.tenant_id, ids) if ids else []
    if "sub_strategy_ids" in data or "strateji_ids" in data:
        ids = ensure_int_list(data.get("sub_strategy_ids") or data.get("strateji_ids"))
        p.sub_strategies = validate_same_tenant_sub_strategies(p.tenant_id, ids) if ids else []

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_update_process] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Süreç güncellenemedi.")}), 500
    return jsonify({"success": True, "message": _("Süreç başarıyla güncellendi")})


@admin_bp.route("/delete-process/<int:process_id>", methods=["DELETE", "POST"])
@login_required
def admin_delete_process(process_id):
    """Admin süreç silme (soft delete)."""
    _require_process_admin()
    p = Process.query.filter_by(id=process_id, is_active=True).first_or_404()
    if p.tenant_id != current_user.tenant_id and current_user.role.name not in PLATFORM_ADMIN_ROLES:
        abort(403)
    from datetime import timezone as tz
    p.is_active = False
    p.deleted_at = datetime.now(tz.utc)
    p.deleted_by = current_user.id
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[admin_delete_process] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Süreç silinemedi.")}), 500
    return jsonify({"success": True, "message": _("Süreç başarıyla silindi")})