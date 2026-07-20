# HASAR TESPİTİ — 2. TUR (Derin Analiz)

> Tarih: 2026-07-20 · 4 ek paralel denetim + tenant bazlı DB ölçümü
> Devamı: [`HASAR-TESPITI.md`](HASAR-TESPITI.md)

---

## 7. Bireysel performans katmanı — **ölü model bulundu**

`IndividualKpiYearConfig` ([`app/models/plan_year.py:260`](../../app/models/plan_year.py#L260))
modeli var, seed ve clone ediliyor ([`plan_year_service.py:176,405`](../../app/services/plan_year_service.py#L176))
— **ama hiçbir okuma yolu yok.** `get_kpi_configs_bulk`'ın bireysel eşdeğeri
hiç yazılmamış.

> **Sonuç: model ölü kod.** Tüm bireysel ekranlar yılsız
> `IndividualPerformanceIndicator.target_value` okuyor. Yıl bazlı bireysel hedef
> yazılıyor ama hiçbir zaman okunmuyor.

| Ekran / Servis | Yıl filtresi | Yıl kaynağı | Hedef kaynağı | Kaynak |
|---|---|---|---|---|
| Bireysel ana sayfa | ❌ | `datetime.now().year` | — | `bireysel/routes.py:79,94` |
| Bireysel PG oluştur | ⚠️ | session (doğru) | `target_value` yazılır, **`IndividualKpiYearConfig` oluşturulmaz** | `routes.py:151-202` |
| **Bireysel PG güncelle** | ❌ | — | `pg.target_value` **yılsız ezilir** | `routes.py:235` |
| Bireysel veri girişi | ✅ | `data_date.year` (tarih egemen) | `IndividualKpiData.year` | `routes.py:277-326` ✅ doğru |
| Faaliyet takip | ⚠️ | `data.get("year", now().year)` — session değil | — | `routes.py:409,414,422` |
| Bireysel karne API | ⚠️ | `?year` → `now().year`, session fallback yok | **yılsız `pg.target_value`** | `routes.py:468,474,494,522` |
| Bireysel PG detay | ⚠️ | `?year` + hardcoded | yılsız | `routes.py:645,651,681` |
| Bireysel karne PDF | ⚠️ | `?year` + `date.today().year` | yılsız | `routes.py:729,745,760` |
| Bireysel AI özet | ⚠️ | `?year` + hardcoded | — | `routes.py:815,826` |

### 7.1 `date_sovereign` gerçek kullanımı — satır satır

Import: [`bireysel/routes.py:30-35`](../../micro/modules/bireysel/routes.py#L30) —
5 fonksiyon import ediliyor.

**Gerçek kullanım tek blokta:** `routes.py:296-307` (veri girişi).
`get_view_year` yalnızca `:306`'da, **sadece pasif rozet üretmek için**.

Diğer 8 rotanın hiçbiri onu çağırmıyor; yanı başlarında `datetime.now().year`
duruyor (`:79, :277, :409, :468, :645, :729, :815`).

> Yani "tek kullanıcı modül" bile doktrini sadece dekoratif olarak kullanıyor.

### 7.2 Süreç karne — bu katmanda doğru

[`surec/routes_karne.py:212,253-254,349`](../../micro/modules/surec/routes_karne.py#L253)
`KpiYearConfig` bulk overlay kullanıyor ✅. Yıl kaynağı `?year` + hardcoded fallback ⚠️.

---

## 8. Erken uyarı — session'sız bağlam sorunu

| Servis | Sorun | Kaynak |
|---|---|---|
| Erken uyarı **gece görevi** (02:00) | Session yok → `today.year`'a **sabitlenmiş**; yılsız hedefle karşılaştırıyor | `services/early_warning_service.py:46,82,90`; `app/__init__.py:671-689` |
| Erken uyarı **dashboard API** | PG'yi plan year'a göre filtreliyor ama **`KpiData`'yı yıla göre hiç filtrelemiyor** | `raporlar/routes_faz1.py:817-850` |
| Bildirim modülü | Yıl kavramı **yok** | `shared/bildirim/routes.py` |

> İki uç birbiriyle **çelişik**: gece görevi takvim yılına bakıyor, dashboard
> plan yılına. Aynı uyarı iki farklı yıl bağlamında üretiliyor.

**Mimari not:** Arka plan görevlerinde `session` yoktur. `get_view_year()`
session'a bağlı olduğu için zamanlayıcılarda **kullanılamaz** — bu katman için
ayrı bir yıl kaynağı kararı gerekir (tenant'ın aktif PlanYear'ı?).

---

## 9. Frontend — yıl taşıma mimarisi yok

### 9.1 Yıl seçim mekanizması

4 ayrı implementasyon, aynı desen:
`sp_plan_year.js`, `masaustu_plan_year.js`, `launcher_plan_year.js`, `k_rapor.js:95-114`

Davranış: `POST /k-plan/strategy/api/plan-years/set-active {year}` → session'a yazar
→ **`window.location.reload()`**. JS state yok, tam sayfa reload.

### 9.2 API çağrılarında `?year` dökümü

| JS dosyası | API çağrısı | year gönderen | göndermeyen | Risk |
|---|---|---|---|---|
| `k_rapor.js` | 25 | **21** | 4 (kasıtlı, yılsız sekmeler) | 🟢 DÜŞÜK |
| **`k_radar.js`** | ~30 | **0** | hepsi | 🔴 **YÜKSEK** |
| **`k_radar_ks.js`** | 7+ | **0** | hepsi | 🔴 **YÜKSEK** |
| **`sp_analiz.js`** | 4 | **0** | 4 | 🔴 YÜKSEK (yıl-kritik) |
| **`sp_bsc.js`** | 3 | **0** | 3 | 🔴 YÜKSEK |
| `analiz.js` | 4 | 0 | 4 | 🟠 ORTA |
| `masaustu.js` | 5 | 0 | 5 | 🟠 ORTA |
| `surec.js` | 8 | 2 (`:567`) | 6 | 🟠 ORTA |
| `bireysel.js` | 3 | 2 (`:273,:310`) | 1 | 🟢 DÜŞÜK |
| `pg_tablo_modal.js` | 1 | 1 | 0 | 🟢 DÜŞÜK |
| `kurum.js`/`kule.js`/`sp.js` | 2/2/2 | 0 | hepsi | 🟢 (yıl-agnostik) |

### 9.3 Tek doğru modül: K-Rapor

`k_rapor.js` `fetchJson(url, params)` wrapper kullanıyor (`:60-66`); yıl
`ROOT.dataset.year` ← `index.html:32` `data-year="{{ year }}"` üzerinden geliyor
— proje kuralına (data-* attribute) uygun.

**`data-year` sadece 4 yerde var:** `k_rapor/index.html:32` (tek fonksiyonel olan),
`sp/donemler.html:72,115`, `sp/sihirbaz_yeni_yil.html:29`.

### 9.4 Kritik sonuç

> **K-Radar'ın ~37 API çağrısının hiçbiri yıl göndermiyor** ve backend'i de
> session'a bakmıyor (§3.2). Yani K-Radar yıl seçicisinden bağımsız çalışıyor —
> **yıl seçicisi görsel olarak çalışıyor gibi görünüp veriyi filtrelemiyor.**

Yıl değişince ekran yenileniyor ama bu **yalnızca full page reload sayesinde**;
hiçbir dosyada "yıl değişti → grafik yeniden yükle" event'i yok.

**Tasarım önerisi (denetimden):** 40+ fetch çağrısını tek tek düzeltmek yerine,
backend'de `?year` yokken `session["sp_active_year"]`'a düşmek çok daha güvenli.

---

## 10. Proje modülü — `plan_year_id` neden kaldırıldı (S3 cevabı)

**Gerekçe mimari karar DEĞİL — hotfix.**

Kod yorumu ([`routes_project_crud.py:184-186`](../../micro/modules/proje/routes_project_crud.py#L184)):

```
# Not: Project modelinde plan_year_id kolonu yok (proje↔plan-yıl bağı plan_projects'te).
# Sprint 53'te eklenen plan_year_id referansı kaldırıldı — model/DB'de karşılığı olmadığı
# için proje oluşturmayı 500'le düşürüyordu.
```

| Commit | Tarih | Ne yaptı |
|---|---|---|
| `973256c7` | 2026-05-24 | S53-S57 SP paketi — `plan_year_id`'yi **ekleyen** commit |
| `0bb0ad64` | 2026-06-04 | **Kaldıran** commit: "model/DB'de olmayan plan_year_id referansı kaldırıldı" |

Commit gövdesi: `Project(...)` constructor'ına `plan_year_id` geçiliyordu ama
`project` tablosunda kolon **yok** → SQLAlchemy invalid-keyword → TypeError → 500.
Değer hiçbir yerde okunmuyordu (ölü referans).

**ADR/karar belgesi bulunamadı** — tek gerekçe kaynağı commit mesajı ve kod yorumu.

### 10.1 İki ayrı proje sistemi — isim çakışması

| Dosya | Sınıf | Tablo | Yıl | Kullanım |
|---|---|---|---|---|
| `app/models/portfolio_project.py` | `Project`, `Task` | `project`, `task` | ❌ yok | **Aktif** — `micro/modules/proje/` CRUD |
| `app/models/project.py` | `PlanProject`, `PlanProjectTask`, `PlanProjectActivity` | `plan_projects` … | ✅ `plan_year_id` NOT NULL + `source_project_id` (yıl devri) | SP tarafı |

İkisi de canlı. Proje↔plan-yıl bağı **tasarım gereği** `plan_projects`'te.
Karışıklığın kaynağı: SP modülü eski dosya adını (`project.py`) devralmış,
portföy modeli `portfolio_project.py`'ye taşınmış.

> **Karar gerekiyor:** "Projeler yıl bazlı olmalı" isteği hangi sistemi kastediyor?
> Portföy `Project`'ine yıl eklemek mi, yoksa iki sistemi birleştirmek mi?

---

## 11. Tenant bazlı gerçek durum (yerel DB ölçümü)

| id | Kurum | flag | Plan yılı | Süreç | PG | cfg | **hedefli cfg** |
|---|---|---|---|---|---|---|---|
| 1 | Default Corp | ❌ | 0 | 2 | 0 | 0 | 0 |
| **16** | **Kayseri Model Fabrika** | ✅ | 7 | 11 | 121 | 7 | **0** |
| **27** | **Tomofil Otomotiv** | ✅ | 10 | 71 | 220 | 640 | **640** |
| **28** | **Eskişehir Makine** | ✅ | 1 | 12 | 101 | 0 | **0** |
| 29 | Kara Brothers | ❌ | 0 | 0 | 0 | 0 | 0 |
| 31 | VolTure Tech | ❌ | 0 | 0 | 0 | 0 | 0 |
| 56 | Yeniçağ Yazılım | ❌ | 0 | 0 | 0 | 0 | 0 |
| 57 | YeniTomofil | ❌ | 0 | 0 | 0 | 0 | 0 |
| 58-61 | tomofiltest, tom1-3 | ❌ | 10 | 71 | 220 | 640 | 640 |

**Özet:** 12 aktif tenant · flag **açık 3** · kapalı 9 · hedefli cfg satırı olan 5

### Kritik gözlem

> **Yıl sistemi açık 3 kurumdan 2'sinde (KMF #16, Eskişehir #28) yıl bazlı hedef
> HİÇ yok.** Sadece Tomofil (#27) ve onun kopyaları düzgün seed'lenmiş (640 satır).

- **KMF #16**: 7 plan yılı, 121 PG, ama sadece 7 cfg satırı ve **0 hedefli** →
  `vm_apply_plan_years.py` ham INSERT'ü seed'i atlamış (bkz `OLCUMLER.md` §1).
- **Eskişehir #28**: 1 plan yılı, 101 PG, **0 cfg** → aynı boşluk.
- **Flag kapalı ama plan yılı olan tenant'lar** (#58-61): veri var, flag kapalı
  olduğu için **hiç kullanılmıyor**.

Bu, seed açığının KMF'ye özgü olmadığını, **sistemik** olduğunu gösteriyor.

---

## 12. Güncellenmiş kök neden tablosu

| # | Kök neden | Kanıt |
|---|---|---|
| 1 | Doktrin yazılmış, uygulanmamış | `date_sovereign` 1 modülde, o da sadece rozet için |
| 2 | Yıl her halkada yeniden türetiliyor | 72 hardcoded nokta |
| 3 | Opt-in tasarım | `?year` + `plan_year_enabled` — unutulan her yerde takvim yılı |
| 4 | Model boşlukları | Proje/Görev/Blue Ocean/VRIO/Süreç-Strateji |
| 5 | **Ölü model** | `IndividualKpiYearConfig` yazılıyor, hiç okunmuyor |
| 6 | **Frontend'de yıl taşıma mimarisi yok** | K-Rapor hariç 40+ çağrı yılsız |
| 7 | **Seed açığı sistemik** | 3 flag-açık tenant'ın 2'sinde hedefli cfg = 0 |
| 8 | **Arka plan görevlerinde yıl kaynağı tanımsız** | Session yok → `today.year` |

---

## 13. MÜHÜR DENETİMİ — kapalı yıl korumasız (2026-07-20, kullanıcı gereksinimi üzerine)

**Kullanıcı gereksinimi:** Kapanmış bir yıla **asla** veri girişi/düzenleme/silme
olmamalı. Sadece kurum üst yönetimi mührü açıp yılı tekrar aktif yapabilmeli.

**Denetim sonucu: mühür isim düzeyinde var, uygulama düzeyinde YOK.**

### 13.1 Açma (mühür kaldırma) route'u: **YOK**

Tüm kod tabanında `status = "active"` ataması yapan **hiçbir route yok**.
`reopen` / `unseal` / "mühür kaldır" anlamına gelen hiçbir endpoint, servis
fonksiyonu veya UI aksiyonu bulunmuyor.

> Bir yıl kapatıldığında uygulama arayüzünden **geri açmanın hiçbir yolu yok** —
> kurum üst yönetimi dahil. Geri dönüş sadece doğrudan DB müdahalesiyle mümkün.

Gereksinimin ikinci yarısı **hiç uygulanmamış**.

### 13.2 Koruma OLAN yerler — sadece 2 endpoint

| Dosya:satır | Route | Not |
|---|---|---|
| `sp/routes_plan_year.py:179` | `.../close` | Idempotency, koruma değil |
| `sp/routes_plan_year.py:231` | `.../kpi-configs/<kpi_id>` | ✅ gerçek koruma |
| `sp/routes_plan_year.py:264` | `.../kpi-configs/bulk` | ✅ gerçek koruma |

İkisi de yalnızca **yıllık KPI hedef konfigürasyonu**. Veri girişinin hiçbirinde yok.

### 13.3 Koruma OLMAYAN yazma yolları — KRİTİK

`micro/**/*.py` altında `"closed"` geçen tek route dosyası `routes_plan_year.py`.
Diğer tüm yazma yolları korumasız:

| Dosya:satır | Yazma yolu |
|---|---|
| `surec/routes_kpi_data.py:79` | **KpiData girişi** |
| `surec/routes_kpi_data.py:217` | Excel toplu içe aktarım |
| `surec/routes_kpi_data.py:378` | Veri düzenleme |
| `surec/routes_kpi_data.py:472` | **Veri silme** |
| `api/routes.py:59,131,157` | **Harici API** — POST/PATCH/DELETE `kpi-data` |
| `surec/routes_kpi.py` (tamamı) | ProcessKpi CRUD |
| `surec/routes_activity.py` | Faaliyet takip |
| `surec/routes_process.py` | Süreç CRUD (sadece rol kontrolü `:452`) |
| `bireysel/routes.py:~226,~251,~270-310` | Bireysel PG düzenle/sil + veri girişi |
| `sp/routes_analysis.py` | SWOT/TOWS/PESTEL/Porter/BSC/OKR (sadece rol) |
| `sp/routes_strategy.py` | Strateji CRUD |
| `proje/*` | Proje/görev CRUD (`closed` hiç geçmiyor) |

> **Sonuç: Kapalı bir yıla serbestçe veri girilebiliyor, düzenlenebiliyor ve
> silinebiliyor.**

### 13.4 Yanıltıcı "koruma" — tarih egemen kontrol yıl durumuna bakmıyor

`routes_kpi_data.py:121-136` ve `bireysel/routes.py:~292-305`'te
`plan_year_enabled` açık tenant'lar için bir kontrol var, **ama yılın kapalı olup
olmadığına bakmıyor**:

- [`date_sovereign.py:55`](../../app/services/date_sovereign.py#L55)
  `resolve_plan_year_for_date` → `filter_by(tenant_id=..., year=y).first()` —
  **status filtresi yok**, kapalı yılı normalce döndürüyor
- [`date_sovereign.py:87`](../../app/services/date_sovereign.py#L87)
  `entity_exists_in_year` → yalnızca `plan_year_id` eşleşmesi; `plan_year_id`
  None ise koşulsuz `True` (`:99`)

> `data_date="2024-06-30"` ile yapılan giriş, kapalı 2024 PlanYear'ını çözer,
> varlık kontrolünü geçer ve **kaydı kapalı yıla yazar**.

### 13.5 `close_plan_year` ne yapıyor

[`plan_year_service.py:297-313`](../../app/services/plan_year_service.py#L297) —
sadece iki alan:

```python
plan_year.status = "closed"
plan_year.closed_at = datetime.now(timezone.utc)
```

**Başka hiçbir kilit yok:** DB trigger yok, ilgili kayıtlara `is_locked`/`frozen`
bayrağı basılmıyor, snapshot/checksum alınmıyor, `Process`/`ProcessKpi`/`KpiData`
salt-okunur hale gelmiyor.

Docstring'in iddiası ("Kapalı bir yıl artık düzenlenemez") **kodda karşılığı
olmayan bir yorum**.

### 13.6 Kapatma yetkisi

`sp/routes_plan_year.py:171-190` → `@sp_manage_required` → roller:
`Admin`, `admin`, `tenant_admin`, `executive_manager`, `kurum_yoneticisi`, `ust_yonetim`

⚠️ Route `@csrf.exempt` (`:172`) — kapatma tek yönlü ve **geri alınamaz** bir işlem
olduğu için CSRF muafiyeti ayrıca riskli.

### 13.7 Önerilen yapısal düzeltme

Endpoint başına elle `if` eklemek bu kadar çok yazma yolunda **tekrar kaçırılmaya
açık**. Doğal nokta:

1. `date_sovereign.resolve_plan_year_for_date` — kapalı yıl döndüğünde çağıranı
   zorlayacak bir sinyal
2. Tüm yazma route'larını saran ortak bir **`plan_year_writable_required`
   dekoratörü**
3. Açma route'u + yetki (üst yönetim) + denetim izi (kim, ne zaman, neden açtı)
