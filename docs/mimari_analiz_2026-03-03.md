# 🚀 Kokpitim Projesi — Mimari Özet ve Risk Analizi
> **Tarih:** 2026-03-03 | **Analiz Eden:** Antigravity (Gemini) | **Port:** `5001`

---

## 📊 Proje Durumu (Genel Tablo)

| Kategori | Durum |
|----------|-------|
| **Port** | ✅ 5001 (run.py'de sabit) |
| **DB (lokal)** | SQLite → `instance/kokpitim.db` |
| **Mimari Pattern** | Application Factory (`create_app()`) |
| **Auth** | Flask-Login + Werkzeug hash |
| **CSRF** | `extensions.py`'de merkezi `CSRFProtect` |
| **Blueprint Sayısı** | 7 adet (auth, dashboard, admin, strategy, process, hgs, core) |
| **Model Dosyaları** | 4 adet (core, saas, process, strategy) |
| **En Büyük Dosyalar** | `process.py` route: 56KB / `process_karne.js`: 74KB |

---

## 1. Anayasa Kuralları — Uyum Durumu

| Kural | Durum | Not |
|-------|-------|-----|
| PORT 5001 | ✅ | `run.py`'de `port=5001` sabit |
| Soft Delete | ✅ | core, saas, process — kritik modellerde mevcut |
| SweetAlert2 | ✅ | `base.html`'den CDN ile global yüklü |
| Hard Delete Yok | ✅ | Tüm delete rotaları `is_active=False` yapıyor |
| Katman Ayrımı (No Inline JS/CSS) | ✅ | Tüm `<script>` etiketleri sadece harici `.js` yüklüyor |
| CSRF | ✅ | `extensions.py` → `csrf.init_app(app)` düzgün kurulmuş |
| Blueprint Disiplini | ✅ | Hiçbir route `app/__init__.py`'de değil |
| Türkçe UI / İngilizce Kod | ✅ | HTML metinler Türkçe, kod tarafı İngilizce |

---

## 2. Blueprint ve Route Haritası

| Blueprint | URL Prefix | Başlıca Rotalar |
|-----------|-----------|-----------------|
| `auth_bp` | `""` | `/login`, `/logout`, `/profile`, `/settings`, `/profile/upload-photo` |
| `dashboard_bp` | `""` | `/`, `/kurum-paneli` + 6 adet strateji CRUD API'si |
| `admin_bp` | `/admin` | `/`, `/tenants`, `/users`, `/packages`, `/kule-iletisim` + CRUD |
| `strategy_bp` | `/strategy` | `/strategy/swot` ← `@require_component("swot_analizi")` |
| `process_bp` | `/process` | `/`, `/<id>/karne` + ~15 CRUD API endpoint |
| `hgs_bp` | `/hgs` | `/hgs/` (basit, küçük) |
| `core_bp` | `""` | Genel yardımcı rotalar |

---

## 3. Veri Modeli ve İlişkiler

```
SubscriptionPackage ←──M:M──→ SystemModule
                                   └── ModuleComponentSlug (component_slug)
                                                │
                                         RouteRegistry.component_slug

Tenant → Package (FK)
Tenant ──< Users, Processes, Strategies, Tickets, SwotAnalyses

Process (hiyerarşik, parent_id) ──< ProcessKpi ──< KpiData (is_deleted)
                                              ──< KpiDataAudit
                              ──< ProcessActivity ──< ActivityTrack
                              ──M:M──> User (leaders, members, owners)
                              ──M:M──> SubStrategy (ProcessSubStrategyLink + contribution_pct)

User ──< IndividualPerformanceIndicator ──< IndividualKpiData
     ──< IndividualActivity ──< IndividualActivityTrack
     ──< FavoriteKpi
```

### Soft Delete Sütunu Karşılaştırması

| Model | Soft Delete Sütunu | Durum |
|-------|-------------------|-------|
| `Tenant`, `User` | `is_active` | ✅ |
| `Strategy`, `SubStrategy` | `is_active` | ✅ |
| `Process` | `is_active` + `deleted_at` + `deleted_by` | ✅ |
| `ProcessKpi`, `ProcessActivity` | `is_active` | ✅ |
| `KpiData` | **`is_deleted`** | ⚠️ Farklı sütun adı |
| `SwotAnalysis` | `is_active` | ✅ |
| `FavoriteKpi` | `is_active` | ✅ |
| `IndividualPerformanceIndicator` | ❌ Yok | 🔴 EKSİK |
| `IndividualActivity` | ❌ Yok | 🔴 EKSİK |

---

## 4. PG Hesaplama Motoru (Score Engine)

**Dosya:** `app/services/score_engine_service.py`

```
KpiData.actual_value
     │
data_collection_method → Ortalama / Toplama / Son Değer
     │
compute_pg_score(hedef, gerçekleşen, direction)
 → direction=Increasing : ratio = gerçek / hedef × 100
 → direction=Decreasing : ratio = hedef / gerçek × 100
 → clamp(0, 100)
     │
ProcessKpi.calculated_score  (DB'ye persist edilir)
     │
Process skoru = Σ(KPI_skor × KPI_ağırlık) / Σ(ağırlık)
     │  (alt süreçler varsa iteratif, yoksa KPI'lardan doğrudan)
SubStrategy skoru = Ort(bağlı süreç skorları)
Strategy skoru    = Ort(alt strateji skorları)
Vision skoru      = Ort(strateji skorları) → clamp(0, 100)
```

`karne_hesaplamalar.py` ayrıca **Başarı Puanı Aralıkları (1-5 ölçek)** hesaplıyor → eski proje uyumluluğu için.

---

## 5. Yetkilendirme Katmanı

| Dekoratör | Dosya | İşlev |
|-----------|-------|-------|
| `@login_required` | Flask-Login built-in | `current_user.is_authenticated` kontrolü |
| `@require_component("slug")` | `app/utils/decorators.py` | Tenant paketinde bu slug var mı? |

### `@require_component` Akışı (Teorik)
```
current_user.is_authenticated?
   → tenant var mı?
       → tenant.package var mı?
           → pkg.modules → mod.component_slugs → comp.component_slug == component_code?
               → Erişim VER / ENGELLE
```

> ⚠️ **BUG:** Dekoratör şu an `mod.components` çağırıyor, bu ilişki modelde tanımlı değil. Bkz. Risk-1.

---

## 6. Bağımlılıklar (`requirements.txt`)

### Mevcut Paketler

| Paket | Versiyon | Kullanım |
|-------|----------|---------|
| `Flask` | Pinlenmemiş | Web framework |
| `Flask-WTF` | Pinlenmemiş | CSRF koruması |
| `Flask-SQLAlchemy` | Pinlenmemiş | ORM |
| `Flask-Migrate` | Pinlenmemiş | Alembic wrapper |
| `Flask-Login` | Pinlenmemiş | Authentication |
| `python-dotenv` | Pinlenmemiş | `.env` okuma |
| `pandas` | Pinlenmemiş | Excel import |
| `openpyxl` | Pinlenmemiş | `.xlsx` okuma |

### Eksik / Eklenmesi Gereken Paketler

| Paket | Neden |
|-------|-------|
| `gunicorn` | Production WSGI server |
| `psycopg2-binary` veya `pg8000` | PostgreSQL bağlantısı (Cloud) |
| Version pin'leri | Tüm paketler `==x.y.z` sabitlenmeli |

---

## 🚨 Tespit Edilen En Büyük 3 Risk

---

### 🔴 RİSK-1 (KRİTİK): `@require_component` Dekoratörü Çalışmıyor

**Dosya:** `app/utils/decorators.py` — Satır 32

```python
# MEVCUT (HATALI):
for comp in mod.components:          # ← AttributeError! Bu ilişki modelde yok!
    if comp.code == component_code:

# OLMASI GEREKEN:
for comp in mod.component_slugs:     # ← ModuleComponentSlug ilişkisi
    if comp.component_slug == component_code:
```

**Etki:** `@require_component` kullanan tek rota şu an `/strategy/swot`. Bu sayfaya erişen herhangi bir kullanıcı `AttributeError: 'SystemModule' object has no attribute 'components'` alır ve 500 hatası döner. SaaS yetki denetimi fiilen **devre dışı**.

**Öncelik:** Hemen düzeltilmeli.

---

### 🔴 RİSK-2 (KRİTİK): `current_app` Import Edilmemiş — KPI Veri Girişinde Runtime Hatası

**Dosya:** `app/routes/process.py` — Satır 575 ve 580

```python
# MEVCUT (HATALI) — dosyanın başında current_app import edilmemiş:
current_app.logger.warning(f'[kpi_data_add] score_engine hatası: {e}')   # NameError!
current_app.logger.warning(f'[kpi_data_add] deviation_service hatası: {e}')  # NameError!

# OLMASI GEREKEN (process.py'nin import bölümüne ekle):
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, send_file, current_app
```

**Etki:** KPI veri girişi sırasında score engine veya deviation service hata verirse bu `NameError` fırlatır ve kullanıcıya 500 döner. Veri kaydedilmiş olsa bile exception handler devreye girer ve yanlış sonuç üretilebilir.

**Öncelik:** Hemen düzeltilmeli.

---

### 🟡 RİSK-3 (ORTA): Bireysel Modellerde Soft Delete Eksik

**Dosya:** `app/models/process.py` — `IndividualPerformanceIndicator` (satır 282) ve `IndividualActivity` (satır 330)

```python
# Bu iki modelde is_active veya is_deleted sütunu yok.
# Anayasa Kural 4: "Hard Delete Yasak"

# EKLENECEK HER İKİ MODELE:
is_active = db.Column(db.Boolean, default=True, nullable=False, index=True)
```

Ayrıca `KpiData` modelinde sütun adı `is_deleted` iken diğer tüm modellerde `is_active` — bu tutarsızlık sorgu yazarken karışıklığa neden olur.

**Öncelik:** Bir sonraki migration döngüsünde düzeltilmeli.

---

## 7. Hızlı Başlangıç Kontrol Listesi

```
[ ] http://127.0.0.1:5001 → Uygulama ayakta mı?
[ ] /login → admin@kokpitim.com / admin123
[ ] /kurum-paneli → Stratejiler kartı görünüyor mu?
[ ] /strategy/swot → 500 hata veriyor mu? (Risk-1 tetiklenir)
[ ] /process/ → Süreç listesi yüklüyor mu?
[ ] F12 Console → Kırmızı hata var mı?
[ ] flask db upgrade → Bekleyen migration var mı?
```

---

*Oluşturulma Tarihi: 2026-03-03 | Dosya: `docs/mimari_analiz_2026-03-03.md`*
