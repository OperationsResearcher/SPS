"""Stratejik Planlama modülü."""

from functools import wraps

from flask import render_template, jsonify, request, current_app
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
from app.services.score_engine_service import compute_vision_score

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
