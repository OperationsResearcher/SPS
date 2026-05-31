# 🗺️ KOKPİTİM — YOL HARİTASI 2026 H2 (Mayıs - Kasım)

> **Süre:** 6 ay (Mayıs 2026 → Kasım 2026)
> **Sprint sayısı:** 9 sprint × 2 hafta
> **Tema:** Stabilite + temel sağlamlaştırma + tüm core modüllerde derinleşme
> **Kaynak:** [PROJE-AUDIT-2026Q2.md](PROJE-AUDIT-2026Q2.md), [RISK-MATRISI-2026Q2.md](RISK-MATRISI-2026Q2.md)
> **Yaklaşım:** Sprint-based · risk-priority · her sprint sonu kabul kriteri

---

## 📅 SPRINT TAKVİMİ

| # | Sprint | Tarih | Tema | Risk skoru kapsanan |
|:-:|---|---|---|:-:|
| 0 | Quick wins (yapıldı) | 23 May | Tomofil demo + acil bug'lar | — |
| 1 | Plan Year Stabilite | 26 May → 6 Haz | Çoklu yıl veri tutarlılığı | ≥16 |
| 2 | Güvenlik & Audit | 9 Haz → 20 Haz | Tenant scope + audit log + logo XSS | ≥15 |
| 3 | N+1 + Test Altyapı | 23 Haz → 4 Tem | Performans + test framework | ~15 |
| 4 | Legacy Sunset Faz 1 | 7 Tem → 18 Tem | dashboard.py + decorators.py | ~16 |
| 5 | Surec Derinleşme | 21 Tem → 1 Ağu | KPI ↔ Aktivite hardening | ~12 |
| 6 | SP & K-Vektor Hardening | 4 Ağu → 15 Ağu | Clone atomicity + graph limit | ~12 |
| 7 | K-Radar Hardening + Test | 18 Ağu → 29 Ağu | Maturity + EVM + scope | ~12 |
| 8 | k_rapor + Proje Derinleşme | 1 Eyl → 12 Eyl | PDF export + Gantt | ~12 |
| 9 | Legacy Sunset Faz 2 | 15 Eyl → 26 Eyl | process.py + main/ | ~16 |
| 10 (rezerv) | Buffer + Roadmap 2027 | 29 Eyl → 10 Eki | Tamponlama, yeni plan | — |

> Toplam 9 ana sprint + 1 buffer = ~20 hafta gerçek iş + buffer

---

# SPRINT 1 — PLAN YEAR STABİLİTE 🔥
**26 Mayıs → 6 Haziran 2026**

## Hedef
Multi-year veri tutarlılığını sağlamak. Aktif yıl + NULL legacy desteğini 3 modülde aynı pattern'le yönetmek.

## İşler

### S1.1 — `app/utils/plan_year_filter.py` merkezi yardımcı (1 saat)
- `filter_by_plan_year(query, model, active_py_id, include_null=True)`
- Test: `tests/test_plan_year_filter.py`

### S1.2 — `surec/routes_kpi_data.py` plan_year filtresi (2 saat)
- Tüm KpiData listing/aggregation sorgularına `filter_by_plan_year()` eklemek
- Test: 2022 verisi 2024 karnesinde GÖRÜNMEMELI

### S1.3 — `surec/routes_activity.py` plan_year filtresi (2 saat)
- Aktiviteler listing'i yıl-aware
- Test: eski yıl aktivitesi yeni karnede GÖRÜNMEMELI

### S1.4 — k_rapor merkezi `active_py` kullanımı (3 saat)
- Hardcoded year parametreleri kaldır
- 25 endpoint için tutarlı plan year kullanımı

### S1.5 — sp routes_pages + routes_flow + routes_donemler tutarlılık (2 saat)
- 3 farklı NULL handling pattern'i birleştirilir

### S1.6 — N+1 guard test (mevcut) genişletilir (1 saat)
- `test_process_n1_guard.py` → tüm plan_year senaryoları

## Kabul Kriterleri
- [ ] Tomofil tenant'ında 2023 seçildiğinde sadece 2023 verisi görünüyor
- [ ] 2024 seçildiğinde KpiData satırı sayısı 2024'e ait (gözlem: ~5.000)
- [ ] Aktivite listesi yıl-aware
- [ ] Tüm yeni testler geçiyor (CI yeşil)
- [ ] Plan year helper'ı en az 5 yerde kullanılıyor

**Tahmini efor:** ~10 saat

---

# SPRINT 2 — GÜVENLİK & AUDİT 🔥
**9 Haziran → 20 Haziran 2026**

## Hedef
Production'da risk taşıyan 3 sorunu kapatmak: tenant scope, audit log, logo upload.

## İşler

### S2.1 — `@verify_tenant_resource` decorator (3 saat)
```python
@verify_tenant_resource(Process, "process_id")  # path parametresi
def process_detail(process_id): ...
```
- K-Radar endpoint'lerine ekle (öncelik)
- k_rapor `/kurum-karsilastirma` Admin role check düzelt
- Test: cross-tenant request 403 dönmeli

### S2.2 — `app/utils/audit_helper.py` merkezi yardımcı (2 saat)
- `log_admin_action(user, action, resource, old, new)`
- Sentinel log (audit yazımı başarısızsa Sentry)
- silent fail kaldırıldı

### S2.3 — Login audit log (1 saat)
- `auth/routes.py` ve `app/routes/auth.py` her login/logout için
- Test: 5 login → 5 audit log

### S2.4 — Tenant + User CRUD audit log (2 saat)
- `micro/modules/admin/routes.py:321-328, 875-881` silent fail kaldır
- Edit'lerde old/new değerler tutuluyor

### S2.5 — Logo upload magic byte check (1 saat)
- `python-magic` veya manual `PIL.Image.verify()`
- SVG reddedilir veya sanitize edilir
- Test: malicious SVG upload reddedilmeli

### S2.6 — Logo path traversal koruma (30 dk)
- `secure_filename(t.logo_path)` doğrulaması
- Test: `../etc/passwd` reddedilmeli

### S2.7 — `decorators.py` (root) sil (15 dk) — quick win
- Grep ile 0 reference doğrula → sil
- CI test'leri çalıştır

## Kabul Kriterleri
- [ ] Cross-tenant request 403
- [ ] Tüm admin CRUD audit_logs tablosunda görünüyor
- [ ] Login/logout audit'lendi
- [ ] Malicious upload reddediliyor (test mevcut)
- [ ] decorators.py silindi, CI yeşil

**Tahmini efor:** ~10 saat

---

# SPRINT 3 — N+1 + TEST ALTYAPI 🟠
**23 Haziran → 4 Temmuz 2026**

## Hedef
Performans en kritik problem (N+1 yaygınlığı). Test altyapısı kuruluyor.

## İşler

### S3.1 — N+1 detection test pattern (`tests/test_query_count.py`) (3 saat)
- `SQLQueryCountAssertion` context manager
- Snapshot-based query count regression test

### S3.2 — sp listing N+1 fix (2 saat)
- `routes_pages.py`'da SubStrategy.process_sub_strategy_links eager loading
- Test: 1 strateji = max 3 sorgu

### S3.3 — surec Process listing N+1 fix (2 saat)
- `routes_process.py:84-88` — leaders/members/owners + activities + KPI
- joinedload + contains_eager

### S3.4 — k_rapor sorgu birleştirme (3 saat)
- 16 API'da N+1 risk azalt
- `_user_lookup_cache` pattern

### S3.5 — k_radar ProcessMaturity index ekle (1 saat)
- Migration: `idx_process_maturity_tenant_active (tenant_id, is_active, updated_at)`
- Limit + cursor pagination

### S3.6 — Test smoke per-modül (4 saat)
- `tests/test_<modül>_smoke.py` her boş modül için (k_rapor, bireysel, admin, marketing, kurum, masaustu)
- Login → ana sayfa render → 200

## Kabul Kriterleri
- [ ] 100 Process listing < 20 sorgu (mevcut 300+)
- [ ] Test count: 18 → 24+ dosya
- [ ] N+1 regression test CI'da çalışıyor
- [ ] ProcessMaturity 10K satır < 1 saniye

**Tahmini efor:** ~15 saat

---

# SPRINT 4 — LEGACY SUNSET FAZ 1 🟠
**7 Temmuz → 18 Temmuz 2026**

## Hedef
Ölü kod ve disabled-by-default legacy yüzeyleri silmek. ~700 satır kod azaltma.

## İşler

### S4.1 — `app/routes/dashboard.py` (264 satır) sil (2 saat)
- LEGACY_DASHBOARD_BP_ENABLED zaten False
- Tüm import grep'i sıfır olmalı
- Test: smoke + e2e yeşil

### S4.2 — `app/routes/strategy.py` (195 satır) audit + sil (2 saat)
- micro/sp ile aynı endpoint'leri sağlıyor mu? Eski mi?
- 0 reference → sil

### S4.3 — `main/routes/__init__.py` ve modülleri audit (3 saat)
- `main/routes/api.py`, `dashboard.py`, `projeler.py`, `strateji.py`
- Hangileri sunset adayı?
- Geçiş haritası dokümante et

### S4.4 — `app/routes/admin.py` (1.141 satır) → micro/admin'e merge planı (4 saat)
- Endpoint diff: hangileri micro/admin'de yok?
- Migration takvimi (Sprint 6'da bitmek üzere)

### S4.5 — Test: `test_legacy_sunset.py` güçlendir (1 saat)
- Hangi endpoint'lerin 410 Gone döndüğü explicit

## Kabul Kriterleri
- [ ] `app/routes/dashboard.py` silindi
- [ ] `app/routes/strategy.py` silindi
- [ ] main/routes geçiş haritası yayınlandı
- [ ] Toplam kod tabanı ~700 satır azaldı
- [ ] Tüm test'ler yeşil

**Tahmini efor:** ~12 saat

---

# SPRINT 5 — SUREC DERİNLEŞME 🟡
**21 Temmuz → 1 Ağustos 2026**

## Hedef
Surec modülünün edge case'lerini kapatmak (transaction, validation, hierarchy).

## İşler

### S5.1 — KpiData + KpiDataAudit transaction atomicity (3 saat)
- Tek transaction'da, hata durumunda full rollback
- Test: zorla flush hatası → orphan log yok

### S5.2 — Process parent-child circular reference validation (1 saat)
- A→B→C→A engelleyici
- Recursive walk + visited set

### S5.3 — KPI period mismatch validation (2 saat)
- Aylık PG'ye sadece ay-uyumlu veri
- Çeyreklik PG'ye sadece çeyrek
- Form-side + server-side

### S5.4 — `hesapla_basari_puani()` unit test'leri (3 saat)
- Edge case: target=0, actual=0, direction=Decreasing
- Tarihsel formula değişimine karşı snapshot test

### S5.5 — Activity assignee cross-tenant kontrol (1 saat)
- `assigned_user.tenant_id == process.tenant_id` validate
- Test: ihlal → 403

### S5.6 — `accessible_processes_filter` performans (2 saat)
- 3× `.any()` query → EXPLAIN analiz
- Gerekirse materialized view veya subquery

### S5.7 — Bulk KPI Excel import + validation (3 saat)
- Şablon Excel + smart mapping
- Validation: decimal, plan year, duplicate detection

## Kabul Kriterleri
- [ ] Transaction atomicity test geçiyor
- [ ] Circular hierarchy reddediliyor
- [ ] Period mismatch reddediliyor
- [ ] hesapla_basari_puani %100 unit test kapsamı
- [ ] Bulk import çalışıyor

**Tahmini efor:** ~15 saat

---

# SPRINT 6 — SP & K-VEKTOR HARDENING 🟡
**4 Ağustos → 15 Ağustos 2026**

## Hedef
SP modülünün clone/graph/k-vektor edge case'lerini kapatmak.

## İşler

### S6.1 — K-Vektor weight update atomic transaction (2 saat)
- Strategy + SubStrategy weight tek transaction
- Test: partial fail → rollback

### S6.2 — `clone_full_plan_year()` FK orphan koruma (3 saat)
- Try/except savepoint + cleanup
- Test: hata durumunda yeni yıl tamamen rollback

### S6.3 — `/sp/api/graph` pagination + limit (2 saat)
- `?limit=50&cursor=X` paging
- Default 50, max 500

### S6.4 — Strategy edit history audit (2 saat)
- StrategyAudit model + trigger
- Edit history sayfası (admin/dashboard'a link)

### S6.5 — Strategy status (Başlanmış/Risk'te/Tamamlandı) (3 saat)
- `Strategy.status` ve `Strategy.status_updated_at`
- Migration
- UI badges

### S6.6 — Strategy bulk editor (3 saat)
- Multi-row inline edit
- Yıl bazlı bulk operations

## Kabul Kriterleri
- [ ] K-Vektor atomic
- [ ] Clone safe (orphan yok)
- [ ] Graph 1000+ strateji'de OOM yok
- [ ] Strategy status UI'da
- [ ] Bulk editor canlı

**Tahmini efor:** ~15 saat

---

# SPRINT 7 — K-RADAR HARDENING + TEST 🟡
**18 Ağustos → 29 Ağustos 2026**

## Hedef
K-Radar'ın production'a hazır seviyeye gelmesi: scope + state + test.

## İşler

### S7.1 — Recommendation state DB'ye taşı (2 saat)
- Şu an file-based → DB-based
- Race condition giderildi

### S7.2 — Schedule persistence DB (3 saat)
- File system → DB tablosu (`k_radar_schedules`)
- Multi-server safe

### S7.3 — `_safe_json()` HTTP status differentiation (1 saat)
- 400, 403, 404, 500 ayrımı
- Client API güvenliği

### S7.4 — K-Radar regression test'leri (4 saat)
- ProcessMaturity CRUD
- Stakeholder map CRUD
- A3 report flow
- EVM calculation

### S7.5 — Sektör benchmark verisi (4 saat)
- Statik veri sözlüğü (sektör başına ortalama olgunluk)
- Olgunluk skoru karşılaştırma UI

## Kabul Kriterleri
- [ ] Recommendation state DB'de
- [ ] Schedule multi-server safe
- [ ] K-Radar test coverage %50+
- [ ] Sektör benchmark UI canlı

**Tahmini efor:** ~14 saat

---

# SPRINT 8 — K-RAPOR + PROJE DERİNLEŞME 🟡
**1 Eylül → 12 Eylül 2026**

## Hedef
Raporlama gücü + proje yönetimi olgunlaşması.

## İşler

### S8.1 — PDF export altyapısı (3 saat)
- `weasyprint` entegrasyonu
- Template yapısı (`ui/templates/platform/k_rapor/pdf/`)

### S8.2 — k_rapor 5 ana rapor PDF (5 saat)
- Kurumsal özet
- Süreç PG ısı haritası
- Risk + paydaş
- Bireysel karne
- Stratejik analiz (SWOT/PESTEL özet)

### S8.3 — Proje Gantt performans (3 saat)
- 500+ task pagination
- Virtual scrolling
- N+1 azaltma

### S8.4 — Project plan year support (2 saat)
- Form'da plan year seçim
- Filtreleme

### S8.5 — RAID register UI completion (3 saat)
- Risk/Assumption/Issue/Decision tabular
- Severity matrix

### S8.6 — Scheduled raporlar (2 saat)
- APScheduler ile aylık/haftalık otomatik PDF
- E-mail gönderim (tenant_email_configs aktifse)

## Kabul Kriterleri
- [ ] 5 raporun PDF export'u çalışıyor
- [ ] Gantt 500 task render < 2 sn
- [ ] RAID register tam akış
- [ ] Scheduled rapor pilot

**Tahmini efor:** ~18 saat

---

# SPRINT 9 — LEGACY SUNSET FAZ 2 🔥
**15 Eylül → 26 Eylül 2026**

## Hedef
**En büyük borç:** `app/routes/process.py` (1.805 satır) ve `main/routes/`'i sunset etmek.

## İşler

### S9.1 — `app/routes/process.py` endpoint diff (3 saat)
- micro/surec'le karşılaştır → eksik fonksiyonlar var mı?
- Test: tüm legacy endpoint'lere 410 Gone döndür

### S9.2 — process.py'yi micro/surec'e merge (8 saat)
- KpiDataAudit logic'i taşı
- Permission check'leri birleştir
- Test: tüm e2e flow yeşil

### S9.3 — `main/routes/` sunset (4 saat)
- 4 dosya, 328 satır
- Kullanılan endpoint'leri micro modüllere taşı

### S9.4 — `app/routes/admin.py` sunset planı uygula (3 saat)
- micro/admin'e merge tamamlandı (Sprint 6'dan)
- Eski dosya silinir

### S9.5 — CI'da legacy import banı (1 saat)
- `tests/test_import_guards.py` genişlet
- `app/routes/process.py` import yasak

## Kabul Kriterleri
- [ ] `app/routes/process.py` silindi
- [ ] `main/routes/` boşaltıldı
- [ ] `app/routes/admin.py` silindi
- [ ] Toplam ~3.500 satır legacy kod silindi
- [ ] CI legacy import koruması aktif

**Tahmini efor:** ~19 saat

---

# SPRINT 10 (REZERV) — BUFFER + 2027 ROADMAP
**29 Eylül → 10 Ekim 2026**

## Hedef
- Sprint 1-9'dan kalan iş
- Test coverage'ı %50 hedefine yaklaştırma
- 2027 H1 planı

## Olası İşler
- i18n altyapısı başlangıcı (Türkçe-İngilizce)
- SSO entegrasyon (Google OAuth)
- 2FA (TOTP)
- Mobile-first CSS revize
- Anomali tespiti AI advisor v2

---

## 📊 KÜMÜLATİF METRİKLER (sprint sonu)

| Sprint | Çözülen risk skoru | Kod azalma | Test sayısı | Test kapsamı |
|:-:|:-:|:-:|:-:|:-:|
| 0 (yapıldı) | 8 | — | 18 | %25 |
| 1 | 20 | — | 22 | %28 |
| 2 | 31 | -207 (decorators) | 25 | %32 |
| 3 | 15 | — | 31 | %42 |
| 4 | — | -700 (dashboard, strategy) | 31 | %42 |
| 5 | 12 | — | 35 | %50 |
| 6 | 12 | — | 38 | %53 |
| 7 | 12 | — | 42 | %58 |
| 8 | 9 | — | 44 | %60 |
| 9 | 16 | -3.500 (process.py + main) | 46 | %62 |

**Sprint 9 sonu hedefler:**
- Test sayısı: 18 → **46** (+155%)
- Test kapsamı: ~%25 → **~%62**
- Legacy kod: 11.346 → ~**6.600 satır** (-4.700)
- Kritik risk (skor ≥16): 5 → **0**

---

## 🎯 BAŞARI KRİTERLERİ (6 ay sonu — Kasım 2026)

1. ✅ Tüm risk skoru ≥16 olan sorunlar kapatıldı
2. ✅ Legacy yüzey %42 küçüldü
3. ✅ Her core modül için en az smoke test var
4. ✅ Multi-tenant veri sızıntısı imkânsız (decorator + test)
5. ✅ PDF export 5 ana raporda
6. ✅ Audit log eksiksiz
7. ✅ Plan year tutarlılığı garanti
8. ✅ N+1 sorgular regression test'le yakalanıyor

---

## 🚀 SPRINT 1 BAŞLANGIÇ (önümüzdeki Pazartesi)

Hazır olduğunda söyle, Sprint 1.1 (plan_year_filter helper) ile başlıyorum.
