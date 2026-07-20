# ÖLÇÜMLER — Ham Veri

> Tüm ölçümler **yerel** ortamda (`kokpitim_db`, PostgreSQL 18) alındı.
> Yayın'a hiçbir yazma yapılmadı. Tarih: 2026-07-20

---

## 1. KMF (Kayseri Model Fabrikası) — yıl bazlı hedef kıyası

Araç: [`scripts/ops/pg_yil_hedef_kiyas.py`](../../scripts/ops/pg_yil_hedef_kiyas.py) — salt okunur.

```
python scripts/ops/pg_yil_hedef_kiyas.py --tenant 16 --csv kmf.csv
```

### Kurum durumu

| | |
|---|---|
| Tenant | `[16] Kayseri Model Fabrika` |
| `plan_year_enabled` | **TRUE** (yıl sistemi açık) |
| Aktif PG | 121 (Yayın'da 126) |
| Plan yılı | 7 → 2020(draft), 2021-2025(closed), 2026(**active**) |
| Toplam hücre | 847 (PG × yıl) |

### Hedef kaynağı dağılımı — ana bulgu

| Kaynak | Hücre | Oran |
|---|---|---|
| **CONFIG** (yıl bazlı gerçek hedef) | **0** | **0.0%** |
| SNAPSHOT (yalnızca `kpi_data`'da) | 183 | 21.6% |
| FALLBACK (yılsız `ProcessKpi`) | 485 | 57.3% |
| YOK | 179 | 21.1% |

**Yıl bazında config kapsamı: 7 yılın hepsinde `0/121`.**

> Plan yılı sistemi açık, `plan_years` satırları var, ama `kpi_year_configs`
> içinde **tek bir hedef bile yazılmamış**. Hedef fiilen yılsız
> `ProcessKpi.target_value`'dan geliyor.

### Neden boş — kök neden

`_seed_kpi_year_configs` ([`app/services/plan_year_service.py:98`](../../app/services/plan_year_service.py#L98))
config satırlarını **yeni PlanYear servis üzerinden oluşturulurken** üretir.

KMF'nin plan yılları [`scripts/ops/vm_apply_plan_years.py`](../../scripts/ops/vm_apply_plan_years.py)
ile **ham INSERT** olarak yazılmış → servis katmanı atlanmış → seed hiç koşmamış.

Yayın'daki 24 `kpi_year_configs` satırı da `vm_kmf_pg_target_fix.sql`'in yazdığı
`is_included` kayıtları; `target_value` alanları boş.

### Hedef format dağılımı — serbest metin riski

`target_value` tipi `String(100)`. 121 PG'de:

| Format | Adet |
|---|---|
| aralık (`50-59`, `90-100`, `%90-100`) | 56 |
| sayı | 32 |
| boş | 27 |
| tire (`-`) | 6 |

> Onarım script'i bu serbest metni **aynen korumalı**, sayıya çevirmeye
> çalışmamalı.

---

## 2. Sahte/üretilmiş veri bulgusu

Kıyas 27 "çakışma" satırı buldu (snapshot ≠ temel hedef). Örnek:

| PG | Ad | snapshot | temel |
|---|---|---|---|
| 420 | Ramakkala Sayısı | 194 | 0 |
| 417 | İş Kazası Sayısı | 134 | 0 |
| 414 | Arizi Sebeple Eğitim Verilememe | 135 | 4 |
| 401 | İkramlardan Memnuniyetlik Oranı | 175 | 90-100 |
| 400 | SP Gözden Geçirme Planına Uyum Oranı | 121 | %90-100 |

### PG#417 tam dökümü — sahtelik kanıtı

12 `kpi_data` satırının tamamı:

- **`created_at` hepsi `2026-03-26 19:08:23`** — mikrosaniyeye kadar aynı
  (783287, 783288, 783303…). Bir insan 2024 Ocak verisini 2026 Mart'ında,
  aynı saniyede 12 dönem birden giremez → **seed/üretici script çıktısı**.
- **`data_date` ay ile tutarsız:** Ocak satırı `2024-01-02`, Aralık satırı
  `2024-04-10`, Şubat satırı `2024-07-06` — rastgele atanmış.
- **2026 satırında `data_date = 2026-11-29`** — gelecek tarih (bugün 2026-07-20).
- **`target_value` 12 satırda da sabit `134`**, yıl fark etmeksizin.
- **`unit = 'Gün'`** ama PG adı "İş Kazası Sayısı" — birim tutarsız.
- `actual_value` 14–153 arası zıplıyor — İş Kazası sayısı için anlamsız.

**Sonuç:** 134 ne yanlış hedef ne kaçmış gerçekleşme — **demo/test amaçlı
rastgele üretilmiş veri**. Gerçek hedef PG tanımındaki `target_value = '0'`
(`direction = Decreasing` ile tutarlı).

### Bunun onarım planına etkisi

> `kpi_data.target_value` snapshot'ları **geçmişin gerçek hedefi sayılamaz.**
> 183 SNAPSHOT hücresinin bilinmeyen bir kısmı bu üreticiden geliyor.
> Snapshot'a güvenen bir onarım KMF'ye çöp hedef yazar.

**Ayrı iş kalemi:** KMF'de gerçek müşteri verisiyle karışmış üretilmiş test
verisi var. Kapsamı ölçülmedi — bkz. [`SORULAR.md`](SORULAR.md).

---

## 3. Yıl seçiminin kod tabanındaki yayılımı

### `sp_active_year` — 9 nokta (891 route'luk sistemde)

| Dosya:satır | Rol |
|---|---|
| `sp/routes_plan_year.py:167` | **YAZAN** (yıl seçimi) |
| `sp/routes_plan_year.py:134` | YAZAN (yeni yıl oluşturunca) |
| `app/services/date_sovereign.py:38` | OKUYAN — merkezî çözücü |
| `app/services/plan_year_service.py:906` | OKUYAN |
| `micro/core/launcher.py:34` | OKUYAN (UI çubuğu) |
| `masaustu/routes.py:242` | OKUYAN (UI çubuğu) |
| `sp/routes_donemler.py:70` | OKUYAN (UI çubuğu) |
| `sp/routes_pages.py:173` | OKUYAN (UI çubuğu) |
| `sp/routes_plan_year.py:67` | OKUYAN |

### `date_sovereign` — import eden modül sayısı: **1**

Tek kullanıcı: [`micro/modules/bireysel/routes.py:30`](../../micro/modules/bireysel/routes.py#L30)

### Hardcoded takvim yılı — 72 nokta

| Modül | Adet |
|---|---|
| `micro/modules/k_rapor` | 18 |
| `app/services` | 12 |
| `micro/modules/raporlar` | 9 |
| `micro/modules/surec` | 8 |
| `micro/modules/sp` | 7 |
| `micro/modules/bireysel` | 7 |
| `app/api` | 5 |
| `micro/modules/masaustu` | 3 |
| `micro/modules/api` | 1 |
| `micro/core` | 1 |
| `app/models` | 1 |

Tespit komutu:
```bash
grep -rn "date\.today()\.year\|datetime\.now()\.year\|datetime\.today()\.year" \
  --include=*.py micro/ app/
```

**Oran:** merkezî çözücüyü kullanan 1 modül · takvim yılını hardcode eden 72 nokta.

---

## 4. Üretilmiş test verisi — tam kapsam (S1 cevabı)

> Ölçüm: yerel DB, tüm tenant'lar, salt okunur. Tarih: 2026-07-20

### 4.1 `kpi_data` — tenant bazında (toplam 366.716 satır)

| id | Kurum | Toplam | Şüpheli | Oran |
|---|---|---|---|---|
| 27 | Tomofil Otomotiv | 91.408 | 90.135 | **%98,6** |
| 58 | tomofiltest | 91.408 | 90.135 | **%98,6** |
| 60 | tom2 | 91.408 | 90.135 | **%98,6** |
| 61 | tom3 | 91.408 | 90.135 | **%98,6** |
| 16 | **Kayseri Model Fabrika** | 497 | **202** | **%40,6** |
| 1 | Default Corp | 298 | 0 | %0 |
| 28 | Eskişehir Makine | 289 | 0 | %0 |

**Şüpheli satırların %98,3'ü dört Tomofil klonunda.** Bu dördü birbirinin tam
kopyası (her biri 71 süreç, 221 PG, 91.408 satır — toplam 366.716'da çakışma yok).

### 4.2 İki ayrı üretim deseni

1. **Gece-yarısı damgaları** (`YYYY-MM-DD 00:00:00.000000`) — en büyük 30 küme,
   her biri 216-268 satır, 2020-09 ile 2026-07 arasına yayılmış. Saat bileşeni
   tam sıfır = üretilmiş.
2. **Mikrosaniye-dağılımlı toplu insert'ler** — `2026-03-21 11:33:37` (291),
   `2026-05-26 11:09:00` (261).

### 4.3 KMF'nin özel durumu

`2026-03-26 19:08:23` kümesi **202 satır** — mikrosaniyeleri farklı olduğu için
`>20` küme kriterine takılmıyor, elle bulundu.

- KMF'nin 497 satırının **%40,6'sı** bu küme
- Sadece **22 farklı `target_value`**, `actual_value` 10-99 arası → rastgele üretim
- **`period_month` ≠ `data_date` ayı: 189 satır** — ve bu tutarsızlık **yalnızca
  KMF'de** var (diğer tüm tenant'larda 0)
- 38 gelecek tarihli satır

### 4.4 `individual_kpi_data` (toplam 19.159)

Tek dev küme: **`2026-05-26 20:46:15` → 18.864 satır (%98,5)**.
Tenant 27/60/61'de 6.288'er satır — üçü de tamamen bu kümeden.
Tenant 16'da 295 satır, kümede **0** → bireysel veri temiz görünüyor.

### 4.5 Gelecek tarihli satırlar (`data_date > 2026-07-20`)

| Tablo | Tenant 27/58/60/61 | Tenant 16 |
|---|---|---|
| `kpi_data` | 5.678'er (toplam 22.712) | 38 |
| `individual_kpi_data` | 385'er (27/60/61) | 1 |

### 4.6 `activity_tracks`

Toplam **1 satır** — tablo pratikte boş, inceleme dışı.

### 4.7 Sınıflandırma

| Durum | Tenant |
|---|---|
| 🔴 **Ağır kirli** | 27, 58, 60, 61 (dört Tomofil klonu) — %98,6 üretilmiş + 22.712 gelecek tarihli |
| 🟠 **Kısmen kirli** | **16 (KMF)** — 497'nin 202'si üretilmiş, 189 ay-tutarsız, 38 gelecek tarihli |
| 🟢 **Temiz** | 1 (Default Corp), 28 (Eskişehir Makine) |

> **Önemli:** KMF gerçek müşteri. Üretilmiş 202 satır gerçek veriyle karışmış
> durumda. Ayırt edici imza mevcut: `created_at = 2026-03-26 19:08:23` +
> `period_month ≠ data_date` ayı. Temizlik teknik olarak mümkün, ama
> **kullanıcı onayı olmadan yapılmaz.**
