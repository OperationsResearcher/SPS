"""Stratejik Planlama — SP ana sayfa ve kurumsal kimlik."""

from flask_babel import gettext as _
from datetime import date
from functools import wraps

from flask import render_template, jsonify, request, current_app, session
from flask_login import login_required, current_user
from sqlalchemy.orm import selectinload

from platform_core import app_bp
from app.extensions import csrf
from app.models import db
from app.utils.audit_logger import AuditLogger
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
    load_sp_strategies_for_user,
    build_strateji_harita_graph,
)

@app_bp.route("/k-plan/strategy/menu")
@login_required
def sp_menu():
    """Stratejik Planlama hub — alt modüller kart görünümünde."""
    return render_template("platform/sp/menu.html")


@app_bp.route("/k-plan/strategy")
@login_required
def sp():
    """Stratejik Planlama ana sayfası."""
    tenant_id = current_user.tenant_id
    tenant = current_user.tenant

    active_py = get_active_plan_year_for_user(current_user)
    strat_q = (
        Strategy.query
        .options(selectinload(Strategy.sub_strategies))
        .filter_by(tenant_id=tenant_id, is_active=True)
        .order_by(Strategy.code)
    )
    _fallback_plan_year_id = None  # Otomatik geri dönülen plan_year_id (varsa)
    if active_py:
        # Sprint 1.5: merkezi plan_year filter helper kullanımı
        from app.utils.plan_year_filter import filter_by_plan_year
        strat_q_year = filter_by_plan_year(strat_q, Strategy, active_py.id, include_null=True)
        strategies = strat_q_year.all() if tenant_id else []
        # Veri yoksa: veri olan plan year'a geri dön
        if not strategies and tenant_id:
            from sqlalchemy import func as _func
            best = (
                db.session.query(Strategy.plan_year_id, _func.count(Strategy.id).label("cnt"))
                .filter(Strategy.tenant_id == tenant_id, Strategy.is_active.is_(True),
                        Strategy.plan_year_id.isnot(None))
                .group_by(Strategy.plan_year_id)
                .order_by(_func.count(Strategy.id).desc())
                .first()
            )
            if best:
                _fallback_plan_year_id = best[0]
                strategies = strat_q.filter(Strategy.plan_year_id == best[0]).all()
    else:
        strategies = strat_q.all() if tenant_id else []
    # Uyarı: etiketlenmemiş (plan_year_id=NULL) kayıt varsa kullanıcıya göster
    has_untagged_strategies = active_py and any(s.plan_year_id is None for s in strategies)

    # Misyon/vizyon: plan_year aktifse TenantYearIdentity'den, yoksa Tenant'tan
    year_identity = None
    if active_py:
        year_identity = TenantYearIdentity.query.filter_by(
            plan_year_id=active_py.id, tenant_id=tenant_id
        ).first()

    k_vektor_enabled = bool(tenant and getattr(tenant, "k_vektor_enabled", False))

    kv_strategy_weights: dict = {}
    kv_sub_strategy_weights: dict = {}
    if tenant_id:
        kv_strategy_weights = {
            r.strategy_id: r.weight_raw
            for r in KVektorStrategyWeight.query.filter_by(tenant_id=tenant_id).all()
        }
        kv_sub_strategy_weights = {
            r.sub_strategy_id: r.weight_raw
            for r in KVektorSubStrategyWeight.query.filter_by(tenant_id=tenant_id).all()
        }

    kv_vision_bar = None
    kv_strategy_scores: dict = {}
    kv_sub_strategy_scores: dict = {}
    kv_contrib_main: dict = {}
    kv_quotas_main: dict = {}
    if tenant_id and k_vektor_enabled:
        try:
            bundle = compute_vision_score(
                tenant_id,
                year=active_py.year if active_py else None,
                persist_pg_scores=False,
                plan_year=active_py,
            )
            if bundle.get("k_vektor") and bundle.get("vision_score_1000") is not None:
                # 100 ölçeğine dönüştür (eski 1000 ölçeği / 10)
                v1000 = float(bundle["vision_score_1000"])
                v100 = min(100.0, max(0.0, v1000 / 10.0))
                as_of = bundle.get("as_of_date") or ""
                kv_vision_bar = {
                    "score": round(v100, 1),
                    "score_1000": round(v1000, 1),  # geriye dönük uyum
                    "pct": round(v100, 2),
                    "as_of": as_of,
                }
                kv_strategy_scores = dict(bundle.get("strategy_scores") or {})
                kv_sub_strategy_scores = dict(bundle.get("sub_strategy_scores") or {})
                # Quotas ve katkılar 1000 ölçeğinde geliyor → 100 ölçeğine indir
                kv_contrib_main = {
                    int(k): float(v) / 10.0
                    for k, v in (bundle.get("k_vektor_contrib_main") or {}).items()
                }
                kv_quotas_main = {
                    int(k): float(v) / 10.0
                    for k, v in (bundle.get("k_vektor_quotas_main") or {}).items()
                }
        except Exception as e:
            current_app.logger.warning(f"[sp] K-Vektör skor verisi alınamadı: {e}")

    # Plan Year: sadece tenant plan_year_enabled ise aktif
    import datetime as _dt
    current_cal_year = _dt.date.today().year
    plan_year_feature = bool(getattr(tenant, "plan_year_enabled", False)) if tenant else False
    if plan_year_feature and tenant_id:
        plan_years_list = list_plan_years(tenant_id)
        active_plan_year_val = session.get("sp_active_year", current_cal_year)
        available_years = [py.year for py in plan_years_list]
        if available_years and active_plan_year_val not in available_years:
            active_plan_year_val = available_years[0]
        # Fallback: seçili yılda veri yoksa, veri olan yılı göster
        if _fallback_plan_year_id:
            fallback_py = PlanYear.query.filter_by(
                id=_fallback_plan_year_id, tenant_id=tenant_id
            ).first()
            if fallback_py:
                active_plan_year_val = fallback_py.year
                active_plan_year_obj = fallback_py
            else:
                active_plan_year_obj = get_plan_year(tenant_id, active_plan_year_val)
        else:
            active_plan_year_obj = get_plan_year(tenant_id, active_plan_year_val)
    else:
        plan_years_list = []
        active_plan_year_val = current_cal_year
        active_plan_year_obj = None

    return render_template(
        "platform/sp/index.html",
        tenant=tenant,
        year_identity=year_identity,
        strategies=strategies,
        sp_can_manage=_check_sp_role(),
        k_vektor_enabled=k_vektor_enabled,
        kv_strategy_weights=kv_strategy_weights,
        kv_sub_strategy_weights=kv_sub_strategy_weights,
        kv_vision_bar=kv_vision_bar,
        kv_strategy_scores=kv_strategy_scores,
        kv_sub_strategy_scores=kv_sub_strategy_scores,
        kv_contrib_main=kv_contrib_main,
        kv_quotas_main=kv_quotas_main,
        plan_years=plan_years_list,
        active_plan_year=active_plan_year_obj,
        active_plan_year_val=active_plan_year_val,
        current_cal_year=current_cal_year,
        plan_year_feature=plan_year_feature,
        has_untagged_strategies=has_untagged_strategies,
        data_fallback=bool(_fallback_plan_year_id),
    )


@app_bp.route("/k-plan/strategy/api/k-vektor/weights", methods=["GET", "POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_k_vektor_weights():
    """K-Vektör ana/alt strateji ham ağırlıkları — düzenleme Stratejik Planlama (/sp) akışında."""
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": _("Tenant bulunamadı.")}), 403

    active_py = get_active_plan_year_for_user(current_user)
    if request.method == "GET":
        return jsonify(k_vektor_weights_get_dict(tid, plan_year=active_py))

    ok, msg = save_k_vektor_weights(tid, current_user.id, request.get_json() or {}, plan_year=active_py)
    if ok:
        return jsonify({"success": True, "message": _("K-Vektör ağırlıkları kaydedildi.")})
    status = 404 if msg and "bulunamadı" in msg else 400
    if msg == "Kayıt sırasında hata oluştu.":
        status = 500
    return jsonify({"success": False, "message": msg or "Kayıt başarısız."}), status


@app_bp.route("/k-plan/strategy/mission")
@login_required
def sp_misyon():
    return render_template("platform/sp/misyon.html")


@app_bp.route("/k-plan/strategy/vision")
@login_required
def sp_vizyon():
    return render_template("platform/sp/vizyon.html")


@app_bp.route("/k-plan/strategy/values")
@login_required
def sp_degerler():
    return render_template("platform/sp/degerler.html")


# ── API: Stratejik kimlik (SP yöneticileri — Admin / kurum rolleri) ────────────

@app_bp.route("/k-plan/strategy/api/tenant-identity", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_tenant_identity():
    """
    Tenant amaç/vizyon/değerler/etik alanları.
    Plan year aktifse TenantYearIdentity'e kaydeder (Tenant'a da yazar — fallback için).
    """
    tid = current_user.tenant_id
    tenant = Tenant.query.filter_by(id=tid).first_or_404()
    data = request.get_json() or {}
    fields = ("purpose", "vision", "core_values", "code_of_ethics", "quality_policy")
    try:
        # Tenant'a her zaman yaz (geriye dönük uyumluluk)
        for field in fields:
            if field in data:
                setattr(tenant, field, data[field])

        # Plan year aktifse TenantYearIdentity'e de yaz
        active_py = get_active_plan_year_for_user(current_user)
        if active_py:
            yi = TenantYearIdentity.query.filter_by(
                plan_year_id=active_py.id, tenant_id=tid
            ).first()
            if not yi:
                yi = TenantYearIdentity(plan_year_id=active_py.id, tenant_id=tid)
                db.session.add(yi)
            for field in fields:
                if field in data:
                    setattr(yi, field, data[field])

        db.session.commit()
        # Hangi kart(lar) değişti — new_values'taki anahtarlar Loglar'da etikete dönüşür.
        changed = {f: (str(data[f])[:80] if data[f] is not None else "") for f in fields if f in data}
        if changed:
            AuditLogger.log_update("Kurum Yönetimi", tid, {}, changed,
                                   description="Stratejik kimlik güncellendi")
        return jsonify({"success": True, "message": _("Stratejik kimlik güncellendi.")})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_tenant_identity] {e}")
        return jsonify({"success": False, "message": _("Güncelleme sırasında hata oluştu.")}), 500




# ── Strateji Haritası ─────────────────────────────────────────────────────────

@app_bp.route("/k-plan/strategy/strategy-map")
@login_required
def sp_strateji_haritasi():
    """Strateji → Alt Strateji → Süreç → KPI hiyerarşisi görsel haritası."""
    tid = current_user.tenant_id or getattr(current_user, "kurum_id", None)
    strategies = load_sp_strategies_for_user(current_user)
    graph = build_strateji_harita_graph(tid, strategies) if tid else {"success": True, "nodes": [], "edges": [], "meta": {}}
    meta = graph.get("meta") or {}
    return render_template(
        "platform/sp/strateji_haritasi.html",
        graph_data=graph,
        strategy_count=len(strategies),
        sub_count=meta.get("sub", 0),
        process_count=meta.get("process", 0),
        pg_count=meta.get("pg", 0),
        initiative_count=meta.get("initiative", 0),
        proje_count=meta.get("proje", 0),
    )


@app_bp.route("/k-plan/strategy/api/strategy-map")
@login_required
def sp_api_strateji_haritasi():
    """Strateji haritası için ağaç verisi döner (SP ile aynı strateji filtresi)."""
    tid = current_user.tenant_id or getattr(current_user, "kurum_id", None)
    if not tid:
        return jsonify({"success": False, "message": _("Kurum bilgisi bulunamadı."), "nodes": [], "edges": []}), 400

    strategies = load_sp_strategies_for_user(current_user)
    return jsonify(build_strateji_harita_graph(tid, strategies))


# ── Dönemsel Rapor ────────────────────────────────────────────────────────────

@app_bp.route("/k-plan/strategy/report/periodic")
@login_required
def sp_rapor_donemsel():
    """Dönemsel karşılaştırma raporunu Excel olarak indirir."""
    from services.period_report_service import generate_period_report
    from flask import send_file
    year         = request.args.get("year", date.today().year, type=int)
    compare_year = request.args.get("compare_year", type=int)
    try:
        bio = generate_period_report(current_user.tenant_id, year, compare_year)
        fname = f"kpi_raporu_{year}.xlsx"
        return send_file(
            bio,
            mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            as_attachment=True,
            download_name=fname,
        )
    except RuntimeError as e:
        return jsonify({"success": False, "message": _("Sunucu hatası oluştu.")}), 500
    except Exception as e:
        current_app.logger.error(f"[sp_rapor_donemsel] {e}", exc_info=True)
        return jsonify({"success": False, "message": _("Rapor oluşturulamadı.")}), 500
