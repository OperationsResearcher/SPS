"""Stratejik Planlama modülü."""

from functools import wraps

from flask import render_template, jsonify, request, current_app, session
from flask_login import login_required, current_user
from sqlalchemy.orm import selectinload

from platform_core import app_bp
from app.extensions import csrf
from app.models import db
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
from app.models.plan_year import PlanYear, KpiYearConfig
from app.services.score_engine_service import compute_vision_score
from app.services.plan_year_service import (
    list_plan_years,
    get_plan_year,
    get_or_create_plan_year,
    close_plan_year,
    clone_plan_year,
    upsert_kpi_year_config,
)

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

    strategies = (
        Strategy.query
        .options(selectinload(Strategy.sub_strategies))
        .filter_by(tenant_id=tenant_id, is_active=True)
        .order_by(Strategy.code)
        .all()
    ) if tenant_id else []

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
            bundle = compute_vision_score(tenant_id, persist_pg_scores=False)
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
        active_plan_year_obj = get_plan_year(tenant_id, active_plan_year_val)
    else:
        plan_years_list = []
        active_plan_year_val = current_cal_year
        active_plan_year_obj = None

    return render_template(
        "platform/sp/index.html",
        tenant=tenant,
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

    if request.method == "GET":
        return jsonify(k_vektor_weights_get_dict(tid))

    ok, msg = save_k_vektor_weights(tid, current_user.id, request.get_json() or {})
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
    """Tenant amaç/vizyon/değerler/etik alanları (Kurum API ile aynı alanlar)."""
    tenant = Tenant.query.filter_by(id=current_user.tenant_id).first_or_404()
    data = request.get_json() or {}
    try:
        for field in ("purpose", "vision", "core_values", "code_of_ethics", "quality_policy"):
            if field in data:
                setattr(tenant, field, data[field])
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

    def _make_strategy():
        return Strategy(
            tenant_id=tenant_id,
            title=title,
            code=(data.get("code") or "").strip() or None,
            description=(data.get("description") or "").strip() or None,
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

    def _make_sub():
        return SubStrategy(
            strategy_id=parent.id,
            title=title,
            code=(data.get("code") or "").strip() or None,
            description=(data.get("description") or "").strip() or None,
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
    strategy_count = Strategy.query.filter_by(tenant_id=tid, is_active=True).count()
    process_count = Process.query.filter_by(tenant_id=tid, is_active=True).count()
    sub_strategy_count = (
        SubStrategy.query
        .join(Strategy)
        .filter(Strategy.tenant_id == tid, SubStrategy.is_active == True)
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

    strategies = (
        Strategy.query
        .options(selectinload(Strategy.sub_strategies))
        .filter_by(tenant_id=tid, is_active=True)
        .all()
    )
    processes = Process.query.filter_by(tenant_id=tid, is_active=True).all()

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
        vision_score = compute_vision_score(tid)
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

    try:
        if from_year:
            try:
                from_year = int(from_year)
            except (TypeError, ValueError):
                return jsonify({"success": False, "message": "Geçersiz kaynak yıl."}), 400
            source_py = get_plan_year(tid, from_year)
            if not source_py:
                return jsonify({"success": False, "message": f"{from_year} yılı planı bulunamadı."}), 404
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
