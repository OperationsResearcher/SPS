"""AI Coach Servisi — LLM Gateway üzerinden çalışır.

Politika: docs/AI-POLITIKASI.md
"""
from typing import Dict, Any, Optional


SYSTEM_PROMPT = """Sen kıdemli bir strateji danışmanısın. Sana verilen kurumsal skor motoru çıktısını analiz edeceksin.

Görevin:
1. Ağırlığı yüksek ama puanı (skor) düşük olan süreçleri ve performans göstergelerini (PG) tespit et.
2. "En Düşük Efor / En Yüksek Etki" kuralına göre tam 3 somut aksiyon öner.
3. Yanıtını Türkçe ve Markdown formatında ver. Başlıklar için ## veya ###, listeler için - kullan.
4. Önerileri numaralı (1., 2., 3.) ve uygulanabilir şekilde yaz."""


def analyze_strategic_performance(
    data: Dict[str, Any],
    tenant_id: Optional[int] = None,
    user_id: Optional[int] = None,
) -> Dict[str, Any]:
    """Skor motoru çıktısını analiz eder.

    tenant_id verilmezse heuristic mod (kota gerek yok, fallback metin).
    Verilirse LLM Gateway üzerinden çağrılır (BYOK ya da sistem key).
    """
    user_content = _build_user_prompt(data)

    # tenant_id yoksa veya gateway yoksa — basit heuristic fallback
    if not tenant_id:
        return {
            "success": True,
            "analysis_markdown": _heuristic_analysis(data),
            "error": None,
            "usage": None,
            "source": "heuristic",
        }

    from app.services.llm_gateway import call_llm
    result = call_llm(
        tenant_id=tenant_id,
        user_id=user_id,
        endpoint="ai_coach",
        system_prompt=SYSTEM_PROMPT,
        prompt=user_content,
        max_output_tokens=4000,
    )

    if result.get("text"):
        return {
            "success": True,
            "analysis_markdown": result["text"].strip(),
            "error": None,
            "usage": result.get("usage"),
            "source": "llm",
            "provider": result.get("provider"),
            "model": result.get("model"),
            "key_source": result.get("key_source"),
            "quota_summary": result.get("quota_summary"),
        }

    # LLM yok / kota aşıldı / hata → heuristic
    return {
        "success": True,
        "analysis_markdown": _heuristic_analysis(data),
        "error": None,
        "usage": result.get("usage"),
        "source": result.get("source") or "heuristic",
        "quota": result.get("quota"),
        "quota_summary": result.get("quota_summary"),
    }


def _heuristic_analysis(data: Dict[str, Any]) -> str:
    """LLM yokken döndürülecek basit Markdown rapor."""
    vs = data.get("vision_score")
    ana = sorted(
        data.get("ana_stratejiler") or [],
        key=lambda s: (s.get("agirlik", 0) * (100 - (s.get("score") or 100))),
        reverse=True,
    )[:3]
    parts = [
        "## Performans Analizi (Kural Motoru)",
        f"**Vizyon puanı:** {vs}/100" if vs is not None else "",
        "",
        "### En yüksek ağırlık × düşük skor stratejiler",
    ]
    for i, s in enumerate(ana, 1):
        ad = s.get('ad', f"Strateji {s.get('id')}")
        parts.append(f"{i}. **{ad}** — skor: {s.get('score', '-')}, ağırlık: {s.get('agirlik', '-')}")

    parts += [
        "",
        "### Aksiyon Önerileri",
        "1. Düşük skorlu yüksek ağırlık stratejilere bağlı süreçleri haftalık review'a al.",
        "2. Bu stratejilerdeki KPI veri girişinin tamlığını kontrol et.",
        "3. Sorumlu atanmamış faaliyetleri belirle ve sahip ata.",
        "",
        "_Not: LLM yapılandırılmamış. Detaylı analiz için tenant ayarlarından AI'yı etkinleştir._",
    ]
    return "\n".join(p for p in parts if p is not None)


def _build_user_prompt(data: Dict[str, Any]) -> str:
    parts = []
    parts.append("Aşağıdaki skor motoru çıktısını analiz et ve yukarıdaki görevi uygula.\n")
    parts.append(f"**Vizyon puanı:** {data.get('vision_score')} / 100")
    parts.append(f"**Hesaplama tarihi:** {data.get('as_of_date', '-')}\n")

    ana = data.get("ana_stratejiler") or []
    if ana:
        parts.append("### Ana stratejiler (ad, skor, ağırlık, vizyona katkı)")
        for s in ana:
            parts.append(f"- {s.get('ad', '?')} | skor: {s.get('score', '-')} | ağırlık: {s.get('agirlik', '-')} | vizyon katkı: {s.get('vizyona_katki', '-')}")
        parts.append("")

    surec = data.get("surecler") or []
    if surec:
        parts.append("### Süreçler (ad, skor, ağırlık)")
        for s in surec[:20]:
            parts.append(f"- {s.get('ad', '?')} | skor: {s.get('score', '-')} | ağırlık: {s.get('agirlik', '-')}")
        parts.append("")

    pg = data.get("performans_gostergeleri") or []
    if pg:
        parts.append("### Performans göstergeleri (ad, skor, süreç_id)")
        for p in pg[:30]:
            parts.append(f"- {p.get('ad', '?')} | skor: {p.get('score', '-')} | süreç: {p.get('surec_id', '-')}")

    return "\n".join(parts)
