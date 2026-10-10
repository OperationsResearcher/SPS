# Kokpitim — Mevcut Durum ve Mimari (Teknik Keşif)

> **Kapsam:** Salt okunur keşif. Kod, DB, config ve git değiştirilmedi; sunuculara bağlanılmadı; `.env` içeriği okunmadı (yalnızca değişken adları listelendi).
> **Kök:** `C:\kokpitim` (aşağıdaki yollar bu köke göredir).
> **Tarih:** 2026-10-10 · **Branch:** `claude/duzeltme-faz1-dogruluk` · **Son TASK:** TASK-311 (2026-10-06)
> **Yöntem:** Belgeler okundu; sayılar komutla ölçüldü (bölüm 8). Belge ile kod çeliştiğinde **kod/komut kanıtı önceliklidir**; çelişkiler bölüm 11'de listelendi.

---

## 1. Ürünün amacı ve kullanıcıya değeri

- **Ürün:** Kokpitim — Türkiye pazarına yönelik, çok kiracılı (multi-tenant) SaaS kurumsal performans yönetimi. Kaynak: `docs/PROJE-MASTER.md` §1, `docs/Kokpitim_Yetenekler.md` §1.
- **Tek platformda birleştirdiği zincir:** Strateji (SP) → Süreç (Surec) → KPI / Performans Göstergesi (PG) → Bireysel performans (karne). Belgeler bu zinciri "benzersiz değer" olarak tanımlar (`docs/PROJE-MASTER.md` §1). Belgede anılan rakipler: Cascade, Perdoo, ClearPoint, Monday.com, Power BI.
- **Kullanıcı rolleri:** Admin, tenant_admin, executive_manager, user (`docs/PROJE-MASTER.md` §1).
- **Kullanım bağlamı (kod kanıtı):** Kurum (tenant) bazlı veri izolasyonu (`config.py` → `TENANT_GUARD_MODE = "enforce"`), demo ortamı (`micro/modules/demo/routes.py`, `app/services/demo_reset_service.py`), EFQM/K-Radar olgunluk değerlendirmesi (`app/services/efqm_assessment.py`), karne ve puanlama motoru (`app/utils/karne_hesaplamalar.py`, `app/services/score_engine_service.py`).
- **Doğrulanamayan:** Müşteri sayısı, ticari plan ve fiyatlandırma belgelerde yoktur. Değer önerisi belgeden alınmıştır; işlevsel olgunluk bu raporda çalıştırılarak doğrulanmadı.

---

## 2. Teknoloji yığını (sürümlerle)

Kaynak: `requirements.txt`, `requirements-ai.txt`, `requirements-test.txt`, `requirements-pwa.txt`, `Dockerfile`, `docker-compose.yml`, `config.py`. Kurulu sürümler yerel `.venv` (`.venv/Scripts/python.exe`, **Python 3.13.7**) üzerinden `importlib.metadata` ile ölçüldü.

| Katman | Teknoloji | Gereksinim (requirements) | Yerelde kurulu |
|---|---|---|---|
| Dil / runtime | Python | Docker: `python:3.11-slim` (`Dockerfile`); CI: 3.11 (`.github/workflows/ci.yml`) | **3.13.7** (yerel venv) |
| Web çatısı | Flask | `>=3.0.2` | 3.1.3 |
| ORM | Flask-SQLAlchemy / SQLAlchemy | `>=3.1.1` / `>=2.0.36` | 3.1.1 / 2.0.50 |
| Migration | Flask-Migrate (Alembic) | `>=4.0.5` | 4.1.0 |
| Auth | Flask-Login | `>=0.6.3` | 0.6.3 |
| CSRF | Flask-WTF | `>=1.2.1` | 1.2.2 |
| Rate limit | Flask-Limiter | `==3.5.0` | 3.5.0 |
| Cache | Flask-Caching | `>=2.3.1` (`CACHE_TYPE` varsayılan SimpleCache, `config.py`) | 2.3.1 |
| i18n | Flask-Babel | `>=4.0.0` | 4.0.0 |
| WebSocket | Flask-SocketIO / python-socketio | `==5.3.5` / `==5.10.0` (async_mode threading) | 5.3.5 / 5.10.0 |
| Güvenlik başlıkları | Flask-Talisman | `>=1.1.0` (prod'da CSP) | 1.1.0 |
| Sunucu (Yayın/Test/Demo) | Gunicorn | `>=23.0.0`; `Dockerfile` CMD: 8 worker, 1 thread, `run:app` | 25.3.0 (yerel) |
| PostgreSQL sürücüsü | psycopg (v3) | `psycopg[binary]>=3.2.0`; `config.py` psycopg3'ü psycopg2'ye tercih eder | 3.3.4 (psycopg2 **kurulu değil**) |
| Veri / Excel | pandas, openpyxl | `>=2.3.0`, `>=3.1.2` | 3.0.2, 3.1.5 |
| Sayısal / ML | numpy, scikit-learn | `>=2.3.1`, `>=1.7.2` | 2.4.4, 1.8.0 |
| PDF / PPTX | reportlab, python-pptx | `>=4.0`, `>=1.0.0` | 4.5.1, 1.0.2 |
| PDF (HTML→PDF) | weasyprint | **yalnız** `requirements-ai.txt` `>=60.0` | 68.1 (yerel) |
| Arka plan işleri | Celery | `>=5.6.2` | 5.6.3 |
| Zamanlayıcı | APScheduler | `>=3.10.0` | 3.11.2 |
| Serialization | marshmallow / marshmallow-sqlalchemy | `==3.20.1` / `==0.29.0` | 3.20.1 |
| Redis | redis | `>=7.3.0` | 7.4.0 |
| Hata takibi | sentry-sdk[flask] | `>=2.43.0` | 2.57.0 |
| 2FA | pyotp, qrcode | `>=2.9`, `>=8.0` | ölçülmedi |
| Web Push | pywebpush | `>=2.3.0` (`requirements.txt`); `==1.14.0` (`requirements-pwa.txt`) | 2.3.0 |
| LLM | google-generativeai, openai, anthropic | yalnız `requirements-ai.txt` (`>=0.8.0`, `>=1.40.0`, `>=0.40.0`) | 0.8.6, 2.38.0, 0.104.1 |
| Test | pytest | `requirements-test.txt` `==7.4.3` | 7.4.3 |
| Frontend | Alpine.js, Chart.js 4.4.0, SweetAlert2 11, Tailwind (CDN) | — | `CLAUDE.md`, `docs/PROJE-MASTER.md` §2 |
| API docs | flask-swagger-ui | `>=5.21.0` | ölçülmedi |

**Veritabanı:** PostgreSQL zorunlu. `config.py::_require_postgres_uri()` SQLite URI'sini **reddeder** (RuntimeError). Bu, `docs/PROJE-MASTER.md` ve `CLAUDE.md`'deki "instance/kokpitim.db" ifadesiyle çelişir (bkz. bölüm 11).

**Bağımlılık sabitleme:** `requirements.txt` başlığı açıkça "tekrarlanabilir build GARANTİ ETMEZ" diyor; çoğu paket alt sınırla (`>=`) tanımlı, lock dosyası yok. Yerel 3.13 ile Docker 3.11 arasında sürüm paritesi yok (`Dockerfile` yorumu).

**Mimari desen:** Application Factory (`app/__init__.py::create_app`), tek DB instance (`extensions.py::db`), Blueprint'ler, strangler geçişi (legacy `main/`, `api/`, `app/routes/` → modern `micro/modules/`).

---

## 3. Giriş noktası ve uygulama başlangıcı

Akış: `app.py` → `create_app()` (`app/__init__.py`) → `config.py::get_config()` → extension init (`extensions.py`, `app/extensions.py`) → blueprint kaydı → zamanlayıcı (`app/utils/scheduler_leader.py`, PG advisory lock) → geliştirmede `app.run(127.0.0.1:5001)`.

- `app.py` — yerel giriş; proje venv'ine yeniden başlatır; `atexit` ile scheduler kapatır.
- `run.py` — Docker/Gunicorn giriş noktası (`Dockerfile` CMD'de `run:app`).
- `config.py` — `FLASK_ENV` ile `DevelopmentConfig` / `ProductionConfig` / `TestingConfig`. `TestingConfig.TENANT_GUARD_MODE = "off"` (bilinçli; yorum satırında gerekçe var).
- Kökteki diğer sunucu/ops dosyaları: `server.py`, `production_server.py`, `maintenance.py`, `github_sync.py`, `seed.py`, `pybasla.py`.

---

## 4. Modül listesi ve durumu

### 4.1 Launcher modülleri (kullanıcının gördüğü kartlar)

Kaynak: `micro/core/module_registry.py` satır 13–109 (`MODULES` listesi, 13 kayıt).

**Durum etiketleri:** *Tamamlanmış (kod)* = route + şablon + iş mantığı kod düzeyinde var ve belgede açık iş maddesi yok; *Kısmi* = kod var, belgede açık iş/roadmap maddesi var; *Yalnızca tasarım* = kodda karşılığı yok. Tümü **kod kanıtına** dayanır; işlevsel test çalıştırılmadı.

| Modül (id) | URL | Route (grep, dekoratör) | Şablon (`ui/templates/platform/…`) | Durum | Kanıt / not |
|---|---|---|---|---|---|
| `sp` Stratejik Planlama | `/sp` | 134 (`micro/modules/sp/`) | 31 | Tamamlanmış (kod); clone/graph sertleştirme kısmen açık | `micro/modules/sp/routes_*.py`; `docs/ROADMAP-2026H2.md` Sprint 6 (clone atomicity, graph limit) planlı |
| `surec` Süreç | `/process` | 43 (`micro/modules/surec/`) | 3 | Tamamlanmış (kod); karne/PG yıl-bazlı düzeltmeler aktif | `routes_kpi_data.py`, `routes_karne.py`; TASK-306…311 (Düzeltme Planı) |
| `kurum` Kurum | `/kurum` | 15 | 2 | Tamamlanmış (kod) | `micro/modules/kurum/` — `/organization/*` uçları (Vizyon/Misyon/Değer/Etik kimlik) |
| `bireysel` Bireysel | `/bireysel/karne` | 21 | 1 | Tamamlanmış (kod); şablon başka klasörde olabilir (doğrulanamadı) | `micro/modules/bireysel/routes.py`; PG unique indeks TASK-309 |
| `proje` Proje | `/project` | 25 | 14 (`platform/project`) | Kısmi | `ROADMAP` Sprint 8: RAID tam UI, Gantt pagination **planlı** |
| `analiz` Analiz | `/analysis`, `/k-radar/analysis` | 9 | 1 | Kısmi | Trend/sağlık/forecast/anomaly uçları var (`micro/modules/analiz/`); `Kokpitim_Yetenekler.md` §7 boşlukları yazıyor |
| `k_radar` K-Radar | `/k-radar` | 91 | 25 | Kısmi | EFQM/olgunluk: TASK-303/304 (yıl, NULL dahil). `ROADMAP` Sprint 7: recommendation state DB'ye taşıma, schedule persistence **planlı** |
| `k_rapor` K-Rapor | `/k-rapor` | 41 | 2 | Kısmi | `ROADMAP` Sprint 8: 5 rapor PDF'i **planlı**; `app/utils/pdf_export.py` ve `/k-report/api/export-pdf` mevcut |
| `admin` Yönetim | `/admin/users` | 90 | 19 | Tamamlanmış (kod) | Kullanıcı/kurum/paket/rol; GUV-01 kurumlar arası açık TASK-306'da yamalandı |
| `api` REST / Swagger | `/api/docs` | 15 (+ `kokpitim_project_api` 88 rota) | 1 | Tamamlanmış (kod) | `micro/modules/api/`, `app/api/`; `api/` kökü legacy |
| `ayarlar` Ayarlar | `/ayarlar` | (shared/ayarlar altında) | 3 | Tamamlanmış (kod) | `micro/modules/shared/ayarlar/` (SMTP ayarları, TASK-306 GUV-06) |
| `bildirim` Bildirim | `/bildirim` | (shared/bildirim altında) | 1 | Tamamlanmış (kod) | `micro/services/notification_triggers.py`, `micro/services/email_service.py` |
| `masaustu` Masaüstü | `/masaustu` | 11 | 2 | Tamamlanmış (kod) | `CLAUDE.md` ve `SISTEM-HARITASI` bunu "iskelet / 1 route" diye yazar — **çelişki**, kod 11 uç içeriyor |

### 4.2 Launcher'da listelenmeyen micro modüller

| Modül | Route | Şablon | Durum | Not |
|---|---|---|---|---|
| `raporlar` | 101 (`routes_faz0/1/3/5.py`) | 45 | Kod var, **launcher kaydı yok** | `module_registry.py` 13 id'den hiçbiri `raporlar` değil; erişim yolu doğrulanamadı. PROJE-MASTER ve SISTEM-HARITASI bu modülü anmaz. |
| `marketing` | 15 (`/`, `/ozellikler/*`, `/blog`, `/demo-talep`) | — (`static/marketing/`) | Tanıtım sitesi, kod var | `marketing_bp` ayrı blueprint |
| `demo` | 5 (`/demo/start/<key>`, `/demo/end`, `/demo/heartbeat`) | 2 | Tamamlanmış (kod); yalnız demo modunda | `KOKPITIM_DEMO_MODE=1`; sıfırlama: `app/services/demo_reset_service.py` |
| `shared/` | auth, ayarlar, bildirim, kule, my_tasks, scheduled_reports, search (≈23 rota) | — | Kod var | Çapraz modül; `shared/auth` login/profil |

### 4.3 Belgede var, kodda yok / kaldırılmış / yalnız tasarım

| Konu | Belge | Kod kanıtı |
|---|---|---|
| **HGS modülü** (`/MfG_hgs`) | `CLAUDE.md` §4 tablosu, `PROJE-MASTER.md` §3.3 | `KURALLAR-MASTER.md` §7 S2: "Tamamen kaldırıldı (2026-06-16)". `micro/modules/hgs/` yok. Yalnız kalıntı referanslar: `app/legacy_redirect_config.py`, `app/middleware/legacy_sunset.py`, `app/services/hata_kontrol_service.py`. |
| **Kurum Analiz Merkezi** (SWOT/PESTLE tabanlı analiz merkezi) | `Kokpitim_Yetenekler.md` §6–8 (öneri stratejisi) | Ayrı modül/route ailesi yok; `micro/`, `app/`, `ui/` içinde bu adla bir yapı bulunmadı. **Yalnızca tasarım/öneri.** (Marketing sayfasında `ozellikler/analiz-merkezi` tanıtımı var — `micro/modules/marketing/routes.py`.) |
| **Celery görev seti** | `Kokpitim_Yetenekler.md` §3.3 | `app/tasks.py` 4 görev dekoratörü içerir; ancak `docker-compose.yml`, `Dockerfile` ve `scripts/ops/` içinde `celery worker` çalıştıran komut bulunamadı. **Kod var, dağıtımda çalıştığı doğrulanamadı.** |
| **PDF/PPTX ~9 gerçek export** | `Kokpitim_Yetenekler.md` §5.2 | Kod: `app/utils/pdf_export.py`, `app/services/report_service.py`, `app/services/weekly_digest_service.py`, `micro/modules/bireysel/routes.py`, `micro/modules/k_rapor/routes.py`. Adet doğrulanmadı; `ROADMAP` Sprint 8 PDF'i yeni eklenecek olarak planlıyor. |

### 4.4 Legacy yüzey (eritilecek)

| Yüzey | Ölçüm | Kaynak |
|---|---|---|
| `main/routes/` (`main_bp`) | 48 dekoratör; `main/` içinde 8 py | GET yollarını `micro/`'a 301 yönlendirme: `app/middleware/legacy_sunset.py` |
| `api/` (kök) | 88 dekoratör, 10 py | `api/routes_*.py` |
| `app/routes/` (auth, totp, sso, admin…) | 73 dekoratör (`app/` geneli) | `app/routes/sso.py`, `app/routes/totp.py` |
| `models/` (kök, legacy) | 6 py | `models/strategy.py` (tablolar boş — `SISTEM-HARITASI.md` §5) |
| `templates/` (kök) | 62 html | `SISTEM-HARITASI.md` §7: 11 redirect-ölü şablon kaldı |
| `v2/`, `v3/`, `bsc/` | 2+2+2 py | Deney/eski; canlılık belirsiz |

---

## 5. Veri modeli ve akışı

### 5.1 Veri katmanı

- **Canonical:** `app/models/` — 32 py dosyası (`core.py`, `process.py`, `plan_year.py`, `tenant_year.py`, `portfolio_project.py`, k_radar/k_vektor/bsc/okr/esg/audit/notification…). `app/models/legacy_bridge.py` eski Türkçe adları alias'lar (`Surec` = `Process`).
- **Legacy:** `models/` (kök) — 6 py. `SISTEM-HARITASI.md` §5'e göre canonical veri modern tek kaynakta.
- **Model sınıfı sayısı:** `db.Model` / `Base` ile tanımlı 131 sınıf satırı (grep; mixin'ler dahil olabilir).
- **Çoklu kurum (tenant):** `tenant_id` / `kurum_id` ayrımı; `config.py::TENANT_GUARD_MODE = enforce` (`app/utils/tenant_guard.py`; muafiyetler: platform admin, holding/dealer, anonim, CLI/scheduler, açık bypass).
- **Çoklu yıl (Plan Year):** `plan_year_id` — `app/utils/plan_year_filter.py` (`include_null=True` ile legacy NULL kayıtlar dahil). TASK-309/311 NULL yıl sorununu ele alır.
- **Soft delete:** `is_active=False` kuralı (`docs/KURALLAR-MASTER.md` §3). Hard delete yasak.
- **Veri ortam kuralı:** Şema Yerel→Yayın (Alembic); veri Yayın→Yerel (`scripts/ops/yayin_yerele_cek.py`). `docs/KURALLAR-MASTER.md` §8.6.

### 5.2 İstek ve olay akışı

1. **İstek:** Gunicorn (Docker: `run:app`) → Flask → `app_bp` (micro modülleri) veya legacy blueprint'ler. Ortak katmanlar: CSRF (Flask-WTF), Talisman CSP (prod), rate limit (Flask-Limiter; `RATELIMIT_STORAGE_URL`), `legacy_sunset` middleware, `demo_guard` middleware (`app/middleware/demo_guard.py`), `tenant_guard`.
2. **Oturum:** Flask-Login; `session_version` ile parola değişince oturum düşürülür (TASK-306 GUV-11); `load_user` pasif kullanıcıyı reddeder. `config.py`: `SESSION_COOKIE_SAMESITE=Strict`.
3. **İş mantığı:** `micro/modules/*/routes*.py` → `app/services/*` ve `services/*` (kökte legacy, kısmen aktif) → SQLAlchemy → PostgreSQL.
4. **Puanlama:** `app/utils/karne_hesaplamalar.py` (bant çözümü) + `app/services/score_engine_service.py` (`aggregate_actuals`, `compute_pg_score`).
5. **Bildirim:** `micro/services/notification_triggers.py` → DB kaydı + Socket.IO push (`app/socketio_events.py`; oda üyeliği şartı TASK-306 GUV-16) + e-posta (`micro/services/email_service.py`; SMTP port allowlist, GUV-06). Web Push: `app/services/push_notification_service.py` (pywebpush).
6. **Zamanlanmış işler:** APScheduler (`app/__init__.py`, `services/*_scheduler.py`) — PG advisory lock ile tek lider (`app/utils/scheduler_leader.py`; KOD-02/PERF-01). `SCHEDULER_ENABLED` ile kapatılabilir. Celery görevleri (`app/tasks.py`) için dağıtım kanıtı yok (bkz. 4.3).
7. **Dış servisler:** LLM gateway (`app/services/llm_gateway.py`, 11 dosya kullanıyor; `GEMINI_API_KEY` ortam değişkeni), SSO (`app/routes/sso.py`), 2FA (`app/services/totp_service.py`), Sentry (`SENTRY_DSN`), SMTP (`MAIL_*`).
8. **Dışa aktarım:** JSON (API), Excel (pandas/openpyxl), PDF (reportlab / `app/utils/pdf_export.py`), PPTX (python-pptx).
9. **Önbellek:** Flask-Caching — `CACHE_TYPE` varsayılan SimpleCache; `docker-compose.yml` RedisCache ile çalışır.

---

## 6. Ortamlar ve deploy yöntemi

Kaynak: `docs/KURALLAR-MASTER.md` §8, `CLAUDE.md`. Aşağıdaki bilgiler belgeye dayanır; sunucu tarafı **doğrulanmadı** (SSH yasak).

| Ortam | URL | Yer / dizin (belge) | Port | DB (belge) | Not |
|---|---|---|---|---|---|
| **Yerel** | `http://127.0.0.1:5001` | `C:\kokpitim` | 5001 | Yerel PostgreSQL (PG18; kullanıcı belleği) | Geliştirme. Port 5000 yasak. |
| **Test** | `https://test.kokpitim.com` | Oracle VM `/opt/kokpitim-test/` | 5050 | `kokpitim_test_db` | Yayın öncesi staging |
| **Demo** | `https://demo.kokpitim.com` | Oracle VM `/opt/kokpitim-demo/` | 5080 | `kokpitim_demo_db` | Tomofil örnek kurum; oturum sonunda sıfırlama (KURALLAR §8.4) |
| **Yayın** | `https://www.kokpitim.com` | Oracle VM `/opt/kokpitim/` | 5000 | `kokpitim_db` | Müşteri verisi — kırmızı çizgi |

- **Üç sunucu ortamı (Test/Demo/Yayın) aynı fiziksel sunucuda** (`129.159.30.175`, Oracle); izolasyon dizin/port/DB seviyesinde. Yerel dördüncü ortamdır.
- **Akış:** Yerel → Test → Yayın; Demo paralel (Yerel → Demo). Yerel değişiklik doğrudan Yayın'a gitmez.
- **Deploy yolu (tercih):** `scripts/ops/oracle/yayina_ver.ps1 -Mod test|yayin -Onay` (`docs/KURALLAR-MASTER.md` §8.3). Elle yol: `scripts/ops/oracle/oracle_safe_deploy.sh`. Test/Demo container'ı image-baked'dir, bind-mount değildir (kullanıcı belleği: `project_test_demo_image_baked_gercegi`).
- **Commit/push:** `scripts/ops/git/commit_push.ps1` (`-Onay` zorunlu; secret dosyaları stage edilmez).
- **CI:** `.github/workflows/ci.yml` — Python 3.11, `ruff check .`, import guard scriptleri, pytest. Kullanıcı belleğinde GitHub Actions faturalandırma kilidi notu var (CI'nın koşmadığı; doğrulanamadı).
- **Ortam değişkenleri (yalnız adlar; `.env.example` + `config.py`):** `SECRET_KEY`, `SQLALCHEMY_DATABASE_URI`, `REDIS_URL`, `CACHE_TYPE`, `CACHE_REDIS_URL`, `RATELIMIT_STORAGE_URL`, `RATELIMIT_*`, `MAIL_*`, `KOKPITIM_DEMO_MODE`, `DEMO_*`, `TENANT_GUARD_MODE`, `LEGACY_SUNSET_ENABLED`, `SCHEDULER_ENABLED`, `SOCKETIO_CORS_ORIGINS`, `SESSION_LIFETIME_HOURS`, `SENTRY_DSN`, `FLASK_ENV`, `GEMINI_API_KEY`, `MAINTENANCE_*`, `ADMIN_BACKUP_MAX_UPLOAD_MB`. **Not:** `.env.example` bunların bir kısmını içermez (örn. `TENANT_GUARD_MODE`, `SCHEDULER_ENABLED`, `DEMO_*`) — kod ile örnek dosya arasında sapma var. Değerler bu raporda yazılmadı.
- **Yedekleme:** `app/services/yedekleme_service.py` — `.env*`, `*.pem`, `*.key`, `*.dump` arşive girmez; web'den DB/kod yedeği yalnız Yerel'de (TASK-306 GUV-08). Yayın dump'ı `backups/yayin/` altında (TASK-311).

---

## 7. Test ve çalıştırma komutları

```powershell
# Yerel çalıştırma (Windows, proje venv)
cd C:\kokpitim
.venv\Scripts\python.exe app.py          # http://127.0.0.1:5001

# Testler (pytest.ini: testpaths = tests; TestingConfig: TENANT_GUARD_MODE=off)
.venv\Scripts\python.exe -m pytest                    # tam suite
.venv\Scripts\python.exe -m pytest --collect-only -q  # yalnız toplama (ölçüm)
.venv\Scripts\python.exe -m pytest tests\test_tenant_guard.py

# Lint (CI ile aynı kapsam)
ruff check .        # ruff.toml; repo geneli ~228 hata arşiv klasörlerinde (TASK-306 notu)

# Migration (Flask-Migrate / Alembic)
.venv\Scripts\python.exe -m flask db upgrade     # doğru DB URI ile; yerel alembic_version sapması notu TASK-306'da

# Bağımlılık kurulumu (belge)
.venv\Scripts\pip.exe install -r requirements.txt
```

- **Test sayıları (ölçüldü):** 82 test dosyası (`tests/test_*.py`), 554 `def test_` tanımı (grep), **889 test toplandı** (`pytest --collect-only`). TASK-309/310 kayıtları son tam koşuyu 884/887 geçti diye yazar; bu raporda **tam suite koşulmadı**.
- **Dağıtımda test:** Yayın/Test deploy scriptlerinde test koşusu doğrulanmadı.

---

## 8. Sayılar (komutla ölçüldü)

| Metrik | Değer | Komut / yöntem |
|---|---|---|
| **Runtime route (url_map)** | **851** | `SCHEDULER_ENABLED=false .venv/Scripts/python.exe -c "from app import create_app; app=create_app(); print(len(list(app.url_map.iter_rules())))"` |
| Route — `app_bp` (modern) | **628** | Aynı çalıştırma, `endpoint.split('.')[0]` ile gruplama |
| Route — `kokpitim_project_api` / `main` / `marketing_bp` / `api_routes` / `admin_bp` | 88 / 48 / 16 / 14 / 12 | Aynı |
| Registered blueprint | 15 | `len(app.blueprints)` |
| Route dekoratörü (statik grep) | micro ≈642 (sp 134, raporlar 101, k_radar 91, admin 90, surec 43, proje 25, bireysel 21, shared 23, …); app 73; main 48; api 88 | `grep -rE "@\w+\.(route\|get\|post\|put\|delete\|patch)\(" <klasör>` (yaklaşık; runtime sayımı esas alınmalı) |
| Python dosyası (venv/ARCHIVE hariç) | 1938 | `find . -name '*.py' -not -path './.venv/*' -not -path '*/__pycache__/*' -not -path './ARCHIVE/*' \| wc -l` |
| Git izlenen `.py` | 872 | `git ls-files '*.py' \| wc -l` |
| `micro/` py / satır | 108 / 30.346 | `find micro -name '*.py' -exec cat {} + \| wc -l` |
| `app/` py / satır | 156 / 30.764 | Aynı yöntem |
| `services/` (kök) py / satır | 41 / 11.072 | Aynı yöntem |
| `api/` / `main/` / `models/` py | 10 / 8 / 6 | `find <klasör> -name '*.py' \| wc -l` |
| `app/models/` py | 32 | `ls app/models/*.py \| wc -l` |
| `db.Model` / `Base` sınıf satırı | 131 | `grep -rhE "^class \w+\(.*(db\.Model\|Base)" app/models models` |
| `migrations/versions` revizyon | 20 (tek head: `ux01a2b3c4d5`) | Python ile `revision` / `down_revision` zinciri; head = hiçbir down_revision'da geçmeyen |
| Migration toplam py (arşiv dahil) | 95 | `find migrations -name '*.py' \| wc -l` |
| `tests/test_*.py` | 82 | `find tests -name 'test_*.py' \| wc -l` |
| Test fonksiyonu (grep) | 554 | `grep -rE "^\s*def test_" tests` |
| Test toplanan (pytest) | **889** | `.venv\Scripts\python.exe -m pytest --collect-only -q -p no:cacheprovider` |
| Şablon (`ui/templates`) html | 168 | `find ui/templates -name '*.html' \| wc -l` |
| Kök `templates/` html | 62 | Aynı yöntem |
| `ui/` JS | 89 | `find ui -name '*.js' \| wc -l` |
| `scripts/` py / satır | 340 / 57.412 | Çoğu tek-seferlik ops. `scripts/_arsiv/` içinde py bulunamadı (bkz. bölüm 11) |
| Git commit | 749 | `git rev-list --count HEAD` |
| Çalışma ağacında değişiklik | 100 satır (M/D/??) | `git status --short \| wc -l` — **commit edilmemiş büyük değişiklik birikimi** |
| TASKLOG görev başlığı | 419 | `grep -c "^## TASK-" docs/TASKLOG.md` (son: TASK-311) |

---

## 9. Dokümantasyon ve operasyon kayıtları (referans)

- Ana kural: `CLAUDE.md`, `docs/KURALLAR-MASTER.md` (tek gerçek kaynak).
- Mimari: `docs/SISTEM-HARITASI.md` (2026-07-02 tarihli), `docs/PROJE-MASTER.md` (2026-05-19 tarihli — büyük ölçüde eski).
- Yol haritası: `docs/ROADMAP-2026H2.md` (Sprint 1–10, Mayıs–Ekim 2026). Son iş kayıtları (TASK-306…311) "Düzeltme Planı Faz 0/1/2" olarak ilerliyor; roadmap ile bu planın ilişkisi belgelenmemiş.
- Denetim: `docs/ekim2026/KOKPITIM-DETAYLI-ANALIZ-EKIM2026.md` (TASK-305; 173 bulgu, 30 özellik önerisi) ve `docs/ekim2026/DUZELTME-PLANI.md`. Bu rapor bunların yerine geçmez; GUV/HATA kodları için oraya bakılmalı.
- Güvenlik borcu (`docs/KURALLAR-MASTER.md` §7): S1 legacy çift yüzey, S3 rate-limit storage (Redis önerisi). S2/S4/S5 kapatılmış.

---

## 10. Veri akışı özeti (tek bakış)

`Tarayıcı → Gunicorn/Flask (CSRF, Talisman, rate limit, tenant_guard, demo_guard, legacy_sunset) → micro/modules route → app/services → app/models (SQLAlchemy) → PostgreSQL`; yan kanallar: `notification_triggers → Socket.IO + SMTP + Web Push`; `APScheduler (PG advisory lock) → servisler`; `llm_gateway → dış LLM API`.

---

## 11. Belge–kod çelişkileri (kod kanıtı önceliklidir)

| Konu | Belge diyor | Kod/komut gösteriyor |
|---|---|---|
| Route sayısı | SISTEM-HARITASI: 871 toplam, app_bp 593 | `create_app` url_map: **851**, app_bp **628** |
| Python dosya sayısı | SISTEM-HARITASI: 835 | 1938 (scripts dahil; venv hariç) |
| `_arsiv` script sayısı | SISTEM-HARITASI: 102 kök script `scripts/_arsiv/` altında | `scripts/_arsiv/` içinde `*.py` bulunamadı (dizin var mı ayrıca doğrulanmadı) |
| DB | CLAUDE.md §4 ve PROJE-MASTER §2: "instance/kokpitim.db" / SQLite | `config.py` SQLite'ı reddeder; PostgreSQL zorunlu |
| HGS | CLAUDE.md, PROJE-MASTER: aktif modül (2 route) | KURALLAR-MASTER: tamamen kaldırıldı (2026-06-16); modül dizini yok |
| Masaüstü | CLAUDE.md, SISTEM-HARITASI: iskelet / 1 route | 11 route, 2 şablon |
| Proje | PROJE-MASTER: 20+ route | 25 route |
| Python sürümü | Dockerfile / CI: 3.11 | Yerel venv 3.13.7 (Dockerfile yorumu bu paritesizliği belirtir) |
| Test sayısı / kapsam | PROJE-MASTER: coverage ~%5–15 | TASKLOG Düzeltme Planı: 884–887 test geçti (son koşu kayıtları); kapsam yüzdesi ölçülmedi |
| Celery | Yetenekler §3.3: görev seti var | `app/tasks.py` var; çalıştıran deploy yok |
| Çalışma ağacı | CLAUDE.md: branch disiplini (feature branch, main'e commit yok) | Branch `claude/duzeltme-faz1-dogruluk`; 100 değişiklik commit edilmemiş |

---

## 12. Doğrulanamayan bilgiler

1. **Yayın / Test / Demo sunucularının gerçek durumu** (container sürümü, DB, çalışan kod sürümü, `.env`): SSH yasak; bu rapor yalnız belgeye dayanır.
2. **Tam test suite'in bugün geçip geçmediği:** yalnız toplama (889) ölçüldü; koşulmadı. Son kayıtlar 884/887 yazıyor.
3. **Celery worker'ın hiçbir ortamda çalışıp çalışmadığı.**
4. **LLM sağlayıcılarının Yayın'da etkin olup olmadığı** (API anahtarı varlığı) ve hangi sağlayıcıların kullanıldığı.
5. **SSO (`app/routes/sso.py`) ve 2FA (`app/services/totp_service.py`)** hangi ortamda açık; üretim akışları çalıştırılmadı.
6. **PDF/PPTX export sayısı** (belgede ~9) ve weasyprint'in Docker imajında kurulu olup olmadığı (weasyprint yalnız `requirements-ai.txt`'te; Dockerfile `requirements.txt` kuruyor).
7. **`raporlar` modülünün erişim yolu** (launcher kaydı yok; başka bir yoldan açılıyor olabilir) ve rol/paket bazlı görünürlüğü.
8. **Modül "tamamlanma" yüzdeleri:** Durum etiketleri kod kanıtına dayanır; iş kuralı doğruluğu (karne puanı, EFQM) bu raporda yeniden hesaplanmadı. TASK-309/311 açık kalan maddeler bildiriyor (ör. "Yerelde 139 KMF PGV'si yanlış yıl görünüyor", "Yayın'da KMF hâlâ yılsız PG").
9. **Demo sıfırlama mekanizmasının Yayın/Demo'da çalıştığı** (kullanıcı belleği: "canlıda sıfırlama henüz YOK" kaydı).
10. **Ortam değişkenlerinin gerçek değerleri ve `ENCRYPTION_KEY` kullanımı:** kasıtlı olarak okunmadı; `ENCRYPTION_KEY` kullanıcı belleğinde deploy riski olarak geçer, kodda ayrıca doğrulanmadı.
11. **Git geçmişindeki sır sızıntısı:** TASK-305 kaydı "git'teki Yayın sırlarının döndürülmesi (GUV-02/OPS-01)" diyor. Bu keşif güvenlik denetimi değildir; bulgu içeriği bu raporda yer almaz.
12. **`instance/kokpitim.db` dosyasının varlığı:** CLAUDE.md oturum kontrolü bunu ister; bu keşifte kontrol edilmedi (uygulama SQLite kullanmıyor).
13. **Yerel `alembic_version` durumu:** TASK-306 notu, yerel DB'nin `Kalder/` kopyasının revizyonunda olduğunu ve `flask db upgrade`'in normal çalışmadığını yazıyor; bu rapor yeniden doğrulamadı.
14. **`scripts/_arsiv/` dizini:** belgelerde var, bu ortamda py dosyası bulunamadı; dizinin tamamen kaldırılıp kaldırılmadığı ayrıca doğrulanmadı.
15. **Kullanıcı sayısı, veri hacmi, performans ölçüleri (N+1, eşzamanlılık):** belgelerde iddialar var (ör. "~20–50 eşzamanlı kullanıcı", PROJE-MASTER §9); ölçülmedi.
16. **CI'nın son koşu durumu:** kullanıcı belleğinde faturalandırma kilidi notu var; GitHub erişimi yok.

---

*Bu rapor değişiklik içermez; yalnız `reports/audit/01-mevcut-durum-ve-mimari.md` dosyası oluşturulmuştur. Yollar `C:\kokpitim` köküne göredir.*
