"""Merkezi API yanıt yardımcıları.

Kullanım:
    from app.utils.api_response import ok, err, paginated

    return ok(data)
    return err("Kayıt bulunamadı.", 404)
    return paginated(items, total, page, per_page)
"""
from __future__ import annotations

from typing import Any

from flask import jsonify


def ok(data: Any = None, message: str = "", status: int = 200):
    """Başarılı yanıt."""
    body: dict = {"success": True}
    if data is not None:
        body["data"] = data
    if message:
        body["message"] = message
    return jsonify(body), status


def err(message: str, status: int = 400, code: str | None = None):
    """Hata yanıtı."""
    body: dict = {"success": False, "message": message}
    if code:
        body["code"] = code
    return jsonify(body), status


def paginated(items: list, total: int, page: int, per_page: int, **extra):
    """Sayfalı liste yanıtı."""
    body = {
        "success": True,
        "data": items,
        "pagination": {
            "total": total,
            "page": page,
            "per_page": per_page,
            "pages": (total + per_page - 1) // per_page,
            "has_next": page * per_page < total,
            "has_prev": page > 1,
        },
    }
    body.update(extra)
    return jsonify(body), 200
