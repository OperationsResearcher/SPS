"""Pagination utility (Sprint 19.3).

Tüm liste endpoint'lerinde DOS koruması — `.all()` yerine bu helper.

Kullanım:
    from app.utils.pagination import paginate_query

    @app_bp.route("/api/users")
    def api_users():
        q = User.query.filter_by(tenant_id=tid)
        return jsonify(paginate_query(q, default_page_size=50, max_page_size=200))
"""
from __future__ import annotations

from flask import request
from sqlalchemy.orm import Query


def paginate_query(
    query: Query,
    default_page_size: int = 50,
    max_page_size: int = 500,
    serializer=None,
) -> dict:
    """Sorguyu sayfalandır ve JSON-uyumlu dict döndür.

    Args:
        query: SQLAlchemy Query
        default_page_size: Varsayılan limit (request.args.page_size yoksa)
        max_page_size: Tek seferde döndürülebilecek max kayıt
        serializer: Her satırı dict'e çeviren fonksiyon. None ise model.to_dict() veya __dict__

    Query params:
        page: 1-bazlı sayfa numarası (default 1)
        page_size: sayfa boyutu (default default_page_size, max max_page_size)

    Returns:
        {
            "data": [...],
            "page": 1,
            "page_size": 50,
            "total": 1234,
            "total_pages": 25,
            "has_next": true,
            "has_prev": false,
        }
    """
    try:
        page = max(1, int(request.args.get("page", 1)))
    except (ValueError, TypeError):
        page = 1
    try:
        page_size = int(request.args.get("page_size", default_page_size))
    except (ValueError, TypeError):
        page_size = default_page_size

    # Clamp
    page_size = max(1, min(page_size, max_page_size))

    total = query.count()
    total_pages = (total + page_size - 1) // page_size if total else 0

    if total_pages and page > total_pages:
        page = total_pages

    offset = (page - 1) * page_size
    items = query.limit(page_size).offset(offset).all()

    def _ser(item):
        if serializer:
            return serializer(item)
        if hasattr(item, "to_dict"):
            return item.to_dict()
        # SQLAlchemy default: __dict__ tüm public kolonları al
        return {k: v for k, v in vars(item).items() if not k.startswith("_")}

    return {
        "data": [_ser(it) for it in items],
        "page": page,
        "page_size": page_size,
        "total": total,
        "total_pages": total_pages,
        "has_next": page < total_pages,
        "has_prev": page > 1,
    }
