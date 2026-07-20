# UYGULAMA PLANI — Yıl Bazlı Sistem

> Tarih: 2026-07-20 · Dal: `claude/fix-pg-yil-hedef`
> Dayanak: [`HASAR-TESPITI.md`](HASAR-TESPITI.md) · [`HASAR-TESPITI-2.md`](HASAR-TESPITI-2.md)
> · [`OLCUMLER.md`](OLCUMLER.md) · [`SORULAR.md`](SORULAR.md) (K5-K9, S1-S15, T1-T13)
>
> **Durum: onay bekliyor.** Onay gelene kadar kod değişikliği yok.

---

## 0. Bu plan neye dayanıyor

Tüm kapsam soruları kapandı. Plan hiçbir yerde varsayım kullanmıyor —
her sayı yerel DB'den ölçüldü, her karar `SORULAR.md`'de kayıtlı.

**Belirleyici 5 karar (T9-T13):**

| # | Karar | Sonucu |
|---|---|---|
| T9 | **Full-clone tek mekanizma** | Override tabloları kalkar, 7.789 satır varlığa taşınır |
| T10 | **`PlanProject` ana model** | Proje birleşmesi — veri taşıma pratikte yok (`project`=1, `task`=0) |
| T11 | **Kapalı yıllar taslağa** | 35 `closed` satır draft'a çevrilir, kurum kendi mühürler |
| T12 | **`kpi_data` yılın PG kopyasına** | 366.604 satır remap — geri alınamaz, yedek zorunlu |
| T13 | **Kesintisiz uygulama** | Üç faz arka arkaya, sonda toplu doğrulama |

---

## 1. Mimari hedef — tek cümlede

> Her varlık kendi `plan_year_id`'sini taşır. Yıl **tek yerden** seçilir
> (`session["sp_active_year"]`), **tek çözücüden** okunur (`date_sovereign`),
> ve kapalı yıl **tek kolondan** kilitlenir (`plan_years.status`).

Bugünkü üç kusurun karşılığı:

| Bugün | Hedef |
|---|---|
| İki mekanizma (clone + override) çakışıyor | **Tek mekanizma:** full-clone |
| Yıl 72 noktada yeniden türetiliyor (`date.today().year`) | **Tek çözücü:** `get_view_year()` |
| Mühür isim düzeyinde var, kilit yok | **Tek kilit:** `plan_year_writable_required` |

---

## 2. FAZ 1 — Model + Migration

> **En ağır faz.** Geri alınamaz adım içerir (T12). Yedeksiz başlanmaz.

### 1.0 Ön koşul — yedek (atlanamaz)

```bash
pg_dump  # tam DB, C:\pgdata\bin (>=18)
```
Hedef: `backups/yilbazli/oncesi_<tarih>.dump`. T12 remap'i geri alınamaz.

### 1.1 Eksik `plan_year_id` kolonları

`plan_year_id` **olmayan** ve eklenecek tablolar:

| Tablo | Satır | Not |
|---|---|---|
| `process_sub_strategy_links` | 559 | Süreç–Strateji bağı (T3) |
| `blue_ocean_canvases` | 6 | T3 — agnostik varlık |
| `blue_ocean_errc_items` | — | canvas'a bağlı |
| `blue_ocean_factors` | — | canvas'a bağlı |
| `vrio_resources` | 0 | T3 — tablo boş, kolon yine de eklenir |
| `process_maturity` | 340 | |
| `strategy_process_matrix` | 0 | |
| `strategy_map_link` | 0 | |
| `initiatives` | — | `start_year`/`end_year` yerine gerçek `plan_year_id` |

**T3 kuralı:** ilk göçte mevcut kayıt **tüm yıllara kopyalanır**; sonrası normal
yıl bazlı davranır (2026'daki düzenleme kapalı 2024'e sızmaz).

### 1.2 Boş `plan_year_id` doldurma

Kolon var ama dolu değil:

| Tablo | Toplam | Dolu | **Boş** |
|---|---|---|---|
| `process_kpis` | 1399 | 1211 | **188** |
| `processes` | 380 | 367 | **13** |
| `strategies` | 197 | 186 | **11** |

Kural (S11): tek hedef varsa **tüm yıllara yazılır**. Boş kalanlar kurumun
plan yılı zincirine göre doldurulur.

### 1.3 Plan yılı zinciri üretimi (K6 + T4 + S10)

| Kural | Kaynak |
|---|---|
| Sistem ekseni 2020'de başlar | K6 |
| Her kurum **kendi ilk verisinin yılından** başlar — boş yıl üretilmez | T4 |
| Yeni kurum 2026'dan başlar | K5 |
| Mevcut veri `kpi_data.year`'a göre yıllara dağıtılır | S10 |

Mevcut durum:

| Tenant | Plan yılı | Aralık |
|---|---|---|
| 16 (KMF) | 7 | 2020–2026 |
| 27, 58, 59, 60, 61 | 10 | 2018–2027 |
| 28 | 1 | 2026 |
| 1, 29, 31, 56, 57 | **0** | — |

→ 5 tenant'ta plan yılı hiç yok, üretilecek.

### 1.4 Override → clone göçü (T9)

Kaldırılacak tablolar ve taşınacak satırlar:

| Tablo | Satır | Nereye |
|---|---|---|
| `kpi_year_configs` | 3224 | `process_kpis` yıl kopyalarına |
| `individual_kpi_year_configs` | 1575 | bireysel PG yıl kopyalarına |
| `sub_strategy_year_configs` | 1405 | `sub_strategies` yıl kopyalarına |
| `process_year_configs` | 1035 | `processes` yıl kopyalarına |
| `strategy_year_configs` | 550 | `strategies` yıl kopyalarına |
| **Toplam** | **7.789** | |

**⚠️ Bu göç bir mevcut hatayı da kapatıyor (İ4/H1):** `kpi_year_configs`'in
başarı puanı formatı (`[{"min":…,"puan":…}]`) `parse_basari_puani_araliklari`
tarafından **hiç anlaşılmıyor** — 3145 kaydın tamamı `{}` dönüyor. Göç sırasında
format tek biçime indirgenir.

**Kod tarafı — 116 nokta:**

| Sınıf | Kod noktası |
|---|---|
| `KpiYearConfig` | 53 |
| `StrategyYearConfig` | 23 |
| `SubStrategyYearConfig` | 16 |
| `ProcessYearConfig` | 16 |
| `IndividualKpiYearConfig` | 8 |

Merkezî yardımcılar (`get_kpi_configs_bulk`, `upsert_kpi_year_config`,
`get_kpi_config`) yerlerini korur ama **içleri clone okuyacak şekilde** yeniden
yazılır → çağıran 116 nokta çoğunlukla değişmez.

### 1.5 `kpi_data` remap (T12) — geri alınamaz

366.604 satır, `year` kolonuna göre o yılın PG kopyasına bağlanır.

| PG'nin yayıldığı yıl | PG adedi | Not |
|---|---|---|
| 1 yıl | **913** | kimlik dönüşümü — kopya sayısı 1 |
| 2 yıl | 40 | |
| 3 yıl | 10 | |
| 4 yıl | 16 | |
| 5 yıl | 44 | |

> Gerçek çoklu-yıl remap'i **110 PG**'yi ilgilendiriyor; 1023 PG'nin %89'u tek yıllık.

**⚠️ `kpi_data`'da `tenant_id` YOK.** Zincir:
`kpi_data → process_kpis → processes.tenant_id`. Tüm migration ve mühür
sorguları bu JOIN'i kullanmak zorunda.

`individual_kpi_data` (19.170) için aynı işlem.

### 1.6 Proje birleşmesi (T10)

`PlanProject` ana model. Veri taşıma pratikte yok:

| Tablo | Satır |
|---|---|
| `project` | **1** |
| `task` | **0** |
| `plan_projects` | 21 |
| `plan_project_tasks` | 63 |

İş **kod bağlama** işi: `micro/modules/proje/` CRUD'ı `PlanProject`'e yönlendirilir.
`0bb0ad64` hotfix'i (2026-06-04, `plan_year_id` kaldırma) anlamını yitirir.

### 1.7 `plan_year_enabled` flag'inin kaldırılması (K5)

**22 dosya, 38 kullanım.** Flag kalkar; `false` dalları silinir (o dallar bugün
yıl filtresini tamamen devre dışı bırakıyor).

Etkilenen: `micro/core/launcher.py`, `bireysel/routes.py`, `kurum/routes.py`,
`masaustu/routes.py`, `raporlar/routes_faz3.py`, `sp/routes_donemler.py`,
`sp/routes_pages.py`, `sp/routes_plan_year.py`, `surec/routes_activity.py`,
`surec/routes_karne.py`, `surec/routes_kpi.py`, `surec/routes_kpi_data.py`,
`surec/routes_process.py`, `app/models/core.py`, `app/services/plan_year_service.py`,
`ui/static/platform/js/kurum_ayarlar.js`, `ui/templates/platform/kurum/ayarlar.html`,
`ui/templates/platform/surec/karne.html`, + 4 script.

### 1.8 Seed garantisi (S9)

`vm_apply_plan_years.py` gibi **ham INSERT yolları kapatılır**. Plan yılı yalnızca
`plan_year_service` üzerinden doğar — KMF (#16) ve Eskişehir (#28) hedefli config'inin
sıfır olmasının sebebi tam olarak servis katmanının atlanmasıydı.

---

## 3. FAZ 2 — Mühür

> Faz 1'in `plan_year_id` temeli üstüne kurulur. Öncesinde uygulanamaz.

### 2.1 Devreye alma (T11) — tek seferlik

35 `closed` plan yılı → **draft**. Kurum verisini gözden geçirip kendi mühürler.
Gerekçe: bugünkü `closed` bilinçli bir mühür kararı değildi.

### 2.2 Kilit mimarisi (S15 — onaylı)

| # | Katman | İş |
|---|---|---|
| 1 | `date_sovereign.resolve_plan_year_for_date` | Kapalı yıl döndüğünde **sinyal** verir (bugün `status` filtresi yok, kapalı yılı normalce döndürüyor) |
| 2 | **`plan_year_writable_required` dekoratörü** | Tüm yazma route'larını sarar |
| 3 | DB trigger | Ek güvenlik katmanı |

**Ayrıca düzeltilecek (§13.4 yanıltıcı koruma):**
- `date_sovereign.py:55` — `resolve_plan_year_for_date`'e `status` filtresi
- `date_sovereign.py:87,99` — `entity_exists_in_year`, `plan_year_id` None ise
  koşulsuz `True` dönüyor

### 2.3 Dekoratörle sarılacak yazma yolları (bugün **hepsi korumasız**)

| Dosya | Yol |
|---|---|
| `surec/routes_kpi_data.py:79` | KpiData girişi |
| `surec/routes_kpi_data.py:217` | Excel toplu içe aktarım |
| `surec/routes_kpi_data.py:378` | Veri düzenleme |
| `surec/routes_kpi_data.py:472` | Veri silme |
| `api/routes.py:59,131,157` | Harici API POST/PATCH/DELETE |
| `surec/routes_kpi.py` | ProcessKpi CRUD (tamamı) |
| `surec/routes_activity.py` | Faaliyet takip |
| `surec/routes_process.py` | Süreç CRUD |
| `bireysel/routes.py` | Bireysel PG düzenle/sil + veri girişi |
| `sp/routes_analysis.py` | SWOT/TOWS/PESTEL/Porter/BSC/OKR |
| `sp/routes_strategy.py` | Strateji CRUD |
| `proje/*` | Proje/görev CRUD |

### 2.4 Açma yolu (K9 + S13 + T1)

Bugün **hiç yok** — `status="active"` ataması yapan tek route bile bulunmuyor.

| İş | Detay |
|---|---|
| Açma route'u | Yetki: kurum üst yönetimi (K9) |
| **Gerekçe alanı zorunlu** | S13 |
| **Denetim tablosu** | kim / ne zaman / **neden** açtı (S13) |
| Tolerans yok | T1 — gecikmeli veri için tek yol mührü açmak |

### 2.5 Arayüz (T7)

| # | İş |
|---|---|
| A | Dönemler sayfası **SP menüsüne** eklenir — "Plan Dönemleri" (bugün hiçbir menüde yok) |
| B | Mühür işlemleri orada toplanır: kapat + aç + gerekçe modalı + denetim geçmişi |
| C | Yönetici Paneli'ne **durum göstergesi + kısayol** (görür, yönetmez) |
| D | Sidebar'a ekleme **ertelendi** — İ1 çözülmeden menü kalabalıklaştırılmaz |
| E | Onay metni yeniden yazılır — "geri alınamaz" artık geçersiz (K9) |
| F | `close_plan_year` docstring'i gerçeğe uydurulur |

### 2.6 Güvenlik (S14)

`routes_plan_year.py:172` `@csrf.exempt` **kaldırılır**.

---

## 4. FAZ 3 — Yıl Akışı

> Kullanıcının seçtiği yılın ekrana kadar ulaşması.

### 3.1 Backend session fallback (S8) — **en yüksek kazanç/maliyet oranı**

40+ fetch çağrısını tek tek düzeltmek yerine: **backend'de `?year` yokken
`session["sp_active_year"]`'a düş.**

Bu tek karar K-Radar'ın ~37 yılsız çağrısını, `sp_analiz.js` (4), `sp_bsc.js` (3),
`analiz.js` (4), `masaustu.js` (5), `surec.js` (6) çağrılarını **kod değişikliği
olmadan** doğru yıla oturtur.

### 3.2 72 hardcoded nokta → `get_view_year()`

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
| `micro/modules/api` · `micro/core` · `app/models` | 1+1+1 |

Öncelik (sessizce yanlış veri gösterenler):
`raporlar/routes_faz4.py:198,207,219,227` · `routes_faz3.py:557,768` ·
`masaustu/routes.py:143,182,233,318` · `surec/routes_karne.py:212,582` ·
`score_engine_service.py:114,322,454` · `analytics_service.py:135` ·
`process_health_service.py:53` · `report_service.py:186` · `cache_service.py:33-34`

### 3.3 K-Radar / Analiz katmanı — yıl kavramı yok

`analiz/routes.py` ve `analytics_service.py` yıl eksenine oturtulur:
trend (son 365 gün → plan yılı), sağlık skoru, tahmin, karşılaştırma, anomali.

### 3.4 Bireysel katman (S7)

`IndividualKpiYearConfig` ölü model — yazılıyor, hiç okunmuyor. T9 ile clone'a
göçtükten sonra **okuma yolu yazılır**; bireysel hedefler yıllara göre değişir.

### 3.5 Arka plan görevleri (S6)

Session yok → `get_view_year()` kullanılamaz. Zamanlayıcılar **tenant'ın aktif
PlanYear'ını** kullanır. Bugün gece görevi (`early_warning_service.py:82,90`)
takvim yılına, dashboard API'si plan yılına bakıyor — **çelişik**.

### 3.6 PG yazma kusuru (K1) — asıl tetikleyici bulgu

`surec/routes_kpi.py:192-199` `target_value`/`weight`/`period`/`direction`/
`basari_puani_araliklari` alanlarını **yılsız** `ProcessKpi`'ye yazıyor.

> 2026'da yapılan hedef değişikliği **2025 karnesini geriye dönük bozuyor.**

T9 sonrası bu kendiliğinden çözülür (yazma aktif yılın kopyasına gider), ama
`surec_api_kpi_get` (`:143-173`) da `?year` okumadığı için düzenleme modalı ham
değeri gösteriyor — **ikisi aynı commit'te** düzeltilir.

### 3.7 Çoklu yıl seçici temizliği (T8)

| # | İş |
|---|---|
| A | PK04'teki seçici kaldırılır (`karne.html:293-298`) |
| B | Üstteki kalır, etiket **"Plan Yılı"** (`karne.html:99`) |
| C | Senkron kodu temizlenir (`surec.js:205`, `surec.js:3138`) |
| D | Yıl listesi **her zaman** gerçek plan yıllarından; `range(...)` dalı silinir |
| E | `.po` güncellenir — msgid "Plan Yılı" |

+ Aynı desen için **tüm sayfalarda çoklu yıl seçici taraması**.

---

## 5. Doğrulama (T13 gereği önceden yazılır)

Betik: `scripts/ops/yilbazli_dogrulama.py` — salt okunur.

| # | Kontrol |
|---|---|
| 1 | Her varlık tablosunda `plan_year_id` **NOT NULL** ve dolu |
| 2 | `kpi_data` satır sayısı **366.604 sabit** — remap kayıp vermedi |
| 3 | Her `kpi_data` satırının PG'sinin `plan_year_id`'si, satırın eski `year`'ına eşit |
| 4 | Override tabloları **boş / kaldırılmış**, karşılığı clone'da |
| 5 | `date.today().year` kalıntısı: `micro/` + `app/` altında **0** |
| 6 | `plan_year_enabled` kalıntısı: **0** |
| 7 | Kapalı yıla yazma denemesi → **reddedilir** (her yazma yolu için test) |
| 8 | Mühür açma → denetim kaydı + gerekçe **zorunlu** |
| 9 | Tenant başına: seçilen yıl değişince K-Radar/K-Rapor/Karne **farklı veri** döndürür |
| 10 | 602 mevcut test + `test_statik_dosya_varligi.py` yeşil |

**Tenant kapsamı (T5):** 12 tenant, 4 Tomofil klonu (58/60/61 + 27) **dahil**.
Kullanıcı: *"hepsini yapalım, gerekirse uzun sürsün"* — bütünlük performanstan önce.

---

## 6. Kapsam dışı — bu programda YAPILMAZ

| # | İş | Nerede |
|---|---|---|
| İ1 | "Kurum Paneli" isim karmaşası | `SONRAKI-ISLER.md` |
| İ2 | Kart açıklama zenginleştirme (405 kart) | `docs/kontrol/KART-ACIKLAMA-DEVIR.md` |
| İ3 | **D0 — 438 gösterge ters hesaplanıyor** | `KART-VERI-TUTARSIZLIKLARI.md` |
| İ4 | Başarı puanı 0 ekleme (11 nokta) | `SONRAKI-ISLER.md` |

**İ3 istisnası:** D0 (`lower_is_better` ölü koşulu, `k_rapor/routes.py:991,1901,2161`)
3 satırlık düzeltme ve Faz 3 zaten aynı dosyalara dokunuyor. **Kullanıcı isterse**
Faz 3 içinde birlikte düzeltilebilir — ayrı karar.

**İ4 kesişimi:** H1 (yıl bazlı başarı puanı formatı hiç çalışmıyor) Faz 1.4'te
override göçüyle **zorunlu olarak** ele alınır — 0 puan özelliği değil, format
tekleştirmesi olarak.

---

## 7. Risk tablosu

| Risk | Etki | Önlem |
|---|---|---|
| **T12 remap geri alınamaz** | 366K satır | Faz 1.0 tam yedek + doğrulama #2/#3 |
| Override göçünde veri kaybı | 7.789 satır | Göç öncesi/sonrası satır sayısı kıyası |
| 116 kod noktası kaçırılması | Sessiz yanlış veri | Merkezî yardımcılar korunur → çağıran değişmez |
| Kilit fazla sıkı → kurum çalışamaz | Kullanım engeli | T11 (kapalı yıllar taslağa) + K9 açma yolu |
| 4 Tomofil klonu migration süresi | 366K satırın %98'i | T5 — süre kabul edildi |
| `kpi_data`'da `tenant_id` yok | Yanlış JOIN → çapraz tenant | Her sorguda `→ process_kpis → processes` zinciri |
| Yayın'a taşıma | Müşteri verisi | K4 — **tüm iş yerelde**, Yayın'a dokunulmaz |

---

## 8. Onay noktası

Bu plan onaylanınca (T13) üç faz **kesintisiz** uygulanır:

```
Faz 1 (model+migration) → Faz 2 (mühür) → Faz 3 (yıl akışı) → toplu doğrulama
```

Her faz kendi commit'inde. Hata çıkarsa orada durulur ve rapor edilir.

**Onay bekleyen ek karar:** İ3 (D0 ters hesaplama) Faz 3'e dahil edilsin mi?
