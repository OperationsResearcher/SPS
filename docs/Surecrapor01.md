# Süreç Yönetimi — Teknik Rapor (Surecrapor01)

**Belge:** Kokpitim — Süreç Yönetimi modülü  
**Tarih:** 2026-03-19  
**Kapsam:** Micro platformdaki güncel süreç yönetimi (`/process`), veri modelleri, API’ler, veri işleme ve ilgili entegrasyonlar; ayrıca kod tabanında var olan **eski (legacy)** süreç modeli özeti.

---

## 1. Özet

Kokpitim’de “Süreç Yönetimi”, kurum (tenant) bazlı **iş süreçlerini** hiyerarşik olarak tanımlama, bunları **strateji (alt strateji)** ile ilişkilendirme, her süreç için **performans göstergeleri (PG / KPI)** ve **faaliyetler** yönetme, **periyodik veri girişi** ve **süreç karnesi** üzerinden izleme işlevlerini kapsar.

Güncel kullanıcı arayüzü ve REST uçları **`micro/modules/surec/`** altında, veri modeli **`app/models/process.py`** içindedir. Kod tabanında paralel olarak **`models/process.py`** içindeki **`Surec`** tabanlı **eski şema** (kurum / `user` / `alt_strateji`) hâlâ bulunur; proje yönetimi gibi bazı modüller legacy `Surec` ile bağ kurabilir. **Micro ana süreç ekranları** ise **`Process`** (tablo: `processes`) üzerinden çalışır.

---

## 2. Kullanıcıya Açılan Sayfalar (Micro)

Tüm yollar uygulama köküne göredir (ör. `http://127.0.0.1:5001/...`). Giriş gerektirir (`@login_required`).

| URL | Açıklama | Şablon |
|-----|----------|--------|
| **`GET /process`** | Süreç listesi / hiyerarşik ağaç; erişilebilir süreçler rol ve atamaya göre filtrelenir; süreç oluşturma-düzenleme modalı (yetkiye bağlı) | `micro/surec/index.html` |
| **`GET /process/<id>/karne`** | Seçilen sürecin **karnesi**: PG’ler, yıllık periyot bazlı değerler, faaliyet özetleri (AJAX ile `/process/api/karne/...`) | `micro/surec/karne.html` |
| **`GET /process/<id>/faaliyetler`** | Süreç **faaliyetleri** ve **aylık takip** arayüzü | `micro/surec/faaliyetler.html` |

### 2.1 Eski URL uyumluluğu

| URL | Davranış |
|-----|----------|
| **`/surec`**, **`/surec/`** | **`307`** ile **`/process`** yönlendirmesi |
| **`/surec/<path>`** | **`307`** ile **`/process/<path>`** (ör. eski yer imleri) |

Kaynak: `micro/modules/surec/routes.py` (dosya sonu redirect fonksiyonları).

### 2.2 Modül menüsü

`micro/core/module_registry.py` içinde modül kimliği `surec`, görünen ad **“Süreç Yönetimi”**, giriş URL’si **`/process`**.

---

## 3. Veri Modeli — Güncel (Micro / `app.models.process`)

Aşağıdaki tablolar ve ilişkiler süreç yönetiminin ana verisidir.

### 3.1 `processes` — `Process`

- **Kimlik:** `id`, `tenant_id`, isteğe bağlı `parent_id` (hiyerarşi).
- **Tanım:** `code`, `name`, `english_name`, `description`.
- **KYS / doküman:** `document_no`, `revision_no`, `revision_date`, `first_publish_date`, `weight`.
- **Durum:** `status`, `progress`, `start_date`, `end_date`, `start_boundary`, `end_boundary`.
- **Yaşam döngüsü:** `is_active`, `deleted_at`, `deleted_by`, zaman damgaları.
- **Roller (çoktan çoğa):**
  - `process_leaders` — liderler  
  - `process_members` — üyeler  
  - `process_owners_table` — sahipler  
- **Alt süreçler:** `parent` / `sub_processes` self-referans ilişkisi.

### 3.2 `process_sub_strategy_links` — `ProcessSubStrategyLink`

Süreç ile **alt strateji** arasında bağ; isteğe bağlı **`contribution_pct`** (katkı yüzdesi).  
İş kuralı: Süreç oluşturma/güncellemede **en az bir alt strateji** bağlantısı zorunludur (`_apply_sub_strategy_links`).

### 3.3 `process_kpis` — `ProcessKpi` (Süreç PG)

- Sürece bağlı KPI tanımı: ad, kod, açıklama, hedef, birim, periyot.
- Veri toplama: `data_source`, `target_setting_method`, `data_collection_method` (ör. Toplama, Ortalama, Son Değer), `calculation_method`.
- Eski proje uyumu: `gosterge_turu`, `target_method`, `basari_puani_araliklari` (JSON metin), `onceki_yil_ortalamasi`.
- Ağırlık / önem: `weight`, `is_important`, `direction` (Increasing/Decreasing), `calculated_score`.
- İsteğe bağlı `sub_strategy_id` ile alt strateji bağlantısı; tarih aralığı `start_date`, `end_date`.

### 3.4 `kpi_data` — `KpiData` (PG verisi)

Periyodik gerçekleşen / hedef değer girişleri:

- `process_kpi_id`, `year`, `data_date`
- `period_type`, `period_no`, `period_month` (sihirbaz / periyot tanımı ile uyumlu)
- `target_value`, `actual_value`, `status`, `status_percentage`, `description`
- `user_id` (giren kullanıcı), soft delete: `is_active`, `deleted_at`, `deleted_by_id`

### 3.5 `kpi_data_audits` — `KpiDataAudit`

PG verisi için **CREATE / UPDATE / DELETE** denetim kaydı (`old_value`, `new_value`, `action_detail`, `user_id`, `created_at`).

### 3.6 `process_activities` — `ProcessActivity`

Süreç faaliyeti: ad, açıklama, tarihler, durum, ilerleme; isteğe bağlı `process_kpi_id` ile PG ile ilişki.

### 3.7 `activity_tracks` — `ActivityTrack`

Faaliyet için **yıl + ay** bazlı tamamlanma (`completed`); `(activity_id, year, month)` tekil kısıtı.

### 3.8 `favorite_kpis` — `FavoriteKpi`

Kullanıcı başına favori PG (`user_id`, `process_kpi_id`, `sort_order`, `is_active`).

### 3.9 Bireysel tarafla ortak model (aynı dosyada)

`IndividualPerformanceIndicator`, `IndividualActivity`, `IndividualKpiData`, `IndividualKpiDataAudit`, `IndividualActivityTrack` — bireysel performans modülü; süreç PG’sinden **`source_process_kpi_id`** ile eşleme yapılabilir (`micro/modules/bireysel/routes.py` içinde süreçten bireysel PG türetme API’si).

---

## 4. Veri İşleme — API ve İş Mantığı

Tüm süreç API’leri **`micro/modules/surec/routes.py`** içinde; önek **`/process/api/...`**. İstekler JSON gövdeli (`POST`/`PUT`) veya sorgu parametreli (`GET`) olabilir.

### 4.1 Süreç CRUD

| Endpoint | İşlev |
|----------|--------|
| `POST /process/api/add` | Yeni süreç (yetki: `can_crud_process_entity`) |
| `GET /process/api/get/<process_id>` | Süreç detayı |
| `POST /process/api/update/<process_id>` | Güncelleme (lider/sahip veya ayrıcalıklı) |
| `POST /process/api/delete/<process_id>` | Soft delete (yetki: tam süreç CRUD) |

Validasyon örnekleri: `validate_process_parent_id`, alt strateji listesi `validate_same_tenant_sub_strategies`, lider/üye/sahip kullanıcı ID’lerinin tenant kontrolü.

### 4.2 PG (KPI) CRUD

| Endpoint | İşlev |
|----------|--------|
| `POST /process/api/kpi/add` | PG ekleme |
| `GET /process/api/kpi/get/<kpi_id>` | PG detayı |
| `POST /process/api/kpi/update/<kpi_id>` | PG güncelleme |
| `POST /process/api/kpi/delete/<kpi_id>` | PG silme/devre dışı |
| `GET /process/api/kpi/list/<process_id>` | Sürece ait PG listesi |

Yetki: `user_can_crud_pg_and_activity` (lider/sahip veya ayrıcalıklı roller).

### 4.3 PG verisi (KpiData)

| Endpoint | İşlev |
|----------|--------|
| `POST /process/api/kpi-data/add` | Yeni veri satırı; periyot son günü `last_day_of_period` ile hesaplanabilir |
| `GET /process/api/kpi-data/list/<kpi_id>` | Liste |
| `GET /process/api/kpi-data/history/<kpi_id>` | Geçmiş |
| `GET /process/api/kpi-data/detail` | Detay |
| `POST,PUT /process/api/kpi-data/update/<data_id>` | Güncelleme |
| `POST,DELETE /process/api/kpi-data/delete/<data_id>` | Soft delete + audit |
| `GET /process/api/kpi-data/proje-gorevleri` | İlgili proje görevleri (entegrasyon) |

Satır düzenleme yetkisi: `user_can_edit_kpi_data_row` (ayrıcalıklı, süreç lideri/sahibi veya veriyi giren kullanıcı).

### 4.4 Faaliyet ve aylık takip

| Endpoint | İşlev |
|----------|--------|
| `POST /process/api/activity/add` | Faaliyet ekle |
| `GET /process/api/activity/get/<act_id>` | Detay |
| `POST /process/api/activity/update/<act_id>` | Güncelle |
| `POST /process/api/activity/delete/<act_id>` | Sil |
| `POST /process/api/activity/track/<act_id>` | Aylık track (yıl/ay, `completed`) |

### 4.5 Karne birleşik veri — `GET /process/api/karne/<process_id>`

- Parametre: `year` (varsayılan iç yıl).
- Dönen JSON: süreç özeti, `kpis[]`, `activities[]`, `favorite_kpi_ids`, `permissions`.
- **PG değerlerinin periyotlara dağıtımı:**
  - Her `KpiData` kaydı için `data_date` üzerinden `data_date_to_period_keys()` ile anahtarlar üretilir (`ceyrek_*`, `aylik_*`, `yillik_1`, `haftalik_*`, `gunluk_*`, `halfyear_*`).
  - Aynı periyotta birden fazla giriş varsa PG’nin `data_collection_method` alanına göre **toplama**, **ortalama** veya **son değer** seçilir (`_aggregate`).

### 4.6 Excel dışa aktarma

`POST /process/api/karne/<process_id>/export-xlsx` — istemciden gelen `headers` ve `rows` ile **openpyxl** ile gerçek `.xlsx` üretir (satır/sütun sınırı kontrolü vardır).

---

## 5. Yardımcı İşleme — `app/utils/process_utils.py`

- **`last_day_of_period`:** Yıllık / çeyrek / aylık / haftalık / günlük periyot için veri tarihi (`data_date`) üretimi.
- **`data_date_to_period_keys`:** Bir tarihin karnede hangi periyot sütunlarına yansıyacağını hesaplar (aynı verinin çoklu periyot görünürlüğü).
- **`validate_process_parent_id`**, **`validate_same_tenant_sub_strategies`**, kullanıcı listesi doğrulamaları: tenant ve varlık tutarlılığı.

---

## 6. Yetkilendirme — `micro/modules/surec/permissions.py`

| Kavram | Açıklama |
|--------|-----------|
| **Ayrıcalıklı roller** | `Admin`, `tenant_admin`, `executive_manager` — tüm süreçleri görür; süreç oluşturma/silme; PGV satırında geniş yetki |
| **`user_can_access_process`** | Karnede / faaliyet sayfasında görüntüleme: ayrıcalıklı veya lider/üye/sahip |
| **`user_can_edit_process_record`** | Süreç kartı güncelleme |
| **`user_can_crud_pg_and_activity`** | PG ve süreç faaliyeti CRUD |
| **`user_can_enter_pgv`** | PG veri girişi ve faaliyet takibi |
| **`accessible_processes_filter`** | Liste sorgularında tenant + `is_active` + atama filtresi |

---

## 7. Süreç Verisini Kullanan Diğer Modüller

### 7.1 Analiz Merkezi (`/analiz`)

- **`GET /analiz`** — tenant aktif süreç listesi.
- **`/analiz/api/trend/<process_id>`** — `AnalyticsService.get_performance_trend` → `KpiData` zaman serisi.
- **`/analiz/api/health/<process_id>`** — `get_process_health_score` → PG ve son verilere göre skor.
- **`/analiz/api/forecast/<process_id>`** — tahmin.
- Karşılaştırma, rapor ve anomali uçları aynı modülde tanımlıdır (`micro/modules/analiz/routes.py`).

Kaynak servis: **`app/services/analytics_service.py`** (`Process`, `ProcessKpi`, `KpiData`).

### 7.2 Proje Yönetimi

Projeler, legacy **`Surec`** ile `related_processes` üzerinden ilişkilendirilebilir (`micro/modules/proje/routes_project_crud.py`). Bu, **eski süreç tablosu** ile köprüdür; Micro süreç ekranı **`Process`** kullanır — kurulumda iki dünya birlikte bulunabilir.

### 7.3 Kurum paneli

`micro/modules/kurum/routes.py` içinde tenant bazlı **`Process`** sayısı gibi özetler kullanılabilir.

### 7.4 Bireysel performans

Süreç PG’sinden bireysel PG türetme: `POST /bireysel/api/pg/ensure-from-process-kpi` (`process_kpi_id`).

---

## 8. Legacy Süreç Modeli (Özet)

**Dosya:** `models/process.py`  
**Tablo:** `surec` — kurum (`kurum_id`), hiyerarşi, lider/üye/owner ve `alt_strateji` çoklu ilişkileri.  
**PG:** `surec_performans_gostergesi` — `SurecPerformansGostergesi`.  
**Faaliyet:** `surec_faaliyet` — `SurecFaaliyet`.  

Klasik **`main.routes`** altında `/surec-karnesi`, `/api/kullanici/sureclerim`, debug uçları gibi yollar bu modele dayanabilir. **Micro `/process`** ile aynı işlev alanı örtüşse de **farklı tablolar** (`surec` vs `processes`) kullanılır; entegrasyon ihtiyaçları kurum bazında netleştirilmelidir.

---

## 9. Önemli Kaynak Dosyalar (Referans)

| Bileşen | Dosya |
|---------|--------|
| Route + API | `micro/modules/surec/routes.py` |
| Yetkiler | `micro/modules/surec/permissions.py` |
| ORM (güncel) | `app/models/process.py` |
| ORM (legacy) | `models/process.py` |
| Periyot / validasyon | `app/utils/process_utils.py` |
| Analitik | `app/services/analytics_service.py` |
| Arayüz | `micro/templates/micro/surec/index.html`, `karne.html`, `faaliyetler.html` |
| Menü | `micro/core/module_registry.py` |

---

## 10. Sonuç

Süreç Yönetimi modülü, **tenant-scoped `Process` hiyerarşisi**, **alt strateji bağlantıları**, **ProcessKpi + KpiData** ile ölçüm, **ProcessActivity + ActivityTrack** ile operasyonel takip ve **karne API** ile periyodik birleştirilmiş görünüm sunar. Veri işleme; Flask JSON API’leri, `process_utils` periyot mantığı, `KpiDataAudit` ile izlenebilirlik ve `AnalyticsService` ile raporlama katmanında devam eder. Legacy **`Surec`** şeması paralel durduğu için kurumsal veri stratejisinde hangi süreç kaynağının “asıl” olduğu net tanımlanmalıdır.

---

*Bu belge kod tabanının anlık durumuna göre hazırlanmıştır; endpoint veya model değişikliklerinde güncellenmelidir.*
