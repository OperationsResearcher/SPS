# -*- coding: utf-8 -*-
"""ESG / Sürdürülebilirlik — metrik + değer girişi (L3 Dal 4).

ESG modeli (EsgMetric/EsgMetricValue) + PDF raporu vardı ama VERİ GİRİŞİ UI'ı
yoktu → rapor üretilemez "ölü kod" idi. Bu dosya CRUD + değer girişi sağlar:
  - Metrik tanımı: ekle/düzenle/sil (E/S/G, scope, hedef, baseline)
  - Yıllık değer girişi: her metriğe yıl bazlı değer

Yönetim sayfası: /reports/esg-management
"""
from __future__ import annotations

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user

from platform_core import app_bp
from app.models import db
from app.models.esg import EsgMetric, EsgMetricValue
from flask_babel import gettext as _

# Yönetici rolleri (ESG yönetimi = stratejik/yönetim işi)
_ESG_ROLES = ("Admin", "admin", "tenant_admin", "executive_manager",
              "kurum_yoneticisi", "ust_yonetim")
_CATEGORIES = ("E", "S", "G")
_SCOPES = ("", "scope1", "scope2", "scope3")


def _can_manage_esg() -> bool:
    return bool(current_user.role and current_user.role.name in _ESG_ROLES)


def _metric_dict(m, values=None):
    d = {
        "id": m.id, "code": m.code or "", "name": m.name,
        "description": m.description or "", "category": m.category or "",
        "scope": m.scope or "", "unit": m.unit or "",
        "sdg_codes": m.sdg_codes or "", "target_value": m.target_value,
        "baseline_year": m.baseline_year, "baseline_value": m.baseline_value,
    }
    if values is not None:
        d["values"] = values
    return d


# ── Sayfa ─────────────────────────────────────────────────────────────────────

@app_bp.route("/reports/esg-management")
@login_required
def raporlar_esg_yonetim():
    """ESG metrik + değer yönetim sayfası."""
    return render_template("platform/reports/esg_yonetim.html",
                           can_edit=_can_manage_esg())


# ── API: Metrik listesi (+ değerler) ──────────────────────────────────────────

@app_bp.route("/reports/api/esg/metrics", methods=["GET"])
@login_required
def esg_api_metrics_list():
    tid = current_user.tenant_id
    try:
        metrics = (EsgMetric.query
                   .filter_by(tenant_id=tid, is_active=True)
                   .order_by(EsgMetric.category, EsgMetric.name).all())
        ids = [m.id for m in metrics]
        vals_by_metric = {}
        if ids:
            for v in EsgMetricValue.query.filter(EsgMetricValue.metric_id.in_(ids)).all():
                vals_by_metric.setdefault(v.metric_id, []).append(
                    {"id": v.id, "year": v.year, "value": v.value,
                     "source": v.source or "", "notes": v.notes or ""}
                )
        for k in vals_by_metric:
            vals_by_metric[k].sort(key=lambda x: x["year"], reverse=True)
        out = [_metric_dict(m, vals_by_metric.get(m.id, [])) for m in metrics]
        return jsonify({"success": True, "metrics": out,
                        "categories": list(_CATEGORIES), "scopes": list(_SCOPES)})
    except Exception as e:
        current_app.logger.error(f"[esg_api_metrics_list] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("ESG metrikleri alınamadı.")}), 500


# ── API: Metrik CRUD ──────────────────────────────────────────────────────────

@app_bp.route("/reports/api/esg/metrics", methods=["POST"])
@login_required
def esg_api_metric_add():
    if not _can_manage_esg():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"success": False, "message": _("Metrik adı zorunludur.")}), 400
    category = (data.get("category") or "").strip().upper()
    if category not in _CATEGORIES:
        return jsonify({"success": False, "message": _("Geçersiz kategori (E/S/G).")}), 400
    try:
        m = EsgMetric(
            tenant_id=current_user.tenant_id, name=name, category=category,
            code=(data.get("code") or "").strip() or None,
            description=(data.get("description") or "").strip() or None,
            scope=(data.get("scope") or "").strip() or None,
            unit=(data.get("unit") or "").strip() or None,
            sdg_codes=(data.get("sdg_codes") or "").strip() or None,
            target_value=_num(data.get("target_value")),
            baseline_year=_int(data.get("baseline_year")),
            baseline_value=_num(data.get("baseline_value")),
            is_active=True,
        )
        db.session.add(m)
        db.session.commit()
        return jsonify({"success": True, "id": m.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[esg_api_metric_add] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Metrik eklenemedi."}), 500


@app_bp.route("/reports/api/esg/metrics/<int:metric_id>", methods=["POST"])
@login_required
def esg_api_metric_update(metric_id):
    if not _can_manage_esg():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403
    m = EsgMetric.query.filter_by(
        id=metric_id, tenant_id=current_user.tenant_id, is_active=True).first()
    if not m:
        return jsonify({"success": False, "message": _("Metrik bulunamadı.")}), 404
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"success": False, "message": _("Metrik adı zorunludur.")}), 400
    category = (data.get("category") or m.category or "").strip().upper()
    if category not in _CATEGORIES:
        return jsonify({"success": False, "message": _("Geçersiz kategori (E/S/G).")}), 400
    try:
        m.name = name
        m.category = category
        m.code = (data.get("code") or "").strip() or None
        m.description = (data.get("description") or "").strip() or None
        m.scope = (data.get("scope") or "").strip() or None
        m.unit = (data.get("unit") or "").strip() or None
        m.sdg_codes = (data.get("sdg_codes") or "").strip() or None
        m.target_value = _num(data.get("target_value"))
        m.baseline_year = _int(data.get("baseline_year"))
        m.baseline_value = _num(data.get("baseline_value"))
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[esg_api_metric_update] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Metrik güncellenemedi.")}), 500


@app_bp.route("/reports/api/esg/metrics/<int:metric_id>/delete", methods=["POST"])
@login_required
def esg_api_metric_delete(metric_id):
    if not _can_manage_esg():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403
    m = EsgMetric.query.filter_by(
        id=metric_id, tenant_id=current_user.tenant_id, is_active=True).first()
    if not m:
        return jsonify({"success": False, "message": _("Metrik bulunamadı.")}), 404
    try:
        m.is_active = False  # soft delete (KURALLAR §3)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[esg_api_metric_delete] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Metrik silinemedi."}), 500


# ── API: Değer girişi (yıl bazlı upsert) ──────────────────────────────────────

@app_bp.route("/reports/api/esg/metrics/<int:metric_id>/value", methods=["POST"])
@login_required
def esg_api_value_save(metric_id):
    if not _can_manage_esg():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403
    m = EsgMetric.query.filter_by(
        id=metric_id, tenant_id=current_user.tenant_id, is_active=True).first()
    if not m:
        return jsonify({"success": False, "message": _("Metrik bulunamadı.")}), 404
    data = request.get_json(silent=True) or {}
    year = _int(data.get("year"))
    if not year:
        return jsonify({"success": False, "message": _("Yıl zorunludur.")}), 400
    try:
        # Yıl bazlı tekil değer (yıllık) — upsert
        row = EsgMetricValue.query.filter_by(
            metric_id=metric_id, year=year, period_type="Yıllık").first()
        if not row:
            row = EsgMetricValue(metric_id=metric_id, year=year, period_type="Yıllık")
            db.session.add(row)
        row.value = _num(data.get("value"))
        row.source = (data.get("source") or "").strip() or None
        row.notes = (data.get("notes") or "").strip() or None
        row.user_id = current_user.id
        db.session.commit()
        return jsonify({"success": True, "id": row.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[esg_api_value_save] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Değer kaydedilemedi.")}), 500


@app_bp.route("/reports/api/esg/values/<int:value_id>/delete", methods=["POST"])
@login_required
def esg_api_value_delete(value_id):
    if not _can_manage_esg():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403
    # tenant izolasyonu: değer → metrik → tenant
    row = (EsgMetricValue.query.join(EsgMetric, EsgMetricValue.metric_id == EsgMetric.id)
           .filter(EsgMetricValue.id == value_id,
                   EsgMetric.tenant_id == current_user.tenant_id).first())
    if not row:
        return jsonify({"success": False, "message": _("Değer bulunamadı.")}), 404
    try:
        db.session.delete(row)  # değer kaydı hard delete (audit dışı)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[esg_api_value_delete] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Değer silinemedi.")}), 500


# ── Yardımcılar ───────────────────────────────────────────────────────────────

def _num(v):
    try:
        return float(v) if v not in (None, "", "null") else None
    except (TypeError, ValueError):
        return None


def _int(v):
    try:
        return int(v) if v not in (None, "", "null") else None
    except (TypeError, ValueError):
        return None
