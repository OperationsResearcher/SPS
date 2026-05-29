"""Raporlar — paylaşılan helper ve sabitler."""
from flask import current_app
from flask_login import current_user

# Performans guard'ları
MUDA_MAX_PROCESSES = 50  # MUDA analizinde tek istekte taranacak max süreç sayısı


def _tid_or_none():
    return current_user.tenant_id if current_user.tenant_id else None


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
