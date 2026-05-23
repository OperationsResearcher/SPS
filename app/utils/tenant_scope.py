"""Tenant scope validation decorator — cross-tenant data leak koruması.

Audit (PROJE-AUDIT-2026Q2.md) bulgu: K-Radar ve diğer modüllerde tenant_id
validation tutarsız. Client başka tenant'ın resource_id'sini request edebilir.

Bu decorator: URL path parametresinden resource id'yi al, DB'den çek,
current_user.tenant_id ile karşılaştır, mismatch ise 403 dön.

Kullanım:
    @app_bp.route("/api/process/<int:process_id>")
    @login_required
    @verify_tenant_resource(Process, "process_id")
    def process_detail(process_id):
        ...

Alternatif: decorator argümanı yerine attr olarak verme:
    @verify_tenant_resource(Process, "process_id", tenant_attr="tenant_id")

Daha derin resource'lar için (Tenant'a indirect bağlı):
    @verify_tenant_resource(ProcessKpi, "kpi_id", resolver=lambda r: r.process.tenant_id)
"""
from __future__ import annotations

from functools import wraps
from typing import Callable, Optional, Any

from flask import abort, current_app
from flask_login import current_user


def verify_tenant_resource(
    model: Any,
    arg_name: str,
    tenant_attr: str = "tenant_id",
    resolver: Optional[Callable[[Any], int]] = None,
):
    """Decorator: URL path arg'dan resource id'yi al, tenant_id kontrol et.

    Args:
        model: SQLAlchemy model (Process, ProcessKpi, Strategy, ...).
        arg_name: URL path parametresinin adı (örn. "process_id").
        tenant_attr: Model'deki tenant_id alanının adı. Varsayılan "tenant_id".
                     Resource doğrudan tenant_id taşımıyorsa kullanma; resolver kullan.
        resolver: Resource verildiğinde tenant_id döndüren fonksiyon (indirect bağlama).

    Davranış:
        - URL arg'da resource_id yok → handler'a dokunmadan geç (404'ü handler verir).
        - Resource bulunamaz → 404.
        - Resource'un tenant_id'si current_user.tenant_id ile eşleşmez → 403 + audit log.
        - User Admin (cross-tenant yetkili) ise: kontrol atlanır.
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if arg_name not in kwargs:
                return f(*args, **kwargs)

            resource_id = kwargs[arg_name]
            if resource_id is None:
                return f(*args, **kwargs)

            # current_user kontrol
            if not current_user.is_authenticated:
                abort(401)

            # Admin kullanıcı her tenant'a erişebilir
            try:
                role_name = (current_user.role.name if current_user.role else "") or ""
            except Exception:
                role_name = ""
            if role_name.strip().lower() == "admin":
                return f(*args, **kwargs)

            # Resource'u getir
            resource = model.query.get(resource_id)
            if resource is None:
                abort(404)

            # Tenant_id çözümle
            if resolver is not None:
                try:
                    resource_tenant_id = resolver(resource)
                except Exception as e:
                    current_app.logger.error(
                        f"[tenant_scope] resolver hata: {model.__name__} "
                        f"id={resource_id}: {e}"
                    )
                    abort(500)
            else:
                resource_tenant_id = getattr(resource, tenant_attr, None)

            user_tenant_id = getattr(current_user, "tenant_id", None)
            if resource_tenant_id != user_tenant_id:
                current_app.logger.warning(
                    f"[tenant_scope] CROSS-TENANT BLOCKED: user={current_user.id} "
                    f"(tenant={user_tenant_id}) → {model.__name__} id={resource_id} "
                    f"(tenant={resource_tenant_id})"
                )
                # Audit log (silent fail OK — security log primary olarak app log'a düşer)
                try:
                    from app.utils.audit_logger import AuditLogger
                    AuditLogger.log(
                        action="CROSS_TENANT_BLOCKED",
                        resource_type=model.__name__,
                        resource_id=resource_id,
                        description=f"Tenant {user_tenant_id} tried to access {model.__name__} "
                                    f"belonging to tenant {resource_tenant_id}",
                    )
                except Exception:
                    pass
                abort(403)

            return f(*args, **kwargs)
        return wrapper
    return decorator
