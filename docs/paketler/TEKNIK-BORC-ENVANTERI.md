# Teknik Borç Envanteri — Sistematik Tarama

> **Tarih:** 2026-06-16
> **Amaç:** Paketleme (L1) + canlı kurum + birikmiş borç üçlüsünü körlemesine değil, haritalı ilerletmek.
> **Strateji:** Strangler (kademeli kuşatma) — legacy çalışır kalır, kavram kavram modern tek-kaynağa taşınır.
> **Yöntem:** 4 eksende paralel sistematik tarama (çift-model / performans / ölü-riskli kod / güvenlik).
> **İlgili:** [`CIFT-MODEL-BORCU-KURUMSAL-KIMLIK.md`](../CIFT-MODEL-BORCU-KURUMSAL-KIMLIK.md) · [`LEGACY_ROUTE_INVENTORY.md`](../LEGACY_ROUTE_INVENTORY.md) · KURALLAR-MASTER §7

---

## 0. Yönetici özeti — bir bakışta

| Eksen | Bulgu | En kritik |
|-------|-------|-----------|
| **A. Çift-model** | 10 çakışan kavram, hiçbiri senkron değil | Strateji/Alt-Strateji, Vizyon, Değerler/Etik (çift-yazma → tutarsız veri) |
| **B. Performans** | N+1, eksik index, döngüde query | Karne/rapor eager-load yok; `(tenant_id,is_active)` index yok |
| **C. Ölü/riskli** | 33+ hard delete, god-files, except:pass | Hard delete (soft-delete kuralı ihlali); `app/routes/process.py` 1806 satır ölü |
| **D. Güvenlik** | HGS bypass, SMTP düz-metin, 11 alert() | Encryption fallback key; HGS bypass; tenant izolasyon **iyi durumda ✅** |

**İyi haber (tarama doğruladı):** Tenant izolasyonu büyük ölçüde **sağlam** — micro modüllerde `tenant_id` filtreleri tutarlı, `_tenant_guard()` / `accessible_processes_filter()` var. Yani en korkulan şey (cross-tenant sızıntı) sistemik değil. Borç **tutarlılık + verimlilik + temizlik** ekseninde, **güvenlik felaketi** ekseninde değil.

---

## A. Çift-model çakışmaları (10 kavram)

Detay: [`CIFT-MODEL-BORCU-KURUMSAL-KIMLIK.md`](../CIFT-MODEL-BORCU-KURUMSAL-KIMLIK.md). Tarama bunu 7 kavramdan **10'a** genişletti:

| # | Kavram | Legacy | Modern | Risk | Taşıma zorluğu |
|---|--------|--------|--------|------|----------------|
| 1 | Tenant/Kurum | `kurum` | `tenants` | 🔴 | Yüksek |
| 2 | User | `user`/LegacyUser | `users`/User | 🔴 | Yüksek |
| 3 | Ana Strateji | `ana_strateji` (+perspective,weight,bsc_code) | `strategies` | 🔴 | **Çok yüksek** (modern'de eksik alanlar) |
| 4 | Alt Strateji | `alt_strateji` | `sub_strategies` | 🔴 | Çok yüksek |
| 5 | Vizyon/Amaç | `kurum.vizyon/amac` | `tenants.vision/purpose` | 🔴 | Orta |
| 6 | Değerler | `deger` (çok-satır) | `tenants.core_values` (TEXT) | 🟠 | Çok yüksek (yapı dönüşümü) |
| 7 | Etik | `etik_kural` (çok-satır) | `tenants.code_of_ethics` (TEXT) | 🟠 | Çok yüksek |
| 8 | Kalite | `kalite_politikasi` (çok-satır) | `tenants.quality_policy` (TEXT) | 🟡 | Çok yüksek |
| 9 | Süreç | `surec` (alias) | `processes` | 🟡 | Orta (alias ile kısmi senkron) |
| 10 | Süreç PG | `surec_performans_gostergesi` (alias) | `process_kpis` | 🟡 | Orta |

**Karar (sabit):** Değerler/Etik/Kalite → **çok-satırlı yapı kazanır** (modern'i çok-satırlıya yükselt). Diğerlerinde **modern kazanır**.
**Açık karar:** `ana_strateji.perspective/weight/bsc_code` modern `Strategy`'ye eklenecek mi, bilinçli düşülecek mi? (BSC ileride lazım → büyük ihtimal eklenmeli.)

**Legacy-only (karşılığı yok, ayrı karar):** `StrategyProcessMatrix`, `StrategyMapLink` (BSC harita), `DashboardLayout`, `UserActivityLog`, `Feedback`, `Note`.

---

## B. Performans / verimsizlik

**En yüksek etkili 5 (ROI sırası):**

| # | Yer | Sorun | Düzeltme |
|---|-----|-------|----------|
| 1 | `app/models/process.py:61` (ve sorgular) | `(tenant_id, is_active)` composite index yok → rapor sayfaları full-scan | DDL: `CREATE INDEX ix_process_tenant_active ON processes(tenant_id, is_active)` (+ `process_kpis(process_id,is_active)`, `kpi_data(year)`) |
| 2 | `micro/modules/surec/routes_karne.py:442` | `p.leaders + p.members + p.owners` döngüde → N+1 (3 sorgu/process) | `selectinload(Process.leaders/members/owners)` |
| 3 | `micro/modules/raporlar/routes_faz0.py:586-617` | Departman başına 4 ayrı sorgu (döngüde subquery+scalar) | tek `GROUP BY` sorgusu |
| 4 | `micro/modules/analiz/routes.py:42` · `recommendation_service.py:48` | KPI başına servis çağrısı (nested N+1) | bulk API |
| 5 | `routes_faz0.py:213` (K-Vektör skor) | her rapor açılışında yeniden hesap | cache (Redis varsa) |

**Model lazy:** `app/models/process.py:103-105` leaders/members/owners `lazy='select'` — kritik route'larda explicit eager-load şart. `ProcessKpi.process` (`:188`) raporlarda eager gerekli.

---

## C. Ölü / riskli kod

> **Hard-delete derin inceleme (2026-06-16) — ajan abartısı düzeltildi:** İlk tarama "33 hard delete, canlıda
> kullanıcı bugün veri kaybediyor 🔴" dedi. Kodda teyit: **bugün gerçekten kullanılan modern yollar (`micro/`)
> zaten soft-delete yapıyor** — kanıt: [`routes_kpi_data.py:463`](../../micro/modules/surec/routes_kpi_data.py#L463)
> PGV silme örnek bir soft-delete (`is_active=False` + `deleted_at` + `deleted_by_id` + `KpiDataAudit` + tenant izolasyon).
> Hard-delete'ler **legacy yüzeyde** (`/api`, `/main`, `/v3`); örneklenenler (`/api/pg-veri/sil`, `/api/gorev/sil`)
> **frontend'in HİÇBİR yerinden çağrılmıyor** (JS/HTML/Py grep = 0). Yani:
> - **Günlük kullanımda veri kaybı: YOK** (kullanıcı modern UI → soft-delete).
> - **Gerçek risk:** ölü legacy hard-delete endpoint'leri hâlâ *erişilebilir* (kayıtlı) — açık arka kapı, günlük kayıp değil.
> - **Karar:** tek tek soft'a çevirme YOK (birazdan emekliye alınacak koda emek). Çift-model dalgalarında legacy
>   route emekliye alınınca hard-delete de ölür. Tehdit acilse → o route'u 410/devre-dışı yap (ucuz), ama dalga zaten çözecek.


| Kategori | Bulgu | Aksiyon |
|----------|-------|---------|
| **Hard delete (KURALLAR §3 ihlali)** | 33+ yer: `api/routes.py` (Task/ProjectRisk/PGV…), `strategy_api.py:93,197,298,374,450`, `pages.py:744,1444`, `v3/routes.py:507`, `notification_service.py:259` | **çift-model dalgalarına bağlandı (2026-06-16) — ayrı tur yok** |
| **except:pass (sessiz hata)** | `auth/routes.py:337`, `api/routes.py:2741`, `scheduled_reports/routes.py:76,79`, `pages.py:1414` (skor recalc) | çoğu legacy/best-effort; **tek gerçek-zararlı:** `pages.py:1414` log'suz → `logger.warning` (modern karşılık zaten yapıyor) |
| **"Başarılı yalanı" / yarım iş (sessiz)** | `auth/routes.py:374` (bildirim ayarı kaydetmiyor, success döner), `app/api/routes.py:410` (webhook placeholder), `app/api/auth.py:102` (api-key doğrulamıyor) | **HEPSİ ölü legacy** — frontend çağırmıyor; modern karşılıklar doğru kaydediyor (`shared/auth`, `scheduled_reports`). Legacy emekliye alınca gider. |
| **Ölü kod** | `app/routes/process.py` (1806 satır, `LEGACY_PROCESS_BP_ENABLED` flag) — micro/surec canonical | flag default=False teyit → kaldır |
| **God-files (>1200 satır)** | `api/routes.py` (4690!), `k_rapor/routes.py` (2534), `projects.py` (2399), `kurum_panel.py` (1951), `pages.py` (1838), `strategy_api.py` (1266) | submodule'lere böl (taşıma sırasında) |
| **DRY ihlali** | tenant filtresi 100+ yer (`app/utils/tenant_scope.py` var ama tutarsız kullanılıyor); yetki kontrolü 50+ yer; db-commit-rollback boilerplate 80+ | `@tenant_scoped` / `@handle_db_error` decorator'ları |
| **Yarım iş / kritik TODO** | `app/utils/encryption.py:24` (geçici fallback key!), webhook DB logging, `migrations/_archive_versions/*:206` NotImplementedError | encryption key → D'ye taşındı |

---

## D. Güvenlik / disiplin

| Risk | Yer | Seviye | Aksiyon |
|------|-----|--------|---------|
| Encryption fallback key (geçici, koda gömülü) | `app/utils/encryption.py:24` | 🔴 | `ENCRYPTION_KEY` env zorunlu yap, fallback'i kaldır |
| HGS login bypass (`@login_required` yok) | `micro/modules/hgs/routes.py:59-66` | 🔴 (S2) | Production'da `HGS_BYPASS_ENABLED=False` teyit; localhost kontrolü spoof'a açık |
| SMTP password fallback düz-metin | `email_digest_service.py:195` · `config.py:169` | 🟠 | tenant config Fernet'li ✅ ama app-default düz; tutarlı şifrele |
| 11× `alert()` (SweetAlert2 olmalı) | `project_form_transfer.js:22`, `veri_kalitesi.js:98`, `sp_analiz.js:71`, `twofa.js:70`, `sp/*.html` inline | 🟡 | SweetAlert2'ye çevir |
| **Tenant izolasyon** | micro modüller | ✅ **TEMİZ** | `_tenant_guard()`, `accessible_processes_filter()` tutarlı — sistemik sızıntı yok |
| CSRF / GET-state-change / hardcoded-URL | — | ✅ | CSRF açık, GET ile mutasyon yok, JS `data-*`/`url_for` kullanıyor |

---

## Sentez: strangler sırası (borç temizliği = L1 inşası)

> Kritik içgörü: çift-model temizliğinin Faz 1-4'ü, **tam da KOE'nin boyutlarını besleyen kavramlar.** Borcu temizlerken L1 altyapısını kuruyoruz — ayrı iş değil, aynı iş.

**Önerilen dalga sırası** (her biri kendi dalında, yerelde doğrula → Test → Yayın; DB değişimi öncesi yedek):

- **Dalga 0 — Bedava kazanımlar (riski düşük, izole):** index DDL'leri (B1), kritik eager-load (B2), `tenant.mission` bug fix, encryption key (D), HGS bypass teyidi (D). Veri taşıması yok, anında değer.
- **Dalga 1 — Kimlik tek-kaynak:** Vizyon/Amaç (#5) → modern. `/kurum/update-amac-vizyon` legacy yazma kapat. → **KOE boyut 1 açılır.**
- **Dalga 2 — Değerler/Etik/Kalite:** çok-satırlı modern modele yükselt (#6-8). → KOE "kimlik netliği" zenginleşir + onboarding/AI bunu ister.
- **Dalga 3 — Strateji/Alt-Strateji:** (#3-4) → modern. perspective/weight kararı burada. → **KOE boyut 1 tam.**
- **Dalga 4 — Süreç/PG ORM tekilleştirme:** (#9-10) legacy route emekliye. → **KOE boyut 2 açılır.**
- **Sürekli (her dalgada fırsatçı):** o dalganın dokunduğu god-file'ı böl, hard-delete'i soft yap, except:pass düzelt, alert→SweetAlert2. "Dokunduğun yeri temizle" — ayrı temizlik turu değil.

**Bilinçli ertelenenler:** User (#1-2 — auth riski yüksek, en sona), legacy-only BSC modelleri (StrategyMapLink/Matrix — BSC kararıyla birlikte), webhook/i18n iskeletleri.

---

## Açık kararlar (envanterden çıkan, netleşmeli)

1. `ana_strateji.perspective/weight/bsc_code` modern Strategy'ye eklensin mi? (BSC gelecek planında → muhtemelen evet)
2. God-file'lar: fırsatçı mı bölünsün (dokununca) yoksa ayrı refactor turu mu?
3. Legacy route emekliye alma yöntemi: 410/redirect geçiş dönemi mi, doğrudan kaldırma mı?
4. Taşıma mekaniği: tek-seferlik script mi, Alembic migration mı (squash baseline `f5215370eebd` üstüne)?
5. Hard-delete→soft-delete: toplu mu (tek tur), yoksa dalga-dalga (taşımayla) mı?
