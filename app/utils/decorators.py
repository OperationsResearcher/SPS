"""Security decorators."""

from functools import wraps

from flask import flash, jsonify, redirect, request, url_for
from flask_login import current_user, login_required


def require_component(component_code):
    """Ensure user's tenant package includes the given component. Use after @login_required.
    Admin, tenant_admin, executive_manager bypass package check and always have access."""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            if not current_user.is_authenticated:
                if _is_ajax():
                    return jsonify({"success": False, "error": "Unauthorized"}), 401
                return redirect(url_for("public_login"))
            if current_user.role and current_user.role.name in ("Admin", "tenant_admin", "executive_manager"):
                return f(*args, **kwargs)
            if not current_user.tenant:
                if _is_ajax():
                    return jsonify({"success": False, "error": "Tenant required"}), 403
                flash("Kurum bilginiz bulunamadı.", "danger")
                return redirect(url_for("dashboard_bp.index"))
            pkg = current_user.tenant.package
            if not pkg:
                if _is_ajax():
                    return jsonify({"success": False, "error": "Package required"}), 403
                flash("Paket bilginiz bulunamadı.", "danger")
                return redirect(url_for("dashboard_bp.index"))
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
                flash("Bu bileşene erişim yetkiniz yok.", "danger")
                return redirect(url_for("dashboard_bp.index"))
            return f(*args, **kwargs)

        return wrapped

    return decorator


def _is_ajax():
    """Check if request expects JSON or is XMLHttpRequest."""
    return (
        request.headers.get("X-Requested-With") == "XMLHttpRequest"
        or request.accept_mimetypes.best == "application/json"
    )
