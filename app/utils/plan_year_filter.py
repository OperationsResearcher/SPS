"""Plan year filter helper — multi-year tenant'larda tutarlı sorgu pattern'i.

Audit (PROJE-AUDIT-2026Q2.md) bulgu #1: Plan year NULL handling 3 farklı pattern'le yapılıyor.
Bu modül tek doğru yöntemi sağlar. Tüm modüller buradan import etmeli.
"""
from __future__ import annotations

from typing import Optional, Any

from sqlalchemy import or_
from sqlalchemy.orm import Query


def filter_by_plan_year(
    query: Query,
    model: Any,
    plan_year_id: Optional[int],
    include_null: bool = True,
) -> Query:
    """Aktif plan year filtresini sorguya ekler.

    Args:
        query: SQLAlchemy Query nesnesi
        model: Filtrelenecek model (Process, Strategy, SubStrategy, ProcessKpi, KpiData...)
        plan_year_id: Aktif plan year id'si. None ise filtre uygulanmaz.
        include_null: True (varsayılan) ise plan_year_id IS NULL olan legacy kayıtlar
                      da dahil edilir. False ise yalnızca tam eşleşme.

    Kullanım:
        from app.utils.plan_year_filter import filter_by_plan_year

        q = Process.query.filter_by(tenant_id=tid, is_active=True)
        q = filter_by_plan_year(q, Process, active_py.id if active_py else None)
        results = q.all()

    Notlar:
        - plan_year_id=None gelirse hiç filtre uygulanmaz (geriye dönük uyum).
        - model'in plan_year_id kolonu OLMASI gerekir; yoksa AttributeError.
        - include_null=False yalnızca yıl-clone tabanlı (Tomofil gibi) tenant'lar için.
    """
    if plan_year_id is None:
        return query

    col = getattr(model, "plan_year_id", None)
    if col is None:
        raise AttributeError(
            f"{model.__name__} modelinde plan_year_id kolonu yok — "
            f"filter_by_plan_year kullanılamaz."
        )

    if include_null:
        return query.filter(or_(col == plan_year_id, col.is_(None)))
    return query.filter(col == plan_year_id)


def filter_by_plan_year_scoped(
    query: Query,
    model: Any,
    plan_year_id: Optional[int],
    tenant_id: int,
    include_null: bool = True,
) -> Query:
    """plan_year + tenant_id güvenlik kombinasyonu (Sprint 53 — Ö2).

    Bu varyant, NULL legacy verileri SADECE aynı tenant'a aitse dahil eder.
    Cross-tenant veri sızıntısı koruması için kritik.

    SQL eşdeğeri:
        WHERE (plan_year_id = X) OR (plan_year_id IS NULL AND tenant_id = T)
    """
    from sqlalchemy import and_, or_

    if plan_year_id is None:
        return query

    col = getattr(model, "plan_year_id", None)
    tenant_col = getattr(model, "tenant_id", None)
    if col is None:
        raise AttributeError(f"{model.__name__} modelinde plan_year_id yok")

    if include_null and tenant_col is not None:
        return query.filter(
            or_(col == plan_year_id, and_(col.is_(None), tenant_col == tenant_id))
        )
    if include_null:
        # Tenant_id yoksa basit OR
        return query.filter(or_(col == plan_year_id, col.is_(None)))
    return query.filter(col == plan_year_id)


def get_active_plan_year_id(user) -> Optional[int]:
    """Kullanıcı için aktif plan year id'sini döndürür. None ise legacy mode (tenant'ta plan year yok).

    Wrapper — tüm modüllerin tek noktadan kullanması için.
    """
    try:
        from app.services.plan_year_service import get_active_plan_year_for_user
    except ImportError:
        return None
    py = get_active_plan_year_for_user(user)
    return py.id if py else None
