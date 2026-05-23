"""AI Strategy Pivot Advisor (Önerilen Hamle #2 — Ö7 muadili).

Tenant snapshot'ı + son trigger event'leri + senaryolar üzerinden Gemini'ye
"strateji pivot" önerileri sordurur. API key yoksa heuristic fallback.
"""
from __future__ import annotations

import os
import json
from typing import Optional

from flask import current_app

from app.services.exec_dashboard_service import build_exec_snapshot
from app.models.replan_trigger import ReplanTriggerEvent


def _build_prompt(snapshot: dict, recent_events: list) -> str:
    return f"""Sen kıdemli bir strateji danışmanısın. Aşağıda bir kurumun GÜNCEL strateji yürütme verileri var.
Görevin: 3-5 somut PIVOT ÖNERİSİ üret. Her öneri için:
- pivot_type: (refocus / sunset / accelerate / new_initiative / risk_mitigation)
- title: kısa Türkçe başlık
- rationale: hangi metrikten kaynaklı (1-2 cümle)
- action: somut aksiyon (1 cümle)
- priority: critical / high / medium
- timeframe: bu çeyrek / önümüzdeki çeyrek / yıl sonu

YALNIZCA geçerli JSON döndür: {{"recommendations": [...]}}

--- KURUM VERİLERİ ---
{json.dumps(snapshot, ensure_ascii=False, indent=2)}

--- SON 7 GÜN TRIGGER OLAYLARI ({len(recent_events)} adet) ---
{json.dumps(recent_events[:10], ensure_ascii=False, indent=2)}
"""


def _heuristic_recommendations(snapshot: dict) -> list[dict]:
    recs = []
    kpi = snapshot.get("kpi", {})
    if kpi.get("on_target_pct", 100) < 50:
        recs.append({
            "pivot_type": "refocus",
            "title": "Stratejik odak daraltma",
            "rationale": f"KPI'ların yalnızca %{kpi.get('on_target_pct',0):.0f}'ı hedef üstünde — kaynaklar dağılmış olabilir.",
            "action": "En düşük 3 KPI'yı incele; bağlı oldukları stratejileri pause veya sunset adayı yap.",
            "priority": "high",
            "timeframe": "bu çeyrek",
        })
    act = snapshot.get("activity", {})
    if act.get("total") and act["overdue"] / max(act["total"], 1) > 0.2:
        recs.append({
            "pivot_type": "risk_mitigation",
            "title": "Faaliyet kapasite revizyonu",
            "rationale": f"Faaliyetlerin %{(act['overdue']/max(act['total'],1))*100:.0f}'ı gecikmiş — yürütme darboğazı var.",
            "action": "Kapasite planlaması ve sorumlu yeniden atama; gerçekçi end_date güncellemeleri.",
            "priority": "high",
            "timeframe": "önümüzdeki çeyrek",
        })
    risk = snapshot.get("risk", {})
    if risk.get("critical", 0) > 0:
        recs.append({
            "pivot_type": "risk_mitigation",
            "title": "Kritik risk mitigasyon planı",
            "rationale": f"{risk['critical']} kritik risk açık — strateji çıktılarını tehdit ediyor.",
            "action": "Her kritik risk için sahibi atanmış mitigation initiative oluştur.",
            "priority": "critical",
            "timeframe": "bu çeyrek",
        })
    anom = snapshot.get("anomaly", {})
    if anom.get("high", 0) > 0:
        recs.append({
            "pivot_type": "new_initiative",
            "title": "Anomali kök neden analizi başlatılmalı",
            "rationale": f"{anom['high']} yüksek-severity KPI anomalisi tespit edildi.",
            "action": "A3 raporu açıp 5-neden analizi yap; gerekirse hedef revizyonu öner.",
            "priority": "medium",
            "timeframe": "bu çeyrek",
        })
    init = snapshot.get("initiative", {})
    in_progress = init.get("by_status", {}).get("in_progress", {})
    if in_progress and in_progress.get("avg_progress", 0) < 30 and snapshot.get("year", 0) > 0:
        recs.append({
            "pivot_type": "accelerate",
            "title": "Devam eden initiative'lerde hız problemi",
            "rationale": f"Devam eden {in_progress['count']} initiative'in ortalama ilerlemesi %{in_progress['avg_progress']:.0f}.",
            "action": "Sponsor seviyesinde haftalık 30dk standup ve blocker eskalasyonu başlat.",
            "priority": "high",
            "timeframe": "önümüzdeki çeyrek",
        })
    if not recs:
        recs.append({
            "pivot_type": "accelerate",
            "title": "Genel durum sağlıklı — momentum koru",
            "rationale": "Kritik gösterge yeşil; bu fırsatı yeni bir stratejik bahis için değerlendir.",
            "action": "Bir sonraki çeyreğe küçük bir 'innovation initiative' ekle.",
            "priority": "medium",
            "timeframe": "önümüzdeki çeyrek",
        })
    return recs


def _call_gemini(prompt: str) -> Optional[str]:
    api_key = (
        (current_app.config.get("GEMINI_API_KEY") if current_app else None)
        or os.environ.get("GEMINI_API_KEY")
        or os.environ.get("GOOGLE_API_KEY")
    )
    if not api_key:
        return None
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model_name = (
            (current_app.config.get("GEMINI_MODEL") if current_app else None)
            or os.environ.get("GEMINI_MODEL")
            or "gemini-2.0-flash"
        )
        m = genai.GenerativeModel(model_name)
        resp = m.generate_content(prompt)
        return getattr(resp, "text", None)
    except Exception as e:
        if current_app:
            current_app.logger.warning(f"ai_pivot gemini error: {e}")
        return None


def generate_pivot_recommendations(tenant_id: int, use_llm: bool = True) -> dict:
    snapshot = build_exec_snapshot(tenant_id)
    events = (
        ReplanTriggerEvent.query
        .filter_by(tenant_id=tenant_id)
        .order_by(ReplanTriggerEvent.fired_at.desc())
        .limit(10)
        .all()
    )
    event_dicts = [e.to_dict() for e in events]

    recommendations = []
    source = "heuristic"

    if use_llm:
        text_resp = _call_gemini(_build_prompt(snapshot, event_dicts))
        if text_resp:
            try:
                cleaned = text_resp.strip()
                if cleaned.startswith("```"):
                    cleaned = cleaned.split("```")[1]
                    if cleaned.startswith("json"):
                        cleaned = cleaned[4:]
                parsed = json.loads(cleaned.strip())
                recs = parsed.get("recommendations") or []
                if recs:
                    recommendations = recs
                    source = "llm"
            except Exception as e:
                if current_app:
                    current_app.logger.warning(f"ai_pivot parse error: {e}")

    if not recommendations:
        recommendations = _heuristic_recommendations(snapshot)

    return {
        "snapshot": snapshot,
        "recommendations": recommendations,
        "source": source,
        "event_count": len(event_dicts),
    }
