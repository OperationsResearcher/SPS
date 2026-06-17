# KOKPİTİM — Sistem Haritası

> **Amaç:** "Bu kod tabanında neyin ne olduğu" tek sayfada. Kaybolduğunda buraya bak.
> **Son güncelleme:** 2026-06-16 (runtime + DB doğrulanmış sayılar)
> **Mimari yön:** Strangler — modern `micro/` + `app/` çekirdeği BÜYÜR, legacy ERİR. Bkz. [paketler/TEKNIK-BORC-ENVANTERI.md](paketler/TEKNIK-BORC-ENVANTERI.md).

---

## 1. Bir bakışta — boğulma matematiği

| | Sayı | Not |
|--|------|-----|
| Toplam `.py` (venv/pycache hariç) | 835 | _(102 kök script 2026-06-16'da `scripts/_arsiv/`'e taşındı — silinmedi, repo'da)_ |
| **Hakim olman gereken çekirdek** | **~40** | aşağıdaki "onboarding çekirdeği" |
| Canlı uygulama (route/model/servis) | ~184 | gerçek bedeni |
| Çevre gürültü (script/test/arşiv) | ~550 | zihinsel yük OLMAMALI |
| Toplam route (runtime) | **891** | aşağıda blueprint dağılımı |

**Anahtar gerçek:** 700+ dosyada boğulmana gerek yok — **~40 dosyaya** hakimiyet yeter. Gerisi tek-seferlik/test/ölü.

---

## 2. Çekirdek (her zaman yüklenir) — kökte 9 `.py`

| Dosya | Rol |
|-------|-----|
| `app.py` | WSGI giriş — `create_app()` çağırır, scheduler temizliği |
| `app/__init__.py` | **Flask factory** — blueprint kaydı, middleware, extension init (ana orkestratör) |
| `config.py` | Ortam config (`FLASK_ENV` → Development/Production; DB URI, flag'ler) |
| `extensions.py` | DB singleton (`from extensions import db` — tek doğru kaynak) |
| `app/extensions.py` | Flask extension'ları (csrf, cache, limiter, talisman, login) |
| `__init__.py` (kök) | Geriye-uyum: `from __init__ import create_app` (eski scriptler) |
| `run.py` / `server.py` / `production_server.py` | Sunucu çalıştırıcılar (yerel/waitress/prod) |
| `maintenance.py`, `github_sync.py` | Ops araçları (bakım, git push) |

---

## 3. Blueprint dağılımı (runtime — 891 route)

| Blueprint | Route | Katman | Durum |
|-----------|-------|--------|-------|
| **`app_bp`** | **556** | **MODERN** (`platform_core` → `micro/modules/*`) | ✅ Asıl modern yüzey |
| `main_bp` | 136 | LEGACY (`main/routes/*`) | ⚠️ Çoğu redirect-ölü / eski; eritiliyor |
| `kokpitim_project_api` | 94 | API (`app/api/routes.py`) | REST API v1 |
| `admin_bp` | 23 | `app/routes/admin.py` | Legacy admin (modern `micro/admin` ile paralel) |
| `marketing_bp` | 16 | `micro/modules/marketing` | Tanıtım/landing |
| `api_routes` + `process_performance_api` + `ai_api` | 33 | API | REST + AI + perf |
| `auth_bp` / `totp_bp` / `sso_bp` | 15 | `app/routes/*` | Login, 2FA, SSO |
| `dataconn_bp` / `push_api` / `swagger_ui` / `core_bp` | 11 | API/yardımcı | BI export, websocket, docs, health |

**Yön:** 556 modern vs 136 legacy → modern baskın. Yeni iş **yalnızca `app_bp` (micro/modules)**'a yazılır.

---

## 4. Modern platform modülleri (`micro/modules/` → `app_bp`)

Launcher modülleri (kullanıcının gördüğü kartlar — `micro/core/module_registry.py`):

| Modül | URL | Ne yapar |
|-------|-----|----------|
| `masaustu` | `/masaustu` | Kişisel özet / launcher |
| `sp` | `/sp` | Stratejik Planlama — strateji, alt strateji, PlanYear, OKR |
| `surec` | `/process` | Süreç yönetimi — süreç, PG/KPI, faaliyet, olgunluk |
| `kurum` | `/kurum` | Kurumsal kimlik (Vizyon/Misyon/Değer/Etik), strateji yönetimi |
| `bireysel` | `/bireysel/karne` | Bireysel performans — karne, hedef, hizalama |
| `proje` | `/project` | Proje yönetimi — Kanban, RAID, portföy, stratejik skor |
| `analiz` | `/analiz` | Performans analitiği — trend, sağlık skoru |
| `k_radar` | `/k-radar` | K-Radar — KS/KP/KPR/Cross radar, karar desteği |
| `k_rapor` | `/k-rapor` | Kurumsal raporlama merkezi (yönetici rolleri) |
| `admin` | `/admin/users` | Kullanıcı/kurum/paket/rol/audit yönetimi |
| `api` | `/api/docs` | REST API dokümantasyonu (Admin) |
| `ayarlar` | `/ayarlar` | Kurum + kullanıcı ayarları |
| `bildirim` | `/bildirim` | Bildirim merkezi |

`shared/` (cross-module): auth, ayarlar, bildirim, arama, görevlerim, zamanlanmış raporlar.
Paket→modül kapısı: `get_accessible_modules(user)` (paketleme/L1 için kritik — bkz. [paketler/PAKETLEME-STRATEJISI.md](paketler/PAKETLEME-STRATEJISI.md)).

---

## 5. Model katmanı

| Konum | Durum | İçerik |
|-------|-------|--------|
| **`app/models/`** | ✅ **CANONICAL** (~30 dosya) | `core.py` (User/Tenant/Role/Strategy/SubStrategy), `process.py` (Process/ProcessKpi/ProcessActivity), `portfolio_project.py`, `plan_year.py`, `tenant_year.py`, k_radar/k_vektor/bsc/okr/esg/audit/notification… |
| `app/models/legacy_bridge.py` | köprü | Legacy Türkçe isimleri (`Surec`=`Process`, `SurecPerformansGostergesi`=`ProcessKpi`) modern'e alias'lar |
| `models/` (kök) | ⚠️ legacy (az dosya) | `strategy.py` (AnaStrateji/AltStrateji — tablolar **boş**), user/dashboard/feedback. `models/process.py` **silindi** (2026-06-16, dead). |

**DB gerçeği (2026-06-16):** Veri katmanı zaten modern tek-kaynakta. Legacy tablolar boş ya da yok. Detay: [paketler/TEKNIK-BORC-ENVANTERI.md](paketler/TEKNIK-BORC-ENVANTERI.md). DB = PostgreSQL (yerel PG18), `instance/kokpitim.db` değil — bkz. proje memory.

---

## 6. Servis & yardımcı katman

- **`app/services/`** (~54 dosya, modern): analytics, anomaly, forecast, evm, ai_pivot_advisor, hata_kontrol_*, automated_reporting, email_digest, demo_reset, score_engine…
- `services/` (kök, ~42 dosya, legacy ama bazıları aktif): scheduler'lar (k_radar, task_reminder, early_warning), eski ai/report servisleri. `app/services/` ile kısmen çift; eritiliyor.
- `app/utils/` (~29): error_handlers, security (CSP/rate-limit), safe_urls, karne_hesaplamalar, file_validation…
- `app/middleware/legacy_sunset.py`: legacy GET path → modern 301 redirect (EXACT_ENDPOINT haritası).

---

## 7. Legacy yüzey (eritilecek — strangler hedefi)

| Yüzey | Ne | Durum |
|-------|-----|-------|
| `main/routes/*` (`main_bp`) | Eski HTML route'ları | Çoğu `legacy_sunset` ile modern'e 301. Temizlendi: `strategy_api.py` legacy yazma (Dalga 1); 7 redirect-ölü route + safe_urls fallback (2026-06-17); **`kurum_panel.py` 1600+→433 satır** (21 ölü route: kurum_paneli/admin_panel/v3*/13 proje alt-görünüm/stratejik-planlama-akisi — runtime 301/410 teyitli; CANLI seed_db/fix-bsc/portfoy/API'ler korundu). Kalan canlı API'ler (`/api/ai/*`, `/api/strategic-planning/graph`) main_bp'de. |
| `templates/` (kök) | Eski template'ler (127→110) | Modern `ui/templates/platform/` ile ölü ikiz. **2026-06-16:** 17 kesin-ölü (hiç render/extends/include yok: `*_backup`/`*_v2`/`*_modern`/`*_old`, eski `project_list`/`project_form` ikizleri) → `ARCHIVE/templates_dead/`. **Kalan iş:** 11 redirect-ölü template (route GET 301'leniyor, runtime teyitli — `dashboard.html`, `kurum_panel.html`, `project_list.html`… render eden route'larla birlikte temizlenecek). **Mock/deney route'ları (`/metaverse`, `/game-theory`, `/crisis`…) CANLI** (302→login, `@login_required`) — silinmez, paketlemede gizlenir. |
| `app/routes/process.py` | 1806 satır legacy süreç | `LEGACY_PROCESS_BP_ENABLED` flag'e bağlı; micro/surec canonical. |
| `bsc/`, `v2/`, `v3/` | BSC + eski API stub | BSC perspective canlı mı belirsiz (ayrı dikkat). |

---

## 8. Onboarding çekirdeği — yeni bakışta önce bunları oku (~12 dosya)

1. `app.py` → `app/__init__.py` (factory + blueprint kaydı)
2. `config.py`, `extensions.py` (config + DB)
3. `platform_core/__init__.py` (modern modül yükleme)
4. `micro/core/module_registry.py` (modül + paket kapısı)
5. `app/models/core.py` (User/Tenant/Strategy)
6. `app/models/process.py` (Process/ProcessKpi)
7. `micro/modules/{sp,surec,proje}/routes*.py` (alan örnekleri — 2-3 seç)
8. `app/services/score_engine_service.py` (servis deseni)
9. `app/middleware/legacy_sunset.py` (legacy→modern köprü)

---

## 9. Ortamlar & dizinler

Yerel (`127.0.0.1:5001`) → Test (`test.kokpitim.com`) → Yayın (`www.kokpitim.com`); Demo paralel. Bağlayıcı terim — "VM" tek başına yasak. Detay: [KURALLAR-MASTER.md §8](KURALLAR-MASTER.md).

## 10. Çevre gürültü (hakimiyet GEREKMEZ)

- `scripts/_arsiv/` — 102 tek-seferlik kök script (2026-06-16 taşındı). Bkz. [scripts/_arsiv/README.md](../scripts/_arsiv/README.md).
- `scripts/ops/` — resmi operasyonel/deploy scriptleri.
- `tests/`, `ARCHIVE/`, `migrations/_archive_versions/` — test + eski sürüm arşivi.
