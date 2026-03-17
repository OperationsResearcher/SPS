# Uygulama Planı: Micro Platform Geçişi

## Genel Bakış

Bu plan, mevcut `app/routes/` katmanındaki tüm bileşenlerin `micro/` modüler mimarisine taşınmasını kapsar.
Her görev bir öncekinin üzerine inşa edilir; son adımda tüm modüller `micro/__init__.py` üzerinden birleştirilir.
Tüm kod Python/Flask, tüm UI Türkçe, tüm backend İngilizce snake_case kuralına uyar.

---

## Görevler

- [x] 1. Süreç Yönetimi modülünü tamamla (`micro/modules/surec/routes.py`)
  - [x] 1.1 Süreç CRUD API endpoint'lerini yaz
    - `surec_api_add` (POST `/micro/surec/api/add`): code, name, english_name, description, document_no, revision_no, status, progress, parent_id, start_boundary, end_boundary, leader_ids, member_ids alanlarını işle
    - `surec_api_update` (POST `/micro/surec/api/update/<id>`): lider/üye/alt-strateji yeniden ataması dahil
    - `surec_api_delete` (POST `/micro/surec/api/delete/<id>`): `is_active=False`, `deleted_at`, `deleted_by` yaz (Soft Delete)
    - Tüm endpoint'lerde `@login_required`, tenant izolasyonu, `db.session.rollback()` + `current_app.logger.error` hata yönetimi
    - _Gereksinimler: 3.3, 3.4, 3.5, 13.1, 13.3, 14.1, 14.2_

  - [x] 1.2 KPI CRUD API endpoint'lerini yaz
    - `surec_api_kpi_add`, `surec_api_kpi_update`, `surec_api_kpi_delete` (soft delete), `surec_api_kpi_list`
    - `surec_api_kpi_data_add`: veri kaydı + `score_engine_service.recalc_on_pg_data_change` + `process_deviation_service.check_pg_performance_deviation` tetikle
    - `surec_api_kpi_data_list`: tenant + process filtreli liste
    - _Gereksinimler: 3.6, 3.8_

  - [x] 1.3 Faaliyet CRUD ve aylık takip endpoint'lerini yaz
    - `surec_api_activity_add`, `surec_api_activity_update`, `surec_api_activity_delete` (soft delete)
    - `surec_api_activity_track` (POST `/micro/surec/api/activity/track/<id>`): aylık tamamlanma toggle
    - _Gereksinimler: 3.7, 3.12_

  - [x] 1.4 Karne sayfası ve AJAX endpoint'ini yaz
    - `surec_karne` (GET `/micro/surec/<id>/karne`): `micro/surec/karne.html` render et
    - `surec_api_karne` (GET `/micro/surec/api/karne/<id>`): yıl bazlı KPI + faaliyet aylık takip verisi döndür
    - Süreç listesi sayfasını (`micro/surec/index.html`) hiyerarşik ağaç görünümü için güncelle; `joinedload`/`selectinload` ile N+1 önle
    - _Gereksinimler: 3.1, 3.2, 3.9, 3.10, 3.11_

  - [x] 1.5 `micro/templates/micro/surec/karne.html` şablonunu oluştur
    - `base.html` extend et, `{% block content %}` kullan
    - Tüm dinamik veriler `data-*` attribute ile JS'e aktar; `<script>/<style>` blokları yasak
    - _Gereksinimler: 15.3, 15.4, 15.5_

  - [x] 1.6 `micro/static/micro/js/surec.js` ve `micro/static/micro/css/surec.css` oluştur
    - Tüm CRUD işlemleri için SweetAlert2 onay/bildirim kalıpları (silme onayı, başarı yeşil, hata kırmızı)
    - `alert()`/`confirm()`/`prompt()` kullanımı yasak
    - _Gereksinimler: 15.1, 15.2, 15.6_

  - [ ]* 1.7 Süreç soft delete round-trip property testi yaz
    - **Property 1: Soft Delete Round-Trip** — süreç oluştur → soft delete → listele → kayıt görünmemeli
    - **Validates: Gereksinim 13.5**

- [x] 2. Kontrol noktası — Süreç Yönetimi
  - Tüm testler geçmeli, soru varsa kullanıcıya sor.

- [x] 3. Stratejik Planlama modülünü genişlet (`micro/modules/sp/routes.py`)
  - [x] 3.1 Alt strateji CRUD endpoint'lerini ekle
    - `sp_add_sub_strategy` (POST `/micro/sp/api/sub-strategy/add`)
    - `sp_update_sub_strategy` (POST `/micro/sp/api/sub-strategy/update/<id>`)
    - `sp_delete_sub_strategy` (POST `/micro/sp/api/sub-strategy/delete/<id>`): soft delete
    - Rol kontrolü: `tenant_admin`, `executive_manager`, `Admin`
    - _Gereksinimler: 4.5, 4.10_

  - [x] 3.2 Stratejik planlama akış sayfalarını ekle
    - `sp_flow` (GET `/micro/sp/flow`): vizyon, strateji sayıları, SWOT sayıları, süreç sayıları
    - `sp_flow_dynamic` (GET `/micro/sp/flow/dynamic`): interaktif node-edge görselleştirme sayfası
    - `micro/templates/micro/sp/flow.html` ve `dynamic_flow.html` şablonlarını oluştur
    - _Gereksinimler: 4.6, 4.7_

  - [x] 3.3 Graf API endpoint'ini yaz
    - `sp_api_graph` (GET `/micro/sp/api/graph`): `score_engine_service.compute_vision_score` çağır, vizyon/strateji/alt-strateji/süreç/KPI node'larını ve edge'lerini JSON olarak döndür
    - `Admin` rolü için `tenant_id` query parametresi desteği ekle
    - _Gereksinimler: 4.8, 4.9_

  - [ ]* 3.4 SP soft delete property testi yaz
    - **Property 2: Strateji Soft Delete** — strateji ekle → soft delete → listede görünmemeli
    - **Validates: Gereksinim 4.10, 13.1**

- [x] 4. Kurum Paneli modülünü oluştur (`micro/modules/kurum/`)
  - [x] 4.1 Modül iskeletini oluştur
    - `micro/modules/kurum/__init__.py` ve `routes.py` dosyalarını oluştur
    - `kurum` (GET `/micro/kurum`): kullanıcı sayısı, aktif destek talepleri, paket kullanım yüzdesi, son aktivite logu; `tenant_admin`/`executive_manager` rol kontrolü
    - `micro/templates/micro/kurum/index.html` şablonunu oluştur
    - _Gereksinimler: 5.4_

  - [x] 4.2 Stratejik kimlik güncelleme API'lerini yaz
    - `kurum_api_update_strategy` (POST `/micro/kurum/api/update-strategy`): purpose, vision, core_values, code_of_ethics, quality_policy güncelle
    - `kurum_api_add_strategy`, `kurum_api_add_sub_strategy`, `kurum_api_update_main_strategy`, `kurum_api_delete_main_strategy`, `kurum_api_update_sub_strategy`, `kurum_api_delete_sub_strategy`
    - Tüm silme işlemleri soft delete; rol kontrolü: `tenant_admin`, `executive_manager`
    - _Gereksinimler: 5.5, 5.6, 5.7_

  - [x] 4.3 `micro/static/micro/js/kurum.js` oluştur
    - SweetAlert2 ile tüm form submit ve silme işlemleri
    - `data-*` attribute pattern ile Jinja2 veri aktarımı
    - _Gereksinimler: 15.1, 15.3, 15.5_

- [x] 5. Bireysel Performans modülünü oluştur (`micro/modules/bireysel/`)
  - [x] 5.1 Modül iskeletini oluştur
    - `micro/modules/bireysel/__init__.py` ve `routes.py` dosyalarını oluştur
    - `bireysel_karne` (GET `/micro/bireysel/karne`): `current_user.id` kapsamlı aktif `IndividualPerformanceIndicator` kayıtları
    - `micro/templates/micro/bireysel/karne.html` şablonunu oluştur
    - _Gereksinimler: 7.1_

  - [x] 5.2 Bireysel PG CRUD endpoint'lerini yaz
    - `bireysel_api_pg_add`, `bireysel_api_pg_update`, `bireysel_api_pg_delete` (soft delete)
    - `bireysel_api_veri_add`: `IndividualKpiData` kaydı (yıl, dönem tipi, dönem no, gerçekleşen değer)
    - `bireysel_api_karne` (GET): yıl bazlı bireysel PG + faaliyet takip verisi, `current_user.id` kapsamlı
    - _Gereksinimler: 7.2, 7.3, 7.5, 7.7_

  - [x] 5.3 Bireysel faaliyet ve favori endpoint'lerini yaz
    - `bireysel_api_faaliyet_add`, `bireysel_api_faaliyet_update`, `bireysel_api_faaliyet_delete` (soft delete)
    - `bireysel_api_faaliyet_track`: `IndividualActivityTrack` aylık toggle
    - `bireysel_api_favori_toggle`: `FavoriteKpi` oluştur veya soft delete
    - _Gereksinimler: 7.4, 7.6, 7.8_

  - [x] 5.4 `micro/static/micro/js/bireysel.js` oluştur
    - SweetAlert2 kalıpları, `data-*` pattern
    - _Gereksinimler: 15.1, 15.5_

  - [ ]* 5.5 Tenant izolasyonu property testi yaz
    - **Property 3: Tenant İzolasyonu** — farklı tenant kullanıcıları birbirinin bireysel PG kayıtlarını görmemeli
    - **Validates: Gereksinim 2.3, 13.4**

- [x] 6. Kontrol noktası — Kurum ve Bireysel modüller
  - Tüm testler geçmeli, soru varsa kullanıcıya sor.

- [x] 7. Admin modülünü oluştur (`micro/modules/admin/`)
  - [x] 7.1 Modül iskeletini ve kullanıcı yönetimi sayfasını oluştur
    - `micro/modules/admin/__init__.py` ve `routes.py` dosyalarını oluştur
    - `admin_users` (GET `/micro/admin/users`): `Admin` rolü tüm kullanıcıları, `tenant_admin`/`executive_manager` yalnızca kendi tenant kullanıcılarını listeler
    - `admin_users_add`, `admin_users_edit`, `admin_users_toggle` (soft delete) endpoint'lerini yaz
    - Duplicate `tenant_admin` kontrolü: tenant'ta zaten aktif `tenant_admin` varsa hata döndür
    - `micro/templates/micro/admin/users.html` şablonunu oluştur
    - _Gereksinimler: 6.1, 6.2, 6.3, 6.4_

  - [x] 7.2 Kurum ve paket yönetimi sayfalarını oluştur
    - `admin_tenants` (GET `/micro/admin/tenants`): kurum listesi
    - `admin_tenants_add`, `admin_tenants_edit`, `admin_tenants_toggle` (soft delete)
    - `admin_packages` (GET `/micro/admin/packages`): `SubscriptionPackage` ve `SystemModule` yönetimi
    - `micro/templates/micro/admin/tenants.html` ve `packages.html` şablonlarını oluştur
    - _Gereksinimler: 6.5, 6.6_

  - [x] 7.3 Bileşen senkronizasyonu ve toplu kullanıcı içe aktarma endpoint'lerini yaz
    - `admin_components_sync` (POST `/micro/admin/components/sync`): Flask URL kurallarını `RouteRegistry`'ye kaydet
    - `admin_components_update` (POST `/micro/admin/components/update`): `component_slug` değerlerini güncelle
    - `admin_users_bulk_import` (POST `/micro/admin/users/bulk-import`): Excel/CSV parse et, duplicate email'leri atla, `standard_user` rolüyle yeni kullanıcı oluştur
    - Tüm admin route'larına HTTP 403 kontrolü ekle (yetkisiz erişimde Türkçe hata)
    - _Gereksinimler: 6.7, 6.8, 6.9, 6.10_

  - [x] 7.4 `micro/static/micro/js/admin.js` ve `micro/static/micro/css/admin.css` oluştur
    - Kullanıcı toggle, kurum arşivleme, bulk import için SweetAlert2 onay diyalogları
    - _Gereksinimler: 15.1, 15.2_

  - [ ]* 7.5 Admin soft delete property testi yaz
    - **Property 4: Kullanıcı Soft Delete** — kullanıcı toggle → `is_active=False` → listede görünmemeli, fiziksel kayıt korunmalı
    - **Validates: Gereksinim 6.3, 13.1**

- [x] 8. HGS modülünü oluştur (`micro/modules/hgs/`)
  - [x] 8.1 Modül iskeletini ve hızlı giriş sayfasını oluştur
    - `micro/modules/hgs/__init__.py` ve `routes.py` dosyalarını oluştur
    - `hgs` (GET `/micro/hgs`): tüm aktif kullanıcıları tenant'a göre grupla, tenant adı → ad/email sıralı; `@login_required` yok
    - `hgs_login` (GET `/micro/hgs/login/<id>`): `login_user` ile giriş yap → `/micro/` yönlendir; `user_id` yoksa veya `is_active=False` ise `/micro/hgs`'e yönlendir
    - `micro/templates/micro/hgs/index.html` şablonunu oluştur
    - _Gereksinimler: 9.1, 9.2, 9.3, 9.4_

- [x] 9. Analiz Merkezi modülünü güncelle (`micro/modules/analiz/routes.py`)
  - [x] 9.1 Analiz API endpoint'lerini yaz
    - `analiz_api_trend` (GET `/micro/analiz/api/trend/<id>`): `AnalyticsService.get_performance_trend` delegasyonu (start_date, end_date, frequency)
    - `analiz_api_health` (GET `/micro/analiz/api/health/<id>`): `AnalyticsService.get_process_health_score` delegasyonu
    - `analiz_api_forecast` (GET `/micro/analiz/api/forecast/<id>`): `AnalyticsService.get_forecast` delegasyonu (periods, method)
    - `analiz_api_comparison` (POST `/micro/analiz/api/comparison`): `AnalyticsService.get_comparative_analysis` delegasyonu
    - _Gereksinimler: 8.2, 8.3, 8.4, 8.5_

  - [x] 9.2 Rapor ve anomali endpoint'lerini yaz
    - `analiz_api_report` (GET `/micro/analiz/api/report/<id>`): `ReportService.generate_performance_report`; `excel` formatında `Content-Disposition: attachment` ile döndür
    - `analiz_api_anomalies` (GET `/micro/analiz/api/anomalies`): `AnomalyService` delegasyonu, tenant kapsamlı
    - `micro/templates/micro/analiz/index.html` şablonunu güncelle
    - _Gereksinimler: 8.6, 8.7, 8.8_

  - [x] 9.3 `micro/static/micro/js/analiz.js` güncelle
    - Trend, health, forecast, anomaly grafikleri için SweetAlert2 hata bildirimleri
    - _Gereksinimler: 15.1_

- [x] 10. REST API katmanını oluştur (`micro/modules/api/`)
  - [x] 10.1 Modül iskeletini ve süreç/KPI endpoint'lerini oluştur
    - `micro/modules/api/__init__.py` ve `routes.py` dosyalarını oluştur
    - `api_processes_list` (GET `/micro/api/v1/processes`), `api_processes_detail` (GET `/micro/api/v1/processes/<id>`): tenant kapsamlı
    - `api_kpi_data_create` (POST), `api_kpi_data_get` (GET), `api_kpi_data_update` (PATCH), `api_kpi_data_delete` (DELETE — soft delete + `AuditLogger`)
    - Kimlik doğrulama yoksa HTTP 401 JSON döndür; sunucu hatasında HTTP 500 + `current_app.logger.error`
    - _Gereksinimler: 10.1, 10.2, 10.3, 10.9, 10.10_

  - [x] 10.2 Analitik, rapor, AI ve push endpoint'lerini yaz
    - `/micro/api/v1/analytics/trend/<id>`, `/health/<id>`, `/comparison`, `/forecast/<id>`: ilgili `AnalyticsService` metodlarına delege et
    - `/micro/api/v1/reports/performance/<id>`, `/reports/dashboard`: `ReportService` delegasyonu
    - `/micro/api/v1/ai/*`: `app/api/ai.py` mantığına delege et
    - `/micro/api/v1/push/*`: `app/api/push.py` mantığına delege et
    - `api_docs` (GET `/micro/api/docs`): Swagger/OpenAPI dokümantasyon sayfası
    - _Gereksinimler: 10.4, 10.5, 10.6, 10.7, 10.8_

  - [ ]* 10.3 API auth property testi yaz
    - **Property 5: API Kimlik Doğrulama** — kimlik doğrulamasız her `/micro/api/v1/` isteği HTTP 401 döndürmeli
    - **Validates: Gereksinim 10.9**

- [x] 11. Kontrol noktası — Admin, HGS, Analiz, API modülleri
  - Tüm testler geçmeli, soru varsa kullanıcıya sor.

- [x] 12. Module Registry'yi güncelle (`micro/core/module_registry.py`)
  - [x] 12.1 Yeni modülleri `MODULES` listesine ekle
    - `kurum`, `bireysel`, `admin`, `hgs`, `api` modüllerini id/name/url/icon/description alanlarıyla ekle
    - `get_accessible_modules(user)` fonksiyonunu `SubscriptionPackage` → `SystemModule` → `ModuleComponentSlug` zincirini kontrol edecek şekilde güncelle
    - Tenant'ın paketi yoksa minimum set döndür: `masaustu`, `bildirim`, `ayarlar`
    - _Gereksinimler: 12.1, 12.2, 12.3, 12.4_

  - [x] 12.2 Launcher sayfasını güncelle
    - `micro/core/launcher.py` içinde `get_accessible_modules` çağrısını doğrula
    - Yetkisiz modül erişiminde HTTP 403 + Türkçe hata mesajı döndür
    - _Gereksinimler: 12.5, 12.6_

  - [ ]* 12.3 Paket bazlı erişim kontrolü property testi yaz
    - **Property 6: Paket Erişim Kontrolü** — paketsiz tenant kullanıcısı yalnızca minimum modül setini görmeli
    - **Validates: Gereksinim 12.4**

- [x] 13. `micro/__init__.py` güncelle — tüm yeni modül importları ✓
  - Yeni modülleri import et: `kurum`, `bireysel`, `admin`, `hgs`, `api`
  - Import sırası: mevcut modüller korunur, yeni modüller eklenir
  - Uygulama başlangıcında tüm route'ların `micro_bp` üzerinden kayıtlı olduğunu doğrula
  - _Gereksinimler: 1.1, 1.2, 1.3_

- [x] 14. Son kontrol noktası — Tüm modüller entegre ✓
  - Tüm testler geçmeli, soru varsa kullanıcıya sor.

---

## Notlar

- `*` ile işaretli alt görevler isteğe bağlıdır; MVP için atlanabilir
- Her görev ilgili gereksinimlere referans verir
- Tüm silme işlemleri soft delete (`is_active=False`); fiziksel silme kesinlikle yasak
- Tüm route'lar `@login_required` ile korunur (HGS hariç)
- Frontend: SweetAlert2 zorunlu, `alert()`/`confirm()`/`prompt()` yasak
- Veri aktarımı: `data-*` attribute pattern, Jinja2 `{{ }}` `.js` dosyalarında yasak
- Backend: İngilizce snake_case; UI mesajları: Türkçe
