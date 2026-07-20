# HASAR TESPİTİ — Yıl Bazlı Sistem Denetimi

> Tarih: 2026-07-20 · Yöntem: 3 paralel kod denetimi + yerel DB ölçümü (KMF, tenant 16)
> Durum: **tespit tamamlandı, uygulama başlamadı**

---

## 0. Yıl seçimi nasıl taşınıyor — zincirin çıpası

Kullanıcının seçtiği yıl: **`session["sp_active_year"]`**

Yazan tek yer: [`micro/modules/sp/routes_plan_year.py:167`](../../micro/modules/sp/routes_plan_year.py#L167)
(ve `:134` yeni yıl oluşturulunca).

Merkezî çözücü **mevcut**: [`app/services/date_sovereign.py:29`](../../app/services/date_sovereign.py#L29)

```python
def get_view_year(user) -> int:
    """Kullanıcının UI'da görmek istediği yıl.
    Öncelik: 1. session["sp_active_year"]  2. bugünün takvim yılı"""
```

Belge kendini "tarih egemen plan year doktrini" olarak tanımlıyor ve üç kavramı
ayırıyor: VIEW context / RECORD routing / EXISTENCE check. Tasarım doğru.

**Kusur: uygulanmamış.** `date_sovereign`'ı import eden tek modül
[`micro/modules/bireysel/routes.py:30`](../../micro/modules/bireysel/routes.py#L30).

`sp_active_year` tüm kod tabanında **9 dosyada** geçiyor (891 route'luk sistemde),
çoğu yalnızca ekrana yıl seçim çubuğunu çizmek için.

Buna karşılık **72 noktada** hardcoded takvim yılı var → §4.

---

## 1. SP (Stratejik Planlama) katmanı

| Varlık | Model | Yıl kolonu | Route filtreliyor? | Kaynak |
|---|---|---|---|---|
| Strateji | `Strategy` | `plan_year_id` (nullable) + `strategy_year_configs` | ✅ `include_null=True` ile | `app/models/core.py:227`; `sp/routes_pages.py:87-102` |
| Alt Strateji | `SubStrategy` | `plan_year_id` + override | ⚠️ Sadece parent join'i; kendi listesinde filtre yok | `core.py:259`; `routes_strategy.py:247,282` |
| Misyon/Vizyon/Değerler | `TenantYearIdentity` | `plan_year_id` (unique) | ✅ | `app/models/tenant_year.py:15` |
| SWOT | `SwotAnalysis` | `plan_year_id` | ✅ okuma+yazma | `app/models/swot.py:15`; `routes_analysis.py:190` |
| TOWS | `TowsAnalysis` | `plan_year_id` | ✅ | `swot.py:69`; `routes_analysis.py:257` |
| PESTEL | `PestelAnalysis` | `plan_year_id` | ✅ | `swot.py:123`; `routes_analysis.py:321` |
| Porter 5 Forces | `PorterFiveForcesAnalysis` | `plan_year_id` | ✅ | `swot.py:178`; `routes_analysis.py:112` |
| Hedef/Amaç (OKR) | `OkrObjective` | `plan_year_id` NOT NULL | ⚠️ Liste ✅, ama update/delete/detail **sadece `tenant_id`** | `app/models/okr.py:16`; `routes_analysis.py:527,569,588` |
| BSC Perspektif | `BscKpiPerspective` | `plan_year_id` NOT NULL | ✅ | `app/models/bsc.py:25` |
| Plan Projesi/Faaliyet | `PlanProject`/`PlanProjectTask` | `plan_year_id` | ✅ `_require_plan_year()` zorunlu | `routes_sp_proje.py:73-75` |
| X-Matrix | türetilmiş | — | ✅ | `routes_frameworks.py:58-62` |
| Girişim | `Initiative` | ❌ `plan_year_id` yok — `start_year`/`end_year` aralığı | ⚠️ Opsiyonel `?year`; `sp_active_year` kullanılmıyor | `app/models/initiative.py:40-41`; `routes_initiative.py:35-37` |
| **Blue Ocean Canvas** | `BlueOceanCanvas` | ❌ **YOK** (sadece `tenant_id`) | ❌ Tüm yıllar | `strategy_frameworks.py:13`; `routes_frameworks.py:84-93` |
| **VRIO Kaynak** | `VRIOResource` | ❌ **YOK** | ❌ Tüm yıllar | `strategy_frameworks.py:125`; `routes_frameworks.py:194,203` |

**Mimari not — çift mekanizma riski:** İki farklı yıl yaklaşımı bir arada:
(a) full-clone (`plan_year_id` doğrudan varlıkta), (b) override tabloları
(`strategy_year_configs`, `kpi_year_configs`, `process_year_configs`…).
Strateji için **ikisi de** mevcut — çakışma riski var.

**Tenant flag bağımlılığı:** `tenant.plan_year_enabled` false ise **hiçbir filtre
uygulanmıyor** ([`routes_pages.py:170-192`](../../micro/modules/sp/routes_pages.py#L170)),
SP tamamen yıl-bağımsız çalışıyor.

---

## 2. Süreç / PG / Proje katmanı

| Varlık | Model | Yıl kolonu | Route filtreliyor? | Kaynak |
|---|---|---|---|---|
| Süreç | `Process` | `plan_year_id` | ✅ aktif PY + NULL fallback | `app/models/process.py:90`; `routes_process.py:95-112` |
| **PG (tanım)** | `ProcessKpi` | `plan_year_id` + `KpiYearConfig` | ❌ Liste `process_id`+`is_active` ile; `plan_year_id` filtresi **YOK** | `process.py:181`; `routes_kpi.py:283-286` |
| PG verisi | `KpiData` | `year` NOT NULL | ✅ | `process.py:388,437` |
| Süreç Faaliyeti | `ProcessActivity` | `plan_year_id` | ❌ Detay/CRUD'da filtre yok | `process.py:250`; `routes_activity.py:280,311,436` |
| Faaliyet takibi | `ActivityTrack` | `year` NOT NULL + unique | ✅ | `process.py:359,370` |
| **Süreç–Strateji bağı** | `ProcessSubStrategyLink` | ❌ **YOK** | ❌ | `process.py:20`; `routes_process.py:248` |
| **Proje** | `Project` | ❌ **YOK** — `plan_year_id` kasıtlı kaldırılmış | ❌ | `app/models/portfolio_project.py:44`; `routes_project_crud.py:184-185` |
| **Proje görevi** | `Task` | ❌ **YOK** | ❌ | `portfolio_project.py:193` |
| **Proje–PG bağı** | `Task.process_kpi_id` | ❌ yılsız FK | ❌ | `portfolio_project.py:226-228` |
| PG ağırlık/dahiliyet | `weight` + `KpiYearConfig.weight/is_included` | Override var | ⚠️ Sadece `?year` gönderilirse | `process.py:170`; `routes_kpi.py:288-307` |

### 2.1 PG yazma kusuru — asıl tetikleyici bulgu

[`micro/modules/surec/routes_kpi.py:192-199`](../../micro/modules/surec/routes_kpi.py#L192)
`surec_api_kpi_update` şu alanları **doğrudan `ProcessKpi` üzerine, yılsız** yazıyor:

- `target_value` (hedef)
- `weight` (ağırlık)
- `period` (periyot)
- `direction` (yön)
- `basari_puani_araliklari` (başarı puanı aralıkları)

`active_py` / `upsert_kpi_year_config` **hiç çağrılmıyor.**

> **Sonuç:** 2026'da yapılan hedef veya ağırlık değişikliği **2025 karnesini
> geriye dönük bozar.**

Doğru yol aynı dosyada mevcut: `:260` `upsert_kpi_year_config(py, kpi.id, {...})`
kullanıyor. Yani mekanizma var, update rotası kullanmıyor.

**İkincil kusur:** `surec_api_kpi_get` ([`:143-173`](../../micro/modules/surec/routes_kpi.py#L143))
`?year` okumuyor, `get_kpi_configs_bulk` çağırmıyor — düzenleme modalı her zaman
ham `ProcessKpi` değerini gösteriyor. Yazma kusuruyla birleşince kullanıcının
base kaydı yanlışlıkla ezmesini **garantiliyor**.

---

## 3. K-Radar / Analiz / Rapor / Masaüstü katmanı

### 3.1 Skor motoru — çekirdek DOĞRU

[`app/services/score_engine_service.py:157`](../../app/services/score_engine_service.py#L157)
`KpiData.year == year` filtreliyor; `:190-196` `kpi_year_configs`'ten hedef alıyor,
yoksa `ProcessKpi.target_value` fallback.

**Ama:** `:114`, `:322`, `:454` — `year=None` geldiğinde `date.today().year`.
Session'ı bilmiyor; yalnızca çağıran doğru yılı verirse doğru çalışıyor.

### 3.2 Ekran/servis tablosu

| Ekran/Servis | Yıl filtresi? | Yıl kaynağı | Hedef kaynağı | Kaynak |
|---|---|---|---|---|
| **K-Radar/Analiz sayfası** | — | **yıl kavramı YOK** | — | `analiz/routes.py:13-27` |
| Analiz → Trend API | ❌ (son 365 gün) | `datetime.now()` HARDCODED | yılsız `ProcessKpi` | `analiz/routes.py:41`; `analytics_service.py:45-49` |
| Analiz → Sağlık skoru | ❌ (KpiData tüm yıllar) | `datetime.now().year` | yılsız | `analiz/routes.py:93`; `analytics_service.py:134-158` |
| Analiz → Tahmin | ❌ | tarih bazlı, yılsız | — | `analytics_service.py:307-311` |
| Analiz → Karşılaştırma | ❌ | yok | yılsız | `analiz/routes.py:143` |
| Analiz → Performans raporu | ❌ | `datetime.now()` | yılsız | `report_service.py:186` |
| Analiz → Anomali | ❌ | yok | — | `analiz/routes.py:185-220` |
| **Masaüstü favori PG kartları** | ❌ | `year.desc()` → **"en son girilen yıl"**, seçili yıl değil | yılsız | `masaustu/routes.py:143-158` |
| Masaüstü eksik PG/bireysel | ❌ | `date.today()` | — | `masaustu/routes.py:181-191` |
| Masaüstü plan year bar | — | ✅ `sp_active_year` (sadece UI çizimi) | — | `masaustu/routes.py:242` |
| K-Rapor index + 17 API | ✅ | `?year` → yoksa `date.today().year`; **session'a bakmıyor** | `kpi_year_configs` | `k_rapor/routes.py:97-116,137,204,391…` |
| Raporlar Faz0 PDF | ✅ | active_py (doğru) | year config | `routes_faz0.py:315-331` |
| Raporlar Faz3 vizyon/strateji | ✅ | active_py | year config | `routes_faz3.py:120,394` |
| Raporlar Faz3 ESG / Audit | ❌ | `date.today().year` HARDCODED | — | `routes_faz3.py:557,768` |
| **Raporlar Faz4 en yüksek/düşük 5 PG** | ⚠️ | `KpiData.year == date.today().year` HARDCODED | — | `routes_faz4.py:198,207,219,227` |
| Raporlar Faz5 vizyon | ✅ | active_py, fallback today | year config | `routes_faz5.py:55-57` |
| SP Analiz | ✅ | active_py | year config | `sp/routes_analysis.py:675` |
| SP Exec Advisor | ✅ | `?year` → today fallback | year config | `routes_exec_advisor.py:72,523` |
| Karne | ✅ | `?year` → `datetime.now().year` | — | `surec/routes_karne.py:212,582` |
| Process health servisi | ❌ | `datetime.now().year` | yılsız | `process_health_service.py:53` |
| Cache servisi | ✅ | `current_year-2..+2` HARDCODED | year config | `cache_service.py:33-34` |
| Hedef Radar | ❌ (gün bazlı, 365) | takvim gününden | — | `hedef_radar_service.py:77-115` |

---

## 4. Hardcoded takvim yılı — 72 nokta

`date.today().year` / `datetime.now().year` kullanımı, kullanıcının seçtiği yılı
**sessizce yok sayar**. Modül dağılımı:

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
| **Toplam** | **72** |

Kritik olanlar (yanlış veriyi sessizce gösterenler):
- `raporlar/routes_faz4.py:198,207,219,227`
- `raporlar/routes_faz3.py:557,768`
- `masaustu/routes.py:143,182,233,318`
- `k_rapor/routes.py` — 17 route'ta default
- `surec/routes_karne.py:212,582`
- `app/services/score_engine_service.py:114,322,454`
- `analytics_service.py:135`; `process_health_service.py:53`; `report_service.py:186`
- `cache_service.py:33-34`
- `sp/routes_exec_advisor.py:72,523`
- `bireysel/routes.py:79,277,409,468,645,729,815`
- `app/api/routes.py:277,384`; `app/api/process/performance_routes.py:25,56,137`

---

## 5. Kök neden

1. **Doktrin yazılmış, uygulanmamış.** `date_sovereign.get_view_year()` doğru
   çözümü içeriyor ama tek modül kullanıyor.
2. **Yıl, zincirin her halkasında yeniden türetiliyor.** Merkezden akmak yerine
   her route kendi `date.today().year`'ını çağırıyor.
3. **Opt-in tasarım.** Yıl filtresi `?year` parametresine ve `plan_year_enabled`
   flag'ine bağlı; unutulduğu her yerde sessizce takvim yılına düşüyor.
4. **Model boşlukları.** Proje/Görev/Blue Ocean/VRIO/Süreç-Strateji bağında yıl
   kolonu hiç yok — kod düzeltmesiyle çözülemez, migration gerekir.

**Hatanın sessiz olması bundan:** hiçbir yerde exception yok, ekran yanlış sayıyı
hatasız gösteriyor.

---

## 6. Kabaca faz ayrımı (öneri — onaylanmadı)

| Faz | Kapsam | Maliyet |
|---|---|---|
| 1 | Sessiz yanlış veri: Faz4 top/bottom 5, Masaüstü favori kartlar, Analiz katmanına `year` | Orta |
| 2 | PG yazma kusuru → aktif yıla yaz (`routes_kpi.py:192`) | Düşük |
| 3 | 72 hardcoded nokta → `get_view_year()`; K-Rapor `?year` bağımlılığı | Geniş, mekanik |
| 4 | Model boşlukları: Proje/Görev/Blue Ocean/VRIO/Süreç-Strateji — migration | Yüksek |

**Bu sıralama önerisidir, karar kullanıcınındır.** Uygulama, hasar tespiti
kapanıp öncelik onayı geldikten sonra başlar.
