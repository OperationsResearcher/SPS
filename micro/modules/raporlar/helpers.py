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
