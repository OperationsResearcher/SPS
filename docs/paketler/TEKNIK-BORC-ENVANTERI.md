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

> **🔑 KRİTİK DÜZELTME (2026-06-16, DB-doğrulanmış):** İlk analiz "10 çakışan kavram, çift canlı yazma" dedi.
> Gerçek DB sorgusu bunu büyük ölçüde **çürüttü** — asıl tehlikeli senaryo (iki canlı tabloya çatallı yazma)
> neredeyse **hiç yok.** Veri katmanı zaten modern tek-kaynakta birleşmiş. Tablo varlık+satır kanıtı:
> - **Kimlik (Vizyon/Değer/Etik):** legacy `kurum`/`deger`/`etik_kural`/`kalite_politikasi` = **0 satır** (boş). Modern `tenants` dolu. → Dalga 1'de yazma route'ları silindi.
> - **Strateji:** legacy `ana_strateji`/`alt_strateji` = **0/0 satır** (boş). Modern `strategies`/`sub_strategies` = **90/229 satır** (canlı). → zaten modern tek-kaynak.
> - **Süreç/PG:** legacy `surec`/`surec_performans_gostergesi` **tabloları YOK**. Sadece modern `processes`(167)/`process_kpis`(731). `models/process.py` = `legacy_bridge` ile modern'e **saf alias** (Türkçe isim → aynı tablo).
>
> **Sonuç:** Kalan "Dalga 3/4" GERÇEK VERİ TAŞIMASI DEĞİL → **ölü legacy kod + isim/import temizliği.** Migration/yedek riski yok.
> (Not: ajan raporları burada birkaç kez yanlış çıktı — "strategies tablosu hiç yok" gibi; her iddia DB'de doğrulandı.)


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
  - **✅ YAPILDI (2026-06-16):** Teşhis sonucu beklenenden iyi çıktı — legacy yazma yolu **zaten ölüydü**
    (`/kurum-paneli` 301 redirect → legacy template hiç render edilmiyor → form/JS ulaşılamaz) ve legacy
    veri **tüm tenant'larda boştu** (taşınacak veri 0, DB'de teyit). Yani "veri taşıması" değil, saf kod temizliği oldu.
    `strategy_api.py`'deki **16 ölü legacy yazma route'u** kaldırıldı (ana/alt-strateji, vizyon/amaç, değer, etik, kalite).
    Route 911→895. `/strategy/*` (matrix/projects/kpi) route'larına dokunulmadı (kapsam dışı).
  - **Dalga 1.5 — kısmen yapıldı (2026-06-16):** 5 ölü backup template silindi (`templates/admin_panel*.html.backup*`,
    `admin_panel_backup_broken.html`, `admin_panel_v2.html`, `admin_v3.html`, `kurum_panel_backup.html`) — hiçbir route
    render etmiyor, extend/include edilmiyor (teyit). **`kurum_panel.py` (1300+ satır) bilinçli BIRAKILDI:** analiz
    gösterdi ki içinde 3 tip karışık — (A) redirect-ölü GET sayfaları, (B) **CANLI admin upload route'ları**
    (`/admin/upload-logo`, `upload-profile-photo`, `upload-users-excel`, `download-user-template` — `admin_panel.js`'den
    çağrılıyor, bazılarının modern karşılığı `micro/modules/admin`'de VAR ama legacy hâlâ çağrılıyor), (C) şüpheli proje
    alt-sayfaları. Bu dosyayı temizlemek = canlı upload'ları micro/admin'e taşıma + her route'u HTTP-seviyesinde test →
    **ayrı bir refactor işi** (Dalga 1.6). Statik analiz yetmez; kapsam disiplini için ertelendi.
    - **Dalga 1.6 — kısmen yapıldı (2026-06-16):** `kurum_panel.py`'den **4 ölü upload route silindi**
      (download-user-template, upload-users-excel, upload-profile-photo, upload-logo). Teyit: GET /admin-panel
      runtime'da 301 → app_bp.yonetim_paneli (middleware), tetikleyici admin_panel.html render-ölü; aktif ui'de referans yok;
      modern karşılıklar canlı (micro/admin). Route 895→891.
    - **Açık iş (Dalga 1.6 kalanı):** `admin_panel()` route'u + redirect-ölü GET'ler **bırakıldı** — `admin_panel`'e
      `url_for` bağımlılığı var (`templates/admin/activity_stream.html:60`, `kurum_panel.py` iç redirect'ler) → silmeden önce
      bu referanslar modern endpoint'e yönlendirilmeli. Ayrıca ölü `templates/kurum_panel.html`, `admin_panel.html`,
      `static/js/kurum_panel.js`/`admin_panel.js`.
- **Dalga 2 — Değerler/Etik/Kalite:** çok-satırlı modern modele yükselt (#6-8). → KOE "kimlik netliği" zenginleşir + onboarding/AI bunu ister.
- **Dalga 3 — Strateji/Alt-Strateji:** (#3-4) → modern. perspective/weight kararı burada. → **KOE boyut 1 tam.**
  - **✅ kısmen yapıldı (2026-06-16):** Teşhis: legacy `ana_strateji`/`alt_strateji`/`strategy_process_matrix` **boş**
    (0/0/0), modern `strategies`/`sub_strategies`/`process_sub_strategy_links` dolu (90/229/250). `micro/proje`'deki iki
    servis legacy okuyordu: (a) `portfolio_service` fallback'li (legacy boşsa modern'e düşer, davranış doğru) →
    **dokunulmadı**; (b) `strategy_detail_service` fallback'siz, legacy boş tablodan okuyordu → **stratejik skorlar hep 0
    (BUG, canlı test ile doğrulandı)**. → modern `Strategy`+`ProcessSubStrategyLink` desenine taşındı (portfolio'nun modern
    fonksiyonuyla aynı). Çıktı sözleşmesi korundu (template uyumu). Tomofil'de 97 link → artık gerçek skor.
  - **Açık iş:** `portfolio_service` ölü legacy fallback'ini sadeleştir (davranış değişmez); `kurum_panel.py` BSC
    okumaları (redirect-ölü route'larda, o dosya url_for bağımlılığıyla bekliyor); `bsc/routes.py` perspective (BSC canlı mı?).
- **Dalga 4 — Süreç/PG ORM tekilleştirme:** (#9-10) legacy route emekliye. → **KOE boyut 2 açılır.**
  - **✅ kısmen yapıldı (2026-06-16):** `models/process.py` (379 satır, `Surec`/`SurecPerformansGostergesi`/
    `SurecFaaliyet` + bireysel, `__tablename__='surec'` vb.) **silindi** — saf dead code. Teyit: hiçbir yerden import
    edilmiyor (`models/__init__.py` legacy isimleri `app.models.process`'ten alias'lıyor, kendi `.process`'ini değil);
    "geçici taşı + app kalk + geri getir" testiyle silmenin app'i etkilemediği kanıtlandı (891 route sabit). Silinen
    sınıflar SQLAlchemy registry'ye hiç girmiyordu (o yüzden `surec` tablosu DB'de yok). `legacy_bridge` modern'e işaret
    ediyor (`Surec.__tablename__='processes'`), sağlam.
  - **Açık iş (kozmetik, düşük öncelik):** Türkçe alias kullanımları (`SurecPerformansGostergesi` → `ProcessKpi`) modern
    isimlere çevrilebilir — ama `legacy_bridge` zaten doğru çalışıyor (modern tabloya yazıyor); mekanik, çok-dosya, düşük değer.
- **Sürekli (her dalgada fırsatçı):** o dalganın dokunduğu god-file'ı böl, hard-delete'i soft yap, except:pass düzelt, alert→SweetAlert2. "Dokunduğun yeri temizle" — ayrı temizlik turu değil.

**Bilinçli ertelenenler:** User (#1-2 — auth riski yüksek, en sona), legacy-only BSC modelleri (StrategyMapLink/Matrix — BSC kararıyla birlikte), webhook/i18n iskeletleri.

---

## Açık kararlar (envanterden çıkan, netleşmeli)

1. `ana_strateji.perspective/weight/bsc_code` modern Strategy'ye eklensin mi? (BSC gelecek planında → muhtemelen evet)
2. God-file'lar: fırsatçı mı bölünsün (dokununca) yoksa ayrı refactor turu mu?
3. Legacy route emekliye alma yöntemi: 410/redirect geçiş dönemi mi, doğrudan kaldırma mı?
4. Taşıma mekaniği: tek-seferlik script mi, Alembic migration mı (squash baseline `f5215370eebd` üstüne)?
5. Hard-delete→soft-delete: toplu mu (tek tur), yoksa dalga-dalga (taşımayla) mı?
