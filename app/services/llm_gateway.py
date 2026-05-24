"""LLM Gateway — provider-agnostic tek geçit.

Tüm AI servisleri buradan geçer:
  from app.services.llm_gateway import call_llm

Çözüm sırası:
  1. Tenant BYOK key (aktifse) → tenant faturalanır, sistem kotası harcanmaz
  2. Sistem default key (env GEMINI_API_KEY) → kotalı
  3. Hiçbiri → text=None, caller heuristic'e düşer

Politika: docs/AI-POLITIKASI.md
"""
from __future__ import annotations

import os
import time
from typing import Optional

from flask import current_app

from app.services.llm_quota_service import check_quota, log_usage, get_tenant_usage_summary
from app.models.tenant_llm_config import TenantLLMConfig


# ─── Provider çağırıcılar ────────────────────────────────────────────────────

def _gemini_pricing(model: str) -> tuple[float, float]:
    """USD per million token (input, output) — 2026 Mayıs."""
    m = (model or "").lower()
    # Ücretsiz tier (alias modeller) — fiyatlama 0
    if "lite" in m and "latest" in m:                return (0.0, 0.0)
    if "flash-latest" in m:                          return (0.0, 0.0)
    # Paid modeller
    if "2.5-flash-lite" in m or "flash-lite" in m:   return (0.10, 0.40)
    if "2.5-flash" in m or "flash" in m:             return (0.15, 0.60)
    if "2.5-pro" in m or "pro-latest" in m:          return (1.25, 5.00)
    if "3-flash" in m:                               return (0.20, 0.80)
    if "3-pro" in m:                                 return (1.50, 6.00)
    return (0.10, 0.40)


def _call_gemini(api_key: str, model: str, prompt: str, system_prompt: Optional[str] = None,
                 max_output_tokens: int = 2048) -> tuple[Optional[str], dict]:
    try:
        import google.generativeai as genai
        # REST transport — gRPC SSL sorununu bypass eder (Windows AV/proxy uyumu)
        # AI-POLITIKASI §7 + ortam uyumluluğu için
        genai.configure(api_key=api_key, transport="rest")
        model_name = model or "gemini-2.5-flash-lite"
        m = genai.GenerativeModel(model_name)
        full = (system_prompt + "\n\n---\n\n" + prompt) if system_prompt else prompt
        resp = m.generate_content(
            full,
            generation_config=genai.types.GenerationConfig(max_output_tokens=max_output_tokens),
        )
        usage = {}
        um = getattr(resp, "usage_metadata", None)
        if um is not None:
            prompt_t = int(getattr(um, "prompt_token_count", 0) or 0)
            output_t = int(getattr(um, "candidates_token_count", 0) or 0)
            price_in, price_out = _gemini_pricing(model_name)
            usage = {
                "prompt_tokens": prompt_t,
                "output_tokens": output_t,
                "total_tokens": prompt_t + output_t,
                "est_cost_usd": round((prompt_t * price_in + output_t * price_out) / 1_000_000, 6),
            }
        return getattr(resp, "text", None), usage
    except Exception as e:
        if current_app:
            current_app.logger.warning(f"[llm_gateway] gemini error: {e}")
        return None, {}


def _call_openai(api_key: str, model: str, prompt: str, system_prompt: Optional[str] = None,
                 base_url: Optional[str] = None, max_output_tokens: int = 2048) -> tuple[Optional[str], dict]:
    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key, base_url=base_url or None)
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        msgs.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(
            model=model or "gpt-4o-mini",
            messages=msgs,
            max_tokens=max_output_tokens,
        )
        text = resp.choices[0].message.content if resp.choices else None
        usage = {}
        if resp.usage:
            # gpt-4o-mini: $0.15/M input, $0.60/M output (2026)
            pin, pout = _openai_pricing(model or "gpt-4o-mini")
            prompt_t = resp.usage.prompt_tokens or 0
            output_t = resp.usage.completion_tokens or 0
            usage = {
                "prompt_tokens": prompt_t,
                "output_tokens": output_t,
                "total_tokens": resp.usage.total_tokens or (prompt_t + output_t),
                "est_cost_usd": round((prompt_t * pin + output_t * pout) / 1_000_000, 6),
            }
        return text, usage
    except Exception as e:
        if current_app:
            current_app.logger.warning(f"[llm_gateway] openai error: {e}")
        return None, {}


def _openai_pricing(model: str) -> tuple[float, float]:
    """USD per million token (input, output) — 2026 Mayıs."""
    m = (model or "").lower()
    if "gpt-4o-mini" in m:    return (0.15, 0.60)
    if "gpt-4o" in m:         return (2.50, 10.00)
    if "gpt-4.1-mini" in m:   return (0.40, 1.60)
    if "gpt-4.1" in m:        return (2.00, 8.00)
    if "o1-mini" in m:        return (1.10, 4.40)
    if "o1" in m:             return (15.00, 60.00)
    return (1.00, 4.00)  # makul varsayılan


def _call_anthropic(api_key: str, model: str, prompt: str, system_prompt: Optional[str] = None,
                    max_output_tokens: int = 2048) -> tuple[Optional[str], dict]:
    try:
        from anthropic import Anthropic
        client = Anthropic(api_key=api_key)
        kwargs = {
            "model": model or "claude-haiku-4-5-20251001",
            "max_tokens": max_output_tokens,
            "messages": [{"role": "user", "content": prompt}],
        }
        if system_prompt:
            kwargs["system"] = system_prompt
        resp = client.messages.create(**kwargs)
        text = resp.content[0].text if resp.content else None
        usage = {}
        if resp.usage:
            pin, pout = _anthropic_pricing(model or "claude-haiku-4-5")
            prompt_t = resp.usage.input_tokens or 0
            output_t = resp.usage.output_tokens or 0
            usage = {
                "prompt_tokens": prompt_t,
                "output_tokens": output_t,
                "total_tokens": prompt_t + output_t,
                "est_cost_usd": round((prompt_t * pin + output_t * pout) / 1_000_000, 6),
            }
        return text, usage
    except Exception as e:
        if current_app:
            current_app.logger.warning(f"[llm_gateway] anthropic error: {e}")
        return None, {}


def _anthropic_pricing(model: str) -> tuple[float, float]:
    m = (model or "").lower()
    if "haiku" in m:  return (1.00, 5.00)
    if "sonnet" in m: return (3.00, 15.00)
    if "opus" in m:   return (15.00, 75.00)
    return (3.00, 15.00)


def _call_groq(api_key: str, model: str, prompt: str, system_prompt: Optional[str] = None,
               max_output_tokens: int = 2048) -> tuple[Optional[str], dict]:
    try:
        from openai import OpenAI  # Groq OpenAI uyumlu
        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        msgs = []
        if system_prompt:
            msgs.append({"role": "system", "content": system_prompt})
        msgs.append({"role": "user", "content": prompt})
        resp = client.chat.completions.create(
            model=model or "llama-3.3-70b-versatile",
            messages=msgs,
            max_tokens=max_output_tokens,
        )
        text = resp.choices[0].message.content if resp.choices else None
        usage = {}
        if resp.usage:
            # Groq llama-3.3-70b: $0.59/M in, $0.79/M out
            prompt_t = resp.usage.prompt_tokens or 0
            output_t = resp.usage.completion_tokens or 0
            usage = {
                "prompt_tokens": prompt_t,
                "output_tokens": output_t,
                "total_tokens": resp.usage.total_tokens or (prompt_t + output_t),
                "est_cost_usd": round((prompt_t * 0.59 + output_t * 0.79) / 1_000_000, 6),
            }
        return text, usage
    except Exception as e:
        if current_app:
            current_app.logger.warning(f"[llm_gateway] groq error: {e}")
        return None, {}


PROVIDERS = {
    "gemini":     {"caller": _call_gemini,    "default_model": "gemini-2.5-flash-lite"},
    "openai":     {"caller": _call_openai,    "default_model": "gpt-4o-mini"},
    "anthropic":  {"caller": _call_anthropic, "default_model": "claude-haiku-4-5-20251001"},
    "groq":       {"caller": _call_groq,      "default_model": "llama-3.3-70b-versatile"},
    "openrouter": {"caller": _call_openai,    "default_model": "google/gemini-2.0-flash-exp:free"},
}


# ─── Anahtar çözümleme ──────────────────────────────────────────────────────

def _resolve_provider(tenant_id: int) -> dict:
    """Hangi provider + key kullanılacak?

    Döner: {
        'source': 'tenant_byok' | 'system' | 'none',
        'provider': str | None,
        'model': str | None,
        'api_key': str | None,
        'base_url': str | None,
        'count_against_system_quota': bool,
    }
    """
    # 1. Tenant BYOK
    cfg = TenantLLMConfig.query.filter_by(tenant_id=tenant_id, is_active=True).first()
    if cfg and cfg.api_key_encrypted:
        plain = cfg.api_key_plain
        if plain:
            provider = cfg.provider or "gemini"
            return {
                "source": "tenant_byok",
                "provider": provider,
                "model": cfg.model or PROVIDERS.get(provider, {}).get("default_model"),
                "api_key": plain,
                "base_url": cfg.base_url,
                "count_against_system_quota": False,
            }

    # 2. Sistem default — şu an sadece Gemini destekli
    sys_key = (
        (current_app.config.get("GEMINI_API_KEY") if current_app else None)
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
    )
    if sys_key:
        return {
            "source": "system",
            "provider": "gemini",
            "model": (
                (current_app.config.get("GEMINI_MODEL") if current_app else None)
                or os.environ.get("GEMINI_MODEL")
                or "gemini-2.0-flash"
            ),
            "api_key": sys_key,
            "base_url": None,
            "count_against_system_quota": True,
        }

    return {"source": "none", "provider": None, "model": None,
            "api_key": None, "base_url": None, "count_against_system_quota": False}


# ─── Ana API ─────────────────────────────────────────────────────────────────

def call_llm(
    tenant_id: int,
    endpoint: str,
    prompt: str,
    system_prompt: Optional[str] = None,
    user_id: Optional[int] = None,
    max_output_tokens: int = 2048,
) -> dict:
    """Tek geçit — tüm AI servisleri buradan geçer.

    Sözleşme: docs/AI-POLITIKASI.md §8
    """
    t_start = time.time()
    resolved = _resolve_provider(tenant_id)

    # Provider yoksa — caller heuristic'e düşer
    if resolved["source"] == "none":
        return _result(
            text=None, source="no_provider", provider=None, model=None,
            usage={}, quota=None, quota_summary=None, duration_ms=0,
        )

    # Sistem kotası sadece sistem key'i kullanılırken kontrol edilir
    quota_check = None
    quota_summary = None
    if resolved["count_against_system_quota"]:
        check = check_quota(tenant_id, endpoint)
        quota_check = check.to_dict()
        if not check.allowed:
            log_usage(
                tenant_id=tenant_id, endpoint=endpoint, user_id=user_id,
                provider=resolved["provider"], model=resolved["model"],
                status="quota_exceeded", error_msg=check.reason,
            )
            quota_summary = get_tenant_usage_summary(tenant_id)
            return _result(
                text=None, source="heuristic_quota",
                provider=resolved["provider"], model=resolved["model"],
                usage={}, quota=quota_check, quota_summary=quota_summary,
                duration_ms=int((time.time() - t_start) * 1000),
            )

    # Provider'ı çağır
    caller = PROVIDERS.get(resolved["provider"], {}).get("caller")
    if not caller:
        return _result(
            text=None, source="no_provider", provider=resolved["provider"],
            model=resolved["model"], usage={}, quota=None, quota_summary=None,
            duration_ms=0,
        )

    text, usage = caller(
        api_key=resolved["api_key"],
        model=resolved["model"],
        prompt=prompt,
        system_prompt=system_prompt,
        max_output_tokens=max_output_tokens,
    ) if resolved["provider"] != "openrouter" else caller(
        api_key=resolved["api_key"],
        model=resolved["model"],
        prompt=prompt,
        system_prompt=system_prompt,
        base_url=resolved["base_url"] or "https://openrouter.ai/api/v1",
        max_output_tokens=max_output_tokens,
    )

    duration_ms = int((time.time() - t_start) * 1000)

    # Log'la — BYOK'ta da log var (sadece görünürlük)
    log_usage(
        tenant_id=tenant_id, endpoint=endpoint, user_id=user_id,
        provider=resolved["provider"], model=resolved["model"],
        prompt_tokens=usage.get("prompt_tokens", 0),
        output_tokens=usage.get("output_tokens", 0),
        cost_usd=usage.get("est_cost_usd", 0) if resolved["count_against_system_quota"] else 0,
        # BYOK'ta maliyet tenant'ın → sistem agregasında gözükmesin
        status="ok" if text else "error",
        error_msg=None if text else "no_response",
        duration_ms=duration_ms,
    )

    if resolved["count_against_system_quota"]:
        quota_summary = get_tenant_usage_summary(tenant_id)

    return _result(
        text=text,
        source="llm" if text else "error",
        provider=resolved["provider"], model=resolved["model"],
        usage=usage, quota=quota_check, quota_summary=quota_summary,
        duration_ms=duration_ms,
        key_source=resolved["source"],  # tenant_byok | system
    )


def _result(text, source, provider, model, usage, quota, quota_summary, duration_ms, key_source=None):
    return {
        "text": text,
        "source": source,
        "provider": provider,
        "model": model,
        "usage": usage or {},
        "quota": quota,
        "quota_summary": quota_summary,
        "duration_ms": duration_ms,
        "key_source": key_source,
    }


def test_tenant_config(tenant_id: int) -> dict:
    """BYOK key'in çalışıp çalışmadığını test et."""
    cfg = TenantLLMConfig.query.filter_by(tenant_id=tenant_id).first()
    if not cfg or not cfg.api_key_encrypted:
        return {"success": False, "message": "API anahtarı tanımlı değil"}
    plain = cfg.api_key_plain
    provider = cfg.provider or "gemini"
    caller = PROVIDERS.get(provider, {}).get("caller")
    if not caller:
        return {"success": False, "message": f"Desteklenmeyen provider: {provider}"}

    import datetime as _dt
    try:
        if provider == "openrouter":
            text, usage = caller(
                plain, cfg.model, "Reply with single word: OK",
                system_prompt=None,
                base_url=cfg.base_url or "https://openrouter.ai/api/v1",
                max_output_tokens=10,
            )
        else:
            text, usage = caller(plain, cfg.model, "Reply with single word: OK",
                                 system_prompt=None, max_output_tokens=10)
        ok = bool(text)
        cfg.last_test_at = _dt.datetime.utcnow()
        cfg.last_test_status = "ok" if ok else "error"
        cfg.last_test_message = (text or "Boş cevap")[:200]
        from extensions import db
        db.session.commit()
        return {
            "success": ok,
            "message": cfg.last_test_message,
            "tokens_used": usage.get("total_tokens", 0),
        }
    except Exception as e:
        cfg.last_test_at = _dt.datetime.utcnow()
        cfg.last_test_status = "error"
        cfg.last_test_message = str(e)[:200]
        from extensions import db
        db.session.commit()
        return {"success": False, "message": str(e)}
