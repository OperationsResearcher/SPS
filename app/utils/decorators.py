"""Security decorators."""

from functools import wraps

from flask import flash, jsonify, redirect, request, url_for
from flask_login import current_user, login_required
from flask_babel import gettext as _


def require_component(component_code):
    """Ensure user's tenant package includes the given component. Use after @login_required.

    Yalnızca platform Admin bypass eder (tüm kurumları yönetir, paketi yok).
    Kurum rolleri (tenant_admin/executive_manager) paket sınırına TABİDİR
    — paket gating'i bu rollerde de geçerli (L2/L3 kararı, 2026-06-20)."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                if _is_ajax():
                    return jsonify({"success": False, "error": "Unauthorized"}), 401
                return redirect(url_for("public_login"))
            if current_user.role and current_user.role.name == "Admin":
                return f(*args, **kwargs)
            if not current_user.tenant:
                if _is_ajax():
                    return jsonify({"success": False, "error": "Tenant required"}), 403
                flash(_("Kurum bilginiz bulunamadı."), "danger")
                return redirect(url_for("app_bp.masaustu"))
            pkg = current_user.tenant.package
            if not pkg:
                if _is_ajax():
                    return jsonify({"success": False, "error": "Package required"}), 403
                flash(_("Paket bilginiz bulunamadı."), "danger")
                return redirect(url_for("app_bp.masaustu"))
            has_access = False
            for mod in pkg.modules:
                for comp in mod.component_slugs:
                    if comp.component_slug == component_code:
                        has_access = True
                        break
                if has_access:
                    break
            if not has_access:
                if _is_ajax():
                    return jsonify({"success": False, "error": "Unauthorized"}), 403
                flash(_("Bu bileşene erişim yetkiniz yok."), "danger")
                return redirect(url_for("app_bp.masaustu"))
            return f(*args, **kwargs)

        return wrapped

    return decorator


def require_module(module_id):
    """Route'u launcher modül kimliğine göre gate'le (paket düzeyi).

    get_accessible_modules ile aynı kapı — sidebar/launcher ile tutarlı.
    Paket'te modül yoksa: AJAX→403, sayfa→masaüstüne yönlendir + uyarı.
    Yalnızca platform Admin bypass (tüm kurumlar). Kurum rolleri pakete tabi.

    Kullanım (@login_required'dan SONRA):
        @app_bp.route("/sp/exec-dashboard")
        @login_required
        @require_module("surec")
        def sp_exec_dashboard(): ...
    """
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                if _is_ajax():
                    return jsonify({"success": False, "error": "Unauthorized"}), 401
                return redirect(url_for("public_login"))
            if current_user.role and current_user.role.name == "Admin":
                return f(*args, **kwargs)
            try:
                from app_platform.core.module_registry import get_accessible_modules
                allowed = {m["id"] for m in get_accessible_modules(current_user)}
            except Exception:
                # Gating çözülemezse engelleme (mevcut davranışa düş)
                return f(*args, **kwargs)
            if module_id not in allowed:
                if _is_ajax():
                    return jsonify({"success": False, "error": "Paket kapsamı dışında."}), 403
                flash(_("Bu bölüm mevcut paketinizde yer almıyor."), "warning")
                return redirect(url_for("app_bp.masaustu"))
            return f(*args, **kwargs)

        return wrapped

    return decorator


def _is_ajax():
    """Check if request expects JSON or is XMLHttpRequest."""
    return (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.accept_mimetypes.best == "application/json"
    )
