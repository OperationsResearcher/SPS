"""Demo modülü — landing + rol bazlı bypass login + session sonu.

KOKPITIM_DEMO_MODE config flag açık değilse hiçbir endpoint 404 döner.

İlk versiyon (v1) — schema isolation YOK:
  - Tüm demo kullanıcılar aynı Tomofil tenant'ı üzerinde çalışır
  - Per-session schema clone (S3) sonraki TASK'ta eklenecek
  - Bu sürüm, demo akışını (landing, bypass-login, banner, timeout) sahaya çıkarır
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from flask import (
    render_template, request, redirect, url_for,
    abort, current_app, session as flask_session, jsonify,
)
from flask_login import login_user, logout_user, current_user

from platform_core import app_bp
from app.models import db
from app.models.core import User, Role, Tenant


# ── Rol haritası ──────────────────────────────────────────────────────────────
# Demo landing'deki kartlar bu sözlüğe karşılık gelir.
# Backend her rolü Tomofil tenant'ı içindeki uygun bir kullanıcıya bağlar.
DEMO_ROLES = {
    "yonetici": {
        "label": "Kurum Yöneticisi",
        "role_name": "tenant_admin",
        "fallback_email": "admin@tomofil.com",
        "icon": "fas fa-user-shield",
        "color": "#4f46e5",
        "color_soft": "#eef2ff",
        "description": "Tüm modüllere tam erişim. Stratejik plan, süreç, kullanıcı, "
                       "PG yapılandırması. Yönetici penceresinden Kokpitim'i deneyin.",
        "bullets": [
            "Vizyon / strateji ağacı düzenleme",
            "Plan dönemleri ve K-Vektör ağırlıkları",
            "Kullanıcı listesi ve rol görünümü",
            "Karşılaştırma raporları (yıllar arası)",
        ],
    },
    "lider": {
        "label": "Süreç Lideri",
        "role_name": "yonetici",
        "fallback_email": None,   # tenant içinde ilk yonetici-rolü olan kullanıcı
        "icon": "fas fa-user-tie",
        "color": "#8b5cf6",
        "color_soft": "#f5f3ff",
        "description": "Sorumlu olduğu süreçlerin lideri. PG verisi girer, faaliyet "
                       "ekler, ekibini koordine eder. Operasyonel deneyim.",
        "bullets": [
            "Sorumlu süreçlerinin karne ekranı",
            "PG hedef-gerçekleşme veri girişi",
            "Faaliyet atama ve ilerleme",
            "Süreç ekibinin görev takibi",
        ],
    },
    "uye": {
        "label": "Süreç Üyesi",
        "role_name": "calisan",
        "fallback_email": None,   # tenant içinde ilk calisan-rolü olan kullanıcı
        "icon": "fas fa-user",
        "color": "#0ea5e9",
        "color_soft": "#e0f2fe",
        "description": "Süreç üyesi olarak kendi görevlerini, bireysel PG'lerini ve "
                       "atanan faaliyetleri yönetir. Çalışan penceresi.",
        "bullets": [
            "Atanan görevler ve faaliyetler",
            "Bireysel PG (kişisel hedefler)",
            "Süreç karnesine veri girişi",
            "Bireysel performans paneli",
        ],
    },
}


def _demo_enabled() -> bool:
    return bool(current_app.config.get("KOKPITIM_DEMO_MODE"))


def _demo_user_for_role(role_key: str):
    """Demo tenant içinde rol_key'e karşılık gelen bir kullanıcıyı bul."""
    if role_key not in DEMO_ROLES:
        return None
    spec = DEMO_ROLES[role_key]
    demo_tenant_id = current_app.config.get("DEMO_TENANT_ID", 27)

    q = User.query.join(Role, isouter=True).filter(
        User.tenant_id == demo_tenant_id,
        User.is_active.is_(True),
    )

    # 1) Sabit fallback email varsa onu kullan (Yönetici → admin@tomofil.com)
    if spec.get("fallback_email"):
        u = q.filter(User.email == spec["fallback_email"]).first()
        if u:
            return u

    # 2) Rol adına göre tenant içindeki ilk kullanıcıyı seç
    u = q.filter(Role.name == spec["role_name"]).order_by(User.id).first()
    if u:
        return u

    # 3) Son fallback: tenant'taki herhangi bir aktif kullanıcı
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
        roles=DEMO_ROLES,
        demo_minutes=current_app.config.get("DEMO_SESSION_MINUTES", 60),
    )


# ─── /demo/start/<role> — Bypass login ────────────────────────────────────────

@app_bp.route("/demo/start/<role>", methods=["GET", "POST"])
def demo_start(role):
    """Seçili role bağlı bir demo kullanıcısıyla otomatik giriş yapar."""
    if not _demo_enabled():
        abort(404)
    if role not in DEMO_ROLES:
        return redirect(url_for("app_bp.demo_landing"))

    user = _demo_user_for_role(role)
    if not user:
        current_app.logger.error(f"[demo] {role} rolü için kullanıcı bulunamadı")
        return render_template(
            "platform/demo/landing.html",
            roles=DEMO_ROLES,
            demo_minutes=current_app.config.get("DEMO_SESSION_MINUTES", 60),
            error=f"\"{DEMO_ROLES[role]['label']}\" rolü için demo kullanıcı hazır değil. Yöneticiyle iletişime geçin.",
        ), 503

    # Mevcut oturumu temizle
    if current_user.is_authenticated:
        logout_user()
    flask_session.clear()

    # Demo session işaretleri
    started_at = datetime.now(timezone.utc)
    expires_minutes = current_app.config.get("DEMO_SESSION_MINUTES", 60)
    flask_session["demo_session_active"] = True
    flask_session["demo_role"] = role
    flask_session["demo_role_label"] = DEMO_ROLES[role]["label"]
    flask_session["demo_started_at"] = started_at.isoformat()
    flask_session["demo_expires_at"] = (started_at + timedelta(minutes=expires_minutes)).isoformat()
    flask_session.permanent = True

    login_user(user, remember=False)
    # İnaktivite sıfırlaması için aktiviteyi damgala (KURALLAR §8.4)
    from app.services.demo_reset_service import mark_activity
    mark_activity()
    current_app.logger.info(
        f"[demo] session başladı role={role} user={user.id} email={user.email}"
    )
    return redirect(url_for("app_bp.launcher"))


# ─── /demo/end — Çıkış + sıfırlama ────────────────────────────────────────────

@app_bp.route("/demo/end", methods=["GET", "POST"])
def demo_end():
    """Demo session'u sonlandırır, landing'e döner."""
    if not _demo_enabled():
        abort(404)
    was_active = flask_session.get("demo_session_active", False)
    role = flask_session.get("demo_role")
    if current_user.is_authenticated:
        logout_user()
    flask_session.clear()
    if was_active:
        current_app.logger.info(f"[demo] session bitti role={role}")
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
        "role": flask_session.get("demo_role"),
        "role_label": flask_session.get("demo_role_label"),
    })
