"""Raporlar — paylaşılan helper ve sabitler."""
from flask import current_app, jsonify
from flask_login import current_user

# Performans guard'ları
MUDA_MAX_PROCESSES = 50  # MUDA analizinde tek istekte taranacak max süreç sayısı


def _tid_or_none():
    return current_user.tenant_id if current_user.tenant_id else None


def _get_tenant_context(year_param: int | None = None):
    """Rapor route'larında tekrar eden tid + active_py başlatma bloğu.

    Döner: (tid, active_py, py_id) — tenant yoksa (None, None, None)
    """
    tid = _tid_or_none()
    if not tid:
        return None, None, None
    try:
        from app.services.plan_year_service import get_active_plan_year_for_user
        from app.models.plan_year import PlanYear
        if year_param:
            active_py = PlanYear.query.filter_by(tenant_id=tid, year=year_param).first()
        else:
            active_py = get_active_plan_year_for_user(current_user)
        py_id = active_py.id if active_py else None
    except Exception:
        active_py, py_id = None, None
    return tid, active_py, py_id


def _ai_text(prompt: str, fallback: str, tid: int, endpoint: str, max_tokens: int = 400) -> str:
    """LLM çağrısı yap, başarısızsa fallback metin dön."""
    try:
        from app.services.llm_gateway import call_llm
        r = call_llm(prompt=prompt, tenant_id=tid, user_id=current_user.id,
                     endpoint=endpoint, max_output_tokens=max_tokens)
        if r and r.get("text"):
            return r["text"].strip()
    except Exception as e:
        current_app.logger.info(f"[{endpoint}] LLM fallback: {e}")
    return fallback


# ── Rol kapıları (B-002/B-003) ───────────────────────────────────────────────
# Mevcut rol adları (sp/helpers.py::_SP_ROLES ile aynı küme); yeni rol sistemi yok.
ROLES_KISISEL = frozenset({"Admin", "admin", "tenant_admin", "executive_manager", "kurum_yoneticisi"})
ROLES_YONETIM = ROLES_KISISEL | {"ust_yonetim"}


def rapor_rol_izinli(tur: str) -> bool:
    """tur: 'kisisel' (PII/audit/2FA) veya 'yonetim' (CFO/yatırımcı)."""
    role = getattr(current_user, "role", None)
    name = getattr(role, "name", None)
    allowed = ROLES_KISISEL if tur == "kisisel" else ROLES_YONETIM
    return bool(name) and name in allowed


def rapor_rol_gerekli(tur: str):
    """Rol kapısı dekoratörü: API yollarında JSON 403, sayfada 403 şablonu."""
    from functools import wraps
    from flask import request, render_template
    from flask_babel import gettext as _

    def deco(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not rapor_rol_izinli(tur):
                if "/api/" in request.path:
                    return jsonify({"success": False, "message": _("Yetkisiz işlem.")}), 403
                return render_template("errors/403.html"), 403
            return f(*args, **kwargs)
        return wrapper
    return deco
