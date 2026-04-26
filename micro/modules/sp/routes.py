"""Stratejik Planlama modülü."""

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


def _check_sp_role():
    """SP sayfasında düzenleme / silme yetkisi olan roller."""
    return current_user.role and current_user.role.name in _SP_ROLES


def sp_manage_required(f):
    """SP CRUD API uçları için merkezi yetki kontrolü (403 JSON)."""

    @wraps(f)
    def decorated(*args, **kwargs):
        if not _check_sp_role():
            return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
        return f(*args, **kwargs)

    return decorated


@app_bp.route("/sp")
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
        strat_q_year = strat_q.filter(
            or_(Strategy.plan_year_id == active_py.id, Strategy.plan_year_id == None)
        )
        strategies = strat_q_year.all() if tenant_id else []
        # Veri yoksa: veri olan plan year'a geri dön
        if not strategies and tenant_id:
            from sqlalchemy import func as _func
            best = (
                db.session.query(Strategy.plan_year_id, _func.count(Strategy.id).label("cnt"))
                .filter(Strategy.tenant_id == tenant_id, Strategy.is_active == True,
                        Strategy.plan_year_id != None)
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
                v1000 = float(bundle["vision_score_1000"])
                v1000 = min(1000.0, max(0.0, v1000))
                as_of = bundle.get("as_of_date") or ""
                kv_vision_bar = {
                    "score_1000": round(v1000, 1),
                    "pct": round((v1000 / 1000.0) * 100.0, 2),
                    "as_of": as_of,
                }
                kv_strategy_scores = dict(bundle.get("strategy_scores") or {})
                kv_sub_strategy_scores = dict(bundle.get("sub_strategy_scores") or {})
                kv_contrib_main = {
                    int(k): float(v)
                    for k, v in (bundle.get("k_vektor_contrib_main") or {}).items()
                }
                kv_quotas_main = {
                    int(k): float(v)
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


@app_bp.route("/sp/api/k-vektor/weights", methods=["GET", "POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_k_vektor_weights():
    """K-Vektör ana/alt strateji ham ağırlıkları — düzenleme Stratejik Planlama (/sp) akışında."""
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": "Tenant bulunamadı."}), 403

    active_py = get_active_plan_year_for_user(current_user)
    if request.method == "GET":
        return jsonify(k_vektor_weights_get_dict(tid, plan_year=active_py))

    ok, msg = save_k_vektor_weights(tid, current_user.id, request.get_json() or {}, plan_year=active_py)
    if ok:
        return jsonify({"success": True, "message": "K-Vektör ağırlıkları kaydedildi."})
    status = 404 if msg and "bulunamadı" in msg else 400
    if msg == "Kayıt sırasında hata oluştu.":
        status = 500
    return jsonify({"success": False, "message": msg or "Kayıt başarısız."}), status


@app_bp.route("/sp/misyon")
@login_required
def sp_misyon():
    return render_template("platform/sp/misyon.html")


@app_bp.route("/sp/vizyon")
@login_required
def sp_vizyon():
    return render_template("platform/sp/vizyon.html")


@app_bp.route("/sp/degerler")
@login_required
def sp_degerler():
    return render_template("platform/sp/degerler.html")


# ── API: Stratejik kimlik (SP yöneticileri — Admin / kurum rolleri) ────────────

@app_bp.route("/sp/api/tenant-identity", methods=["POST"])
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
        return jsonify({"success": True, "message": "Stratejik kimlik güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_tenant_identity] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


# ── API: Strateji CRUD (mevcut dashboard_bp API'lerini yeniden kullanır) ──

@app_bp.route("/sp/api/strategy/add", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_add_strategy():
    """Ana strateji ekle."""
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"success": False, "message": "Strateji adı zorunludur."}), 400

    tenant_id = current_user.tenant_id
    if not tenant_id:
        return jsonify({"success": False, "message": "Kurum (tenant) bilgisi eksik."}), 400

    active_py = get_active_plan_year_for_user(current_user)

    def _make_strategy():
        return Strategy(
            tenant_id=tenant_id,
            title=title,
            code=(data.get("code") or "").strip() or None,
            description=(data.get("description") or "").strip() or None,
            plan_year_id=active_py.id if active_py else None,
        )

    try:
        new_strategy = _make_strategy()
        db.session.add(new_strategy)
        db.session.commit()
        return jsonify({"success": True, "message": "Strateji eklendi.", "id": new_strategy.id})
    except Exception as e:
        db.session.rollback()
        if is_pk_duplicate(e, "strategies"):
            try:
                sync_pg_sequence_if_needed("strategies", "id")
                new_strategy = _make_strategy()
                db.session.add(new_strategy)
                db.session.commit()
                return jsonify({"success": True, "message": "Strateji eklendi.", "id": new_strategy.id})
            except Exception as e2:
                db.session.rollback()
                current_app.logger.error(f"[sp_add_strategy/retry] {e2}")
        current_app.logger.error(f"[sp_add_strategy] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@app_bp.route("/sp/api/strategy/update/<int:strategy_id>", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_update_strategy(strategy_id):
    """Ana strateji güncelle."""
    st = Strategy.query.filter_by(
        id=strategy_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()
    data = request.get_json() or {}
    tid = current_user.tenant_id
    tenant = Tenant.query.get(tid) if tid else None
    try:
        if "title" in data:
            t = (data.get("title") or "").strip()
            if not t:
                return jsonify({"success": False, "message": "Başlık boş olamaz."}), 400
            st.title = t
        if "code" in data:
            st.code = (data.get("code") or "").strip() or None
        if "description" in data:
            st.description = (data.get("description") or "").strip() or None
        if tenant and tenant.k_vektor_enabled and "k_vektor_weight_raw" in data:
            err = apply_single_strategy_k_vektor_weight(
                tid, current_user.id, strategy_id, data.get("k_vektor_weight_raw")
            )
            if err:
                db.session.rollback()
                return jsonify({"success": False, "message": err}), 400
        db.session.commit()
        return jsonify({"success": True, "message": "Ana strateji güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_update_strategy] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


@app_bp.route("/sp/api/strategy/delete/<int:strategy_id>", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_delete_strategy(strategy_id):
    """Ana strateji sil (soft delete)."""
    st = Strategy.query.filter_by(
        id=strategy_id, tenant_id=current_user.tenant_id
    ).first_or_404()
    try:
        st.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Strateji silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_delete_strategy] {e}")
        return jsonify({"success": False, "message": "Silme sırasında hata oluştu."}), 500


# ── API: Alt Strateji CRUD ────────────────────────────────────────────────────

@app_bp.route("/sp/api/sub-strategy/add", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_add_sub_strategy():
    """Alt strateji ekle."""
    data = request.get_json() or {}
    raw_sid = data.get("strategy_id")
    title = (data.get("title") or "").strip()
    if not raw_sid or not title:
        return jsonify({"success": False, "message": "Strateji ve başlık zorunludur."}), 400

    try:
        strategy_id = int(raw_sid)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Geçersiz strateji numarası."}), 400

    parent = Strategy.query.filter_by(
        id=strategy_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()

    active_py = get_active_plan_year_for_user(current_user)

    def _make_sub():
        return SubStrategy(
            strategy_id=parent.id,
            title=title,
            code=(data.get("code") or "").strip() or None,
            description=(data.get("description") or "").strip() or None,
            plan_year_id=active_py.id if active_py else None,
        )

    try:
        sub = _make_sub()
        db.session.add(sub)
        db.session.commit()
        return jsonify({"success": True, "message": "Alt strateji eklendi.", "id": sub.id})
    except Exception as e:
        db.session.rollback()
        if is_pk_duplicate(e, "sub_strategies"):
            try:
                sync_pg_sequence_if_needed("sub_strategies", "id")
                sub = _make_sub()
                db.session.add(sub)
                db.session.commit()
                return jsonify({"success": True, "message": "Alt strateji eklendi.", "id": sub.id})
            except Exception as e2:
                db.session.rollback()
                current_app.logger.error(f"[sp_add_sub_strategy/retry] {e2}")
        current_app.logger.error(f"[sp_add_sub_strategy] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@app_bp.route("/sp/api/sub-strategy/update/<int:sub_id>", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_update_sub_strategy(sub_id):
    """Alt strateji güncelle."""
    sub = SubStrategy.query.join(Strategy).filter(
        SubStrategy.id == sub_id,
        Strategy.tenant_id == current_user.tenant_id,
        SubStrategy.is_active == True,
    ).first_or_404()

    data = request.get_json() or {}
    tid = current_user.tenant_id
    tenant = Tenant.query.get(tid) if tid else None
    try:
        sub.title = (data.get("title") or sub.title).strip()
        sub.code = (data.get("code") or "").strip() or sub.code
        sub.description = data.get("description", sub.description)
        if tenant and tenant.k_vektor_enabled and "k_vektor_weight_raw" in data:
            err = apply_single_sub_strategy_k_vektor_weight(
                tid, current_user.id, sub_id, data.get("k_vektor_weight_raw")
            )
            if err:
                db.session.rollback()
                return jsonify({"success": False, "message": err}), 400
        db.session.commit()
        return jsonify({"success": True, "message": "Alt strateji güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_update_sub_strategy] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


@app_bp.route("/sp/api/sub-strategy/delete/<int:sub_id>", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_delete_sub_strategy(sub_id):
    """Alt strateji soft delete."""
    sub = SubStrategy.query.join(Strategy).filter(
        SubStrategy.id == sub_id,
        Strategy.tenant_id == current_user.tenant_id,
    ).first_or_404()
    try:
        sub.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Alt strateji silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_delete_sub_strategy] {e}")
        return jsonify({"success": False, "message": "Silme sırasında hata oluştu."}), 500


# ── Akış Sayfaları ────────────────────────────────────────────────────────────

@app_bp.route("/sp/flow")
@login_required
def sp_flow():
    """Stratejik planlama akış özet sayfası."""
    tid = current_user.tenant_id
    active_py = get_active_plan_year_for_user(current_user)
    strat_base = Strategy.query.filter_by(tenant_id=tid, is_active=True)
    proc_base = Process.query.filter_by(tenant_id=tid, is_active=True)
    if active_py:
        strat_base = strat_base.filter(
            or_(Strategy.plan_year_id == active_py.id, Strategy.plan_year_id == None))
        proc_base = proc_base.filter(
            or_(Process.plan_year_id == active_py.id, Process.plan_year_id == None))
    strategy_count = strat_base.count()
    process_count = proc_base.count()
    sub_strategy_count = (
        SubStrategy.query
        .join(Strategy)
        .filter(Strategy.tenant_id == tid, SubStrategy.is_active == True,
                *([or_(Strategy.plan_year_id == active_py.id, Strategy.plan_year_id == None)]
                  if active_py else []))
        .count()
    )
    tenant = current_user.tenant
    return render_template(
        "platform/sp/flow.html",
        tenant=tenant,
        strategy_count=strategy_count,
        sub_strategy_count=sub_strategy_count,
        process_count=process_count,
    )


@app_bp.route("/sp/flow/dynamic")
@login_required
def sp_flow_dynamic():
    """İnteraktif node-edge görselleştirme sayfası."""
    return render_template("platform/sp/dynamic_flow.html")


# ── API: Graf verisi ──────────────────────────────────────────────────────────

@app_bp.route("/sp/api/graph")
@login_required
def sp_api_graph():
    """Vizyon/strateji/alt-strateji/süreç/KPI node ve edge'lerini JSON döndür."""
    # Admin başka tenant'ı sorgulayabilir
    if current_user.role and current_user.role.name == "Admin":
        tid = request.args.get("tenant_id", current_user.tenant_id, type=int)
    else:
        tid = current_user.tenant_id

    tenant = Tenant.query.get_or_404(tid)

    active_py = get_active_plan_year_for_user(current_user)
    strat_q = (
        Strategy.query
        .options(selectinload(Strategy.sub_strategies))
        .filter_by(tenant_id=tid, is_active=True)
    )
    if active_py:
        strat_q = strat_q.filter(
            or_(Strategy.plan_year_id == active_py.id, Strategy.plan_year_id == None))
    strategies = strat_q.all()
    proc_q = Process.query.filter_by(tenant_id=tid, is_active=True)
    if active_py:
        proc_q = proc_q.filter(
            or_(Process.plan_year_id == active_py.id, Process.plan_year_id == None))
    processes = proc_q.all()

    nodes = []
    edges = []

    # Vizyon node
    nodes.append({"id": "vision", "label": tenant.vision or tenant.name, "type": "vision"})

    for st in strategies:
        st_node_id = f"st_{st.id}"
        nodes.append({"id": st_node_id, "label": f"{st.code or ''} {st.title}".strip(), "type": "strategy"})
        edges.append({"from": "vision", "to": st_node_id})

        for ss in st.sub_strategies:
            if not ss.is_active:
                continue
            ss_node_id = f"ss_{ss.id}"
            nodes.append({"id": ss_node_id, "label": f"{ss.code or ''} {ss.title}".strip(), "type": "sub_strategy"})
            edges.append({"from": st_node_id, "to": ss_node_id})

    for proc in processes:
        p_node_id = f"proc_{proc.id}"
        nodes.append({"id": p_node_id, "label": f"{proc.code or ''} {proc.name}".strip(), "type": "process"})
        # Süreci bağlı alt stratejilere bağla
        for link in proc.process_sub_strategy_links:
            ss_node_id = f"ss_{link.sub_strategy_id}"
            edges.append({"from": ss_node_id, "to": p_node_id})

        kpis = ProcessKpi.query.filter_by(process_id=proc.id, is_active=True).all()
        for k in kpis:
            k_node_id = f"kpi_{k.id}"
            nodes.append({"id": k_node_id, "label": k.name, "type": "kpi"})
            edges.append({"from": p_node_id, "to": k_node_id})

    try:
        from app.services.score_engine_service import compute_vision_score
        _graph_py = get_active_plan_year_for_user(current_user)
        vision_score = compute_vision_score(tid, plan_year=_graph_py)
    except Exception as e:
        current_app.logger.warning(f"[sp_api_graph] score_engine: {e}")
        vision_score = None

    return jsonify({
        "success": True,
        "nodes": nodes,
        "edges": edges,
        "vision_score": vision_score,
    })


# ═══════════════════════════════════════════════════════════════════════════════
# PLAN YEAR API — Yıllık Stratejik Plan Dönem Yönetimi
# ═══════════════════════════════════════════════════════════════════════════════

def _plan_year_to_dict(py: PlanYear) -> dict:
    return {
        "id": py.id,
        "year": py.year,
        "name": py.name or f"{py.year} Stratejik Planı",
        "status": py.status,
        "template_source_id": py.template_source_id,
        "created_at": py.created_at.isoformat() if py.created_at else None,
        "closed_at": py.closed_at.isoformat() if py.closed_at else None,
    }


@app_bp.route("/sp/api/plan-years", methods=["GET"])
@login_required
def sp_api_plan_years_list():
    """Tenant'ın tüm plan yıllarını döner."""
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": "Tenant bulunamadı."}), 403
    plan_years_list = list_plan_years(tid)
    import datetime as _dt
    active_year = session.get("sp_active_year", _dt.date.today().year)
    return jsonify({
        "success": True,
        "plan_years": [_plan_year_to_dict(py) for py in plan_years_list],
        "active_year": active_year,
    })


@app_bp.route("/sp/api/plan-years", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_plan_years_create():
    """
    Yeni plan yılı oluşturur.
    Body: {year, name (opsiyonel), from_year (opsiyonel — klonlamak için kaynak yıl)}
    """
    tid = current_user.tenant_id
    if not tid:
        return jsonify({"success": False, "message": "Tenant bulunamadı."}), 403

    data = request.get_json() or {}
    new_year = data.get("year")
    if not new_year:
        return jsonify({"success": False, "message": "Yıl zorunludur."}), 400
    try:
        new_year = int(new_year)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Geçersiz yıl değeri."}), 400

    if new_year < 2000 or new_year > 2100:
        return jsonify({"success": False, "message": "Yıl 2000-2100 aralığında olmalıdır."}), 400

    # Zaten var mı?
    existing = get_plan_year(tid, new_year)
    if existing:
        return jsonify({
            "success": False,
            "message": f"{new_year} yılı için plan zaten mevcut.",
            "plan_year": _plan_year_to_dict(existing),
        }), 409

    from_year = data.get("from_year")
    name = (data.get("name") or "").strip() or None

    plan_year_feature = bool(getattr(Tenant.query.get(tid), "plan_year_enabled", False))

    try:
        if from_year:
            try:
                from_year = int(from_year)
            except (TypeError, ValueError):
                return jsonify({"success": False, "message": "Geçersiz kaynak yıl."}), 400
            source_py = get_plan_year(tid, from_year)
            if not source_py:
                return jsonify({"success": False, "message": f"{from_year} yılı planı bulunamadı."}), 404
            # Full clone sistemi aktifse tam klon, yoksa eski overlay klon
            if plan_year_feature:
                new_py = clone_full_plan_year(source_py, new_year, name=name)
            else:
                new_py = clone_plan_year(source_py, new_year, name=name)
        else:
            new_py = get_or_create_plan_year(tid, new_year)
            if name:
                new_py.name = name
                db.session.commit()

        session["sp_active_year"] = new_py.year
        return jsonify({
            "success": True,
            "message": f"{new_year} yılı planı oluşturuldu.",
            "plan_year": _plan_year_to_dict(new_py),
        })
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_plan_years_create] {e}")
        return jsonify({"success": False, "message": "Plan yılı oluşturulurken hata oluştu."}), 500


@app_bp.route("/sp/api/plan-years/set-active", methods=["POST"])
@csrf.exempt
@login_required
def sp_api_plan_years_set_active():
    """Aktif plan yılını session'a yazar."""
    data = request.get_json() or {}
    year = data.get("year")
    try:
        year = int(year)
    except (TypeError, ValueError):
        return jsonify({"success": False, "message": "Geçersiz yıl."}), 400

    tid = current_user.tenant_id
    if tid:
        py = get_plan_year(tid, year)
        if not py:
            # Plan yoksa oluştur (yeni tenant için kolay başlangıç)
            py = get_or_create_plan_year(tid, year)
    session["sp_active_year"] = year
    return jsonify({"success": True, "active_year": year})


@app_bp.route("/sp/api/plan-years/<int:year_id>/close", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_plan_year_close(year_id):
    """Plan yılını kapatır (status=closed)."""
    tid = current_user.tenant_id
    py = PlanYear.query.filter_by(id=year_id, tenant_id=tid).first_or_404()
    if py.status == "closed":
        return jsonify({"success": False, "message": "Bu yıl zaten kapalı."}), 400
    try:
        close_plan_year(py, actor_id=current_user.id)
        return jsonify({
            "success": True,
            "message": f"{py.year} yılı kapatıldı.",
            "plan_year": _plan_year_to_dict(py),
        })
    except Exception as e:
        current_app.logger.error(f"[sp_api_plan_year_close] {e}")
        return jsonify({"success": False, "message": "Yıl kapatılırken hata oluştu."}), 500


@app_bp.route("/sp/api/plan-years/<int:year_id>/kpi-configs", methods=["GET"])
@login_required
def sp_api_plan_year_kpi_configs(year_id):
    """Bir plan yılına ait tüm KPI konfigürasyonlarını döner."""
    tid = current_user.tenant_id
    py = PlanYear.query.filter_by(id=year_id, tenant_id=tid).first_or_404()
    cfgs = KpiYearConfig.query.filter_by(plan_year_id=py.id).all()
    return jsonify({
        "success": True,
        "year": py.year,
        "kpi_configs": [
            {
                "id": c.id,
                "process_kpi_id": c.process_kpi_id,
                "target_value": c.target_value,
                "unit": c.unit,
                "period": c.period,
                "direction": c.direction,
                "target_method": c.target_method,
                "calculation_method": c.calculation_method,
                "basari_puani_araliklari": c.basari_puani_araliklari,
                "onceki_yil_ortalamasi": c.onceki_yil_ortalamasi,
                "weight": c.weight,
                "is_included": c.is_included,
            }
            for c in cfgs
        ],
    })


@app_bp.route("/sp/api/plan-years/<int:year_id>/kpi-configs/<int:kpi_id>", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_plan_year_kpi_config_upsert(year_id, kpi_id):
    """Tek KPI için yıllık config güncelle/oluştur."""
    tid = current_user.tenant_id
    py = PlanYear.query.filter_by(id=year_id, tenant_id=tid).first_or_404()
    if py.status == "closed":
        return jsonify({"success": False, "message": "Kapalı plan yılı düzenlenemez."}), 400

    data = request.get_json() or {}
    try:
        cfg = upsert_kpi_year_config(py, kpi_id, data)
        return jsonify({"success": True, "id": cfg.id, "message": "KPI yıllık hedef güncellendi."})
    except ValueError as ve:
        return jsonify({"success": False, "message": str(ve)}), 404
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_plan_year_kpi_config_upsert] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@app_bp.route("/sp/api/plan-years/<int:year_id>/kpi-configs/bulk", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_plan_year_kpi_configs_bulk(year_id):
    """
    Birden fazla KPI için yıllık config toplu güncelle.
    Body: {"configs": [{"kpi_id": 1, "target_value": "30", ...}, ...]}
    """
    tid = current_user.tenant_id
    py = PlanYear.query.filter_by(id=year_id, tenant_id=tid).first_or_404()
    if py.status == "closed":
        return jsonify({"success": False, "message": "Kapalı plan yılı düzenlenemez."}), 400

    data = request.get_json() or {}
    configs = data.get("configs", [])
    if not configs:
        return jsonify({"success": False, "message": "Konfigürasyon listesi boş."}), 400

    updated = 0
    errors = []
    for item in configs:
        kpi_id = item.get("kpi_id")
        if not kpi_id:
            continue
        try:
            upsert_kpi_year_config(py, int(kpi_id), item)
            updated += 1
        except Exception as e:
            errors.append({"kpi_id": kpi_id, "error": str(e)})

    if errors:
        db.session.rollback()
        return jsonify({"success": False, "message": "Bazı kayıtlarda hata oluştu.", "errors": errors}), 400

    return jsonify({"success": True, "message": f"{updated} KPI hedefi güncellendi.", "updated": updated})


# ── SP Projeler ───────────────────────────────────────────────────────────────

@app_bp.route("/sp/donemler")
@login_required
def sp_donemler():
    """SP Dönem yönetimi sayfası."""
    import datetime as _dt
    tenant = current_user.tenant
    tenant_id = current_user.tenant_id
    plan_year_feature = bool(getattr(tenant, "plan_year_enabled", False)) if tenant else False
    current_cal_year = _dt.date.today().year

    if plan_year_feature and tenant_id:
        plan_years_list = list_plan_years(tenant_id)
        active_plan_year_val = session.get("sp_active_year", current_cal_year)
        available_years = [py.year for py in plan_years_list]
        if available_years and active_plan_year_val not in available_years:
            active_plan_year_val = available_years[0]
        active_plan_year_obj = get_plan_year(tenant_id, active_plan_year_val)
    else:
        plan_years_list = []
        active_plan_year_val = current_cal_year
        active_plan_year_obj = None

    return render_template(
        "platform/sp/donemler.html",
        plan_year_feature=plan_year_feature,
        plan_years=plan_years_list,
        active_plan_year=active_plan_year_obj,
        active_plan_year_val=active_plan_year_val,
        current_cal_year=current_cal_year,
        sp_can_manage=_check_sp_role(),
    )


@app_bp.route("/sp/api/donem-karsilastir", methods=["GET"])
@login_required
def sp_api_donem_karsilastir():
    """İki stratejik plan dönemini karşılaştırır ve farkları döner."""
    tid = current_user.tenant_id
    y1 = request.args.get("y1", type=int)
    y2 = request.args.get("y2", type=int)

    if not y1 or not y2:
        return jsonify({"success": False, "message": "İki dönem yılı gerekli (y1, y2)."}), 400
    if y1 == y2:
        return jsonify({"success": False, "message": "Aynı dönemi karşılaştıramazsınız."}), 400

    py1 = get_plan_year(tid, y1)
    py2 = get_plan_year(tid, y2)

    if not py1:
        return jsonify({"success": False, "message": f"{y1} dönemi bulunamadı."}), 404
    if not py2:
        return jsonify({"success": False, "message": f"{y2} dönemi bulunamadı."}), 404

    def _status_label(s):
        return {"active": "Aktif", "closed": "Kapalı", "draft": "Taslak", "archived": "Arşiv"}.get(s, s or "—")

    def _fmt_date(dt):
        return dt.strftime("%d.%m.%Y") if dt else "—"

    # ── Meta karşılaştırması ───────────────────────────────────────────────────
    meta_diffs = []
    meta_fields = [
        ("Ad",           py1.name or f"{py1.year} Stratejik Planı", py2.name or f"{py2.year} Stratejik Planı"),
        ("Durum",        _status_label(py1.status),                  _status_label(py2.status)),
        ("Oluşturulma",  _fmt_date(py1.created_at),                  _fmt_date(py2.created_at)),
        ("Kapanış",      _fmt_date(py1.closed_at),                   _fmt_date(py2.closed_at)),
    ]
    for field, v1, v2 in meta_fields:
        meta_diffs.append({"field": field, "y1": v1, "y2": v2, "changed": v1 != v2})

    # ── Yardımcı: source_id eşleştirmesi ─────────────────────────────────────
    def _match_pairs(items1, items2, src_attr):
        """
        Full Clone mimarisinde iki yılın kayıtlarını source_*_id ile eşleştirir.
        Döner: [(item1_or_None, item2_or_None), ...]
        """
        by_id1 = {x.id: x for x in items1}
        by_id2 = {x.id: x for x in items2}
        matched1, matched2 = set(), set()
        pairs = []

        # Y2 → Y1 yönü (Y2 klonlandıysa Y1'den)
        for x2 in items2:
            src = getattr(x2, src_attr, None)
            if src and src in by_id1:
                pairs.append((by_id1[src], x2))
                matched1.add(by_id1[src].id)
                matched2.add(x2.id)

        # Y1 → Y2 yönü (Y1 klonlandıysa Y2'den — ters sıra)
        for x1 in items1:
            if x1.id in matched1:
                continue
            src = getattr(x1, src_attr, None)
            if src and src in by_id2 and by_id2[src].id not in matched2:
                pairs.append((x1, by_id2[src]))
                matched1.add(x1.id)
                matched2.add(by_id2[src].id)

        # Ortak kaynak varsa (ikisi de aynı atadan)
        src_to_x1 = {}
        for x1 in items1:
            if x1.id in matched1:
                continue
            src = getattr(x1, src_attr, None)
            if src:
                src_to_x1[src] = x1
        for x2 in items2:
            if x2.id in matched2:
                continue
            src = getattr(x2, src_attr, None)
            if src and src in src_to_x1:
                x1 = src_to_x1[src]
                pairs.append((x1, x2))
                matched1.add(x1.id)
                matched2.add(x2.id)

        # Sadece Y1'de olanlar
        for x1 in items1:
            if x1.id not in matched1:
                pairs.append((x1, None))

        # Sadece Y2'de olanlar
        for x2 in items2:
            if x2.id not in matched2:
                pairs.append((None, x2))

        # Legacy/overlay kayıtlar: iki yılda da aynı fiziksel satır (aynı id) kullanılmış olabilir.
        # Böyle durumlarda aynı id'leri eşleştirip yalancı "sadece Y1/Y2" farkını önle.
        if pairs:
            only_1 = [a for a, b in pairs if a is not None and b is None]
            only_2 = [b for a, b in pairs if a is None and b is not None]
            by_id_only_2 = {x.id: x for x in only_2}
            repacked = []
            used_2 = set()
            for a, b in pairs:
                if a is not None and b is None and a.id in by_id_only_2:
                    b2 = by_id_only_2[a.id]
                    repacked.append((a, b2))
                    used_2.add(b2.id)
                elif a is None and b is not None and b.id in used_2:
                    continue
                else:
                    repacked.append((a, b))
            pairs = repacked

        return pairs

    # ── Strateji karşılaştırması (strategies tablosu, plan_year_id ile) ──────
    from app.models.core import Strategy as _Strategy, SubStrategy as _SubStrategy
    from app.models.process import Process as _Process, ProcessKpi as _ProcessKpi

    strats1 = _Strategy.query.filter_by(tenant_id=tid, plan_year_id=py1.id, is_active=True).all()
    strats2 = _Strategy.query.filter_by(tenant_id=tid, plan_year_id=py2.id, is_active=True).all()

    strategy_diffs = []
    for s1, s2 in _match_pairs(strats1, strats2, "source_strategy_id"):
        only_in_y1 = s2 is None
        only_in_y2 = s1 is None
        title = (s1 or s2).title
        changed_fields = []
        if s1 and s2:
            if (s1.title or "") != (s2.title or ""):
                changed_fields.append(("Başlık", s1.title or "—", s2.title or "—"))
            if (s1.code or "") != (s2.code or ""):
                changed_fields.append(("Kod", s1.code or "—", s2.code or "—"))
            if (s1.description or "").strip() != (s2.description or "").strip():
                changed_fields.append(("Açıklama", "değişti", "değişti"))
        changed = only_in_y1 or only_in_y2 or bool(changed_fields)
        strategy_diffs.append({
            "title": title,
            "only_in_y1": only_in_y1,
            "only_in_y2": only_in_y2,
            "changed_fields": changed_fields,
            "y1": {"code": s1.code if s1 else None, "title": s1.title if s1 else None},
            "y2": {"code": s2.code if s2 else None, "title": s2.title if s2 else None},
            "changed": changed,
        })

    # ── Alt strateji karşılaştırması ──────────────────────────────────────────
    # Y1/Y2 stratejilerinden alt stratejilere ulaş
    s1_ids = [s.id for s in strats1]
    s2_ids = [s.id for s in strats2]

    ss1 = (_SubStrategy.query
           .filter(_SubStrategy.strategy_id.in_(s1_ids), _SubStrategy.is_active == True)
           .all()) if s1_ids else []
    ss2 = (_SubStrategy.query
           .filter(_SubStrategy.strategy_id.in_(s2_ids), _SubStrategy.is_active == True)
           .all()) if s2_ids else []

    ss_diffs = []
    for s1, s2 in _match_pairs(ss1, ss2, "source_sub_strategy_id"):
        only_in_y1 = s2 is None
        only_in_y2 = s1 is None
        title = (s1 or s2).title
        changed_fields = []
        if s1 and s2:
            if (s1.title or "") != (s2.title or ""):
                changed_fields.append(("Başlık", s1.title or "—", s2.title or "—"))
            if (s1.code or "") != (s2.code or ""):
                changed_fields.append(("Kod", s1.code or "—", s2.code or "—"))
            if (s1.description or "").strip() != (s2.description or "").strip():
                changed_fields.append(("Açıklama", "değişti", "değişti"))
        changed = only_in_y1 or only_in_y2 or bool(changed_fields)
        ss_diffs.append({
            "title": title,
            "only_in_y1": only_in_y1,
            "only_in_y2": only_in_y2,
            "changed_fields": changed_fields,
            "y1": {"code": s1.code if s1 else None, "title": s1.title if s1 else None},
            "y2": {"code": s2.code if s2 else None, "title": s2.title if s2 else None},
            "changed": changed,
        })

    # ── Süreç + KPI karşılaştırması (süreç bazında gruplu) ───────────────────
    # Legacy uyumluluk: plan_year_id NULL süreçler iki yıl için de ortak taban kabul edilir.
    procs1 = _Process.query.filter(
        _Process.tenant_id == tid,
        _Process.is_active == True,
        or_(_Process.plan_year_id == py1.id, _Process.plan_year_id == None),
    ).all()
    procs2 = _Process.query.filter(
        _Process.tenant_id == tid,
        _Process.is_active == True,
        or_(_Process.plan_year_id == py2.id, _Process.plan_year_id == None),
    ).all()

    # KPI karşılaştırmasında process_kpi.plan_year_id dolu olmayan legacy kayıtlar da dikkate alınmalı.
    p1_ids = [p.id for p in procs1]
    p2_ids = [p.id for p in procs2]
    kpis1_all = (
        _ProcessKpi.query
        .filter(_ProcessKpi.process_id.in_(p1_ids), _ProcessKpi.is_active == True)
        .all()
    ) if p1_ids else []
    kpis2_all = (
        _ProcessKpi.query
        .filter(_ProcessKpi.process_id.in_(p2_ids), _ProcessKpi.is_active == True)
        .all()
    ) if p2_ids else []

    # Yıllık KPI config'leri (is_included/weight/target vb.) karşılaştırmaya dahil et.
    all_kpi_ids = list({k.id for k in (kpis1_all + kpis2_all)})
    cfg1_map = {}
    cfg2_map = {}
    if all_kpi_ids:
        cfg1_map = {
            c.process_kpi_id: c
            for c in KpiYearConfig.query.filter(
                KpiYearConfig.plan_year_id == py1.id,
                KpiYearConfig.process_kpi_id.in_(all_kpi_ids),
            ).all()
        }
        cfg2_map = {
            c.process_kpi_id: c
            for c in KpiYearConfig.query.filter(
                KpiYearConfig.plan_year_id == py2.id,
                KpiYearConfig.process_kpi_id.in_(all_kpi_ids),
            ).all()
        }

    kpis1_by_proc = {}
    for k in kpis1_all:
        kpis1_by_proc.setdefault(k.process_id, []).append(k)
    kpis2_by_proc = {}
    for k in kpis2_all:
        kpis2_by_proc.setdefault(k.process_id, []).append(k)

    def _kpi_diff(k1, k2):
        only_in_y1 = k2 is None
        only_in_y2 = k1 is None
        title = (k1 or k2).name
        changed_fields = []
        if k1 and k2:
            cfg1 = cfg1_map.get(k1.id)
            cfg2 = cfg2_map.get(k2.id)

            t1 = cfg1.target_value if (cfg1 and cfg1.target_value is not None) else k1.target_value
            t2 = cfg2.target_value if (cfg2 and cfg2.target_value is not None) else k2.target_value
            if (t1 or "") != (t2 or ""):
                changed_fields.append(("Hedef", t1 or "—", t2 or "—"))

            u1 = cfg1.unit if (cfg1 and cfg1.unit is not None) else k1.unit
            u2 = cfg2.unit if (cfg2 and cfg2.unit is not None) else k2.unit
            if (u1 or "") != (u2 or ""):
                changed_fields.append(("Birim", u1 or "—", u2 or "—"))

            d1 = cfg1.direction if (cfg1 and cfg1.direction is not None) else k1.direction
            d2 = cfg2.direction if (cfg2 and cfg2.direction is not None) else k2.direction
            if (d1 or "") != (d2 or ""):
                changed_fields.append(("Yön", d1 or "—", d2 or "—"))

            p1 = cfg1.period if (cfg1 and cfg1.period is not None) else k1.period
            p2 = cfg2.period if (cfg2 and cfg2.period is not None) else k2.period
            if (p1 or "") != (p2 or ""):
                changed_fields.append(("Periyot", p1 or "—", p2 or "—"))

            w1 = cfg1.weight if (cfg1 and cfg1.weight is not None) else (k1.weight or 0)
            w2 = cfg2.weight if (cfg2 and cfg2.weight is not None) else (k2.weight or 0)
            if abs(round(w1 or 0, 3) - round(w2 or 0, 3)) > 0.001:
                changed_fields.append(("Ağırlık", str(w1), str(w2)))

            inc1 = cfg1.is_included if cfg1 is not None else True
            inc2 = cfg2.is_included if cfg2 is not None else True
            if bool(inc1) != bool(inc2):
                changed_fields.append(("Plana Dahil", "Evet" if inc1 else "Hayır", "Evet" if inc2 else "Hayır"))

            if (k1.name or "") != (k2.name or ""):
                changed_fields.append(("Ad", k1.name or "—", k2.name or "—"))
        return {
            "title": title,
            "only_in_y1": only_in_y1,
            "only_in_y2": only_in_y2,
            "changed_fields": changed_fields,
            "changed": only_in_y1 or only_in_y2 or bool(changed_fields),
        }

    process_diffs = []
    for p1, p2 in _match_pairs(procs1, procs2, "source_process_id"):
        only_in_y1 = p2 is None
        only_in_y2 = p1 is None
        title = (p1 or p2).name
        changed_fields = []
        if p1 and p2:
            if (p1.name or "") != (p2.name or ""):
                changed_fields.append(("Ad", p1.name or "—", p2.name or "—"))
            if (p1.code or "") != (p2.code or ""):
                changed_fields.append(("Kod", p1.code or "—", p2.code or "—"))
            if abs(round(p1.weight or 0, 3) - round(p2.weight or 0, 3)) > 0.001:
                changed_fields.append(("Ağırlık", str(p1.weight), str(p2.weight)))
            if (p1.status or "") != (p2.status or ""):
                changed_fields.append(("Durum", p1.status or "—", p2.status or "—"))

        # Bu sürece ait KPI çiftlerini eşleştir
        p1_kpis = kpis1_by_proc.get(p1.id, []) if p1 else []
        p2_kpis = kpis2_by_proc.get(p2.id, []) if p2 else []
        kpi_diffs = [_kpi_diff(k1, k2) for k1, k2 in _match_pairs(p1_kpis, p2_kpis, "source_kpi_id")]

        proc_changed = only_in_y1 or only_in_y2 or bool(changed_fields) or any(k["changed"] for k in kpi_diffs)
        process_diffs.append({
            "title": title,
            "only_in_y1": only_in_y1,
            "only_in_y2": only_in_y2,
            "changed_fields": changed_fields,
            "kpis": kpi_diffs,
            "changed": proc_changed,
        })

    # ── Kimlik alanları karşılaştırması (Misyon, Vizyon, Değerler…) ────────────
    from app.models.tenant_year import TenantYearIdentity
    ident1 = TenantYearIdentity.query.filter_by(plan_year_id=py1.id).first()
    ident2 = TenantYearIdentity.query.filter_by(plan_year_id=py2.id).first()

    _IDENTITY_FIELDS = [
        ("Misyon / Amaç",    "purpose"),
        ("Vizyon",           "vision"),
        ("Değerler",         "core_values"),
        ("Etik Kurallar",    "code_of_ethics"),
        ("Kalite Politikası","quality_policy"),
    ]
    identity_diffs = []
    for label, attr in _IDENTITY_FIELDS:
        v1 = getattr(ident1, attr, None) if ident1 else None
        v2 = getattr(ident2, attr, None) if ident2 else None
        v1 = v1.strip() if v1 else None
        v2 = v2.strip() if v2 else None
        changed = (bool(v1) != bool(v2)) or (v1 or "") != (v2 or "")
        identity_diffs.append({
            "field": label,
            "y1_filled": bool(v1),
            "y2_filled": bool(v2),
            "y1_preview": v1[:150] if v1 else None,
            "y2_preview": v2[:150] if v2 else None,
            "changed": changed,
        })

    def _count_changed(lst):
        return sum(1 for x in lst if x["changed"])

    return jsonify({
        "success": True,
        "y1": _plan_year_to_dict(py1),
        "y2": _plan_year_to_dict(py2),
        "summary": {
            "identity_changed": _count_changed(identity_diffs),
            "meta_changed": sum(1 for m in meta_diffs if m["changed"]),
            "strategies_changed": _count_changed(strategy_diffs),
            "sub_strategies_changed": _count_changed(ss_diffs),
            "processes_changed": sum(1 for p in process_diffs if p["changed"]),
            "kpis_changed": sum(1 for p in process_diffs for k in p["kpis"] if k["changed"]),
        },
        "diff": {
            "identity": identity_diffs,
            "meta": meta_diffs,
            "strategies": strategy_diffs,
            "sub_strategies": ss_diffs,
            "processes": process_diffs,
        },
    })


@app_bp.route("/sp/api/proje", methods=["GET"])
@login_required
def sp_api_proje_list():
    """Aktif dönemin projelerini listeler."""
    py, err = _require_plan_year()
    if err:
        return err
    items = PlanProject.query.filter_by(
        tenant_id=current_user.tenant_id,
        plan_year_id=py.id,
        is_active=True,
    ).order_by(PlanProject.id).all()
    return jsonify({"success": True, "items": [_plan_project_to_dict(p) for p in items]})


@app_bp.route("/sp/api/proje", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_proje_save():
    """Proje ekle veya güncelle."""
    py, err = _require_plan_year()
    if err:
        return err
    data = request.get_json() or {}
    item_id = data.get("id")
    try:
        if item_id:
            obj = PlanProject.query.filter_by(
                id=item_id, tenant_id=current_user.tenant_id
            ).first_or_404()
        else:
            obj = PlanProject(tenant_id=current_user.tenant_id, plan_year_id=py.id)
            db.session.add(obj)
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"success": False, "message": "Proje adı zorunludur."}), 400
        obj.name        = name
        obj.description = data.get("description", obj.description)
        obj.status      = data.get("status", obj.status) or "Planlandı"
        obj.progress    = _try_int(data.get("progress")) if data.get("progress") is not None else obj.progress
        if data.get("start_date"):
            from datetime import datetime as _dt
            obj.start_date = _dt.strptime(data["start_date"], "%Y-%m-%d").date()
        if data.get("end_date"):
            from datetime import datetime as _dt
            obj.end_date = _dt.strptime(data["end_date"], "%Y-%m-%d").date()
        db.session.commit()
        return jsonify({"success": True, "message": "Proje kaydedildi.", "id": obj.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_proje_save] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@app_bp.route("/sp/api/proje/<int:item_id>", methods=["DELETE"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_proje_delete(item_id):
    obj = PlanProject.query.filter_by(
        id=item_id, tenant_id=current_user.tenant_id
    ).first_or_404()
    try:
        obj.is_active = False
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_proje_delete] {e}")
        return jsonify({"success": False, "message": "Silme hatası."}), 500


# ── Proje Görevleri ────────────────────────────────────────────────────────────

@app_bp.route("/sp/api/proje/<int:project_id>/gorev", methods=["GET"])
@login_required
def sp_api_proje_gorev_list(project_id):
    proj = PlanProject.query.filter_by(
        id=project_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()
    items = PlanProjectTask.query.filter_by(
        project_id=proj.id, is_active=True
    ).order_by(PlanProjectTask.id).all()
    return jsonify({"success": True, "items": [_plan_task_to_dict(t) for t in items]})


@app_bp.route("/sp/api/proje/<int:project_id>/gorev", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_proje_gorev_save(project_id):
    proj = PlanProject.query.filter_by(
        id=project_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()
    data = request.get_json() or {}
    item_id = data.get("id")
    try:
        if item_id:
            obj = PlanProjectTask.query.filter_by(
                id=item_id, project_id=proj.id
            ).first_or_404()
        else:
            obj = PlanProjectTask(
                project_id=proj.id,
                plan_year_id=proj.plan_year_id,
            )
            db.session.add(obj)
        name = (data.get("name") or "").strip()
        if not name:
            return jsonify({"success": False, "message": "Görev adı zorunludur."}), 400
        obj.name        = name
        obj.description = data.get("description", obj.description)
        obj.status      = data.get("status", obj.status) or "Planlandı"
        obj.assignee_id = data.get("assignee_id") or obj.assignee_id
        if data.get("start_date"):
            from datetime import datetime as _dt
            obj.start_date = _dt.strptime(data["start_date"], "%Y-%m-%d").date()
        if data.get("end_date"):
            from datetime import datetime as _dt
            obj.end_date = _dt.strptime(data["end_date"], "%Y-%m-%d").date()
        db.session.commit()
        return jsonify({"success": True, "message": "Görev kaydedildi.", "id": obj.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_proje_gorev_save] {e}")
        return jsonify({"success": False, "message": "Kayıt hatası."}), 500


@app_bp.route("/sp/api/proje/gorev/<int:task_id>", methods=["DELETE"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_api_proje_gorev_delete(task_id):
    obj = PlanProjectTask.query.filter_by(id=task_id).first_or_404()
    proj = PlanProject.query.filter_by(
        id=obj.project_id, tenant_id=current_user.tenant_id
    ).first_or_404()
    try:
        obj.is_active = False
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_api_proje_gorev_delete] {e}")
        return jsonify({"success": False, "message": "Silme hatası."}), 500


# ── Yardımcılar ────────────────────────────────────────────────────────────────

def _plan_project_to_dict(p):
    return {
        "id": p.id,
        "name": p.name,
        "description": p.description,
        "status": p.status,
        "progress": p.progress,
        "start_date": str(p.start_date) if p.start_date else None,
        "end_date": str(p.end_date) if p.end_date else None,
        "plan_year_id": p.plan_year_id,
    }


def _plan_task_to_dict(t):
    return {
        "id": t.id,
        "name": t.name,
        "description": t.description,
        "status": t.status,
        "assignee_id": t.assignee_id,
        "start_date": str(t.start_date) if t.start_date else None,
        "end_date": str(t.end_date) if t.end_date else None,
    }



# ── Stratejik Analiz API'leri (SWOT / TOWS / PESTLE) ─────────────────────────

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

        for kpi_id in kpi_ids:
            row = BscKpiPerspective.query.filter_by(
                tenant_id=tid, plan_year_id=active_py.id, process_kpi_id=kpi_id
            ).first()
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
