# HAM BULGU — Hesaplama Motorları

> Kaynak: paralel backend/hesaplama uzmanı · skor motoru, karne hesapları, analitik servisler
> Tarih: 2026-07-21 · **B2 ana oturumda çalıştırılarak yeniden doğrulandı**

---

## B1 — Bağlantısız alt strateji 0 sayılıyor → vizyon skoru 24 puan düşük · KRİTİK

`app/services/score_engine_service.py:380, :403`

Hiç aktif sürece bağlı olmayan alt strateji **`0.0` puan alıp ortalamaya dahil ediliyor**.
Bu "ölçülmedi" durumu "tamamen başarısız" olarak işleniyor.

> Aynı dosyada **süreç seviyesinde bu doğru yapılmış** (satır 273/282: KPI'sız süreç `None`
> dönüp ortalamadan dışlanıyor) — mantık üst katmanlara taşınmamış.

### Canlı ölçüm

| | Tenant 27 (2026) |
|---|---|
| Mevcut vizyon skoru | **55.78** |
| Sıfırlar dışlanınca | **80.02** |
| **Sapma** | **24.24 puan** |
| 16 alt stratejinin 6'sı | `0.0` (hepsi bağlı aktif süreç = 0) |
| Sıfır olmayanların ortalaması | 93.75 |

Tenant 16 (KMF) daha ağır: 21 alt stratejinin **18'i** `0.0` → vizyon **6.48** görünüyor,
ölçülen işlerin gerçek ortalaması **27.73**.

**DB geneli:** 754 aktif alt stratejinin **230'u** hiç aktif sürece bağlı değil.

**Etki:** Tenant 27 yönetimi "55.78 — orta" görüyor; ölçülen işlerin gerçek başarısı 93.75.
Tenant 16'da sistem pratikte *"her şey battı"* diyor.

**Öneri:** 380 ve 403'te `0.0` yerine `None`; üst ortalamalarda (382, 405, 412) `None` olanları
hem paydan hem paydadan düş — **süreç katmanındaki mevcut desen birebir uygulanabilir**.

---

## B2 — İki `karne_hesaplamalar` kopyası: üretim ESKİ ve HATALI olanı kullanıyor ✅ ANA OTURUMDA DOĞRULANDI · KRİTİK

`utils/karne_hesaplamalar.py` (üretim) vs `app/utils/karne_hesaplamalar.py` (test)

Düzeltilmiş bir hata var ve düzeltme **yanlış kopyaya** uygulanmış.

### Ana oturumda çalıştırılan karşılaştırma

| Girdi | `utils/` **(ÜRETİM)** | `app/utils/` (TEST) |
|---|---|---|
| `3-3,99` | `(3.0, 399.0)` ❌ | `(3.0, 3.99)` ✅ |
| `4,5-9,5` | `(45.0, 95.0)` ❌ | `(4.5, 9.5)` ✅ |
| `1,5` | `(15.0, 15.0)` ❌ | `(1.5, 1.5)` ✅ |
| `-50--10` | `None` ❌ | `(-50.0, -10.0)` ✅ |
| `-10-5` | `None` ❌ | `(-10.0, 5.0)` ✅ |
| `90-100` | `(90.0, 100.0)` | `(90.0, 100.0)` |

**5/7 girdide farklı sonuç.** Üretim kopyası ondalık virgülü **siliyor** → 10-100 kat hata.

### Hangi kopya nerede (ana oturumda sayıldı)

| Kopya | Kullanan |
|---|---|
| `utils/` **(HATALI)** | **9 üretim dosyası**: `api/helpers.py`, `process_performance_service.py`, `surec/{helpers,routes_karne,routes_kpi,routes_kpi_data,routes_activity,routes_process,routes_legacy}.py` |
| `app/utils/` (DOĞRU) | `bireysel/routes.py` + **6 test dosyasının TAMAMI** |

> **Testlerin tamamı düzgün kopyayı test ediyor, süreç karnesi bozuk kopyayı çalıştırıyor.**
> Testler yeşil, üretim yanlış — bu yüzden hata görünmez kaldı.

**Somut etki:** 7 PG'de (`361, 1006945, 1007069, 1007193, 1007317, 1007441, 1007565`)
`'3-3,99'` hedefi üst sınırı **3.99 yerine 399** olarak okunuyor; 4–399 arası her değer
"1 puan (en kötü)" alıyor. Negatif aralık tanımlayan her PG üretimde sessizce `None` dönüp
puanlamadan düşüyor.

**Öneri:** 9 üretim dosyasının import'unu `app.utils.karne_hesaplamalar`'a çevir,
`utils/karne_hesaplamalar.py`'yi shim'e indir. Tek kaynak olmadan bu ikilik tekrar ayrışır.

---

## B3 — `analytics_service` `direction`'ı hiç uygulamıyor: 589 azalan PG ters · KRİTİK

`app/services/analytics_service.py:178` → `performance = (act / tgt) * 100`

`kpi.direction` **hiç okunmuyor**. Kardeş motorlar (`compute_pg_score:86`,
`process_health_service:105`) `Decreasing` dalını doğru işliyor. Üst sınır kırpması da yok.

```
Decreasing, hedef=10, gerçekleşen=50 (KÖTÜ) → 500.0 → 'excellent'
Decreasing, hedef=10, gerçekleşen=2  (İYİ)  →  20.0 → 'critical'
```

**589 aktif `Decreasing` PG** etkileniyor. Maliyet/hata/şikâyet göstergeleri **tam ters** okunuyor.
Kırpma olmadığı için tek sapan KPI ağırlıklı ortalamayı 500'e taşıyabiliyor.

> Bu, `lower_is_better` vakasıyla **aynı sınıf hata** — orada koşul hiç tutmuyordu,
> burada koşul hiç yazılmamış.

---

## B4 — `analytics_service` `year`'ı çözüyor ama HİÇ kullanmıyor: 7 yıl karışıyor · KRİTİK

`app/services/analytics_service.py:135-162`

Satır 135-137 `year`'ı `resolve_request_year()` ile çözüyor; 157-160'taki `KpiData` sorgusunda
**`KpiData.year` filtresi yok**. Değişken kullanılmadan ölüyor.

**Yıl filtresiz "en son veri" seçiminin dağılımı:**

| Yıl | KPI sayısı |
|---|---|
| 2020 | **118** |
| 2021 | 161 |
| 2022 | 187 |
| 2023 | 172 |
| 2024 | 183 |
| 2025 | 235 |
| 2026 | 152 |

Süreç sağlık skoru KPI'ların yalnızca **%12'sinde** 2026 verisine bakıyor; **118 KPI hâlâ 2020
verisiyle** puanlanıyor. Ayrıca `data_date <= today` sınırı yok — DB'de **22.579 gelecek
tarihli** aktif satır var, bunlar "en son" seçiliyor.

**Etki:** Kullanıcı 2026'yı seçse bile aynı skoru görüyor. **Yıl seçici bu ekranda etkisiz.**

---

## B5 — Karışık ağırlık: paydalar tutarsızlaşıyor · YÜKSEK

`score_engine_service.py:95-100, :288-296`

`_default_weight` her KPI'yı **bağımsız** değerlendiriyor: ağırlık doluysa o değeri,
boşsa `100/n`. Aynı süreçte ikisi karışıksa toplam 100 etmiyor.

```
3 KPI, skorlar [100, 0, 0], ağırlıklar [60, 0, 0]
_default_weight → [60.0, 33.33, 33.33]  (toplam 126.67)
sonuç           : 47.37
beklenen (60/20/20): 60.00              → 12.6 puan sapma
```

**DB:** 2327 aktif KPI'nın **469'unun ağırlığı 0**; **64 süreçte** hem dolu hem boş ağırlık bir arada.

---

## B6 — Yüzde işaretli hedef çevrilemiyor: 126 PG hiç puanlanmıyor · YÜKSEK

`score_engine_service.py:39-67` — `_resolve_target_for_calculation` `%`, `₺`, boşluk temizliği yapmıyor.

| | Sayı |
|---|---|
| Hedefi dolu aktif PG | 1914 |
| **Sayıya çevrilemeyen** | **126** |
| bunların % işaretli olanı | 84 |

`'%90-100'` → `None` (90.0 olmalıydı) · `'1.234,5'` → `None` (binlik nokta işlenmiyor)

**Etki:** 84 PG kullanıcının gözünde hedefi tanımlı ama motor `None` döndürüyor →
süreç ortalamasında `sc = 0.0` ile **sıfır** sayılıyor. Hedefi "%90-100" yazan gösterge,
verisi ne olursa olsun 0 puan getirip süreç skorunu aşağı çekiyor.

> Kardeş `parse_aralik_degeri` (karne tarafı) `%` ve `TL`'yi temizliyor — bu motor temizlemiyor.

---

## B7 — `k_radar_service`'te `lower_is_better` ölü koşulu HÂLÂ CANLI · YÜKSEK

`services/k_radar_service.py:1224`

```python
if getattr(kpi, 'direction', 'Increasing') == 'lower_is_better':
```

Bu oturumda `k_rapor/routes.py`'de düzeltilen hatanın **aynısı bu dosyada duruyor**.
`k_rapor/routes.py:41` hatayı belgelemiş ve `_AZALMASI_IYI` ile düzeltmiş — bu dosya güncellenmemiş.

**DB:** `Increasing` 1723 · `Decreasing` 604 · `lower_is_better` **0**

**Etki:** K-Radar gap analizinde **604 azalan gösterge ters puanlanıyor**;
"hedefte/riskli/kritik" etiketleri yanlış.

---

## B8 — `early_warning` sayısal olmayan hedefleri sessizce atlıyor: 840 PG kör · YÜKSEK

`services/early_warning_service.py:100-102` → `target = float(kpi.target_value or 0)` (ham `float()`)

Aralık (`'90-100'`), yüzde (`'%90-100'`) veya `'-'` hedefli her PG `ValueError` fırlatıyor,
dıştaki `except` yakalayıp KPI'yı atlıyor.

**DB:** Aktif 2282 PG'nin **840'ı (%36,8)** sayıya çevrilemeyen hedefe sahip.

**Etki:** Gece taraması PG'lerin **üçte birinden fazlasında kör**. Yöneticiye giden
"N KPI hedef altında" özeti bu 840 göstergeyi hiç saymıyor — sessiz eksik kapsama.

---

## B9 — `early_warning` azalan göstergelerde eşik asimetrik · ORTA

Artan için eşik `target * 0.80`, azalan için `target * 1.20`. Görünüşte simetrik ama
**oransal değil** — doğru karşılık `target / 0.80 = target * 1.25` olurdu.

604 `Decreasing` PG bu daldan geçiyor; azalan göstergelerde uyarı eşiği ~%4 daha hassas.

---

## B10 — `process_health_service` fallback'inde alt sınır yok · ORTA (latent)

`:84-85` → `min(100.0, float(kpi.calculated_score))` — `max(0.0, ...)` **yok**.
Ana dal (satır 109) her iki sınırı da uyguluyor.

DB'de şu an `calculated_score < 0` kayıt yok (0/565) — **hata tetiklenmiyor** ama koruma yok.

---

## B11 — `get_anomaly_detection` ham metin üzerinde pandas istatistiği · ORTA

`analytics_service.py:322-333` — `'value': d.actual_value` doğrudan `String(100)` kolonundan;
`pd.to_numeric` **yok**. Ardından `.mean()`, `.std()` çağrılıyor.

> Bu, aynı dosyadaki `get_forecast` docstring'inde *"GERÇEK VERİYLE PATLIYORDU"* diye
> belgelenen hatanın **birebir aynısı** — orası düzeltilmiş, burası atlanmış.

DB'de sayısal olmayan **116 aktif `actual_value`** var (`'-'`×101, `'%100'`, `'₺100.070.853'`).

---

## B12 — Üst üç katmanda ağırlık yok · ORTA

`score_engine_service.py:382-384, :405-407, :412-414` — süreç→alt strateji, alt strateji→ana
strateji ve ana strateji→vizyon geçişlerinin **üçü de düz aritmetik ortalama**.

`KVektorStrategyWeight` tabloları ağırlıkları kaydediyor ama **klasik motor onları hiç okumuyor**
(yalnız `k_vektor_enabled` tenant'larda ayrı motora devrediliyor).

**Etki:** K-Vektör kapalı kurumlarda 5 alt stratejili bir ana strateji ile 1 alt stratejili
diğeri vizyona **eşit** katkı veriyor.

---

## B13 — `get_comparative_analysis` tenant filtresi uygulamıyor · ORTA (güvenlik)

`analytics_service.py:260` → `Process.query.filter(Process.id.in_(process_ids))` — `tenant_id` yok.

Kod yorumu bunu açıkça devrediyor: *"tenant_id sorguya dahil edilmez (caller sorumluluğu)"*.
Çıktı `process_name` ve `process_code` döndürüyor — **başka kurumun süreç adı ve kodu**.

> S2/S3 ile aynı desen: savunma çağırana bırakılmış.

---

## B14 — Aralık hedefinde en kolay uç seçiliyor · DÜŞÜK (tasarım kararı)

`score_engine_service.py:58-65` — `'90-100'` → `Increasing` için `90.0`, `Decreasing` için `100.0`.
Her iki yönde de **ulaşılması en kolay uç**.

Gerçekleşen 90 olan bir PG `'90-100'` hedefinde **tam 100 puan** alıyor; aralığın üst ucuna
göre bu %90 başarıdır. Skorlar sistematik olarak iyimser tarafa kayıyor. **378 aktif PG** aralık hedefli.

Docstring'de bilinçli karar olarak yazılmış — ama kullanıcıya görünür kılınmalı.

---

# ŞÜPHELİ (doğrulanamadı, karar gerektirir)

- **`_default_weight` üst sınırı 100** — DB'de `weight > 100` aktif KPI yok (0/2327), şu an etkisiz.
  Ağırlıkların "yüzde" mi "puan" mı olduğu netleşmeden hata denemez.
- **`compute_pg_score` `Decreasing` + gerçekleşen=0 → 100 puan** — Sıfır hata/maliyet için doğru,
  ama "veri girilmedi ve 0 yazıldı"dan ayırt edilemiyor. `SONRAKI-ISLER.md` İ4'teki
  "0 ve None ayrımı" kararıyla örtüşüyor, orada çözülmeli.
- **`get_forecast` tahmin tarihleri sabit 30 gün** — dönem tipi çeyreklik/yıllıksa etiketler kayar.
- **`hedef_radar_service._yon` `old_target=0` dalı** — matematiksel olarak savunulabilir, tasarım tercihi.
