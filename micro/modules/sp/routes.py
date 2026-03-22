"""Stratejik Planlama modülü."""

from functools import wraps

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user
from sqlalchemy.orm import selectinload

from micro import micro_bp
from app.extensions import csrf
from app.models import db
from app.models.core import Strategy, SubStrategy, Tenant
from app.models.strategy import SwotAnalysis
from app.models.process import Process, ProcessKpi

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


@micro_bp.route("/sp")
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

    swot_counts = {}
    if tenant_id:
        for cat in ("strength", "weakness", "opportunity", "threat"):
            swot_counts[cat] = SwotAnalysis.query.filter_by(
                tenant_id=tenant_id, category=cat, is_active=True
            ).count()

    return render_template(
        "micro/sp/index.html",
        tenant=tenant,
        strategies=strategies,
        swot_counts=swot_counts,
        sp_can_manage=_check_sp_role(),
    )


@micro_bp.route("/sp/swot")
@login_required
def sp_swot():
    """SWOT Analizi sayfası."""
    tenant_id = current_user.tenant_id
    if not tenant_id:
        return render_template("micro/sp/swot.html", items={})

    items = SwotAnalysis.query.filter_by(
        tenant_id=tenant_id, is_active=True
    ).order_by(SwotAnalysis.created_at).all()

    grouped = {
        "strength": [i for i in items if i.category == "strength"],
        "weakness": [i for i in items if i.category == "weakness"],
        "opportunity": [i for i in items if i.category == "opportunity"],
        "threat": [i for i in items if i.category == "threat"],
    }

    return render_template("micro/sp/swot.html", grouped=grouped)


@micro_bp.route("/sp/misyon")
@login_required
def sp_misyon():
    return render_template("micro/sp/misyon.html")


@micro_bp.route("/sp/vizyon")
@login_required
def sp_vizyon():
    return render_template("micro/sp/vizyon.html")


@micro_bp.route("/sp/degerler")
@login_required
def sp_degerler():
    return render_template("micro/sp/degerler.html")


# ── API: Stratejik kimlik (SP yöneticileri — Admin / kurum rolleri) ────────────

@micro_bp.route("/sp/api/tenant-identity", methods=["POST"])
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

@micro_bp.route("/sp/api/strategy/add", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_add_strategy():
    """Ana strateji ekle."""
    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"success": False, "message": "Strateji adı zorunludur."}), 400

    new_strategy = Strategy(
        tenant_id=current_user.tenant_id,
        title=title,
        code=(data.get("code") or "").strip() or None,
        description=(data.get("description") or "").strip() or None,
    )
    try:
        db.session.add(new_strategy)
        db.session.commit()
        return jsonify({"success": True, "message": "Strateji eklendi.", "id": new_strategy.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_add_strategy] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@micro_bp.route("/sp/api/strategy/update/<int:strategy_id>", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_update_strategy(strategy_id):
    """Ana strateji güncelle."""
    st = Strategy.query.filter_by(
        id=strategy_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()
    data = request.get_json() or {}
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
        db.session.commit()
        return jsonify({"success": True, "message": "Ana strateji güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_update_strategy] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


@micro_bp.route("/sp/api/strategy/delete/<int:strategy_id>", methods=["POST"])
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


@micro_bp.route("/sp/api/swot/add", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_add_swot():
    """SWOT maddesi ekle."""
    data = request.get_json() or {}
    category = (data.get("category") or "").strip()
    content = (data.get("content") or "").strip()

    if category not in ("strength", "weakness", "opportunity", "threat") or not content:
        return jsonify({"success": False, "message": "Geçersiz veri."}), 400

    item = SwotAnalysis(
        tenant_id=current_user.tenant_id,
        category=category,
        content=content,
        is_active=True,
    )
    try:
        db.session.add(item)
        db.session.commit()
        return jsonify({"success": True, "id": item.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_add_swot] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@micro_bp.route("/sp/api/swot/delete/<int:item_id>", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_delete_swot(item_id):
    """SWOT maddesi sil (soft delete)."""
    item = SwotAnalysis.query.filter_by(
        id=item_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()
    try:
        item.is_active = False
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_delete_swot] {e}")
        return jsonify({"success": False, "message": "Silme sırasında hata oluştu."}), 500


# ── API: Alt Strateji CRUD ────────────────────────────────────────────────────

@micro_bp.route("/sp/api/sub-strategy/add", methods=["POST"])
@csrf.exempt
@login_required
@sp_manage_required
def sp_add_sub_strategy():
    """Alt strateji ekle."""
    data = request.get_json() or {}
    strategy_id = data.get("strategy_id")
    title = (data.get("title") or "").strip()
    if not strategy_id or not title:
        return jsonify({"success": False, "message": "Strateji ve başlık zorunludur."}), 400

    parent = Strategy.query.filter_by(
        id=strategy_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()

    sub = SubStrategy(
        strategy_id=parent.id,
        title=title,
        code=(data.get("code") or "").strip() or None,
        description=(data.get("description") or "").strip() or None,
    )
    try:
        db.session.add(sub)
        db.session.commit()
        return jsonify({"success": True, "message": "Alt strateji eklendi.", "id": sub.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_add_sub_strategy] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@micro_bp.route("/sp/api/sub-strategy/update/<int:sub_id>", methods=["POST"])
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
    try:
        sub.title = (data.get("title") or sub.title).strip()
        sub.code = (data.get("code") or "").strip() or sub.code
        sub.description = data.get("description", sub.description)
        db.session.commit()
        return jsonify({"success": True, "message": "Alt strateji güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[sp_update_sub_strategy] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


@micro_bp.route("/sp/api/sub-strategy/delete/<int:sub_id>", methods=["POST"])
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

@micro_bp.route("/sp/flow")
@login_required
def sp_flow():
    """Stratejik planlama akış özet sayfası."""
    tid = current_user.tenant_id
    strategy_count = Strategy.query.filter_by(tenant_id=tid, is_active=True).count()
    swot_count = SwotAnalysis.query.filter_by(tenant_id=tid, is_active=True).count()
    process_count = Process.query.filter_by(tenant_id=tid, is_active=True).count()
    sub_strategy_count = (
        SubStrategy.query
        .join(Strategy)
        .filter(Strategy.tenant_id == tid, SubStrategy.is_active == True)
        .count()
    )
    tenant = current_user.tenant
    return render_template(
        "micro/sp/flow.html",
        tenant=tenant,
        strategy_count=strategy_count,
        sub_strategy_count=sub_strategy_count,
        swot_count=swot_count,
        process_count=process_count,
    )


@micro_bp.route("/sp/flow/dynamic")
@login_required
def sp_flow_dynamic():
    """İnteraktif node-edge görselleştirme sayfası."""
    return render_template("micro/sp/dynamic_flow.html")


# ── API: Graf verisi ──────────────────────────────────────────────────────────

@micro_bp.route("/sp/api/graph")
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
