# 🚀 KOKPİTİM — YAPAY ZEKA DEVİR TESLİM VE HAFIZA DOSYASI
> **Oluşturulma Tarihi:** 2026-03-01 | **Son Faz:** 5.24 | **Port:** `5001` (DEĞİŞMEZ)

---

## ⚠️ ÖNCE OKU — MUTLAK KURALLAR (SIKIYÖNETİM)

| Kural | Açıklama |
|-------|----------|
| 🔴 **PORT** | Uygulama **HER ZAMAN** `5001` portunda çalışır. `run.py` → `port=5001`. URL: `http://127.0.0.1:5001` |
| 🔴 **HAM HTML YOK** | HTML dosyaları içinde `<script>` veya `<style>` bloğu **KESİNLİKLE YAZILMAZ**. |
| 🔴 **İNGİLİZCE KOD** | DB sütunları, değişkenler, fonksiyonlar, rotalar → `snake_case` İngilizce |
| 🔴 **TÜRKÇE UI** | Kullanıcının gördüğü her metin (HTML, SweetAlert, Flash) → Türkçe |
| 🔴 **SOFT DELETE** | Hiçbir veri veritabanından fiziksel olarak silinmez. `is_active=False` kullanılır. |
| 🔴 **SWEETALERT2** | Tüm bildirim/onay pencereleri için `alert()`/`confirm()` yasak, sadece SweetAlert2 kullanılır. |
| 🔴 **CSRF** | Tüm POST formlarında CSRF token zorunlu. `meta[name=csrf-token]` kullanılır. |
| 🟡 **OTONOM ÇALIŞMA** | Kullanıcıdan onay beklenmez, komutlar direkt çalıştırılır. |

---

## 1. 🏗️ PROJE MİMARİSİ

### Teknoloji Yığını

```
Backend:    Python 3.x + Flask (Application Factory Pattern)
ORM:        Flask-SQLAlchemy + Flask-Migrate (Alembic)
Auth:       Flask-Login + Werkzeug (password_hash)
CSRF:       Flask-WTF (CSRFProtect)
DB (local): SQLite → instance/kokpitim.db
DB (prod):  PostgreSQL (Cloud SQL) → .env ile SQLALCHEMY_DATABASE_URI
Frontend:   Bootstrap 5.3.2 + FontAwesome 6.5 + SweetAlert2 v11 + Chart.js
JS:         Vanilla JS / Fetch API (harici .js dosyaları)
CSS:        Vanilla CSS (harici .css dosyaları)
```

### Klasör Yapısı

```
c:\kokpitim\
├── run.py                    ← Giriş noktası (port=5001)
├── config.py                 ← Config sınıfı (.env'den yükler)
├── .env                      ← SECRET_KEY + SQLALCHEMY_DATABASE_URI
├── requirements.txt          ← Pip bağımlılıkları
├── app/
│   ├── __init__.py           ← create_app() factory
│   ├── extensions.py         ← csrf = CSRFProtect() (merkezi)
│   ├── models/
│   │   ├── __init__.py       ← db = SQLAlchemy() + tüm model import'ları (Alembic keşfi için)
│   │   ├── core.py           ← Tenant, User, Role, Ticket, Strategy, SubStrategy, Notification
│   │   ├── saas.py           ← SubscriptionPackage, SystemModule, SystemComponent, RouteRegistry, ModuleComponentSlug
│   │   ├── process.py        ← Process, ProcessKpi, ProcessActivity, KpiData, KpiDataAudit, vb.
│   │   └── strategy.py       ← SwotAnalysis
│   ├── routes/
│   │   ├── __init__.py       ← Boş (Blueprint'ler __init__.py'de kayitli)
│   │   ├── auth.py           ← auth_bp: /login, /logout, /profile, /settings
│   │   ├── dashboard.py      ← dashboard_bp: /, /kurum-paneli, strategy CRUD API'leri
│   │   ├── admin.py          ← admin_bp (/admin prefix): tenant/user/package yönetimi
│   │   ├── strategy.py       ← strategy_bp (/strategy prefix): /swot
│   │   ├── process.py        ← process_bp: Süreç Yönetimi + Karne
│   │   ├── hgs.py            ← hgs_bp: HGS ekranı
│   │   └── core.py           ← core_bp: Genel yardımcı rotalar
│   ├── services/             ← İş mantığı servisleri
│   └── utils/
│       ├── decorators.py     ← @require_component, @_is_ajax()
│       ├── karne_hesaplamalar.py
│       └── process_utils.py
├── templates/
│   ├── base.html             ← Ana layout (navbar + sidebar + flash)
│   ├── dashboard/
│   │   ├── tenant_panel.html ← /kurum-paneli (Tenant Dashboard) ← AKTİF ÇALIŞMA ALANI
│   │   ├── classic.html
│   │   └── sideview.html
│   ├── admin/                ← Kurum/Kullanıcı/Paket yönetimi sayfaları
│   ├── auth/                 ← login, profile, settings
│   ├── strategy/             ← swot.html
│   └── process/              ← Süreç Yönetimi sayfaları
├── static/
│   ├── css/                  ← Her sayfa için ayrı .css dosyası
│   ├── js/                   ← Her sayfa için ayrı .js dosyası
│   │   └── modules/          ← Modül bazlı JS
│   └── img/
│       └── kokpitim-logo.png ← Şeffaf PNG logo (favicon da bu)
├── migrations/               ← Alembic migration dosyaları
├── eski_proje/               ← 🚫 SADECE REFERANS - import yasak!
└── docs/                     ← Dokümantasyon ve raporlar
```

### Blueprint Kayıt Yapısı (`app/__init__.py`)

```python
app.register_blueprint(auth_bp)           # url_prefix=""
app.register_blueprint(hgs_bp)            # url_prefix="/hgs"
app.register_blueprint(dashboard_bp)      # url_prefix=""
app.register_blueprint(admin_bp, url_prefix="/admin")
app.register_blueprint(strategy_bp)       # url_prefix="/strategy"
app.register_blueprint(process_bp)        # url_prefix="/process" (tahminen)
app.register_blueprint(core_bp)           # url_prefix=""
```

### Katman Ayrımı (KATI KURAL)

```
HTML → Sadece yapı + Jinja2 template
CSS  → static/css/<sayfa>.css
JS   → static/js/<sayfa>.js (Jinja2 YOK, Fetch API kullanılır)
Veri → HTML elementlerinde data-* öznitelikleri VEYA window.CONFIG objesi (max 10 satır)
```

---

## 2. 🗄️ VERİTABANI ŞEMASI

### İlişki Diyagramı

```
SubscriptionPackage ──< package_modules >── SystemModule ──< ModuleComponentSlug

Tenant ──belongs_to──> SubscriptionPackage
Tenant ──has_many──> User
Tenant ──has_many──> Strategy ──has_many──> SubStrategy
Tenant ──has_many──> Ticket
Tenant ──has_many──> Process

User ──belongs_to──> Tenant
User ──belongs_to──> Role

Process ──belongs_to──> Tenant
Process ──has_many──> ProcessKpi
Process ──has_many──> ProcessActivity
Process ──many_to_many──> User (leaders, members, owners)
Process ──many_to_many──> SubStrategy

RouteRegistry → Bağımsız tablo (endpoint→component_slug mapping)
SwotAnalysis → tenant_id FK
```

### `tenants` Tablosu (Tenant Modeli)

| Sütun | Tip | Açıklama |
|-------|-----|----------|
| `id` | Integer PK | |
| `name` | String(255) | Tam ad |
| `short_name` | String(64) | Kısa ad |
| `is_active` | Boolean | Soft delete |
| `package_id` | FK → subscription_packages | |
| `created_at` | DateTime | |
| `activity_area` | String(200) | Faaliyet alanı |
| `sector` | String(100) | Sektör |
| `employee_count` | Integer | |
| `contact_email` | String(120) | |
| `phone_number` | String(20) | |
| `website_url` | String(200) | |
| `tax_office` | String(100) | Vergi dairesi |
| `tax_number` | String(20) | |
| `max_user_count` | Integer | Lisans kullanıcı limiti |
| `license_end_date` | Date | Lisans bitiş tarihi |
| `purpose` | Text | Kurum Amaç (Misyon) |
| `vision` | Text | Vizyon |
| `core_values` | Text | Değerler (newline ayrımlı) |
| `code_of_ethics` | Text | Etik kurallar (newline ayrımlı) |
| `quality_policy` | Text | Kalite politikası (newline ayrımlı) |

### `users` Tablosu (User Modeli)

| Sütun | Tip | Açıklama |
|-------|-----|----------|
| `id` | Integer PK | |
| `email` | String(255) unique | |
| `password_hash` | String(255) | Werkzeug hash |
| `first_name` | String(64) | |
| `last_name` | String(64) | |
| `is_active` | Boolean | Soft delete |
| `tenant_id` | FK → tenants | Null = bireysel/admin |
| `role_id` | FK → roles | |
| `created_at` | DateTime | |
| `phone_number` | String(20) | |
| `job_title` | String(100) | Unvan |
| `department` | String(100) | |
| `profile_picture` | String(500) | URL veya path |
| `theme_preferences` | Text | JSON |
| `layout_preference` | String(20) | classic/sidebar |
| `notification_preferences` | Text | JSON |
| `locale_preferences` | Text | JSON |
| `show_page_guides` | Boolean | |
| `guide_character_style` | String(50) | professional/friendly/minimal |

### `roles` Tablosu — Roller ve Yetkiler

| Role Name | Açıklama |
|-----------|----------|
| `Admin` | Süper Admin — tüm kurumları yönetir |
| `tenant_admin` | Kurum Yöneticisi — `/kurum-paneli`'ne erişir |
| `executive_manager` | Üst Yönetici — sınırlı kurum yönetimi |
| `standard_user` | Standart kullanıcı |

### `strategies` Tablosu (Strategy Modeli — `app/models/core.py`)

| Sütun | Tip | Açıklama |
|-------|-----|----------|
| `id` | Integer PK | |
| `tenant_id` | FK → tenants | Multi-tenant izolasyon |
| `code` | String(20) | Örn: ST1 |
| `title` | String(200) | Strateji başlığı |
| `description` | Text | |
| `is_active` | Boolean | Soft delete |
| `created_at` / `updated_at` | DateTime | |

### `sub_strategies` Tablosu (SubStrategy Modeli — `app/models/core.py`)

| Sütun | Tip | Açıklama |
|-------|-----|----------|
| `id` | Integer PK | |
| `strategy_id` | FK → strategies | Ana strateji |
| `code` | String(20) | Örn: ST1.1 |
| `title` | String(200) | |
| `description` | Text | |
| `is_active` | Boolean | Soft delete |
| `created_at` / `updated_at` | DateTime | |

### SaaS Hiyerarşisi (Paket → Modül → Bileşen)

```
SubscriptionPackage (subscription_packages)
    └── SystemModule (system_modules) [M:M via package_modules]
            └── ModuleComponentSlug (module_component_slugs) [1:M]
                    └── component_slug → RouteRegistry.component_slug ile eşleşir
```

- `RouteRegistry` → Uygulamadaki URL endpoint'lerinin kaydıdır. Admin panelinde "Bileşenler" sekmesinden yönetilir.
- `@require_component("swot_analizi")` decorator'ü → Tenant'ın paketinde o `component_slug` var mı kontrol eder.

### `swot_analyses` Tablosu

| Sütun | Tip | Açıklama |
|-------|-----|----------|
| `id` | Integer PK | |
| `tenant_id` | FK → tenants | |
| `category` | String(32) | strength / weakness / opportunity / threat |
| `content` | Text | |
| `created_at` | DateTime | |
| `is_active` | Boolean | |

---

## 3. 🔐 MULTİ-TENANT İZOLASYON MANTIĞI

Her rota kendisi filtreleme yapar:

```python
# Örnek pattern (DOĞRU kullanım)
tenant_id = current_user.tenant_id
strategies = Strategy.query.filter_by(tenant_id=tenant_id, is_active=True).all()
```

**Rol kontrolü pattern'i (route başında):**

```python
if not current_user.role or current_user.role.name not in ["tenant_admin", "executive_manager"]:
    return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
```

---

## 4. 🌐 BACKEND'DEN JS'E VERİ AKTARIMI

**DOĞRU yöntem — data-* attribute:**
```html
<div id="dashboardChartContainer" 
     data-chart-data='{{ dict(user_count=stats.user_count)|tojson|safe }}'>
</div>
```

**JS tarafında okuma:**
```javascript
const container = document.getElementById('dashboardChartContainer');
const chartData = JSON.parse(container.dataset.chartData);
```

**YANLIŞ — Harici JS içinde Jinja2:**
```javascript
// ❌ YAPMA!
const url = "{{ url_for('dashboard_bp.tenant_dashboard') }}";
```

**CSRF token okuma (tüm Fetch POST'larında):**
```javascript
const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRFToken': csrfToken },
    body: JSON.stringify(data)
});
```

---

## 5. ☁️ GOOGLE CLOUD YAYINLAMA HAFIZASI

> ⚠️ Bu bölüm gelecekteki cloud deployment için kritik ders belgesidir.

### Mevcut Durum

Proje şu an yerel SQLite ile çalışmaktadır. Cloud deployment henüz production'a taşınmamıştır ancak geçmiş denemelerde edinilen bilgiler aşağıdadır.

### Veritabanı Bağlantısı — Cloud SQL (PostgreSQL)

**Sorun:** SQLite ile yerel çalışan uygulama, Cloud SQL'e geçişte bağlantı hatası verir.

**Çözüm — Cloud SQL Socket:**
```python
# config.py'de production için
import os
DB_USER = os.environ.get("DB_USER", "kokpitim_user")
DB_PASS = os.environ.get("DB_PASS", "")
DB_NAME = os.environ.get("DB_NAME", "kokpitim_db")
DB_HOST = os.environ.get("DB_HOST", "/cloudsql/PROJECT:REGION:INSTANCE")

# Cloud SQL Unix socket bağlantısı (App Engine / Cloud Run)
SQLALCHEMY_DATABASE_URI = f"postgresql+pg8000://{DB_USER}:{DB_PASS}@/{DB_NAME}?unix_sock={DB_HOST}/.s.PGSQL.5432"

# TCP bağlantısı (Cloud SQL Auth Proxy ile lokal test)
# SQLALCHEMY_DATABASE_URI = f"postgresql+psycopg2://{DB_USER}:{DB_PASS}@127.0.0.1:5432/{DB_NAME}"
```

**Gerekli ek paketler (`requirements.txt`'e eklenecek):**
```
psycopg2-binary   # veya pg8000 (App Engine için pg8000 tercih edilir)
gunicorn
google-cloud-sql-connector  # opsiyonel, yeni connector yöntemi için
```

### App Engine (`app.yaml`)

```yaml
runtime: python311

env_variables:
  SECRET_KEY: "PRODUCTION_SECRET_KEY_BURAYA"
  DB_USER: "kokpitim_user"
  DB_PASS: "SIFRE_BURAYA"
  DB_NAME: "kokpitim_db"
  DB_HOST: "/cloudsql/proje-id:us-central1:kokpitim-db"
  SQLALCHEMY_DATABASE_URI: "postgresql+pg8000://kokpitim_user:SIFRE@/kokpitim_db?unix_sock=/cloudsql/proje-id:us-central1:kokpitim-db/.s.PGSQL.5432"

beta_settings:
  cloud_sql_instances: proje-id:us-central1:kokpitim-db

entrypoint: gunicorn -w 2 -b :$PORT run:app

handlers:
  - url: /static
    static_dir: static
  - url: /.*
    script: auto
```

**⚠️ Kritik not:** App Engine'de `$PORT` environment variable otomatik set edilir. `gunicorn -b :$PORT run:app` kullanılmalıdır, `port=5001` yazılmamalıdır!

### Cloud Run (`Dockerfile`)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Cloud Run $PORT'u otomatik atar (genellikle 8080)
CMD exec gunicorn --bind :$PORT --workers 2 --threads 8 --timeout 60 run:app
```

**Cloud Run için `cloudbuild.yaml`:**
```yaml
steps:
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/kokpitim', '.']
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/kokpitim']
  - name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
    args:
      - 'run'
      - 'deploy'
      - 'kokpitim'
      - '--image=gcr.io/$PROJECT_ID/kokpitim'
      - '--platform=managed'
      - '--region=europe-west1'
      - '--allow-unauthenticated'
```

### Statik Dosya Sorunu

**Sorun:** Cloud Run'da Flask `static/` klasörünü doğru servis etmeyebilir, özellikle gunicorn ile.

**Çözüm 1 — Flask Static Handler (geliştirme):** Flask zaten `/static/...` route'u handle eder, production'da gunicorn bunu da yönetir — genellikle ek yapılandırma gerekmez.

**Çözüm 2 — Cloud CDN / GCS Bucket (production tavsiyesi):**
```python
# config.py'de
STATIC_URL = os.environ.get("STATIC_URL", "/static")  # CDN veya yerel
```

**Çözüm 3 — App Engine'de `app.yaml` handlers:** Yukarıda gösterildi, `/static` için `static_dir` tanımlandığında App Engine otomatik servis eder ve Flask'ı bypass eder (daha hızlı).

### Gunicorn Parametreleri

```bash
# Temel
gunicorn run:app -w 2 -b :$PORT --timeout 120

# Async (yüksek trafikte)
gunicorn run:app -w 4 -k gevent -b :$PORT --timeout 120

# Loglama ile
gunicorn run:app -w 2 -b :$PORT --access-logfile - --error-logfile - --log-level info
```

**`run:app` açıklaması:** `run.py` dosyasındaki `app = create_app()` nesnesi. Flask factory pattern olduğu için `run:app` doğru formattır.

### Flask Migration (Cloud'da)

Database migration'ları cloud'da çalıştırmak için:
```bash
# Cloud Shell veya Cloud Run job olarak
flask db upgrade
```

Ya da `run.py`'de startup hook:
```python
with app.app_context():
    from flask_migrate import upgrade
    upgrade()  # Otomatik migration (dikkatli kullanılmalı!)
```

### `.env` Dosyası Cloud'da Kullanılmaz

Cloud ortamında `.env` dosyası olmamalıdır. Tüm değişkenler:
- **App Engine:** `app.yaml` → `env_variables` bölümü
- **Cloud Run:** Secret Manager veya `--set-env-vars` flag'i
- **Cloud SQL bağlantısı:** `cloud_sql_instances` veya Cloud SQL Connector

---

## 6. 📍 MEVCUT DURUM VE SON FAZ

### Son Tamamlanan Faz: **Faz 5.24 — Stratejiler Modülü**

**Ne yapıldı:**
- `Strategy` ve `SubStrategy` modelleri `app/models/core.py`'ye eklendi (migration yapıldı)
- `/kurum-paneli` (Tenant Dashboard) sayfasına "Stratejiler" kartı inşa edildi
- Hiyerarşik, yatay kayan kart yapısı: Ana Strateji kartları + içlerinde Alt Strateji listeleri
- Bootstrap modal'larla CRUD işlemleri (Ekle/Düzenle/Sil)
- Fetch API + SweetAlert2 ile asenkron güncelleme
- Tüm API endpoint'leri `dashboard.py`'de yazıldı:
  - `POST /kurum-paneli/add-strategy` → Yeni ana strateji
  - `POST /kurum-paneli/add-sub-strategy` → Yeni alt strateji
  - `POST /kurum-paneli/update-main-strategy/<id>` → Ana strateji düzenle
  - `POST /kurum-paneli/delete-main-strategy/<id>` → Ana strateji soft delete
  - `POST /kurum-paneli/update-sub-strategy/<id>` → Alt strateji düzenle
  - `POST /kurum-paneli/delete-sub-strategy/<id>` → Alt strateji soft delete
- **JS:** `static/js/tenant_dashboard.js` (20KB) — tüm interaktif mantık burada
- **CSS:** `static/css/tenant_dashboard.css` (5KB) — stratejiler dahil özel stiller

### Kurum Paneli (`/kurum-paneli`) Bölüm Sırası

1. **Header** — Hoş geldiniz mesajı
2. **Stratejik Kimlik Kartları** (Amaç, Vizyon, Değerler, Etik Kurallar, Kalite Politikası)
   - Satır içi düzenlemeli, katlanabilir kartlar
   - Fetch API ile `/kurum-paneli/update-strategy` endpoint'ine
3. **Stratejiler Kartı** ← **EN SON EKLENEN**
   - Collapsible (Bootstrap collapse)
   - Yatay scroll'lu kart grid'i
   - Ana strateji + Alt strateji hiyerarşisi
4. **İstatistik Kartları** (Kullanıcı sayısı, Paket adı, Kullanım %, Bekleyen talepler)
5. **Grafik ve Son İşlemler** (Chart.js donut grafik + aktivite listesi)

### Süreç Yönetimi (Faz 4)

- `app/routes/process.py` (55KB!) — Süreç CRUD, Süreç Karnesi, Performans hesaplama
- `static/js/process_karne.js` (74KB!) — Karne ekranı JS mantığı
- `app/models/process.py` (22KB) — Process, ProcessKpi, ProcessActivity, KpiData, KpiDataAudit, IndividualPerformanceIndicator, IndividualActivity vb.
- Eski projeden (`eski_proje/`) başarıyla migrate edilmiştir.

---

## 7. 🧩 KRİTİK KALIP VE ŞEKİLLER

### Yeni Bir Route Eklemek

```python
# app/routes/<modül>.py'de
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user

<modül>_bp = Blueprint("<modül>_bp", __name__, url_prefix="/<prefix>")

@<modül>_bp.route("/yeni-rota", methods=["POST"])
@login_required
def yeni_fonksiyon():
    # Rol kontrolü
    if not current_user.role or current_user.role.name not in ["tenant_admin"]:
        return jsonify({"success": False, "message": "Yetkisiz işlem."}), 403
    # Multi-tenant izolasyon
    tenant_id = current_user.tenant_id
    # İş mantığı...
    return jsonify({"success": True, "message": "İşlem tamamlandı."})

# app/__init__.py'de kaydet:
from app.routes.<modül> import <modül>_bp
app.register_blueprint(<modül>_bp)
```

### Yeni Model Eklemek

```python
# app/models/<dosya>.py'de tanımla
# app/models/__init__.py'de import et (Alembic keşfi için)
# Sonra migration:
flask db migrate -m "Yeni model açıklaması"
flask db upgrade
```

### Dekoratörler

```python
@login_required          # Flask-Login — giriş kontrolü
@require_component("component_code")  # SaaS paket erişim kontrolü (login_required'dan SONRA)
```

---

## 8. 🔗 TEMEL URL'LER (Local: `http://127.0.0.1:5001`)

| URL | Blueprint | Açıklama |
|-----|-----------|----------|
| `/` | `dashboard_bp.index` | Rol'e göre yönlendirme |
| `/login` | `auth_bp.login` | Giriş |
| `/kurum-paneli` | `dashboard_bp.tenant_dashboard` | Tenant Yönetim Paneli |
| `/performans-kartim` | `dashboard_bp.performans_kartim` | Bireysel Panel |
| `/strategy/swot` | `strategy_bp.swot` | SWOT Analizi |
| `/admin/` | `admin_bp.index` | Admin Özet |
| `/admin/tenants` | `admin_bp.tenants` | Kurum Yönetimi |
| `/admin/users` | `admin_bp.users` | Kullanıcı Yönetimi |
| `/admin/packages` | `admin_bp.packages` | SaaS Paket Yönetimi |
| `/admin/kule-iletisim` | `admin_bp.kule_iletisim` | Destek Talepleri |
| `/process/` | `process_bp.index` | Süreç Yönetimi |

---

## 9. 📦 BAĞIMLILIKLAR (`requirements.txt`)

```
Flask
Flask-WTF          ← CSRF
Flask-SQLAlchemy
Flask-Migrate      ← Alembic wrapper
Flask-Login
python-dotenv      ← .env okuma
pandas             ← Excel import fonksiyonu
openpyxl           ← xlsx okuma
```

**Eksik / Eklenebilecek (production için):**
```
gunicorn           ← Production WSGI
psycopg2-binary    ← PostgreSQL connector
Pillow             ← Görsel işleme (remove_bg.py için)
```

---

## 10. ⚡ HIZLI BAŞLANGIÇ KONTROL LİSTESİ

Yeni oturumda projeye başlarken:

- [ ] `http://127.0.0.1:5001` → Uygulama ayakta mı?
- [ ] `/login` → `admin@kokpitim.com` / `admin123` (veya seed'deki credentials)
- [ ] `/kurum-paneli` → Stratejiler kartı görünüyor mu?
- [ ] `flask db upgrade` gerekiyor mu? (yeni migration var mı?)
- [ ] F12 Console → Kırmızı hata var mı?

---

*Bu dosya `c:\kokpitim\GEMINI_HANDOVER.md` konumunda saklanmaktadır. Proje ilerledikçe güncellenmelidir.*
