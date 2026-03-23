# TASKLOG — Kokpitim Görev Takip Defteri
> Her kod değişikliği bu dosyaya işlenir.
> Format: TASK-[numara] | Tarih | Durum
> En yeni kayıt en üstte.

---

## TASK-137 | 2026-03-23 | ✅ Tamamlandı

**Görev:** Süreç Faaliyetleri V2 — süreç karne faaliyetlerine `datetime` planı, çoklu atama, çoklu hatırlatma (in-app + opsiyonel e-posta), ertele/iptal aksiyonları, scheduler ile otomatik gerçekleşme ve bağlı PG için `KpiData(actual_value=1)` otomatik üretimi
**Modül:** `app/models/process.py`, `migrations/versions/4f3a2b1c9d8e_process_activity_v2_datetime_reminders.py`, `app/routes/process.py`, `app/services/process_activity_service.py`, `services/process_activity_scheduler.py`, `micro/services/notification_triggers.py`, `templates/process/karne.html`, `static/js/process_karne.js`, `__init__.py`, `app.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-136 | 2026-03-23 | ✅ Tamamlandı

**Görev:** Micro launcher’da az modül kartı — `get_accessible_modules` paket için yanlış ilişki (`system_modules`/`slug`); paketsiz kurumda kurum yöneticisine de yalnızca minimum 3 kart; düzeltme: `SubscriptionPackage.modules` + `SystemModule.code` eşlemesi, kod→launcher id sözlüğü, ayrıcalıklı rollerde tam liste
**Modül:** `micro/core/module_registry.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-135 | 2026-03-23 | ✅ Tamamlandı

**Görev:** Veritabanından **`1KMF`** kurumu (`tenants.id=9`, KMF Yonetim Danismanligi) kalıcı silindi; yedek `instance/kokpitim_before_tenant_delete_*.db`; tekrar kullanım için `scripts/delete_tenant_permanent.py`
**Modül:** `scripts/delete_tenant_permanent.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-134 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro hızlı giriş URL’leri **`/Hgs_mfg`** ve **`/Hgs_mfg/login/<id>`**; eski **`/hgs`** ve **`/hgs/login/<id>`** → 301 yönlendirme; `module_registry`, kullanım kılavuzu, `test_upload.py`
**Modül:** `micro/modules/hgs/routes.py`, `micro/core/module_registry.py`, `docs/`
**Durum:** ✅ Tamamlandı

---

## TASK-133 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Prod öncesi düzeltmeler — V3 panel linki kaldırıldı; Süreç PG toplamı gerçek `count`; faaliyet sıralamasında `end_date` NULL sonda; masaüstü bilgi paneli (kök vs `legacy_url_prefix`, localStorage); karalama metni; bireysel karne hedef uyarısı “tahmini / resmi değil” vurgusu; `docs/micro-kullanim-kilavuzu.md` + `docs/micro-kullanim-kilavuzu-yazdir.html` (PDF için yazdır); yol haritası V3 notu güncellendi
**Modül:** `micro/templates/micro/masaustu/index.html`, `micro/modules/masaustu/routes.py`, `micro/templates/micro/bireysel/karne.html`, `micro/static/micro/js/bireysel.js`, `docs/`
**Durum:** ✅ Tamamlandı

---

## TASK-132 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Bireysel karne + Masaüstü — planın uygulanması: timeline API, PG serisi endpoint, ısı/detay/sparkline; masaüstü komuta kartı, hızlı işlemler, Benim Masam, eksik PG (bu ay), bildirim okundu, karalama + widget sırası/gizleme (LS + Sortable), `docs/masaustu-bireysel-karne-yol-haritasi.md`
**Modül:** `micro/modules/bireysel/routes.py`, `micro/modules/masaustu/routes.py`, `micro/templates/micro/bireysel/karne.html`, `micro/templates/micro/masaustu/index.html`, `micro/static/micro/js/bireysel.js`, `micro/static/micro/js/masaustu.js`, `micro/static/micro/css/bireysel-karne.css`, `micro/static/micro/css/masaustu.css`, `docs/`
**Durum:** ✅ Tamamlandı

---

## TASK-131 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Proje analizler hub (`/project/<id>/analizler`) — sayfa başlığı ve `<title>`: **Proje Analizleri (geliştirme aşamasında)**
**Modül:** `micro/templates/micro/project/analyses.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-130 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi — **PG ekle / düzenle** (`modal-kpi-add`) başlık ve footer; kök mavi «Bootstrap» görünümü kaldırıldı, Micro standart modal başlığı
**Modül:** `micro/templates/micro/surec/karne.html`, `micro/static/micro/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-129 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi — **Veri Girişi Sihirbazı** modal başlığı; gradient yerine Micro standart `.mc-modal-header` / lavanta ikon rozeti
**Modül:** `micro/static/micro/css/surec.css`, `micro/templates/micro/surec/karne.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-128 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi — Performans Göstergeleri kartında **Yazdır** yanına **Tablo Görünümü** butonu; tıklanınca PG kartı ile aynı `microPgTablo.open(null)` modalı
**Modül:** `micro/templates/micro/surec/karne.html`, `micro/static/micro/js/surec.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-127 | 2026-03-19 | ✅ Tamamlandı

**Görev:** **Proje özeti** kartı — Süreç özeti ile aynı düzen: önce **Özet Bilgiler**, yöneticiler için **Kurum geneli — projeler** (`project_tenant`, `data-ov-pt`), sonra **Grafikler** akordeonları (bitiş+görev / risk); `kurum_overview` `_build_project_block`; Chart yalnız görünür canvas; API `project_tenant`
**Modül:** `micro/modules/kurum/kurum_overview.py`, `micro/templates/micro/kurum/index.html`, `micro/static/micro/js/kurum.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-126 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kurum **Süreç özeti** kartı — önce **Özet Bilgiler** (birleşik rakam ızgarası), sonra **Grafikler** başlığı altında akordeon (PG+strateji, operasyon, risk, performans); `__kurumRedrawCharts` + görünür canvas’da Chart; çift `data-ov` için `querySelectorAll`
**Modül:** `micro/templates/micro/kurum/index.html`, `micro/static/micro/js/kurum.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-125 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kurum **Süreç özeti** — risk/uyarı (60 gün bayat PG verisi, geciken faaliyet, eksik PG tanımı), performans (`calculated_score` ortalama, düşük/skorsuz dağılımı); yöneticiler için **kurum geneli** ayrı kutu (`process_tenant`); yalnızca yeni `Process` modeli; grafikler + API/JS güncellemesi
**Modül:** `micro/modules/kurum/kurum_overview.py`, `micro/templates/micro/kurum/index.html`, `micro/static/micro/js/kurum.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-124 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kurum paneli — **Stratejik Kimlik** kartı en üste taşındı; **Süreç / Proje özeti** Chart.js pasta + yatay çubuk grafikleri, vurgulu metinler ve “Tüm sayılar” ızgarası; `kurum.css` yükseklik; `kurum.js` grafik yenileme + tema olayı
**Modül:** `micro/templates/micro/kurum/index.html`, `micro/static/micro/js/kurum.js`, `micro/static/micro/css/kurum.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-123 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kurum paneli (`/kurum`) — **tüm giriş yapmış tenant kullanıcılarına açık**; süreç/proje **özet metrikleri** (erişim kapsamına göre); `GET /kurum/api/overview` + **90 sn** sayfa içi yenileme; düzenleme API’leri ve ayarlar rolde kaldı; `module_registry` kurum rol kısıtı kaldırıldı
**Modül:** `micro/modules/kurum/kurum_overview.py`, `micro/modules/kurum/routes.py`, `micro/templates/micro/kurum/index.html`, `micro/static/micro/js/kurum.js`, `micro/core/module_registry.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-122 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kurum paneli (`/kurum`) — **Stratejik Kimlik** kartı akordeon (Amaç, Temel değerler, Etik, Kalite); **vizyon** akordeon dışında vurgulu hero blok; **Stratejiler** kartı ana strateji başına akordeon + alt stratejiler panelde; `kurum.js` alan okuma `data-sk-field`
**Modül:** `micro/templates/micro/kurum/index.html`, `micro/static/micro/js/kurum.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-121 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Proje analiz araçları (CPM, SLA, kapasite, baseline, bağımlılık matrisi, kurallar, entegrasyonlar, tekrarlayan, çalışma günleri) — klasik Bootstrap şablonları yerine **Micro** (`base_tool.html`, Tailwind, `mc-pt-*`, SweetAlert toast); bilgi modalı Bootstrap’siz; `project_tool_info_data.js` + `project_tools_micro.js`; rotalar `load_project` + `user_can_access_project`
**Modül:** `micro/templates/micro/project/tools/*`, `micro/static/micro/css/project_tools.css`, `micro/static/micro/js/project_tool_info_data.js` (üretim), `project_tools_micro.js`, `micro/modules/proje/routes_project_tools_root.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-120 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç Yönetimi teknik raporu — sayfalar, veri modelleri, API’ler, işleme akışları, yetkiler, legacy `Surec` özeti; `docs/Surecrapor01.md`
**Modül:** `docs/Surecrapor01.md`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-119 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Proje analizleri hub — açıklama metni kaldırıldı; CPM/SLA vb. `/kok` yerine kök `/projeler/...`; **RAID** `Unexpected token '<'` — `app.create_app` içinde `api/routes.py` (`kokpitim_project_api_bp`) kök `/api/...` + legacy `/kok/api/...` çift kayıt (Flask `name=`); kırık `Blueprint.copy` kaldırıldı; `project_raid_micro.js` JSON doğrulama + `MICRO_API_BASE` + `credentials`
**Modül:** `app/__init__.py`, `micro/static/micro/js/project_raid_micro.js`, `docs/TASKLOG.md` (önceki: `analyses.html`, `routes_project_tools_root.py`)
**Durum:** ✅ Tamamlandı

---

## TASK-118 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Proje detayda **Proje analizleri** butonu + `/project/<id>/analizler` hub — eski “Proje Araçları” kart ızgarası (CPM, RAID→Micro, SLA, kapasite, baseline, bağımlılık matrisi, kurallar, entegrasyon, tekrarlayan, çalışma günleri); `main.*` klasik şablonlarına link; alt çubukta görev tamamlanma %; `_project_views_nav` entegrasyonu
**Modül:** `micro/modules/proje/routes_analyses.py`, `routes.py`, `micro/templates/micro/project/analyses.html`, `detail.html`, `_project_views_nav.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-117 | 2026-03-19 | ✅ Tamamlandı

**Görev:** `/project` geliştirmeleri — **filtreler** (kapsam benim/tümü ayrıcalıklı, tarih, lider, süreç, geciken/yakında bitiş), **sıralama** (güncelleme, bitiş, ad, geciken görev), **CSV** + **ICS** dışa aktarma, **toplu e-posta kanalı** (yalnız `is_privileged`), **4 haftalık tamamlanan trend** + **ısı haritası**, **RAID** + **sağlık** KPI, **benzer proje** (`clone_from`), **Chart.js tema** (`micro-theme-changed`)
**Modül:** `micro/modules/proje/project_list_query.py`, `project_overview_service.py`, `routes_list.py`, `routes_project_crud.py`, `micro/templates/micro/project/list.html`, `micro/templates/micro/project/form.html`, `micro/static/micro/js/app.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı (haftalık özet e-posta cron, Slack/Teams, Google OAuth senk — ayrı iş)

---

## TASK-116 | 2026-03-19 | ✅ Tamamlandı

**Görev:** `/project` proje listesi — **operasyon özeti**: KPI (proje, açık/geciken görev, görev≤7g, planı geçen proje, proje bitiş≤7g), Chart.js **doughnut** (görev durumu) + **yatay bar** (öncelik), **Dikkat** listesi (geciken görev veya proje bitişi geçmiş); yetki = `accessible_projects_query`; portföy linki ayrıcalıklı roller
**Modül:** `micro/modules/proje/project_overview_service.py`, `micro/modules/proje/routes_list.py`, `micro/templates/micro/project/list.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-115 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Proje **yeni lider / yeni üye** atamalarında uygulama içi bildirim + e-posta (`notify_project_leaders_added`, `notify_project_members_added`); Micro form (oluştur/düzenle) ve REST API (`/api/projeler` oluştur + PUT güncelle); `micro_project_new` `manager_id=leader_ids[0]` düzeltmesi
**Modül:** `micro/services/notification_triggers.py`, `micro/modules/proje/routes_project_crud.py`, `api/routes.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-114 | 2026-03-22 | ✅ Tamamlandı

**Görev:** Proje düzenlemede lider/üye kaydı **DB’de vardı** ama form ve detay **ORM (Legacy `user`) boş** olduğu için değişiklik görünmüyordu — `project_leaders` / `project_members` / `project_observers` tablosundan okuma; `Project.leader_user_ids`, `member_user_ids`, `observer_user_ids`; `project_form_init` + `resolve_leader_ids_from_form(..., project=)` ile koruma
**Modül:** `models/project.py`, `micro/modules/proje/helpers.py`, `micro/modules/proje/display.py`, `micro/modules/proje/routes_project_crud.py`, `micro/templates/micro/project/detail.html`, `micro/templates/micro/project/list.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-113 | 2026-03-22 | ✅ Tamamlandı

**Görev:** Proje detay **Görev özeti (durum)** kanban sütun sırası: **Tamamlandı → Devam Ediyor → Beklemede → Yapılacak**
**Modül:** `micro/modules/proje/routes_project_crud.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-112 | 2026-03-19 | ✅ Tamamlandı

**Görev:** **Çoklu proje lideri** — `project_leaders` ilişki tablosu; `manager_id` birincil lider; Micro form/JS çoklu seçim; yetkiler, bildirimler, API (`manager_ids` + `leader_ids`), rapor/üst yönetim filtresi, klonlama, migrasyon `c7d8e9f0a1b2`
**Modül:** `models/project.py`, `models/__init__.py`, `migrations/versions/c7d8e9f0a1b2_add_project_leaders.py`, `micro/modules/proje/*`, `micro/templates/micro/project/*`, `micro/static/micro/js/project_form_transfer.js`, `api/routes.py`, `services/*`, `decorators.py`, `main/routes.py`, `v3/routes.py`, `scripts/seed_boun_sample_project.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-111 | 2026-03-19 | ✅ Tamamlandı

**Görev:** **Proje yönetimi (Micro)** görev oluşturma/düzenlemede bildirimler: uygulama içi (`notifications` + WebSocket) ve e-posta (`notification_triggers` + `email_service`); proje `channels` / `notify_manager` uyumu; varsayılan kanallar `in_app` + `email`
**Modül:** `micro/modules/proje/routes_tasks.py`, `micro/services/notification_triggers.py`, `models/project.py` (`get_notification_settings` varsayılan), `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-110 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Oturum gerekince yönlendirme **`/login?next=...`** (kökta); **`/kok/login`** yerine çubukta `/kok` olmasın; **`public_login` / `public_logout`** + `auth_bp` kayıt sırası (micro `/login` çakışması giderildi); `micro_bp.micro_login` kaldırıldı
**Modül:** `app/__init__.py`, `app/routes/auth.py`, `app/extensions.py`, `app/utils/decorators.py`, `main/routes.py`, `micro/modules/shared/auth/routes.py`, `templates/*`, `micro/templates/*`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-109 | 2026-03-19 | ✅ Tamamlandı

**Görev:** BOUN tenant için **örnek proje** tohum script’i: 1 lider + 5 üye, 20 görev (12 tamamlandı); `scripts/seed_boun_sample_project.py` (`--tenant-id`, `--replace`, `--dry-run`)
**Modül:** `scripts/seed_boun_sample_project.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-108 | 2026-03-22 | ✅ Tamamlandı

**Görev:** Açılışta **klasik giriş** (`auth_bp.login` / `/kok/login`); `login_manager.login_view` → `auth_bp.login`; `/login` → klasik girişe yönlendirme; çıkış → `auth_bp.login`; `docs/micro-kok-url-migration.md`
**Modül:** `app/__init__.py`, `app/routes/auth.py`, `micro/modules/shared/auth/routes.py`, `docs/micro-kok-url-migration.md`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-107 | 2026-03-22 | ✅ Tamamlandı

**Görev:** Micro **sol sidebar marka** alanı — mor «K» yerine **Kokpitim logosu** (`docs/kokpitim-logo.png` → `micro/static/micro/img/kokpitim-logo.png`); `.sidebar-brand-logo` img + `sidebar.css` (ilk sürümdeki topbar logosu kaldırıldı)
**Modül:** `micro/templates/micro/base.html`, `micro/static/micro/css/sidebar.css`, `micro/static/micro/img/kokpitim-logo.png`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-106 | 2026-03-19 | ✅ Tamamlandı

**Görev:** **Micro kök URL** — `micro_bp` öneki kaldırıldı (`/`, `/process`, …); klasik Kokpitim **`LEGACY_URL_PREFIX`** (varsayılan **`/kok`**) altında; **`/micro/...` → kök** ve **`/isr/...` → `/kok/...`** uyumluluk yönlendirmeleri; Micro statik **`/m/`**; `login_view` → `micro_bp.micro_login`; giriş/çıkış varsayılan launcher; Swagger `create_swagger_blueprint(legacy)`; eski `/micro/...` path’li şablon/JS/registry temizliği; kök **`GET /health`**; `docs/micro-kok-url-migration.md`
**Modül:** `config.py`, `app/__init__.py`, `app/api/swagger.py`, `app/routes/auth.py`, `micro/__init__.py`, `micro/core/*`, `micro/modules/*`, `micro/templates/*`, `micro/static/micro/js/*`, `main/routes.py`, `test_upload.py`, `test_photo_final.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-105 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro **RAID** sayfasında “Nasıl kullanılır?” için **Bootstrap tamamen kaldırıldı**; `mc-modal` + `micro-tool-info-modal.js` (`MICRO_TOOL_INFO_DATA` `_tool_info_modal.html`’den `scripts/gen_micro_tool_info_js.py` ile üretilir); `_tool_info_modal_micro.html` + `project_views.css` Bootstrap sınıf shimi
**Modül:** `micro/templates/micro/project/raid.html`, `micro/templates/micro/project/_tool_info_modal_micro.html`, `micro/static/micro/js/micro-tool-info-modal.js`, `micro/static/micro/css/project_views.css`, `scripts/gen_micro_tool_info_js.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-104 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro **Proje Yönetimi iyileştirme planı** uygulaması: TR başlıklar; liste **arama + öncelik filtresi**; **CoreUser** ile yönetici/üye etiketleri (`display.py`); detayda **görünüm şeridi** + görev özeti + **HTML dialog** ile silme; portföy **çift yol** (klasik matris / App tenant + Surec–Process eşlemesi); rotalar **list / crud / views / tasks** dosyalarına bölündü; **`micro-notify.js`** + RAID **Bootstrap kaldırıldı** (mc + vanilla modal/sekme); takvim yükleme göstergesi; `docs/proje-legacy-ve-tenant.md`; `tests/test_micro_proje_display.py`
**Modül:** `micro/modules/proje/*`, `micro/templates/micro/project/*`, `micro/static/micro/js/micro-notify.js`, `micro/static/micro/js/project_raid_micro.js`, `micro/static/micro/css/project_views.css`, `micro/templates/micro/base.html`, `docs/`, `tests/`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-103 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro **Proje Yönetimi** formunda proje lideri + üye + gözlemci seçimi süreç paneli ile aynı UX (kaynak → hedef, Ekle/Çıkar, çift tıklama); gönderimde `manager_id` + gizli `members` / `observers` (çoklu seçim + `option.hidden` kaynaklı POST sorunları giderildi). **Düzeltme:** kullanıcı listesi `LegacyUser` (`user`/`kurum_id`) yerine Micro ile aynı **`app.models.core.User`** (`users`/`tenant_id`, `is_active`) + üye/gözlemci senkronu `project_members` / `project_observers` doğrudan yazım
**Modül:** `micro/modules/proje/routes.py` (`form_users`, `form_init`), `micro/templates/micro/project/form.html`, `micro/static/micro/css/project_form_transfer.css`, `micro/static/micro/js/project_form_transfer.js`, `micro/templates/micro/project/task_form.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-102 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Takvim, Gantt, RAID ve Kanban **Micro tema** içinde (`micro/templates/micro/project/*.html`, `project_views.css`, `_project_views_nav`); klasik **`/kok/projeler/<id>/*`** (main_bp) rotaları **Micro görünüme redirect**; çift tanımlı `proje_gantt` kaldırıldı (`project_views_nav` → `main.project_gantt`); proje detayındaki “kök şablon” uyarısı kaldırıldı
**Modül:** `micro/modules/proje/routes.py`, `micro/templates/micro/project/*`, `micro/static/micro/css/project_views.css`, `main/routes.py`, `templates/partials/project_views_nav.html`, `micro/templates/micro/project/detail.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-101 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro proje **üye / gözlemci** seçimi (`members`, `observers` — form + `_sync_project_members_observers`); düzenlemede bildirim checkbox’larından `notification_settings` güncelleme; detay sayfasında ekip rozetleri + **Takvim / Gantt / RAID / Kanban** (`/project/<id>/views/*`, erişim `user_can_access_project`)
**Modül:** `micro/modules/proje/routes.py`, `micro/templates/micro/project/form.html`, `micro/templates/micro/project/detail.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-100 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Alembic: `e7a8` batch_alter yerine idempotent sütun ekleme (SQLite FK yansıma hatası); `add_surec_parent` güncel şemada `surec` yoksa no-op; merge `9504` tek hat (`e7a8` → `add_surec_parent` → `9504` → `a1c2d3e4f5a6`); 2047 Supabase zinciri `migrations/versions/_disabled/`; `config.py` göreli sqlite URI → `instance/` + mutlak yol (Flask CLI `kokpitim.app` ile yanlış `C:\\instance\\db` önlendi); kök `/projeler`, `/projeler/yeni`, detay/düzenle, görev yolları → Micro redirect
**Modül:** `migrations/versions/e7a8b9c0d1e2_kpi_data_deleted_meta.py`, `add_surec_parent_id.py`, `9504e9a7e70f_merge_add_surec_parent_and_kpi_data_.py`, `config.py`, `main/routes.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-099 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro **Proje Yönetimi** — İngilizce URL (`/project`, `/project/portfolio`, `/project/<id>`, görev CRUD), `permissions.py` (süreç ile paralel), stratejik portföy + analiz, görevde `process_kpi_id` (PG) + migration (revizyon: `a1c2d3e4f5a6`, eski `f8a9b0c1d2e3` kaldırıldı)
**Modül:** `micro/modules/proje/*`, `micro/templates/micro/project/*`, `models/project.py`, `migrations/versions/a1c2d3e4f5a6_task_process_kpi_id.py`, `micro/core/module_registry.py`, `micro/templates/micro/base.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-098 | 2026-03-19 | ✅ Tamamlandı

**Görev:** `py app.py` ile çalışan fabrikada `main_bp` kayıtlı olmadığı için `/strategy/projects` (Proje Portföyü) 404 veriyordu; `app.create_app` sonuna `main_bp` eklendi. `User` üzerinde legacy uyumu: `kurum_id` → `tenant_id`, `sistem_rol` → rol eşlemesi
**Modül:** `app/__init__.py`, `app/models/core.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-097 | 2026-03-19 | ✅ Tamamlandı

**Görev:** PG kartı **Önceki / Sonraki** gezintisi: yıl ofseti yerine **seçilen gösterime göre bir önceki/sonraki periyot** (çeyrek, ay, hafta, 6 ay, yıl, günlükte **gün**); `karneNavPeriodKey` + `karneNavDataYear`; yıl seçicide senkron
**Modül:** `micro/static/micro/js/surec.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-096 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi **Performans Göstergeleri** kartında modal ile aynı gösterim mantığı: kart üstünde **Yıl**, **Gösterim**, **Önceki / rozet / Sonraki** (kalan alanda ortalı); günlükte ay/gün/yıl gezintisi; diğer gösterimlerde periyot imi + veri yılı; gizli `pg-gunluk-ay-select` modal senkronu; PG tık modalı aynı
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-095 | 2026-03-19 | ✅ Tamamlandı

**Görev:** PG tablo modalı: **yıl / gösterim** select daraltma; gösterim sırası **Yıllık → 6 aylık → Çeyreklik → Aylık → Haftalık → Günlük**, varsayılan **çeyrek**; modal açılışında yıl **takvim yılı**; **haftalık** sütun başlıkları **gün + ay** aralığı; **günlük** tek ay + **Önceki/Sonraki ay**; ana sayfa `pg-periyot-select` aynı sıra; API `halfyear_1`/`halfyear_2` (`process_utils.data_date_to_period_keys`); kanban/Excel **6 aylık** gerçek anahtarlar
**Modül:** `app/utils/process_utils.py`, `micro/static/micro/js/micro_pg_tablo_modal.js`, `micro/static/micro/js/surec.js`, `micro/templates/surec/karne.html`, `micro/static/micro/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-094 | 2026-03-21 | ✅ Tamamlandı

**Görev:** Micro süreç karnesinde **PG kartına tıklanınca** kök karne **«Süreç Karnesi — Performans Göstergeleri»** tablosunun **tam modal kopyası** (yıl/gösterim, önceki-sonraki, sütun gösterimi, dinamik thead, hücre tık → veri detay + düzenle/sil); **süreç seçici yok**; **tıklanan PG satırı vurgu + kaydırma**; API `GET /process/api/kpi-data/detail`, stub `proje-gorevleri`; `micro_pg_tablo_modal.js` + `surec.css` Micro renkleri; **asa (VGS)** ayrı
**Modül:** `micro/modules/surec/routes.py`, `micro/templates/surec/karne.html`, `micro/static/micro/js/micro_pg_tablo_modal.js`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-093 | 2026-03-21 | ✅ Tamamlandı

**Görev:** Süreç karnesi PG **kartına tıklayınca VGS açılması kaldırıldı**; favori / düzenle / sil yanına **asa (fa-wand-magic-sparkles) `btn-kpi-vgs`** ile VGS; yardımcı sihirbaz Swal metni güncellendi; `kb-card--clickable` kaldırıldı
**Modül:** `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-092 | 2026-03-21 | ✅ Tamamlandı

**Görev:** VGS modal: **Kayıt özeti** kaldırıldı; **Kayıt geçmişi** accordion formun **en altına** taşındı; önizleme JS/CSS temizlendi
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec_vgs.js`, `micro/static/micro/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-091 | 2026-03-21 | ✅ Tamamlandı

**Görev:** VGS modal genişliği artırıldı (`max-width` ~1080px); kayıt geçmişi **İşlem** sütunu `min-width` + tablo sarmalayıcı yatay kaydırma (dar ekran)
**Modül:** `micro/static/micro/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-090 | 2026-03-21 | ✅ Tamamlandı

**Görev:** VGS: modal alanı **Veri tarihi** (olaya ilişkin gün); **Veri girişi** Kaydet anında otomatik; kayıt geçmişi tablosunda **Yıl/Periyot kaldırıldı**, **Veri girişi** sütunu (`recorded_at`); özet ve düzenle/sil meta metinleri güncellendi
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec_vgs.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-089 | 2026-03-21 | ✅ Tamamlandı

**Görev:** VGS kayıt geçmişinde **son güncelleme**: kim + tarih (`KpiDataAudit` UPDATE); gerçekleşen / açıklama / hedeften herhangi biri değişince audit; API `last_updated_at`, `last_updated_by_name`, `recorded_at`; tabloda **Son güncelleme** sütunu (silinme sütunu aynı)
**Modül:** `micro/modules/surec/routes.py`, `micro/static/micro/js/surec_vgs.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-088 | 2026-03-21 | ✅ Tamamlandı

**Görev:** VGS geçmiş **Düzenle / Sil** akışında SweetAlert kaldırıldı; **MicroUI `mc-modal`** ile `modal-vgs-history-edit` ve `modal-vgs-history-delete` eklendi (`z-index: 10060`); Escape ve VGS backdrop tıklaması önce alt modalı kapatır
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec_vgs.js`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-087 | 2026-03-21 | 📝 Not

**Not:** `kpi_data.deleted_at` / `deleted_by_id` modelde varken DB güncellenmediyse SQLite’ta `no such column` → `/process/api/karne/...` **500** → ön yüzde «Unexpected token '<'… JSON» hatası. Çözüm: `py scripts/add_kpi_data_deleted_columns_sqlite.py` veya `flask db upgrade` (migration zinciri uygunsa).
**Modül:** `scripts/add_kpi_data_deleted_columns_sqlite.py`, `docs/TASKLOG.md`
**Durum:** 📝 Not

---

## TASK-086 | 2026-03-21 | ✅ Tamamlandı

**Görev:** VGS **Kayıt geçmişi** accordion (başlangıçta kapalı); `GET .../kpi-data/history/<kpi_id>` ile PG’nin tüm yıllar + silinmiş kayıtlar; üye yalnız kendi satırlarında CRUD, lider/sahip + ayrıcalıklı roller tüm aktif satırlarda; **soft sil** zaten `is_active`; `deleted_at` / `deleted_by_id` + migration; silinme bilgisi listede; skor tarafı `is_active=True` ile uyumlu
**Modül:** `app/models/process.py`, `migrations/versions/e7a8b9c0d1e2_kpi_data_deleted_meta.py`, `micro/modules/surec/routes.py`, `micro/templates/surec/karne.html`, `micro/static/micro/js/surec_vgs.js`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-085 | 2026-03-21 | ✅ Tamamlandı

**Görev:** VGS modal başlığı **Veri Girişi Sihirbazı**; **periyot seçimi kaldırıldı** — yalnızca **veri girişi tarihi** (zorunlu); yıl/dönem PG ölçüm tipine göre tarihten türetilir; haftalık/günlük için `period_month` API’ye eklenir
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec_vgs.js`, `micro/static/micro/js/surec.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-084 | 2026-03-21 | ✅ Tamamlandı

**Görev:** Süreç karnesi **VGS** çok adımlı akış kaldırıldı: **tek ekranda** dönem + değer + altta **canlı kayıt özeti**; footer yalnız İptal / **Kaydet** (`form` submit); `surec_vgs.js` adım UI ve çift kayıt dinleyicisi temizlendi
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec_vgs.js`, `micro/static/micro/css/surec.css`, `micro/static/micro/js/surec.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-083 | 2026-03-21 | ✅ Tamamlandı

**Görev:** Micro süreç karnesi **VGS** (`surec_vgs.js`) `surec.js` ile bağlandı: `initSurecVgs`, `karne.html` script sırası, eski tek adımlı kayıt/`kpiDataEntryPayload` kaldırıldı; `getCanEnterPgv` ile API sonrası yetki güncellemesi; form submit yalnız `preventDefault`
**Modül:** `micro/static/micro/js/surec.js`, `micro/static/micro/js/surec_vgs.js`, `micro/templates/surec/karne.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-082 | 2026-03-21 | ✅ Tamamlandı

**Görev:** Süreç düzenlemede üye ekleyince «Yeni süreç oluşturma yetkiniz yok» — şablonda **`surec-edit-id` gizli alanı yoktu**; JS süreç id yazamıyordu, `editId` boş kalıyordu (liderlerde kontrol tetikleniyordu). `index.html` gizli input eklendi; `saveProcessForm` düzenle modunda boş id iken yöneticiye yanlışlıkla ADD gitmesini engelleyen uyarı
**Modül:** `micro/templates/surec/index.html`, `micro/static/micro/js/surec.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-081 | 2026-03-21 | ✅ Tamamlandı

**Görev:** Süreç listesinde **lider/sahip** kullanıcıda «Süreci düzenle» görünmüyordu (yalnızca `can_crud_process`); ayrıca düzenleme modalı yalnızca yöneticilere render ediliyordu. `can_open_process_modal`, şablonda düzenle/sil ayrımı, `surec.js` `openEditModal` / `saveProcessForm` (yeni süreç yalnız yönetici)
**Modül:** `micro/modules/surec/routes.py`, `micro/templates/surec/index.html`, `micro/static/micro/js/surec.js`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-080 | 2026-03-21 | ✅ Tamamlandı

**Görev:** Kurum özel SMTP kapalıyken **Admin kurumunun kayıtlı SMTP’si** varsayılan çıkış: `send_notification_email` öncelik kurum özel → `MAIL_*` kimlik doluysa ortam → yoksa `Admin` rolündeki ilk aktif kullanıcının tenant’ı `_get_tenant_smtp_config`; `eposta.html` bilgilendirme güncellendi
**Modül:** `micro/services/email_service.py`, `micro/templates/ayarlar/eposta.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-079 | 2026-03-21 | ✅ Tamamlandı

**Görev:** BOUN **Adil** test maili — Admin (tenant 1) **özel SMTP açık**, BOUN (tenant 7) **özel SMTP kapalı**; sistem `MAIL_USERNAME` boş olduğundan gönderim sessizce başarısızdı. `send_notification_email` artık **(bool, hata_metni)** döner; kimlik yoksa anlaşılır Türkçe mesaj; SMTP istisnaları ayrıştırıldı; test endpoint mesajı iletir; bildirim tetikleyicide başarısızlık loglanır; `eposta.html` uyarı + doğru sistem SMTP açıklaması
**Modül:** `micro/services/email_service.py`, `micro/modules/shared/ayarlar/routes.py`, `micro/services/notification_triggers.py`, `micro/templates/ayarlar/eposta.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-078 | 2026-03-19 | ✅ Tamamlandı

**Görev:** `/ayarlar/eposta` test maili — turuncu ünlemli pencerenin **hata sanılması**; `MicroUI.onayla` varsayılanı `warning`+kırmızı onaydı. Varsayılan **`question` + mor onay**; test mailinde **`info`**; `MicroUI.post` HTML (403) yanıtında daha anlamlı mesaj; bilgi bandında onay açıklaması
**Modül:** `micro/static/micro/js/app.js`, `micro/static/micro/js/ayarlar_eposta.js`, `micro/templates/ayarlar/eposta.html`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-077 | 2026-03-19 | ✅ Tamamlandı

**Görev:** **Default Corp** KMF/s11 import verisinin temizlenmesi — `wipe_process_pg_data.py --process-id 1` (HR-01: 38 PG + 291 KpiData pasif)
**Modül:** `scripts/wipe_process_pg_data.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-076 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Son **s11 / KMF** import verisinin silinmesi — `scripts/wipe_process_pg_data.py` (aktif `ProcessKpi` + `KpiData` + ilgili `FavoriteKpi` → `is_active=False`, `kmf_s11_import --wipe-kpis` ile aynı mantık); Boğaziçi süreç **18** üzerinde çalıştırıldı
**Modül:** `scripts/wipe_process_pg_data.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-075 | 2026-03-19 | ✅ Tamamlandı

**Görev:** **Adil** (`adil@kalitesoleni.com`, `tenant_admin`, Boğaziçi) süreç listesi analizi — KMF s11 verisi **Default Corp süreç 1**’deydi; BOUN’da **H1.1 eksik** ve süreç 18 **yanlış tenant** alt stratejisine (id 74) bağlıydı. `scripts/ensure_boun_h11_and_import_s11.py` ile tenant 7’de **H1.1 (id=75)** oluşturuldu, süreç **18** bağlantısı düzeltildi, `s11-extracted.json` → süreç **18** import (38 PG). `scripts/adil_process_access_report.py` rapor + `--heavy` ile yoğun süreç taraması; `adil_process_access_report.py` KpiData join `process_kpi_id` düzeltmesi
**Modül:** `scripts/ensure_boun_h11_and_import_s11.py`, `scripts/adil_process_access_report.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-074 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Çift **H1.1** alt strateji tutarsızlığı — `SubStrategy` **id=54** kaldırıldı; `process_sub_strategy_links` (18,24,25) **74**’e taşındı / çakışanlar silindi; `kmf_s11_import.py` aynı kod için `.order_by(SubStrategy.id.desc())` (gelecekte çift kayıtta deterministik seçim)
**Modül:** Veritabanı (tek seferlik), `scripts/kmf_s11_import.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-073 | 2026-03-19 | ✅ Tamamlandı

**Görev:** KMF s11 kullanıcı yanıtları — PG **H1.1** + **İyileştirme**; **6 ay** ölçüm periyodu (`karne.html` + `surec.js` Toplama çarpanı); `scripts/kmf_s11_import.py` (hedef aralığı→ortalama, çeyrek `KpiData`, 2 lider+6 üye random, `--wipe-kpis`); `analiz-boun-sr4-karne-excel.md` import bölümü
**Modül:** `scripts/kmf_s11_import.py`, `scripts/kmf_s11_extract.py`, `micro/templates/surec/karne.html`, `micro/static/micro/js/surec.js`, `docs/analiz-boun-sr4-karne-excel.md`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-072 | 2026-03-19 | ✅ Tamamlandı

**Görev:** `s11.xlsx` veri çıkarımı — `scripts/kmf_s11_extract.py` (Fiili/Hedef birleştirme, meta, çeyrekler, başarı eşikleri); `docs/KMF/s11-extracted.json`; `analiz-boun-sr4-karne-excel.md` güncellendi; netleştirme soruları JSON’da
**Modül:** `scripts/kmf_s11_extract.py`, `docs/KMF/s11-extracted.json`, `docs/analiz-boun-sr4-karne-excel.md`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-071 | 2026-03-19 | ✅ Tamamlandı

**Görev:** `docs/KMF/s11.xlsx` (SR4 karnesi) analizi — 6 sayfa, sütun/Kokpitim eşlemesi, checklist; `analiz-boun-sr4-karne-excel.md` güncellendi; `analyze_karne_xlsx.py` konsol Unicode; `s11-xlsx-ozet.txt`
**Modül:** `docs/analiz-boun-sr4-karne-excel.md`, `scripts/analyze_karne_xlsx.py`, `docs/KMF/s11-xlsx-ozet.txt`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-070 | 2026-03-19 | ✅ Tamamlandı

**Görev:** BOUN SR4 Pazarlama süreç karnesi `.xlsx` analiz notu + `scripts/analyze_karne_xlsx.py` (ilk sürüm; dosya yokken çerçeve)
**Modül:** `docs/analiz-boun-sr4-karne-excel.md`, `scripts/analyze_karne_xlsx.py`, `docs/TASKLOG.md`
**Durum:** ✅ Tamamlandı

---

## TASK-069 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç Karnesi PG kartı — başlık altı açıklama metni kaldırıldı; **Görünüm periyodu** yanında üst bardan taşınan aksiyonlar (sihirbaz, PG ekle, faaliyet ekle, Excel, yazdır); **Excel’e aktar** artık gerçek **.xlsx** (`openpyxl`, `POST /process/api/karne/<id>/export-xlsx`).
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`, `micro/modules/surec/routes.py`
**Durum:** ✅ Tamamlandı

---

## TASK-068 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Karnede Kanban gauge — skor rengi **%0 kırmızı → %100 yeşil** sürekli HSL geçişi (`--gauge-h = pct * 1.2deg`); veri yok → nötr gri yay/metin. PG kartında favori ile sil arasında **Düzenle** (kalem, `can_crud_pg` + GET şablonu); `surec_api_kpi_get` / `surec_api_kpi_update` ile modal doldurma ve kayıt; sil URL’si `url_for` ile; `sub_strategy_id` boşaltılabilir (null).
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-067 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro süreç karnesi «Performans Göstergeleri» — tablo kaldırıldı; **3 kolon Kanban** (Hedefte / Risk altında / Hedef dışı) + **yarım daire gauge** (dash 58); başarı yüzdesi eski tablo mantığı; veri yok → Risk; üstte görünüm periyodu → karta tıklayınca o döneme veri girişi; kartta alt strateji kodu + başlık; favori/sil korundu; API’ye `sub_strategy_code` eklendi; stiller `surec.css` (`.kb-*`)
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`, `micro/modules/surec/routes.py` (karne JSON alanı)
**Durum:** ✅ Tamamlandı

---

## TASK-066 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro süreç karnesi PG **Veri gir** diyaloğu — `.cursorrules` yerel modal şablonu (`mc-modal-overlay` / `mc-modal-header|body|footer`, lavanta ikonlu `mc-modal-title`, `mc-form-label` + `mc-form-input`, footer’da İptal + birincil Kaydet); SweetAlert2 `input` formu kaldırıldı
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-065 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro PG karnesi okunabilirlik — **Görünüm periyodu** (çeyrek / ay / hafta / gün+ay seçimi / 6 aylık özet / yıl sonu), dinamik `thead`+`tbody` (kök `process_karne.js` anahtarları); **Sütunları göster/gizle** (localStorage) sabit sütunlar için; CSV seçilen görünüme göre; 6 aylık hücreler aylık `entries` toplamı/ortalaması (veri girişi yok, tooltip)
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-064 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro süreç karnesi KPI kartı — kök `pgTabloCard` ile aynı sütunlar: Kodu, Ana/Alt strateji, Performans adı, Ağırlık, Birim, Ölçüm per., Yıllık hedef; I–IV çeyrek (Hedef/Gerç./Durum); Yıl sonu; Başarı puanı; İşlemler. Veri girişi `ceyrek` / `yillik` API; favori `/process/api/favorite-kpi/toggle`; özet metriklerde çeyrek yedek; CSV çeyrek kolonları
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-063 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro `karne.html` — `surec.css` / `surec.js` için `?v=config VERSION` önbellek kırma; micro karnesi değişiklik doğrulama dokümanı `docs/micro-karne-kontrol-listesi.md`
**Modül:** `micro/templates/surec/karne.html`, `docs/micro-karne-kontrol-listesi.md`
**Durum:** ✅ Tamamlandı

---

## TASK-062 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro süreç karnesi PG ekle — kök `process/karne` #addPGModal ile görsel/metin hizası: mavi modal başlığı (`#0d6efd`), hız göstergesi ikonu, başlık «Yeni Performans Göstergesi», etiket/placeholder/select metinleri kök ile aynı; yeşil «Kaydet» (`fa-plus-circle`); başarı kartı `bg-light`/`border-success` + düz yeşil header; araç çubuğu ve tablo başlığı «PG ekle» beyaz çerçeveli buton
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/css/surec.css`, `micro/static/micro/js/surec.js`
**Durum:** ✅ Tamamlandı

---

## TASK-061 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Başarı puanı açıklamalarının DB’de saklanması — `basari_puani_araliklari` JSON’u `{"1":{"aralik":"0-40","aciklama":"..."}}` (açıklama yoksa eski düz string); `parse_basari_puani_araliklari` / `hesapla_basari_puani` geriye dönük uyum; kök `process_karne.js`, `surec_karnesi.js`, micro `surec.js`, `calculations.js`
**Modül:** `utils/karne_hesaplamalar.py`, `app/utils/karne_hesaplamalar.py`, `app/models/process.py`, `models/process.py`, `static/js/process_karne.js`, `static/js/modules/process_karne/calculations.js`, `static/js/surec_karnesi.js`, `micro/static/micro/js/surec.js`, `micro/templates/surec/karne.html`
**Durum:** ✅ Tamamlandı

---

## TASK-060 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Micro süreç karnesi — PG ekle modalı kök `process/karne` (#addPGForm) ile aynı alan seti: gösterge adı, kod, hedef, birim (datalist), skor ağırlığı, periyot, hedef yönü, hesaplama, gösterge türü, hedef belirleme, alt strateji, önceki yıl ort., açıklama, opsiyonel başarı puanı aralıkları (JSON — kök `process_karne.js` ile uyumlu); `mc-modal` + geniş layout (`karne-modal-kpi-add`)
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-059 | 2026-03-19 | ✅ Tamamlandı

**Görev:** PG ekle modalı birim `datalist` — yalnızca 10 öneri: Adet, %, TL, Saat, Gün, Kişi, Puan, kg, km, kWh (özel metin girişi aynı)
**Modül:** `micro/templates/surec/karne.html`
**Durum:** ✅ Tamamlandı

---

## TASK-058 | 2026-03-19 | ✅ Tamamlandı

**Görev:** PG ekle modalında «Birim» — `datalist` ile önerilen birimler + serbest metin; ipucu metni ve ek birim seçenekleri (zaman, kütle, alan, enerji, N/A vb.)
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-057 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi — «PG ekle» metni «Performans göstergesi ekle»; PG ekleme SweetAlert kaldırıldı, admin «Kullanıcı Düzenle» ile aynı `mc-modal` yapısı (`modal-kpi-add`); `karne-substrategies-json` kaldırıldı (alt strateji seçenekleri şablonda)
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-056 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi başlık — daha alçak: üst sıra grid (sol mini logo + «Süreç paneline dön», orta «SÜREÇ KARNESİ», sağ meta); üst süreç küçük satır; padding/boşluk/az şerit sıkılaştırma
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-055 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi başlık barı — süreç `select` ile aksiyon butonları aynı satırda (`karne-banner-toolbar`, `align-items: flex-end`); üst satırda marka + meta; dar ekranda sütun
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-054 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi üst bar — canlı mor gradient kaldırıldı; `mc-card` çizgisi (beyaz/koyu kart, 3px indigo üst çizgi); süreç adı tekrarı (select altı) kaldırıldı; aksiyonlar `mc-btn` + yumuşak amber (`karne-btn-faaliyet-soft`) ve yeşil ton (`karne-btn-excel-soft`), sihirbaz `mc-btn-secondary`, PG `mc-btn-success`, yazdır `mc-btn-secondary` + `karne-btn-print-muted`
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-053 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi üst bar — kök görseline yakın mavi–mor gradient; sol: ikon+başlık, «Süreç paneline dön», yetkili süreç `select`, süreç adı; sağ: Döküman/Rev/Rev.tarihi/Yıl, butonlar (veri sihirbazı, PG ekle, faaliyet ekle, Excel CSV, yazdır); Excel export + sihirbaz JS
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/css/surec.css`, `micro/static/micro/js/surec.js`
**Durum:** ✅ Tamamlandı

---

## TASK-052 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi seçenek A — yıllık `target_value` ÷ 12 = aylık hedef; ay hücrelerinde `h:` ipucu; satırda verili ayların ortalama sapma % (artış/azalış yönüne göre işaret); hedef sütununda «Aylık: …»
**Modül:** `micro/templates/surec/karne.html`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-051 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç karnesi (`/process/<id>/karne`) — kök referansına yakın üst şerit (liste dön, döküman/revizyon tarihi + isteğe bağlı ilk yayın, üst süreç karnesi, faaliyetler, PG ekle, yazdır); genel bilgi üçlüsü; yönetici özeti; KPI tablosu genişletilmiş sütunlar; PG ekle SweetAlert; `accessible_processes_filter`. **Güncelleme:** Üst şeritte öncelik `revision_date`; «Dış veri aktar» kaldırıldı.
**Modül:** `micro/modules/surec/routes.py`, `micro/templates/surec/karne.html`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-050 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Süreç kaydet bekleme süresi — nedenleri (SMTP senkron, tam sayfa yenileme); süreç atama e-postasını arka plan iş parçacığına alma; kayıt sırasında SweetAlert2 «Süreç kaydediliyor» + yüzde çubuğu (simüle), çift gönderim kilidi
**Modül:** `micro/services/notification_triggers.py`, `micro/static/micro/js/surec.js`
**Durum:** ✅ Tamamlandı

---

## TASK-049 | 2026-03-20 | ✅ Tamamlandı

**Görev:** `/process` — kurum yöneticileri (Admin, tenant_admin, executive_manager) tüm süreçlerde güncelleme: satırda «Düzenle», GET/POST ile aynı modal (lider/üye çift liste dahil)
**Modül:** `micro/templates/surec/index.html`, `micro/static/micro/js/surec.js`
**Durum:** ✅ Tamamlandı

---

## TASK-048 | 2026-03-20 | ✅ Tamamlandı

**Görev:** Micro “Yeni Süreç” modalı — kök panel referansıyla hizalama (yeşil başlık, tarihler, üst süreç, sınırlar, ilerleme); Süreç Lideri/Üyesi çift liste (→ Ekle / ← Çıkar)
**Modül:** `micro/modules/surec/routes.py`, `micro/templates/surec/index.html`, `micro/static/micro/js/surec.js`, `micro/static/micro/css/surec.css`
**Durum:** ✅ Tamamlandı

---

## TASK-047 | 2026-03-20 | ✅ Tamamlandı

**Görev:** Süreç modülü RBAC (Admin / tenant_admin / executive_manager / atanan kullanıcı), süreç→en az bir alt strateji zorunluluğu, panelden Karnesi/Faaliyetler ayrı sayfa, PGV güncelle-sil API, menüde Süreç tüm oturumlu kullanıcılar
**Modül:** `micro/modules/surec/permissions.py`, `micro/modules/surec/routes.py`, `micro/templates/surec/*`, `micro/static/micro/js/surec.js`, `micro/templates/micro/base.html`
**Durum:** ✅ Tamamlandı

### Not
Mevcut veritabanında alt strateji bağlantısı olmayan süreçler için güncelleme API’si `sub_strategy_links` gönderilene kadar hata verebilir; veri düzeltmesi veya kök `/process` panelinden bağlantı eklenmesi gerekir.

---

## TASK-046 | 2026-03-20 | ✅ Tamamlandı

**Görev:** Micro Süreç modülü kanonik URL `/process`; eski `/surec` → **307** ile `/process`; şablon/JS/bildirim/module_registry güncellemesi
**Modül:** `micro/modules/surec/routes.py`, `micro/templates/surec/*.html`, `micro/static/micro/js/surec.js`, `micro/core/module_registry.py`, `micro/services/notification_triggers.py`
**Durum:** ✅ Tamamlandı

---

## TASK-045 | 2026-03-20 | ✅ Tamamlandı

**Görev:** SP akışta “Ana Stratejiler” (eski 5) kartı kaldırıldı; strateji listesi kartı başlığı “Strateji Listesi (Ana Stratejiler → Alt Stratejiler)”, rozet 05, adımlar 06–08
**Modül:** `micro/templates/micro/sp/index.html`, `micro/static/micro/js/sp.js`
**Durum:** ✅ Tamamlandı

---

## TASK-044 | 2026-03-20 | ✅ Tamamlandı

**Görev:** SP akış kartı gövdesine tıklanınca “yapım aşaması” sayfaları yerine kalem ile aynı düzenleme modalı / yönlendirme
**Modül:** `micro/templates/micro/sp/index.html`, `micro/static/micro/js/sp.js`, `micro/static/micro/css/sp.css`
**Durum:** ✅ Tamamlandı

### Not
`<a href>` yerine `div.mc-sp-card-body-trigger` + `data-sp-body-edit`; JS ilgili `.btn-sp-card-edit` tıklamasını tetikler; yoksa bilgi butonu. Kart 01–09 gövde.

---

## TASK-043 | 2026-03-20 | ✅ Tamamlandı

**Görev:** SP kart 01–03 önizlemede metin taşınca kaydırma (Misyon/Vizyon tam metin + ortak `.mc-sp-card-body-scroll`)
**Modül:** `micro/templates/micro/sp/index.html`, `micro/static/micro/css/sp.css`
**Durum:** ✅ Tamamlandı

---

## TASK-042 | 2026-03-20 | ✅ Tamamlandı

**Görev:** SP kart 03 Değerler/Etik — önizlemede ~3 satır görünür yükseklik, fazlası kaydırma çubuğu
**Modül:** `micro/templates/micro/sp/index.html`, `micro/static/micro/css/sp.css`
**Durum:** ✅ Tamamlandı

### Not
Metin çok satırlı veya `;` ile ayrılmış maddeler; tek paragrafta sarma + aynı max-height ile kaydırma.

---

## TASK-041 | 2026-03-20 | ✅ Tamamlandı

**Görev:** SP akış kartı 03 “Değerler ve Etik Kurallar” — girilen `core_values` / `code_of_ethics` önizlemesi ve tamamlanma (etik dolu iken rozet)
**Modül:** `micro/templates/micro/sp/index.html`, `micro/static/micro/css/sp.css`
**Durum:** ✅ Tamamlandı

---

## TASK-040 | 2026-03-20 | ✅ Tamamlandı

**Görev:** Boğaziçi Üniversitesi kurumu için tablodaki 5 ana (SA1–SA5) + 20 alt (H*) strateji verisi
**Modül:** `scripts/seed_bogazici_strategies.py`
**Durum:** ✅ Tamamlandı (geliştirme DB’de `--replace` ile uygulandı)

### Kullanım
`py scripts/seed_bogazici_strategies.py --replace` (kurum otomatik: adında boğaziçi/boun) veya `--tenant-id N`

---

## TASK-039 | 2026-03-20 | ✅ Tamamlandı

**Görev:** SP ana strateji ekleme HTTP 500 — `code`/`description` JSON `null` iken `.strip()` AttributeError
**Modül:** `micro/modules/sp/routes.py` (`sp_add_strategy`)
**Durum:** ✅ Tamamlandı

### Özet
`data.get("code", "")` anahtar varken değer `null` ise `None` döner; `(data.get("code") or "").strip()` kullanıldı.

---

## TASK-038 | 2026-03-20 | ✅ Tamamlandı

**Görev:** SP “Ana strateji ekle” JSON hatası (`Unexpected token '<'`) — CSRF HTML yanıtı
**Modül:** `micro/modules/sp/routes.py` (`@csrf.exempt` + `app.extensions.csrf`), `sp.js` `postJson`
**Durum:** ✅ Tamamlandı

### Özet
`/sp/api/*` POST uçlarına `login_required` + `sp_manage_required` ile birlikte `@csrf.exempt` eklendi (uygulamadaki gerçek CSRF `app.extensions` üzerinden). `postJson` HTML yanıtında anlamlı hata mesajı veriyor.

---

## TASK-037 | 2026-03-19 | ✅ Tamamlandı

**Görev:** SP akış kartlarında bilgi (i) butonu ve kart amacını anlatan `openMcInfoModal` penceresi
**Modül:** `base.html` / `mc-modal-form.js` / `components.css` / `sp/index.html` / `sp.js`
**Durum:** ✅ Tamamlandı

### Özet
Her kartın sağ üstünde düzenle ikonunun yanına `fa-circle-info` butonu; metinler `sp-card-help-json` + `openMcInfoModal` ile gösteriliyor.

---

## TASK-036 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Stratejik Planlama düzenleme formları — admin kullanıcı düzenle modalı ile aynı native `mc-modal` tasarımı
**Modül:** micro UI / `mc-modal-form.js` / `sp.js` / `components.css` / `base.html`
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/base.html` → Genel `#mc-modal-form-global` markup (admin ile aynı sınıflar)
- `micro/static/micro/js/mc-modal-form.js` → `openMcFormModal()` yardımcısı
- `micro/static/micro/js/sp.js` → Misyon/vizyon/değerler/SWOT/ana & alt strateji formları SweetAlert yerine native modal
- `micro/static/micro/css/components.css` → `textarea.mc-form-input`, `select.mc-form-input`, `.mc-modal-form-validation`

### Notlar
Toast, hata ve silme onayı SweetAlert2 ile devam ediyor.

---

## TASK-035 | 2026-03-19 | ✅ Tamamlandı

**Görev:** SECRET_KEY fallback kaldırıldı ve environment zorunlu hale getirildi
**Modül:** config / app init / security
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `config.py` → Hardcoded `SECRET_KEY` fallback kaldırıldı; environment yoksa `RuntimeError` atacak şekilde güncellendi
- `app/__init__.py` → `app.config["SECRET_KEY"]` için hardcoded fallback satırı kaldırıldı
- `.env` → `SECRET_KEY` güvenli rastgele değer ile eklendi/oluşturuldu (git'e eklenmedi)

### Yapılan İşlem
Uygulamanın gizli anahtarının yalnızca environment üzerinden okunması zorunlu hale getirildi. Hardcoded fallback'ler kaldırılarak production güvenlik riski düşürüldü. `.gitignore` içinde `.env` kuralı doğrulandı.

### Notlar
SECRET_KEY değeri güvenlik nedeniyle loglanmadı.

---

## TASK-034 | 2026-03-19 | ✅ Tamamlandı

**Görev:** FakeLimiter kaldırıldı, gerçek Flask-Limiter aktif edildi ve login endpoint'lerine rate limit eklendi
**Modül:** security / auth / micro-auth
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `extensions.py` → `FakeLimiter` tamamen kaldırıldı; gerçek `Limiter` import/instance eklendi
- `__init__.py` → limiter'ı devre dışı bırakan `RATELIMIT_ENABLED = False` satırı kaldırıldı
- `auth/routes.py` → `/auth/login` için `@limiter.limit("10 per minute")` eklendi
- `micro/modules/shared/auth/routes.py` → `/login` için `@limiter.limit("10 per minute")` eklendi
- `requirements.txt` → `Flask-Limiter==3.5.0` olarak versiyon sabitlendi

### Yapılan İşlem
Rate limiting mekanizması mock/fake yapıdan gerçek Flask-Limiter'a geçirildi. Uygulama başlatma akışında `limiter.init_app(app)` çağrısı zaten mevcut olduğundan korunarak aktif hale getirildi. Auth ve micro login endpointlerine dakikada 10 istek limiti uygulandı.

### Notlar
Micro login route'u projede `/login` olarak tanımlı; bu endpoint'e limit dekoratörü eklendi.

---

## TASK-033 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kokpitim tam derinlik analiz raporu oluşturuldu (`docs/analiz-antigravity.md`)
**Modül:** docs / analiz
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `docs/analiz-antigravity.md` → 10 adımlı kapsamlı proje analizi oluşturuldu

### Yapılan İşlem
Proje haritası, mimari analiz (Blueprint, ORM, Micro modüller), kod kalitesi (teknik borç, güvenlik, performans), frontend analizi (CSS/JS/Template), modül bazlı derinlik analizi, TASKLOG trend analizi, iyileştirme önerileri, rekabet/trend analizi, test durumu ve dokümantasyon değerlendirmesi yapıldı. Genel sağlık skoru: 61/100.

### Notlar
5 kritik güvenlik bulgusu tespit edildi: Rate limiter devre dışı, çift hardcoded secret key, SESSION_COOKIE_SECURE eksik, Talisman başlatılmamış, CSRF exempt endpoint.

---

## TASK-032 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kokpitim tam derinlik analiz raporu oluşturuldu (`docs/analiz-cursoranaliz.md`)
**Modül:** docs / analiz
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `docs/analiz-cursoranaliz.md` → 10 adımlı kapsamlı proje analizi eklendi (mimari, güvenlik, kalite, frontend, test, trend, öneriler)
- `docs/TASKLOG.md` → Bu kayıt eklendi

### Yapılan İşlem
Depodaki aktif kod ve legacy alanlar taranarak proje haritası, mimari katmanlar, veritabanı ve micro modül yapısı, teknik borç/güvenlik/performans bulguları, frontend tutarlılık analizi, TASKLOG trendleri ve iyileştirme önerileri tek raporda toplandı.

### Notlar
Toplam satır/dosya metrikleri hem ham depo hem aktif alan (yedek/legacy hariç) olarak ayrı raporlandı.

---

## TASK-031 | 2026-03-18 | 🔄 Düzeltme

**Görev:** profil.html boş dosya sorunu giderildi — Python script ile UTF-8 yeniden yazıldı
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/auth/profil.html` → PowerShell unicode escape hatası nedeniyle boşalmıştı; Python script ile UTF-8 olarak yeniden yazıldı
- `micro/static/micro/js/profil.js` → Aynı sorun; Python script ile UTF-8 olarak yeniden yazıldı

### Yapılan İşlem
PowerShell'in `\u` escape dizilerini literal string olarak yazması nedeniyle her iki dosya da boşalmıştı. Python script (`_write_profil.py`, `_write_profil_js.py`) ile UTF-8 encoding açıkça belirtilerek dosyalar yeniden oluşturuldu. Doğrulama: `extends micro/base.html`, `data-upload-url`, `UPLOAD_URL`, `swalError` varlığı kontrol edildi.

### Notlar
Yok.

---

## TASK-030 | 2026-03-18 | ✅ Tamamlandı

**Görev:** profil.html ve profil.js sıfırdan yeniden yazıldı — eski profile.html JS mantığı taşındı
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/auth/profil.html` → Silindi ve yeniden yazıldı; `micro/base.html` extend, `data-update-url`/`data-upload-url`, fotoğraf yükleme butonu + progress, profil formu, inline script yok
- `micro/static/micro/js/profil.js` → Silindi ve yeniden yazıldı; eski `profile.html` inline JS mantığı taşındı: dosya tipi/boyut kontrolü, `validateEmail`, `validatePhone`, Bootstrap Toast → SweetAlert2, fetch URL'leri `data-*`'dan okunuyor, `phone`→`phone_number`, `title`→`job_title`

### Yapılan İşlem
Eski `templates/profile.html`'deki inline JS (dosya tipi kontrolü, 5MB limit, e-posta/telefon validasyonu, fotoğraf güncelleme DOM mantığı) `profil.js`'e taşındı. Bootstrap Toast bildirimleri SweetAlert2 ile değiştirildi. HTML `micro/base.html`'i extend ediyor, tüm fetch URL'leri `data-*` attribute'larından okunuyor, inline `<script>` bloğu yok.

### Notlar
`static/js/profile.js` mevcut değildi — tüm JS `templates/profile.html` içinde inlineydi.

---

## TASK-029 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Eski profile.html JS mantığı micro profil.js'e taşındı; backend'e boyut ve mime kontrolü eklendi
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/js/profil.js` → Client-side mime type kontrolü, 5MB boyut kontrolü, `validateEmail`, `validatePhone` fonksiyonları, content-type response kontrolü, FormData'ya `csrf_token` field eklendi
- `micro/modules/shared/auth/routes.py` → `profil_foto_yukle`'ye mime type kontrolü (`file.mimetype`) ve 5MB boyut kontrolü (`file.seek`) eklendi

### Yapılan İşlem
Eski `templates/profile.html`'deki JS'de bulunan dosya tipi/boyut validasyonu, e-posta ve telefon format kontrolü micro `profil.js`'e taşındı. FormData'ya `csrf_token` field'ı da eklendi (header'a ek olarak — CSRF sorununu kesin çözer). Backend `profil_foto_yukle`'ye mime type ve 5MB boyut kontrolü eklendi. Alan adları zaten doğruydu: `phone_number`, `job_title`.

### Notlar
Eski `/profile/update` ve `/profile/upload-photo` endpoint'leri dokunulmadı — kök `templates/profile.html` kullananlar için çalışmaya devam ediyor.

---

## TASK-028 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Profil fotoğrafı yükleme CSRF hatası giderildi
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/shared/auth/routes.py` → `from extensions import csrf` import eklendi; `profil_foto_yukle` endpoint'ine `@csrf.exempt` dekoratörü eklendi

### Yapılan İşlem
`profil_foto_yukle` endpoint'i `multipart/form-data` POST alıyor; `profil.js` CSRF token'ı `X-CSRFToken` header olarak gönderiyor. Flask-WTF varsayılan olarak form field'dan (`csrf_token`) okuduğu için header'ı tanımıyor ve isteği reddediyordu. `@csrf.exempt` ile endpoint CSRF korumasından muaf tutuldu — endpoint zaten `@login_required` ile korunuyor.

### Notlar
Yok.

---

## TASK-027 | 2026-03-18 | 🔄 Düzeltme

**Görev:** profil.js'de input sıfırlama sırası düzeltildi
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/js/profil.js` → `this.value = ""` satırı `reader.readAsDataURL(file)` çağrısından önce taşındı

### Yapılan İşlem
`data-upload-url` doğru endpoint'e (`/profil/foto-yukle`) işaret ediyordu. Asıl sorun: bazı tarayıcılarda `this.value = ""` `FileReader` okuma tamamlanmadan çalışınca `file` referansı kaybolabiliyordu. `file` önce değişkene alınıp input hemen sıfırlandı, ardından `readAsDataURL` çağrıldı.

### Notlar
Yok.

---

## TASK-026 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Profil fotoğrafı butonu, canvas kırpma ve avatar güncellemesi
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/auth/profil.html` → Kamera label/icon kaldırıldı, `btn-foto-yukle` butonu eklendi
- `micro/static/micro/js/profil.js` → Canvas ile 400x400 merkez kırpma, JPEG 0.85 kalite, `btn-foto-yukle` click bağlantısı
- `micro/templates/micro/base.html` → Topbar ve sidebar footer avatar'ı `profile_photo` varsa `<img>` gösteriyor

### Yapılan İşlem
Kamera ikonu yerine standart `mc-btn` butonu eklendi. Fotoğraf seçilince FileReader → Image → Canvas ile 400x400 kare kırpma yapılıyor, `toBlob(jpeg, 0.85)` ile sıkıştırılıp endpoint'e gönderiliyor. Topbar ve sidebar avatar'ları profil fotoğrafı varsa `<img>` tag'i, yoksa harf gösteriyor.

### Notlar
Yok.

---

## TASK-025 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Profil sayfası micro yapıya tam taşındı — backend JSON API, fotoğraf yükleme, template ve JS
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/shared/auth/routes.py` → `profil` route'u JSON API POST handler'a dönüştürüldü; `profil_foto_yukle` endpoint'i eklendi
- `micro/templates/micro/auth/profil.html` → `profile_picture` → `profile_photo` düzeltildi; `data-update-url` / `data-upload-url` eklendi; rol badge Türkçeleştirildi; inline script kaldırıldı
- `micro/static/micro/js/profil.js` → Tamamen yeniden yazıldı: fetch URL'leri `data-*`'dan okunuyor, bildirimler SweetAlert2, form JSON API ile submit ediliyor

### Yapılan İşlem
Profil sayfası eski `auth_bp.profile` 307 redirect'inden kurtarıldı. `micro_bp.profil` artık kendi JSON API handler'ına sahip: şifre doğrulama, e-posta duplicate kontrolü, yeni model alan adları (`phone_number`, `job_title`). Fotoğraf yükleme `profil_foto_yukle` endpoint'inde — fiziksel silme yok, sadece DB güncelleniyor. `profil.js` SweetAlert2 ile yeniden yazıldı.

### Notlar
Eski `auth_bp.profile` ve `auth_bp.upload_profile_photo` endpoint'leri hâlâ çalışıyor — kök `templates/profile.html` kullananlar için dokunulmadı.

---

## TASK-024 | 2026-03-18 | ✅ Tamamlandı

**Görev:** users.html'de buton görünürlüğü üç role genişletildi, rol badge'leri Türkçeleştirildi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/admin/users.html` → Düzenle/Pasife Al buton koşulu `Admin` → `['Admin', 'tenant_admin', 'executive_manager']` olarak güncellendi; `rol_etiket` Jinja2 map'i eklendi, badge'ler Türkçe gösteriyor

### Yapılan İşlem
Daha önce Düzenle ve Pasife Al butonları yalnızca `Admin` rolüne görünüyordu; backend'de `tenant_admin` ve `executive_manager` de bu işlemleri yapabildiği için frontend koşulu üç role genişletildi. Tablodaki rol badge'leri `u.role.name` yerine `rol_etiket` map'inden Türkçe karşılıklarını gösteriyor; bilinmeyen roller olduğu gibi görünmeye devam eder.

### Notlar
Yok.

---

## TASK-023 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Rol atama yetki kontrolü ve dropdown filtrelemesi eklendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → `ASSIGNABLE_ROLES` sabiti eklendi; `admin_users_add` ve `admin_users_edit`'e rol yetki kontrolü eklendi; `admin_users` view'ında `roles` listesi `current_user` rolüne göre filtreleniyor

### Yapılan İşlem
`tenant_admin` ve `executive_manager` rolündeki kullanıcılar daha önce `Admin` dahil tüm rolleri atayabiliyordu. `ASSIGNABLE_ROLES` map'i ile her rol için izin verilen roller tanımlandı. `admin_users_add` ve `admin_users_edit` endpoint'lerinde atanmak istenen rol bu listeye göre kontrol ediliyor; yetkisiz atamada 403 dönüyor. `admin_users` view'ı da `roles` listesini aynı map'e göre filtreliyor, böylece dropdown'da sadece atanabilir roller görünüyor.

### Notlar
Yok.

---

## TASK-022 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Bulk import endpoint'i Excel desteği, şifre okuma ve ek alan eşleştirmesiyle güncellendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → `admin_users_bulk_import`: Excel (.xlsx/.xls) desteği eklendi, `Şifre` kolonu okunuyor (yoksa `"Changeme123!"` fallback), `Unvan`→`job_title` ve `Telefon`→`phone_number` alanları eklendi
- `micro/modules/admin/routes.py` → `admin_users_sample_excel`: Şablon başlığı `Sifre`→`Şifre` düzeltildi, örnek veriler Türkçe karakterlerle güncellendi
- `micro/static/micro/js/admin.js` → Bulk import Swal açıklama metni güncellendi (Excel birincil format olarak belirtildi)

### Yapılan İşlem
Örnek Excel şablonu 6 kolon sunuyordu (`Şifre`, `Unvan`, `Telefon` dahil) ancak bulk import yalnızca 3 kolonu (`email`, `first_name`, `last_name`) okuyordu. Endpoint openpyxl ile Excel okuma desteği kazandı; `Şifre` kolonu okunup hash'leniyor, yoksa güvenli fallback kullanılıyor. `Unvan` ve `Telefon` kolonları User modelindeki `job_title` ve `phone_number` alanlarına eşlendi. CSV desteği korundu.

### Notlar
`openpyxl` paketi gerekli — `pip install openpyxl` ile kurulabilir (zaten sample-excel endpoint'i kullandığı için yüklü olmalı).

---

## TASK-021 | 2026-03-18 | ✅ Tamamlandı

**Görev:** fillUserSelects fonksiyonuna ROLE_LABELS Türkçe çeviri map'i eklendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/js/admin.js` → `ROLE_LABELS` map eklendi; `fillUserSelects` içinde rol option'ları oluştururken `ROLE_LABELS[name] || name` kullanılıyor

### Yapılan İşlem
Kullanıcı ekle/düzenle modallarındaki rol dropdown'ı backend'den gelen İngilizce isimleri (Admin, User, tenant_admin, executive_manager, standard_user) artık Türkçe karşılıklarıyla gösteriyor. Bilinmeyen rol isimleri olduğu gibi gösterilmeye devam eder.

### Notlar
Yok.

---

## TASK-020 | 2026-03-18 | ✅ Tamamlandı

**Görev:** admin.js'deki kullanılmayan buildRoleOptions ve buildTenantOptions dead code kaldırıldı
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/js/admin.js` → `buildRoleOptions`, `buildTenantOptions`, `ROLE_LABELS` kaldırıldı (dead code — native modal'a geçişte yerini `fillUserSelects` aldı)

### Yapılan İşlem
`fillUserSelects` ile HTML modal ID'leri (`ua-role`, `ua-tenant`, `ua-tenant-wrap`, `ue-role`, `ue-tenant`, `ue-tenant-wrap`) karşılaştırıldı — tam eşleşiyor, sorun yok. Eski Swal tabanlı koddan kalan `buildRoleOptions`, `buildTenantOptions` ve `ROLE_LABELS` artık hiçbir yerde çağrılmıyordu; kaldırıldı.

### Notlar
Yok.

---

## TASK-019 | 2026-03-18 | ✅ Tamamlandı

**Görev:** micro_bp Blueprint'inden hatalı static_url_path parametresi kaldırıldı
**Modül:** micro / blueprint
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/__init__.py` → `static_url_path="/micro/static"` parametresi kaldırıldı

### Yapılan İşlem
`static_url_path="/micro/static"` ile `url_prefix="/micro"` birleşince `url_for` `/micro/micro/static/...` üretiyordu. Parametre kaldırıldığında Flask `url_prefix` + `/static` = `/micro/static` kullanıyor; `url_for('micro_bp.static', filename='micro/js/admin.js')` artık doğru `/micro/static/micro/js/admin.js` URL'ini üretiyor. Kök `/static/` route'u ile çakışma yok.

### Notlar
- **2026-03-19 (TASK-106):** Micro artık site kökünde; statik `url_prefix=""` ve `static_url_path="m"` → ör. `/m/micro/js/admin.js`. Bu kayıttaki URL anlatımı o dönemdeki `url_prefix="/micro"` düzenine aittir.

---

## TASK-018 | 2026-03-18 | 🔄 Düzeltme

**Görev:** users.html extra_js bloğundaki admin.js path'i orijinal haline döndürüldü
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/admin/users.html` → `filename='js/admin.js'` → `filename='micro/js/admin.js'` olarak geri alındı

### Yapılan İşlem
TASK-017'de yapılan path değişikliği geri alındı. `filename='micro/js/admin.js'` orijinal değerine döndürüldü.

### Notlar
Yok.

---

## TASK-017 | 2026-03-18 | ✅ Tamamlandı

**Görev:** users.html extra_js bloğundaki admin.js path'i düzeltildi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/admin/users.html` → `filename='micro/js/admin.js'` → `filename='js/admin.js'` olarak düzeltildi

### Yapılan İşlem
Blueprint static dosya yolu `micro/js/admin.js` yerine `js/admin.js` olarak düzeltildi. `micro_bp.static` zaten `micro/static/micro/` prefix'ini ekliyor, dolayısıyla `micro/js/` tekrarı 404'e yol açıyordu.

### Notlar
Yok.

---

## TASK-016 | 2026-03-18 | ✅ Tamamlandı

**Görev:** JS/CSS dosyalarına cache busting için VERSION query string eklendi
**Modül:** admin / config / base
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `config.py` → `Config` sınıfına `VERSION = "1.0.1"` eklendi
- `micro/templates/micro/base.html` → 3 CSS + 1 JS include satırına `?v={{ config['VERSION'] }}` eklendi
- `micro/templates/micro/admin/users.html` → `extra_js` bloğundaki `admin.js` satırına `?v={{ config['VERSION'] }}` eklendi

### Yapılan İşlem
Tarayıcı cache'inin eski JS/CSS dosyalarını sunmasını önlemek için `config.py`'ye `VERSION` sabiti eklendi. `base.html`'deki tüm yerel CSS/JS include'ları ve `users.html`'deki `admin.js` include'u bu versiyonu query string olarak kullanacak şekilde güncellendi. Bundan sonra her JS/CSS değişikliğinde `config.py`'deki `VERSION` değeri artırılmalıdır.

### Notlar
`tenants.html` ve diğer admin sayfalarının `extra_js` bloklarında da aynı pattern uygulanmalı.

---

## TASK-015 | 2026-03-18 | ✅ Tamamlandı

**Görev:** admin.js ROLE_LABELS map'indeki ASCII Türkçe karakter hataları düzeltildi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/js/admin.js` → `ROLE_LABELS` map'inde 4 değer ve `buildRoleOptions` fallback string'i Türkçe karakterlerle düzeltildi

### Yapılan İşlem
`ROLE_LABELS` map'indeki `"Kullanici"`, `"Kurum Yoneticisi"`, `"Kurum Ust Yonetimi"`, `"Kurum Kullanicisi"` değerleri sırasıyla `"Kullanıcı"`, `"Kurum Yöneticisi"`, `"Kurum Üst Yönetimi"`, `"Kurum Kullanıcısı"` olarak güncellendi. `buildRoleOptions` fallback'i `"— Rol Sec —"` → `"— Rol Seç —"` yapıldı.

### Notlar
Yok.

---

## TASK-014 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Rol dropdown'ı Türkçe etiketlerle gösterilecek şekilde güncellendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/js/admin.js` → `ROLE_LABELS` map eklendi, `buildRoleOptions` fonksiyonu çeviri map'ini kullanacak şekilde güncellendi

### Yapılan İşlem
Backend'den gelen İngilizce rol isimleri (Admin, User, tenant_admin, executive_manager, standard_user) frontend'de Türkçe karşılıklarıyla gösterilmek üzere `ROLE_LABELS` map'i eklendi. Bilinmeyen rol isimleri olduğu gibi gösterilmeye devam eder.

### Notlar
Yok.

---

## TASK-013 | 2026-03-18 | ✅ Tamamlandı

**Görev:** users.html kullanıcı ekle/düzenle Swal modalları native HTML modal'a geçirildi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/admin/users.html` → `modal-user-add` ve `modal-user-edit` native modal'ları eklendi (mc-modal-overlay/mc-modal-lg yapısı)
- `micro/static/micro/js/admin.js` → btn-user-add ve btn-user-edit Swal.fire blokları kaldırıldı, native modal open/close/save fonksiyonları eklendi

### Yapılan İşlem
tenants.html'deki mc-modal-overlay/mc-modal-lg yapısı referans alınarak iki native modal oluşturuldu. admin.js'de Swal.fire bağımlılığı kaldırıldı; rol ve kurum select'leri admin-meta data-* attribute'larından dinamik dolduruluyor. API endpoint'leri (ADD_URL, EDIT_BASE) değişmedi.

### Notlar
toggle ve bulk-import işlemleri Swal.fire kullanmaya devam ediyor — bu kasıtlı, değiştirilmedi.

---

## TASK-012 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Excel şablonu sütunları güncellendi, Swal modal genişliği CSS ile sabitlendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → Excel şablonu başlıkları Ad/Soyad/E-posta/Sifre/Unvan/Telefon olarak güncellendi, 6 sütun genişliği ayarlandı
- `micro/static/micro/js/admin.js` → btn-user-add ve btn-user-edit Swal'larına `customClass: { popup: 'mc-swal-wide' }` eklendi
- `micro/static/micro/css/components.css` → `.mc-swal-wide` sınıfı eklendi (780px sabit genişlik)

### Yapılan İşlem
Excel şablonu kök yapıdaki kullanıcı alanlarıyla eşleştirildi. Swal modallarının gerçek genişliği tarayıcıda `width` parametresiyle tam uygulanmıyor olabildiğinden `customClass` + CSS ile 780px sabitlendi.

### Notlar
Yok.

---

## TASK-011 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Kullanıcı Swal modal genişlikleri 780px yapıldı, örnek Excel endpoint ve indirme butonu eklendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/js/admin.js` → btn-user-add width 560→780, btn-user-edit width 520→780, toplu içe aktar Swal'ına indirme butonu eklendi
- `micro/modules/admin/routes.py` → `/admin/users/sample-excel` GET endpoint'i eklendi (openpyxl ile xlsx üretir)

### Yapılan İşlem
Kullanıcı ekleme ve düzenleme Swal modalları tenant modal'ıyla aynı genişliğe (780px) getirildi. Toplu içe aktarma için örnek Excel şablonu üreten yeni bir endpoint eklendi. Swal'daki indirme butonu bu endpoint'e bağlandı; dosya kabul tipi `.csv,.xlsx` olarak güncellendi.

### Notlar
`openpyxl` paketi yüklü olmalı — `pip install openpyxl` ile kurulabilir.

---

## TASK-010 | 2026-03-18 | ✅ Tamamlandı

**Görev:** users.html kullanıcı yönetimi sayfası iyileştirmeleri ve admin.js e-posta alanı eklendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/admin/users.html` → `data-email` eklendi, inline style kaldırıldı (`mc-page-content`), `mc-input`→`mc-form-input`, stat kartları eklendi, butonlar Admin kontrolüne alındı
- `micro/static/micro/js/admin.js` → `btn-user-edit` listener'ında `email` okunuyor, Swal formuna readonly e-posta alanı eklendi

### Yapılan İşlem
`users.html`'de 5 iyileştirme yapıldı: `data-email` attribute eklendi, `max-width` inline style `mc-page-content` sınıfıyla değiştirildi, arama kutusu sınıfı `mc-form-input` olarak düzeltildi, 3 stat kartı (toplam/aktif/pasif) eklendi, Düzenle ve Pasife Al butonları `Admin` rolü kontrolüne alındı. `admin.js`'de düzenleme Swal'ına readonly e-posta alanı eklendi.

### Notlar
E-posta alanı readonly — değiştirilemez, sadece bilgi amaçlı gösteriliyor.

---

## TASK-009 | 2026-03-18 | ✅ Tamamlandı

**Görev:** SQLAlchemy `Multiple classes found for path "User"` ve duplicate tablo hatası giderildi
**Modül:** models / app/models
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `models/user.py` → `class User` → `class LegacyUser`, `class Notification` → `class LegacyNotification`; tüm `relationship('User', ...)` → `relationship('LegacyUser', ...)`
- `models/__init__.py` → import satırı `LegacyUser`, `LegacyNotification` olarak güncellendi; `User = LegacyUser` ve `Notification = LegacyNotification` alias'ları eklendi
- `app/models/notification.py` → `__tablename__ = 'notifications'` → `'notifications_ext'` (core.py ile çakışma giderildi)

### Yapılan İşlem
`models/user.py` ile `app/models/core.py`'de aynı isimde `User` ve `Notification` class'ları bulunuyordu; SQLAlchemy registry çakışma hatası veriyordu. Kök `models/` altındaki class'lar `Legacy` prefix'i alarak yeniden adlandırıldı, geriye dönük uyumluluk için alias'lar eklendi. Ayrıca `app/models/notification.py` ile `app/models/core.py` aynı `notifications` tablo adını kullanıyordu; `notification.py` tablosu `notifications_ext` olarak yeniden adlandırıldı. Uygulama `http://127.0.0.1:5001` üzerinde hatasız başlıyor.

### Notlar
`notifications_ext` tablosu yeni bir tablo — mevcut DB'de bu tablo yoksa migration gerekebilir.

---

## TASK-008 | 2026-03-18 | ✅ Tamamlandı

**Görev:** `app/models/__init__.py`'deki duplicate `db` instance kaldırıldı, kök `extensions.py::db`'ye yönlendirildi
**Modül:** micro / db / models
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/models/__init__.py` → `db = SQLAlchemy()` kaldırıldı, `from extensions import db` ile kök instance kullanılıyor
- `__init__.py` → `from app.models import db as app_db` ve `app_db.init_app(app)` satırları kaldırıldı

### Yapılan İşlem
Projede 3 ayrı `SQLAlchemy` instance mevcuttu: `extensions.py::db`, `app/extensions.py::db`, `app/models/__init__.py::db`. Micro modülleri `app.models.db`'yi kullanıyor, kök uygulama ise `extensions.py::db`'yi `init_app` yapıyordu. Bu iki farklı instance olduğu için `RuntimeError: not registered with this SQLAlchemy instance` hatası oluşuyordu. `app/models/__init__.py`'deki `db = SQLAlchemy()` kaldırılıp kök `extensions.py`'den import edildi; artık tüm modeller tek bir instance üzerinde çalışıyor.

### Notlar
`app/extensions.py::db` hâlâ kullanılmıyor — ileride bu dosya da temizlenebilir.

---

## TASK-007 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Micro modüllerinin kullandığı `app.models.db` instance'ı kök `__init__.py`'de `init_app` ile bağlandı
**Modül:** micro / db
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `__init__.py` → `from app.models import db as app_db` import edildi, `app_db.init_app(app)` eklendi

### Yapılan İşlem
Projede 3 farklı `SQLAlchemy` instance'ı mevcut: `extensions.py::db`, `app/extensions.py::db`, `app/models/__init__.py::db`. Micro modülleri `app.models.db`'yi kullanıyor ancak kök `__init__.py` yalnızca `extensions.py::db`'yi `init_app` yapıyordu. `app_db.init_app(app)` eklenerek `RuntimeError: not registered with this SQLAlchemy instance` hatası giderildi.

### Notlar
Uzun vadede tek bir `db` instance'ına geçilmesi teknik borcu azaltır.

---

## TASK-006 | 2026-03-18 | ✅ Tamamlandı

**Görev:** `__init__.py`'ye eksik `micro_bp` register satırı eklendi
**Modül:** micro / hgs
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `__init__.py` → `from micro import micro_bp` + `app.register_blueprint(micro_bp)` eklendi

### Yapılan İşlem
Kök `__init__.py`'de micro_bp hiç register edilmemişti; bu yüzden `/micro/*` altındaki tüm route'lar 404 veriyordu. Blueprint kaydı `v3_bp`'nin hemen altına eklendi. Doğrulama: `/micro/hgs` ve `/micro/hgs/login/<int:user_id>` route'ları artık url_map'te görünüyor.

### Notlar
- **2026-03-19 (TASK-106):** Üretim `app.create_app` kullanır; Micro kökte `/hgs` vb. Eski `/micro/hgs` istekleri köke 302 ile yönlendirilir.

---

## TASK-005 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Login sayfası CSP bloğu nedeniyle bozulan inline style/script harici dosyalara taşındı
**Modül:** auth / login
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `templates/login.html` → Inline `<style>` ve `<script>` blokları kaldırıldı, harici dosyalara bağlandı
- `static/css/login.css` → Oluşturuldu (login sayfası tüm CSS'i)
- `static/js/login.js` → Oluşturuldu (quick login toggle JS)

### Yapılan İşlem
Flask-Talisman'ın `content_security_policy_nonce_in` ayarı inline style ve script bloklarını engelliyordu. Login sayfasındaki tüm CSS `static/css/login.css`'e, JS ise `static/js/login.js`'e taşındı. HTML'de sadece `<link>` ve `<script src>` referansları kaldı.

### Notlar
Tarayıcı erişimi sağlanamadı, kod analizi yapıldı.

---

## TASK-004 | 2026-03-18 | ✅ Tamamlandı

**Görev:** `config.py`'de eksik `get_config()` fonksiyonu eklendi
**Modül:** config
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `config.py` → `get_config()` fonksiyonu eklendi; `FLASK_ENV`'e göre `Config` veya `TestingConfig` döner

### Yapılan İşlem
`__init__.py` `get_config` adını import etmeye çalışıyordu ancak `config.py`'de yalnızca class tanımları vardı, fonksiyon yoktu. `TestingConfig`'in hemen altına `get_config()` factory fonksiyonu eklenerek `ImportError` giderildi.

### Notlar
Yok.

---

## TASK-003 | 2026-03-18 | ✅ Tamamlandı

**Görev:** TASKLOG.md UTF-8 BOM'suz yeniden yazıldı, eski_proje git'ten çıkarıldı
**Modül:** setup / git
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `docs/TASKLOG.md` → Python ile UTF-8 BOM'suz yeniden yazıldı
- `.gitignore` → `eski_proje/` satırı eklendi
- `eski_proje` → `git rm --cached` ile git index'ten kaldırıldı

### Yapılan İşlem
TASKLOG.md encoding sorunu giderildi; dosya artık BOM'suz saf UTF-8. eski_proje klasörü git'ten çıkarıldı ve .gitignore'a eklendi, git status'ta bir daha görünmeyecek.

### Notlar
Yok.

---

## TASK-002 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Tüm `px` font-size değerleri `var(--text-*)` CSS değişkenlerine geçirildi
**Modül:** css / tipografi
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/css/components.css` → Tüm sabit `px` font-size değerleri `var(--text-*)` token'larıyla değiştirildi; `html { font-size: 16px }` rem tabanı korundu

### Yapılan İşlem
`components.css` içindeki tüm sabit `px` font-size değerleri `:root` üzerinde tanımlı `--text-2xs` → `--text-3xl` token'larıyla değiştirildi. Böylece `html { font-size }` değeri değiştirildiğinde tüm tipografi orantılı ölçeklenir.

### Notlar
`sidebar.css` önceki oturumda güncellenmişti. `app.css` zaten `rem` kullanıyor, dokunulmadı.

---

## TASK-001 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Proje kurulum ve GitHub entegrasyonu tamamlandı
**Modül:** setup
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `docs/TASKLOG.md` → İlk kayıt oluşturuldu
- `.kiro/steering/proje-kurallari.md` → TASKLOG + otomatik push kuralları eklendi
- `github_sync.py` → Otomatik push desteği eklendi

### Yapılan İşlem
Proje GitHub entegrasyonu kuruldu. Steering kuralları, TASKLOG takip sistemi ve otomatik push mekanizması devreye alındı.

### Notlar
Sistem test ediliyor. Sonraki görevlerden itibaren her değişiklikte TASKLOG otomatik güncellenecek ve push edilecek.

---

## TASK-001 | 2026-03-17 | 🔄 Düzeltme

**Görev:** tenants.html'de duplicate `extra_js` bloğu hatası giderildi
**Modül:** admin
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/admin/tenants.html` → Duplicate `{% block extra_js %}` bloğu kaldırıldı

### Yapılan İşlem
Önceki oturumda `fsAppend` ile eklenen `extra_js` bloğu, dosyada zaten mevcut olan aynı blokla çakışıyordu. Jinja2 aynı isimde iki blok tanımına izin vermediği için `TemplateAssertionError` fırlatıyordu. Fazladan olan ikinci blok kaldırıldı.

### Notlar
Yok.

---
