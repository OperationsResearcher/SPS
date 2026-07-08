# -*- coding: utf-8 -*-
"""Kurulum verisi import sihirbazı route'ları (TASK-235).

Tasarım: docs/paketler/KURULUM-IMPORT-SIHIRBAZI.md
Erişim: platform Admin veya tenant_admin (kurum yöneticisi).
"""
from flask import render_template, request, jsonify, send_file, current_app
from flask_login import login_required, current_user
from flask_babel import gettext as _

from platform_core import app_bp
from app.extensions import csrf


def _can_setup_import():
    role = current_user.role.name if current_user.role else ""
    return role in ("Admin", "tenant_admin")


@app_bp.route("/admin/setup-import")
@login_required
def admin_setup_import_page():
    """Sihirbaz sayfası (3 adım)."""
    if not _can_setup_import():
        return render_template("platform/errors/403.html"), 403
    return render_template("platform/admin/setup_import.html")


@app_bp.route("/admin/setup-import/template")
@login_required
def admin_setup_import_template():
    """3 sayfalı kurulum şablonu indir."""
    if not _can_setup_import():
        return jsonify({"success": False, "message": _("Yetkiniz yok.")}), 403
    import io
    from app.services.setup_import_service import make_setup_template_excel

    return send_file(
        io.BytesIO(make_setup_template_excel()),
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name="kokpitim_kurulum_sablonu.xlsx",
    )


def _read_upload():
    """Yüklenen dosyayı doğrula, bytes döndür. (None, response) hatada."""
    from app.utils.security import validate_file_upload

    f = request.files.get("file")
    ok, err = validate_file_upload(f, allowed_extensions={"xlsx"}, max_size_mb=5)
    if not ok:
        return None, (jsonify({"success": False, "message": err}), 400)
    return f.read(), None


@app_bp.route("/admin/setup-import/dry-run", methods=["POST"])
@csrf.exempt
@login_required
def admin_setup_import_dry_run():
    """Yazma yapmadan önizleme planı döner."""
    if not _can_setup_import():
        return jsonify({"success": False, "message": _("Yetkiniz yok.")}), 403
    file_bytes, err = _read_upload()
    if err:
        return err
    from app.services.setup_import_service import parse_workbook

    plan = parse_workbook(file_bytes, current_user.tenant_id)
    return jsonify(plan)


@app_bp.route("/admin/setup-import/apply", methods=["POST"])
@csrf.exempt
@login_required
def admin_setup_import_apply():
    """Planı tek transaction'da uygular."""
    if not _can_setup_import():
        return jsonify({"success": False, "message": _("Yetkiniz yok.")}), 403
    file_bytes, err = _read_upload()
    if err:
        return err
    skip_errors = (request.form.get("skip_errors") or "").lower() in ("1", "true", "on")

    plan_year_id = None
    try:
        from app.services.plan_year_service import get_active_plan_year_for_user

        py = get_active_plan_year_for_user(current_user)
        plan_year_id = py.id if py else None
    except Exception as e:
        current_app.logger.warning(f"[setup_import] plan year resolution suppressed: {e}")

    from app.services.setup_import_service import apply_workbook

    result = apply_workbook(
        file_bytes, current_user.tenant_id, current_user.id,
        skip_errors=skip_errors, plan_year_id=plan_year_id,
    )

    if result.get("applied"):
        try:
            from app.utils.audit_logger import AuditLogger

            AuditLogger.log(
                action="SETUP_IMPORT_APPLY",
                resource_type="SetupImport",
                description=f"file={request.files['file'].filename}",
                new_values=result.get("result"),
            )
        except Exception as e:
            current_app.logger.warning(f"[setup_import] audit suppressed: {e}")
    return jsonify(result)
