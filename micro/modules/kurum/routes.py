"""Kurum Paneli modülü."""

from datetime import datetime, timezone

from flask import render_template, jsonify, request, current_app, abort
from flask_login import login_required, current_user

from platform_core import app_bp
from app.models import db
from app.models.core import Strategy, SubStrategy, Tenant, User
from app.models.tenant_identity import (
    TenantValue, TenantEthicsCode, TenantQualityPolicy,
)
from app.services.k_vektor_config_service import (
    add_k_vektor_snapshot,
    k_vektor_weights_get_dict,
    save_k_vektor_weights,
)
from app_platform.modules.kurum.kurum_overview import build_kurum_overview
from flask_babel import gettext as _

_KURUM_ROLES = ("tenant_admin", "executive_manager")


def _check_kurum_role():
    return current_user.role and current_user.role.name in _KURUM_ROLES


@app_bp.route("/organization/settings", methods=["GET", "POST"])
@login_required
def kurum_ayarlar():
    """Kurum bilgileri ayarları + logo yükleme."""
    if not _check_kurum_role():
        abort(403)

    tenant = current_user.tenant
    if tenant is None:
        abort(404)

    if request.method == "GET":
        from flask import url_for

        logo_url = None
        if tenant.logo_path:
            v = int(tenant.logo_updated_at.timestamp()) if tenant.logo_updated_at else 0
            logo_url = url_for("app_bp.tenant_logo", tenant_id=tenant.id, v=v)

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

        # Yıl bazlı Faz 1.7 (K5): plan_year_enabled artık AÇILIP KAPANMAZ.
        # Yıl bazlılık sistemin temel çalışma biçimi; kapatmak tüm yıl
        # filtrelerini devre dışı bırakıyordu. Gelen istek sessizce yok
        # sayılır — eski istemciler hata almasın diye 400 döndürülmüyor.
        if "plan_year_enabled" in data:
            current_app.logger.info(
                "[kurum] plan_year_enabled toggle ignored (K5: always on) "
                f"tenant={tenant.id} requested={data.get('plan_year_enabled')!r}"
            )

        if "plan_year_start" in data:
            raw_pys = data.get("plan_year_start")
            try:
                pys = int(raw_pys) if raw_pys not in (None, "", "null") else None
            except (ValueError, TypeError):
                pys = None
            if pys is not None and pys != tenant.plan_year_start:
                from app.services.plan_year_service import initialize_plan_years
                initialize_plan_years(tenant.id, pys)
            tenant.plan_year_start = pys

        # Logo yükleme (multipart/form-data) — instance/uploads/tenant_logos/{tenant_id}.{ext}
        logo_file = request.files.get("logo")
        if logo_file and logo_file.filename:
            import os
            import datetime as _dt
            from app.utils.upload_security import validate_uploaded_image, safe_filename

            allowed_ext = {".png", ".jpg", ".jpeg", ".gif", ".webp", ".svg"}
            max_size = 2 * 1024 * 1024

            blob = logo_file.read()
            if len(blob) > max_size:
                return jsonify({"success": False, "message": _("Logo dosyası 2MB'dan büyük olamaz.")}), 400

            ok, msg, detected_ext = validate_uploaded_image(blob, allowed_ext, accept_svg=True)
            if not ok:
                current_app.logger.warning(
                    f"[kurum_ayarlar logo] reject tenant={tenant.id} user={current_user.id}: {msg}"
                )
                return jsonify({"success": False, "message": msg}), 400

            folder = os.path.join(current_app.instance_path, "uploads", "tenant_logos")
            os.makedirs(folder, exist_ok=True)
            fname = safe_filename(f"{tenant.id}.{detected_ext}", fallback=f"{tenant.id}.png")
            dest = os.path.join(folder, fname)
            if not os.path.abspath(dest).startswith(os.path.abspath(folder)):
                current_app.logger.error(f"[kurum_ayarlar logo] path traversal blocked: {dest}")
                return jsonify({"success": False, "message": _("Geçersiz dosya yolu.")}), 400

            # Eski uzantılı dosyaları temizle
            for old in os.listdir(folder):
                if old.startswith(f"{tenant.id}.") and old != fname:
                    try:
                        os.remove(os.path.join(folder, old))
                    except OSError:
                        pass

            with open(dest, "wb") as out:
                out.write(blob)
            tenant.logo_path = fname
            tenant.logo_updated_at = _dt.datetime.now(_dt.timezone.utc)

        db.session.commit()
        return jsonify({"success": True, "message": _("Kurum ayarları kaydedildi.")}), 200

    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[kurum_ayarlar] {e}")
        return jsonify({"success": False, "message": _("Sunucu hatası oluştu.")}), 500


# ── Sayfa ─────────────────────────────────────────────────────────────────────

@app_bp.route("/organization")
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

    # Çok-satırlı kimlik maddeleri (Değer / Etik / Kalite) — canonical kaynak
    def _kimlik_maddeleri(Model):
        return (
            Model.query
            .filter(Model.tenant_id == tid, Model.is_active.is_(True))
            .order_by(Model.sira.asc(), Model.id.asc())
            .all()
        )

    kimlik = {
        "values": _kimlik_maddeleri(TenantValue),
        "ethics": _kimlik_maddeleri(TenantEthicsCode),
        "quality": _kimlik_maddeleri(TenantQualityPolicy),
    }

    return render_template(
        "platform/kurum/index.html",
        tenant=tenant,
        user_count=user_count,
        process_count=process_count,
        strategy_count=strategy_count,
        strategies=strategies,
        overview=overview,
        can_edit_kurum=can_edit_kurum,
        kimlik=kimlik,
    )


@app_bp.route("/organization/api/overview")
@login_required
def kurum_api_overview():
    """Panel özet metrikleri (yenileme / yarı-gerçek zamanlı)."""
    if current_user.tenant is None:
        return jsonify({"success": False, "message": _("Tenant bulunamadı.")}), 404

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

@app_bp.route("/organization/api/update-strategy", methods=["POST"])
@login_required
def kurum_api_update_strategy():
    """Stratejik kimlik alanlarını güncelle (purpose, vision, core_values, ...)."""
    if not _check_kurum_role():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403

    tenant = Tenant.query.get_or_404(current_user.tenant_id)
    data = request.get_json() or {}
    try:
        for field in ("purpose", "vision", "core_values", "code_of_ethics", "quality_policy"):
            if field in data:
                setattr(tenant, field, data[field])
        db.session.commit()
        return jsonify({"success": True, "message": _("Stratejik kimlik güncellendi.")})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[kurum_api_update_strategy] {e}")
        return jsonify({"success": False, "message": _("Güncelleme sırasında hata oluştu.")}), 500


# ── API: Kimlik maddeleri (çok-satırlı Değer / Etik / Kalite) ────────────────

# kind → (Model, insan-okunur etiket)
_KIMLIK_MODELLERI = {
    "values": (TenantValue, "Değer"),
    "ethics": (TenantEthicsCode, "Etik kural"),
    "quality": (TenantQualityPolicy, "Kalite politikası maddesi"),
}


def _kimlik_model(kind):
    """kind doğrula → Model döndür ya da None."""
    pair = _KIMLIK_MODELLERI.get(kind)
    return pair if pair else (None, None)


@app_bp.route("/organization/api/identity/<kind>/list", methods=["GET"])
@login_required
def kurum_api_kimlik_list(kind):
    """Bir kimlik boyutunun aktif maddelerini sıralı döndür."""
    Model, _etiket = _kimlik_model(kind)
    if Model is None:
        return jsonify({"success": False, "message": _("Geçersiz tür.")}), 400

    rows = (
        Model.query
        .filter(Model.tenant_id == current_user.tenant_id, Model.is_active.is_(True))
        .order_by(Model.sira.asc(), Model.id.asc())
        .all()
    )
    return jsonify({
        "success": True,
        "items": [
            {"id": r.id, "baslik": r.baslik, "aciklama": r.aciklama, "sira": r.sira}
            for r in rows
        ],
    })


@app_bp.route("/organization/api/identity/<kind>/add", methods=["POST"])
@login_required
def kurum_api_kimlik_add(kind):
    """Yeni kimlik maddesi ekle (sıra = mevcut maks + 1)."""
    if not _check_kurum_role():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403
    Model, etiket = _kimlik_model(kind)
    if Model is None:
        return jsonify({"success": False, "message": _("Geçersiz tür.")}), 400

    data = request.get_json() or {}
    baslik = (data.get("baslik") or "").strip()
    if not baslik:
        return jsonify({"success": False, "message": _("Başlık zorunludur.")}), 400

    from sqlalchemy import func
    son_sira = (
        db.session.query(func.coalesce(func.max(Model.sira), -1))
        .filter(Model.tenant_id == current_user.tenant_id, Model.is_active.is_(True))
        .scalar()
    )
    row = Model(
        tenant_id=current_user.tenant_id,
        baslik=baslik,
        aciklama=(data.get("aciklama") or "").strip() or None,
        sira=int(son_sira) + 1,
        is_active=True,
    )
    try:
        db.session.add(row)
        db.session.commit()
        return jsonify({"success": True, "message": f"{etiket} eklendi.", "id": row.id})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[kurum_api_kimlik_add:{kind}] {e}")
        return jsonify({"success": False, "message": _("Kayıt sırasında hata oluştu.")}), 500


@app_bp.route("/organization/api/identity/<kind>/update/<int:item_id>", methods=["POST"])
@login_required
def kurum_api_kimlik_update(kind, item_id):
    """Kimlik maddesini güncelle (tenant izolasyonlu)."""
    if not _check_kurum_role():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403
    Model, etiket = _kimlik_model(kind)
    if Model is None:
        return jsonify({"success": False, "message": _("Geçersiz tür.")}), 400

    row = Model.query.filter_by(
        id=item_id, tenant_id=current_user.tenant_id, is_active=True,
    ).first()
    if row is None:
        return jsonify({"success": False, "message": _("Madde bulunamadı.")}), 404

    data = request.get_json() or {}
    baslik = (data.get("baslik") or "").strip()
    if not baslik:
        return jsonify({"success": False, "message": _("Başlık zorunludur.")}), 400

    row.baslik = baslik
    row.aciklama = (data.get("aciklama") or "").strip() or None
    try:
        db.session.commit()
        return jsonify({"success": True, "message": f"{etiket} güncellendi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[kurum_api_kimlik_update:{kind}] {e}")
        return jsonify({"success": False, "message": _("Güncelleme sırasında hata oluştu.")}), 500


@app_bp.route("/organization/api/identity/<kind>/delete/<int:item_id>", methods=["POST"])
@login_required
def kurum_api_kimlik_delete(kind, item_id):
    """Kimlik maddesini soft-delete (is_active=False)."""
    if not _check_kurum_role():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403
    Model, etiket = _kimlik_model(kind)
    if Model is None:
        return jsonify({"success": False, "message": _("Geçersiz tür.")}), 400

    row = Model.query.filter_by(
        id=item_id, tenant_id=current_user.tenant_id, is_active=True,
    ).first()
    if row is None:
        return jsonify({"success": False, "message": _("Madde bulunamadı.")}), 404

    row.is_active = False
    try:
        db.session.commit()
        return jsonify({"success": True, "message": f"{etiket} silindi."})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[kurum_api_kimlik_delete:{kind}] {e}")
        return jsonify({"success": False, "message": _("Silme sırasında hata oluştu.")}), 500


# ── API: Ana Strateji CRUD ────────────────────────────────────────────────────

@app_bp.route("/organization/api/add-strategy", methods=["POST"])
@login_required
def kurum_api_add_strategy():
    if not _check_kurum_role():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403

    data = request.get_json() or {}
    title = (data.get("title") or "").strip()
    if not title:
        return jsonify({"success": False, "message": _("Başlık zorunludur.")}), 400

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
        return jsonify({"success": False, "message": _("Kayıt sırasında hata oluştu.")}), 500


@app_bp.route("/organization/api/update-main-strategy/<int:strategy_id>", methods=["POST"])
@login_required
def kurum_api_update_main_strategy(strategy_id):
    if not _check_kurum_role():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403

    st = Strategy.query.filter_by(
        id=strategy_id, tenant_id=current_user.tenant_id
    ).first_or_404()
    data = request.get_json() or {}
    try:
        st.title = (data.get("title") or st.title).strip()
        st.code  = (data.get("code") or "").strip() or st.code
        st.description = data.get("description", st.description)
        db.session.commit()
        return jsonify({"success": True, "message": _("Strateji güncellendi.")})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[kurum_api_update_main_strategy] {e}")
        return jsonify({"success": False, "message": _("Güncelleme sırasında hata oluştu.")}), 500


@app_bp.route("/organization/api/delete-main-strategy/<int:strategy_id>", methods=["POST"])
@login_required
def kurum_api_delete_main_strategy(strategy_id):
    if not _check_kurum_role():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403

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
        return jsonify({"success": False, "message": _("Silme sırasında hata oluştu.")}), 500


# ── API: Alt Strateji CRUD ────────────────────────────────────────────────────

@app_bp.route("/organization/api/add-sub-strategy", methods=["POST"])
@login_required
def kurum_api_add_sub_strategy():
    if not _check_kurum_role():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403

    data = request.get_json() or {}
    strategy_id = data.get("strategy_id")
    title = (data.get("title") or "").strip()
    if not strategy_id or not title:
        return jsonify({"success": False, "message": _("Strateji ve başlık zorunludur.")}), 400

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
        return jsonify({"success": False, "message": _("Kayıt sırasında hata oluştu.")}), 500


@app_bp.route("/organization/api/update-sub-strategy/<int:sub_id>", methods=["POST"])
@login_required
def kurum_api_update_sub_strategy(sub_id):
    if not _check_kurum_role():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403

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
        return jsonify({"success": True, "message": _("Alt strateji güncellendi.")})
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"[kurum_api_update_sub_strategy] {e}")
        return jsonify({"success": False, "message": _("Güncelleme sırasında hata oluştu.")}), 500


@app_bp.route("/organization/api/delete-sub-strategy/<int:sub_id>", methods=["POST"])
@login_required
def kurum_api_delete_sub_strategy(sub_id):
    if not _check_kurum_role():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403

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
        return jsonify({"success": False, "message": _("Silme sırasında hata oluştu.")}), 500


# ── K-Vektör ağırlıkları ─────────────────────────────────────────────────────

@app_bp.route("/organization/api/k-vektor/weights", methods=["GET", "POST"])
@login_required
def kurum_api_k_vektor_weights():
    """Ana / alt strateji ham ağırlıkları (geriye dönük; asıl düzenleme /sp sayfasında)."""
    if not _check_kurum_role():
        return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403

    tid = current_user.tenant_id
    from app.services.plan_year_service import get_active_plan_year_for_user
    active_py = get_active_plan_year_for_user(current_user)
    if request.method == "GET":
        return jsonify(k_vektor_weights_get_dict(tid, plan_year=active_py))

    ok, msg = save_k_vektor_weights(tid, current_user.id, request.get_json() or {}, plan_year=active_py)
    if ok:
        return jsonify({"success": True, "message": _("K-Vektör ağırlıkları kaydedildi.")})
    status = 404 if "bulunamadı" in (msg or "") else 400
    if msg == "Kayıt sırasında hata oluştu.":
        status = 500
    return jsonify({"success": False, "message": msg or "Kayıt başarısız."}), status
