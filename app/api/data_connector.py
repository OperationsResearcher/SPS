"""Power BI / Tableau / Excel için JSON data connector (Sprint 48).

REST API JSON formatında KPI verilerini döndürür. Power BI'da:
  Get Data → Web → URL: https://kokpitim.com/api/v1/dataconn/kpi-data?token=...

Token-based auth (API key) — kullanıcının kendi token'ı.
Bu token kullanıcı role + tenant_id ile sınırlı.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
import secrets
from typing import Optional

from flask import Blueprint, request, jsonify, current_app

from extensions import db
from app.models.core import User
from app.models.process import KpiData, ProcessKpi, Process


dataconn_bp = Blueprint("dataconn_bp", __name__, url_prefix="/api/v1/dataconn")


# ─── Token yönetimi ──────────────────────────────────────────────────────────
# Basit token sistemi: SHA256(user_id + secret) → token
# Production'da: ayrı api_tokens tablosu + expiration + scope

def _generate_user_api_token(user_id: int) -> str:
    """Deterministik token (user başına aynı). Production'da random + DB'de saklanmalı."""
    secret = current_app.config.get("SECRET_KEY", "")
    digest = hashlib.sha256(f"{user_id}:{secret}:dataconn".encode()).hexdigest()
    return f"kk_{digest[:32]}"


def _user_from_token(token: str) -> Optional[User]:
    """Token'dan user'ı bul."""
    if not token or not token.startswith("kk_"):
        return None
    # Tüm aktif user'larda match ara (küçük tenant için OK; ölçek için ayrı tablo gerek)
    users = User.query.filter(User.is_active == True).all()
    for u in users:
        if _generate_user_api_token(u.id) == token:
            return u
    return None


def _auth_or_401():
    """Header veya query'den token al, user döndür."""
    token = (
        request.headers.get("X-API-Token")
        or request.args.get("token")
        or request.args.get("apikey")
    )
    user = _user_from_token(token) if token else None
    return user


# ─── Endpoint'ler ────────────────────────────────────────────────────────────

@dataconn_bp.route("/kpi-data")
def dataconn_kpi_data():
    """KPI Data flat JSON — Power BI/Tableau için uygun denormalized format.

    Query params:
        ?year=2026
        ?from_date=2024-01-01
        ?process_code=P2M
        ?limit=10000 (default 5000, max 50000)
    """
    user = _auth_or_401()
    if not user:
        return jsonify({"error": "Geçersiz token. X-API-Token header veya ?token= ile gönder"}), 401

    tid = user.tenant_id
    year = request.args.get("year", type=int)
    from_date = request.args.get("from_date")
    process_code = request.args.get("process_code")
    limit = min(50000, max(1, request.args.get("limit", 5000, type=int)))

    q = (
        db.session.query(
            KpiData.id.label("data_id"),
            KpiData.year, KpiData.data_date, KpiData.period_type,
            KpiData.period_no, KpiData.period_month,
            KpiData.target_value, KpiData.actual_value,
            ProcessKpi.id.label("kpi_id"),
            ProcessKpi.code.label("kpi_code"),
            ProcessKpi.name.label("kpi_name"),
            ProcessKpi.unit, ProcessKpi.direction,
            Process.id.label("process_id"),
            Process.code.label("process_code"),
            Process.name.label("process_name"),
        )
        .join(ProcessKpi, KpiData.process_kpi_id == ProcessKpi.id)
        .join(Process, ProcessKpi.process_id == Process.id)
        .filter(Process.tenant_id == tid, KpiData.is_active == True)
    )

    if year:
        q = q.filter(KpiData.year == year)
    if from_date:
        try:
            d = _dt.date.fromisoformat(from_date)
            q = q.filter(KpiData.data_date >= d)
        except ValueError:
            pass
    if process_code:
        q = q.filter(Process.code == process_code)

    rows = q.order_by(KpiData.data_date.desc()).limit(limit).all()

    def _row_dict(r):
        return {
            "data_id": r.data_id,
            "year": r.year,
            "data_date": r.data_date.isoformat() if r.data_date else None,
            "period_type": r.period_type,
            "period_no": r.period_no,
            "period_month": r.period_month,
            "target_value": r.target_value,
            "actual_value": r.actual_value,
            "kpi_id": r.kpi_id,
            "kpi_code": r.kpi_code,
            "kpi_name": r.kpi_name,
            "unit": r.unit,
            "direction": r.direction,
            "process_id": r.process_id,
            "process_code": r.process_code,
            "process_name": r.process_name,
        }

    return jsonify({
        "tenant_id": tid,
        "count": len(rows),
        "limit": limit,
        "data": [_row_dict(r) for r in rows],
    })


@dataconn_bp.route("/processes")
def dataconn_processes():
    """Süreç listesi (Power BI için master data)."""
    user = _auth_or_401()
    if not user:
        return jsonify({"error": "Geçersiz token"}), 401

    rows = (
        Process.query.filter_by(tenant_id=user.tenant_id, is_active=True)
        .order_by(Process.code).all()
    )
    return jsonify({
        "tenant_id": user.tenant_id,
        "count": len(rows),
        "data": [{
            "id": p.id, "code": p.code, "name": p.name,
            "english_name": p.english_name,
            "weight": p.weight, "parent_id": p.parent_id,
            "plan_year_id": p.plan_year_id,
        } for p in rows],
    })


@dataconn_bp.route("/kpis")
def dataconn_kpis():
    """KPI tanım listesi."""
    user = _auth_or_401()
    if not user:
        return jsonify({"error": "Geçersiz token"}), 401

    rows = (
        ProcessKpi.query.join(Process)
        .filter(Process.tenant_id == user.tenant_id, ProcessKpi.is_active == True)
        .all()
    )
    return jsonify({
        "tenant_id": user.tenant_id,
        "count": len(rows),
        "data": [{
            "id": k.id, "code": k.code, "name": k.name,
            "unit": k.unit, "period": k.period,
            "target_value": k.target_value, "direction": k.direction,
            "weight": k.weight, "is_important": k.is_important,
            "process_id": k.process_id,
        } for k in rows],
    })


@dataconn_bp.route("/metadata")
def dataconn_metadata():
    """OData-style metadata + token info (Power BI bağlantı için)."""
    user = _auth_or_401()
    if not user:
        return jsonify({"error": "Geçersiz token"}), 401

    base = request.url_root.rstrip("/")
    return jsonify({
        "tenant_id": user.tenant_id,
        "user_email": user.email,
        "endpoints": {
            "kpi_data": f"{base}/api/v1/dataconn/kpi-data",
            "processes": f"{base}/api/v1/dataconn/processes",
            "kpis": f"{base}/api/v1/dataconn/kpis",
        },
        "auth": "X-API-Token header veya ?token= parametre",
        "rate_limit": "default tenant rate limit kuralları geçerli",
    })


# ─── Token alma — login'li kullanıcı için ────────────────────────────────────
# Bu endpoint AYRI bp'de, kullanıcı oturum açtıktan sonra /api/v1/dataconn'ı
# nasıl kullanacağını öğrenir.

def register_token_endpoint(app):
    """app/__init__.py'da çağrılır."""
    from flask_login import login_required, current_user

    @app.route("/api/me/dataconn-token", endpoint="api_me_dataconn_token")
    @login_required
    def _my_dataconn_token():
        from flask import jsonify
        token = _generate_user_api_token(current_user.id)
        base = request.url_root.rstrip("/")
        return jsonify({
            "token": token,
            "user_id": current_user.id,
            "tenant_id": current_user.tenant_id,
            "usage": f'curl -H "X-API-Token: {token}" "{base}/api/v1/dataconn/kpi-data"',
            "power_bi_url": f"{base}/api/v1/dataconn/kpi-data?token={token}",
            "warning": "Bu token'ı paylaşmayın — kullanıcı yetkilerinizi devreder.",
        })
