"""Kurum Paneli modülü."""

from datetime import datetime, timezone

from flask import render_template, jsonify, request, current_app, abort
from flask_login import login_required, current_user

from platform_core import app_bp
from app.models import db
from app.models.core import Strategy, SubStrategy, Tenant, User
from app.services.k_vektor_config_service import (
    add_k_vektor_snapshot,
    k_vektor_weights_get_dict,
    save_k_vektor_weights,
)
from app_platform.modules.kurum.kurum_overview import build_kurum_overview

_KURUM_ROLES = ("tenant_admin", "executive_manager")


def _check_kurum_role():
    return current_user.role and current_user.role.name in _KURUM_ROLES


@app_bp.route("/kurum/ayarlar", methods=["GET", "POST"])
@login_required
def kurum_ayarlar():
    """Kurum bilgileri ayarları + logo yükleme."""
    if not _check_kurum_role():
        abort(403)

    tenant = current_user.tenant
    if tenant is None:
        abort(404)

    if request.method == "GET":
        import os

        logo_url = None
        upload_folder = os.path.join(current_app.static_folder, "uploads", "logos")
        base = f"tenant_{tenant.id}_logo"
        for ext in ("png", "jpg", "jpeg", "gif", "webp"):
            candidate = os.path.join(upload_folder, f"{base}.{ext}")
            if os.path.exists(candidate):
                logo_url = f"/static/uploads/logos/{base}.{ext}"
                break

        return render_template("platform/kurum/ayarlar.html", tenant=tenant, logo_url=logo_url)

    # POST
    try:
        data = request.get_json() if request.is_json else (request.form.to_dict() if request.form else {})

        # Alanları güncelle (boş gelirse mevcut değeri koru)
        kurum_adi = (data.get("kurum_adi") or "").strip()
        if kurum_adi:
            tenant.name = kurum_adi

        sektor = (data.get("sektor") or "").strip()
        if sektor:
            tenant.sector = sektor

        vergi_no = (data.get("vergi_no") or "").strip()
        if vergi_no:
            tenant.tax_number = vergi_no

        adres = (data.get("adres") or "").strip()
        if adres:
            tenant.activity_area = adres

        telefon = (data.get("telefon") or "").strip()
        if telefon:
            tenant.phone_number = telefon

        email = (data.get("email") or "").strip()
        if email:
            tenant.contact_email = email

        website = (data.get("website") or "").strip()
        if website:
            tenant.website_url = website

        old_kv = bool(getattr(tenant, "k_vektor_enabled", False))
        if "k_vektor_enabled" in data:
            v = data.get("k_vektor_enabled")
            if isinstance(v, bool):
                tenant.k_vektor_enabled = v
            elif isinstance(v, str):
                tenant.k_vektor_enabled = v.strip().lower() in ("1", "true", "yes", "on")
            elif isinstance(v, (int, float)):
                tenant.k_vektor_enabled = bool(v)
        if old_kv != bool(getattr(tenant, "k_vektor_enabled", False)):
            add_k_vektor_snapshot(
                tenant.id,
                current_user.id,
                "k_vektor_toggle",
                {"k_vektor_enabled": tenant.k_vektor_enabled},
            )

        # Logo yükleme (multipart/form-data)
        logo_file = request.files.get("logo")
        if logo_file and logo_file.filename:
            allowed_ext = {"png", "jpg", "jpeg", "gif", "webp"}
            allowed_mime = {"image/png", "image/jpeg", "image/jpg", "image/gif", "image/webp"}
            max_size = 2 * 1024 * 1024  # 2MB

            ext = logo_file.filename.rsplit(".", 1)[-1].lower() if "." in logo_file.filename else ""
            if ext not in allowed_ext:
                return jsonify({"success": False, "message": "Geçersiz logo dosya uzantısı."}), 400

            if logo_file.mimetype and logo_file.mimetype not in allowed_mime:
                return jsonify({"success": False, "message": "Geçersiz logo MIME tipi."}), 400

            logo_file.seek(0, 2)
            size = logo_file.tell()
            logo_file.seek(0)
            if size > max_size:
                return jsonify({"success": False, "message": "Logo dosyası 2MB'dan büyük olamaz."}), 400

            import os
            upload_folder = os.path.join(current_app.static_folder, "uploads", "logos")
            os.makedirs(upload_folder, exist_ok=True)
            base = f"tenant_{tenant.id}_logo"
            filename = f"{base}.{ext}"
            file_path = os.path.join(upload_folder, filename)
            logo_file.save(file_path)

        db.session.commit()
        return jsonify({"success": True, "message": "Kurum ayarları kaydedildi."}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[kurum_ayarlar] {e}")
        return jsonify({"success": False, "message": str(e)}), 500


# ── Sayfa ─────────────────────────────────────────────────────────────────────

@app_bp.route("/kurum")
@login_required
def kurum():
    """Kurum Paneli ana sayfası — tüm giriş yapmış tenant kullanıcıları; düzenleme API’leri rol ile sınırlı."""
    tenant = current_user.tenant
    if tenant is None:
        abort(404)

    tid = current_user.tenant_id
    kid = getattr(current_user, "kurum_id", None) or tid

    user_count = User.query.filter_by(tenant_id=tid, is_active=True).count()
    overview = build_kurum_overview(current_user, tid, kid)
    process_count = overview["process"]["process_count"]
    strategy_count = Strategy.query.filter_by(tenant_id=tid, is_active=True).count()

    strategies = (
        Strategy.query
        .filter_by(tenant_id=tid, is_active=True)
        .order_by(Strategy.code)
        .all()
    )

    can_edit_kurum = _check_kurum_role()

    return render_template(
        "platform/kurum/index.html",
        tenant=tenant,
        user_count=user_count,
        process_count=process_count,
        strategy_count=strategy_count,
        strategies=strategies,
        overview=overview,
        can_edit_kurum=can_edit_kurum,
    )


@app_bp.route("/kurum/api/overview")
@login_required
def kurum_api_overview():
    """Panel özet metrikleri (yenileme / yarı-gerçek zamanlı)."""
    if current_user.tenant is None:
        return jsonify({"success": False, "message": "Tenant bulunamadı."}), 404

    tid = current_user.tenant_id
    kid = getattr(current_user, "kurum_id", None) or tid
    overview = build_kurum_overview(current_user, tid, kid)

    user_n = User.query.filter_by(tenant_id=tid, is_active=True).count()
    strategy_n = Strategy.query.filter_by(tenant_id=tid, is_active=True).count()

    return jsonify(
        {
            "success": True,
            "overview": overview,
            "user_count": user_n,
            "strategy_count": strategy_n,
            "server_time": datetime.now(timezone.utc).isoformat(),
        }
    )


# ── API: Stratejik Kimlik ─────────────────────────────────────────────────────

@app_bp.route("/kurum/api/update-strategy", methods=["POST"])
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

@app_bp.route("/kurum/api/add-strategy", methods=["POST"])
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


@app_bp.route("/kurum/api/update-main-strategy/<int:strategy_id>", methods=["POST"])
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


@app_bp.route("/kurum/api/delete-main-strategy/<int:strategy_id>", methods=["POST"])
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

@app_bp.route("/kurum/api/add-sub-strategy", methods=["POST"])
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


@app_bp.route("/kurum/api/update-sub-strategy/<int:sub_id>", methods=["POST"])
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


@app_bp.route("/kurum/api/delete-sub-strategy/<int:sub_id>", methods=["POST"])
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


# ── K-Vektör ağırlıkları ─────────────────────────────────────────────────────

@app_bp.route("/kurum/api/k-vektor/weights", methods=["GET", "POST"])
@login_required
def kurum_api_k_vektor_weights():
    """Ana / alt strateji ham ağırlıkları (geriye dönük; asıl düzenleme /sp sayfasında)."""
    if not _check_kurum_role():
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403

    tid = current_user.tenant_id
    if request.method == "GET":
        return jsonify(k_vektor_weights_get_dict(tid))

    ok, msg = save_k_vektor_weights(tid, current_user.id, request.get_json() or {})
    if ok:
        return jsonify({"success": True, "message": "K-Vektör ağırlıkları kaydedildi."})
    status = 404 if "bulunamadı" in (msg or "") else 400
    if msg == "Kayıt sırasında hata oluştu.":
        status = 500
    return jsonify({"success": False, "message": msg or "Kayıt başarısız."}), status
