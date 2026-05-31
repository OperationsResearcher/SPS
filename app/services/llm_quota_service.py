"""LLM kotası ve maliyet kontrol servisi.

4 katman:
  1. Cooldown — aynı tenant+endpoint kısa sürede tekrar arayamasın
  2. Tenant günlük çağrı sayısı
  3. Tenant aylık çağrı / maliyet
  4. Sistem geneli günlük çağrı (Gemini free tier korur)
"""
from __future__ import annotations

import datetime as _dt
from typing import Optional

from flask import current_app
from sqlalchemy import func, text

from extensions import db
from app.models.llm_usage import LLMUsageLog, LLMQuotaOverride


# ─── Varsayılan limitler (config'ten ezilebilir) ────────────────────────────

DEFAULT_LIMITS = {
    "cooldown_seconds":            30,         # aynı tenant+endpoint
    "tenant_daily_calls":          50,         # tenant başına gün/çağrı
    "tenant_monthly_calls":        500,        # tenant başına ay/çağrı
    "tenant_monthly_cost_usd":     2.00,       # tenant başına ay/USD
    "system_daily_calls":          1000,       # toplam gün/çağrı (Gemini free 1500/g)
    "system_monthly_cost_usd":     50.00,      # toplam ay/USD
    "alert_threshold_pct":         80,         # %X aşılınca uyar
}


def _get_limits() -> dict:
    """config'ten override edilmiş limitler veya varsayılan."""
    if not current_app:
        return DEFAULT_LIMITS
    cfg = current_app.config.get("LLM_QUOTA_LIMITS", {})
    return {**DEFAULT_LIMITS, **cfg}


class QuotaCheckResult:
    def __init__(self, allowed: bool, reason: Optional[str] = None,
                 retry_after_sec: Optional[int] = None,
                 details: Optional[dict] = None):
        self.allowed = allowed
        self.reason = reason
        self.retry_after_sec = retry_after_sec
        self.details = details or {}

    def to_dict(self) -> dict:
        return {
            "allowed": self.allowed,
            "reason": self.reason,
            "retry_after_sec": self.retry_after_sec,
            **self.details,
        }


def check_quota(tenant_id: int, endpoint: str) -> QuotaCheckResult:
    """LLM çağrısından önce kota kontrolü.

    Sırayla 5 kontrol — biri red ederse erken döner.
    """
    limits = _get_limits()
    now = _dt.datetime.now()  # DB yerel saati ile tutarlı (utcnow → yanlış offset hesabı)
    today_start = _dt.datetime(now.year, now.month, now.day)
    month_start = _dt.datetime(now.year, now.month, 1)

    # ── 0. Tenant override — pause edilmiş mi? ───────────────────────────
    override = LLMQuotaOverride.query.filter_by(tenant_id=tenant_id).first()
    if override and override.is_paused:
        return QuotaCheckResult(
            False, reason="tenant_paused",
            details={"note": override.note or "Tenant LLM çağrıları durduruldu"},
        )

    # ── 1. Cooldown — son çağrı bu tenant+endpoint için ne zamandı? ─────
    last = (
        LLMUsageLog.query
        .filter_by(tenant_id=tenant_id, endpoint=endpoint)
        .order_by(LLMUsageLog.created_at.desc())
        .first()
    )
    if last:
        elapsed = (now - last.created_at).total_seconds()
        if elapsed < limits["cooldown_seconds"]:
            return QuotaCheckResult(
                False, reason="cooldown",
                retry_after_sec=int(limits["cooldown_seconds"] - elapsed),
                details={"last_call_at": last.created_at.isoformat()},
            )

    # ── 2. Tenant günlük çağrı sayısı ────────────────────────────────────
    daily_limit = (
        (override.daily_call_limit if override and override.daily_call_limit else None)
        or limits["tenant_daily_calls"]
    )
    tenant_today_count = db.session.query(func.count(LLMUsageLog.id)).filter(
        LLMUsageLog.tenant_id == tenant_id,
        LLMUsageLog.created_at >= today_start,
        LLMUsageLog.status == "ok",
    ).scalar() or 0
    if tenant_today_count >= daily_limit:
        return QuotaCheckResult(
            False, reason="tenant_daily_limit",
            details={"used": tenant_today_count, "limit": daily_limit},
        )

    # ── 3. Tenant aylık çağrı / maliyet ──────────────────────────────────
    monthly_call_limit = (
        (override.monthly_call_limit if override and override.monthly_call_limit else None)
        or limits["tenant_monthly_calls"]
    )
    monthly_cost_limit = (
        (float(override.monthly_cost_limit_usd) if override and override.monthly_cost_limit_usd else None)
        or limits["tenant_monthly_cost_usd"]
    )

    month_row = db.session.execute(text("""
        SELECT
            count(*) FILTER (WHERE status='ok') as calls,
            COALESCE(sum(cost_usd) FILTER (WHERE status='ok'), 0) as cost
        FROM llm_usage_logs
        WHERE tenant_id=:t AND created_at >= :start
    """), {"t": tenant_id, "start": month_start}).fetchone()
    month_calls = int(month_row.calls or 0)
    month_cost = float(month_row.cost or 0)

    if month_calls >= monthly_call_limit:
        return QuotaCheckResult(
            False, reason="tenant_monthly_call_limit",
            details={"used": month_calls, "limit": monthly_call_limit},
        )
    if month_cost >= monthly_cost_limit:
        return QuotaCheckResult(
            False, reason="tenant_monthly_cost_limit",
            details={"used_usd": round(month_cost, 4), "limit_usd": monthly_cost_limit},
        )

    # ── 4. Sistem geneli günlük tavan ────────────────────────────────────
    system_today_count = db.session.query(func.count(LLMUsageLog.id)).filter(
        LLMUsageLog.created_at >= today_start,
        LLMUsageLog.status == "ok",
    ).scalar() or 0
    if system_today_count >= limits["system_daily_calls"]:
        return QuotaCheckResult(
            False, reason="system_daily_limit",
            details={"used": system_today_count, "limit": limits["system_daily_calls"]},
        )

    # ✅ Tüm kontroller geçti
    return QuotaCheckResult(True, details={
        "tenant_today": tenant_today_count,
        "tenant_today_limit": daily_limit,
        "tenant_month_calls": month_calls,
        "tenant_month_cost_usd": round(month_cost, 4),
        "system_today": system_today_count,
    })


def log_usage(
    tenant_id: int,
    endpoint: str,
    user_id: Optional[int] = None,
    provider: str = "gemini",
    model: Optional[str] = None,
    prompt_tokens: int = 0,
    output_tokens: int = 0,
    cost_usd: float = 0.0,
    status: str = "ok",
    error_msg: Optional[str] = None,
    duration_ms: Optional[int] = None,
) -> LLMUsageLog:
    """Çağrı sonrası log kaydı + alarm kontrolü."""
    log = LLMUsageLog(
        tenant_id=tenant_id,
        user_id=user_id,
        endpoint=endpoint,
        provider=provider,
        model=model,
        prompt_tokens=prompt_tokens,
        output_tokens=output_tokens,
        total_tokens=prompt_tokens + output_tokens,
        cost_usd=cost_usd,
        status=status,
        error_msg=error_msg,
        duration_ms=duration_ms,
    )
    db.session.add(log)
    db.session.commit()

    # Alarm kontrolü — %80 aşılınca log'a yaz
    if status == "ok" and current_app:
        limits = _get_limits()
        threshold = limits["alert_threshold_pct"] / 100.0
        # Sistem günlük
        today_start = _dt.datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        sys_count = db.session.query(func.count(LLMUsageLog.id)).filter(
            LLMUsageLog.created_at >= today_start, LLMUsageLog.status == "ok",
        ).scalar() or 0
        if sys_count >= limits["system_daily_calls"] * threshold:
            current_app.logger.warning(
                f"[llm_quota] SYSTEM günlük çağrı %{int(threshold*100)} eşik aşıldı: "
                f"{sys_count}/{limits['system_daily_calls']}"
            )

    return log


def get_tenant_usage_summary(tenant_id: int) -> dict:
    """Tenant'ın güncel kullanım özeti — UI için."""
    limits = _get_limits()
    override = LLMQuotaOverride.query.filter_by(tenant_id=tenant_id).first()
    daily_limit = (
        (override.daily_call_limit if override and override.daily_call_limit else None)
        or limits["tenant_daily_calls"]
    )
    monthly_call_limit = (
        (override.monthly_call_limit if override and override.monthly_call_limit else None)
        or limits["tenant_monthly_calls"]
    )
    monthly_cost_limit = (
        (float(override.monthly_cost_limit_usd) if override and override.monthly_cost_limit_usd else None)
        or limits["tenant_monthly_cost_usd"]
    )

    now = _dt.datetime.now()
    today_start = _dt.datetime(now.year, now.month, now.day)
    month_start = _dt.datetime(now.year, now.month, 1)

    today_count = db.session.query(func.count(LLMUsageLog.id)).filter(
        LLMUsageLog.tenant_id == tenant_id,
        LLMUsageLog.created_at >= today_start,
        LLMUsageLog.status == "ok",
    ).scalar() or 0

    month_row = db.session.execute(text("""
        SELECT count(*) FILTER (WHERE status='ok') as c,
               COALESCE(sum(cost_usd) FILTER (WHERE status='ok'), 0) as cost
        FROM llm_usage_logs WHERE tenant_id=:t AND created_at >= :s
    """), {"t": tenant_id, "s": month_start}).fetchone()

    return {
        "today": {"used": today_count, "limit": daily_limit,
                  "pct": round((today_count / daily_limit) * 100, 1) if daily_limit else 0},
        "month_calls": {"used": int(month_row.c or 0), "limit": monthly_call_limit,
                        "pct": round((int(month_row.c or 0) / monthly_call_limit) * 100, 1) if monthly_call_limit else 0},
        "month_cost": {"used_usd": round(float(month_row.cost or 0), 4),
                       "limit_usd": monthly_cost_limit,
                       "pct": round((float(month_row.cost or 0) / monthly_cost_limit) * 100, 1) if monthly_cost_limit else 0},
        "paused": bool(override and override.is_paused),
    }
