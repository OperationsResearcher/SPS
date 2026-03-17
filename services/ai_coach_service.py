# -*- coding: utf-8 -*-
"""
AI Coach Servisi - Gemini API ile stratejik performans analizi.
Skor motoru verilerini (vision_score, strateji/süreç/PG skorları ve ağırlıklar) analiz eder.
"""
from typing import Dict, Any, Optional


SYSTEM_PROMPT = """Sen kıdemli bir strateji danışmanısın. Sana verilen kurumsal skor motoru çıktısını analiz edeceksin.

Görevin:
1. Ağırlığı yüksek ama puanı (skor) düşük olan süreçleri ve performans göstergelerini (PG) tespit et.
2. "En Düşük Efor / En Yüksek Etki" kuralına göre tam 3 somut aksiyon öner.
3. Yanıtını Türkçe ve Markdown formatında ver. Başlıklar için ## veya ###, listeler için - kullan.
4. Önerileri numaralı (1., 2., 3.) ve uygulanabilir şekilde yaz."""


def analyze_strategic_performance(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Skor motoru çıktısını Gemini ile analiz eder; strateji danışmanı rolünde
    yüksek ağırlık / düşük puan alanları ve 3 aksiyon önerisi döner.

    Args:
        data: vision_score, ana_stratejiler (ad, score, agirlik, vizyona_katki),
              surecler (ad, score, agirlik?), performans_gostergeleri (ad, score, surec_id, agirlik?),
              as_of_date vb. içeren JSON.

    Returns:
        {
            'success': bool,
            'analysis_markdown': str,   # Gemini'nin Markdown yanıtı
            'error': str | None
        }
    """
    try:
        from flask import current_app
        api_key = current_app.config.get('GEMINI_API_KEY') if current_app else None
        if not api_key:
            import os
            api_key = os.environ.get('GEMINI_API_KEY') or os.environ.get('GOOGLE_API_KEY')
        if not api_key:
            return {
                'success': False,
                'analysis_markdown': None,
                'error': 'GEMINI_API_KEY veya GOOGLE_API_KEY .env dosyasında tanımlı değil.',
                'usage': None,
            }

        import google.generativeai as genai
        genai.configure(api_key=api_key)
        # Model: .env'de GEMINI_MODEL varsa onu kullan; yoksa sirayla dene (gemini-1.5-flash v1beta'da 404 verebiliyor)
        model_name = None
        if current_app:
            model_name = (current_app.config.get('GEMINI_MODEL') or '').strip() or None
        if not model_name:
            import os
            model_name = (os.environ.get('GEMINI_MODEL') or '').strip() or None
        candidates = [model_name] if model_name else ['gemini-2.0-flash', 'gemini-2.5-flash', 'gemini-pro']
        user_content = _build_user_prompt(data)
        full_prompt = SYSTEM_PROMPT + '\n\n---\n\n' + user_content
        response = None
        last_error = None
        for candidate in candidates:
            if not candidate:
                continue
            try:
                m = genai.GenerativeModel(candidate)
                try:
                    response = m.generate_content(
                        full_prompt,
                        generation_config=genai.types.GenerationConfig(
                            temperature=0.3,
                            max_output_tokens=8192,
                        ),
                    )
                except (AttributeError, TypeError):
                    response = m.generate_content(full_prompt)
                if response and getattr(response, 'text', None):
                    break
            except Exception as e:
                last_error = e
                continue
        text = response.text if response and getattr(response, 'text', None) else ''
        if not text.strip():
            err_msg = 'Gemini boş yanıt döndü.'
            if last_error:
                err_msg += ' Son hata: ' + str(last_error)
            return {
                'success': False,
                'analysis_markdown': None,
                'error': err_msg,
                'usage': None,
            }
        usage = None
        if response and hasattr(response, 'usage_metadata') and response.usage_metadata:
            um = response.usage_metadata
            usage = {
                'prompt_token_count': getattr(um, 'prompt_token_count', None) or getattr(um, 'input_token_count', None),
                'candidates_token_count': getattr(um, 'candidates_token_count', None) or getattr(um, 'output_token_count', None),
                'total_token_count': getattr(um, 'total_token_count', None),
            }
            if usage['total_token_count'] is None and (usage['prompt_token_count'] or usage['candidates_token_count']):
                p = usage['prompt_token_count'] or 0
                c = usage['candidates_token_count'] or 0
                usage['total_token_count'] = p + c
        return {
            'success': True,
            'analysis_markdown': text.strip(),
            'error': None,
            'usage': usage,
        }
    except Exception as e:
        return {
            'success': False,
            'analysis_markdown': None,
            'error': str(e),
            'usage': None,
        }


def _build_user_prompt(data: Dict[str, Any]) -> str:
    """Skor motoru verisinden Gemini'ye gönderilecek metni oluşturur."""
    parts = []
    parts.append('Aşağıdaki skor motoru çıktısını analiz et ve yukarıdaki görevi uygula.\n')
    parts.append(f"**Vizyon puanı:** {data.get('vision_score')} / 100")
    parts.append(f"**Hesaplama tarihi:** {data.get('as_of_date', '-')}\n")

    ana = data.get('ana_stratejiler') or []
    if ana:
        parts.append('### Ana stratejiler (ad, skor, ağırlık, vizyona katkı)')
        for a in ana:
            parts.append(f"- {a.get('ad')}: skor={a.get('score')}, ağırlık={a.get('agirlik')}, vizyona_katkı={a.get('vizyona_katki')}")
        parts.append('')

    surecler = data.get('surecler') or []
    if surecler:
        parts.append('### Süreçler (ad, skor, ağırlık)')
        for s in surecler:
            parts.append(f"- {s.get('ad')}: skor={s.get('score')}, ağırlık={s.get('agirlik', '-')}")
        parts.append('')

    pg_list = data.get('performans_gostergeleri') or []
    if pg_list:
        parts.append('### Performans göstergeleri (ad, skor, ağırlık)')
        for p in pg_list:
            parts.append(f"- {p.get('ad')}: skor={p.get('score')}, ağırlık={p.get('agirlik', '-')}")
        parts.append('')

    parts.append('Yukarıdaki verilere göre: (1) Ağırlığı yüksek ama puanı düşük süreç/PG\'leri tespit et, (2) En Düşük Efor / En Yüksek Etki ile 3 aksiyon öner. Yanıtını Türkçe Markdown ile yaz.')
    return '\n'.join(parts)
