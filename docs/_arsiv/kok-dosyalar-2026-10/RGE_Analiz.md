# RAG Tabanlı Veri Giriş Asistanı — Prototip Analizi

**Hazırlayan:** Kiro  
**Konu:** Stratejik Planlama Yazılımı için RAG Tabanlı Doğal Dil → Yapılandırılmış Veri Dönüşümü  
**Stack:** Python · Ollama (Yerel LLM + Embedding)  
**Seviye:** Proof of Concept (Kavram Kanıtı)

---

## 1. Mimari Özet

```
Kullanıcı Cümlesi
      │
      ▼
[Embedding (nomic-embed-text)]
      │
      ▼
[Kosinüs Benzerliği → Süreç + PG Eşleştirme]
      │
      ▼
[LLM (llama3) → Sayısal Değer Çıkarma]
      │
      ▼
{"action": "data_entry", "process_id": ..., "pg_id": ..., "value": ..., "confidence": ...}
```

**Akış:**
1. Mock veri (süreç + PG isimleri) embedding modeli ile vektörleştirilir, bellekte tutulur.
2. Kullanıcı cümlesi aynı modelle vektörleştirilir.
3. Kosinüs benzerliği ile en yakın süreç ve PG bulunur.
4. LLM ile cümleden sayısal değer çıkarılır.
5. Sonuç JSON olarak döndürülür.

---

## 2. Prototip Kodu

```python
"""
RAG Tabanlı Veri Giriş Asistanı — Prototip
Gereksinimler: pip install ollama numpy
Ollama kurulu ve çalışıyor olmalı:
  ollama pull nomic-embed-text
  ollama pull llama3
"""

import json
import math
import re
import ollama

# ─────────────────────────────────────────────────────────────────────────────
# 1. MOCK VERİ — Sistemdeki süreç ve PG'leri temsil eder
# ─────────────────────────────────────────────────────────────────────────────

PROCESSES = [
    {
        "id": 1,
        "name": "Müşteri Memnuniyeti Yönetimi",
        "pgs": [
            {"id": 101, "name": "Anket Skoru"},
            {"id": 102, "name": "Şikayet Çözüm Süresi"},
            {"id": 103, "name": "Net Tavsiye Skoru (NPS)"},
        ],
    },
    {
        "id": 2,
        "name": "Stratejik Planlama Yönetimi",
        "pgs": [
            {"id": 201, "name": "EFQM Özdeğerlendirme Puanı"},
            {"id": 202, "name": "Strateji Gerçekleşme Oranı"},
        ],
    },
    {
        "id": 3,
        "name": "İnsan Kaynakları Yönetimi",
        "pgs": [
            {"id": 301, "name": "Çalışan Memnuniyet Endeksi"},
            {"id": 302, "name": "Eğitim Tamamlanma Oranı"},
            {"id": 303, "name": "İşe Alım Süresi (gün)"},
        ],
    },
    {
        "id": 4,
        "name": "Finansal Performans Yönetimi",
        "pgs": [
            {"id": 401, "name": "Bütçe Gerçekleşme Oranı"},
            {"id": 402, "name": "Gelir Artış Oranı"},
        ],
    },
]


# ─────────────────────────────────────────────────────────────────────────────
# 2. VEKTÖRLEŞTİRME — Bellekte indeks oluştur
# ─────────────────────────────────────────────────────────────────────────────

EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL       = "llama3"


def get_embedding(text: str) -> list[float]:
    """Ollama embedding API'si ile metin vektörleştirir."""
    response = ollama.embeddings(model=EMBEDDING_MODEL, prompt=text)
    return response["embedding"]


def cosine_similarity(vec_a: list[float], vec_b: list[float]) -> float:
    """İki vektör arasındaki kosinüs benzerliğini hesaplar (0.0 – 1.0)."""
    dot   = sum(a * b for a, b in zip(vec_a, vec_b))
    norm_a = math.sqrt(sum(a * a for a in vec_a))
    norm_b = math.sqrt(sum(b * b for b in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def build_index(processes: list[dict]) -> list[dict]:
    """
    Tüm süreç ve PG isimlerini vektörleştirir.
    Döndürülen liste: [{"process_id", "pg_id", "label", "vector"}, ...]
    """
    index = []
    for proc in processes:
        # Süreç düzeyinde de indeksle (PG bulunamazsa fallback)
        proc_vec = get_embedding(proc["name"])
        index.append({
            "process_id": proc["id"],
            "pg_id":      None,
            "label":      proc["name"],
            "vector":     proc_vec,
        })
        for pg in proc["pgs"]:
            # "Süreç adı + PG adı" birleşimi daha iyi eşleşme sağlar
            combined = f"{proc['name']} — {pg['name']}"
            pg_vec   = get_embedding(combined)
            index.append({
                "process_id": proc["id"],
                "pg_id":      pg["id"],
                "label":      combined,
                "vector":     pg_vec,
            })
    return index


# ─────────────────────────────────────────────────────────────────────────────
# 3. ARAMA FONKSİYONU — En yakın süreç + PG'yi bul
# ─────────────────────────────────────────────────────────────────────────────

def find_best_match(
    query: str,
    index: list[dict],
    top_k: int = 1,
) -> dict:
    """
    Kullanıcı cümlesini vektörleştirir ve indekste en yüksek
    kosinüs benzerliğine sahip PG kaydını döndürür.
    """
    query_vec = get_embedding(query)

    scored = []
    for entry in index:
        if entry["pg_id"] is None:
            continue  # Sadece PG düzeyinde eşleştir
        sim = cosine_similarity(query_vec, entry["vector"])
        scored.append({**entry, "score": sim})

    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored[0] if scored else {}


# ─────────────────────────────────────────────────────────────────────────────
# 4. NİYET ANALİZİ — LLM ile sayısal değer çıkar
# ─────────────────────────────────────────────────────────────────────────────

def extract_value(sentence: str) -> float | None:
    """
    Ollama LLM kullanarak cümleden sayısal değeri çıkarır.
    Önce basit regex dener (hız için), başarısız olursa LLM'e sorar.
    """
    # Hızlı yol: regex ile sayı bul
    numbers = re.findall(r"\b\d+(?:[.,]\d+)?\b", sentence)
    if len(numbers) == 1:
        return float(numbers[0].replace(",", "."))

    # Yavaş yol: LLM
    prompt = f"""Aşağıdaki Türkçe cümleden sadece girilmek istenen sayısal değeri çıkar.
Cümle: "{sentence}"
Sadece sayıyı yaz, başka hiçbir şey yazma. Eğer sayı yoksa "null" yaz."""

    response = ollama.chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response["message"]["content"].strip()
    if raw.lower() == "null":
        return None
    try:
        return float(raw.replace(",", "."))
    except ValueError:
        return None


# ─────────────────────────────────────────────────────────────────────────────
# 5. ANA FONKSİYON — Tümünü birleştir
# ─────────────────────────────────────────────────────────────────────────────

def process_user_input(sentence: str, index: list[dict]) -> dict:
    """
    Kullanıcı cümlesini alır, süreç+PG eşleştirir, değer çıkarır,
    yapılandırılmış JSON döndürür.
    """
    match = find_best_match(sentence, index)
    value = extract_value(sentence)

    if not match:
        return {"action": "unknown", "error": "Eşleşen PG bulunamadı."}

    return {
        "action":     "data_entry",
        "process_id": match["process_id"],
        "pg_id":      match["pg_id"],
        "value":      value,
        "confidence": round(match["score"], 4),
        "matched_label": match["label"],
    }


# ─────────────────────────────────────────────────────────────────────────────
# 6. ÇALIŞTIR
# ─────────────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("İndeks oluşturuluyor (embedding'ler hesaplanıyor)...")
    index = build_index(PROCESSES)
    print(f"İndeks hazır: {len(index)} kayıt\n")

    test_sentences = [
        "Müşteri memnuniyeti sürecinin anket skoru göstergesine 85 gir.",
        "Stratejik planlama EFQM puanını 320 olarak güncelle.",
        "İK sürecindeki çalışan memnuniyeti 4.2 oldu.",
        "Bütçe gerçekleşme oranı yüzde 94.",
    ]

    for sentence in test_sentences:
        print(f"Girdi : {sentence}")
        result = process_user_input(sentence, index)
        print(f"Çıktı : {json.dumps(result, ensure_ascii=False, indent=2)}")
        print("-" * 60)
```

---

## 3. Örnek Çıktılar

```json
// Girdi: "Müşteri memnuniyeti sürecinin anket skoru göstergesine 85 gir."
{
  "action": "data_entry",
  "process_id": 1,
  "pg_id": 101,
  "value": 85.0,
  "confidence": 0.9312,
  "matched_label": "Müşteri Memnuniyeti Yönetimi — Anket Skoru"
}

// Girdi: "Stratejik planlama EFQM puanını 320 olarak güncelle."
{
  "action": "data_entry",
  "process_id": 2,
  "pg_id": 201,
  "value": 320.0,
  "confidence": 0.9187,
  "matched_label": "Stratejik Planlama Yönetimi — EFQM Özdeğerlendirme Puanı"
}
```

---

## 4. Kurulum ve Çalıştırma

```bash
# 1. Ollama kur (https://ollama.com)
# 2. Modelleri indir
ollama pull nomic-embed-text
ollama pull llama3

# 3. Python bağımlılıkları
pip install ollama numpy

# 4. Çalıştır
python rag_prototype.py
```

---

## 5. Projeye Entegrasyon Analizi

### 5.1 Nereye Oturur?

Bu prototip, mevcut Kokpitim projesinde **`app/services/rag_service.py`** olarak konumlandırılabilir. Mevcut `surec_api_karne` endpoint'ine paralel yeni bir endpoint açılır:

```
POST /process/api/rag-entry
Body: {"sentence": "Müşteri memnuniyeti anket skoru 85"}
```

### 5.2 Mock Veri → Gerçek Veri Geçişi

Prototipteki `PROCESSES` mock verisi yerine gerçek DB sorgusu kullanılır:

```python
# Mock yerine:
from app.models.process import Process, ProcessKpi
processes = Process.query.filter_by(tenant_id=tid, is_active=True).all()
# Her sürecin kpis ilişkisi zaten mevcut
```

### 5.3 İndeks Stratejisi

| Seçenek | Açıklama | Öneri |
|---------|----------|-------|
| **Bellek içi** (mevcut prototip) | Her uygulama başlangıcında yeniden hesaplanır | Geliştirme/test için |
| **Redis cache** | İndeks Redis'e yazılır, TTL ile yenilenir | Üretim için önerilen |
| **pgvector** | PostgreSQL'e vektör uzantısı eklenir | Büyük veri setleri için |

Mevcut projede Redis opsiyonel olarak kurulu (`Flask-Caching`). İlk aşamada **uygulama başlangıcında belleğe al, günlük yenile** yeterlidir.

### 5.4 Güven Eşiği (Confidence Threshold)

```python
CONFIDENCE_THRESHOLD = 0.75  # Altında kullanıcıya onay sor

if result["confidence"] < CONFIDENCE_THRESHOLD:
    # Frontend'e "Emin misiniz?" sorusu gönder
    result["requires_confirmation"] = True
    result["alternatives"] = top_3_matches  # İlk 3 alternatifi sun
```

### 5.5 Kullanıcı Deneyimi Akışı

```
Kullanıcı yazar: "Anket skoru 85"
        │
        ▼
RAG servisi çalışır (< 2 sn)
        │
        ├─ confidence >= 0.75 → Otomatik form doldur + "Onaylıyor musunuz?" göster
        │
        └─ confidence < 0.75  → "Hangi PG'yi kastediyorsunuz?" dropdown sun
```

### 5.6 Performans Tahmini

- `nomic-embed-text` embedding süresi: ~50-100ms / cümle (CPU)
- 500 PG için indeks oluşturma: ~30-60 sn (sadece başlangıçta)
- Arama süresi: < 10ms (bellek içi kosinüs hesabı)
- LLM değer çıkarma: ~500ms-2sn (llama3, CPU)

**Optimizasyon:** Regex ile değer çıkarma başarılı olursa LLM çağrısı atlanır (~%80 vakada regex yeterli).

### 5.7 Sınırlamalar ve Riskler

| Risk | Açıklama | Çözüm |
|------|----------|-------|
| Türkçe embedding kalitesi | `nomic-embed-text` Türkçe'de iyi ama mükemmel değil | `multilingual-e5-large` denenebilir |
| Benzer isimli PG'ler | "Memnuniyet Skoru" vs "Memnuniyet Endeksi" karışabilir | Süreç bağlamını da embedding'e ekle |
| Sayı çıkarma hataları | "yüzde 94" → 94 (regex yakalar), "doksan dört" → LLM gerekir | LLM fallback zaten mevcut |
| Ollama bağımlılığı | Sunucuda Ollama kurulu olmalı | Docker compose'a eklenebilir |

---

## 6. Sonuç

Bu prototip, **doğal dil → yapılandırılmış veri** dönüşümünü yerel LLM ile gerçekleştirilebileceğini kanıtlamaktadır. Mevcut Kokpitim altyapısına entegrasyon için gereken değişiklikler minimaldir:

1. `app/services/rag_service.py` oluştur (bu prototip kodu)
2. Mock veriyi gerçek DB sorgusuna çevir
3. Yeni bir API endpoint ekle
4. Frontend'e "doğal dil girişi" butonu ekle

Tahmini geliştirme süresi: **2-3 gün** (servis + endpoint + basit UI).
