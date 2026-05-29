"""Stratejik Planlama — SWOT/TOWS/PESTLE/OKR/BSC API."""

from functools import wraps

from flask import render_template, jsonify, request, current_app, session
from flask_login import login_required, current_user
from sqlalchemy.orm import selectinload

from platform_core import app_bp
from app.extensions import csrf
from app.models import db
from sqlalchemy import or_
from app.models.core import Strategy, SubStrategy, Tenant
from app.models.k_vektor import KVektorStrategyWeight, KVektorSubStrategyWeight
from app.services.k_vektor_config_service import (
    apply_single_strategy_k_vektor_weight,
    apply_single_sub_strategy_k_vektor_weight,
    k_vektor_weights_get_dict,
    save_k_vektor_weights,
)
from app.utils.db_sequence import is_pk_duplicate, sync_pg_sequence_if_needed
from app.models.process import Process, ProcessKpi
from app.models.plan_year import (
    PlanYear, KpiYearConfig,
    StrategyYearConfig, SubStrategyYearConfig, ProcessYearConfig,
)
from app.models.project import PlanProject, PlanProjectTask, PlanProjectActivity
from app.services.score_engine_service import compute_vision_score
from app.services.plan_year_service import (
    list_plan_years,
    get_plan_year,
    get_or_create_plan_year,
    close_plan_year,
    clone_plan_year,
    clone_full_plan_year,
    upsert_kpi_year_config,
    get_active_plan_year_for_user,
)
from app.models.tenant_year import TenantYearIdentity

_SP_ROLES = (
    "Admin",
    "admin",
    "tenant_admin",
    "executive_manager",
    "kurum_yoneticisi",
    "ust_yonetim",
)
from micro.modules.sp.helpers import (
    _check_sp_role,
    sp_manage_required,
    _plan_year_to_dict,
    _plan_project_to_dict,
    _plan_task_to_dict,
)

@app_bp.route("/sp/api/swot", methods=["GET"])
@login_required
def sp_api_swot_get():
    """Aktif plan year için SWOT verisini döner."""
    tid = current_user.tenant_id
    try:
        from app.models.swot import SwotAnalysis
        import json as _json
        active_py = get_active_plan_year_for_user(current_user)
        swot = None
        if active_py:
            swot = SwotAnalysis.query.filter_by(tenant_id=tid, plan_year_id=active_py.id).first()
        if not swot:
            return jsonify({"success": True, "data": {
                "strengths": [], "weaknesses": [], "opportunities": [], "threats": [],
                "plan_year_id": active_py.id if active_py else None,
                "year": active_py.year if active_py else None,
            }})
        def _parse(f):
            try: return _json.loads(f or "[]")
            except: return []
        return jsonify({"success": True, "data": {
            "id": swot.id,
            "plan_year_id": swot.plan_year_id,
            "year": active_py.year if active_py else None,
            "strengths":     _parse(swot.strengths),
            "weaknesses":    _parse(swot.weaknesses),
            "opportunities": _parse(swot.opportunities),
            "threats":       _parse(swot.threats),
            "guncelleme":    str(swot.updated_at)[:10] if swot.updated_at else None,
        }})
    except Exception as e:
        current_app.logger.error(f"[sp_api_swot_get] {e}", exc_info=True)
        return jsonify({"success": False, "message": "SWOT verisi alınamadı."}), 500


@app_bp.route("/sp/api/swot", methods=["POST"])
@login_required
@sp_manage_required
def sp_api_swot_save():
    """SWOT verisini kaydet (upsert)."""
    tid = current_user.tenant_id
    try:
        from app.models.swot import SwotAnalysis
        import json as _json
        payload = request.get_json(silent=True) or {}
        active_py = get_active_plan_year_for_user(current_user)
        if not active_py:
            return jsonify({"success": False, "message": "Aktif plan yılı bulunamadı."}), 400

        swot = SwotAnalysis.query.filter_by(tenant_id=tid, plan_year_id=active_py.id).first()
        if not swot:
            swot = SwotAnalysis(tenant_id=tid, plan_year_id=active_py.id)
            db.session.add(swot)

        swot.strengths     = _json.dumps(payload.get("strengths", []),     ensure_ascii=False)
        swot.weaknesses    = _json.dumps(payload.get("weaknesses", []),    ensure_ascii=False)
        swot.opportunities = _json.dumps(payload.get("opportunities", []), ensure_ascii=False)
        swot.threats       = _json.dumps(payload.get("threats", []),       ensure_ascii=False)
        db.session.commit()
        return jsonify({"success": True, "data": {"id": swot.id}})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_swot_save] {e}", exc_info=True)
        return jsonify({"success": False, "message": "SWOT kaydedilemedi."}), 500


@app_bp.route("/sp/api/tows", methods=["GET"])
@login_required
def sp_api_tows_get():
    """Aktif plan year için TOWS verisini döner."""
    tid = current_user.tenant_id
    try:
        from app.models.swot import TowsAnalysis
        import json as _json
        active_py = get_active_plan_year_for_user(current_user)
        tows = None
        if active_py:
            tows = TowsAnalysis.query.filter_by(tenant_id=tid, plan_year_id=active_py.id).first()
        if not tows:
            return jsonify({"success": True, "data": {
                "so": [], "st": [], "wo": [], "wt": [],
                "plan_year_id": active_py.id if active_py else None,
            }})
        def _parse(f):
            try: return _json.loads(f or "[]")
            except: return []
        return jsonify({"success": True, "data": {
            "id": tows.id,
            "plan_year_id": tows.plan_year_id,
            "so": _parse(tows.so_strategies),
            "st": _parse(tows.st_strategies),
            "wo": _parse(tows.wo_strategies),
            "wt": _parse(tows.wt_strategies),
        }})
    except Exception as e:
        current_app.logger.error(f"[sp_api_tows_get] {e}", exc_info=True)
        return jsonify({"success": False, "message": "TOWS verisi alınamadı."}), 500


@app_bp.route("/sp/api/tows", methods=["POST"])
@login_required
@sp_manage_required
def sp_api_tows_save():
    """TOWS verisini kaydet (upsert)."""
    tid = current_user.tenant_id
    try:
        from app.models.swot import TowsAnalysis
        import json as _json
        payload = request.get_json(silent=True) or {}
        active_py = get_active_plan_year_for_user(current_user)
        if not active_py:
            return jsonify({"success": False, "message": "Aktif plan yılı bulunamadı."}), 400

        tows = TowsAnalysis.query.filter_by(tenant_id=tid, plan_year_id=active_py.id).first()
        if not tows:
            tows = TowsAnalysis(tenant_id=tid, plan_year_id=active_py.id)
            db.session.add(tows)

        tows.so_strategies = _json.dumps(payload.get("so", []), ensure_ascii=False)
        tows.st_strategies = _json.dumps(payload.get("st", []), ensure_ascii=False)
        tows.wo_strategies = _json.dumps(payload.get("wo", []), ensure_ascii=False)
        tows.wt_strategies = _json.dumps(payload.get("wt", []), ensure_ascii=False)
        db.session.commit()
        return jsonify({"success": True, "data": {"id": tows.id}})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_tows_save] {e}", exc_info=True)
        return jsonify({"success": False, "message": "TOWS kaydedilemedi."}), 500


@app_bp.route("/sp/api/pestle", methods=["GET"])
@login_required
def sp_api_pestle_get():
    """Aktif plan year için PESTLE verisini döner."""
    tid = current_user.tenant_id
    try:
        from app.models.swot import PestelAnalysis
        import json as _json
        active_py = get_active_plan_year_for_user(current_user)
        pestle = None
        if active_py:
            pestle = PestelAnalysis.query.filter_by(tenant_id=tid, plan_year_id=active_py.id).first()
        empty = {"political": [], "economic": [], "social": [], "technological": [], "environmental": [], "legal": []}
        if not pestle:
            return jsonify({"success": True, "data": {**empty, "plan_year_id": active_py.id if active_py else None}})
        def _parse(f):
            try: return _json.loads(f or "[]")
            except: return []
        return jsonify({"success": True, "data": {
            "id": pestle.id,
            "plan_year_id": pestle.plan_year_id,
            "political":     _parse(pestle.political),
            "economic":      _parse(pestle.economic),
            "social":        _parse(pestle.social),
            "technological": _parse(pestle.technological),
            "environmental": _parse(pestle.environmental),
            "legal":         _parse(pestle.legal),
        }})
    except Exception as e:
        current_app.logger.error(f"[sp_api_pestle_get] {e}", exc_info=True)
        return jsonify({"success": False, "message": "PESTLE verisi alınamadı."}), 500


@app_bp.route("/sp/api/pestle", methods=["POST"])
@login_required
@sp_manage_required
def sp_api_pestle_save():
    """PESTLE verisini kaydet (upsert)."""
    tid = current_user.tenant_id
    try:
        from app.models.swot import PestelAnalysis
        import json as _json
        payload = request.get_json(silent=True) or {}
        active_py = get_active_plan_year_for_user(current_user)
        if not active_py:
            return jsonify({"success": False, "message": "Aktif plan yılı bulunamadı."}), 400

        pestle = PestelAnalysis.query.filter_by(tenant_id=tid, plan_year_id=active_py.id).first()
        if not pestle:
            pestle = PestelAnalysis(tenant_id=tid, plan_year_id=active_py.id)
            db.session.add(pestle)

        pestle.political     = _json.dumps(payload.get("political", []),     ensure_ascii=False)
        pestle.economic      = _json.dumps(payload.get("economic", []),      ensure_ascii=False)
        pestle.social        = _json.dumps(payload.get("social", []),        ensure_ascii=False)
        pestle.technological = _json.dumps(payload.get("technological", []), ensure_ascii=False)
        pestle.environmental = _json.dumps(payload.get("environmental", []), ensure_ascii=False)
        pestle.legal         = _json.dumps(payload.get("legal", []),         ensure_ascii=False)
        db.session.commit()
        return jsonify({"success": True, "data": {"id": pestle.id}})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_pestle_save] {e}", exc_info=True)
        return jsonify({"success": False, "message": "PESTLE kaydedilemedi."}), 500


# ── OKR API'leri ──────────────────────────────────────────────────────────────

@app_bp.route("/sp/api/okr/sync-kpis", methods=["POST"])
@login_required
def sp_api_okr_sync_kpis():
    """Sprint 33: Tüm bağlı KR'leri KPI'larından senkronize et."""
    from app.services.okr_kpi_sync import sync_all_krs_for_tenant
    from app.services.plan_year_service import get_active_plan_year_for_user
    py = get_active_plan_year_for_user(current_user)
    py_id = py.id if py else None
    result = sync_all_krs_for_tenant(current_user.tenant_id, plan_year_id=py_id)
    return jsonify(result)


# Sprint 13 — OKR UI sayfası
@app_bp.route("/sp/okr")
@login_required
def sp_okr():
    """OKR (Objectives + Key Results) yönetim sayfası."""
    active_py = get_active_plan_year_for_user(current_user)
    return render_template(
        "platform/sp/okr.html",
        active_year=active_py.year if active_py else None,
        active_plan_year_id=active_py.id if active_py else None,
    )


@app_bp.route("/sp/api/okr", methods=["GET"])
@login_required
def sp_api_okr_list():
    """Aktif plan year için OKR listesi."""
    tid = current_user.tenant_id
    try:
        from app.models.okr import OkrObjective, OkrKeyResult
        active_py = get_active_plan_year_for_user(current_user)
        if not active_py:
            return jsonify({"success": True, "data": [], "plan_year_id": None})

        objectives = (OkrObjective.query
                      .filter_by(tenant_id=tid, plan_year_id=active_py.id, is_active=True)
                      .order_by(OkrObjective.quarter.nullsfirst(), OkrObjective.order_no)
                      .all())

        def _obj_dict(o):
            krs = [k for k in o.key_results if k.is_active]
            avg_progress = None
            pcts = [k.progress_pct for k in krs if k.progress_pct is not None]
            if pcts:
                avg_progress = round(sum(pcts) / len(pcts), 1)
            return {
                "id":          o.id,
                "title":       o.title,
                "description": o.description,
                "quarter":     o.quarter,
                "owner":       o.owner,
                "order_no":    o.order_no,
                "avg_progress": avg_progress,
                # Sprint 17: strateji bağı
                "linked_strategy_id":     o.linked_strategy_id,
                "linked_sub_strategy_id": o.linked_sub_strategy_id,
                "linked_strategy":     (
                    {"id": o.linked_strategy.id, "code": o.linked_strategy.code, "title": o.linked_strategy.title}
                    if o.linked_strategy_id and o.linked_strategy else None
                ),
                "linked_sub_strategy": (
                    {"id": o.linked_sub_strategy.id, "code": o.linked_sub_strategy.code, "title": o.linked_sub_strategy.title}
                    if o.linked_sub_strategy_id and o.linked_sub_strategy else None
                ),
                "key_results": [{
                    "id":            k.id,
                    "title":         k.title,
                    "metric":        k.metric,
                    "start_value":   k.start_value,
                    "target_value":  k.target_value,
                    "current_value": k.current_value,
                    "progress_pct":  k.progress_pct,
                    "order_no":      k.order_no,
                } for k in krs],
            }

        return jsonify({
            "success": True,
            "data": [_obj_dict(o) for o in objectives],
            "plan_year_id": active_py.id,
            "year": active_py.year,
        })
    except Exception as e:
        current_app.logger.error(f"[sp_api_okr_list] {e}", exc_info=True)
        return jsonify({"success": False, "message": "OKR verisi alınamadı."}), 500


@app_bp.route("/sp/api/okr/objective", methods=["POST"])
@login_required
@sp_manage_required
def sp_api_okr_objective_create():
    """Yeni Objective ekle."""
    tid = current_user.tenant_id
    try:
        from app.models.okr import OkrObjective
        payload = request.get_json(silent=True) or {}
        active_py = get_active_plan_year_for_user(current_user)
        if not active_py:
            return jsonify({"success": False, "message": "Aktif plan yılı bulunamadı."}), 400
        title = (payload.get("title") or "").strip()
        if not title:
            return jsonify({"success": False, "message": "Başlık zorunludur."}), 400
        obj = OkrObjective(
            tenant_id=tid, plan_year_id=active_py.id,
            title=title,
            description=(payload.get("description") or "").strip() or None,
            quarter=payload.get("quarter") or None,
            owner=(payload.get("owner") or "").strip() or None,
            order_no=payload.get("order_no") or 0,
            # Sprint 17: strateji bağı
            linked_strategy_id=payload.get("linked_strategy_id") or None,
            linked_sub_strategy_id=payload.get("linked_sub_strategy_id") or None,
        )
        db.session.add(obj)
        db.session.commit()
        return jsonify({"success": True, "data": {"id": obj.id}})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_okr_objective_create] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Objective eklenemedi."}), 500


@app_bp.route("/sp/api/okr/objective/<int:obj_id>", methods=["PUT"])
@login_required
@sp_manage_required
def sp_api_okr_objective_update(obj_id):
    """Objective güncelle."""
    tid = current_user.tenant_id
    try:
        from app.models.okr import OkrObjective
        payload = request.get_json(silent=True) or {}
        obj = OkrObjective.query.filter_by(id=obj_id, tenant_id=tid, is_active=True).first_or_404()
        title = (payload.get("title") or "").strip()
        if not title:
            return jsonify({"success": False, "message": "Başlık zorunludur."}), 400
        obj.title       = title
        obj.description = (payload.get("description") or "").strip() or None
        obj.quarter     = payload.get("quarter") or None
        obj.owner       = (payload.get("owner") or "").strip() or None
        # Sprint 17: strateji bağı (None gönderirse temizler)
        if "linked_strategy_id" in payload:
            obj.linked_strategy_id = payload.get("linked_strategy_id") or None
        if "linked_sub_strategy_id" in payload:
            obj.linked_sub_strategy_id = payload.get("linked_sub_strategy_id") or None
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_okr_objective_update] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Güncellenemedi."}), 500


@app_bp.route("/sp/api/okr/objective/<int:obj_id>", methods=["DELETE"])
@login_required
@sp_manage_required
def sp_api_okr_objective_delete(obj_id):
    """Objective sil (soft)."""
    tid = current_user.tenant_id
    try:
        from app.models.okr import OkrObjective
        obj = OkrObjective.query.filter_by(id=obj_id, tenant_id=tid, is_active=True).first_or_404()
        obj.is_active = False
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_okr_objective_delete] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Silinemedi."}), 500


@app_bp.route("/sp/api/okr/objective/<int:obj_id>/kr", methods=["POST"])
@login_required
@sp_manage_required
def sp_api_okr_kr_create(obj_id):
    """Key Result ekle."""
    tid = current_user.tenant_id
    try:
        from app.models.okr import OkrObjective, OkrKeyResult
        payload = request.get_json(silent=True) or {}
        obj = OkrObjective.query.filter_by(id=obj_id, tenant_id=tid, is_active=True).first_or_404()
        title = (payload.get("title") or "").strip()
        if not title:
            return jsonify({"success": False, "message": "Başlık zorunludur."}), 400
        kr = OkrKeyResult(
            objective_id=obj.id,
            title=title,
            metric=(payload.get("metric") or "").strip() or None,
            start_value=payload.get("start_value"),
            target_value=payload.get("target_value"),
            current_value=payload.get("current_value"),
            order_no=payload.get("order_no") or 0,
        )
        db.session.add(kr)
        db.session.commit()
        return jsonify({"success": True, "data": {"id": kr.id}})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_okr_kr_create] {e}", exc_info=True)
        return jsonify({"success": False, "message": "KR eklenemedi."}), 500


@app_bp.route("/sp/api/okr/kr/<int:kr_id>", methods=["PUT"])
@login_required
@sp_manage_required
def sp_api_okr_kr_update(kr_id):
    """Key Result güncelle (ilerleme dahil)."""
    tid = current_user.tenant_id
    try:
        from app.models.okr import OkrKeyResult, OkrObjective
        payload = request.get_json(silent=True) or {}
        kr = (OkrKeyResult.query.join(OkrObjective)
              .filter(OkrKeyResult.id == kr_id, OkrObjective.tenant_id == tid, OkrKeyResult.is_active == True)
              .first_or_404())
        if "title" in payload:
            kr.title = (payload["title"] or "").strip() or kr.title
        if "metric" in payload:
            kr.metric = (payload["metric"] or "").strip() or None
        if "start_value" in payload:
            kr.start_value = payload["start_value"]
        if "target_value" in payload:
            kr.target_value = payload["target_value"]
        if "current_value" in payload:
            kr.current_value = payload["current_value"]
        db.session.commit()
        return jsonify({"success": True, "data": {"progress_pct": kr.progress_pct}})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_okr_kr_update] {e}", exc_info=True)
        return jsonify({"success": False, "message": "KR güncellenemedi."}), 500


@app_bp.route("/sp/api/okr/kr/<int:kr_id>", methods=["DELETE"])
@login_required
@sp_manage_required
def sp_api_okr_kr_delete(kr_id):
    """Key Result sil (soft)."""
    tid = current_user.tenant_id
    try:
        from app.models.okr import OkrKeyResult, OkrObjective
        kr = (OkrKeyResult.query.join(OkrObjective)
              .filter(OkrKeyResult.id == kr_id, OkrObjective.tenant_id == tid, OkrKeyResult.is_active == True)
              .first_or_404())
        kr.is_active = False
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_okr_kr_delete] {e}", exc_info=True)
        return jsonify({"success": False, "message": "KR silinemedi."}), 500


# ── BSC API'leri ──────────────────────────────────────────────────────────────

@app_bp.route("/sp/api/bsc", methods=["GET"])
@login_required
def sp_api_bsc_get():
    """BSC verisi: 4 perspektif × KPI'lar + strateji bağlantıları + performans."""
    tid = current_user.tenant_id
    try:
        import datetime as _dt
        from app.models.bsc import BscKpiPerspective, BSC_PERSPECTIVES
        from app.models.process import Process, ProcessKpi, KpiData
        from app.models.core import Strategy, SubStrategy
        from app.services.plan_year_service import get_active_plan_year_for_user

        active_py = get_active_plan_year_for_user(current_user)
        year = active_py.year if active_py else _dt.date.today().year
        py_id = active_py.id if active_py else None

        # Tüm aktif KPI'lar
        kpis = (
            ProcessKpi.query.join(Process)
            .filter(Process.tenant_id == tid, Process.is_active == True, ProcessKpi.is_active == True)
            .all()
        )
        kpi_map = {k.id: k for k in kpis}
        proc_map = {p.id: p for p in Process.query.filter_by(tenant_id=tid, is_active=True).all()}

        # Perspektif atamaları
        persp_rows = BscKpiPerspective.query.filter_by(tenant_id=tid, plan_year_id=py_id).all() if py_id else []
        persp_map = {r.process_kpi_id: r.perspective for r in persp_rows}

        # En son KPI verileri
        kpi_ids = [k.id for k in kpis]
        latest_data = {}
        if kpi_ids:
            rows = (
                KpiData.query
                .filter(KpiData.process_kpi_id.in_(kpi_ids), KpiData.year == year, KpiData.is_active == True)
                .order_by(KpiData.data_date.desc())
                .all()
            )
            for d in rows:
                if d.process_kpi_id not in latest_data:
                    latest_data[d.process_kpi_id] = d

        # Strateji hiyerarşisi
        strategies = Strategy.query.filter_by(tenant_id=tid, is_active=True).order_by(Strategy.code).all()
        sub_strats = SubStrategy.query.join(Strategy).filter(
            Strategy.tenant_id == tid, Strategy.is_active == True, SubStrategy.is_active == True
        ).all()
        strat_map = {s.id: s for s in strategies}
        sub_map   = {ss.id: ss for ss in sub_strats}

        def _kpi_perf(kpi_id):
            kpi = kpi_map.get(kpi_id)
            d   = latest_data.get(kpi_id)
            if not kpi or not d:
                return None
            try:
                target = float(kpi.target_value or 0)
                actual = float(d.actual_value or 0)
                if target <= 0:
                    return None
                if (kpi.direction or "Increasing") == "Decreasing":
                    return round(min(100.0, target / actual * 100), 1) if actual > 0 else 0.0
                return round(min(100.0, actual / target * 100), 1)
            except (ValueError, TypeError):
                return None

        def _kpi_dict(k):
            proc = proc_map.get(k.process_id)
            d    = latest_data.get(k.id)
            perf = _kpi_perf(k.id)
            ss   = sub_map.get(k.sub_strategy_id) if k.sub_strategy_id else None
            s    = strat_map.get(ss.strategy_id) if ss else None
            return {
                "id":             k.id,
                "code":           k.code or "",
                "name":           k.name,
                "unit":           k.unit or "",
                "target_value":   k.target_value,
                "actual_value":   d.actual_value if d else None,
                "perf_pct":       perf,
                "weight":         k.weight,
                "direction":      k.direction or "Increasing",
                "process_id":     k.process_id,
                "process_name":   proc.name if proc else "—",
                "process_code":   proc.code or "" if proc else "",
                "sub_strategy_id":    k.sub_strategy_id,
                "sub_strategy_title": ss.title if ss else None,
                "sub_strategy_code":  ss.code or "" if ss else None,
                "strategy_id":    s.id if s else None,
                "strategy_title": s.title if s else None,
                "strategy_code":  s.code or "" if s else None,
                "perspective":    persp_map.get(k.id),
            }

        # Perspektif bazlı grupla
        perspectives = {}
        unassigned   = []
        for k in kpis:
            kd = _kpi_dict(k)
            p  = persp_map.get(k.id)
            if p:
                perspectives.setdefault(p, []).append(kd)
            else:
                unassigned.append(kd)

        # Perspektif özet skorları
        def _persp_score(kpi_list):
            scores = [k["perf_pct"] for k in kpi_list if k["perf_pct"] is not None]
            return round(sum(scores) / len(scores), 1) if scores else None

        persp_summary = {}
        for key, label in BSC_PERSPECTIVES:
            items = perspectives.get(key, [])
            persp_summary[key] = {
                "label":     label,
                "kpi_count": len(items),
                "score":     _persp_score(items),
                "kpis":      items,
            }

        # Strateji haritası: Strateji → Alt Strateji → KPI'lar (perspektifle)
        strat_map_data = []
        for s in strategies:
            subs_data = []
            for ss in sub_strats:
                if ss.strategy_id != s.id:
                    continue
                ss_kpis = [_kpi_dict(k) for k in kpis if k.sub_strategy_id == ss.id]
                if not ss_kpis:
                    continue
                subs_data.append({
                    "id":    ss.id,
                    "code":  ss.code or "",
                    "title": ss.title,
                    "kpis":  ss_kpis,
                    "score": _persp_score(ss_kpis),
                })
            if subs_data:
                all_kpis = [k for ss in subs_data for k in ss["kpis"]]
                strat_map_data.append({
                    "id":    s.id,
                    "code":  s.code or "",
                    "title": s.title,
                    "score": _persp_score(all_kpis),
                    "sub_strategies": subs_data,
                })

        return jsonify({
            "success":      True,
            "year":         year,
            "plan_year_id": py_id,
            "perspectives": persp_summary,
            "unassigned":   unassigned,
            "strategy_map": strat_map_data,
            "toplam_kpi":   len(kpis),
            "atanmis_kpi":  len(kpis) - len(unassigned),
        })
    except Exception as e:
        current_app.logger.error(f"[sp_api_bsc_get] {e}", exc_info=True)
        return jsonify({"success": False, "message": "BSC verisi alınamadı."}), 500


@app_bp.route("/sp/api/bsc/assign", methods=["POST"])
@login_required
@sp_manage_required
def sp_api_bsc_assign():
    """KPI'ya perspektif ata (upsert)."""
    tid = current_user.tenant_id
    try:
        from app.models.bsc import BscKpiPerspective
        payload = request.get_json(silent=True) or {}
        kpi_id      = payload.get("kpi_id")
        perspective = (payload.get("perspective") or "").strip()
        active_py   = get_active_plan_year_for_user(current_user)
        if not active_py:
            return jsonify({"success": False, "message": "Aktif plan yılı bulunamadı."}), 400
        if not kpi_id:
            return jsonify({"success": False, "message": "kpi_id zorunludur."}), 400

        row = BscKpiPerspective.query.filter_by(
            tenant_id=tid, plan_year_id=active_py.id, process_kpi_id=kpi_id
        ).first()

        if not perspective:
            # Atamayı kaldır
            if row:
                db.session.delete(row)
                db.session.commit()
            return jsonify({"success": True, "action": "removed"})

        if row:
            row.perspective = perspective
        else:
            row = BscKpiPerspective(
                tenant_id=tid, plan_year_id=active_py.id,
                process_kpi_id=kpi_id, perspective=perspective,
            )
            db.session.add(row)
        db.session.commit()
        return jsonify({"success": True, "action": "assigned", "data": {"id": row.id}})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_bsc_assign] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Atama kaydedilemedi."}), 500


@app_bp.route("/sp/api/bsc/assign-bulk", methods=["POST"])
@login_required
@sp_manage_required
def sp_api_bsc_assign_bulk():
    """Birden fazla KPI'ya aynı anda perspektif ata."""
    tid = current_user.tenant_id
    try:
        from app.models.bsc import BscKpiPerspective
        payload     = request.get_json(silent=True) or {}
        kpi_ids     = payload.get("kpi_ids") or []
        perspective = (payload.get("perspective") or "").strip()
        active_py   = get_active_plan_year_for_user(current_user)
        if not active_py:
            return jsonify({"success": False, "message": "Aktif plan yılı bulunamadı."}), 400

        # Mevcut row'ları tek sorguda topla (N+1 önlemi)
        _existing_rows = {r.process_kpi_id: r for r in BscKpiPerspective.query.filter(
            BscKpiPerspective.tenant_id == tid,
            BscKpiPerspective.plan_year_id == active_py.id,
            BscKpiPerspective.process_kpi_id.in_(kpi_ids),
        ).all()} if kpi_ids else {}

        for kpi_id in kpi_ids:
            row = _existing_rows.get(kpi_id)
            if not perspective:
                if row:
                    db.session.delete(row)
            elif row:
                row.perspective = perspective
            else:
                db.session.add(BscKpiPerspective(
                    tenant_id=tid, plan_year_id=active_py.id,
                    process_kpi_id=kpi_id, perspective=perspective,
                ))
        db.session.commit()
        return jsonify({"success": True, "updated": len(kpi_ids)})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_bsc_assign_bulk] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Toplu atama kaydedilemedi."}), 500


@app_bp.route("/sp/api/bsc/auto-suggest", methods=["GET"])
@login_required
def sp_api_bsc_auto_suggest():
    """Atanmamış PG'ler için BSC perspektif önerileri (keyword tabanlı sınıflandırıcı)."""
    tid = current_user.tenant_id
    try:
        from app.models.bsc import BscKpiPerspective
        from app.models.process import ProcessKpi, Process
        from app.services.bsc_auto_classifier import classify

        active_py = get_active_plan_year_for_user(current_user)
        py_id = active_py.id if active_py else None

        # Atanmış kpi_id seti
        assigned_ids = set()
        if py_id:
            assigned_ids = {r.process_kpi_id for r in BscKpiPerspective.query.filter_by(
                tenant_id=tid, plan_year_id=py_id
            ).all()}

        kpis = (
            ProcessKpi.query.join(Process)
            .filter(Process.tenant_id == tid, Process.is_active == True,
                    ProcessKpi.is_active == True)
            .all()
        )
        proc_map = {p.id: p for p in Process.query.filter_by(tenant_id=tid, is_active=True).all()}

        suggestions = []
        for k in kpis:
            if k.id in assigned_ids:
                continue
            proc = proc_map.get(k.process_id)
            persp, conf, matched = classify(
                name=k.name or "", code=k.code or "",
                description=k.description or "",
                process_name=proc.name if proc else "",
                process_code=proc.code if proc else "",
            )
            suggestions.append({
                "kpi_id": k.id,
                "kpi_code": k.code or "",
                "kpi_name": k.name or "",
                "process_code": proc.code if proc else "",
                "process_name": proc.name if proc else "",
                "suggested_perspective": persp,
                "confidence": conf,
                "matched_keywords": matched,
            })

        # Güvene göre sırala (yüksek önce)
        suggestions.sort(key=lambda x: -x["confidence"])
        return jsonify({"success": True, "items": suggestions,
                        "total_unassigned": len(suggestions)})
    except Exception as e:
        current_app.logger.error(f"[sp_api_bsc_auto_suggest] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Öneri üretilemedi."}), 500


@app_bp.route("/sp/api/bsc/auto-assign", methods=["POST"])
@login_required
@sp_manage_required
def sp_api_bsc_auto_assign():
    """Yüksek güvenli önerileri toplu uygular (min_confidence parametresi ile)."""
    tid = current_user.tenant_id
    try:
        from app.models.bsc import BscKpiPerspective
        from app.models.process import ProcessKpi, Process
        from app.services.bsc_auto_classifier import classify

        payload = request.get_json(silent=True) or {}
        min_conf = int(payload.get("min_confidence", 30))

        active_py = get_active_plan_year_for_user(current_user)
        if not active_py:
            return jsonify({"success": False, "message": "Aktif plan yılı bulunamadı."}), 400

        assigned_ids = {r.process_kpi_id for r in BscKpiPerspective.query.filter_by(
            tenant_id=tid, plan_year_id=active_py.id
        ).all()}

        kpis = (
            ProcessKpi.query.join(Process)
            .filter(Process.tenant_id == tid, Process.is_active == True,
                    ProcessKpi.is_active == True)
            .all()
        )
        proc_map = {p.id: p for p in Process.query.filter_by(tenant_id=tid, is_active=True).all()}

        applied = 0
        skipped_low_conf = 0
        skipped_unclassified = 0
        for k in kpis:
            if k.id in assigned_ids:
                continue
            proc = proc_map.get(k.process_id)
            persp, conf, _ = classify(
                name=k.name or "", code=k.code or "",
                description=k.description or "",
                process_name=proc.name if proc else "",
                process_code=proc.code if proc else "",
            )
            if not persp:
                skipped_unclassified += 1
                continue
            if conf < min_conf:
                skipped_low_conf += 1
                continue
            db.session.add(BscKpiPerspective(
                tenant_id=tid, plan_year_id=active_py.id,
                process_kpi_id=k.id, perspective=persp,
            ))
            applied += 1

        db.session.commit()
        return jsonify({"success": True, "applied": applied,
                        "skipped_low_confidence": skipped_low_conf,
                        "skipped_unclassified": skipped_unclassified})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_bsc_auto_assign] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Otomatik atama yapılamadı."}), 500


@app_bp.route("/sp/api/bsc/balance", methods=["GET"])
@login_required
def sp_api_bsc_balance():
    """Tenant için BSC denge skoru (Kaplan-Norton ideal %25-%25-%25-%25)."""
    tid = current_user.tenant_id
    try:
        from app.models.bsc import BscKpiPerspective
        from app.services.bsc_auto_classifier import balance_score

        active_py = get_active_plan_year_for_user(current_user)
        py_id = active_py.id if active_py else None

        counts = {"finansal": 0, "musteri": 0, "ic_surec": 0, "ogrenme": 0}
        if py_id:
            for row in BscKpiPerspective.query.filter_by(
                tenant_id=tid, plan_year_id=py_id
            ).all():
                if row.perspective in counts:
                    counts[row.perspective] += 1

        balance_pct, shares = balance_score(counts)
        total = sum(counts.values())

        recommendations = []
        if total == 0:
            recommendations.append("Hiçbir PG perspektife atanmamış. 'Otomatik Atama' ile başlayın.")
        else:
            ideal = 25.0
            for persp_key, persp_lbl in [("finansal","Finansal"), ("musteri","Müşteri"),
                                          ("ic_surec","İç Süreç"), ("ogrenme","Öğrenme")]:
                share = shares[persp_key]
                if share < ideal - 10:
                    recommendations.append(
                        f"⚠️ {persp_lbl} perspektifi düşük (%{share}, ideal %25). "
                        f"Daha fazla PG'yi bu perspektife atamayı düşünün."
                    )
                elif share > ideal + 15:
                    recommendations.append(
                        f"⚖️ {persp_lbl} perspektifi yoğun (%{share}, ideal %25). "
                        f"Diğer perspektiflere kaydırma değerlendirilebilir."
                    )

        return jsonify({"success": True,
                        "balance_score": balance_pct,
                        "counts": counts, "shares": shares,
                        "total_assigned": total,
                        "recommendations": recommendations})
    except Exception as e:
        current_app.logger.error(f"[sp_api_bsc_balance] {e}", exc_info=True)
        return jsonify({"success": False, "message": "Denge skoru hesaplanamadı."}), 500
