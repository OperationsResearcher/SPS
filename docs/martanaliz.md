# Kokpitim — Master Dokümantasyon
> Hazırlanma tarihi: Mart 2026 | Versiyon: 1.0
> Bu döküman projeyi sıfırdan anlayıp üzerinde çalışabilmek için hazırlanmıştır.

---

## 1. PROJE GENEL BİLGİLERİ

### Projenin Adı ve Amacı
**Kokpitim** — Multi-tenant SaaS kurumsal performans yönetimi platformu.

Çözdüğü problem: Danışmanlık firmalarının müşteri kurumlarına (tenant) sunduğu stratejik planlama,
süreç yönetimi ve performans göstergesi (PG) takibini tek bir platformda toplamak.
Kurumlar kendi süreçlerini, PG'lerini, stratejilerini ve bireysel performanslarını yönetir.

### Hedef Kullanıcı Kitlesi
- Danışmanlık firmaları (platform sahibi — Admin rolü)
- Müşteri kurumlar (Tenant — tenant_admin, executive_manager rolleri)
- Kurum çalışanları (standard_user rolü)

### Projenin Mevcut Durumu
Aktif geliştirme aşaması (MVP sonrası). Temel modüller çalışır durumda.
Sprint 1–21 tamamlanmış; micro platform (yeni UI katmanı) aktif olarak geliştirilmekte.

### Genel Mimari Yaklaşım
**Monolith** — Tek Flask uygulaması, Blueprint tabanlı modüler yapı.
İki paralel UI katmanı mevcuttur:
- **Kök yapı** (`/...`) — Eski Jinja2 şablonları, legacy rotalar
- **Micro yapı** (`/micro/...`) — Yeni modüler platform, mc-* component sistemi

---

## 2. TEKNOLOJİ STACK'İ

### Backend
| Katman | Teknoloji | Versiyon / Not |
|--------|-----------|----------------|
| Dil | Python | 3.13 (pycache dosyalarından) |
| Framework | Flask | requirements.txt'te sabitlenmemiş, güncel |
| ORM | Flask-SQLAlchemy | — |
| Migration | Flask-Migrate (Alembic) | — |
| Auth | Flask-Login + Werkzeug password hash | Session tabanlı |
| CSRF | Flask-WTF | WTF_CSRF_ENABLED=True |
| Rate Limiting | Flask-Limiter | 200/gün, 50/saat (memory://) |
| Cache | Flask-Caching | SimpleCache (dev), RedisCache (prod) |
| WebSocket | Flask-SocketIO 5.3.5 | async_mode='threading' |
| Task Queue | Celery benzeri yapı yok; app/tasks.py manuel | — |
| Serialization | marshmallow 3.20.1 + marshmallow-sqlalchemy 0.29.0 | — |
| JWT | PyJWT 2.8.0 | API auth için |
| Error Tracking | sentry-sdk[flask] | Opsiyonel, SENTRY_DSN env ile |
| Excel/CSV | pandas + openpyxl | Raporlama ve bulk import |
| HTML Sanitize | bleach | XSS koruması |
| Async | eventlet 0.33.3 | SocketIO için |

### Frontend
| Katman | Teknoloji | Not |
|--------|-----------|-----|
| Şablon | Jinja2 (Flask built-in) | Server-side rendering |
| CSS Framework | Tailwind CSS (CDN) | Kök yapıda; micro'da mc-* custom sınıflar |
| UI Bileşenleri | mc-* component sistemi | ui/static/platform/css/components.css |
| İkonlar | Font Awesome | CDN |
| Bildirimler | SweetAlert2 | alert()/confirm() YASAK |
| Grafikler | Chart.js (muhtemelen) | analiz modülünde |
| Real-time | Socket.IO client | Flask-SocketIO ile eşleşik |
| State Management | Yok (SSR) | data-* attribute ile veri aktarımı |

### Database
- **Dev:** SQLite (`kokpitim.db`)
- **Prod:** PostgreSQL (SQLALCHEMY_DATABASE_URI env ile)
- **Migration:** Flask-Migrate / Alembic (`flask db migrate`, `flask db upgrade`)
- **Cache:** Redis (prod), SimpleCache (dev)

### Authentication
- Flask-Login session tabanlı
- Werkzeug `generate_password_hash` / `check_password_hash`
- JWT (PyJWT) — API endpoint'leri için ayrıca

### 3rd Party Servisler
| Servis | Kullanım |
|--------|----------|
| SMTP (Gmail varsayılan) | E-posta bildirimleri |
| Tenant özel SMTP | TenantEmailConfig modeli ile per-tenant |
| Sentry | Hata takibi (opsiyonel) |
| Redis | Cache + Rate limiting (prod) |
| Web Push | PushSubscription modeli, push_notification_service.py |

### Dev Tools
- python-dotenv (.env yönetimi)
- pytest (.pytest_cache mevcut)
- flask-swagger-ui (API dokümantasyonu)

---

## 3. KLASÖR & DOSYA YAPISI

```
kokpitim/
├── app/                          → Ana Flask uygulama paketi (kök yapı)
│   ├── __init__.py               → Application factory (create_app)
│   ├── extensions.py             → Tüm Flask extension'ları (db, cache, socketio vb.)
│   ├── tasks.py                  → Arka plan görevleri (Celery benzeri manuel)
│   ├── socketio_events.py        → SocketIO event handler'ları
│   ├── api/                      → REST API Blueprint'leri
│   │   ├── routes.py             → Ana API rotaları (/api/v1/...)
│   │   ├── ai.py                 → AI/ML API endpoint'leri
│   │   ├── auth.py               → API auth (JWT)
│   │   ├── push.py               → Web Push bildirim endpoint'leri
│   │   └── swagger.py            → Swagger UI entegrasyonu
│   ├── models/                   → SQLAlchemy model tanımları
│   │   ├── __init__.py           → db = SQLAlchemy() tanımı
│   │   ├── core.py               → Tenant, Role, User, Strategy, SubStrategy, Notification, Ticket
│   │   ├── saas.py               → SubscriptionPackage, SystemModule, ModuleComponentSlug, RouteRegistry
│   │   ├── process.py            → Process, ProcessKpi, KpiData, ProcessActivity, ActivityTrack + Bireysel modeller
│   │   ├── audit.py              → AuditLog
│   │   ├── notification.py       → Notification (Sprint 7-9 versiyonu), NotificationPreference, PushSubscription
│   │   ├── strategy.py           → SwotAnalysis
│   │   └── email_config.py       → TenantEmailConfig (per-tenant SMTP)
│   ├── routes/                   → Kök yapı Blueprint rotaları
│   │   ├── admin.py              → /admin/* rotaları
│   │   ├── auth.py               → /login, /logout, /register
│   │   ├── dashboard.py          → / ana sayfa
│   │   ├── hgs.py                → Hızlı giriş (dev)
│   │   ├── strategy.py           → Strateji rotaları
│   │   ├── process.py            → Süreç rotaları
│   │   └── core.py               → Genel core rotalar
│   ├── schemas/                  → Marshmallow serialization şemaları
│   │   ├── kpi_schemas.py        → KPI veri şemaları
│   │   ├── process_schemas.py    → Süreç şemaları
│   │   └── user_schemas.py       → Kullanıcı şemaları
│   ├── services/                 → İş mantığı servis katmanı
│   │   ├── analytics_service.py  → Analitik hesaplamalar
│   │   ├── anomaly_service.py    → Anomali tespiti
│   │   ├── automated_reporting_service.py → Otomatik raporlama
│   │   ├── cache_service.py      → Cache yönetimi
│   │   ├── ml_service.py         → Makine öğrenmesi servisi
│   │   ├── muda_analyzer.py      → Muda (israf) analizi
│   │   ├── notification_service.py → Bildirim gönderme
│   │   ├── process_deviation_service.py → Süreç sapma tespiti
│   │   ├── process_health_service.py → Süreç sağlık skoru
│   │   ├── push_notification_service.py → Web Push
│   │   ├── recommendation_service.py → AI öneri motoru
│   │   ├── report_service.py     → Rapor üretimi
│   │   ├── score_engine_service.py → PG skor hesaplama motoru
│   │   └── webhook_service.py    → Webhook entegrasyonu
│   └── utils/                    → Yardımcı araçlar
│       ├── audit_logger.py       → Audit log yazma
│       ├── cache_utils.py        → Cache dekoratörleri
│       ├── decorators.py         → @require_component, @_is_ajax
│       ├── error_tracking.py     → Sentry + logging setup
│       ├── karne_hesaplamalar.py → Karne puan hesaplama algoritmaları
│       ├── process_utils.py      → Süreç yardımcı fonksiyonları
│       ├── query_optimizer.py    → N+1 sorgu optimizasyonu
│       ├── security.py           → Rate limiter, security headers
│       └── validation.py         → Input validasyon
│
├── micro/                        → Yeni modüler platform (/micro prefix)
│   ├── __init__.py               → micro_bp Blueprint factory + tüm modül import'ları
│   ├── core/
│   │   ├── launcher.py           → /micro launcher (modül seçim ekranı)
│   │   └── module_registry.py    → MODULES listesi, get_accessible_modules()
│   ├── modules/                  → Her modül kendi klasöründe
│   │   ├── admin/routes.py       → /micro/admin/* — kullanıcı, kurum, paket yönetimi
│   │   ├── analiz/routes.py      → /micro/analiz — analiz merkezi
│   │   ├── api/routes.py         → /micro/api/docs — API dokümantasyonu
│   │   ├── bireysel/routes.py    → /micro/bireysel — bireysel performans
│   │   ├── hgs/routes.py         → /micro/hgs — hızlı giriş (dev)
│   │   ├── kurum/routes.py       → /micro/kurum — kurum paneli
│   │   ├── masaustu/routes.py    → /micro/masaustu — kişisel dashboard
│   │   ├── proje/routes.py       → /micro/proje — proje yönetimi
│   │   ├── sp/routes.py          → /micro/sp — stratejik planlama
│   │   ├── surec/routes.py       → /micro/surec — süreç yönetimi
│   │   └── shared/
│   │       ├── auth/routes.py    → /micro/login, /micro/logout
│   │       ├── ayarlar/routes.py → /micro/ayarlar — kullanıcı/kurum ayarları
│   │       └── bildirim/routes.py → /micro/bildirim — bildirim merkezi
│   ├── services/
│   │   ├── email_service.py      → Tenant SMTP ile e-posta gönderimi
│   │   └── notification_triggers.py → Bildirim tetikleyicileri
│   ├── static/micro/
│   │   ├── css/components.css    → mc-* component kütüphanesi (tek CSS dosyası)
│   │   └── js/admin.js           → Admin modülü JS (SweetAlert2 tabanlı)
│   └── templates/micro/
│       ├── base.html             → Micro platform ana layout
│       ├── launcher.html         → Modül seçim ekranı
│       └── [modül]/              → Her modülün kendi şablonları
│
├── config.py                     → Config sınıfı (Config, TestingConfig)
├── app.py / run.py               → Uygulama giriş noktası (port 5001)
├── requirements.txt              → Python bağımlılıkları
├── .env                          → Ortam değişkenleri (SECRET_KEY, DB URI)
├── migrations/                   → Alembic migration dosyaları
├── static/                       → Kök yapı statik dosyaları (dokunulmaz)
├── templates/                    → Kök yapı şablonları (dokunulmaz)
├── docs/                         → Proje dokümantasyonu
└── eski_proje/                   → Eski proje (SADECE OKUMA — referans)
```

---

## 4. VERİTABANI ŞEMASI (DATABASE SCHEMA)

### 4.1 Tablo Listesi ve İlişkiler

#### `tenants` — Kurum (Tenant)
| Alan | Tip | Zorunlu | Default | Açıklama |
|------|-----|---------|---------|----------|
| id | Integer PK | ✓ | — | — |
| name | String(255) | ✓ | — | Kurum adı |
| short_name | String(64) | — | NULL | Kısa ad |
| is_active | Boolean | ✓ | True | Soft delete |
| package_id | FK → subscription_packages | — | NULL | Abonelik paketi |
| created_at | DateTime | — | now() | — |
| activity_area | String(200) | — | NULL | Faaliyet alanı |
| sector | String(100) | — | NULL | Sektör |
| employee_count | Integer | — | NULL | Çalışan sayısı |
| contact_email | String(120) | — | NULL | Kurum e-postası |
| phone_number | String(20) | — | NULL | Telefon |
| website_url | String(200) | — | NULL | Web adresi |
| tax_office | String(100) | — | NULL | Vergi dairesi |
| tax_number | String(20) | — | NULL | Vergi numarası |
| max_user_count | Integer | — | 5 | Maks. kullanıcı |
| license_end_date | Date | — | NULL | Lisans bitiş |
| purpose | Text | — | NULL | Amaç (stratejik kimlik) |
| vision | Text | — | NULL | Vizyon |
| core_values | Text | — | NULL | Değerler |
| code_of_ethics | Text | — | NULL | Etik kurallar |
| quality_policy | Text | — | NULL | Kalite politikası |

#### `roles` — Rol
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| id | Integer PK | ✓ | — |
| name | String(64) UNIQUE | ✓ | Admin, tenant_admin, executive_manager, standard_user |
| description | String(255) | — | — |

#### `users` — Kullanıcı
| Alan | Tip | Zorunlu | Default | Açıklama |
|------|-----|---------|---------|----------|
| id | Integer PK | ✓ | — | — |
| email | String(255) UNIQUE | ✓ | — | — |
| password_hash | String(255) | ✓ | — | Werkzeug hash |
| first_name | String(64) | — | NULL | — |
| last_name | String(64) | — | NULL | — |
| is_active | Boolean | ✓ | True | Soft delete |
| tenant_id | FK → tenants | — | NULL | — |
| role_id | FK → roles | — | NULL | — |
| created_at | DateTime | — | now() | — |
| phone_number | String(20) | — | NULL | — |
| job_title | String(100) | — | NULL | Unvan |
| department | String(100) | — | NULL | Departman |
| profile_picture | String(500) | — | NULL | URL |
| theme_preferences | Text (JSON) | — | NULL | {theme, color} |
| layout_preference | String(20) | ✓ | 'classic' | classic / sidebar |
| notification_preferences | Text (JSON) | — | NULL | — |
| locale_preferences | Text (JSON) | — | NULL | {language, timezone} |
| show_page_guides | Boolean | ✓ | True | — |
| guide_character_style | String(50) | ✓ | 'professional' | — |

#### `subscription_packages` — Abonelik Paketi
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| id | Integer PK | ✓ | — |
| name | String(128) | ✓ | Paket adı |
| code | String(64) UNIQUE | ✓ | Benzersiz kod (slug) |
| description | String(512) | — | — |
| is_active | Boolean | ✓ | Soft delete |

#### `system_modules` — Sistem Modülü
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| id | Integer PK | ✓ | — |
| name | String(128) | ✓ | Modül adı |
| code | String(64) UNIQUE | ✓ | Benzersiz kod |
| description | String(512) | — | — |
| is_active | Boolean | ✓ | Soft delete |

#### `package_modules` — Paket-Modül (M2M)
| Alan | Tip | Açıklama |
|------|-----|----------|
| package_id | FK → subscription_packages | Composite PK |
| module_id | FK → system_modules | Composite PK |

#### `module_component_slugs` — Modül-Bileşen
| Alan | Tip | Açıklama |
|------|-----|----------|
| module_id | FK → system_modules | Composite PK |
| component_slug | String(128) | Flask endpoint adı |

#### `route_registry` — Rota Kaydı
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | Integer PK | — |
| endpoint | String(255) UNIQUE | Flask endpoint adı |
| url_rule | String(512) | URL pattern |
| methods | String(128) | GET, POST vb. |
| component_slug | String(128) | Atanan bileşen ismi |

#### `strategies` — Ana Strateji
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| id | Integer PK | ✓ | — |
| tenant_id | FK → tenants | ✓ | — |
| code | String(20) | — | Örn: ST1 |
| title | String(200) | ✓ | — |
| description | Text | — | — |
| is_active | Boolean | ✓ | Soft delete |
| created_at / updated_at | DateTime | — | — |

#### `sub_strategies` — Alt Strateji
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| id | Integer PK | ✓ | — |
| strategy_id | FK → strategies | ✓ | — |
| code | String(20) | — | Örn: ST1.1 |
| title | String(200) | ✓ | — |
| is_active | Boolean | ✓ | Soft delete |

#### `processes` — Süreç
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| id | Integer PK | ✓ | — |
| tenant_id | FK → tenants | ✓ | — |
| parent_id | FK → processes | — | Hiyerarşik yapı |
| code | String(20) | — | Örn: SR1 |
| name | String(200) | ✓ | Türkçe ad |
| english_name | String(200) | — | İngilizce çeviri |
| weight | Float | — | 0-100 skor ağırlığı |
| document_no | String(50) | — | KYS doküman no |
| revision_no | String(20) | — | — |
| status | String(50) | — | Aktif/Pasif |
| progress | Integer | — | 0-100 |
| is_active | Boolean | ✓ | Soft delete |
| deleted_at / deleted_by | DateTime/FK | — | Soft delete meta |

#### `process_kpis` — Süreç PG (Performans Göstergesi)
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| id | Integer PK | ✓ | — |
| process_id | FK → processes | ✓ | — |
| name | String(200) | ✓ | PG adı |
| code | String(50) | — | Örn: PG-01 |
| target_value | String(100) | — | Hedef değer |
| unit | String(50) | — | Birim |
| period | String(50) | — | Aylık/Çeyreklik/Yıllık |
| gosterge_turu | String(50) | — | İyileştirme/Koruma/Bilgi |
| target_method | String(10) | — | RG/HKY/HK/SH/DH/SGH |
| basari_puani_araliklari | Text (JSON) | — | Başarı puan aralıkları |
| weight | Float | — | Ağırlık |
| direction | String(20) | — | Increasing/Decreasing |
| calculated_score | Float | — | Hesaplanan skor |
| is_active | Boolean | ✓ | Soft delete |

#### `kpi_data` — PG Veri Girişi
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| id | Integer PK | ✓ | — |
| process_kpi_id | FK → process_kpis | ✓ | — |
| year | Integer | ✓ | — |
| data_date | Date | ✓ | — |
| period_type | String(20) | — | yillik/ceyrek/aylik |
| actual_value | String(100) | ✓ | Gerçekleşen değer |
| target_value | String(100) | — | Dönem hedefi |
| status_percentage | Float | — | Gerçekleşme % |
| user_id | FK → users | ✓ | Veriyi giren |
| is_active | Boolean | ✓ | Soft delete |

#### `process_activities` — Süreç Faaliyeti
| Alan | Tip | Zorunlu | Açıklama |
|------|-----|---------|----------|
| id | Integer PK | ✓ | — |
| process_id | FK → processes | ✓ | — |
| process_kpi_id | FK → process_kpis | — | Bağlı PG |
| name | String(200) | ✓ | — |
| status | String(50) | — | Planlandı/Devam/Tamamlandı |
| progress | Integer | — | 0-100 |
| is_active | Boolean | ✓ | Soft delete |

#### `activity_tracks` — Aylık Faaliyet Takibi
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | Integer PK | — |
| activity_id | FK → process_activities | — |
| year | Integer | — |
| month | Integer | 1-12 |
| completed | Boolean | Tamamlandı mı? |
| UNIQUE | (activity_id, year, month) | — |

#### `notifications` — Bildirimler (core.py versiyonu)
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | Integer PK | — |
| user_id | FK → users | — |
| tenant_id | FK → tenants | — |
| notification_type | String(50) | pg_performance_deviation, task_assigned vb. |
| title | String(200) | — |
| message | Text | — |
| link | String(500) | Yönlendirme URL |
| is_read | Boolean | — |
| created_at | DateTime | — |

#### `audit_logs` — Denetim Kaydı
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | Integer PK | — |
| user_id | FK → users | — |
| action | String(50) | CREATE/UPDATE/DELETE/LOGIN/LOGOUT |
| resource_type | String(50) | Process, KPI, User vb. |
| resource_id | Integer | — |
| old_values / new_values | JSON | Değişiklik detayı |
| ip_address | String(45) | — |
| created_at | DateTime | — |

#### `tenant_email_configs` — Tenant SMTP Ayarları
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | Integer PK | — |
| tenant_id | FK → tenants UNIQUE | — |
| use_custom_smtp | Boolean | Özel SMTP aktif mi? |
| smtp_host/port/tls/ssl | — | SMTP bağlantı bilgileri |
| smtp_username/password | String | Kimlik bilgileri |
| sender_name/email | String | Gönderici bilgisi |
| notify_on_* | Boolean | Bildirim tercihleri |

#### `swot_analyses` — SWOT Analizi
| Alan | Tip | Açıklama |
|------|-----|----------|
| id | Integer PK | — |
| tenant_id | FK → tenants | — |
| category | String(32) | strength/weakness/opportunity/threat |
| content | Text | — |
| is_active | Boolean | Soft delete |

### 4.2 Diğer Tablolar (Özet)
- `individual_performance_indicators` — Bireysel PG
- `individual_activities` — Bireysel faaliyet
- `individual_kpi_data` — Bireysel PG veri girişi
- `individual_activity_tracks` — Bireysel aylık takip
- `individual_kpi_data_audits` — Bireysel PG audit log
- `kpi_data_audits` — Süreç PG audit log
- `favorite_kpis` — Favori PG listesi
- `process_sub_strategy_links` — Süreç-Alt Strateji bağlantısı (katkı %)
- `process_members` / `process_leaders` / `process_owners_table` — M2M
- `tickets` — Destek talepleri
- `notification_preferences` — Bildirim tercihleri
- `push_subscriptions` — Web Push abonelikleri

### 4.3 Tablolar Arası İlişkiler (Özet)
```
Tenant (1) ──< User (N)
Tenant (1) ──< Process (N)
Tenant (1) ──< Strategy (N)
Tenant (1) ── TenantEmailConfig (1)
Tenant (N) >── SubscriptionPackage (1)
SubscriptionPackage (M) >──< SystemModule (M)  [package_modules]
SystemModule (1) ──< ModuleComponentSlug (N)
Strategy (1) ──< SubStrategy (N)
Process (1) ──< ProcessKpi (N)
Process (1) ──< ProcessActivity (N)
ProcessKpi (1) ──< KpiData (N)
ProcessActivity (1) ──< ActivityTrack (N)
Process (M) >──< SubStrategy (M)  [process_sub_strategy_links]
Process (M) >──< User (M)  [process_members, process_leaders, process_owners_table]
User (1) ──< IndividualPerformanceIndicator (N)
User (1) ──< IndividualActivity (N)
```

---

## 5. API DOKÜMANTASYONU

### 5.1 Micro Admin API Endpoint'leri (`/micro/admin/...`)

Tüm endpoint'ler `@login_required` ile korunur. JSON request/response.

#### Kullanıcı Yönetimi
| Method | URL | Auth | Açıklama |
|--------|-----|------|----------|
| GET | `/micro/admin/users` | Manager+ | Kullanıcı listesi sayfası |
| POST | `/micro/admin/users/add` | Manager+ | Yeni kullanıcı ekle |
| POST | `/micro/admin/users/edit/<id>` | Manager+ | Kullanıcı güncelle |
| POST | `/micro/admin/users/toggle/<id>` | Manager+ | Aktif/pasif toggle |
| POST | `/micro/admin/users/bulk-import` | Manager+ | CSV ile toplu import |

**POST /micro/admin/users/add — Request Body:**
```json
{
  "email": "string (zorunlu)",
  "first_name": "string",
  "last_name": "string",
  "password": "string (boş = Changeme123!)",
  "role_id": "integer",
  "tenant_id": "integer"
}
```
**Response:** `{"success": true, "message": "...", "id": 1}`

#### Kurum Yönetimi
| Method | URL | Auth | Açıklama |
|--------|-----|------|----------|
| GET | `/micro/admin/tenants` | Manager+ | Kurum listesi sayfası |
| POST | `/micro/admin/tenants/add` | Admin only | Yeni kurum ekle |
| POST | `/micro/admin/tenants/edit/<id>` | Manager+ | Kurum güncelle |
| POST | `/micro/admin/tenants/toggle/<id>` | Admin only | Arşivle/aktifleştir |

**POST /micro/admin/tenants/add — Request Body:**
```json
{
  "name": "string (zorunlu)",
  "short_name": "string",
  "sector": "string",
  "activity_area": "string",
  "employee_count": "integer",
  "contact_email": "string",
  "phone_number": "string",
  "website_url": "string",
  "tax_office": "string",
  "tax_number": "string",
  "max_user_count": "integer (default: 5)",
  "license_end_date": "YYYY-MM-DD",
  "package_id": "integer"
}
```

#### Paket & Modül Yönetimi
| Method | URL | Auth | Açıklama |
|--------|-----|------|----------|
| GET | `/micro/admin/packages` | Admin only | Paket listesi sayfası |
| POST | `/micro/admin/packages/add` | Admin only | Yeni paket |
| POST | `/micro/admin/packages/edit/<id>` | Admin only | Paket güncelle |
| POST | `/micro/admin/packages/toggle/<id>` | Admin only | Aktif/pasif |
| POST | `/micro/admin/modules/add` | Admin only | Yeni modül |
| POST | `/micro/admin/modules/toggle/<id>` | Admin only | Aktif/pasif |
| POST | `/micro/admin/components/sync` | Admin only | Route'ları tara ve kaydet |
| POST | `/micro/admin/components/update` | Admin only | Component slug güncelle |

#### Bildirim Yönetimi
| Method | URL | Auth | Açıklama |
|--------|-----|------|----------|
| GET | `/micro/admin/notifications` | Manager+ | Bildirim listesi |
| POST | `/micro/admin/notifications/broadcast` | Manager+ | Toplu bildirim gönder |
| POST | `/micro/admin/notifications/delete/<id>` | Manager+ | Soft delete (is_read=True) |
| GET | `/micro/admin/notifications/stats` | Manager+ | İstatistikler |

### 5.2 Genel Response Formatı
**Başarılı:**
```json
{"success": true, "message": "İşlem tamamlandı.", "id": 1}
```
**Hatalı:**
```json
{"success": false, "message": "Hata açıklaması."}
```
HTTP status: 400 (validation), 403 (yetki), 500 (sunucu hatası)

### 5.3 Kök Yapı API (`/api/v1/...`)
`app/api/routes.py` — Marshmallow şemaları ile serialize edilmiş REST API.
Swagger UI: `/api/docs` adresinde erişilebilir (flask-swagger-ui).
JWT auth: `app/api/auth.py` — Bearer token.

### 5.4 Micro Modül Sayfaları (GET rotaları)
| URL | Modül | Açıklama |
|-----|-------|----------|
| `/micro` | launcher | Modül seçim ekranı |
| `/micro/masaustu` | masaustu | Kişisel dashboard |
| `/micro/sp` | sp | Stratejik planlama |
| `/micro/surec` | surec | Süreç yönetimi |
| `/micro/kurum` | kurum | Kurum paneli |
| `/micro/bireysel/karne` | bireysel | Bireysel performans karnesi |
| `/micro/proje` | proje | Proje yönetimi |
| `/micro/analiz` | analiz | Analiz merkezi |
| `/micro/admin/users` | admin | Kullanıcı yönetimi |
| `/micro/admin/tenants` | admin | Kurum yönetimi |
| `/micro/admin/packages` | admin | Paket yönetimi |
| `/micro/admin/notifications` | admin | Bildirim yönetimi |
| `/micro/ayarlar` | ayarlar | Kullanıcı/kurum ayarları |
| `/micro/bildirim` | bildirim | Bildirim merkezi |
| `/micro/api/docs` | api | API referansı |
| `/micro/hgs` | hgs | Hızlı giriş (dev only) |

---

## 6. UYGULAMA MİMARİSİ & VERİ AKIŞI

### 6.1 Genel Request Akışı
```
Kullanıcı (Browser)
    │
    ▼
Flask Router (url_map)
    │
    ├── @login_required  →  Flask-Login session kontrolü
    │       │ Başarısız → /micro/login yönlendirme
    │
    ├── @require_component  →  Tenant paketi + modül erişim kontrolü
    │       │ Başarısız → 403 veya dashboard yönlendirme
    │
    ▼
Blueprint Route Handler (routes.py)
    │
    ├── GET  →  SQLAlchemy query → Jinja2 render_template → HTML response
    │
    └── POST (JSON) →  request.get_json()
                           │
                           ├── Validasyon
                           ├── SQLAlchemy model oluştur/güncelle
                           ├── db.session.commit()
                           └── jsonify({"success": True}) response
                                   │ Hata durumunda:
                                   ├── db.session.rollback()
                                   ├── current_app.logger.error(...)
                                   └── jsonify({"success": False, "message": "..."})
```

### 6.2 Authentication Flow
```
1. Kullanıcı /micro/login'e POST gönderir (email + password)
2. User.query.filter_by(email=email).first()
3. check_password_hash(user.password_hash, password)
4. login_user(user) → Flask-Login session'a yazar
5. Sonraki isteklerde: @login_required → current_user.is_authenticated
6. /micro/logout → logout_user() → session temizlenir
```

### 6.3 Yetkilendirme (Authorization) Akışı
```
Rol hiyerarşisi:
  Admin > tenant_admin > executive_manager > standard_user

@require_component(component_code):
  1. current_user.role.name in ("Admin", "tenant_admin", "executive_manager") → bypass
  2. current_user.tenant.package → SystemModule → ModuleComponentSlug zinciri
  3. component_slug eşleşmesi varsa → erişim verilir
  4. Yoksa → 403 veya dashboard yönlendirme

Micro admin rotaları:
  _is_admin()   → role.name in ("Admin",)
  _is_manager() → role.name in ("Admin", "tenant_admin", "executive_manager")
```

### 6.4 Modül Erişim Kontrolü (module_registry.py)
```
get_accessible_modules(user):
  1. Admin → tüm modüller
  2. Tenant paketi varsa → package.system_modules slug'larına göre filtrele
  3. Rol kısıtlamaları uygula (_ROLE_RESTRICTED dict)
  4. Paketsiz tenant → yalnızca minimum set (masaustu, bildirim, ayarlar)
```

### 6.5 PG Skor Hesaplama Akışı
```
KpiData (veri girişi)
    │
    ▼
score_engine_service.py
    │
    ├── target_method'a göre algoritma seç (RG, HKY, HK, SH, DH, SGH)
    ├── basari_puani_araliklari JSON'unu parse et
    ├── actual_value / target_value oranını hesapla
    └── calculated_score → ProcessKpi.calculated_score güncelle
```

### 6.6 Bildirim Akışı
```
Tetikleyici (notification_triggers.py)
    │
    ├── PG sapması, görev atama, faaliyet ekleme vb.
    │
    ▼
Notification model oluştur (core.py)
    │
    ├── DB'ye kaydet
    ├── SocketIO ile real-time push (socketio_events.py)
    └── E-posta (email_service.py → TenantEmailConfig SMTP veya sistem SMTP)
```

### 6.7 Cache Mekanizması
```
Flask-Caching (cache_utils.py dekoratörleri)
    │
    ├── Dev: SimpleCache (in-memory)
    └── Prod: RedisCache (REDIS_URL env)

Cache key prefix: "kokpitim_"
Default timeout: 300 saniye (5 dakika)
```

### 6.8 Real-time (WebSocket) Akışı
```
Flask-SocketIO (async_mode='threading')
    │
    ├── Client: Socket.IO JS client
    ├── Events: socketio_events.py
    └── Bildirim push: Notification oluşturulduğunda emit
```

---

## 7. COMPONENT / MODULE HARİTASI

### 7.1 Micro Platform Modülleri

#### `masaustu` — Kişisel Dashboard
- Tüm modüllerden gelen görevler, PG'ler ve iş planlarının özeti
- Kullanıcıya özel widget'lar
- API çağrısı: Kendi tenant'ının process, kpi, activity verileri

#### `sp` — Stratejik Planlama
- Ana stratejiler (Strategy) ve alt stratejiler (SubStrategy) CRUD
- Strateji-süreç bağlantısı yönetimi
- SWOT analizi (SwotAnalysis)

#### `surec` — Süreç Yönetimi
- Process hiyerarşisi (parent_id ile ağaç yapısı)
- ProcessKpi (PG) tanımlama ve veri girişi (KpiData)
- ProcessActivity ve ActivityTrack (aylık takip)
- Süreç üyeleri/liderleri/sahipleri atama

#### `kurum` — Kurum Paneli
- Tenant stratejik kimlik bilgileri (vizyon, misyon, değerler)
- Kurum bilgileri düzenleme
- Sadece tenant_admin, executive_manager, Admin erişebilir

#### `bireysel` — Bireysel Performans
- IndividualPerformanceIndicator CRUD
- IndividualActivity ve IndividualActivityTrack
- Bireysel karne görünümü
- Süreçten PG/faaliyet atama (source alanı)

#### `proje` — Proje Yönetimi
- Proje ve görev yönetimi
- Zaman çizelgesi görünümü

#### `analiz` — Analiz Merkezi
- Raporlar, grafikler, performans analizleri
- analytics_service.py, anomaly_service.py kullanır
- Muda (israf) analizi: muda_analyzer.py

#### `admin` — Yönetim Paneli
- Kullanıcı yönetimi (CRUD + bulk import)
- Kurum yönetimi (CRUD + arşivleme)
- Paket & modül yönetimi
- Bileşen senkronizasyonu (route_registry)
- Bildirim merkezi yönetimi

#### `ayarlar` — Ayarlar
- Kullanıcı profil ayarları (tema, dil, bildirim tercihleri)
- Kurum SMTP ayarları (TenantEmailConfig)
- E-posta bildirim tercihleri

#### `bildirim` — Bildirim Merkezi
- Kullanıcıya gelen bildirimlerin listesi
- Okundu/okunmadı yönetimi
- Topbar'da unread badge

### 7.2 Micro CSS Component Sistemi (`components.css`)
| Sınıf | Açıklama |
|-------|----------|
| `mc-card` | Beyaz kart, border-radius:12px, shadow |
| `mc-stat-card` | İstatistik kartı, renk varyantları: mc-stat-{indigo,emerald,amber,red,blue,purple} |
| `mc-btn` | Temel buton; varyantlar: mc-btn-{primary,secondary,danger,success,ghost,sm,lg} |
| `mc-table-wrap` | Tablo sarmalayıcı (overflow-x:auto) |
| `mc-table` | Standart tablo stili |
| `mc-badge` | Etiket; varyantlar: mc-badge-{success,warning,danger,info,gray,indigo,purple} |
| `mc-modal-overlay` | Modal arka plan (display:none → .open ile flex) |
| `mc-modal` | Modal kutu (max-width:680px) |
| `mc-modal-lg` | Geniş modal (max-width:780px) |
| `mc-modal-header/body/footer` | Modal bölümleri |
| `mc-form-input` | Form input stili |
| `mc-form-label` | Form etiket stili |
| `mc-page-header` | Sayfa başlığı (flex, space-between) |
| `mc-grid-{2,3,4}` | Responsive grid |
| `mc-avatar` / `mc-avatar-{sm,lg}` | Avatar dairesi |
| `mc-progress` / `mc-progress-fill` | Progress bar |
| `tm-grid` | 3 kolonlu tenant form grid |
| `tm-grid-2` | 2 kolonlu tenant form grid |
| `tm-field` / `tm-full` | Form alanı / tam genişlik |
| `tm-section-label` | Form bölüm başlığı |

### 7.3 Admin JS Modülleri (`admin.js`)
Tek dosya, IIFE pattern, üç ana bölüm:

**Kullanıcı Yönetimi** (`#admin-users-root` varsa aktif)
- `btn-user-add` → SweetAlert2 form modal
- `btn-bulk-import` → CSV dosya yükleme
- `.btn-user-edit` → SweetAlert2 düzenleme modal
- `.btn-user-toggle` → Aktif/pasif toggle
- `#user-search` → Anlık tablo filtresi

**Kurum Yönetimi** (`#admin-tenants-root` varsa aktif)
- `openTenantModal(null)` → Yeni kurum ekleme (native modal)
- `openTenantModal(dataset)` → Kurum düzenleme (native modal)
- `.btn-tenant-detail` → Detay görüntüleme (native modal)
- `.btn-tenant-toggle` → Arşivle/aktifleştir
- `#btn-toggle-archived` → Arşivlenenleri göster/gizle

**Paket & Modül Yönetimi** (`#admin-packages-root` varsa aktif)
- `btn-sync-components` → Route senkronizasyonu
- `btn-pkg-add` / `.btn-pkg-edit` / `.btn-pkg-toggle`
- `btn-mod-add` / `.btn-mod-toggle`

**Bildirim Yönetimi** (`#admin-notifications-root` varsa aktif)
- `btn-broadcast` → Toplu bildirim gönderme
- `.btn-notif-delete` → Soft delete

---

## 8. AUTHENTICATION & AUTHORIZATION

### 8.1 Kimlik Doğrulama
- **Yöntem:** Flask-Login session tabanlı (cookie)
- **Şifre:** Werkzeug `generate_password_hash` (PBKDF2-SHA256)
- **Session:** Flask secret key ile imzalanmış cookie
- **API:** PyJWT Bearer token (ayrı endpoint'ler için)

### 8.2 Kullanıcı Yükleme
```python
# app/__init__.py
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id)) if user_id else None
```

### 8.3 Rol Yapısı
| Rol | Açıklama | Erişim |
|-----|----------|--------|
| `Admin` | Platform sahibi (danışmanlık firması) | Her şey |
| `tenant_admin` | Kurum yöneticisi | Kendi kurumu + manager rotaları |
| `executive_manager` | Üst düzey yönetici | Manager rotaları |
| `standard_user` | Normal kullanıcı | Paket kapsamındaki modüller |

### 8.4 Korumalı Rotalar
```python
# Tüm rotalar @login_required ile korunur
@micro_bp.route("/admin/tenants")
@login_required
def admin_tenants():
    if not _is_manager():
        return render_template("platform/errors/403.html"), 403
    ...

# Bileşen bazlı koruma
@process_bp.route("/surec/<int:id>")
@login_required
@require_component("process_management")
def process_detail(id):
    ...
```

### 8.5 Login Redirect
```python
login_manager.login_view = "auth_bp.login"
login_manager.login_message = "Bu sayfayı görüntülemek için giriş yapmalısınız."
```

### 8.6 CSRF Koruması
- Flask-WTF CSRFProtect tüm POST form'larını korur
- AJAX istekleri: `X-CSRFToken` header ile
- Meta tag: `<meta name="csrf-token" content="{{ csrf_token() }}">`
- JS: `getCsrf()` fonksiyonu meta tag'den okur

---

## 9. ENVIRONMENT & KONFİGÜRASYON

### 9.1 .env Değişkenleri
| Key | Açıklama | Örnek Değer |
|-----|----------|-------------|
| `SECRET_KEY` | Flask session şifreleme anahtarı | Güçlü rastgele string |
| `SQLALCHEMY_DATABASE_URI` | Veritabanı bağlantı URL'i | `sqlite:///kokpitim.db` veya `postgresql://...` |
| `TEST_DATABASE_URI` | Test DB URI | `sqlite:///:memory:` |
| `REDIS_URL` | Redis bağlantı URL'i | `redis://localhost:6379/0` |
| `CACHE_TYPE` | Cache backend | `SimpleCache` / `RedisCache` |
| `MAIL_SERVER` | SMTP sunucu | `smtp.gmail.com` |
| `MAIL_PORT` | SMTP port | `587` |
| `MAIL_USE_TLS` | TLS aktif mi? | `true` |
| `MAIL_USE_SSL` | SSL aktif mi? | `false` |
| `MAIL_USERNAME` | SMTP kullanıcı adı | `bildirim@kokpitim.com` |
| `MAIL_PASSWORD` | SMTP şifresi | — |
| `MAIL_SENDER_NAME` | Gönderici adı | `Kokpitim` |
| `MAIL_SENDER_EMAIL` | Gönderici e-posta | `bildirim@kokpitim.com` |
| `SENTRY_DSN` | Sentry hata takip URL'i | Opsiyonel |

### 9.2 Config Sınıfları
```python
# config.py
class Config:          # Üretim/geliştirme temel config
class TestingConfig:   # Test ortamı (CSRF kapalı, in-memory DB)
```

### 9.3 Ortamlar
| Ortam | DB | Cache | Not |
|-------|-----|-------|-----|
| Dev | SQLite | SimpleCache | .env'de minimal ayar |
| Test | SQLite in-memory | SimpleCache | WTF_CSRF_ENABLED=False |
| Prod | PostgreSQL | RedisCache | Tüm env değişkenleri dolu olmalı |

### 9.4 Port
**Kesinlikle 5001** — `localhost:5000` yasaktır (proje kuralı).
```bash
flask run --port 5001
# veya
python run.py  # port=5001 hardcoded
```

---

## 10. BAĞIMLILIKLAR (DEPENDENCIES)

### 10.1 Production Dependencies (`requirements.txt`)
| Paket | Versiyon | Kullanım |
|-------|----------|----------|
| Flask | — | Web framework |
| Flask-WTF | — | CSRF koruması, form validasyonu |
| Flask-SQLAlchemy | — | ORM |
| Flask-Migrate | — | Alembic migration yönetimi |
| Flask-Login | — | Session tabanlı authentication |
| Flask-Limiter | — | Rate limiting |
| Flask-Caching | — | Cache (SimpleCache/Redis) |
| Flask-SocketIO | 5.3.5 | WebSocket / real-time |
| python-socketio | 5.10.0 | SocketIO Python implementasyonu |
| python-dotenv | — | .env dosyası yükleme |
| pandas | — | Excel/CSV işleme, raporlama |
| openpyxl | — | Excel okuma/yazma |
| bleach | — | HTML sanitizasyon (XSS koruması) |
| sentry-sdk[flask] | — | Hata takibi (opsiyonel) |
| redis | — | Redis client (prod cache) |
| marshmallow | 3.20.1 | API serialization/deserialization |
| marshmallow-sqlalchemy | 0.29.0 | SQLAlchemy model → marshmallow şema |
| eventlet | 0.33.3 | Async I/O (SocketIO için) |
| PyJWT | 2.8.0 | JWT token üretimi/doğrulaması |
| flask-swagger-ui | — | Swagger UI entegrasyonu |

### 10.2 Frontend Dependencies (CDN — requirements.txt'te yok)
| Kütüphane | Kullanım |
|-----------|----------|
| Tailwind CSS | Kök yapı utility sınıfları |
| Font Awesome | İkon seti |
| SweetAlert2 | Bildirim/onay pencereleri (alert() yasak) |
| Chart.js | Grafik ve görselleştirme |
| Socket.IO client | Real-time bildirimler |

---

## 11. MEVCUT SORUNLAR & TEKNİK BORÇ

### 11.1 Duplicate Model Tanımı
`app/models/core.py` ve `app/models/notification.py` dosyalarında **iki farklı `Notification` modeli** tanımlı:
- `core.py` → `notification_type`, `tenant_id`, `link` alanları var
- `notification.py` → `type`, `priority`, `action_url`, `extra_data` alanları var, `tenant_id` yok

Bu durum import sırasına göre hangisinin kullanıldığını belirsiz kılar. `core.py` versiyonu aktif kullanımda görünüyor.

### 11.2 Notification Model Çakışması
`notification.py`'deki `Notification` sınıfı `app.extensions.db`'yi import ederken,
`core.py`'deki `app.models.db`'yi kullanıyor. İkisi aynı SQLAlchemy instance olsa da
aynı `__tablename__ = 'notifications'` tanımı çakışma riski taşır.

### 11.3 RouteRegistry url_rule Alanı
`saas.py`'de `RouteRegistry` modeli `url_rule` alanını tanımlıyor ancak
`admin_components_sync` route handler'ı `url_pattern` adıyla kaydetmeye çalışıyor:
```python
db.session.add(RouteRegistry(
    endpoint=slug,
    url_pattern=str(rule),  # ← url_rule olmalı
    ...
))
```
Bu bir AttributeError'a yol açar.

### 11.4 Hard-coded Şifreler
`admin_users_add` ve `admin_users_bulk_import`'ta varsayılan şifre `"Changeme123!"` hard-coded.
Üretimde bu şifrenin zorunlu değiştirilmesini sağlayan bir mekanizma yok.

### 11.5 Test Coverage
`.pytest_cache` mevcut ancak test dosyaları görünür değil.
Servis katmanı (score_engine, analytics, ml_service) için test coverage belirsiz.

### 11.6 Eksik `app.py` / `run.py`
Workspace kökünde `app.py` veya `run.py` dosyası görünmüyor (gizli olabilir).
`create_app()` factory mevcut ama giriş noktası belirsiz.

### 11.7 Potansiyel N+1 Sorgu
`admin_tenants` route'unda `sum(len(t.users) for t in tenants)` ifadesi
her tenant için ayrı SQL sorgusu tetikler. `query_optimizer.py` mevcut ama
bu noktada kullanılmıyor.

### 11.8 SMTP Şifresi Düz Metin
`TenantEmailConfig.smtp_password` alanı düz metin olarak saklanıyor.
Model yorumunda "üretimde şifreli saklanmalı" notu var ama implementasyon yok.

### 11.9 TODO / FIXME Yorumları
Kod içinde `# Eski proje uyumluluğu` yorumları mevcut — eski proje alanlarının
modernize edilmesi tamamlanmamış.

---

## 12. TEST YAPISI

### 12.1 Mevcut Durum
`.pytest_cache` klasörü mevcut → pytest kullanılıyor.
`config.py`'de `TestingConfig` tanımlı:
```python
class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    WTF_CSRF_ENABLED = False
```

### 12.2 Test Komutu
```bash
pytest                    # Tüm testler (watch mode değil)
pytest --tb=short         # Kısa hata çıktısı
pytest -v                 # Verbose
```

### 12.3 Test Coverage Durumu
Test dosyaları workspace'de görünmüyor — muhtemelen `tests/` klasöründe veya
henüz yazılmamış. Servis katmanı (score_engine, analytics) için test coverage
zayıf olduğu değerlendiriliyor.

---

## 13. KURULUM & ÇALIŞTIRMA TALİMATLARI

### 13.1 Sistem Gereksinimleri
- Python 3.10+
- pip
- Redis (prod için, dev'de opsiyonel)
- PostgreSQL (prod için, dev'de SQLite yeterli)

### 13.2 Sıfırdan Kurulum
```bash
# 1. Repoyu klonla
git clone <repo-url>
cd kokpitim

# 2. Virtual environment oluştur
python -m venv venv
source venv/bin/activate        # Linux/Mac
venv\Scripts\activate           # Windows

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. .env dosyasını oluştur
cp .env.example .env            # Yoksa manuel oluştur
# .env içeriği (minimum):
# SECRET_KEY=guclu-rastgele-anahtar-buraya
# SQLALCHEMY_DATABASE_URI=sqlite:///kokpitim.db

# 5. Veritabanını oluştur
flask db upgrade

# 6. İlk admin kullanıcısını oluştur
python create_user.py           # veya check_admin.py

# 7. Uygulamayı başlat (PORT 5001 — 5000 YASAK)
flask run --port 5001
# veya
python run.py
```

### 13.3 Veritabanı Migration Komutları
```bash
flask db init          # İlk kez (migrations/ klasörü yoksa)
flask db migrate -m "Açıklama"   # Yeni migration oluştur
flask db upgrade       # Migration'ları uygula
flask db downgrade     # Bir önceki versiyona dön
flask db history       # Migration geçmişi
```

### 13.4 Geliştirme Ortamı Notları
- `micro/` altındaki değişiklikler için Flask hot-reload çalışır
- `static/` ve `templates/` kök klasörlerine dokunma — sadece `micro/` altında çalış
- Yeni bir micro modülü eklemek için:
  1. `micro/modules/<modül_adı>/routes.py` oluştur
  2. `micro/__init__.py`'ye import ekle
  3. `micro/core/module_registry.py`'deki `MODULES` listesine ekle
  4. `ui/templates/platform/<modül_adı>/` şablon klasörü oluştur

---

## 14. GELİŞTİRME NOTLARI & CONVENTIONS

### 14.1 Kodlama Standartları
| Kural | Detay |
|-------|-------|
| Backend dili | %100 İngilizce, snake_case |
| Frontend dili | %100 Türkçe (UI metinleri, mesajlar) |
| Değişken isimleri | `performance_indicator`, `pi_score` — asla `pg` (PostgreSQL ile karışır) |
| Port | **5001** — 5000 kesinlikle yasak |
| Bildirimler | Yalnızca SweetAlert2 — `alert()`, `confirm()`, `prompt()` yasak |
| Silme | Soft delete zorunlu — `is_active=False`, fiziksel silme yasak |
| Hata yönetimi | `except: pass` yasak — `current_app.logger.error()` + rollback zorunlu |

### 14.2 Frontend Katman Ayrımı
```
YASAK:
  HTML içinde <script> veya <style> bloğu
  .js dosyalarında {{ jinja2_ifadesi }}

DOĞRU:
  Tüm JS → ui/static/platform/js/
  Tüm CSS → ui/static/platform/css/
  Veri aktarımı → data-* attribute'ları
  Örnek: data-add-url="{{ url_for('micro_bp.admin_tenants_add') }}"
```

### 14.3 Blueprint Kuralı
```python
# YASAK: app.py'ye doğrudan rota ekleme
@app.route("/yeni-rota")  # ← YASAK

# DOĞRU: Blueprint modülü
@micro_bp.route("/yeni-rota")
@login_required
def yeni_rota():
    ...
```

### 14.4 Soft Delete Standardı
```python
# YASAK:
db.session.delete(obj)

# DOĞRU:
obj.is_active = False
db.session.commit()

# Veri çekerken:
Model.query.filter_by(is_active=True).all()
```

### 14.5 Hata Yönetimi Standardı
```python
try:
    # işlem
    db.session.commit()
    return jsonify({"success": True, "message": "İşlem tamamlandı."})
except Exception as e:
    db.session.rollback()
    current_app.logger.error(f"[fonksiyon_adi] {e}")
    return jsonify({"success": False, "message": "İşlem sırasında hata oluştu."}), 500
```

### 14.6 Micro Modül Ekleme Checklist
- [ ] `micro/modules/<ad>/__init__.py` oluştur
- [ ] `micro/modules/<ad>/routes.py` oluştur (tüm rotalar `@login_required`)
- [ ] `micro/__init__.py`'ye import ekle
- [ ] `module_registry.py` MODULES listesine ekle
- [ ] `ui/templates/platform/<ad>/` klasörü oluştur
- [ ] `ui/templates/platform/<ad>/index.html` → `{% extends "platform/base.html" %}`
- [ ] Gerekirse `_ROLE_RESTRICTED` dict'e ekle

### 14.7 PG Terminolojisi
```
PG = Performans Göstergesi (ASLA PostgreSQL değil)
Kod içinde: performance_indicator, pi_score, indicator_data
Tablo adı: process_kpis (KPI = Key Performance Indicator)
```

### 14.8 Micro vs Kök Yapı
```
Kök yapı (/...):
  - Eski Jinja2 şablonları
  - templates/ ve static/ klasörleri
  - DOKUNMA — sadece okuma/referans

Micro yapı (/micro/...):
  - Yeni modüler platform
  - ui/templates/platform/ ve ui/static/platform/
  - Tüm yeni geliştirmeler buraya
```

---

## ÖZET — Projeyi Hızlıca Anlamak İçin

1. **Giriş noktası:** `app/__init__.py` → `create_app()` factory
2. **Yeni UI:** `micro/` klasörü — tüm aktif geliştirme burада
3. **Veritabanı:** `app/models/` — core.py en kritik (Tenant, User, Role)
4. **İş mantığı:** `app/services/` — score_engine, analytics, notification
5. **Admin panel:** `/micro/admin/users` ve `/micro/admin/tenants`
6. **Kurallar:** Port 5001, SweetAlert2, soft delete, İngilizce backend, Türkçe frontend
7. **Çalıştırma:** `flask run --port 5001` veya `python run.py`

> Tarayıcı erişimi sağlanamadı, kod analizi yapıldı.
