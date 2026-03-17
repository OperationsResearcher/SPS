"""Kurum Paneli modülü."""

from flask import render_template, jsonify, request, current_app
from flask_login import login_required, current_user

from micro import micro_bp
from app.models import db
from app.models.core import Strategy, SubStrategy, Tenant, User
from app.models.process import Process

_KURUM_ROLES = ("tenant_admin", "executive_manager")


def _check_kurum_role():
    return current_user.role and current_user.role.name in _KURUM_ROLES


# ── Sayfa ─────────────────────────────────────────────────────────────────────

@micro_bp.route("/kurum")
@login_required
def kurum():
    """Kurum Paneli ana sayfası."""
    if not _check_kurum_role():
        return render_template("micro/errors/403.html"), 403

    tid = current_user.tenant_id
    tenant = current_user.tenant

    user_count    = User.query.filter_by(tenant_id=tid, is_active=True).count()
    process_count = Process.query.filter_by(tenant_id=tid, is_active=True).count()
    strategy_count = Strategy.query.filter_by(tenant_id=tid, is_active=True).count()

    strategies = (
        Strategy.query
        .filter_by(tenant_id=tid, is_active=True)
        .order_by(Strategy.code)
        .all()
    )

    return render_template(
        "micro/kurum/index.html",
        tenant=tenant,
        user_count=user_count,
        process_count=process_count,
        strategy_count=strategy_count,
        strategies=strategies,
    )


# ── API: Stratejik Kimlik ─────────────────────────────────────────────────────

@micro_bp.route("/kurum/api/update-strategy", methods=["POST"])
@login_required
def kurum_api_update_strategy():
    """Stratejik kimlik alanlarını güncelle (purpose, vision, core_values, ...)."""
    if not _check_kurum_role():
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403

    tenant = Tenant.query.get_or_404(current_user.tenant_id)
    data = request.get_json() or {}
    try:
        for field in ("purpose", "vision", "core_values", "code_of_ethics", "quality_policy"):
            if field in data:
                setattr(tenant, field, data[field])
        db.session.commit()
        return jsonify({"success": True, "message": "Stratejik kimlik güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[kurum_api_update_strategy] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


# ── API: Ana Strateji CRUD ────────────────────────────────────────────────────

@micro_bp.route("/kurum/api/add-strategy", methods=["POST"])
@login_required
def kurum_api_add_strategy():
    if not _check_kurum_role():
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403

    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"success": False, "message": "Başlık zorunludur."}), 400

    st = Strategy(
        tenant_id=current_user.tenant_id,
        title=title,
        code=(data.get("code") or "").strip() or None,
        description=(data.get("description") or "").strip() or None,
    )
    try:
        db.session.add(st)
        db.session.commit()
        return jsonify({"success": True, "message": "Strateji eklendi.", "id": st.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[kurum_api_add_strategy] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@micro_bp.route("/kurum/api/update-main-strategy/<int:strategy_id>", methods=["POST"])
@login_required
def kurum_api_update_main_strategy(strategy_id):
    if not _check_kurum_role():
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403

    st = Strategy.query.filter_by(
        id=strategy_id, tenant_id=current_user.tenant_id
    ).first_or_404()
    data = request.get_json() or {}
    try:
        st.title = (data.get("title") or st.title).strip()
        st.code  = (data.get("code") or "").strip() or st.code
        st.description = data.get("description", st.description)
        db.session.commit()
        return jsonify({"success": True, "message": "Strateji güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[kurum_api_update_main_strategy] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


@micro_bp.route("/kurum/api/delete-main-strategy/<int:strategy_id>", methods=["POST"])
@login_required
def kurum_api_delete_main_strategy(strategy_id):
    if not _check_kurum_role():
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403

    st = Strategy.query.filter_by(
        id=strategy_id, tenant_id=current_user.tenant_id
    ).first_or_404()
    try:
        st.is_active = False
        db.session.commit()
        return jsonify({"success": True, "message": "Strateji silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[kurum_api_delete_main_strategy] {e}")
        return jsonify({"success": False, "message": "Silme sırasında hata oluştu."}), 500


# ── API: Alt Strateji CRUD ────────────────────────────────────────────────────

@micro_bp.route("/kurum/api/add-sub-strategy", methods=["POST"])
@login_required
def kurum_api_add_sub_strategy():
    if not _check_kurum_role():
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403

    data = request.get_json() or {}
    strategy_id = data.get("strategy_id")
    title = (data.get("title") or "").strip()
    if not strategy_id or not title:
        return jsonify({"success": False, "message": "Strateji ve başlık zorunludur."}), 400

    Strategy.query.filter_by(
        id=strategy_id, tenant_id=current_user.tenant_id, is_active=True
    ).first_or_404()

    sub = SubStrategy(
        strategy_id=strategy_id,
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
        current_app.logger.error(f"[kurum_api_add_sub_strategy] {e}")
        return jsonify({"success": False, "message": "Kayıt sırasında hata oluştu."}), 500


@micro_bp.route("/kurum/api/update-sub-strategy/<int:sub_id>", methods=["POST"])
@login_required
def kurum_api_update_sub_strategy(sub_id):
    if not _check_kurum_role():
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403

    sub = SubStrategy.query.join(Strategy).filter(
        SubStrategy.id == sub_id,
        Strategy.tenant_id == current_user.tenant_id,
    ).first_or_404()
    data = request.get_json() or {}
    try:
        sub.title = (data.get("title") or sub.title).strip()
        sub.code  = (data.get("code") or "").strip() or sub.code
        sub.description = data.get("description", sub.description)
        db.session.commit()
        return jsonify({"success": True, "message": "Alt strateji güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[kurum_api_update_sub_strategy] {e}")
        return jsonify({"success": False, "message": "Güncelleme sırasında hata oluştu."}), 500


@micro_bp.route("/kurum/api/delete-sub-strategy/<int:sub_id>", methods=["POST"])
@login_required
def kurum_api_delete_sub_strategy(sub_id):
    if not _check_kurum_role():
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403

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
        current_app.logger.error(f"[kurum_api_delete_sub_strategy] {e}")
        return jsonify({"success": False, "message": "Silme sırasında hata oluştu."}), 500
