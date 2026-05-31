# 📊 KOKPİTİM — PROJE AUDIT RAPORU (2026 Q2)

> **Audit tarihi:** 2026-05-23
> **Yöntem:** 3 paralel sub-agent + manuel doğrulama
> **Kapsam:** 15 micro modül + altyapı + legacy + tests + güvenlik
> **Çıktı dosyaları:** Bu rapor + [RISK-MATRISI-2026Q2.md](RISK-MATRISI-2026Q2.md) + [ROADMAP-2026H2.md](ROADMAP-2026H2.md)

---

## 🎯 EXECUTIVE SUMMARY

**Genel sağlık skoru:** 🟡 **Sağlam temel + kritik orta-ölçek borçlar.** Uygulama production-ready bir mimariye sahip, fakat 3 ana alanda yapısal iyileştirme gerekiyor: (1) Multi-year veri tutarlılığı, (2) Legacy yüzey sunset, (3) Test kapsamı + audit logging.

**3 en yüksek öncelik:**
1. 🔴 **Plan year NULL handling tutarsızlığı** (sp, surec, k_rapor — multi-year data corruption riski)
2. 🔴 **`app/routes/process.py` (1805 satır)** — legacy monolith, sunset gerekiyor
3. 🟠 **Audit logging eksikliği (S3 borcu)** — login/admin operasyonları log'lanmıyor

**Bugün çözüldü (bu oturumda):**
- ✅ OKR migration (`b2c3d4e5f009`) — tablolar yaratıldı
- ✅ Project soft-delete migration (`a1b2c3d4e008`) — is_active/deleted_at/deleted_by
- ✅ /kurum dropdown bug — Process listesi artık aktif plan_year'a göre filtreleniyor
- ✅ Tomofil 6-yıllık demo tenant (id=26, 48.283 KpiData)

---

## 📈 ÖZET METRİKLER

| Metrik | Değer |
|---|---|
| Micro modül sayısı | 15 |
| Toplam route | 339+ |
| Toplam DB modeli | 22 dosya / ~80 tablo |
| Toplam migration | 53 (OKR + project soft-delete dahil) |
| Test dosyası | 18 (~1.700 satır) |
| Legacy yüzey kod satırı | ~11.346 |
| Kritik açık güvenlik borcu | 2 (S1, S3) — S2 doğrulandı, üretimde kapalı |

### Modül başına yoğunluk (route + kod)

| Modül | Route | Kod (satır) | Tehlike |
|---|---|---|---|
| k_radar | 76 | 988 | 🟢 |
| sp | 52 | 2.541 | 🟡 |
| admin | 41 | 1.678 | 🟡 |
| surec | 37 | 2.797 | 🟠 |
| k_rapor | 25 | 1.999 | 🟡 |
| proje | 21 | ~2.000 | 🟡 |
| bireysel | 16 | 567 | 🟢 |
| api | 15 | 319 | 🟢 |
| marketing | 15 | 368 | 🟢 |
| shared | 12 | 364 | 🟢 |
| kurum | 11 | 384 | 🟢 (bugün düzeltildi) |
| masaustu | 7 | 668 | 🟡 |
| analiz | 7 | 144 | 🟢 |
| hgs | 6 | 75 | 🟢 (S2 doğrulandı) |

🟢 = sağlıklı · 🟡 = orta borç · 🟠 = yüksek borç · 🔴 = kritik

---

## 🌍 KESİŞEN KONULAR (CROSS-CUTTING)

### 1. Plan Year NULL Handling Tutarsızlığı 🔴

**Problem:** `plan_year_id=NULL` legacy verilere uyum için her modül kendi yaklaşımını geliştirmiş. Sonuç: aktif yıl filtresinde 2022 verisi 2024'te görünebiliyor, dropdown'larda tekrar var.

**Etkilenen yerler:**
- `micro/modules/sp/routes_pages.py:76` — `plan_year_id != None` kullanılıyor
- `micro/modules/sp/routes_flow.py:67` — `or_(plan_year_id == active.id, plan_year_id.is_(None))`
- `micro/modules/surec/routes_process.py` — bugün düzeltildi (sadece /kurum dropdown)
- `micro/modules/surec/routes_kpi_data.py:100+` — KpiData filter'da plan_year_id eksik
- `micro/modules/surec/routes_activity.py` — Activity filter'da plan_year_id eksik
- `micro/modules/k_rapor/routes.py:24-27, 448-456` — `get_active_plan_year_for_user()` bazı yerlerde çağrılıyor bazılarında hardcoded year

**Çözüm önerisi:** `app/utils/plan_year_filter.py` adında merkezi yardımcı yarat:
```python
def filter_by_plan_year(query, model, active_py_id, include_null=True):
    """Aktif plan year + NULL legacy veri kapsama"""
    if include_null:
        return query.filter(or_(model.plan_year_id == active_py_id, model.plan_year_id.is_(None)))
    return query.filter(model.plan_year_id == active_py_id)
```
Tüm modüller bu fonksiyonu kullansın.

### 2. N+1 Sorgu Riskleri 🟠

**Yaygın problem:** Process.leaders/members/owners + Activity.assignees + ProcessKpi.user gibi relationship'ler `lazy='select'`. Liste sayfalarında 100 process = 300+ sorgu.

**Tespit edilen yerler:**
- `micro/modules/surec/routes_process.py:84-88` — Process listesinde leader/member yüklenirken
- `micro/modules/k_rapor/routes.py:71-89, 278-308` — Strategy + SubStrategy zinciri
- `micro/modules/k_radar/routes_kp.py:74-78` — ProcessMaturity listesi
- `micro/modules/bireysel/routes.py:422-431, 437-485` — Timeline event'ler
- `micro/modules/proje/routes_project_crud.py` — project_members/observers/leaders

**Çözüm:** Her liste sorgusuna `.options(joinedload(...), selectinload(...))` ekle. Test:
```python
# tests/test_n_plus_one.py — her modül için
def test_process_list_query_count(db_session, snapshot):
    with sql_query_counter() as counter:
        Process.query.all()
    assert counter.count < 10  # mevcut 300+, hedef <10
```

### 3. Tenant Scope Validation Tutarsız 🟠

**Problem:** Bazı endpoint'lerde `current_user.tenant_id` kontrolü var, bazılarında yok. Cross-tenant data leakage potansiyeli.

**Risk:**
- `micro/modules/k_radar/routes_kp.py:74-84` — ProcessMaturity döndürürken tenant kontrolü yok (sadece user'dan alınan tenant_id ile filtreliyor, ama client başka process_id'yi request edebilir)
- `micro/modules/k_rapor/routes.py:1641-1654` — `/kurum-karsilastirma` Admin role check yapıyor ama case-sensitive string equality (`role_name == "Admin"`)
- `micro/modules/proje/routes_list.py:77` — `build_filtered_projects_query()` içinde tenant filter var mı? Doğrulanmadı

**Çözüm:** Merkezi decorator:
```python
@app_bp.route("/api/process/<int:process_id>")
@login_required
@verify_tenant_resource(Process, "process_id")  # Bunu yarat
def process_detail(process_id):
    ...
```

### 4. Audit Logging Eksikliği (S3 Borcu) 🟠

**Mevcut:** `AuditLog` modeli var (`app/models/audit.py`), `audit_logs` tablosu indekslenmiş. **KpiDataAudit** var.

**Eksik:**
- `app/routes/auth.py` — login_user() çağrısında AuditLog yok
- `app/routes/admin.py` + `micro/modules/admin/routes.py:321-328, 875-881` — Tenant/User CRUD'da audit log try/except ile silent fail
- Permission/role değişikliği log'lanmıyor
- Backup operasyonları log'lanmıyor

**Çözüm:** `app/utils/audit_helper.py`:
```python
def log_admin_action(user, action, resource_type, resource_id, old=None, new=None):
    """Centralized audit logger. Failure ASLA silent değil — sentinel log + sentry."""
    ...
```

### 5. Test Kapsamı 🟠

| Modül | Test dosyası | Kapsam tahmin |
|---|---|---|
| sp | 1 (`test_sp_strateji_haritasi.py`) | ~5% |
| k_radar | 1 (`test_k_radar_regression.py`) | ~0% (sadece fixture) |
| surec | 3 (`test_process_*.py`, `test_micro_proje_display.py`) | ~60% |
| k_rapor | 0 | 0% |
| proje | 1 (`test_project_service.py`) | ~30% |
| bireysel | 0 | 0% |
| admin | 0 | 0% |
| marketing | 0 | 0% |
| kurum | 0 | 0% |
| masaustu | 0 | 0% |
| hgs | 1 | iyi |
| Genel | `test_e2e_flow.py`, `test_models.py`, `test_validation.py`, `test_smoke_routes.py` | iyi |

**Çözüm:** Her modül için en az bir smoke test (`tests/test_<modül>_smoke.py`) — login sonrası ana sayfa render olabiliyor mu, kritik API'lar 200 dönüyor mu.

### 6. PDF Export Yok 🟡

**Mevcut:** Excel export var (`k_rapor/api/export-excel`).
**Eksik:** k_rapor sayfaları, bireysel karne, proje raporları için PDF export.

**Çözüm:** `weasyprint` veya `reportlab` entegrasyonu + her ana raporun PDF template'i.

---

## 🔍 MODÜL BAZINDA DETAYLI BULGULAR

### 📌 sp (Stratejik Planlama) — 52 route, 2.541 satır

**Yapı:** 9 dosyalı modül: `routes_pages`, `routes_strategy`, `routes_flow`, `routes_plan_year`, `routes_donemler`, `routes_sp_proje`, `routes_analysis`

**En kritik bulgular:**

| # | Bulgu | Konum | Öncelik |
|---|---|---|---|
| 1 | Plan year NULL handling 3 farklı pattern'le yapılıyor | routes_pages.py:76, routes_flow.py:67, routes_donemler.py | 🔴 KRİTİK |
| 2 | K-Vektor strateji + alt strateji ağırlık update atomic değil — partial state kalabilir | routes_strategy.py:125-144 | 🟠 YÜKSEK |
| 3 | `clone_full_plan_year()` rollback'te FK orphan riski | routes_plan_year.py:150+ | 🟠 YÜKSEK |
| 4 | `/sp/api/graph` limit yok — büyük tenant'larda OOM | routes_flow.py:99-150 | 🟠 YÜKSEK |
| 5 | `@sp_manage_required` sadece role check, tenant_id validation handler içinde | routes_strategy.py:145-180 | 🟡 ORTA |
| 6 | Strategy.source_strategy_id self-reference; clone cascade unclear | app/models/core.py:170 | 🟡 ORTA |
| 7 | Test coverage %5 (2 senaryo) | tests/test_sp_*.py | 🟠 YÜKSEK |

**Eksik özellikler:**
- Strateji ağırlık analizi (kurum hedefine katkı %)
- Strateji statüsü (başlanmış/risk'te/tamamlanmış — şu an sadece is_active)
- Edit history / audit trail
- Bulk strateji editor

---

### 📌 k_radar — 76 route, 988 satır

**Yapı:** 5 dosyalı: `routes_common` (hub), `routes_ks` (K-Süreç), `routes_kp` (K-Performans), `routes_kpr` (K-Proje), `routes_cross` (Paydaş/A3)

**En kritik bulgular:**

| # | Bulgu | Konum | Öncelik |
|---|---|---|---|
| 1 | Tenant scope validation: client başka process_id request edebilir | routes_kp.py:74-84 | 🔴 KRİTİK |
| 2 | ProcessMaturity sorgusu N+1 + index yok | routes_kp.py:74-78 | 🟠 YÜKSEK |
| 3 | Schedule persistence dosya sisteminde — multi-server'da sync sorunu | routes_common.py:50-60 | 🟡 ORTA |
| 4 | Recommendation state — race condition (concurrent users) | routes_common.py:95-110 | 🟡 ORTA |
| 5 | `_safe_json()` tüm error'ları 500 dönüyor — 400/403 ayrımı yok | routes_common.py:31-36 | 🟢 DÜŞÜK |
| 6 | Test coverage ~0% (sadece fixture) | tests/test_k_radar_regression.py | 🟠 YÜKSEK |

**Eksik özellikler:**
- Sektör benchmark karşılaştırma
- Risk → otomatik action item workflow
- EVM threshold alert
- Real-time push notifications

---

### 📌 surec — 37 route, 2.797 satır

**Yapı:** 9 dosyalı: `routes_process`, `routes_kpi`, `routes_kpi_data`, `routes_activity`, `routes_karne`, `routes_legacy`

**En kritik bulgular:**

| # | Bulgu | Konum | Öncelik |
|---|---|---|---|
| 1 | KpiData ve Activity'de plan_year_id filtresi yok — 2022 verisi 2024 karnesinde görünür | routes_kpi_data.py:100+, routes_activity.py | 🔴 KRİTİK |
| 2 | N+1 explosion: Process.leaders/members/owners + Activity.assignees | routes_process.py:84-88 | 🟠 YÜKSEK |
| 3 | KpiData + KpiDataAudit transaction atomicity zayıf | routes_kpi_data.py:150-200 | 🟠 YÜKSEK |
| 4 | Activity atanması cross-tenant olabilir (assigned user tenant kontrolü yok) | routes_activity.py:67-85 | 🟠 YÜKSEK |
| 5 | Process parent-child circular reference validation yok (A→B→C→A) | routes_process.py:250-270 | 🟡 ORTA |
| 6 | KPI period mismatch (Aylık PG'ye Çeyreklik veri) validation zayıf | routes_kpi_data.py:120-140 | 🟡 ORTA |
| 7 | `hesapla_basari_puani()` business logic, unit test yok — formula değişirse tarihsel tutarsızlık | routes_karne.py:100-150 | 🟡 ORTA |
| 8 | `accessible_processes_filter` — 3'lü `.any()` query — büyük tenant'ta performans | routes_process.py:98 | 🟡 ORTA |

**Eksik özellikler:**
- Bulk KPI Excel import (var mı belirsiz; varsa validation eksik)
- KPI versioning (şablon değişince tarihsel veri reconciliation)
- Faaliyet gecikme bildirim entegrasyonu
- Activity resource leveling (kapasite uyarısı)

---

### 📌 k_rapor — 25 route, 1.999 satır

**Yapı:** Tek dosya, alt yapı yok.

**En kritik bulgular:**

| # | Bulgu | Konum | Öncelik |
|---|---|---|---|
| 1 | N+1: Strategy + SubStrategy + Process zinciri | routes.py:71-89, 278-308 | 🟠 YÜKSEK |
| 2 | N+1: User lookup loop'larda | routes.py:443-444, 591-592 | 🟠 YÜKSEK |
| 3 | PG veri filtresi in-memory — SQL'de yapılmıyor | routes.py:31-40, 130-178 | 🟠 YÜKSEK |
| 4 | Plan year farkındalığı zayıf — bazı yerlerde hardcoded year | routes.py:24-27, 448-456 | 🟠 YÜKSEK |
| 5 | PDF export yok (sadece Excel) | routes.py (bütün) | 🟡 ORTA |
| 6 | `/kurum-karsilastirma` Admin check zayıf (string equality) | routes.py:1643-1654 | 🟡 ORTA |
| 7 | 0 test dosyası | — | 🟠 YÜKSEK |

**Eksik özellikler:**
- PDF export + scheduled raporlar
- Executive summary AI özetleyici
- Rapor kustomizasyonu (logo, custom metrik)
- Drilldown link'leri

---

### 📌 proje — 21 route, ~2.000 satır

**Yapı:** 5 dosyalı: `routes_list`, `routes_project_crud`, `routes_views`, `routes_tasks`, `helpers/permissions/display/portfolio_service`

**En kritik bulgular:**

| # | Bulgu | Konum | Öncelik |
|---|---|---|---|
| 1 | N+1: project_members/observers/leaders cascade loads | routes_project_crud.py | 🟠 YÜKSEK |
| 2 | Project ORM ↔ DB drift (BUGÜN çözüldü — migration uygulandı) | — | ✅ ÇÖZÜLDÜ |
| 3 | Task `due_date` vs `due_at` karmaşası — Gantt hangi alanı kullanıyor? | routes_tasks.py:68-73 | 🟡 ORTA |
| 4 | Legacy `Surec.query` fallback (modern `Process` geçişi tamamlanmamış) | routes_list.py:40-55, routes_project_crud.py:60-74 | 🟡 ORTA |
| 5 | Plan year support yok (Project.plan_year_id model'de ama formda yok) | routes_project_crud.py | 🟡 ORTA |
| 6 | Gantt performans riski — 500+ task render | routes_views.py | 🟠 YÜKSEK |
| 7 | RAID register (Risk/Assumption/Issue/Decision) — modeller var ama akış belirsiz | RaidItem model | 🟡 ORTA |
| 8 | Test coverage ~30% — Gantt/RAID için test yok | tests/test_project_service.py | 🟠 YÜKSEK |

**Eksik özellikler:**
- Gantt'ta görev bağımlılığı + kritik yol
- Resource leveling
- Baseline tracking (plan vs actual)
- EVM real-time hesap

---

### 📌 bireysel — 16 route, 567 satır

**En kritik bulgular:**

| # | Bulgu | Konum | Öncelik |
|---|---|---|---|
| 1 | Plan year fallback bulunamayınca davranış belirsiz | routes.py:381-388 | 🟡 ORTA |
| 2 | N+1: Timeline event yüklerken IndividualKpiData + IndividualActivityTrack ayrı loop | routes.py:437-485 | 🟠 YÜKSEK |
| 3 | `user_can_enter_pgv` cross-module import (sürec'ten) | routes.py:83 | 🟡 ORTA |
| 4 | `from services.alignment_score_service import` — modül yapısı belirsiz | routes.py:553-567 | 🟡 ORTA |
| 5 | PK sequence sync workaround — DB sağlığı problemi | routes.py:120, 156 | 🟢 DÜŞÜK |
| 6 | Bireysel karne PDF/Excel export yok | — | 🟡 ORTA |
| 7 | 0 test dosyası | — | 🟠 YÜKSEK |

**Eksik özellikler:**
- İK karne PDF
- Peer comparison (aynı departman ile)
- Year-over-year trend
- Development plan tracking
- 360° feedback

---

### 📌 admin — 41 route, 1.678 satır

**En kritik bulgular:**

| # | Bulgu | Konum | Öncelik |
|---|---|---|---|
| 1 | Logo upload — file type sadece extension check (SVG → XSS riski) | routes.py:1260-1264 | 🟠 YÜKSEK |
| 2 | Tenant logo path traversal — `os.path.join(folder, t.logo_path)` doğrudan | routes.py:68-72 | 🟠 YÜKSEK |
| 3 | Audit log silent fail (try/except içinde) | routes.py:321-328, 875-881 | 🟠 YÜKSEK |
| 4 | Login stats query subquery + outerjoin kompleks — case-sensitive string matching | routes.py:116-194 | 🟡 ORTA |
| 5 | Bulk import: CSV UTF-8-sig + Excel OPENPYXL — encoding tutarsızlığı | routes.py:1028-1029 | 🟢 DÜŞÜK |
| 6 | Tenant name unique check eksik (model-level constraint yok) | routes.py:1125 | 🟢 DÜŞÜK |
| 7 | i18n yok — tüm mesajlar hardcoded Türkçe | tüm dosya | 🟡 ORTA |

**Eksik özellikler:**
- Custom RBAC (role yaratma)
- Audit log retention policy
- SSO/LDAP entegrasyonu
- License management (feature gating)
- Backup encryption

---

### 📌 admin altyapı + diğer modüller

| Modül | Önemli bulgu |
|---|---|
| **marketing** | 0 test, public route güvenlik kontrolü yapılmadı |
| **masaustu** | 668 satır kod ama amaç belirsiz, 7 route — gözden geçirme adayı |
| **analiz** | 144 satır, 7 route — küçük, sağlıklı |
| **api** | 319 satır, 15 route — REST API, Swagger var mı? |
| **hgs** | ✅ S2 borç doğrulandı: prod'da `HGS_BYPASS_ENABLED=False` hardcoded; dev'de local IP check var |
| **kurum** | ✅ Bugün dropdown bug düzeltildi |
| **shared** | 3 alt modül (auth, ayarlar, bildirim) — sağlıklı modular yapı |

---

## 🏗️ ALTYAPI

### Konfigürasyon ve Extensions ✅

- Extensions doğru initialize (db, migrate, csrf, limiter, cache, login_manager, talisman)
- Config layering net (Development/Testing/Production)
- Secret key enforcement (config.py:33-35)
- pool_recycle=280s (Cloudflare 524 timeout uyumlu)
- Talisman CSP/X-Frame-Options/HSTS aktif (prod)

### Migration zinciri ✅

- 53 migration (OKR + project soft-delete dahil)
- Boşluk yok, downgrade'ler tanımlı
- Alembic head: `b2c3d4e5f009`

### Blueprint çakışmaları yok ✅

- 7 blueprint, namespace isolation doğru
- `LEGACY_PROCESS_BP_ENABLED=False` (micro/surec canonical)
- `LEGACY_DASHBOARD_BP_ENABLED=False`

### Frontend ✅

- Template path: `ui/templates/platform/` (sp/, k_radar/, k_rapor/, surec/, vd. dolu)
- Static: `ui/static/platform/`
- VERSION=1.0.7 cache busting
- 46+ CSS, modüler JS

---

## 🚧 LEGACY YÜZEY (~11.346 satır)

| Dosya | Satır | Durum | Sunset planı |
|---|---|---|---|
| `app/routes/process.py` | **1.805** | 🔴 LEGACY_PROCESS_BP_ENABLED=False ama dosya canlı | Q3 2026: silmek için ek test gerekiyor |
| `app/routes/admin.py` | 1.141 | 🟠 hala kullanılıyor | Q4 2026: micro/admin'e merge |
| `app/routes/auth.py` | 302 | 🟠 root blueprint | Q3 2026: shared/auth'a merge |
| `main/routes/` (4 dosya) | ~328 | 🟡 64+ route | Q4 2026 |
| `app/routes/dashboard.py` | 264 | 🟢 disabled by default | Q3 2026: sil |
| **`decorators.py` (root)** | **207** | 🔴 **0 reference** | **HEMEN SİL** (quick win) |

---

## 🔒 GÜVENLİK

### Kapalı borçlar ✅
- S4 (FakeLimiter) — kaldırıldı 2026-05
- S5 (CSP pasif) — production'da aktif

### Açık borçlar 🟠
| Kod | Sorun | Durum |
|---|---|---|
| **S1** | Legacy route çift yüzey | Sunset planı netleştirildi (bu rapor) |
| **S2** | HGS hızlı giriş | ✅ Doğrulandı — prod'da kapalı |
| **S3** | Rate limit storage | Prod'da Redis önerilir, mevcut memory |
| **(yeni)** | Audit log eksikliği | Login + admin operations |
| **(yeni)** | Logo upload — file magic byte check yok | XSS/SVG riski |
| **(yeni)** | Tenant scope validation tutarsız | K-Radar başta olmak üzere |

---

## ✅ BU OTURUMDA ÇÖZÜLENLER

| # | Sorun | Konum | Çözüm |
|---|---|---|---|
| 1 | OKR tabloları DB'de yok | migration eksik | `b2c3d4e5f009_okr_tables.py` yazıldı + uygulandı |
| 2 | Project ORM ↔ DB drift (is_active, deleted_at, deleted_by) | `a1b2c3d4e008` migration vardı ama uygulanmamıştı | flask db upgrade çalıştırıldı |
| 3 | /kurum dropdown — süreçler 6 kez tekrar ediyordu | `routes_process.py:204` | active_plan_year_id filtresi eklendi |
| 4 | Demo veri kalitesi düşük | KpiData tüm admin tarafından girilmişti | Süreç üyelerine rastgele dağıtım + aylık 50-150 ölçüm |

---

## 📋 TESPİT EDİLEN QUICK WIN'LER (sonraki sprint'te)

| # | Sorun | Tahmini efor |
|---|---|---|
| 1 | `decorators.py` (root) sil — 0 reference | 15 dk |
| 2 | Plan year filter helper (`app/utils/plan_year_filter.py`) | 1 saat |
| 3 | `surec/routes_kpi_data.py` ve `routes_activity.py`'a plan_year filtresi ekle | 2 saat |
| 4 | k_rapor `get_active_plan_year_for_user()` tutarlı kullanım | 2 saat |
| 5 | Logo upload magic byte check | 1 saat |
| 6 | Login audit log | 30 dk |
| 7 | Tenant create/edit audit log | 1 saat |
| 8 | `app/utils/audit_helper.py` merkezi yardımcı | 2 saat |

**Toplam tahmin:** ~10 saat (1 sprint başına dağıtılabilir)

---

> **Sonraki adım:** [RISK-MATRISI-2026Q2.md](RISK-MATRISI-2026Q2.md) + [ROADMAP-2026H2.md](ROADMAP-2026H2.md)
