"""Demo modülü — landing + kurum bazlı admin bypass login + session sonu.

KOKPITIM_DEMO_MODE config flag açık değilse hiçbir endpoint 404 döner.

v2 — 4 kurum, admin-only giriş:
  - Ziyaretçi 4 kurumdan (Tom1/Tom2/Tom3/Tomofil, her biri farklı paket) birini
    seçer, doğrudan o kurumun admin kullanıcısıyla giriş yapar.
  - Rol seçimi (Yönetici/Lider/Üye) bu sürümde YOK — sonraki işe ertelendi.
  - Per-session schema clone (S3) yok; 4 kurum da paylaşımlı, ortak sıfırlama
    (KURALLAR §8.4 Yol B) tüm demo DB'yi kapsar.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from flask import (
    render_template, request, redirect, url_for,
    abort, current_app, session as flask_session, jsonify,
)
from flask_login import login_user, logout_user, current_user
from flask_babel import lazy_gettext as _

from platform_core import app_bp
from app.models import db
from app.models.core import User, Role, Tenant


# ── Kurum haritası ────────────────────────────────────────────────────────────
# Demo landing'deki kartlar bu sözlüğe karşılık gelir.
# Backend her kurum key'ini config.DEMO_TENANT_IDS üzerinden tenant_id'ye bağlar.
#
# I4 (2026-07-21): `label` alanları ÖZEL İSİMDİR — `_()` ile sarılmamalı.
# Sarılı oldukları için Babel bunları çevrilebilir dize sayıyor ve fuzzy
# eşleştirme absürt sonuçlar üretmişti:
#     "Tomofil" → "Profile"      "Tom1"/"Tom2"/"Tom3" → "TOTAL" (üçü de)
# İngilizce arayüzde kurumun adı değişirdi. Kurum adı çevrilmez.
DEMO_TENANTS = {
    "tom1": {
        "label": "Tom1",
        "package_label": _("Başlangıç Paketi"),
        "icon": "fas fa-seedling",
        "color": "#0ea5e9",
        "color_soft": "#e0f2fe",
        "description": _("Temel modüllerle başlayan küçük ölçekli bir kurum deneyimi."),
    },
    "tom2": {
        "label": "Tom2",
        "package_label": _("Yönetim Paketi"),
        "icon": "fas fa-diagram-project",
        "color": "#8b5cf6",
        "color_soft": "#f5f3ff",
        "description": _("Süreç ve performans yönetimi modülleriyle genişletilmiş kurum deneyimi."),
    },
    "tom3": {
        "label": "Tom3",
        "package_label": _("Strateji Paketi"),
        "icon": "fas fa-chess-knight",
        "color": "#f59e0b",
        "color_soft": "#fffbeb",
        "description": _("Stratejik planlama ve analiz araçlarını da içeren ileri seviye deneyim."),
    },
    "tomofil": {
        "label": "Tomofil",
        "package_label": _("Master Paketi"),
        "icon": "fas fa-crown",
        "color": "#4f46e5",
        "color_soft": "#eef2ff",
        "description": _("Kokpitim'in tüm modüllerine tam erişim — 7 yıllık gerçek stratejik plan verisi."),
    },
}


def _demo_enabled() -> bool:
    return bool(current_app.config.get("KOKPITIM_DEMO_MODE"))


def _demo_admin_for_tenant(tenant_key: str):
    """Kurum key'ine karşılık gelen tenant içinde admin kullanıcıyı bul."""
    if tenant_key not in DEMO_TENANTS:
        return None
    tenant_ids = current_app.config.get("DEMO_TENANT_IDS", {})
    tenant_id = tenant_ids.get(tenant_key)
    if not tenant_id:
        return None

    q = User.query.join(Role, isouter=True).filter(
        User.tenant_id == tenant_id,
        User.is_active.is_(True),
    )

    # 1) tenant_admin rolündeki ilk kullanıcı
    u = q.filter(Role.name == "tenant_admin").order_by(User.id).first()
    if u:
        return u

    # 2) Son fallback: tenant'taki herhangi bir aktif kullanıcı
    return q.order_by(User.id).first()


# ─── /demo/ — Landing sayfası ─────────────────────────────────────────────────

@app_bp.route("/demo/")
@app_bp.route("/demo")
def demo_landing():
    """Demo giriş sayfası — 3 rol kartı + açıklamalar."""
    if not _demo_enabled():
        abort(404)
    # Eğer kullanıcı zaten demo session'da ise direkt launcher'a
    if current_user.is_authenticated and flask_session.get("demo_session_active"):
        return redirect(url_for("app_bp.launcher"))
    return render_template(
        "platform/demo/landing.html",
        tenants=DEMO_TENANTS,
        demo_minutes=current_app.config.get("DEMO_SESSION_MINUTES", 60),
    )


# ─── /demo/start/<tenant_key> — Bypass admin login ────────────────────────────

@app_bp.route("/demo/start/<tenant_key>", methods=["GET", "POST"])
def demo_start(tenant_key):
    """Seçili kurumun admin kullanıcısıyla otomatik giriş yapar."""
    if not _demo_enabled():
        abort(404)
    if tenant_key not in DEMO_TENANTS:
        return redirect(url_for("app_bp.demo_landing"))

    user = _demo_admin_for_tenant(tenant_key)
    if not user:
        current_app.logger.error(f"[demo] {tenant_key} kurumu için admin bulunamadı")
        return render_template(
            "platform/demo/landing.html",
            tenants=DEMO_TENANTS,
            demo_minutes=current_app.config.get("DEMO_SESSION_MINUTES", 60),
            error=f"\"{DEMO_TENANTS[tenant_key]['label']}\" kurumu için demo hesabı hazır değil. Yöneticiyle iletişime geçin.",
        ), 503

    # Mevcut oturumu temizle
    if current_user.is_authenticated:
        logout_user()
    flask_session.clear()

    # Demo session işaretleri
    started_at = datetime.now(timezone.utc)
    expires_minutes = current_app.config.get("DEMO_SESSION_MINUTES", 60)
    flask_session["demo_session_active"] = True
    flask_session["demo_tenant_key"] = tenant_key
    flask_session["demo_tenant_label"] = str(DEMO_TENANTS[tenant_key]["label"])  # lazy_gettext → str (session JSON serileştirilebilir olmalı)
    flask_session["demo_started_at"] = started_at.isoformat()
    flask_session["demo_expires_at"] = (started_at + timedelta(minutes=expires_minutes)).isoformat()
    flask_session.permanent = True

    login_user(user, remember=False)
    # İnaktivite sıfırlaması için aktiviteyi damgala (KURALLAR §8.4)
    from app.services.demo_reset_service import mark_activity
    mark_activity()
    current_app.logger.info(
        f"[demo] session başladı tenant={tenant_key} user={user.id} email={user.email}"
    )
    return redirect(url_for("app_bp.launcher"))


# ─── /demo/end — Çıkış + sıfırlama ────────────────────────────────────────────

@app_bp.route("/demo/end", methods=["GET", "POST"])
def demo_end():
    """Demo session'u sonlandırır, landing'e döner."""
    if not _demo_enabled():
        abort(404)
    was_active = flask_session.get("demo_session_active", False)
    tenant_key = flask_session.get("demo_tenant_key")
    if current_user.is_authenticated:
        logout_user()
    flask_session.clear()
    if was_active:
        current_app.logger.info(f"[demo] session bitti tenant={tenant_key}")
        # KURALLAR §8.4: çıkışta Tomofil'i baseline'a sıfırla — ARKA PLANDA
        # (senkron çalışırsa ~1-2 dk sürüp worker timeout → 502 verir).
        from app.services.demo_reset_service import trigger_async_reset
        trigger_async_reset()
    if request.method == "POST":
        return jsonify({"success": True, "redirect": url_for("app_bp.demo_landing")})
    return redirect(url_for("app_bp.demo_landing"))


# ─── /demo/heartbeat — Session timeout kontrolü ───────────────────────────────

@app_bp.route("/demo/heartbeat", methods=["GET"])
def demo_heartbeat():
    """Frontend'in her dakika çağırdığı endpoint — kalan süreyi döner."""
    if not _demo_enabled():
        return jsonify({"active": False}), 404
    if not flask_session.get("demo_session_active"):
        return jsonify({"active": False})
    exp_iso = flask_session.get("demo_expires_at")
    if not exp_iso:
        return jsonify({"active": False})
    try:
        exp = datetime.fromisoformat(exp_iso)
    except ValueError:
        return jsonify({"active": False})
    now = datetime.now(timezone.utc)
    if now >= exp:
        # Süre doldu — session'ı temizle + Tomofil'i baseline'a sıfırla (KURALLAR §8.4)
        logout_user()
        flask_session.clear()
        from app.services.demo_reset_service import trigger_async_reset
        trigger_async_reset()
        return jsonify({"active": False, "expired": True})
    remaining_seconds = int((exp - now).total_seconds())
    # Aktif heartbeat → inaktivite sayacını sıfırla (KURALLAR §8.4)
    from app.services.demo_reset_service import mark_activity
    mark_activity()
    return jsonify({
        "active": True,
        "remaining_seconds": remaining_seconds,
        "tenant_key": flask_session.get("demo_tenant_key"),
        "tenant_label": flask_session.get("demo_tenant_label"),
    })
