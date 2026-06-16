# Kokpitim Proje Analizi — CursorAnaliz
**Analiz Tarihi:** 2026-03-19  
**Analiz Eden:** CursorAnaliz  
**Proje Versiyonu:** TASK-031

## Özet Kart
- Toplam Dosya: 1905 (tam depo), 970 (aktif alan; `eski_proje`, `Yedekler`, `ARCHIVE` hariç)
- Toplam Satır: 5,260,723 (ham), 425,292 (aktif alan)
- Kritik Güvenlik Sorunu: 3 ana başlık (hardcoded secret/DB URL, yaygın `@csrf.exempt`, `HGS` açık login)
- Teknik Borç Seviyesi: Kritik
- Genel Sağlık Skoru: 57/100

---

## ADIM 1 — Proje Haritası

### 1.1 Klasör Ağacı (özet)
- `app/`: Yeni Flask katmanı (core model, route, servis ve API)
- `micro/`: `/micro` altında modüler arayüz ve route katmanı
- `main/`: Legacy ana route katmanı (çok büyük monolitik `main/routes.py`)
- `api/`: Legacy API route katmanı (çok büyük `api/routes.py`)
- `auth/`: Legacy auth katmanı
- `models/`: Legacy model katmanı (`LegacyUser`, `Surec`, vb.)
- `migrations/`: Alembic/Flask-Migrate migrasyonları
- `templates/`: Kök Jinja2 şablonları
- `ui/templates/platform/`: Micro arayüz şablonları
- `static/`: Kök JS/CSS/asset dosyaları
- `ui/static/platform/`: Micro JS/CSS dosyaları
- `services/`: Legacy servisler
- `app/services/`: Yeni servis katmanı
- `tests/`: Test klasörü (ek olarak kökte birçok `test_*.py` var)
- `scripts/`: Operasyon/import/yardımcı scriptler
- `docs/`: Dokümantasyon ve TASKLOG
- `logs/`: Uygulama logları
- `instance/`: SQLite/instance artefact alanı
- `prototypes/`: Prototip HTML/JS dosyaları
- `eski_proje/`: Eski kod bazının büyük bir kopyası (teknik borç kaynağı)
- `Yedekler/`: Zip yedekler

> Not: Klasör detayları çok geniş; bu rapor aktif kod yollarına odaklıdır.

### 1.2 Sayısal Envanter
- Toplam dosya (ham): `1905`
- Toplam satır (ham): `5,260,723`
- Aktif alan dosya: `970`
- Aktif alan satır: `425,292`

### 1.3 Teknolojiler
- Backend: Flask (çoklu app-factory yapısı)
- ORM: Flask-SQLAlchemy / SQLAlchemy
- Migration: Flask-Migrate + Alembic
- Auth: Flask-Login
- CSRF: Flask-WTF CSRFProtect
- Security headers: Flask-Talisman (legacy factory tarafında)
- Rate limit: Flask-Limiter (bir factory'de aktif, diğerinde fake limiter)
- Cache: Flask-Caching
- Realtime: Flask-SocketIO
- Frontend: Jinja2 + Vanilla JS + Tailwind CDN + Alpine.js + SweetAlert2 + Chart.js
- Veri araçları: pandas, openpyxl
- AI/opsiyonel: scikit-learn, celery, redis

### 1.4 Bağımlılıklar
`requirements.txt`:
- Flask
- Flask-WTF
- Flask-SQLAlchemy
- Flask-Migrate
- Flask-Login
- Flask-Limiter
- Flask-Caching
- Flask-SocketIO==5.3.5
- python-socketio==5.10.0
- python-dotenv
- pandas
- openpyxl
- bleach
- sentry-sdk[flask]
- redis
- marshmallow==3.20.1
- marshmallow-sqlalchemy==0.29.0
- eventlet==0.33.3
- PyJWT==2.8.0
- flask-swagger-ui

Ek:
- `requirements-test.txt`: pytest, pytest-cov, pytest-flask, pytest-mock, coverage, faker, marshmallow
- `requirements-pwa.txt`: pywebpush, py-vapid
- `requirements-ai.txt`: scikit-learn, numpy, pandas, celery, redis

---

## ADIM 2 — Mimari Analiz

### 2.1 Genel Mimari
- Projede **iki ayrı uygulama fabrikası** var:
  - `__init__.py` (legacy, çok geniş setup, Talisman/limiter/auto create_all)
  - `app/__init__.py` (yeni app katmanı)
- `app.py`, `from __init__ import create_app` kullanıyor; fiili runtime legacy factory üzerinden açılıyor.
- Giriş noktası: `app.py`, host `127.0.0.1`, port `5001`.

#### Blueprint Kayıtları (ana)
- Legacy factory (`__init__.py`):
  - `main_bp` (prefix yok)
  - `auth_bp` (`/auth`)
  - `api_bp` (legacy API)
  - `admin_bp`
  - `analysis_bp`
  - `bsc_bp`
  - `v2_bp`, `v3_bp`
  - `micro_bp` (`/micro`)
- Yeni factory (`app/__init__.py`):
  - `auth_bp`, `hgs_bp`, `dashboard_bp`, `admin_bp` (`/admin`), `strategy_bp`, `process_bp`, `core_bp`
  - `app.api` blueprints
  - `micro_bp`

#### Middleware / Security
- Flask-Login aktif, `@login_required` yaygın.
- CSRF global aktif ancak birçok endpoint `@csrf.exempt`.
- Talisman yalnız legacy factory'de (yeni factory tarafında custom header fonksiyonu kullanılıyor).
- Rate limiter mimarisi çelişkili: bir yerde gerçek limiter, bir yerde FakeLimiter.

#### Config / .env
- `config.py` ortam değişkeni okuyor.
- `SECRET_KEY` için fallback sabit var (`cok-gizli-...`).
- Session cookie güvenlik ayarları (`SESSION_COOKIE_SECURE`, `SESSION_COOKIE_HTTPONLY`) config içinde açıkça görülmüyor.

### 2.2 Veritabanı Mimarisi
- ORM: SQLAlchemy (Flask-SQLAlchemy)
- Migration: Alembic var (`migrations/versions/*`)
- SQLAlchemy instance durumu:
  - `extensions.py::db` (legacy)
  - `app/extensions.py::db` (yeni katman)
  - `app/models/__init__.py` `extensions` import ediyor
  - Teknik olarak birleştirme yapılmış olsa da kod tabanı hala çoklu instance izi taşıyor.

#### Model Sayısı (yaklaşık, aktif + legacy birlikte)
- `app/models/*`: Tenant, Role, User, Ticket, Strategy, SubStrategy, Notification, Process, ProcessKpi, ProcessActivity, KpiData, Individual* modeller, SaaS modelleri, email config vb.
- `models/*`: LegacyUser/Kurum/Surec/AnaStrateji/AltStrateji/proje modeli ailesi vb.
- Toplam class(db.Model) sayısı (backup dahil taramada): çok yüksek (100+ görünüm); aktif odakta ~45-60 bandı.

#### İlişkiler
- `ForeignKey`, `relationship`, M2M association table kullanımı yaygın.
- Process tarafında:
  - `process_members`, `process_leaders`, `process_owners_table`
  - `process_sub_strategy_links` ile katkı yüzdesi
- Tenant/User/Role/Package ilişkileri düzgün tanımlı.

#### Soft delete
- Yeni model setinde çoğunlukla `is_active` var.
- Legacy sette `silindi` + `deleted_at` + `deleted_by` var.
- Bazı CRUD endpointlerinde soft delete tutarlı, bazı yerlerde direkt fiziksel dosya silme/sert davranış bulunuyor.

### 2.3 Micro Yapısı

#### Micro modüller
- `admin`, `analiz`, `api`, `bireysel`, `hgs`, `kurum`, `masaustu`, `proje`, `sp`, `surec`, `shared/auth`, `shared/ayarlar`, `shared/bildirim`

#### Route envanteri (micro)
- `admin`: 22
- `surec`: 19
- `api`: 15
- `shared/*`: 13
- `sp`: 12
- `bireysel`: 11
- `kurum`: 8
- `analiz`: 7
- `hgs`: 2
- `masaustu`: 1
- `proje`: 1

#### `micro_bp` vs `auth_bp` ilişki/çakışma
- Profil, login, ayarlar benzeri işlevler hem micro hem kök auth'ta var.
- Alan adı tutarsızlığı (`profile_picture` vs `profile_photo`) legacy kalıntılarda devam ediyor.
- Endpoint davranışları farklı (micro JSON-first, kök form-first); bakım maliyeti yüksek.

#### `templates/` vs `ui/templates/platform/` duplicate
- Aynı isimli şablonlar tespit edildi: `base.html`, `index.html`, `users.html`, `tenants.html`, `packages.html`, `karne.html`, `login.html`, `403.html`, `dynamic_flow.html`.
- Bu durum hem isimsel çakışma hem de tasarım davranış farkı riski doğuruyor.

---

## ADIM 3 — Kod Kalitesi Analizi

### 3.1 Teknik Borç
- Monolit dosyalar: `main/routes.py` (~çok büyük), `api/routes.py` (~çok büyük), `app/routes/process.py` (çok uzun).
- Duplicate işlev: auth/profil, süreç/kpi CRUD hem micro hem root katmanda tekrarlı.
- Hardcoded örnek/parola ve sabitler var (`config.py` fallback secret, scriptlerde şifre).
- `except: pass` örneği mevcut (`api/routes.py` içinde en az bir örnek).
- `print()` kullanımı yüksek (özellikle script/debug dosyalarında).
- `TODO` noktaları var (webhook, AI placeholder, report PDF vb.).

### 3.2 Güvenlik Açıkları
- Çok sayıda `@csrf.exempt` (özellikle `api/routes.py`, `main/routes.py`, `auth/routes.py`, `micro/modules/shared/auth/routes.py`).
- `HGS` route'ları (`/micro/hgs`, `/micro/hgs/login/<id>`) login gerektirmeden oturum açtırıyor.
- Kod içinde hardcoded credential izleri var:
  - `verify_count.py`, `transfer_data.py`: açık DB URL
  - bazı scriptlerde açık parola stringleri
- `SECRET_KEY` fallback sabit.
- Dosya yükleme kontrolleri endpoint'e göre değişken:
  - Micro profil upload: extension + mime + 5MB var
  - `core_bp.kule_send`: uzantı kontrolü var, MIME/size doğrulaması sınırlı
- Session cookie güvenlik ayarları config'de net değil.
- CSP/Talisman sadece bir app-factory tarafında; çift factory nedeniyle korunma tutarsızlığı riski.

### 3.3 Performans
- N+1 azaltımı için bazı yerlerde `joinedload/selectinload` iyi kullanılmış (`micro/surec`, `app/routes/process`).
- Buna rağmen döngü içinde query örnekleri var (`sp_api_graph` içinde process bazlı KPI query).
- `.all()` kullanımı yaygın; pagination her yerde yok.
- Statik cache-busting (`?v={{ config['VERSION'] }}`) kısmi uygulanmış.
- Büyük dosya yüklemelerinde stream tabanlı/scan tabanlı güvenlik sınırlı.

---

## ADIM 4 — Frontend Analizi

### 4.1 CSS / Responsive
- CSS dosya sayısı: 62
- Toplam CSS boyutu: ~1.55 MB
- Tespit edilen breakpoint yoğunlukları: 576, 768, 992, 1200, 1400 (ek: 640, 1024)
- Responsive tutarlılık: micro tarafı daha modern/tutarlı; legacy template tarafında dağınık.
- Kullanılmayan class tespiti için kesin statik analiz yapılmadı; bu konuda kesin bilgim yok.

### 4.2 JavaScript
- JS dosya sayısı: 118
- Toplam JS boyutu: ~3.70 MB
- Inline `<script>` olan template sayısı yüksek (özellikle prototype/legacy alanlarda).
- `alert/confirm` kullanım kalıntıları var (`static/js/kurum_panel.js`, `static/js/surec_karnesi.js`, prototype dosyaları).
- JS dosyalarında Jinja `{{ }}` kalıntıları tespit edildi (`static/js/components/*` gibi dosyalarda template benzeri kullanım).
- `console.log` kalıntıları mevcut.

### 4.3 Template Analizi
- `templates/base.html`: Bootstrap ağırlıklı klasik layout.
- `ui/templates/platform/base.html`: Tailwind + Alpine + micro sidebar/topbar.
- İki base arasında stil/komponent paradigması farklı; ortaklaştırma yok.
- Extend ilişkisi:
  - Kök template'lerin büyük çoğunluğu `base.html` extend ediyor.
  - Micro template'lerin neredeyse tamamı `platform/base.html` extend ediyor.
- `profile_picture` / `profile_photo` adlandırma tutarsızlığı legacy dosyalarda devam ediyor.

---

## ADIM 5 — Modül Bazlı Derinlik Analizi

### 5.1 auth (kök + micro)
- Route sayısı: ~16 (yaklaşık; kök + micro toplam)
- Template: ~9
- JS/CSS: düşük-orta
- Test: sınırlı, doğrudan kapsama zayıf
- Riskli parça: profil foto yükleme ve CSRF istisna kararları

### 5.2 admin
- Route sayısı: ~45 (kök + micro)
- Template: ~30
- JS: yüksek
- Test: sınırlı/doğrudan az
- Riskli parça: yetki sınırları dağıtık; duplicate admin mantıkları

### 5.3 surec
- Route sayısı: micro 19 + kök process yüksek
- Template: ~9
- JS/CSS: orta
- Test: düşük
- Riskli parça: büyük tek dosya API, karmaşık dönemsel agregasyon

### 5.4 sp
- Route sayısı: micro 12 (+ kök strategy routeları)
- Riskli parça: grafik üretiminde döngü-ici query ve role/tenant dallanmaları

### 5.5 hgs
- Route sayısı: 2
- Riskli parça: login bypass benzeri hızlı giriş akışı

### 5.6 Diğer modüller
- `analiz`: servis bağımlı endpointler; hata durumları 500 dönebilir.
- `bireysel`: kullanıcı scoped CRUD daha temiz.
- `kurum`: tenant yönetimi/strateji güncelleme tutarlı.
- `proje` (micro): şu an iskelet.

---

## ADIM 6 — TASKLOG Analizi

- Toplam TASK başlığı: 32
- Durum:
  - Tamamlandı: 32
  - Devam ediyor: 0
  - Hata ile kapanan: 0
- En çok sorun/işlem görülen modül: `admin / users` (13 kayıt), ardından `auth / profil` (7 kayıt)
- Tekrarlayan tema:
  - Profil taşıma ve foto yükleme/CSRF
  - Admin kullanıcı yönetimi ve rol yetkileri
  - Blueprint/static path düzeltmeleri
- Son 10 TASK: `TASK-031` ... `TASK-022` aralığı (çoğu profil/admin düzeltmeleri)
- Yarım kalan/not uyarılı işler: bazı kayıtlarda “ileride uygulanmalı” notları var (örn. cache busting tüm sayfalara yayılımı).

---

## ADIM 7 — İyileştirme Önerileri

### 7.1 Acil (Güvenlik/Stabilite)
1. Kod tabanındaki hardcoded secret/DB URL/parolaları temizle ve rotate et.
2. `@csrf.exempt` kullanımını azalt; JSON endpointlerde CSRF token doğrulama standardı kur.
3. `HGS` modülünü production'da tamamen kapat (feature flag + env guard).
4. Tek app-factory mimarisine in; çift bootstrap akışını kaldır.
5. Session cookie güvenlik parametrelerini açıkça set et.

### 7.2 Kısa Vadeli (1-2 hafta)
1. auth/admin/process duplicate route bloklarını konsolide et.
2. `main/routes.py` ve `api/routes.py` böl-parçala (blueprint modülerleştirme).
3. Upload güvenlik katmanını merkezi utility'ye taşı.
4. `print()` yerine merkezi logger standardı uygula.

### 7.3 Orta Vadeli (1 ay)
1. Legacy `models/` ile `app/models/` dualitesini tasfiye et.
2. Template katmanında ortak design system kararı al (kök vs micro).
3. Endpoint sözleşmeleri için OpenAPI şemalarını gerçek zamanlı üret.
4. Sorgu profilleme + index review çalışması yap.

### 7.4 Uzun Vadeli
1. Tam modüler monolit veya servis ayrıştırma kararı (özellikle büyük route dosyaları için).
2. Asenkron işlerin Celery’ye sistematik taşınması.
3. Çok kiracılı veri izolasyonu için row-level policy veya ayrı schema stratejisi değerlendirmesi.

---

## ADIM 8 — Rekabet ve Trend Analizi

### 8.1 Benzer Ürünler
- ClearPoint, Cascade, AchieveIt, WorkBoard, Perdoo.
- Güçlü yön: Kokpitim’de micro modülerleşme + yerel ihtiyaçlara uygun süreç/KPI derinliği.
- Zayıf yön: kod tabanı tutarlılığı ve güvenlik operasyon olgunluğu, kurumsal rakiplere göre geride.

### 8.2 Teknoloji Trendleri
- Flask -> FastAPI geçişi:
  - Tam geçiş kısa vadede riskli (büyük legacy kod).
  - Önce API katmanında kademeli pilot daha mantıklı.
- SQLAlchemy 2.0 async:
  - Yüksek IO yoğun endpointler için faydalı olabilir.
  - Mevcut senkron mimaride doğrudan toplu geçiş maliyetli.
- HTMX/Alpine:
  - Micro katmanında zaten Alpine var; HTMX ile JS karmaşıklığı azaltılabilir.
- Redis cache:
  - Dashboard/analitik endpointlerde ciddi fayda sağlar.
- Celery/task queue:
  - Rapor üretimi, mail gönderimi, ağır analizler async'e alınmalı.

### 8.3 Ölçeklenebilirlik
- Mevcut yapının eşzamanlı kullanıcı kapasitesi için kesin benchmark yok; bu konuda kesin bilgim yok.
- Muhtemel darboğazlar:
  - Büyük monolit route dosyaları
  - Döngü içi sorgular
  - Tek proses Flask çalışma düzeni
- Multi-tenant izolasyon:
  - Kod seviyesinde `tenant_id` filtreleri yaygın.
  - Ancak merkezi policy enforcement eksik; atlanan endpoint olursa izolasyon riski doğar.

---

## ADIM 9 — Test Durumu

- Test dosyaları var (`tests/`, `test_*.py`, script testleri).
- Tahmini coverage: düşük-orta (kritik route/izin/izolasyon alanlarında sistematik coverage eksik).
- Kritik test edilmemiş görünen alanlar:
  - CSRF ve auth boundary testleri
  - Tenant izolasyonu regression testleri
  - Upload güvenlik testleri
  - Büyük CRUD akışları (admin/surec/sp)
- Öncelikli test önerisi:
  1. Auth + tenant isolation integration testleri
  2. CSRF enforced endpoint testleri
  3. Upload validation/security testleri
  4. Süreç KPI aggregate doğrulama testleri

---

## ADIM 10 — Dokümantasyon

- API dokümantasyonu:
  - Micro tarafında `/micro/api/docs` var (manuel endpoint listesi)
  - Swagger/OpenAPI bütüncül ve canlı değil
- Kurulum kılavuzu:
  - `README.md` var fakat kısmen güncellik problemi taşıyor (port/çalışma yolu farkları)
- Docstring:
  - Bazı dosyalarda iyi, genel olarak tutarsız
- Eksikler:
  - Mimari tek-kaynak doküman (hangi factory gerçek runtime?)
  - Güvenlik baseline dokümanı
  - Modül sınırları ve ownership dokümanı

---

## TASKLOG Formatında Önerilen Yeni Kayıtlar (Rapor Amaçlı)

- TASK-ÖNERİ-001 | Güvenlik | Hardcoded secret/credential temizliği ve rotate
- TASK-ÖNERİ-002 | Mimari | Çift app-factory birleştirme
- TASK-ÖNERİ-003 | Güvenlik | `@csrf.exempt` minimizasyonu + standart middleware
- TASK-ÖNERİ-004 | Güvenlik | HGS production guard
- TASK-ÖNERİ-005 | Refactor | `main/routes.py` ve `api/routes.py` parçalama
- TASK-ÖNERİ-006 | Test | Tenant isolation + auth regression paketi

---

## Sonuç

Proje güçlü bir ürün çekirdeğine sahip ancak aynı anda legacy + yeni mimarinin birlikte yaşaması nedeniyle bakım maliyeti ve güvenlik riski yükselmiş durumda. Kısa vadede güvenlik sertleştirme ve mimari sadeleştirme yapılırsa, orta vadede ölçeklenebilirlik ve geliştirme hızı anlamlı şekilde artar.
