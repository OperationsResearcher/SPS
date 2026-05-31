# TASKLOG — Son 10 Task

## TASK-142 | 2026-05-30 / 2026-05-31 | ✅ Tamamlandı (yerel) — Büyük UX yenileme oturumu

**Görev:** 4 sprint + K-Radar birleşmesi + breadcrumb sistemi + Initiative ↔ Proje stratejik bağı + Hiyerarşi Rehberi + 38+ rapor sayfası standardizasyonu
**Modül:** platform geneli (sp, k_radar, raporlar, proje, ayarlar, base, app/__init__)
**Durum:** ✅ Tamamlandı

### Kısa Özet (detay için `docs/TASKLOG.md`)
- **Sprint 1-4:** 16 yeni UX özelliği (Ctrl+K palet, favoriler, benim görevlerim, toplu işlem, KV bubble, PG sparkline, strateji-proje matris, süreç radar, PG-proje çapraz etki, zamanlanmış raporlar)
- **K-Radar Birleşmesi:** `/k-rapor` + `/raporlar` + `/k-analiz` → tek `/k-radar` hub (65 kart, 5 grup, eski URL'ler redirect)
- **Breadcrumb Sistemi:** Otomatik 3-4 katmanlı navigasyon (`current_section` + `current_subgroup` context processor); 38 sayfadan "Raporlara Dön" temizlendi
- **Initiative ↔ Proje:** UI'da "Initiative" → "**Stratejik Girişim**" (12 dosya); `Project.initiative_id` FK + UI dropdown + detay rozet + altında projeler widget
- **Hiyerarşi Rehberi:** 6 katmanlı (Vizyon→Ana Strateji→Alt→Girişim→Proje→Görev) paylaşılabilir popup, 3 sayfada erişilebilir
- **Sayfa Standardizasyonu:** 30+ sayfa `mc-page-header` + 1240px + breadcrumb pattern'ine geçirildi
- **Bug Fix:** Süreç karne sonsuz reset, /sp/digest/weekly.pdf, Tomofil 30s sorgu 0.05s'ye, K-Rapor sürec tekrarı, /raporlar/op-istatistik 404, sidebar ikonu, /raporlar/roi-strategy tamamen kaldırıldı, EVM/CMMI/Muda/Sankey detaylı Türkçeleştirildi

### Veritabanı
- `project` tablosuna `initiative_id INTEGER REFERENCES initiatives(id) ON DELETE SET NULL` + index eklendi
- `requirements.txt`'ye `reportlab>=4.0`

### Notlar
- Test/Yayın deploy bekliyor — kullanıcı "deploy edelim" dediğinde tek tarball + DB migration ile gönderilecek.
- Tüm sayfalar smoke geçti.

---

## TASK-121 | 2026-05-24 | ✅ Tamamlandı (sadece yerel)

**Görev:** Otonom iş mantığı testinin (`tests/otonom_is_mantigi_testi.py`) veritabanı kısıt hatası nedeniyle düzeltilmesi
**Modül:** tests/
**Durum:** ✅ Tamamlandı

### Değiştirilen / Eklenen Dosyalar
- `tests/otonom_is_mantigi_testi.py` → `populate_base_data` aşamasında oluşturulan test kurumu için eksik olan `tenant_id=1` ataması eklendi.

### Yapılan İşlem
Yeni projede "tenant isolation" ve "NOT NULL tenant_id" veri kısıtlamaları getirildiğinden dolayı eski test veritabanında SQLite üzerinde hata fırlatan `IntegrityError` (NOT NULL constraint failed: kurum.tenant_id) sorunu giderilmiştir. Yapılan düzeltme sonrası tüm otonom iş mantığı testleri (`unittest`) başarıyla `OK` statüsünde tamamlanmıştır.

### Notlar
Test çıktılarında Windows terminal CP1254 encoding uyumsuzluğu nedeniyle emoji (`✓`) karakterlerinden kaynaklanan hata, `PYTHONIOENCODING=utf-8` parametresiyle çözümlenmektedir.

---

## TASK-120 | 2026-05-24 | ✅ Tamamlandı (sadece yerel)

**Görev:** EFQM Olgunluk Modülü için arayüze görsel sonuç kartı ve detay modalı entegre edilmesi
**Modül:** ui/templates/platform/k_radar/, ui/static/platform/js/
**Durum:** ✅ Tamamlandı

### Değiştirilen / Eklenen Dosyalar
- `ui/templates/platform/k_radar/ks.html` → EFQM card, data-api-efqm niteliği ve EFQM sonuç modalı eklendi.
- `ui/static/platform/js/k_radar_ks.js` → `API.efqm` adresi eşleştirildi, açılışta verileri fetch eden boot kodları eklendi ve `loadModal` switch-case yapısına `"efqm"` eklendi.

### Yapılan İşlem
Mevcut backend modelleri (`ProcessMaturity`), API rotaları (`/k-radar/api/ks/efqm`) ve hesaplama motoru tam hazır olan EFQM Olgunluk modülü için KS-Radar sayfasına görsel sonuç kartı eklendi. Kart tıklandığında açılan ve başarı aralıkları/puan bantlarını (KPI 327) listeleyen şık bir modal entegre edildi.

### Notlar
Herhangi bir şema veya backend değişikliği gerektirmeden, mevcut altyapı arayüze tam entegre edilmiştir.

---

## TASK-119 | 2026-05-24 | ✅ Tamamlandı (sadece yerel)

**Görev:** Stratejik Planlama (/sp/) sayfalarındaki 500 hatalarının (TypeError: _check_sp_role() takes 0 positional arguments but 1 was given) düzeltilmesi
**Modül:** micro/modules/sp/
**Durum:** ✅ Tamamlandı

### Değiştirilen / Eklenen Dosyalar
- `micro/modules/sp/helpers.py` → `_check_sp_role` fonksiyonu parametresiz çağrılara ve `current_user` ile yapılan parametreli çağrılara uyumlu hale getirildi (`def _check_sp_role(user=None):` yapıldı).

### Yapılan İşlem
Stratejik planlama rotalarındaki (örn. `/sp/ceyreklik-review`, `/sp/donemler` vb.) yetki denetimi sırasında fırlatılan `TypeError: _check_sp_role() takes 0 positional arguments but 1 was given` hatası, yardımcı fonksiyona `user` parametresi isteğe bağlı olarak eklenerek çözüldü. Flask dev server reloads başarılı.

### Notlar
Geriye dönük tüm `_check_sp_role` çağrıları ve parametreli kullanımlar sorunsuz çalışmaktadır.

---

## TASK-118 | 2026-05-24 | ✅ Tamamlandı (sadece yerel)

**Görev:** Rekabet analizi sonrası 5 önerinin uygulanması — UX entegrasyon + AI Pivot + Exec Dashboard + TR Kamu şablonu + Initiative haritası
**Modül:** ui/templates/platform/, app/services/, app/templates_data/, micro/modules/sp/
**Durum:** ✅ Tamamlandı

### Değiştirilen / Eklenen Dosyalar
- `ui/templates/platform/base.html` → SP altına 5 sub-link (exec dashboard, çeyreklik, initiative, scenario, replan, templates) — Hamle #1
- `micro/modules/sp/helpers.py` → strateji haritası grafına Initiative node'ları (pembe, kesik kenar, dashed edge) — Hamle #3
- `ui/templates/platform/sp/strateji_haritasi.html` → vis-network `initiative` group theme — Hamle #3
- `app/services/exec_dashboard_service.py` → yeni; KPI/strateji/initiative/risk/anomali/trigger snapshot + health_score — Hamle #5
- `app/services/ai_pivot_advisor_service.py` → yeni; Gemini LLM + heuristic fallback ile pivot önerileri — Hamle #2
- `app/services/plan_year_template_service.py` → yeni; JSON şablon marketplace iskeleti — Hamle #4
- `app/templates_data/sbb_kamu_template.json` → yeni; Cumhurbaşkanlığı SBB 2024-2028 uyumlu 5 stratejik amaç + 13 alt strateji + 8 KPI — Hamle #4
- `micro/modules/sp/routes_exec_advisor.py` → yeni; 7 endpoint (exec-dashboard, exec-snapshot, ai-pivot, templates list/get/apply)
- `ui/templates/platform/sp/exec_dashboard.html` → yeni; sağlık skoru hero + 6 metrik kartı + AI Pivot paneli
- `ui/templates/platform/sp/templates.html` → yeni; şablon marketplace UI
- `micro/modules/sp/routes.py` → yeni route modülünü import

### Yapılan İşlem
Önceki rekabet analizi raporundaki 5 öncelikli hamlenin tamamı uygulandı: (1) sidebar entegrasyonu — S54-S57 yatırımı artık menüden erişilebilir; (2) AI Strategy Pivot Advisor — exec snapshot + son 7 gün trigger event'leri Gemini'ye gönderiliyor, key yoksa heuristic kural motoru fallback'i; (3) strateji haritasına initiative node'ları (vis-network group `initiative`, kesik çizgili kenar); (4) Cumhurbaşkanlığı SBB Stratejik Plan Hazırlama Kılavuzu uyumlu kamu şablonu + apply servisi — global rakiplerde olmayan TR-spesifik diferansiyatör; (5) Exec Dashboard tek bakışta 360° strateji sağlığı (health_score ağırlıklı: KPI on-target %40 + coverage %20 + faaliyet timeliness %20 + risk %10 + anomali %10). Tomofil tenant'ında smoke: health 45.7, 221 KPI.

### Notlar
SBB şablonu MVP — sektör genişletme için private/ngo şablonları sonraki sprintte. AI Pivot'ın LLM modu için GEMINI_API_KEY/.env şart; yoksa heuristic mod ile silent fallback. Schema migration yok (mevcut tablolar yeterli).

---

## TASK-117 | 2026-05-24 | ✅ Tamamlandı (sadece yerel)

**Görev:** Stratejik planlama geliştirme planı S53-S57 — 5 sprint somut çıktı (Ö1-Ö5, Ö8)
**Modül:** app/services/, app/models/, micro/modules/sp/, ui/templates/platform/sp/, migrations/
**Durum:** ✅ Tamamlandı

### Değiştirilen / Eklenen Dosyalar
- `app/utils/plan_year_filter.py` → `filter_by_plan_year_scoped()` helper (S53/Ö2)
- `micro/modules/k_rapor/routes.py` → helper kullanımı + syntax fix (S53)
- `micro/modules/proje/routes_project_crud.py` → plan_year_id form alanı (S53/Ö3)
- `app/services/quarterly_review_service.py` → yeni; çeyreklik review aggregator (S54/Ö1)
- `micro/modules/sp/routes_donemler.py` → `/sp/ceyreklik-review` + JSON API (S54/Ö1)
- `ui/templates/platform/sp/ceyreklik_review.html` → yeni dashboard (S54/Ö1)
- `app/models/initiative.py` + migration `a4b5c6d7e008` → Initiative + Milestone (S55/Ö4)
- `micro/modules/sp/routes_initiative.py` + `initiatives.html` → CRUD UI (S55/Ö4)
- `app/models/plan_year.py` + migration `b5c6d7e8f009` → scenario_of_id + scenario_label (S56/Ö5)
- `app/services/plan_year_service.py` → `clone_full_plan_year(as_scenario_label=...)` (S56)
- `micro/modules/sp/routes_scenario.py` + `scenarios.html` → senaryo dalları UI (S56/Ö5)
- `app/models/replan_trigger.py` + migration `c6d7e8f9g010` → ReplanTrigger + Event (S57/Ö8)
- `app/services/replan_trigger_service.py` → değerlendirme motoru (S57/Ö8)
- `micro/modules/sp/routes_replan_trigger.py` + `replan_triggers.html` → trigger UI (S57/Ö8)

### Yapılan İşlem
docs/SP-DONEM-ANALIZ-2026.md'deki 12 öneriden 5 tanesi (Ö1, Ö2, Ö3, Ö4, Ö5, Ö8) somut olarak uygulandı: Çeyreklik review wizard, plan_year NULL legacy uyum helper'ı, Project planYear form alanı, Multi-Year Initiative tabloları/CRUD, PlanYear senaryo dallanma (partial unique index), trigger-based otomatik replan motoru. 3 yeni Alembic migration uygulandı (a4-c6 zinciri f6g7h8i9j013 üzerine).

### Notlar
VM deploy ertelendi (kullanıcı önceki direktif). Trigger eval cron entegrasyonu (APScheduler) sonraki sprintte yapılabilir — şu an manuel "Şimdi Değerlendir" butonu var. Senaryo karşılaştırma UI'sı henüz yok; mevcut donem-karsilastir endpoint'i scenario_of_id'yi de göstermek için genişletilebilir.

---

## TASK-116 | 2026-05-23 | ✅ Tamamlandı (sadece yerel)

**Görev:** 9 Sprint paralel uygulaması — audit + roadmap + 6 sprint somut çıktı
**Modül:** app/utils/, tests/, docs/, migrations/
**Durum:** ✅ Tamamlandı (Sprint 9 büyük temizlik kullanıcı onayı bekliyor)

### Oluşturulan / Değiştirilen Dosyalar
- `docs/PROJE-AUDIT-2026Q2.md` → 15 modül + altyapı audit (3 paralel agent)
- `docs/RISK-MATRISI-2026Q2.md` → 32 risk, olasılık×etki matrisi
- `docs/ROADMAP-2026H2.md` → 9 sprint × 2 hafta detaylı plan
- `docs/LEGACY_SUNSET_MAP.md` → ~3.940 satır silme planı (Sprint 9)
- `docs/SPRINT-RAPORU-2026Q2.md` → bu oturumun sonuç raporu
- `app/utils/plan_year_filter.py` (+test, 4 senaryo) — Sprint 1
- `app/utils/tenant_scope.py` (+test, 7 senaryo) — Sprint 2
- `app/utils/upload_security.py` (+test, 22 senaryo) — Sprint 2
- `app/utils/query_counter.py` (+test, 6 senaryo) — Sprint 3
- `app/utils/pdf_export.py` (+test, 7 senaryo) — Sprint 8
- `tests/test_module_smoke.py` (17 senaryo) — Sprint 3
- `tests/test_karne_hesaplamalar.py` (27 senaryo) — Sprint 5
- `micro/modules/admin/routes.py` — logo upload security
- `micro/modules/sp/routes_flow.py` — graph performans limit
- `migrations/versions/b2c3d4e5f009_okr_tables.py` — OKR tabloları

### Yapılan İşlem
3 paralel sub-agent ile 15 modül + altyapı detaylı audit'i çıkarıldı, 32 risk sınıflandırıldı, 9 sprint × 2 hafta roadmap yayınlandı. Sonra paralel uygulama: Sprint 1-8 somut çıktılarla tamamlandı. **90 yeni test**, **5 yeni utility**, **2 migration** uygulandı. Sprint 9 (~3.940 satır legacy sunset) planlandı, yürütme kullanıcı onayıyla. 4 audit yanılgısı manuel doğrulamayla düzeltildi.

### Notlar
- Risk skoru ≥16 olan kritik açık: 5 → 2 (Sprint 9 ile 0 olacak)
- Test sayısı: ~80 → ~160 (+100%)
- Yeni production kod: ~1.500 satır (utility + decorator + helper'lar)
- Tomofil tenant_id=26 hala canlı (48.283 KpiData)
- VM'e push yapılmadı

---

## TASK-115 | 2026-05-23 | ✅ Tamamlandı (sadece yerel)

**Görev:** Tomofil demo tenant v2 — 6 yıllık (2021-2026) evrim + EV pivot hikayesi + generic seed script
**Modül:** scripts/, docs/sablon.md, docs/tomofil-demo/
**Durum:** ✅ Yerelde tamamlandı — VM yayını yapılmadı

### Oluşturulan / Değiştirilen Dosyalar
- `docs/sablon.md` → yeni — boş şablon, 21 bölümlü demo-tenant onboarding rehberi
- `docs/tomofil-demo/sablon-dolu.md` → yeni — doldurulmuş örnek (insanlar için doküman)
- `docs/tomofil-demo/tenant_data.yaml` → yeni — script için 2026 baseline yapılandırılmış veri
- `docs/tomofil-demo/year_deltas.yaml` → yeni — 2021-2025 yıllara göre strateji/süreç/KPI evrim delta'ları
- `scripts/seed_generic_tenant.py` → yeni — YAML-driven generic tenant seeder (--data --deltas --dry-run/--commit/--reset)

### Yapılan İşlem
Tomofil yerel PG (`kokpitim_db`) içine `tenant_id=26` ile yeniden açıldı: yerli EV parça üreticisi profili, 2021 kuruluş, 100 çalışan (97 user — admin + 20 manuel yönetici + 76 bulk), 7 plan yılı, 6 yıllık strateji evrimi (3 → 7 ana strateji, ~16 değişim eventi), 28 Strategy + 135 SubStrategy + 46 Process + 221 ProcessKpi (yıllara göre ayrı kayıt, source_*_id zinciri ile), 679 KpiData (2026 aylık + 2024-25 çeyreklik + 2021-23 yıllık), 4 proje + 13 görev, 6×4 = 24 SWOT/TOWS/PESTEL/Porter analizi, K-Vektor ağırlıkları (18), K-Radar tüm modüller (71 kayıt). OKR tabloları DB'de migrate edilmediği için skip edildi.

### Notlar
- Login: `admin@tomofil.test` / `Tomofil2026!`
- Hikaye: 2021 kuruluş → 2022 chip krizi → 2023 ihracat (H4) → 2024 EV pivot (H5) → 2025 sürdürülebilirlik (H6) → 2026 dijital dönüşüm (H7)
- `1.A.2` (İçten Yanmalı Motor Krank Mili) 2024'te is_active=False olarak pasifestirildi (kayıtta var, görünmüyor)
- Toplu kullanıcı sayısı 80 hedeflendi, departman dağılımları toplamı 76 — istenirse 4'lük ince ayar yapılabilir
- Project tablosunda ORM ↔ DB şema sapması var (is_active, deleted_at fazla); script raw SQL'e düşüyor
- Task tablosu da benzer şekilde raw SQL ile yazıldı (due_date alanı, end_date değil)
- OKR migration eksiği ayrı bir task: kokpitim'in OKR modülünü gerçekten kullanıyorsa alembic'e migration eklenmeli
- VM yayını kullanıcı yerel doğrulama yapana kadar bekliyor

---

## TASK-114 | 2026-05-22 | ✅ Tamamlandı (sadece yerel)

**Görev:** Tomofil Group N.V. örnek/test tenantı — Phase 1 seed (yereldeki PostgreSQL'e)
**Modül:** scripts/, docs/tomofil/
**Durum:** ✅ Yerelde tamamlandı — VM'e yayın **YAPILMADI** (kullanıcı yerel test ediyor)

### Oluşturulan / Değiştirilen Dosyalar
- `scripts/seed_tomofil_full.py` → yeni — idempotent seeder (`--dry-run` / `--commit` / `--reset`)
- `docs/tomofil/` → kaynak dosyalar (strateji ağacı md + 3.800 çalışan JSON + atomik veri JSON + 2 PDF)

### Yapılan İşlem
Yerel PostgreSQL (`kokpitim_db`) içine `tenant_id=21` ile yeni tenant açıldı: 3.801 kullanıcı (admin dahil), 10 plan yılı (2026 active, 2027-2035 draft), 14 süreç (A2R, C2L, P2M…), 6 ana + 73 alt strateji (H1-H6 → 1.A → 1.A.1 prefix hiyerarşi), 120 ProcessKpi, 14 süreç sahibi. Strateji ağacı md'den regex ile parse edildi, kullanıcılar Workday HCM formatındaki JSON'dan bulk insert ile yüklendi.

### Notlar
- Login: `admin@tomofil.test` / `Tomofil2026!` (role=tenant_admin)
- O2C sürecinde çalışan JSON'da yönetici kademesi olmadığı için fallback olarak admin user owner atandı.
- Phase 2 (kaynak `Tomofil_Veriler_v3.json` → 25.300 atomik kayıt → `kpi_data` agregasyonu ve PDF kopyalama) ayrı bir script ile yerel test sonrası yapılacak.
- VM (Oracle Cloud) yayını kullanıcı yerel doğrulama yapana kadar bekliyor.

---

## TASK-113 | 2026-05-21 | ✅ Tamamlandı

**Görev:** Terim standardı — «VM» = Oracle Cloud üretim; dokümantasyon ve deploy betikleri güncellemesi
**Modül:** docs, scripts/ops/oracle, scripts/vm_safe_deploy.sh, scripts/vm_smoke_check.ps1, CLAUDE.md, Agents
**Durum:** ✅ Tamamlandı

### Oluşturulan / Değiştirilen Dosyalar
- `docs/ORACLE-PROD-VM.md` → yeni — tek referans: SSH, dizinler, terim tablosu (VM / yerel / GCP arşiv)
- `scripts/ops/oracle/oracle_safe_deploy.sh` → yeni — rutin Oracle deploy (PG yedek, pull, Docker, Alembic, satır sayısı)
- `docs/KURALLAR-MASTER.md`, `docs/PROJE-MASTER.md` (bölüm 12) → üretim Oracle; GCP arşiv
- `docs/YERELDEN_VM_YAYIN.md`, `docs/VM_DEN_YERELE.md`, `docs/VM-YEREL-SENKRON-REHBERI.md` → `ssh`/`scp`, `/opt/kokpitim/`
- `docs/ORACLE_DEPLOY_ADIMLAR.md`, `docs/gcp2oraclegecisplani.md` → geçiş tamamlandı notu
- `docs/clauderapor.md`, `docs/kirowebsitesi.md`, `Agents/KURALLAR-MASTER.md`, `CLAUDE.md` → VM = Oracle
- `scripts/vm_safe_deploy.sh` → LEGACY GCP üst notu
- `scripts/vm_smoke_check.ps1` → varsayılan hedef Oracle SSH (`kokpitim-web`)

### Yapılan İşlem
GCP→Oracle geçişi sonrası repoda «VM» ifadesi **Oracle `kokpitim-v2` (`129.159.30.175`)** anlamına sabitlendi. Eski `sps-server-v2` / `gcloud` komutları tarihsel arşiv olarak işaretlendi; canlı yayın yordamı `oracle_safe_deploy.sh` ile hizalandı.

### Notlar
- Üretim: `ubuntu@129.159.30.175`, uygulama `/opt/kokpitim/app`, container `kokpitim-web`, PG `kokpitim_db` @ `127.0.0.1`.
- GCP Faz 0 yedekleri: `backups/oracle_migration/` — değişmedi.

---

## TASK-112 | 2026-05-19 | ✅ Tamamlandı

**Görev:** 19mayonderi.md planı — 10 yeni özellik uygulaması
**Modül:** masaustu, surec/kpi_data, sp, admin, bireysel, k_radar_service, app/socketio_events
**Durum:** ✅ Tamamlandı

### Değiştirilen / Oluşturulan Dosyalar
- `services/executive_morning_service.py` → yeni — KPI/faaliyet/proje durum özeti API servisi
- `micro/modules/masaustu/routes.py` → `/api/morning-summary` endpoint eklendi
- `ui/templates/platform/masaustu/index.html` → Yönetici Sabah Özeti widget eklendi
- `ui/static/platform/js/masaustu.js` → widget JS + WebSocket refresh dinleyicisi
- `micro/modules/surec/routes_kpi_data.py` → `/process/api/kpi-data/bulk-template` (Excel şablon), `/process/api/kpi-data/bulk-import` (toplu yükleme), `/process/api/kpi/<id>/score-detail` (puan şeffaflığı) eklendi
- `services/early_warning_service.py` → yeni — gece KPI trend analizi + bildirim servisi
- `app/__init__.py` → `_init_early_warning_scheduler()` — APScheduler ile her gece 02:00 tetikleyici
- `services/k_radar_service.py` → `_get_radar_weights()` eklendi, `get_hub_summary` tenant'a özgü ağırlık kullanıyor
- `micro/modules/admin/routes.py` → `/admin/k-radar/weights` GET+POST endpoint eklendi
- `micro/modules/sp/routes_pages.py` → `/sp/strateji-haritasi`, `/sp/api/strateji-haritasi`, `/sp/rapor/donemsel` eklendi
- `ui/templates/platform/sp/strateji_haritasi.html` → yeni — vis-network ağaç görselleştirme
- `services/period_report_service.py` → yeni — dönemsel KPI karşılaştırma Excel raporu
- `services/alignment_score_service.py` → yeni — bireysel→stratejik hizalama skoru hesaplama
- `micro/modules/bireysel/routes.py` → `/bireysel/api/hizalama-skoru`, `/bireysel/api/ekip-hizalama` eklendi
- `micro/modules/sp/routes_plan_year.py` → sihirbaz endpoint'leri: `/sp/sihirbaz/yeni-yil`, preview, uygula
- `ui/templates/platform/sp/sihirbaz_yeni_yil.html` → yeni — 3 adımlı plan yılı geçiş sihirbazı
- `app/socketio_events.py` → `kpi_data_entered` event + `notify_kpi_update()` yardımcı fonksiyonu

### Yapılan İşlem
19mayonderi.md planındaki 10 maddenin tamamı uygulandı. Uygulama import testi geçti (`create_app()` hatasız).

### Notlar
- Cache invalidation: K-Radar verileri değiştiğinde (yeni KPI, yeni proje) önbellek 5 dk içinde kendiliğinden sona erer. Anlık yenileme gerekirse `cache.delete_memoized(get_hub_summary, tenant_id)` çağrılabilir.
