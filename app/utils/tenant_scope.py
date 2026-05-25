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


# ═══════════════════════════════════════════════════════════════════════════
# BAYI / HOLDING HİYERARŞİSİ — Sprint A
# ═══════════════════════════════════════════════════════════════════════════
#
# Tenant tipi: 'normal' / 'dealer' (bayi) / 'holding' (grup şirketi)
#
# Yetki politikası:
#   - Platform Admin (role='Admin')        → tüm tenant'lara erişim
#   - Bayi admin                            → sadece kendi tenant verisi (alt-tenantı yönetimsel görür)
#   - Holding admin                         → kendi tenant + alt-tenantlar (alt-tenantlar READ-ONLY)
#   - Normal kullanıcı                      → sadece kendi tenant
#
# KRİTİK: SQL sorgularında `accessible_tenant_ids(user)` filtre olarak kullanılır.
# Veri sızıntısını önleyen TEK katman bu. Test edilmeden değişiklik yapma.

from typing import Optional


TENANT_TYPE_NORMAL  = "normal"
TENANT_TYPE_DEALER  = "dealer"
TENANT_TYPE_HOLDING = "holding"
VALID_TENANT_TYPES  = {TENANT_TYPE_NORMAL, TENANT_TYPE_DEALER, TENANT_TYPE_HOLDING}


def is_platform_admin(user=None) -> bool:
    """Platform Admin (Kokpitim sahibi) mı?"""
    u = user or current_user
    if not u or not u.is_authenticated:
        return False
    return bool(u.role and u.role.name == "Admin")


def is_dealer_user(user=None) -> bool:
    """Bayi tenant'ına bağlı kullanıcı mı (admin olmak zorunda değil)?"""
    u = user or current_user
    if not u or not u.is_authenticated or not u.tenant:
        return False
    return u.tenant.tenant_type == TENANT_TYPE_DEALER


def is_holding_user(user=None) -> bool:
    """Holding tenant'ına bağlı kullanıcı mı?"""
    u = user or current_user
    if not u or not u.is_authenticated or not u.tenant:
        return False
    return u.tenant.tenant_type == TENANT_TYPE_HOLDING


def is_dealer_admin(user=None) -> bool:
    """Bayi admin mı (tenant_admin/Admin rol + bayi tenant)?"""
    u = user or current_user
    if not is_dealer_user(u):
        return False
    return bool(u.role and u.role.name in ("tenant_admin", "Admin"))


def is_holding_admin(user=None) -> bool:
    """Holding admin mı?"""
    u = user or current_user
    if not is_holding_user(u):
        return False
    return bool(u.role and u.role.name in ("tenant_admin", "executive_manager", "Admin"))


def child_tenant_ids(tenant_id: int) -> list[int]:
    """Verilen tenant'ın doğrudan alt-tenant id'leri (aktif olanlar)."""
    from extensions import db
    from app.models.core import Tenant
    rows = db.session.query(Tenant.id).filter(
        Tenant.parent_tenant_id == tenant_id,
        Tenant.is_active == True,
    ).all()
    return [r[0] for r in rows]


def accessible_tenant_ids(user=None) -> Optional[list[int]]:
    """Bu kullanıcı hangi tenant verisini GÖREBİLİR?

    Dönen:
      - None       → tüm tenant'lar (Platform Admin)
      - list[int]  → izinli tenant_id'leri (boş = hiçbir erişim)

    Kullanım:
        ids = accessible_tenant_ids(current_user)
        q = Model.query
        if ids is not None:
            q = q.filter(Model.tenant_id.in_(ids))
    """
    u = user or current_user
    if not u or not u.is_authenticated:
        return []

    # Platform Admin → tümü
    if is_platform_admin(u):
        return None

    own_tid = u.tenant_id
    if not own_tid:
        return []

    # Holding kullanıcısı → kendi + tüm alt tenantlar
    if is_holding_user(u):
        return [own_tid] + child_tenant_ids(own_tid)

    # Bayi ve normal kullanıcılar → sadece kendi tenant verisi
    return [own_tid]


def can_manage_sub_tenants(user=None) -> bool:
    """Bu kullanıcı alt-tenant açabilir/yönetebilir mi?"""
    u = user or current_user
    return is_platform_admin(u) or is_dealer_admin(u) or is_holding_admin(u)


def default_landing_endpoint(user=None) -> str:
    """Login sonrası yönlendirilecek varsayılan endpoint.

    - Holding admin       → app_bp.holding_dashboard_page
    - Bayi admin          → app_bp.admin_sub_tenants_page
    - Diğerleri (Platform Admin / normal kullanıcı) → app_bp.launcher
    """
    u = user or current_user
    if is_holding_admin(u):
        return "app_bp.holding_dashboard_page"
    if is_dealer_admin(u):
        return "app_bp.admin_sub_tenants_page"
    return "app_bp.launcher"


def is_readonly_for_tenant(tenant_id: int, user=None) -> bool:
    """Bu kullanıcı verilen tenant'a SALT-OKUR mu erişiyor?

    Holding admin alt-tenant'lara erişirken read-only olur.
    Kendi (parent) tenant'ında normal yetkisi geçerli.
    """
    u = user or current_user
    if not u or not u.is_authenticated:
        return True
    if is_platform_admin(u):
        return False
    # Holding kullanıcısı başka tenant'ı görüyorsa read-only
    if is_holding_user(u) and tenant_id and tenant_id != u.tenant_id:
        return True
    return False


def scope_query(query, model, user=None):
    """Bir SQLAlchemy query'ye tenant kapsam filtresi ekler.

    KULLANIM (yeni endpoint'lerde standart kullanılmalı):
        from app.utils.tenant_scope import scope_query
        items = scope_query(Process.query, Process).all()
    """
    if not hasattr(model, "tenant_id"):
        raise AttributeError(f"{model.__name__} modelinde tenant_id kolonu yok")
    ids = accessible_tenant_ids(user)
    if ids is None:  # Platform Admin
        return query
    if not ids:
        return query.filter(model.tenant_id == -1)
    return query.filter(model.tenant_id.in_(ids))


# ─── Validasyon ──────────────────────────────────────────────────────────────

def validate_tenant_type(tenant_type: str) -> str:
    """Tenant tipini doğrula, normalize et."""
    t = (tenant_type or "normal").strip().lower()
    if t not in VALID_TENANT_TYPES:
        raise ValueError(
            f"Geçersiz tenant tipi: {t}. Geçerli: {sorted(VALID_TENANT_TYPES)}"
        )
    return t


def can_be_parent(parent_tenant) -> tuple[bool, Optional[str]]:
    """Verilen tenant alt-tenant kabul edebilir mi? (ok, hata_mesajı)"""
    if not parent_tenant:
        return False, "Parent tenant bulunamadı"
    if not parent_tenant.is_active:
        return False, "Parent tenant pasif"
    if parent_tenant.tenant_type not in (TENANT_TYPE_DEALER, TENANT_TYPE_HOLDING):
        return False, "Parent yalnızca 'dealer' veya 'holding' tipi olabilir"
    if parent_tenant.parent_tenant_id is not None:
        # İç içe hiyerarşi yok: dealer/holding altına dealer/holding açılamaz.
        return False, "İç içe hiyerarşi desteklenmiyor (alt-tenant'ın altına tenant açılamaz)"
    return True, None


def check_sub_tenant_limit(parent_tenant) -> tuple[bool, Optional[str]]:
    """Parent'ın alt-tenant kotası aşıldı mı?"""
    if not parent_tenant.sub_tenant_limit:
        return True, None  # sınırsız
    current = parent_tenant.sub_tenants.filter_by(is_active=True).count()
    if current >= parent_tenant.sub_tenant_limit:
        return False, f"Alt tenant kotası dolu ({current}/{parent_tenant.sub_tenant_limit})"
    return True, None


# ─── Decorator: Read-Only Mode ───────────────────────────────────────────────

def block_if_holding_readonly(get_tenant_id: Optional[Callable] = None):
    """Holding kullanıcısının başka tenant'a yazma işlemi yapmasını engeller.

    Kullanım:
        @app_bp.route("/sp/api/initiatives", methods=["POST"])
        @login_required
        @block_if_holding_readonly()  # current_user.tenant_id'yi alır
        def create_initiative():
            ...

        # Veya URL'den tenant_id alıyorsan:
        @block_if_holding_readonly(lambda kw: kw.get("tenant_id"))

    Davranış:
        - Holding kullanıcı kendi tenant'ında değilse (alt-tenant'a erişiyorsa) → 403
        - Diğer kullanıcılar etkilenmez
    """
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)
            if is_holding_user(current_user) and not is_platform_admin(current_user):
                # Hangi tenant'a yazıyor?
                target_tid = None
                if get_tenant_id:
                    target_tid = get_tenant_id(kwargs)
                if target_tid is None:
                    # Default: kendi tenant'ında olduğunu varsay → izin
                    return f(*args, **kwargs)
                if target_tid != current_user.tenant_id:
                    current_app.logger.warning(
                        f"[tenant_scope] HOLDING_READONLY_BLOCKED: user={current_user.id} "
                        f"(holding tenant={current_user.tenant_id}) → write attempt to tenant={target_tid}"
                    )
                    try:
                        from app.utils.audit_logger import AuditLogger
                        AuditLogger.log(
                            action="HOLDING_READONLY_BLOCKED",
                            resource_type="HOLDING",
                            resource_id=target_tid,
                            description=f"Holding user attempted write on sub-tenant {target_tid}",
                        )
                    except Exception:
                        pass
                    abort(403, description="Holding görünümünde alt-tenant verisi yalnızca okunabilir.")
            return f(*args, **kwargs)
        return wrapper
    return decorator
