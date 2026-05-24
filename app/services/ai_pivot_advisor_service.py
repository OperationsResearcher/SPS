"""AI Strategy Pivot Advisor — LLM Gateway'i kullanır.

Politika: docs/AI-POLITIKASI.md
"""
from __future__ import annotations

import json
from typing import Optional

from flask import current_app

from app.services.exec_dashboard_service import build_exec_snapshot
from app.services.llm_gateway import call_llm
from app.models.replan_trigger import ReplanTriggerEvent


SYSTEM_PROMPT = (
    "Sen kıdemli bir strateji danışmanısın. "
    "Aşağıdaki kurum verilerine bakarak 3-5 somut PIVOT ÖNERİSİ üret. "
    "YALNIZCA geçerli JSON döndür, başka bir şey yazma. "
    "Her öneri için: pivot_type (refocus/sunset/accelerate/new_initiative/risk_mitigation), "
    "title, rationale, action, priority (critical/high/medium), timeframe."
)


def _build_user_prompt(snapshot: dict, events: list) -> str:
    return (
        f"## KURUM VERİLERİ\n```json\n{json.dumps(snapshot, ensure_ascii=False, indent=2)}\n```\n\n"
        f"## SON {len(events)} TRIGGER OLAYI\n```json\n{json.dumps(events[:10], ensure_ascii=False, indent=2)}\n```\n\n"
        'Format: {"recommendations": [{"pivot_type":"...","title":"...","rationale":"...","action":"...","priority":"...","timeframe":"..."}]}'
    )


def _heuristic_recommendations(snapshot: dict) -> list[dict]:
    recs = []
    kpi = snapshot.get("kpi", {})
    if kpi.get("on_target_pct", 100) < 50:
        recs.append({
            "pivot_type": "refocus",
            "title": "Stratejik odak daraltma",
            "rationale": f"KPI'ların yalnızca %{kpi.get('on_target_pct', 0):.0f}'ı hedef üstünde.",
            "action": "En düşük 3 KPI'yı incele; bağlı oldukları stratejileri pause/sunset adayı yap.",
            "priority": "high",
            "timeframe": "bu çeyrek",
        })
    act = snapshot.get("activity", {})
    if act.get("total") and act["overdue"] / max(act["total"], 1) > 0.2:
        recs.append({
            "pivot_type": "risk_mitigation",
            "title": "Faaliyet kapasite revizyonu",
            "rationale": f"Faaliyetlerin %{(act['overdue'] / max(act['total'], 1)) * 100:.0f}'ı gecikmiş.",
            "action": "Kapasite planlaması + sorumlu yeniden atama.",
            "priority": "high",
            "timeframe": "önümüzdeki çeyrek",
        })
    risk = snapshot.get("risk", {})
    if risk.get("critical", 0) > 0:
        recs.append({
            "pivot_type": "risk_mitigation",
            "title": "Kritik risk mitigasyon planı",
            "rationale": f"{risk['critical']} kritik risk açık.",
            "action": "Her kritik risk için sahipli mitigation initiative aç.",
            "priority": "critical",
            "timeframe": "bu çeyrek",
        })
    anom = snapshot.get("anomaly", {})
    if anom.get("high", 0) > 0:
        recs.append({
            "pivot_type": "new_initiative",
            "title": "Anomali kök neden analizi",
            "rationale": f"{anom['high']} yüksek-severity KPI anomalisi.",
            "action": "A3 raporu + 5-neden analizi başlat.",
            "priority": "medium",
            "timeframe": "bu çeyrek",
        })
    init = snapshot.get("initiative", {})
    in_progress = init.get("by_status", {}).get("in_progress", {})
    if in_progress and in_progress.get("avg_progress", 0) < 30:
        recs.append({
            "pivot_type": "accelerate",
            "title": "Devam eden initiative'lerde hız problemi",
            "rationale": f"{in_progress['count']} initiative ortalama %{in_progress['avg_progress']:.0f}.",
            "action": "Haftalık 30dk sponsor standup + blocker eskalasyonu.",
            "priority": "high",
            "timeframe": "önümüzdeki çeyrek",
        })
    if not recs:
        recs.append({
            "pivot_type": "accelerate",
            "title": "Genel durum sağlıklı — momentum koru",
            "rationale": "Kritik gösterge yeşil.",
            "action": "Bir sonraki çeyreğe küçük 'innovation initiative' ekle.",
            "priority": "medium",
            "timeframe": "önümüzdeki çeyrek",
        })
    return recs


def _parse_llm_json(text: str) -> Optional[list]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```")[1]
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    cleaned = cleaned.strip().rstrip("`").strip()
    try:
        parsed = json.loads(cleaned)
        return parsed.get("recommendations")
    except Exception as e:
        if current_app:
            current_app.logger.warning(f"[ai_pivot] parse error: {e}")
        return None


def generate_pivot_recommendations(
    tenant_id: int, use_llm: bool = True, user_id: Optional[int] = None,
) -> dict:
    snapshot = build_exec_snapshot(tenant_id)
    events = (
        ReplanTriggerEvent.query
        .filter_by(tenant_id=tenant_id)
        .order_by(ReplanTriggerEvent.fired_at.desc())
        .limit(10)
        .all()
    )
    event_dicts = [e.to_dict() for e in events]

    llm_result = {"text": None, "source": "no_provider"}
    if use_llm:
        llm_result = call_llm(
            tenant_id=tenant_id,
            endpoint="ai_pivot",
            user_id=user_id,
            system_prompt=SYSTEM_PROMPT,
            prompt=_build_user_prompt(snapshot, event_dicts),
            max_output_tokens=2000,
        )

    recommendations = []
    final_source = "heuristic"

    if llm_result.get("text"):
        parsed = _parse_llm_json(llm_result["text"])
        if parsed:
            recommendations = parsed
            final_source = "llm"

    if not recommendations:
        recommendations = _heuristic_recommendations(snapshot)
        # llm_result.source: "no_provider" / "heuristic_quota" / "error"
        final_source = llm_result.get("source") or "heuristic"

    return {
        "snapshot": snapshot,
        "recommendations": recommendations,
        "source": final_source,
        "event_count": len(event_dicts),
        "usage": llm_result.get("usage") or {},
        "provider": llm_result.get("provider"),
        "model": llm_result.get("model"),
        "key_source": llm_result.get("key_source"),  # tenant_byok | system
        "quota": llm_result.get("quota"),
        "quota_summary": llm_result.get("quota_summary"),
    }
