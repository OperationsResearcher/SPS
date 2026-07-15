# Kokpitim AI API Politikası

> **Yürürlük tarihi:** 2026-05-24
> **Kapsam:** Tüm AI/LLM çağrıları (Gemini, OpenAI, Anthropic, Groq, OpenRouter, vb.)
> **Bağlayıcılık:** Yeni AI servisi yazılırken bu kurallar **zorunlu**.

---

## 1. Felsefe

| İlke | Pratik karşılığı |
|---|---|
| **Kullanıcı her zaman cevap alır** | LLM yoksa → kural motoru. Çökmek yasak. |
| **Maliyet ve abuse görünür** | Her çağrı log'lanır, kullanıcıya bugünkü kullanımı söylenir. |
| **Tenant kendi anahtarını kullanabilir** | "BYOK" (Bring Your Own Key) — kurumsal müşteri kendi faturasını yönetir. |
| **Sistem anahtarı yedek** | Tenant key yoksa sistem (Kokpitim) anahtarı devreye girer — ücretsiz kotada. |
| **Provider bağımsız** | Servisler doğrudan `google.generativeai`, `openai` import etmez. Tek geçit (`llm_gateway`) kullanır. |

---

## 2. Çağrı Akışı (Yeni Servis Yazarken Uy)

```python
# YANLIŞ — provider'a doğrudan bağımlı:
import google.generativeai as genai
genai.configure(api_key=os.environ["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.0-flash")
resp = model.generate_content(prompt)

# DOĞRU — tek geçit, tüm provider'lar, otomatik kota + log:
from app.services.llm_gateway import call_llm

result = call_llm(
    tenant_id=current_user.tenant_id,
    user_id=current_user.id,
    endpoint="ai_coach",          # log'da kategorize
    prompt=user_prompt,
    system_prompt="Sen kıdemli koçsun…",
    max_output_tokens=2000,
    expect_json=False,
)
# result = {"text": "...", "usage": {...}, "source": "llm"|"heuristic_quota",
#           "provider": "gemini"|"openai"|..., "quota_summary": {...}}
```

---

## 3. Anahtar Çözüm Sırası

`call_llm` her çağrıda şu sırayla anahtar arar:

```
1. Tenant kendi BYOK key'i tanımlı mı?  →  Kullan (tenant faturalanır)
2. Sistem default key'i tanımlı mı?     →  Kullan (Kokpitim faturalanır, kotalı)
3. Hiçbiri yok                           →  None döner, caller heuristic'e düşer
```

**BYOK desteklenen provider'lar:**
- `gemini` (Google AI Studio)
- `openai` (OpenAI API)
- `anthropic` (Claude API)
- `groq` (Groq Cloud)
- `openrouter` (OpenRouter — 200+ model)

Tenant tek bir provider seçer (UI'dan), key + model adı + opsiyonel endpoint URL girer.

### 🔒 Veri ikametgâhı — kendi sunucunuzdaki LLM (KVKK)

> **Bu zaten çalışıyor** (2026-07-15'te doğrulandı) ama belgede yoktu.
> Kurumsal/kamu satışında en güçlü argümanlardan biri; görünür olmalı.

`provider = openai` + `base_url = <kendi sunucunuz>` verildiğinde çağrı
OpenAI'a değil, **belirtilen adrese** gider. Ollama ve vLLM OpenAI-uyumlu API
sunduğu için kurumun kendi sunucusundaki model doğrudan kullanılabilir:

```
provider : openai
base_url : http://10.0.0.5:11434/v1     # Ollama
model    : llama3.1:70b
api_key  : ollama                        # Ollama key istemez, boş geçilemez
```

**Neden önemli:** KVKK'nın **hiçbir ülkeye yeterlilik kararı yok**
([kvkk.gov.tr](https://www.kvkk.gov.tr/Icerik/2053/Yurtdisina-Aktarim) —
*"Bu konuda Kurul tarafından henüz bir belirleme yapılmamıştır"*). Bu, her
yurt dışı LLM çağrısını "uygun güvence" (standart sözleşme + 5 iş günü içinde
Kurum'a bildirim) yüküne sokar. Yerel LLM'de veri kurumun ağından **hiç
çıkmaz** → bu yük ortadan kalkar.

Global rakipler bunu yapısal olarak veremez (iş modelleri merkezi buluta
bağlı). En yakın örnek Spider Impact 5.8'in "metadata-only" mimarisi — ham
veri müşteri ortamından çıkmıyor, ama **Türkiye'de barındırma yok**.

**Sınır:** Yerel modelin kalitesi kurumun donanımına bağlıdır; heuristik
fallback (§Felsefe) yine devrededir. `pii_mask_enabled` yerel LLM'de de
uygulanır — savunma derinliği.

---

## 4. Kota Politikası

### Sistem (Kokpitim) anahtarı kullanılırken kotalar geçerli:

| Katman | Varsayılan limit | Override edilebilir mi? |
|---|---:|---|
| Cooldown (aynı tenant + endpoint) | 30 sn | ✓ tenant_override |
| Tenant günlük çağrı | 50 | ✓ |
| Tenant aylık çağrı | 500 | ✓ |
| Tenant aylık maliyet | $2.00 | ✓ |
| Sistem geneli günlük | 1.000 | env: `LLM_QUOTA_LIMITS` |
| Sistem aylık maliyet | $50.00 | env |
| Alarm eşiği | %80 | env |

### Tenant kendi key'ini kullanırken:

| Kontrol | Var mı? |
|---|---|
| Cooldown | ✓ var (abuse önleme) |
| Tenant günlük/aylık çağrı | ✗ yok (kendi anahtarı, kendi limiti) |
| Tenant maliyet | ✗ yok (kendi faturası) |
| Sistem günlük | ✗ yok (sistem kotasını yemez) |
| Log kaydı | ✓ var (raporlama için) |

**Mantık:** Tenant kendi key'ini koyduysa zaten Google/OpenAI kendisini sınırlandırıyor. Kokpitim sadece spam ve görünürlük için log tutar.

---

## 5. Paket Bazlı Kota (Kokpitim Sistem Anahtarı İçin)

UI Kılavuzunda tanımlı paket-bazlı varsayılan kotalar:

| Paket | Günlük | Aylık | Aylık Maliyet |
|---|---:|---:|---:|
| **Free / Trial** | 10 | 100 | $0.50 |
| **Starter** | 30 | 300 | $1.50 |
| **Growth** | 100 | 1.000 | $5.00 |
| **Business** | 300 | 5.000 | $20.00 |
| **Enterprise** | 1.000 | 20.000 | $100.00 |
| **Public Sector** | 500 | 8.000 | $40.00 |

Tenant paketi `SubscriptionPackage` modelinden okunur; o paketin LLM limitleri `LLMQuotaOverride` tablosuna yansıtılır (otomatik).

---

## 6. Endpoint Kategorileri

Her LLM çağrısı bir **endpoint** etiketiyle log'lanır. Raporlama ve analitik için zorunlu:

| Endpoint kodu | Servis | Tipik token |
|---|---|---:|
| `ai_pivot` | Strateji pivot önerileri | ~2.000 |
| `ai_coach` | Bireysel performans koçluğu | ~1.500 |
| `ai_summary` | Yönetici özet | ~3.000 |
| `ai_early_warning` | Erken uyarı analizi | ~1.000 |
| `ai_advisor` | Strateji danışmanı | ~2.500 |
| `ai_anomaly_explain` | Anomali yorumlama | ~800 |
| `ai_kpi_suggest` | KPI önerisi | ~1.500 |
| `ai_swot_assist` | SWOT doldurma asistanı | ~1.800 |

Yeni endpoint eklerken bu listeye ekle.

---

## 7. Güvenlik Kuralları

| Kural | Neden |
|---|---|
| **API key DB'de plaintext yazılmaz** | `Fernet` (cryptography) ile şifreli, `SECRET_KEY` türevi |
| **Key UI'da yalnızca `***...xyz` gösterilir** | Ekran paylaşımı / screenshot riski |
| **Key sadece tenant_admin görür ve düzenler** | RBAC |
| **Prompt'ta PII gönderilmesin** | TC kimlik, banka hesap, IBAN — regex ile maskeleme katmanı (S65) |
| **Yanıtlar log'da saklanmaz** | KVKK — sadece token sayısı + endpoint + status |
| **API key rotasyonu** | Her 90 günde uyarı (cron) |

---

## 8. Çıktı Sözleşmesi

`call_llm()` her zaman aynı yapıda döner:

```python
{
    "text": str | None,           # LLM cevabı (yoksa None)
    "source": str,                # "llm" | "heuristic_quota" | "no_provider"
    "provider": str | None,       # "gemini" | "openai" | ...
    "model": str | None,
    "usage": {
        "prompt_tokens": int,
        "output_tokens": int,
        "total_tokens": int,
        "est_cost_usd": float,
    },
    "quota": dict | None,         # check_quota detayı
    "quota_summary": dict | None, # bugün/bu ay kullanım
    "duration_ms": int,
}
```

Caller bu sözleşmeye göre render eder. Provider değişse bile UI değişmez.

---

## 9. Heuristic Fallback Zorunluluğu

Her AI servisinin **LLM olmadan da çalışan bir heuristic motoru olmak zorunda**. Aksi halde sistem dayanıksız olur (Gemini down → sistem down).

Şablon:

```python
def my_ai_endpoint(tenant_id, user_id):
    # 1. Veri topla
    snapshot = collect_data(tenant_id)

    # 2. LLM dene
    if WANT_LLM:
        r = call_llm(tenant_id, user_id, "ai_X", prompt=build_prompt(snapshot))
        if r["text"]:
            try:
                parsed = parse_llm_output(r["text"])
                return {**parsed, "source": "llm", **r}
            except Exception:
                pass  # parse hatası → heuristic'e düş

    # 3. Heuristic — her zaman çalışır
    return {
        **heuristic_logic(snapshot),
        "source": r.get("source", "heuristic"),
        **r,
    }
```

---

## 10. Tenant BYOK UI Sözleşmesi

Tenant ayarlarında **Yapay Zeka** sekmesi:

```
┌─────────────────────────────────────────────────────────┐
│  Yapay Zeka Yapılandırması                              │
├─────────────────────────────────────────────────────────┤
│  ○ Kokpitim sistem AI'sını kullan (ücretsiz, kotalı)    │
│  ● Kendi API anahtarımı kullan (sınırsız, kendi faturam)│
│                                                         │
│  Sağlayıcı:  [Gemini ▼] (Gemini/OpenAI/Anthropic/Groq) │
│  Model:      [gemini-2.0-flash         ]                │
│  API Key:    [••••••••••••••••••••xyz ] [Test Et]      │
│                                                         │
│  ☑ Bu anahtarı sadece bu tenant'ta kullan               │
│  ☐ KVKK: Hassas veri otomatik maskelensin               │
│                                                         │
│  [Kaydet]   [Sil]                                       │
│                                                         │
│  Son test: 2026-05-24 18:30 — Gemini ✓ 1.234 token      │
└─────────────────────────────────────────────────────────┘
```

Test butonu: Hello world tarzında 1 tokenlik test çağrısı yapar, başarılıysa ✓ + kullanılan token sayısını gösterir.

---

## 11. Audit & Raporlama

| Rapor | Sıklık | Alıcı |
|---|---|---|
| Tenant kendi kullanım özeti | UI canlı | Tenant admin |
| Tenant aylık LLM raporu (PDF) | Aylık otomatik | Tenant admin |
| Sistem geneli LLM raporu | Aylık | Kokpitim sahibi (sen) |
| Kota %80 alarmı | Anlık | Tenant admin |
| Anormal kullanım alarmı (10× normal) | Anlık | Tenant admin + Kokpitim |

---

## 12. Sözleşmeyi İhlal Eden Kod Reddedilir

Yeni AI servisi PR'ı incelenirken kontrol listesi:

- [ ] Doğrudan `google.generativeai` / `openai` / `anthropic` import edilmemiş
- [ ] `call_llm()` kullanılmış
- [ ] Heuristic fallback var
- [ ] `endpoint` adı `§6`'da listeli (yoksa eklenmiş)
- [ ] Çıktı `§8` sözleşmesine uyuyor
- [ ] PII filtresi aktif (eğer hassas veri varsa)
- [ ] Token sayısı/maliyet UI'da gösteriliyor

---

## 13. Sürüm Notları

| Sürüm | Tarih | Değişim |
|---|---|---|
| 1.0 | 2026-05-24 | İlk yayın — Gemini tek provider |
| 1.1 | (planlı) | OpenAI + Anthropic + Groq + OpenRouter |
| 1.2 | (planlı) | BYOK UI, encrypted storage |
| 2.0 | (planlı) | Streaming response, function calling |
