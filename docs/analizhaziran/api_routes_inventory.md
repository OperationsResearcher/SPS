# Kokpitim API Rotaları ve Uç Noktaları Envanter Raporu

**Analiz Tarihi:** 2026-06-09  
**Rapor Amacı:** Kokpitim uygulamasındaki tüm aktif web ve API rotalarının, HTTP metotlarının ve denetleyici (controller) fonksiyonlarının listesi.  

## 📊 Genel Özet

| Metrik | Değer |
| :--- | :--- |
| **Toplam Aktif Rota Sayısı** | 916 |
| **Kayıtlı Blueprint Sayısı** | 17 |

## 📂 Blueprint Bazlı Rota Dağılımı

| Blueprint Adı | Rota Sayısı | Açıklama |
| :--- | :---: | :--- |
| `app_bp` | 561 | Modüler bileşen rotaları |
| `main` | 157 | Modüler bileşen rotaları |
| `kokpitim_project_api` | 94 | Proje, RAID, SLA ve görev yönetim API'leri |
| `admin_bp` | 23 | Modüler bileşen rotaları |
| `marketing_bp` | 15 | Modüler bileşen rotaları |
| `api_routes` | 14 | Modüler bileşen rotaları |
| `process_performance_api` | 10 | Süreç performans göstergeleri ve karne API'leri |
| `ai_api` | 9 | Modüler bileşen rotaları |
| `auth_bp` | 7 | Modüler bileşen rotaları |
| `totp_bp` | 6 | Modüler bileşen rotaları |
| `Root` | 4 | Uygulamanın kök seviyesindeki genel rotalar (örn. /health) |
| `dataconn_bp` | 4 | Modüler bileşen rotaları |
| `push_api` | 4 | Modüler bileşen rotaları |
| `hgs_bp` | 2 | Modüler bileşen rotaları |
| `sso_bp` | 2 | Modüler bileşen rotaları |
| `core_bp` | 2 | Modüler bileşen rotaları |
| `swagger_ui` | 2 | Modüler bileşen rotaları |

---

## 🔍 Detaylı Rota Listesi

### 📦 Blueprint: `Root`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/api/me/dataconn-token` | `GET` | `api_me_dataconn_token` | `_my_dataconn_token` | Açıklama yok. |
| `/health` | `GET` | `global_health` | `global_health` | Yük dengeleyici / izleme endpoint'i. |
| `/login` | `GET, POST` | `public_login` | `login` | Handle login form - GET shows form, POST validates credentials. |
| `/logout` | `GET` | `public_logout` | `logout` | Log out user and redirect to login. |

---

### 📦 Blueprint: `admin_bp`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/admin/` | `GET` | `admin_bp.index` | `index` | Admin dashboard - summary stats and tenants overview. |
| `/admin/add-process` | `POST` | `admin_bp.admin_add_process` | `admin_add_process` | Admin panel hiyerarşik ekleme - create ile aynı. |
| `/admin/components/sync` | `POST` | `admin_bp.components_sync` | `components_sync` | Rota keşfi - url_map'teki tüm rotaları RouteRegistry'ye ekler (static hariç). |
| `/admin/components/update` | `POST` | `admin_bp.components_update` | `components_update` | AJAX ile bileşen slug güncelleme. |
| `/admin/create-process` | `POST` | `admin_bp.admin_create_process` | `admin_create_process` | Admin süreç oluştur. |
| `/admin/delete-process/<int:process_id>` | `DELETE, POST` | `admin_bp.admin_delete_process` | `admin_delete_process` | Admin süreç silme (soft delete). |
| `/admin/get-process/<int:process_id>` | `GET` | `admin_bp.admin_get_process` | `admin_get_process` | Süreç bilgilerini getir - admin/edit için. |
| `/admin/kule-iletisim` | `GET` | `admin_bp.kule_iletisim` | `kule_iletisim` | Kule İletişim yönetim paneli (Admin ve Yönetici erişimi). |
| `/admin/kule-iletisim/<int:ticket_id>/detail` | `GET` | `admin_bp.kule_ticket_detail` | `kule_ticket_detail` | Açıklama yok. |
| `/admin/kule-iletisim/<int:ticket_id>/update` | `POST` | `admin_bp.kule_ticket_update` | `kule_ticket_update` | Açıklama yok. |
| `/admin/packages` | `GET, POST` | `admin_bp.packages` | `packages` | Manage packages and modules. |
| `/admin/strategy-management` | `GET` | `admin_bp.strategy_management` | `strategy_management` | Stratejik planlama akış yapısı - Admin tüm kurumları, tenant_admin/executive_manager sadece kendi kurumunu görür. |
| `/admin/tenants` | `GET` | `admin_bp.tenants` | `tenants` | List tenants - Admin tümünü, tenant_admin/executive_manager sadece kendi kurumunu görür. |
| `/admin/tenants/add` | `POST` | `admin_bp.tenants_add` | `tenants_add` | Add new tenant. |
| `/admin/tenants/archive/<int:tenant_id>` | `POST` | `admin_bp.tenants_archive` | `tenants_archive` | Archive tenant (soft delete - set is_active=False). |
| `/admin/tenants/edit/<int:tenant_id>` | `POST` | `admin_bp.tenants_edit` | `tenants_edit` | Edit tenant - Admin her kurumu, tenant_admin sadece kendi kurumunu düzenleyebilir. |
| `/admin/update-process/<int:process_id>` | `PUT, POST` | `admin_bp.admin_update_process` | `admin_update_process` | Admin süreç güncelle. |
| `/admin/users` | `GET` | `admin_bp.users` | `users` | List users - Admin sees all, tenants see theirs. |
| `/admin/users/add` | `POST` | `admin_bp.users_add` | `users_add` | Add new user. |
| `/admin/users/bulk-import` | `POST` | `admin_bp.users_bulk_import` | `users_bulk_import` | Handle bulk user import from Excel/CSV. |
| `/admin/users/bulk-template` | `GET` | `admin_bp.users_bulk_template` | `users_bulk_template` | Download template for bulk user import. |
| `/admin/users/edit/<int:user_id>` | `POST` | `admin_bp.users_edit` | `users_edit` | Edit user. |
| `/admin/users/toggle/<int:user_id>` | `POST` | `admin_bp.users_toggle` | `users_toggle` | Toggle user active status (soft delete). |

---

### 📦 Blueprint: `ai_api`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/achievement-probability/<int:kpi_id>` | `GET` | `ai_api.achievement_probability` | `achievement_probability` | Hedef başarı olasılığı |
| `/anomalies/<int:kpi_id>` | `GET` | `ai_api.detect_anomalies` | `detect_anomalies` | Anomali tespiti |
| `/forecast/<int:kpi_id>` | `GET` | `ai_api.forecast_kpi` | `forecast_kpi` | KPI tahmini |
| `/insights` | `GET` | `ai_api.smart_insights` | `smart_insights` | Akıllı insights |
| `/recommendations/process/<int:process_id>` | `GET` | `ai_api.process_recommendations` | `process_recommendations` | Süreç önerileri |
| `/reports/daily` | `GET` | `ai_api.daily_digest` | `daily_digest` | Günlük özet raporu |
| `/reports/monthly` | `GET` | `ai_api.monthly_report` | `monthly_report` | Aylık rapor |
| `/reports/weekly` | `GET` | `ai_api.weekly_summary` | `weekly_summary` | Haftalık özet |
| `/seasonality/<int:kpi_id>` | `GET` | `ai_api.detect_seasonality` | `detect_seasonality` | Mevsimsellik analizi |

---

### 📦 Blueprint: `api_routes`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/analytics/comparison` | `POST` | `api_routes.get_comparison` | `get_comparison` | Karşılaştırmalı analiz |
| `/analytics/forecast/<int:kpi_id>` | `GET` | `api_routes.get_forecast` | `get_forecast` | Tahminleme |
| `/analytics/health/<int:process_id>` | `GET` | `api_routes.get_health` | `get_health` | Süreç sağlık skoru |
| `/analytics/trend/<int:kpi_id>` | `GET` | `api_routes.get_trend` | `get_trend` | KPI trend analizi |
| `/kpi-data` | `POST` | `api_routes.create_kpi_data` | `create_kpi_data` | KPI veri girişi |
| `/kpi-data/<int:kpi_data_id>` | `GET` | `api_routes.get_kpi_data` | `get_kpi_data` | KPI veri detayı |
| `/kpi-data/<int:kpi_data_id>` | `PATCH` | `api_routes.update_kpi_data` | `update_kpi_data` | KPI veri güncelleme |
| `/kpi-data/<int:kpi_data_id>` | `DELETE` | `api_routes.delete_kpi_data` | `delete_kpi_data` | KPI veri silme (soft delete) |
| `/processes` | `GET` | `api_routes.list_processes` | `list_processes` | Süreç listesi |
| `/processes/<int:process_id>` | `GET` | `api_routes.get_process` | `get_process` | Süreç detayı |
| `/processes/<int:process_id>/kpis` | `GET` | `api_routes.list_process_kpis` | `list_process_kpis` | Süreç KPI'ları |
| `/reports/dashboard` | `GET` | `api_routes.get_dashboard_report` | `get_dashboard_report` | Dashboard özet raporu |
| `/reports/performance/<int:process_id>` | `GET` | `api_routes.get_performance_report` | `get_performance_report` | Performans raporu |
| `/webhooks` | `POST` | `api_routes.create_webhook` | `create_webhook` | Webhook oluştur |

---

### 📦 Blueprint: `app_bp`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/` | `GET` | `app_bp.platform_root` | `platform_root` | Kök URL — giriş yapmışsa launcher, yapmamışsa marketing. |
| `/Hgs_mfg` | `GET` | `app_bp.hgs_public_paths_disabled` | `hgs_public_paths_disabled` | Eski / hatalı URL'ler — kasıtlı 404. |
| `/Hgs_mfg/login/<int:user_id>` | `GET` | `app_bp.hgs_public_paths_disabled` | `hgs_public_paths_disabled` | Eski / hatalı URL'ler — kasıtlı 404. |
| `/MfG_hgs` | `GET` | `app_bp.hgs` | `hgs` | Açıklama yok. |
| `/MfG_hgs/login/<int:user_id>` | `GET` | `app_bp.hgs_login` | `hgs_login` | Açıklama yok. |
| `/admin/api/sub-tenants` | `GET` | `app_bp.admin_api_sub_tenants_list` | `admin_api_sub_tenants_list` | Açıklama yok. |
| `/admin/api/sub-tenants` | `POST` | `app_bp.admin_api_sub_tenants_create` | `admin_api_sub_tenants_create` | Açıklama yok. |
| `/admin/api/sub-tenants/<int:sub_tenant_id>/admin/reset-password` | `POST` | `app_bp.admin_api_sub_tenant_admin_reset_password` | `admin_api_sub_tenant_admin_reset_password` | Açıklama yok. |
| `/admin/api/sub-tenants/<int:sub_tenant_id>/toggle` | `POST` | `app_bp.admin_api_sub_tenant_toggle` | `admin_api_sub_tenant_toggle` | Açıklama yok. |
| `/admin/api/sub-tenants/usage` | `GET` | `app_bp.admin_api_sub_tenants_usage` | `admin_api_sub_tenants_usage` | Açıklama yok. |
| `/admin/api/sub-tenants/usage/export.xlsx` | `GET` | `app_bp.admin_api_sub_tenants_usage_export` | `admin_api_sub_tenants_usage_export` | Excel dışa aktarma. |
| `/admin/api/users` | `GET` | `app_bp.admin_api_users_paginated` | `admin_api_users_paginated` | Sprint 24: Paginated admin user list — Tomofil gibi 100+ user tenant'larda performans. |
| `/admin/araclar` | `GET` | `app_bp.admin_tools_home` | `admin_tools_home` | Açıklama yok. |
| `/admin/araclar/hata-kontrolu` | `GET` | `app_bp.admin_tools_hata_kontrolu` | `admin_tools_hata_kontrolu` | Açıklama yok. |
| `/admin/araclar/hata-kontrolu/gecmis` | `GET` | `app_bp.admin_tools_hk_gecmis` | `admin_tools_hk_gecmis` | Kaydedilmiş koşuların özet listesi. |
| `/admin/araclar/hata-kontrolu/gecmis-yukle` | `GET` | `app_bp.admin_tools_hk_gecmis_yukle` | `admin_tools_hk_gecmis_yukle` | Tek bir kaydedilmiş koşunun tam içeriği. |
| `/admin/araclar/hata-kontrolu/kesif` | `GET` | `app_bp.admin_tools_hk_kesif` | `admin_tools_hk_kesif` | Faz 2 — taranacak sayfaların keşfi (route haritası, statik). |
| `/admin/araclar/hata-kontrolu/senaryo-baslat` | `POST` | `app_bp.admin_tools_hk_senaryo_baslat` | `admin_tools_hk_senaryo_baslat` | Faz 3d — aktif CRUD senaryolarını arka planda başlatır. Yalnız Admin + Yerel. |
| `/admin/araclar/hata-kontrolu/senaryo-durum` | `GET` | `app_bp.admin_tools_hk_senaryo_durum` | `admin_tools_hk_senaryo_durum` | Açıklama yok. |
| `/admin/araclar/hata-kontrolu/tarama-baslat` | `POST` | `app_bp.admin_tools_hk_tarama_baslat` | `admin_tools_hk_tarama_baslat` | Faz 3b — Playwright tarayıcı taramasını arka planda başlatır. Yalnız Admin + Yerel. |
| `/admin/araclar/hata-kontrolu/tarama-durum` | `GET` | `app_bp.admin_tools_hk_tarama_durum` | `admin_tools_hk_tarama_durum` | Açıklama yok. |
| `/admin/araclar/hata-kontrolu/tomofiltest-durum` | `GET` | `app_bp.admin_tools_tomofiltest_durum` | `admin_tools_tomofiltest_durum` | Açıklama yok. |
| `/admin/araclar/hata-kontrolu/tomofiltest-yenile` | `POST` | `app_bp.admin_tools_tomofiltest_yenile` | `admin_tools_tomofiltest_yenile` | tomofiltest'i Tomofil'den (yeniden) klonlar. Yalnız Admin + Yerel. |
| `/admin/araclar/istatistikler` | `GET` | `app_bp.admin_tools_istatistikler` | `admin_tools_istatistikler` | Sistemdeki kurum bazında kullanıcı/strateji/süreç/PG/proje sayıları (salt-okuma). |
| `/admin/araclar/kilavuz-olusturucu` | `GET` | `app_bp.admin_tools_kilavuz_olusturucu` | `admin_tools_kilavuz_olusturucu` | Açıklama yok. |
| `/admin/araclar/kilavuz-olusturucu/baslat` | `POST` | `app_bp.admin_tools_kilavuz_olusturucu_baslat` | `admin_tools_kilavuz_olusturucu_baslat` | Açıklama yok. |
| `/admin/araclar/kilavuz-olusturucu/durdur` | `POST` | `app_bp.admin_tools_kilavuz_olusturucu_durdur` | `admin_tools_kilavuz_olusturucu_durdur` | Çalışan otonom çekimi durdurur (kooperatif iptal — güvenli noktada durur). |
| `/admin/araclar/kilavuz-olusturucu/durum` | `GET` | `app_bp.admin_tools_kilavuz_olusturucu_durum` | `admin_tools_kilavuz_olusturucu_durum` | Açıklama yok. |
| `/admin/araclar/kilavuz-olusturucu/indir-pdf` | `GET` | `app_bp.admin_tools_kilavuz_olusturucu_indir_pdf` | `admin_tools_kilavuz_olusturucu_indir_pdf` | Açıklama yok. |
| `/admin/araclar/kilavuz-olusturucu/kurum-durum` | `GET` | `app_bp.admin_tools_kilavuz_kurum_durum` | `admin_tools_kilavuz_kurum_durum` | YeniTomofil kurumunun durumu (durum kartı için). |
| `/admin/araclar/loglar` | `GET` | `app_bp.admin_tools_loglar` | `admin_tools_loglar` | Kurum bazında ve genel giriş/veri hareketi logları (salt-okuma). |
| `/admin/araclar/loglar/kurum/<int:tenant_id>` | `GET` | `app_bp.admin_tools_loglar_kurum` | `admin_tools_loglar_kurum` | Tek kuruma ilişkin kategori bazlı detaylı log zaman çizelgesi (salt-okuma). |
| `/admin/araclar/yedekleme` | `GET` | `app_bp.admin_tools_yedekleme` | `admin_tools_yedekleme` | Yedekleme bölümü — otomatik durum + manuel indir + geri yükle (Admin). |
| `/admin/araclar/yedekleme/geri-yukle/db` | `POST` | `app_bp.admin_tools_yedekleme_geri_yukle_db` | `admin_tools_yedekleme_geri_yukle_db` | YIKICI: yüklenen .dump'tan DB'yi geri yükle. Admin + şifre + onay metni. |
| `/admin/araclar/yedekleme/indir-dosya` | `GET` | `app_bp.admin_tools_yedekleme_indir_dosya` | `admin_tools_yedekleme_indir_dosya` | Mevcut otomatik yedek dosyasını indir (yalnız otomatik dizininden). |
| `/admin/araclar/yedekleme/indir/db` | `POST` | `app_bp.admin_tools_yedekleme_indir_db` | `admin_tools_yedekleme_indir_db` | Manuel: anlık tam DB yedeği üret → indir. |
| `/admin/araclar/yedekleme/indir/kod` | `POST` | `app_bp.admin_tools_yedekleme_indir_kod` | `admin_tools_yedekleme_indir_kod` | Manuel: anlık tam kod yedeği üret → indir. |
| `/admin/araclar/yedekleme/otomatik-calistir` | `POST` | `app_bp.admin_tools_yedekleme_otomatik_calistir` | `admin_tools_yedekleme_otomatik_calistir` | Otomatik yedeği şimdi elle tetikle (test/acil). |
| `/admin/bakim-modu` | `GET, POST` | `app_bp.admin_bakim_modu` | `admin_bakim_modu` | Bakım modu (yalnız platform Admin). Ortam değişkeni kilitliyse yalnız okuma. |
| `/admin/components/sync` | `POST` | `app_bp.admin_components_sync` | `admin_components_sync` | Açıklama yok. |
| `/admin/components/update` | `POST` | `app_bp.admin_components_update` | `admin_components_update` | Açıklama yok. |
| `/admin/k-radar/weights` | `GET` | `app_bp.admin_k_radar_weights_get` | `admin_k_radar_weights_get` | Mevcut K-Radar ağırlıklarını döner. |
| `/admin/k-radar/weights` | `POST` | `app_bp.admin_k_radar_weights_save` | `admin_k_radar_weights_save` | K-Radar ağırlıklarını kaydeder ve cache'i temizler. |
| `/admin/modules/add` | `POST` | `app_bp.admin_modules_add` | `admin_modules_add` | Açıklama yok. |
| `/admin/modules/toggle/<int:mod_id>` | `POST` | `app_bp.admin_modules_toggle` | `admin_modules_toggle` | Açıklama yok. |
| `/admin/notifications` | `GET` | `app_bp.admin_notifications` | `admin_notifications` | Açıklama yok. |
| `/admin/notifications/broadcast` | `POST` | `app_bp.admin_notifications_broadcast` | `admin_notifications_broadcast` | Açıklama yok. |
| `/admin/notifications/delete/<int:notif_id>` | `POST` | `app_bp.admin_notifications_delete` | `admin_notifications_delete` | Açıklama yok. |
| `/admin/notifications/stats` | `GET` | `app_bp.admin_notifications_stats` | `admin_notifications_stats` | Açıklama yok. |
| `/admin/packages` | `GET` | `app_bp.admin_packages` | `admin_packages` | Açıklama yok. |
| `/admin/packages/add` | `POST` | `app_bp.admin_packages_add` | `admin_packages_add` | Açıklama yok. |
| `/admin/packages/edit/<int:pkg_id>` | `POST` | `app_bp.admin_packages_edit` | `admin_packages_edit` | Açıklama yok. |
| `/admin/packages/toggle/<int:pkg_id>` | `POST` | `app_bp.admin_packages_toggle` | `admin_packages_toggle` | Açıklama yok. |
| `/admin/sub-tenants` | `GET` | `app_bp.admin_sub_tenants_page` | `admin_sub_tenants_page` | Açıklama yok. |
| `/admin/sub-tenants/usage` | `GET` | `app_bp.admin_sub_tenants_usage_page` | `admin_sub_tenants_usage_page` | Açıklama yok. |
| `/admin/tenants` | `GET` | `app_bp.admin_tenants` | `admin_tenants` | Açıklama yok. |
| `/admin/tenants/add` | `POST` | `app_bp.admin_tenants_add` | `admin_tenants_add` | Açıklama yok. |
| `/admin/tenants/edit/<int:tenant_id>` | `POST` | `app_bp.admin_tenants_edit` | `admin_tenants_edit` | Açıklama yok. |
| `/admin/tenants/logo/<int:tenant_id>` | `POST` | `app_bp.admin_tenants_logo` | `admin_tenants_logo` | Açıklama yok. |
| `/admin/tenants/toggle/<int:tenant_id>` | `POST` | `app_bp.admin_tenants_toggle` | `admin_tenants_toggle` | Açıklama yok. |
| `/admin/users` | `GET` | `app_bp.admin_users` | `admin_users` | Açıklama yok. |
| `/admin/users/<int:user_id>/2fa-reset` | `POST` | `app_bp.admin_users_2fa_reset` | `admin_users_2fa_reset` | Bir kullanıcının 2FA'sını admin olarak sıfırla. |
| `/admin/users/add` | `POST` | `app_bp.admin_users_add` | `admin_users_add` | Açıklama yok. |
| `/admin/users/bulk-import` | `POST` | `app_bp.admin_users_bulk_import` | `admin_users_bulk_import` | Açıklama yok. |
| `/admin/users/edit/<int:user_id>` | `POST` | `app_bp.admin_users_edit` | `admin_users_edit` | Açıklama yok. |
| `/admin/users/sample-excel` | `GET` | `app_bp.admin_users_sample_excel` | `admin_users_sample_excel` | Toplu kullanıcı içe aktarma için örnek Excel dosyası indir. |
| `/admin/users/toggle/<int:user_id>` | `POST` | `app_bp.admin_users_toggle` | `admin_users_toggle` | Açıklama yok. |
| `/admin/yonetim-paneli` | `GET` | `app_bp.yonetim_paneli` | `yonetim_paneli` | Açıklama yok. |
| `/admin/yonetim-paneli/aktiviteler` | `GET` | `app_bp.yonetim_paneli_aktiviteler` | `yonetim_paneli_aktiviteler` | Açıklama yok. |
| `/admin/yonetim-paneli/istatistik` | `GET` | `app_bp.yonetim_paneli_istatistik` | `yonetim_paneli_istatistik` | Açıklama yok. |
| `/admin/yonetim-paneli/kullanici-detay` | `GET` | `app_bp.yonetim_paneli_kullanici_detay` | `yonetim_paneli_kullanici_detay` | Açıklama yok. |
| `/analiz` | `GET` | `app_bp.analiz` | `analiz` | Analitik özet — tenant süreçleri üzerinden. |
| `/analiz/api/anomalies` | `GET` | `app_bp.analiz_api_anomalies` | `analiz_api_anomalies` | Tenant geneli (veya tek süreç) için tüm aktif PG'lerde anomali tarar. |
| `/analiz/api/comparison` | `POST` | `app_bp.analiz_api_comparison` | `analiz_api_comparison` | Açıklama yok. |
| `/analiz/api/forecast/<int:process_id>` | `GET` | `app_bp.analiz_api_forecast` | `analiz_api_forecast` | Açıklama yok. |
| `/analiz/api/health/<int:process_id>` | `GET` | `app_bp.analiz_api_health` | `analiz_api_health` | Açıklama yok. |
| `/analiz/api/report/<int:process_id>` | `GET` | `app_bp.analiz_api_report` | `analiz_api_report` | Açıklama yok. |
| `/analiz/api/trend/<int:process_id>` | `GET` | `app_bp.analiz_api_trend` | `analiz_api_trend` | Süreçteki tüm aktif PG'ler için trend serileri döner (frontend çoklu seri çizer). |
| `/api/calendar/events` | `GET` | `app_bp.masaustu_calendar_events` | `masaustu_calendar_events` | Masaüstü ortak takvim etkinlikleri (süreç faaliyet + proje görev). |
| `/api/calendar/events/org` | `GET` | `app_bp.kurum_calendar_events` | `kurum_calendar_events` | Kurum geneli ortak takvim etkinlikleri. |
| `/api/calendar/process/<int:process_id>/activity-form-meta` | `GET` | `app_bp.api_calendar_activity_form_meta` | `api_calendar_activity_form_meta` | Süreç faaliyeti modalı: PG listesi, atanabilir kullanıcılar, çoklu atama izni (karne ile aynı veri). |
| `/api/calendar/quick-create-meta` | `GET` | `app_bp.api_calendar_quick_create_meta` | `api_calendar_quick_create_meta` | Takvimden hızlı oluşturma: süreç / proje / bireysel için seçenek listeleri ve bayraklar. |
| `/api/docs` | `GET` | `app_bp.api_docs` | `api_docs` | Swagger/OpenAPI dokümantasyon sayfası. |
| `/api/kule/tour/<tour_key>` | `GET` | `app_bp.kule_get_tour` | `kule_get_tour` | Tur tanımını + kullanıcı durumunu döner. |
| `/api/kule/tour/<tour_key>/complete` | `POST` | `app_bp.kule_mark_complete` | `kule_mark_complete` | Tur tamamlandı. |
| `/api/kule/tour/<tour_key>/dismiss` | `POST` | `app_bp.kule_mark_dismiss` | `kule_mark_dismiss` | Kullanıcı turu atladı. |
| `/api/kule/tour/<tour_key>/restart` | `POST` | `app_bp.kule_restart` | `kule_restart` | Tur durumunu sıfırla, tekrar gösterilebilir hale gelsin. |
| `/api/kule/tour/<tour_key>/seen` | `POST` | `app_bp.kule_mark_seen` | `kule_mark_seen` | Kullanıcı turu görüntüledi (seen_count artar). |
| `/api/morning-summary` | `GET` | `app_bp.api_morning_summary` | `api_morning_summary` | Yönetici sabah özeti — KPI, faaliyet, proje durumu. |
| `/api/my-tasks` | `GET` | `app_bp.api_my_tasks` | `api_my_tasks` | Kullanıcıya atanmış aktif görevleri tek listede döner — son tarihe göre sıralı. |
| `/api/profile/theme` | `GET, POST` | `app_bp.api_profile_theme` | `api_profile_theme` | Kullanıcının tema tercihini sunucuya kaydeder/okur (çoklu cihaz senkronu). |
| `/api/scheduled-reports` | `GET` | `app_bp.api_scheduled_reports_get` | `api_scheduled_reports_get` | Açıklama yok. |
| `/api/scheduled-reports` | `POST` | `app_bp.api_scheduled_reports_save` | `api_scheduled_reports_save` | Açıklama yok. |
| `/api/search` | `GET` | `app_bp.api_global_search` | `api_global_search` | Stratejik plan + süreç + PG + proje + kullanıcı genelinde hızlı arama. |
| `/api/tenant-last-change` | `GET` | `app_bp.api_tenant_last_change` | `api_tenant_last_change` | Tenant'ın son PG veri değişiklik zaman damgası — canlı yenileme sinyali (poll). |
| `/api/v1/ai/recommend` | `GET` | `app_bp.api_ai_recommend` | `api_ai_recommend` | Açıklama yok. |
| `/api/v1/analytics/comparison` | `POST` | `app_bp.api_analytics_comparison` | `api_analytics_comparison` | Açıklama yok. |
| `/api/v1/analytics/forecast/<int:process_id>` | `GET` | `app_bp.api_analytics_forecast` | `api_analytics_forecast` | Açıklama yok. |
| `/api/v1/analytics/health/<int:process_id>` | `GET` | `app_bp.api_analytics_health` | `api_analytics_health` | Açıklama yok. |
| `/api/v1/analytics/trend/<int:process_id>` | `GET` | `app_bp.api_analytics_trend` | `api_analytics_trend` | Açıklama yok. |
| `/api/v1/kpi-data` | `POST` | `app_bp.api_kpi_data_create` | `api_kpi_data_create` | Açıklama yok. |
| `/api/v1/kpi-data/<int:entry_id>` | `GET` | `app_bp.api_kpi_data_get` | `api_kpi_data_get` | Açıklama yok. |
| `/api/v1/kpi-data/<int:entry_id>` | `PATCH` | `app_bp.api_kpi_data_update` | `api_kpi_data_update` | Açıklama yok. |
| `/api/v1/kpi-data/<int:entry_id>` | `DELETE` | `app_bp.api_kpi_data_delete` | `api_kpi_data_delete` | Açıklama yok. |
| `/api/v1/processes` | `GET` | `app_bp.api_processes_list` | `api_processes_list` | Açıklama yok. |
| `/api/v1/processes/<int:process_id>` | `GET` | `app_bp.api_processes_detail` | `api_processes_detail` | Açıklama yok. |
| `/api/v1/push/subscribe` | `POST` | `app_bp.api_push_subscribe` | `api_push_subscribe` | Açıklama yok. |
| `/api/v1/reports/dashboard` | `GET` | `app_bp.api_reports_dashboard` | `api_reports_dashboard` | Açıklama yok. |
| `/api/v1/reports/performance/<int:process_id>` | `GET` | `app_bp.api_reports_performance` | `api_reports_performance` | Açıklama yok. |
| `/ayarlar` | `GET` | `app_bp.ayarlar` | `ayarlar` | Ayarlar hub sayfası. |
| `/ayarlar/eposta` | `GET` | `app_bp.ayarlar_eposta` | `ayarlar_eposta` | Kurum e-posta ayarları sayfası. |
| `/ayarlar/eposta/api/save` | `POST` | `app_bp.ayarlar_eposta_save` | `ayarlar_eposta_save` | Kurum e-posta ayarlarını kaydet. |
| `/ayarlar/eposta/api/send-test` | `POST` | `app_bp.ayarlar_eposta_send_test` | `ayarlar_eposta_send_test` | Kayıtlı ayarlarla test maili gönder. |
| `/ayarlar/eposta/api/test` | `POST` | `app_bp.ayarlar_eposta_test` | `ayarlar_eposta_test` | SMTP bağlantısını test et. |
| `/ayarlar/hesap` | `GET, POST` | `app_bp.ayarlar_hesap` | `ayarlar_hesap` | Kişisel hesap ayarları — mevcut auth_bp.settings ile aynı mantık, micro UI. |
| `/ayarlar/zamanlanmis-raporlar` | `GET` | `app_bp.scheduled_reports_page` | `scheduled_reports_page` | Açıklama yok. |
| `/bildirim` | `GET` | `app_bp.bildirim` | `bildirim` | Bildirim Merkezi ana sayfası — okunmamışlar önce. |
| `/bildirim/api/mark-all-read` | `POST` | `app_bp.bildirim_api_mark_all_read` | `bildirim_api_mark_all_read` | Tüm bildirimleri okundu işaretle. |
| `/bildirim/api/mark-read/<int:notif_id>` | `POST` | `app_bp.bildirim_api_mark_read` | `bildirim_api_mark_read` | Tekil bildirimi okundu işaretle. |
| `/bildirim/api/unread-count` | `GET` | `app_bp.bildirim_api_unread_count` | `bildirim_api_unread_count` | Okunmamış bildirim sayısı — topbar badge için. |
| `/bireysel` | `GET` | `app_bp.bireysel` | `bireysel` | Bireysel modül giriş yönlendirmesi. |
| `/bireysel/api/ai-ozet` | `GET` | `app_bp.bireysel_api_ai_ozet` | `bireysel_api_ai_ozet` | Bireysel karne üstü 2 cümlelik Türkçe AI özet (heuristik + opsiyonel LLM). |
| `/bireysel/api/ekip-hizalama` | `GET` | `app_bp.bireysel_api_ekip_hizalama` | `bireysel_api_ekip_hizalama` | Yöneticiler için tüm ekip hizalama özeti. |
| `/bireysel/api/faaliyet/add` | `POST` | `app_bp.bireysel_api_faaliyet_add` | `bireysel_api_faaliyet_add` | Açıklama yok. |
| `/bireysel/api/faaliyet/delete/<int:act_id>` | `POST` | `app_bp.bireysel_api_faaliyet_delete` | `bireysel_api_faaliyet_delete` | Açıklama yok. |
| `/bireysel/api/faaliyet/track/<int:act_id>` | `POST` | `app_bp.bireysel_api_faaliyet_track` | `bireysel_api_faaliyet_track` | Bireysel faaliyet aylık tamamlanma toggle. |
| `/bireysel/api/faaliyet/update/<int:act_id>` | `POST` | `app_bp.bireysel_api_faaliyet_update` | `bireysel_api_faaliyet_update` | Açıklama yok. |
| `/bireysel/api/favori/toggle/<int:kpi_id>` | `POST` | `app_bp.bireysel_api_favori_toggle` | `bireysel_api_favori_toggle` | Favori KPI oluştur veya soft delete. |
| `/bireysel/api/hizalama-skoru` | `GET` | `app_bp.bireysel_api_hizalama_skoru` | `bireysel_api_hizalama_skoru` | Oturum kullanıcısının bireysel→stratejik hizalama skorunu döner. |
| `/bireysel/api/karne` | `GET` | `app_bp.bireysel_api_karne` | `bireysel_api_karne` | Yıl bazlı bireysel PG + faaliyet takip verisi. |
| `/bireysel/api/karne/export-pdf` | `GET` | `app_bp.bireysel_api_karne_export_pdf` | `bireysel_api_karne_export_pdf` | Kullanıcının bireysel karnesini PDF olarak indir. |
| `/bireysel/api/pg/<int:pg_id>/series` | `GET` | `app_bp.bireysel_api_pg_series` | `bireysel_api_pg_series` | Seçilen PG için yıllık veri serisi (modal / sparkline). |
| `/bireysel/api/pg/add` | `POST` | `app_bp.bireysel_api_pg_add` | `bireysel_api_pg_add` | Açıklama yok. |
| `/bireysel/api/pg/delete/<int:pg_id>` | `POST` | `app_bp.bireysel_api_pg_delete` | `bireysel_api_pg_delete` | Açıklama yok. |
| `/bireysel/api/pg/ensure-from-process-kpi` | `POST` | `app_bp.bireysel_api_pg_ensure_from_process_kpi` | `bireysel_api_pg_ensure_from_process_kpi` | Süreç PG'si için geçerli kullanıcıda bireysel PG yoksa oluşturur (aynı kullanıcı adına). |
| `/bireysel/api/pg/update/<int:pg_id>` | `POST` | `app_bp.bireysel_api_pg_update` | `bireysel_api_pg_update` | Açıklama yok. |
| `/bireysel/api/veri/add` | `POST` | `app_bp.bireysel_api_veri_add` | `bireysel_api_veri_add` | Açıklama yok. |
| `/bireysel/karne` | `GET` | `app_bp.bireysel_karne` | `bireysel_karne` | Bireysel karne sayfası. |
| `/demo` | `GET` | `app_bp.demo_landing` | `demo_landing` | Demo giriş sayfası — 3 rol kartı + açıklamalar. |
| `/demo/` | `GET` | `app_bp.demo_landing` | `demo_landing` | Demo giriş sayfası — 3 rol kartı + açıklamalar. |
| `/demo/end` | `GET, POST` | `app_bp.demo_end` | `demo_end` | Demo session'u sonlandırır, landing'e döner. |
| `/demo/heartbeat` | `GET` | `app_bp.demo_heartbeat` | `demo_heartbeat` | Frontend'in her dakika çağırdığı endpoint — kalan süreyi döner. |
| `/demo/start/<role>` | `GET, POST` | `app_bp.demo_start` | `demo_start` | Seçili role bağlı bir demo kullanıcısıyla otomatik giriş yapar. |
| `/hgs` | `GET` | `app_bp.hgs_public_paths_disabled` | `hgs_public_paths_disabled` | Eski / hatalı URL'ler — kasıtlı 404. |
| `/hgs/login/<int:user_id>` | `GET` | `app_bp.hgs_public_paths_disabled` | `hgs_public_paths_disabled` | Eski / hatalı URL'ler — kasıtlı 404. |
| `/holding/api/snapshot` | `GET` | `app_bp.holding_api_snapshot` | `holding_api_snapshot` | Açıklama yok. |
| `/holding/api/tenant/<int:sub_tenant_id>/drilldown` | `GET` | `app_bp.holding_api_drilldown` | `holding_api_drilldown` | Açıklama yok. |
| `/holding/dashboard` | `GET` | `app_bp.holding_dashboard_page` | `holding_dashboard_page` | Açıklama yok. |
| `/holding/tenant/<int:sub_tenant_id>/view` | `GET` | `app_bp.holding_sub_tenant_view_page` | `holding_sub_tenant_view_page` | Açıklama yok. |
| `/k-analiz` | `GET` | `app_bp.k_analiz_hub` | `k_analiz_hub` | K-Analiz alt sayfası — KS-Radar'a yönlendirir (K-Radar hub'undan da erişilebilir). |
| `/k-radar` | `GET` | `app_bp.k_radar_hub` | `k_radar_hub` | K-Radar birleşik hub — Eski K-Rapor sekmeleri + raporlar bir arada. |
| `/k-radar/api/cross/a3` | `GET` | `app_bp.k_radar_api_cross_a3` | `k_radar_api_cross_a3` | Açıklama yok. |
| `/k-radar/api/cross/anket` | `GET` | `app_bp.k_radar_api_cross_anket` | `k_radar_api_cross_anket` | Açıklama yok. |
| `/k-radar/api/cross/paydas` | `GET` | `app_bp.k_radar_api_cross_paydas` | `k_radar_api_cross_paydas` | Açıklama yok. |
| `/k-radar/api/cross/paydas` | `POST` | `app_bp.k_radar_api_cross_paydas_create` | `k_radar_api_cross_paydas_create` | Açıklama yok. |
| `/k-radar/api/cross/paydas/<int:row_id>` | `PUT` | `app_bp.k_radar_api_cross_paydas_update` | `k_radar_api_cross_paydas_update` | Açıklama yok. |
| `/k-radar/api/cross/paydas/<int:row_id>` | `DELETE` | `app_bp.k_radar_api_cross_paydas_delete` | `k_radar_api_cross_paydas_delete` | Açıklama yok. |
| `/k-radar/api/cross/rekabet` | `GET` | `app_bp.k_radar_api_cross_rekabet` | `k_radar_api_cross_rekabet` | Açıklama yok. |
| `/k-radar/api/cross/risk-heatmap` | `GET` | `app_bp.k_radar_api_cross_risk_heatmap` | `k_radar_api_cross_risk_heatmap` | Açıklama yok. |
| `/k-radar/api/hub-summary` | `GET` | `app_bp.k_radar_api_hub_summary` | `k_radar_api_hub_summary` | Açıklama yok. |
| `/k-radar/api/kp` | `GET` | `app_bp.k_radar_api_kp` | `k_radar_api_kp` | Açıklama yok. |
| `/k-radar/api/kp/benchmark` | `GET` | `app_bp.k_radar_api_kp_benchmark` | `k_radar_api_kp_benchmark` | Açıklama yok. |
| `/k-radar/api/kp/darbogaz` | `GET` | `app_bp.k_radar_api_kp_darbogaz` | `k_radar_api_kp_darbogaz` | Açıklama yok. |
| `/k-radar/api/kp/deger-zinciri` | `GET` | `app_bp.k_radar_api_kp_deger_zinciri` | `k_radar_api_kp_deger_zinciri` | Açıklama yok. |
| `/k-radar/api/kp/kapasite` | `GET` | `app_bp.k_radar_api_kp_kapasite` | `k_radar_api_kp_kapasite` | Açıklama yok. |
| `/k-radar/api/kp/oee` | `GET` | `app_bp.k_radar_api_kp_oee` | `k_radar_api_kp_oee` | Açıklama yok. |
| `/k-radar/api/kp/olgunluk` | `GET` | `app_bp.k_radar_api_kp_olgunluk` | `k_radar_api_kp_olgunluk` | Açıklama yok. |
| `/k-radar/api/kp/olgunluk` | `POST` | `app_bp.k_radar_api_kp_olgunluk_create` | `k_radar_api_kp_olgunluk_create` | Açıklama yok. |
| `/k-radar/api/kp/olgunluk/<int:row_id>` | `PUT` | `app_bp.k_radar_api_kp_olgunluk_update` | `k_radar_api_kp_olgunluk_update` | Açıklama yok. |
| `/k-radar/api/kp/olgunluk/<int:row_id>` | `DELETE` | `app_bp.k_radar_api_kp_olgunluk_delete` | `k_radar_api_kp_olgunluk_delete` | Açıklama yok. |
| `/k-radar/api/kp/pareto` | `GET` | `app_bp.k_radar_api_kp_pareto` | `k_radar_api_kp_pareto` | Açıklama yok. |
| `/k-radar/api/kp/radar` | `GET` | `app_bp.k_radar_api_kp_radar` | `k_radar_api_kp_radar` | Süreç olgunluk radarı — 5 boyutta 0-100 skor. |
| `/k-radar/api/kp/sla` | `GET` | `app_bp.k_radar_api_kp_sla` | `k_radar_api_kp_sla` | Açıklama yok. |
| `/k-radar/api/kp/vsm` | `GET` | `app_bp.k_radar_api_kp_vsm` | `k_radar_api_kp_vsm` | Açıklama yok. |
| `/k-radar/api/kpr` | `GET` | `app_bp.k_radar_api_kpr` | `k_radar_api_kpr` | Açıklama yok. |
| `/k-radar/api/kpr/cpm` | `GET` | `app_bp.k_radar_api_kpr_cpm` | `k_radar_api_kpr_cpm` | Açıklama yok. |
| `/k-radar/api/kpr/evm` | `GET` | `app_bp.k_radar_api_kpr_evm` | `k_radar_api_kpr_evm` | Açıklama yok. |
| `/k-radar/api/kpr/gantt` | `GET` | `app_bp.k_radar_api_kpr_gantt` | `k_radar_api_kpr_gantt` | Açıklama yok. |
| `/k-radar/api/kpr/kaynak-kapasite` | `GET` | `app_bp.k_radar_api_kpr_kaynak_kapasite` | `k_radar_api_kpr_kaynak_kapasite` | Açıklama yok. |
| `/k-radar/api/kpr/risk` | `GET` | `app_bp.k_radar_api_kpr_risk` | `k_radar_api_kpr_risk` | Açıklama yok. |
| `/k-radar/api/ks` | `GET` | `app_bp.k_radar_api_ks` | `k_radar_api_ks` | Açıklama yok. |
| `/k-radar/api/ks/ansoff` | `GET` | `app_bp.k_radar_api_ks_ansoff` | `k_radar_api_ks_ansoff` | Açıklama yok. |
| `/k-radar/api/ks/bcg` | `GET` | `app_bp.k_radar_api_ks_bcg` | `k_radar_api_ks_bcg` | Açıklama yok. |
| `/k-radar/api/ks/bsc` | `GET` | `app_bp.k_radar_api_ks_bsc` | `k_radar_api_ks_bsc` | Açıklama yok. |
| `/k-radar/api/ks/efqm` | `GET` | `app_bp.k_radar_api_ks_efqm` | `k_radar_api_ks_efqm` | Açıklama yok. |
| `/k-radar/api/ks/efqm-detail` | `GET` | `app_bp.k_radar_api_ks_efqm_detail` | `k_radar_api_ks_efqm_detail` | EFQM Modeli 2025 — 7 kriter × 3 boyut türev değerlendirmesi (1000 ölçek). |
| `/k-radar/api/ks/gap` | `GET` | `app_bp.k_radar_api_ks_gap` | `k_radar_api_ks_gap` | Açıklama yok. |
| `/k-radar/api/ks/gap-real` | `GET` | `app_bp.k_radar_api_ks_gap_real` | `k_radar_api_ks_gap_real` | Açıklama yok. |
| `/k-radar/api/ks/hoshin` | `GET` | `app_bp.k_radar_api_ks_hoshin` | `k_radar_api_ks_hoshin` | Açıklama yok. |
| `/k-radar/api/ks/okr` | `GET` | `app_bp.k_radar_api_ks_okr` | `k_radar_api_ks_okr` | Açıklama yok. |
| `/k-radar/api/ks/pestel-real` | `GET` | `app_bp.k_radar_api_ks_pestel_real` | `k_radar_api_ks_pestel_real` | Açıklama yok. |
| `/k-radar/api/ks/pestle` | `GET` | `app_bp.k_radar_api_ks_pestle` | `k_radar_api_ks_pestle` | Açıklama yok. |
| `/k-radar/api/ks/porter-real` | `GET` | `app_bp.k_radar_api_ks_porter_real` | `k_radar_api_ks_porter_real` | Açıklama yok. |
| `/k-radar/api/ks/strateji-real` | `GET` | `app_bp.k_radar_api_ks_strateji_real` | `k_radar_api_ks_strateji_real` | Açıklama yok. |
| `/k-radar/api/ks/swot-real` | `GET` | `app_bp.k_radar_api_ks_swot_real` | `k_radar_api_ks_swot_real` | Açıklama yok. |
| `/k-radar/api/ks/swot-summary` | `GET` | `app_bp.k_radar_api_ks_swot_summary` | `k_radar_api_ks_swot_summary` | Açıklama yok. |
| `/k-radar/api/ks/tows` | `GET` | `app_bp.k_radar_api_ks_tows` | `k_radar_api_ks_tows` | Açıklama yok. |
| `/k-radar/api/ks/tows-real` | `GET` | `app_bp.k_radar_api_ks_tows_real` | `k_radar_api_ks_tows_real` | Açıklama yok. |
| `/k-radar/api/recommendations` | `GET` | `app_bp.k_radar_api_recommendations` | `k_radar_api_recommendations` | Açıklama yok. |
| `/k-radar/api/recommendations/action` | `POST` | `app_bp.k_radar_api_recommendation_action` | `k_radar_api_recommendation_action` | Açıklama yok. |
| `/k-radar/api/recommendations/history` | `GET` | `app_bp.k_radar_api_recommendation_history` | `k_radar_api_recommendation_history` | Açıklama yok. |
| `/k-radar/api/recommendations/history.csv` | `GET` | `app_bp.k_radar_api_recommendation_history_csv` | `k_radar_api_recommendation_history_csv` | Açıklama yok. |
| `/k-radar/api/recommendations/triggers` | `GET` | `app_bp.k_radar_api_recommendation_triggers` | `k_radar_api_recommendation_triggers` | Açıklama yok. |
| `/k-radar/api/risk/<int:risk_id>` | `PUT, DELETE` | `app_bp.k_radar_api_risk_modify` | `k_radar_api_risk_modify` | Açıklama yok. |
| `/k-radar/api/risk/add` | `POST` | `app_bp.k_radar_api_risk_add` | `k_radar_api_risk_add` | Yeni risk ekle. |
| `/k-radar/api/risk/list` | `GET` | `app_bp.k_radar_api_risk_list` | `k_radar_api_risk_list` | Aktif riskler listesi + filter. |
| `/k-radar/api/risk/matrix` | `GET` | `app_bp.k_radar_api_risk_matrix` | `k_radar_api_risk_matrix` | 5×5 probability × impact heatmap için count grid. |
| `/k-radar/cross` | `GET` | `app_bp.k_radar_cross` | `k_radar_cross` | Açıklama yok. |
| `/k-radar/cross/a3` | `GET` | `app_bp.k_radar_cross_a3` | `k_radar_cross_a3` | Açıklama yok. |
| `/k-radar/cross/anket` | `GET` | `app_bp.k_radar_cross_anket` | `k_radar_cross_anket` | Açıklama yok. |
| `/k-radar/cross/paydas` | `GET` | `app_bp.k_radar_cross_paydas` | `k_radar_cross_paydas` | Açıklama yok. |
| `/k-radar/cross/paydas/ekle` | `POST` | `app_bp.k_radar_cross_paydas_ekle` | `k_radar_cross_paydas_ekle` | Açıklama yok. |
| `/k-radar/cross/rekabet` | `GET` | `app_bp.k_radar_cross_rekabet` | `k_radar_cross_rekabet` | Açıklama yok. |
| `/k-radar/kp` | `GET` | `app_bp.k_radar_kp` | `k_radar_kp` | Açıklama yok. |
| `/k-radar/kp/benchmark` | `GET` | `app_bp.k_radar_kp_benchmark` | `k_radar_kp_benchmark` | Açıklama yok. |
| `/k-radar/kp/darbogaz` | `GET` | `app_bp.k_radar_kp_darbogaz` | `k_radar_kp_darbogaz` | Açıklama yok. |
| `/k-radar/kp/deger-zinciri` | `GET` | `app_bp.k_radar_kp_deger_zinciri` | `k_radar_kp_deger_zinciri` | Açıklama yok. |
| `/k-radar/kp/kapasite` | `GET` | `app_bp.k_radar_kp_kapasite` | `k_radar_kp_kapasite` | Açıklama yok. |
| `/k-radar/kp/oee` | `GET` | `app_bp.k_radar_kp_oee` | `k_radar_kp_oee` | Açıklama yok. |
| `/k-radar/kp/olgunluk` | `GET` | `app_bp.k_radar_kp_olgunluk` | `k_radar_kp_olgunluk` | Açıklama yok. |
| `/k-radar/kp/olgunluk/ekle` | `POST` | `app_bp.k_radar_kp_olgunluk_ekle` | `k_radar_kp_olgunluk_ekle` | Açıklama yok. |
| `/k-radar/kp/pareto` | `GET` | `app_bp.k_radar_kp_pareto` | `k_radar_kp_pareto` | Açıklama yok. |
| `/k-radar/kp/sla` | `GET` | `app_bp.k_radar_kp_sla` | `k_radar_kp_sla` | Açıklama yok. |
| `/k-radar/kp/vsm` | `GET` | `app_bp.k_radar_kp_vsm` | `k_radar_kp_vsm` | Açıklama yok. |
| `/k-radar/kpr` | `GET` | `app_bp.k_radar_kpr` | `k_radar_kpr` | Açıklama yok. |
| `/k-radar/kpr/cpm` | `GET` | `app_bp.k_radar_kpr_cpm` | `k_radar_kpr_cpm` | Açıklama yok. |
| `/k-radar/kpr/evm` | `GET` | `app_bp.k_radar_kpr_evm` | `k_radar_kpr_evm` | Açıklama yok. |
| `/k-radar/kpr/gantt` | `GET` | `app_bp.k_radar_kpr_gantt` | `k_radar_kpr_gantt` | Açıklama yok. |
| `/k-radar/kpr/kaynak-kapasite` | `GET` | `app_bp.k_radar_kpr_kaynak_kapasite` | `k_radar_kpr_kaynak_kapasite` | Açıklama yok. |
| `/k-radar/kpr/risk` | `GET` | `app_bp.k_radar_kpr_risk` | `k_radar_kpr_risk` | Açıklama yok. |
| `/k-radar/ks` | `GET` | `app_bp.k_radar_ks` | `k_radar_ks` | Açıklama yok. |
| `/k-radar/risk` | `GET` | `app_bp.k_radar_risk_page` | `k_radar_risk_page` | Risk Yönetim ana sayfası. |
| `/k-radar/takvim/kaydet` | `POST` | `app_bp.k_radar_schedule_save` | `k_radar_schedule_save` | Açıklama yok. |
| `/k-rapor` | `GET` | `app_bp.k_rapor` | `k_rapor` | K-Rapor sayfası — ?tab=X seçiliyse o sekme; değilse K-Radar hub'ına yönlendirir. |
| `/k-rapor/anomalies` | `GET` | `app_bp.k_rapor_anomalies_page` | `k_rapor_anomalies_page` | KPI anomali UI sayfası. |
| `/k-rapor/api/aktivite-takvim` | `GET` | `app_bp.k_rapor_api_aktivite_takvim` | `k_rapor_api_aktivite_takvim` | Son 365 günde günlük veri giriş sayısı — GitHub heatmap tarzı. |
| `/k-rapor/api/anomalies` | `GET` | `app_bp.k_rapor_api_anomalies` | `k_rapor_api_anomalies` | Aktif tenant için KPI anomali listesi (Z-score tabanlı). |
| `/k-rapor/api/anomalies/notify-slack` | `POST` | `app_bp.k_rapor_api_anomalies_notify_slack` | `k_rapor_api_anomalies_notify_slack` | Tespit edilen anomalileri Slack'e gönder. |
| `/k-rapor/api/anomalies/notify-webhook` | `POST` | `app_bp.k_rapor_anomalies_notify_webhook` | `k_rapor_anomalies_notify_webhook` | Sprint 45: Anomalileri generic webhook ile gönder. |
| `/k-rapor/api/bildirim-analiz` | `GET` | `app_bp.k_rapor_api_bildirim_analiz` | `k_rapor_api_bildirim_analiz` | Bildirim türü dağılımı, okunma oranı, günlük trend, yaşlanma, kullanıcı bazlı. |
| `/k-rapor/api/bireysel` | `GET` | `app_bp.k_rapor_api_bireysel` | `k_rapor_api_bireysel` | Kullanıcı bazlı bireysel PG — özet + detay + sağlık. |
| `/k-rapor/api/dashboard/widgets` | `GET` | `app_bp.k_rapor_dashboard_widgets` | `k_rapor_dashboard_widgets` | Kullanılabilir widget'ları listele (kategori filtreli). |
| `/k-rapor/api/denetim` | `GET` | `app_bp.k_rapor_api_denetim` | `k_rapor_api_denetim` | Audit log özeti — kim ne yaptı. |
| `/k-rapor/api/digest/preview` | `GET` | `app_bp.k_rapor_digest_preview` | `k_rapor_digest_preview` | Digest mail içeriğini HTML olarak preview et. |
| `/k-rapor/api/digest/send` | `POST` | `app_bp.k_rapor_digest_send` | `k_rapor_digest_send` | Digest mail'i tenant yöneticilerine gönder. |
| `/k-rapor/api/evm` | `GET` | `app_bp.k_rapor_api_evm` | `k_rapor_api_evm` | EVM snapshot — CPI / SPI zaman serisi. |
| `/k-rapor/api/export-excel` | `GET` | `app_bp.k_rapor_api_export_excel` | `k_rapor_api_export_excel` | Seçili tab verisini Excel olarak indir. |
| `/k-rapor/api/export-pdf` | `GET` | `app_bp.k_rapor_api_export_pdf` | `k_rapor_api_export_pdf` | K-Rapor kurumsal özet PDF (executive summary). |
| `/k-rapor/api/faaliyet` | `GET` | `app_bp.k_rapor_api_faaliyet` | `k_rapor_api_faaliyet` | Faaliyet tamamlanma oranı, geciken ve tamamlanan. |
| `/k-rapor/api/faaliyet-matris` | `GET` | `app_bp.k_rapor_api_faaliyet_matris` | `k_rapor_api_faaliyet_matris` | Her süreç için faaliyet durumu dağılımı — yatay bar chart. |
| `/k-rapor/api/forecast/<int:kpi_id>` | `GET` | `app_bp.k_rapor_api_forecast` | `k_rapor_api_forecast` | KPI trend forecasting — linear regression + güven aralığı. |
| `/k-rapor/api/k-vektor` | `GET` | `app_bp.k_rapor_api_k_vektor` | `k_rapor_api_k_vektor` | K-Vektör kota dağılımı ve strateji skorları (compute_k_vektor_bundle). |
| `/k-rapor/api/kurum-karsilastirma` | `GET` | `app_bp.k_rapor_api_kurum_karsilastirma` | `k_rapor_api_kurum_karsilastirma` | Kurumları ortalama PG başarısına göre karşılaştır (yalnız Admin). |
| `/k-rapor/api/kurumsal` | `GET` | `app_bp.k_rapor_api_kurumsal` | `k_rapor_api_kurumsal` | Vizyon skoru + strateji bazlı başarı + en iyi/kötü süreçler. |
| `/k-rapor/api/paydas` | `GET` | `app_bp.k_rapor_api_paydas` | `k_rapor_api_paydas` | Paydaş haritası + anket özeti. |
| `/k-rapor/api/pg-dagilim` | `GET` | `app_bp.k_rapor_api_pg_dagilim` | `k_rapor_api_pg_dagilim` | Tüm PG'lerin başarı yüzdesi dağılımı — histogram + özet. |
| `/k-rapor/api/rekabet` | `GET` | `app_bp.k_rapor_api_rekabet` | `k_rapor_api_rekabet` | Rekabetçi analiz + A3 raporları özeti. |
| `/k-rapor/api/risk` | `GET` | `app_bp.k_rapor_api_risk` | `k_rapor_api_risk` | Risk matrisi + darboğaz + süreç olgunluk. |
| `/k-rapor/api/sorumlu-analiz` | `GET` | `app_bp.k_rapor_api_sorumlu_analiz` | `k_rapor_api_sorumlu_analiz` | Kişi başına faaliyet yükü, tamamlanma ve gecikme oranları. |
| `/k-rapor/api/strateji-kapsama` | `GET` | `app_bp.k_rapor_api_strateji_kapsama` | `k_rapor_api_strateji_kapsama` | Hangi stratejilerin altında süreç yok, hangi süreçler stratejisiz. |
| `/k-rapor/api/stratejik-analiz` | `GET` | `app_bp.k_rapor_api_stratejik_analiz` | `k_rapor_api_stratejik_analiz` | SWOT / TOWS / PESTEL / Porter özet — yıl yoksa en son analizi döner. |
| `/k-rapor/api/surec-pg` | `GET` | `app_bp.k_rapor_api_surec_pg` | `k_rapor_api_surec_pg` | Süreçler × dönemler ısı haritası verisi. |
| `/k-rapor/api/swot-trend` | `GET` | `app_bp.k_rapor_api_swot_trend` | `k_rapor_api_swot_trend` | Yıllar içinde SWOT madde sayıları ve TOWS strateji sayıları. |
| `/k-rapor/api/trend/<int:kpi_id>` | `GET` | `app_bp.k_rapor_api_trend` | `k_rapor_api_trend` | KPI zaman serisi — analytics_service'e delege. |
| `/k-rapor/api/uyari` | `GET` | `app_bp.k_rapor_api_uyari` | `k_rapor_api_uyari` | Uyarı merkezi — kritik PG'ler, geciken faaliyetler, yüksek riskler. |
| `/k-rapor/api/uyum` | `GET` | `app_bp.k_rapor_api_uyum` | `k_rapor_api_uyum` | Strateji → Alt Strateji → Süreç katkı ağacı. |
| `/k-rapor/api/veri-durumu` | `GET` | `app_bp.k_rapor_api_veri_durumu` | `k_rapor_api_veri_durumu` | Aktif plan yılında cari döneme ait PG veri giriş durumu. |
| `/k-rapor/api/webhook/test` | `POST` | `app_bp.k_rapor_webhook_test` | `k_rapor_webhook_test` | Sprint 45: Test mesajı gönder (Slack/Teams/Discord). |
| `/kurum` | `GET` | `app_bp.kurum` | `kurum` | Kurum Paneli ana sayfası — tüm giriş yapmış tenant kullanıcıları; düzenleme API’leri rol ile sınırlı. |
| `/kurum/api/add-strategy` | `POST` | `app_bp.kurum_api_add_strategy` | `kurum_api_add_strategy` | Açıklama yok. |
| `/kurum/api/add-sub-strategy` | `POST` | `app_bp.kurum_api_add_sub_strategy` | `kurum_api_add_sub_strategy` | Açıklama yok. |
| `/kurum/api/delete-main-strategy/<int:strategy_id>` | `POST` | `app_bp.kurum_api_delete_main_strategy` | `kurum_api_delete_main_strategy` | Açıklama yok. |
| `/kurum/api/delete-sub-strategy/<int:sub_id>` | `POST` | `app_bp.kurum_api_delete_sub_strategy` | `kurum_api_delete_sub_strategy` | Açıklama yok. |
| `/kurum/api/k-vektor/weights` | `GET, POST` | `app_bp.kurum_api_k_vektor_weights` | `kurum_api_k_vektor_weights` | Ana / alt strateji ham ağırlıkları (geriye dönük; asıl düzenleme /sp sayfasında). |
| `/kurum/api/overview` | `GET` | `app_bp.kurum_api_overview` | `kurum_api_overview` | Panel özet metrikleri (yenileme / yarı-gerçek zamanlı). |
| `/kurum/api/update-main-strategy/<int:strategy_id>` | `POST` | `app_bp.kurum_api_update_main_strategy` | `kurum_api_update_main_strategy` | Açıklama yok. |
| `/kurum/api/update-strategy` | `POST` | `app_bp.kurum_api_update_strategy` | `kurum_api_update_strategy` | Stratejik kimlik alanlarını güncelle (purpose, vision, core_values, ...). |
| `/kurum/api/update-sub-strategy/<int:sub_id>` | `POST` | `app_bp.kurum_api_update_sub_strategy` | `kurum_api_update_sub_strategy` | Açıklama yok. |
| `/kurum/ayarlar` | `GET, POST` | `app_bp.kurum_ayarlar` | `kurum_ayarlar` | Kurum bilgileri ayarları + logo yükleme. |
| `/launcher` | `GET` | `app_bp.launcher` | `launcher` | Modül launcher ekranı. |
| `/masaustu` | `GET` | `app_bp.masaustu` | `masaustu` | Masaüstüm ana sayfası. |
| `/masaustu-launcher` | `GET` | `app_bp.launcher` | `launcher` | Modül launcher ekranı. |
| `/process` | `GET` | `app_bp.surec` | `surec` | Süreç Yönetimi ana sayfası — hiyerarşik ağaç; erişim rol/atamaya göre filtrelenir. |
| `/process/<int:process_id>/faaliyetler` | `GET` | `app_bp.surec_faaliyetler` | `surec_faaliyetler` | Geriye dönük URL: faaliyet görünümünü karne sayfasında açar. |
| `/process/<int:process_id>/karne` | `GET` | `app_bp.surec_karne` | `surec_karne` | Süreç Karnesi sayfası (PG odaklı). |
| `/process/api/activity/add` | `POST` | `app_bp.surec_api_activity_add` | `surec_api_activity_add` | Açıklama yok. |
| `/process/api/activity/cancel/<int:act_id>` | `POST` | `app_bp.surec_api_activity_cancel` | `surec_api_activity_cancel` | Açıklama yok. |
| `/process/api/activity/complete/<int:act_id>` | `POST` | `app_bp.surec_api_activity_complete` | `surec_api_activity_complete` | Açıklama yok. |
| `/process/api/activity/delete/<int:act_id>` | `POST` | `app_bp.surec_api_activity_delete` | `surec_api_activity_delete` | Açıklama yok. |
| `/process/api/activity/get/<int:act_id>` | `GET` | `app_bp.surec_api_activity_get` | `surec_api_activity_get` | Açıklama yok. |
| `/process/api/activity/postpone/<int:act_id>` | `POST` | `app_bp.surec_api_activity_postpone` | `surec_api_activity_postpone` | Açıklama yok. |
| `/process/api/activity/track/<int:act_id>` | `POST` | `app_bp.surec_api_activity_track` | `surec_api_activity_track` | Faaliyet aylık tamamlanma toggle (upsert). |
| `/process/api/activity/update/<int:act_id>` | `POST` | `app_bp.surec_api_activity_update` | `surec_api_activity_update` | Açıklama yok. |
| `/process/api/add` | `POST` | `app_bp.surec_api_add` | `surec_api_add` | Açıklama yok. |
| `/process/api/delete/<int:process_id>` | `POST` | `app_bp.surec_api_delete` | `surec_api_delete` | Açıklama yok. |
| `/process/api/favorite-kpi/toggle` | `POST` | `app_bp.surec_api_favorite_kpi_toggle` | `surec_api_favorite_kpi_toggle` | Favori KPI ekle/kaldır (legacy process_bp.favorite_kpi_toggle yerine). |
| `/process/api/get/<int:process_id>` | `GET` | `app_bp.surec_api_get` | `surec_api_get` | Açıklama yok. |
| `/process/api/karne/<int:process_id>` | `GET` | `app_bp.surec_api_karne` | `surec_api_karne` | Karne sayfasının yıl bazlı KPI + faaliyet aylık takip verisini döner. |
| `/process/api/karne/<int:process_id>/ai-ozet` | `GET` | `app_bp.surec_api_karne_ai_ozet` | `surec_api_karne_ai_ozet` | Karne üstü 2-3 cümlelik Türkçe yönetici özeti. |
| `/process/api/karne/<int:process_id>/export-xlsx` | `POST` | `app_bp.surec_api_karne_export_xlsx` | `surec_api_karne_export_xlsx` | Karne tablosunu istemcinin ürettiği başlık/satırlarla gerçek .xlsx olarak döner. |
| `/process/api/kpi-data/add` | `POST` | `app_bp.surec_api_kpi_data_add` | `surec_api_kpi_data_add` | Açıklama yok. |
| `/process/api/kpi-data/bulk-import` | `POST` | `app_bp.surec_api_kpi_data_bulk_import` | `surec_api_kpi_data_bulk_import` | Excel'den KPI veri toplu import (dry-run + commit modu). |
| `/process/api/kpi-data/bulk-template` | `GET` | `app_bp.surec_api_kpi_bulk_template` | `surec_api_kpi_bulk_template` | Tenant'ın aktif KPI listesini Excel şablon olarak indirir. |
| `/process/api/kpi-data/delete/<int:data_id>` | `POST, DELETE` | `app_bp.surec_api_kpi_data_delete` | `surec_api_kpi_data_delete` | Açıklama yok. |
| `/process/api/kpi-data/detail` | `GET` | `app_bp.surec_api_kpi_data_detail` | `surec_api_kpi_data_detail` | Kök karne «veri detay» modalı ile uyumlu: periyot bazlı kayıtlar + audit. |
| `/process/api/kpi-data/history/<int:kpi_id>` | `GET` | `app_bp.surec_api_kpi_data_history` | `surec_api_kpi_data_history` | PG’ye ait tüm yıllar + silinmiş kayıtlar (salt okuma listesi). |
| `/process/api/kpi-data/list/<int:kpi_id>` | `GET` | `app_bp.surec_api_kpi_data_list` | `surec_api_kpi_data_list` | Açıklama yok. |
| `/process/api/kpi-data/proje-gorevleri` | `GET` | `app_bp.surec_api_kpi_data_proje_gorevleri` | `surec_api_kpi_data_proje_gorevleri` | Kök API ile uyumlu; proje modülü entegrasyonu yoksa boş liste. |
| `/process/api/kpi-data/template.xlsx` | `GET` | `app_bp.surec_api_kpi_data_template` | `surec_api_kpi_data_template` | Boş Excel şablonu indir. |
| `/process/api/kpi-data/update/<int:data_id>` | `PUT, POST` | `app_bp.surec_api_kpi_data_update` | `surec_api_kpi_data_update` | Açıklama yok. |
| `/process/api/kpi/<int:kpi_id>/score-detail` | `GET` | `app_bp.surec_api_kpi_score_detail` | `surec_api_kpi_score_detail` | KPI başarı puanı hesaplama detayını döner (şeffaflık için). |
| `/process/api/kpi/add` | `POST` | `app_bp.surec_api_kpi_add` | `surec_api_kpi_add` | Açıklama yok. |
| `/process/api/kpi/delete/<int:kpi_id>` | `POST` | `app_bp.surec_api_kpi_delete` | `surec_api_kpi_delete` | Açıklama yok. |
| `/process/api/kpi/get/<int:kpi_id>` | `GET` | `app_bp.surec_api_kpi_get` | `surec_api_kpi_get` | Açıklama yok. |
| `/process/api/kpi/list/<int:process_id>` | `GET` | `app_bp.surec_api_kpi_list` | `surec_api_kpi_list` | Açıklama yok. |
| `/process/api/kpi/update/<int:kpi_id>` | `POST` | `app_bp.surec_api_kpi_update` | `surec_api_kpi_update` | Açıklama yok. |
| `/process/api/resolve-for-year` | `GET` | `app_bp.surec_api_resolve_for_year` | `surec_api_resolve_for_year` | Karne yıl navigasyonu: mevcut process.code + hedef yıl → hedef yılın process_id. |
| `/process/api/sparklines` | `GET` | `app_bp.surec_api_sparklines` | `surec_api_sparklines` | Tenant'ın tüm süreçleri için son 3 ay aylık PG hedef-üstü oranı. |
| `/process/api/update/<int:process_id>` | `POST` | `app_bp.surec_api_update` | `surec_api_update` | Açıklama yok. |
| `/profil` | `GET, POST` | `app_bp.profil` | `profil` | Profil sayfası — GET: form, POST: JSON API güncelleme. |
| `/profil/foto-yukle` | `POST` | `app_bp.profil_foto_yukle` | `profil_foto_yukle` | Profil fotoğrafı yükleme — fiziksel silme yok, sadece DB güncellenir. |
| `/proje` | `GET` | `app_bp.proje_legacy_redirect` | `proje_legacy_redirect` | Açıklama yok. |
| `/project` | `GET` | `app_bp.project_list` | `project_list` | Açıklama yok. |
| `/project/<int:project_id>` | `GET` | `app_bp.project_detail` | `project_detail` | Açıklama yok. |
| `/project/<int:project_id>/delete` | `POST` | `app_bp.project_delete` | `project_delete` | Açıklama yok. |
| `/project/<int:project_id>/edit` | `GET, POST` | `app_bp.project_edit` | `project_edit` | Açıklama yok. |
| `/project/<int:project_id>/strategy` | `GET` | `app_bp.project_strategy` | `project_strategy` | Açıklama yok. |
| `/project/<int:project_id>/strategy/processes` | `POST` | `app_bp.project_strategy_processes` | `project_strategy_processes` | Açıklama yok. |
| `/project/<int:project_id>/task/<int:task_id>` | `GET` | `app_bp.project_task_detail` | `project_task_detail` | Açıklama yok. |
| `/project/<int:project_id>/task/<int:task_id>/delete` | `POST` | `app_bp.project_task_delete` | `project_task_delete` | Açıklama yok. |
| `/project/<int:project_id>/task/<int:task_id>/edit` | `GET, POST` | `app_bp.project_task_edit` | `project_task_edit` | Açıklama yok. |
| `/project/<int:project_id>/task/new` | `GET, POST` | `app_bp.project_task_new` | `project_task_new` | Açıklama yok. |
| `/project/<int:project_id>/views/calendar` | `GET` | `app_bp.project_view_calendar` | `project_view_calendar` | Açıklama yok. |
| `/project/<int:project_id>/views/gantt` | `GET` | `app_bp.project_view_gantt` | `project_view_gantt` | Açıklama yok. |
| `/project/<int:project_id>/views/kanban` | `GET` | `app_bp.project_view_kanban` | `project_view_kanban` | Açıklama yok. |
| `/project/<int:project_id>/views/raid` | `GET` | `app_bp.project_view_raid` | `project_view_raid` | Açıklama yok. |
| `/project/api/task/quick-add` | `POST` | `app_bp.project_task_quick_add` | `project_task_quick_add` | Takvim vb. için JSON ile hızlı proje görevi oluşturma. |
| `/project/bulk-notifications` | `POST` | `app_bp.project_bulk_notifications` | `project_bulk_notifications` | Açıklama yok. |
| `/project/deadlines.ics` | `GET` | `app_bp.project_deadlines_ics` | `project_deadlines_ics` | Açıklama yok. |
| `/project/export.csv` | `GET` | `app_bp.project_export_csv` | `project_export_csv` | Açıklama yok. |
| `/project/new` | `GET, POST` | `app_bp.project_new` | `project_new` | Açıklama yok. |
| `/project/portfolio` | `GET` | `app_bp.project_portfolio` | `project_portfolio` | Açıklama yok. |
| `/raporlar` | `GET` | `app_bp.raporlar_index` | `raporlar_index` | Eski rapor merkezi — K-Radar hub'ı ile birleştirildi, yönlendirir. |
| `/raporlar/ai-coach` | `GET` | `app_bp.raporlar_ai_coach` | `raporlar_ai_coach` | Açıklama yok. |
| `/raporlar/ai-danisman` | `GET` | `app_bp.raporlar_ai_danisman` | `raporlar_ai_danisman` | Açıklama yok. |
| `/raporlar/ai-sunum` | `GET` | `app_bp.raporlar_ai_sunum` | `raporlar_ai_sunum` | Açıklama yok. |
| `/raporlar/api/ai-coach` | `GET` | `app_bp.raporlar_api_ai_coach` | `raporlar_api_ai_coach` | Açıklama yok. |
| `/raporlar/api/ai-danisman` | `GET` | `app_bp.raporlar_api_ai_danisman` | `raporlar_api_ai_danisman` | Açıklama yok. |
| `/raporlar/api/ai-status` | `GET` | `app_bp.raporlar_api_ai_status` | `raporlar_api_ai_status` | Kullanıcının AI kota durumu — BYOK vs sistem anahtarı. |
| `/raporlar/api/ai-sunum/generate` | `GET, POST` | `app_bp.raporlar_api_ai_sunum_generate` | `raporlar_api_ai_sunum_generate` | Gerçek PowerPoint dosyasını üretir + indirme URL'i döner. |
| `/raporlar/api/ai-sunum/preview` | `GET` | `app_bp.raporlar_api_ai_sunum_preview` | `raporlar_api_ai_sunum_preview` | Sunumun veri özetini ve üretilecek slayt başlıklarını döner (preview). |
| `/raporlar/api/audit-paketi/generate` | `GET, POST` | `app_bp.raporlar_api_audit_paketi_generate` | `raporlar_api_audit_paketi_generate` | Açıklama yok. |
| `/raporlar/api/bi/kpi-data.csv` | `GET` | `app_bp.raporlar_api_bi_kpi_data_csv` | `raporlar_api_bi_kpi_data_csv` | KPI ölçümlerini CSV olarak döner (Power BI/Tableau direkt çekebilir). |
| `/raporlar/api/bi/strategies.json` | `GET` | `app_bp.raporlar_api_bi_strategies_json` | `raporlar_api_bi_strategies_json` | Strateji ağacı + skor JSON (BI tool'lar için). |
| `/raporlar/api/bireysel-hizalama` | `GET` | `app_bp.raporlar_api_bireysel_hizalama` | `raporlar_api_bireysel_hizalama` | Açıklama yok. |
| `/raporlar/api/bireysel-karne-batch/generate` | `GET, POST` | `app_bp.raporlar_api_bireysel_karne_batch_generate` | `raporlar_api_bireysel_karne_batch_generate` | Açıklama yok. |
| `/raporlar/api/bireysel-karne-batch/preview` | `GET` | `app_bp.raporlar_api_bireysel_karne_batch_preview` | `raporlar_api_bireysel_karne_batch_preview` | Açıklama yok. |
| `/raporlar/api/carbon-trend` | `GET` | `app_bp.raporlar_api_carbon_trend` | `raporlar_api_carbon_trend` | Açıklama yok. |
| `/raporlar/api/cfo-dashboard` | `GET` | `app_bp.raporlar_api_cfo_dashboard` | `raporlar_api_cfo_dashboard` | Açıklama yok. |
| `/raporlar/api/chro-dashboard` | `GET` | `app_bp.raporlar_api_chro_dashboard` | `raporlar_api_chro_dashboard` | Açıklama yok. |
| `/raporlar/api/cmmi-heatmap` | `GET` | `app_bp.raporlar_api_cmmi_heatmap` | `raporlar_api_cmmi_heatmap` | Açıklama yok. |
| `/raporlar/api/coo-dashboard` | `GET` | `app_bp.raporlar_api_coo_dashboard` | `raporlar_api_coo_dashboard` | Açıklama yok. |
| `/raporlar/api/departman-performans` | `GET` | `app_bp.raporlar_api_departman_performans` | `raporlar_api_departman_performans` | Departman bazlı kullanıcı + bireysel PG + atanan görev sayısı. |
| `/raporlar/api/early-warning` | `GET` | `app_bp.raporlar_api_early_warning` | `raporlar_api_early_warning` | Açıklama yok. |
| `/raporlar/api/esg-rapor/generate` | `GET, POST` | `app_bp.raporlar_api_esg_rapor_generate` | `raporlar_api_esg_rapor_generate` | Açıklama yok. |
| `/raporlar/api/evrim-filmi` | `GET` | `app_bp.raporlar_api_evrim_filmi` | `raporlar_api_evrim_filmi` | Yıllar boyunca strateji ağacının evrimi — her yıl için snapshot. |
| `/raporlar/api/hedef-revizyon` | `GET` | `app_bp.raporlar_api_hedef_revizyon` | `raporlar_api_hedef_revizyon` | Yıl bazlı hedef override sayımı (kpi_year_configs vs ProcessKpi.target_value). |
| `/raporlar/api/hizalama-sankey` | `GET` | `app_bp.raporlar_api_hizalama_sankey` | `raporlar_api_hizalama_sankey` | Vizyon → Strateji → Alt Strateji → Süreç → PG akış verisi (5 seviye). |
| `/raporlar/api/iki-fa` | `GET` | `app_bp.raporlar_api_iki_fa` | `raporlar_api_iki_fa` | Açıklama yok. |
| `/raporlar/api/initiative-bubble` | `GET` | `app_bp.raporlar_api_initiative_bubble` | `raporlar_api_initiative_bubble` | Initiative portföyü: bütçe × ilerleme × öncelik. |
| `/raporlar/api/initiative-roadmap` | `GET` | `app_bp.raporlar_api_initiative_roadmap` | `raporlar_api_initiative_roadmap` | Açıklama yok. |
| `/raporlar/api/k-vektor-carpiklik` | `GET` | `app_bp.raporlar_api_kv_carpiklik` | `raporlar_api_kv_carpiklik` | Her ana stratejinin K-Vektör ağırlığı vs gerçek skor uyumsuzluğu. |
| `/raporlar/api/ml-anomaly` | `GET` | `app_bp.raporlar_api_ml_anomaly` | `raporlar_api_ml_anomaly` | IsolationForest tabanlı KPI anomali tespiti. |
| `/raporlar/api/mobile/snapshot` | `GET` | `app_bp.raporlar_api_mobile_snapshot` | `raporlar_api_mobile_snapshot` | Mobile için kompakt veri snapshot — anasayfa metrikleri. |
| `/raporlar/api/muda-analizi` | `GET` | `app_bp.raporlar_api_muda_analizi` | `raporlar_api_muda_analizi` | Açıklama yok. |
| `/raporlar/api/nlp-query` | `GET, POST` | `app_bp.raporlar_api_nlp_query` | `raporlar_api_nlp_query` | Pattern bazlı + free-form NLP sorgu — tenant filtreli güvenli. |
| `/raporlar/api/nlp-query/patterns` | `GET` | `app_bp.raporlar_api_nlp_patterns` | `raporlar_api_nlp_patterns` | Açıklama yok. |
| `/raporlar/api/okr-cascade` | `GET` | `app_bp.raporlar_api_okr_cascade` | `raporlar_api_okr_cascade` | Açıklama yok. |
| `/raporlar/api/onay-zinciri` | `GET` | `app_bp.raporlar_api_onay_zinciri` | `raporlar_api_onay_zinciri` | Initiative onay zinciri MVP — durum + sorumlu + işlem. |
| `/raporlar/api/operasyon-istatistik` | `GET` | `app_bp.raporlar_api_op_istatistik` | `raporlar_api_op_istatistik` | Açıklama yok. |
| `/raporlar/api/pg-proje-etki` | `GET` | `app_bp.raporlar_api_pg_proje_etki` | `raporlar_api_pg_proje_etki` | Proje × Süreç × PG matrisini ve özet metrikleri döner. |
| `/raporlar/api/quarterly-review` | `GET` | `app_bp.raporlar_api_quarterly_review` | `raporlar_api_quarterly_review` | Açıklama yok. |
| `/raporlar/api/risk-heatmap` | `GET` | `app_bp.raporlar_api_risk_heatmap` | `raporlar_api_risk_heatmap` | Açıklama yok. |
| `/raporlar/api/sabah-ozeti` | `GET` | `app_bp.raporlar_api_sabah_ozeti` | `raporlar_api_sabah_ozeti` | Bugünün ve son 7 günün operasyonel özeti. |
| `/raporlar/api/sektor-benchmark` | `GET` | `app_bp.raporlar_api_sektor_benchmark` | `raporlar_api_sektor_benchmark` | Açıklama yok. |
| `/raporlar/api/sektor-benchmark/ai-yorum` | `POST` | `app_bp.raporlar_api_sektor_benchmark_ai` | `raporlar_api_sektor_benchmark_ai` | AI yorumu isteğe bağlı — butona basılınca çağrılır. |
| `/raporlar/api/sektorel/<code>` | `GET` | `app_bp.raporlar_api_sektorel` | `raporlar_api_sektorel` | Açıklama yok. |
| `/raporlar/api/strateji-hikayesi` | `GET` | `app_bp.raporlar_api_strateji_hikayesi` | `raporlar_api_strateji_hikayesi` | Açıklama yok. |
| `/raporlar/api/stratejik-yillik/generate` | `GET, POST` | `app_bp.raporlar_api_stratejik_yillik_generate` | `raporlar_api_stratejik_yillik_generate` | Açıklama yok. |
| `/raporlar/api/stratejik-yillik/preview` | `GET` | `app_bp.raporlar_api_stratejik_yillik_preview` | `raporlar_api_stratejik_yillik_preview` | Açıklama yok. |
| `/raporlar/api/sunburst` | `GET` | `app_bp.raporlar_api_sunburst` | `raporlar_api_sunburst` | Açıklama yok. |
| `/raporlar/api/veri-kalitesi` | `GET` | `app_bp.raporlar_api_veri_kalitesi` | `raporlar_api_veri_kalitesi` | Veri kalitesi metriklerini JSON döner. |
| `/raporlar/api/vrio-portfoy` | `GET` | `app_bp.raporlar_api_vrio_portfoy` | `raporlar_api_vrio_portfoy` | Açıklama yok. |
| `/raporlar/api/yatirimci-sunum/generate` | `GET, POST` | `app_bp.raporlar_api_yatirimci_sunum_generate` | `raporlar_api_yatirimci_sunum_generate` | Açıklama yok. |
| `/raporlar/api/yatirimci-sunum/preview` | `GET` | `app_bp.raporlar_api_yatirimci_sunum_preview` | `raporlar_api_yatirimci_sunum_preview` | Açıklama yok. |
| `/raporlar/api/yonetici-liderlik` | `GET` | `app_bp.raporlar_api_yonetici_liderlik` | `raporlar_api_yonetici_liderlik` | Süreç liderlerinin liderliğindeki süreçlerin ortalama performans skoru. |
| `/raporlar/audit-paketi` | `GET` | `app_bp.raporlar_audit_paketi` | `raporlar_audit_paketi` | Açıklama yok. |
| `/raporlar/bi-connector` | `GET` | `app_bp.raporlar_bi_connector` | `raporlar_bi_connector` | Açıklama yok. |
| `/raporlar/bireysel-hizalama` | `GET` | `app_bp.raporlar_bireysel_hizalama` | `raporlar_bireysel_hizalama` | Açıklama yok. |
| `/raporlar/bireysel-karne-batch` | `GET` | `app_bp.raporlar_bireysel_karne_batch` | `raporlar_bireysel_karne_batch` | Açıklama yok. |
| `/raporlar/carbon-trend` | `GET` | `app_bp.raporlar_carbon_trend` | `raporlar_carbon_trend` | Açıklama yok. |
| `/raporlar/cfo-dashboard` | `GET` | `app_bp.raporlar_cfo_dashboard` | `raporlar_cfo_dashboard` | Açıklama yok. |
| `/raporlar/chro-dashboard` | `GET` | `app_bp.raporlar_chro_dashboard` | `raporlar_chro_dashboard` | Açıklama yok. |
| `/raporlar/cmmi-heatmap` | `GET` | `app_bp.raporlar_cmmi_heatmap` | `raporlar_cmmi_heatmap` | Açıklama yok. |
| `/raporlar/coo-dashboard` | `GET` | `app_bp.raporlar_coo_dashboard` | `raporlar_coo_dashboard` | Açıklama yok. |
| `/raporlar/departman-performans` | `GET` | `app_bp.raporlar_departman_performans` | `raporlar_departman_performans` | Açıklama yok. |
| `/raporlar/early-warning` | `GET` | `app_bp.raporlar_early_warning` | `raporlar_early_warning` | Açıklama yok. |
| `/raporlar/esg-rapor` | `GET` | `app_bp.raporlar_esg_rapor` | `raporlar_esg_rapor` | Açıklama yok. |
| `/raporlar/evrim-filmi` | `GET` | `app_bp.raporlar_evrim_filmi` | `raporlar_evrim_filmi` | Açıklama yok. |
| `/raporlar/hedef-revizyon` | `GET` | `app_bp.raporlar_hedef_revizyon` | `raporlar_hedef_revizyon` | Açıklama yok. |
| `/raporlar/hizalama-sankey` | `GET` | `app_bp.raporlar_hizalama_sankey` | `raporlar_hizalama_sankey` | Açıklama yok. |
| `/raporlar/iki-fa` | `GET` | `app_bp.raporlar_iki_fa` | `raporlar_iki_fa` | Açıklama yok. |
| `/raporlar/initiative-bubble` | `GET` | `app_bp.raporlar_initiative_bubble` | `raporlar_initiative_bubble` | Açıklama yok. |
| `/raporlar/initiative-roadmap` | `GET` | `app_bp.raporlar_initiative_roadmap` | `raporlar_initiative_roadmap` | Açıklama yok. |
| `/raporlar/k-vektor-carpiklik` | `GET` | `app_bp.raporlar_kv_carpiklik` | `raporlar_kv_carpiklik` | K-Vektör Çarpıklık — strateji ağırlığı × skor uyumsuzluğu. |
| `/raporlar/ml-anomaly` | `GET` | `app_bp.raporlar_ml_anomaly` | `raporlar_ml_anomaly` | Açıklama yok. |
| `/raporlar/mobile` | `GET` | `app_bp.raporlar_mobile` | `raporlar_mobile` | Açıklama yok. |
| `/raporlar/muda-analizi` | `GET` | `app_bp.raporlar_muda_analizi` | `raporlar_muda_analizi` | Açıklama yok. |
| `/raporlar/nlp-query` | `GET` | `app_bp.raporlar_nlp_query` | `raporlar_nlp_query` | Açıklama yok. |
| `/raporlar/okr-cascade` | `GET` | `app_bp.raporlar_okr_cascade` | `raporlar_okr_cascade` | Açıklama yok. |
| `/raporlar/onay-zinciri` | `GET` | `app_bp.raporlar_onay_zinciri` | `raporlar_onay_zinciri` | Açıklama yok. |
| `/raporlar/operasyon-istatistik` | `GET` | `app_bp.raporlar_op_istatistik` | `raporlar_op_istatistik` | Açıklama yok. |
| `/raporlar/pg-proje-etki` | `GET` | `app_bp.raporlar_pg_proje_etki` | `raporlar_pg_proje_etki` | PG × Proje çapraz etki analizi sayfası. |
| `/raporlar/quarterly-review` | `GET` | `app_bp.raporlar_quarterly_review` | `raporlar_quarterly_review` | Açıklama yok. |
| `/raporlar/risk-heatmap` | `GET` | `app_bp.raporlar_risk_heatmap` | `raporlar_risk_heatmap` | Açıklama yok. |
| `/raporlar/sabah-ozeti` | `GET` | `app_bp.raporlar_sabah_ozeti` | `raporlar_sabah_ozeti` | Açıklama yok. |
| `/raporlar/sektor-benchmark` | `GET` | `app_bp.raporlar_sektor_benchmark` | `raporlar_sektor_benchmark` | Açıklama yok. |
| `/raporlar/sektorel` | `GET` | `app_bp.raporlar_sektorel` | `raporlar_sektorel` | Açıklama yok. |
| `/raporlar/sektorel/<code>` | `GET` | `app_bp.raporlar_sektorel_detay` | `raporlar_sektorel_detay` | Açıklama yok. |
| `/raporlar/strateji-hikayesi` | `GET` | `app_bp.raporlar_strateji_hikayesi` | `raporlar_strateji_hikayesi` | Açıklama yok. |
| `/raporlar/stratejik-yillik` | `GET` | `app_bp.raporlar_stratejik_yillik` | `raporlar_stratejik_yillik` | Açıklama yok. |
| `/raporlar/sunburst` | `GET` | `app_bp.raporlar_sunburst` | `raporlar_sunburst` | Açıklama yok. |
| `/raporlar/veri-kalitesi` | `GET` | `app_bp.raporlar_veri_kalitesi` | `raporlar_veri_kalitesi` | Veri Kalitesi Raporu — PG doluluk, eksik alanlar, son giriş tarihleri. |
| `/raporlar/vrio-portfoy` | `GET` | `app_bp.raporlar_vrio_portfoy` | `raporlar_vrio_portfoy` | Açıklama yok. |
| `/raporlar/yatirimci-sunum` | `GET` | `app_bp.raporlar_yatirimci_sunum` | `raporlar_yatirimci_sunum` | Açıklama yok. |
| `/raporlar/yonetici-liderlik` | `GET` | `app_bp.raporlar_yonetici_liderlik` | `raporlar_yonetici_liderlik` | Açıklama yok. |
| `/sp` | `GET` | `app_bp.sp` | `sp` | Stratejik Planlama ana sayfası. |
| `/sp/api/ai-config` | `GET` | `app_bp.sp_api_ai_config_get` | `sp_api_ai_config_get` | Açıklama yok. |
| `/sp/api/ai-config` | `POST` | `app_bp.sp_api_ai_config_save` | `sp_api_ai_config_save` | Açıklama yok. |
| `/sp/api/ai-config` | `DELETE` | `app_bp.sp_api_ai_config_delete` | `sp_api_ai_config_delete` | Açıklama yok. |
| `/sp/api/ai-config/test` | `POST` | `app_bp.sp_api_ai_config_test` | `sp_api_ai_config_test` | Açıklama yok. |
| `/sp/api/ai-pivot` | `POST` | `app_bp.sp_api_ai_pivot` | `sp_api_ai_pivot` | Açıklama yok. |
| `/sp/api/blue-ocean/canvases` | `GET` | `app_bp.sp_api_bo_canvases` | `sp_api_bo_canvases` | Açıklama yok. |
| `/sp/api/blue-ocean/canvases` | `POST` | `app_bp.sp_api_bo_canvas_create` | `sp_api_bo_canvas_create` | Açıklama yok. |
| `/sp/api/blue-ocean/canvases/<int:cid>` | `GET` | `app_bp.sp_api_bo_canvas_detail` | `sp_api_bo_canvas_detail` | Açıklama yok. |
| `/sp/api/blue-ocean/canvases/<int:cid>/errc` | `POST` | `app_bp.sp_api_bo_errc_add` | `sp_api_bo_errc_add` | Açıklama yok. |
| `/sp/api/blue-ocean/canvases/<int:cid>/factors` | `POST` | `app_bp.sp_api_bo_factor_add` | `sp_api_bo_factor_add` | Açıklama yok. |
| `/sp/api/bsc` | `GET` | `app_bp.sp_api_bsc_get` | `sp_api_bsc_get` | BSC verisi: 4 perspektif × KPI'lar + strateji bağlantıları + performans. |
| `/sp/api/bsc/assign` | `POST` | `app_bp.sp_api_bsc_assign` | `sp_api_bsc_assign` | KPI'ya perspektif ata (upsert). |
| `/sp/api/bsc/assign-bulk` | `POST` | `app_bp.sp_api_bsc_assign_bulk` | `sp_api_bsc_assign_bulk` | Birden fazla KPI'ya aynı anda perspektif ata. |
| `/sp/api/bsc/auto-assign` | `POST` | `app_bp.sp_api_bsc_auto_assign` | `sp_api_bsc_auto_assign` | Yüksek güvenli önerileri toplu uygular (min_confidence parametresi ile). |
| `/sp/api/bsc/auto-suggest` | `GET` | `app_bp.sp_api_bsc_auto_suggest` | `sp_api_bsc_auto_suggest` | Atanmamış PG'ler için BSC perspektif önerileri (keyword tabanlı sınıflandırıcı). |
| `/sp/api/bsc/balance` | `GET` | `app_bp.sp_api_bsc_balance` | `sp_api_bsc_balance` | Tenant için BSC denge skoru (Kaplan-Norton ideal %25-%25-%25-%25). |
| `/sp/api/donem-karsilastir` | `GET` | `app_bp.sp_api_donem_karsilastir` | `sp_api_donem_karsilastir` | İki stratejik plan dönemini karşılaştırır ve farkları döner. |
| `/sp/api/exec-ai-ozet` | `GET` | `app_bp.sp_api_exec_ai_ozet` | `sp_api_exec_ai_ozet` | Tenant-geneli 2-3 cümlelik Türkçe yönetici özeti (exec + kurum üstü). |
| `/sp/api/exec-kvektor-trend` | `GET` | `app_bp.sp_api_exec_kvektor_trend` | `sp_api_exec_kvektor_trend` | K-Vektör puanı gelişimi — günlük / aylık / çeyreklik / yıllık seriler. |
| `/sp/api/exec-snapshot` | `GET` | `app_bp.sp_api_exec_snapshot` | `sp_api_exec_snapshot` | Açıklama yok. |
| `/sp/api/exec-strategy-scores` | `GET` | `app_bp.sp_api_exec_strategy_scores` | `sp_api_exec_strategy_scores` | Aktif (veya verilen) yıl için strateji bazlı PG hedef üstü %; top 5 + bottom 5. |
| `/sp/api/exec-trend` | `GET` | `app_bp.sp_api_exec_trend` | `sp_api_exec_trend` | Son 12 ay için aylık PG hedef üstü yüzdesi — sparkline için. |
| `/sp/api/graph` | `GET` | `app_bp.sp_api_graph` | `sp_api_graph` | Vizyon/strateji/alt-strateji/süreç/KPI node ve edge'lerini JSON döndür. |
| `/sp/api/initiatives` | `GET` | `app_bp.sp_api_initiatives_list` | `sp_api_initiatives_list` | Açıklama yok. |
| `/sp/api/initiatives` | `POST` | `app_bp.sp_api_initiatives_create` | `sp_api_initiatives_create` | Açıklama yok. |
| `/sp/api/initiatives/<int:iid>` | `PATCH` | `app_bp.sp_api_initiatives_update` | `sp_api_initiatives_update` | Açıklama yok. |
| `/sp/api/initiatives/<int:iid>` | `DELETE` | `app_bp.sp_api_initiatives_delete` | `sp_api_initiatives_delete` | Açıklama yok. |
| `/sp/api/initiatives/<int:iid>/milestones` | `POST` | `app_bp.sp_api_milestone_create` | `sp_api_milestone_create` | Açıklama yok. |
| `/sp/api/initiatives/<int:iid>/projects` | `GET` | `app_bp.sp_api_initiative_projects` | `sp_api_initiative_projects` | Bir stratejik girişimin altındaki projeleri döner. |
| `/sp/api/k-vektor/weights` | `GET, POST` | `app_bp.sp_api_k_vektor_weights` | `sp_api_k_vektor_weights` | K-Vektör ana/alt strateji ham ağırlıkları — düzenleme Stratejik Planlama (/sp) akışında. |
| `/sp/api/llm-usage/recent` | `GET` | `app_bp.sp_api_llm_recent` | `sp_api_llm_recent` | Açıklama yok. |
| `/sp/api/llm-usage/summary` | `GET` | `app_bp.sp_api_llm_summary` | `sp_api_llm_summary` | Açıklama yok. |
| `/sp/api/okr` | `GET` | `app_bp.sp_api_okr_list` | `sp_api_okr_list` | Aktif plan year için OKR listesi. |
| `/sp/api/okr/kr/<int:kr_id>` | `PUT` | `app_bp.sp_api_okr_kr_update` | `sp_api_okr_kr_update` | Key Result güncelle (ilerleme dahil). |
| `/sp/api/okr/kr/<int:kr_id>` | `DELETE` | `app_bp.sp_api_okr_kr_delete` | `sp_api_okr_kr_delete` | Key Result sil (soft). |
| `/sp/api/okr/objective` | `POST` | `app_bp.sp_api_okr_objective_create` | `sp_api_okr_objective_create` | Yeni Objective ekle. |
| `/sp/api/okr/objective/<int:obj_id>` | `PUT` | `app_bp.sp_api_okr_objective_update` | `sp_api_okr_objective_update` | Objective güncelle. |
| `/sp/api/okr/objective/<int:obj_id>` | `DELETE` | `app_bp.sp_api_okr_objective_delete` | `sp_api_okr_objective_delete` | Objective sil (soft). |
| `/sp/api/okr/objective/<int:obj_id>/kr` | `POST` | `app_bp.sp_api_okr_kr_create` | `sp_api_okr_kr_create` | Key Result ekle. |
| `/sp/api/okr/sync-kpis` | `POST` | `app_bp.sp_api_okr_sync_kpis` | `sp_api_okr_sync_kpis` | Sprint 33: Tüm bağlı KR'leri KPI'larından senkronize et. |
| `/sp/api/pestle` | `GET` | `app_bp.sp_api_pestle_get` | `sp_api_pestle_get` | Aktif plan year için PESTLE verisini döner. |
| `/sp/api/pestle` | `POST` | `app_bp.sp_api_pestle_save` | `sp_api_pestle_save` | PESTLE verisini kaydet (upsert). |
| `/sp/api/plan-years` | `GET` | `app_bp.sp_api_plan_years_list` | `sp_api_plan_years_list` | Tenant'ın tüm plan yıllarını döner. |
| `/sp/api/plan-years` | `POST` | `app_bp.sp_api_plan_years_create` | `sp_api_plan_years_create` | Yeni plan yılı oluşturur. |
| `/sp/api/plan-years/<int:year_id>/close` | `POST` | `app_bp.sp_api_plan_year_close` | `sp_api_plan_year_close` | Plan yılını kapatır (status=closed). |
| `/sp/api/plan-years/<int:year_id>/kpi-configs` | `GET` | `app_bp.sp_api_plan_year_kpi_configs` | `sp_api_plan_year_kpi_configs` | Bir plan yılına ait tüm KPI konfigürasyonlarını döner. |
| `/sp/api/plan-years/<int:year_id>/kpi-configs/<int:kpi_id>` | `POST` | `app_bp.sp_api_plan_year_kpi_config_upsert` | `sp_api_plan_year_kpi_config_upsert` | Tek KPI için yıllık config güncelle/oluştur. |
| `/sp/api/plan-years/<int:year_id>/kpi-configs/bulk` | `POST` | `app_bp.sp_api_plan_year_kpi_configs_bulk` | `sp_api_plan_year_kpi_configs_bulk` | Birden fazla KPI için yıllık config toplu güncelle. |
| `/sp/api/plan-years/set-active` | `POST` | `app_bp.sp_api_plan_years_set_active` | `sp_api_plan_years_set_active` | Aktif plan yılını session'a yazar. |
| `/sp/api/proje` | `GET` | `app_bp.sp_api_proje_list` | `sp_api_proje_list` | Aktif dönemin projelerini listeler. |
| `/sp/api/proje` | `POST` | `app_bp.sp_api_proje_save` | `sp_api_proje_save` | Proje ekle veya güncelle. |
| `/sp/api/proje/<int:item_id>` | `DELETE` | `app_bp.sp_api_proje_delete` | `sp_api_proje_delete` | Açıklama yok. |
| `/sp/api/proje/<int:project_id>/gorev` | `GET` | `app_bp.sp_api_proje_gorev_list` | `sp_api_proje_gorev_list` | Açıklama yok. |
| `/sp/api/proje/<int:project_id>/gorev` | `POST` | `app_bp.sp_api_proje_gorev_save` | `sp_api_proje_gorev_save` | Açıklama yok. |
| `/sp/api/proje/gorev/<int:task_id>` | `DELETE` | `app_bp.sp_api_proje_gorev_delete` | `sp_api_proje_gorev_delete` | Açıklama yok. |
| `/sp/api/projects/<int:pid>/evm` | `GET` | `app_bp.sp_api_project_evm` | `sp_api_project_evm` | Açıklama yok. |
| `/sp/api/projects/<int:pid>/initiative` | `POST` | `app_bp.sp_api_project_set_initiative` | `sp_api_project_set_initiative` | Bir projeyi bir stratejik girişime bağlar (veya bağı keser: initiative_id=null). |
| `/sp/api/quarterly-review` | `GET` | `app_bp.sp_api_quarterly_review` | `sp_api_quarterly_review` | Çeyreklik review JSON. |
| `/sp/api/replan-triggers` | `GET` | `app_bp.sp_api_triggers_list` | `sp_api_triggers_list` | Açıklama yok. |
| `/sp/api/replan-triggers` | `POST` | `app_bp.sp_api_triggers_create` | `sp_api_triggers_create` | Açıklama yok. |
| `/sp/api/replan-triggers/<int:tid>` | `DELETE` | `app_bp.sp_api_triggers_delete` | `sp_api_triggers_delete` | Açıklama yok. |
| `/sp/api/replan-triggers/evaluate` | `POST` | `app_bp.sp_api_triggers_evaluate` | `sp_api_triggers_evaluate` | Tüm trigger'ları şimdi değerlendir (dry_run opsiyonel). |
| `/sp/api/replan-triggers/events` | `GET` | `app_bp.sp_api_triggers_events` | `sp_api_triggers_events` | Açıklama yok. |
| `/sp/api/savas-odasi/fronts` | `GET` | `app_bp.sp_api_savas_odasi_fronts` | `sp_api_savas_odasi_fronts` | Savaş Odası ek cepheleri: alt strateji + süreç (hedef üstü %) + proje (sağlık). |
| `/sp/api/scenarios` | `GET` | `app_bp.sp_api_scenarios_list` | `sp_api_scenarios_list` | Tenant'a ait tüm plan yılları + senaryo ağacı. |
| `/sp/api/scenarios` | `POST` | `app_bp.sp_api_scenario_create` | `sp_api_scenario_create` | Bir plan yılından senaryo dalı oluştur. |
| `/sp/api/scenarios/<int:py_id>` | `DELETE` | `app_bp.sp_api_scenario_delete` | `sp_api_scenario_delete` | Açıklama yok. |
| `/sp/api/scenarios/compare` | `GET` | `app_bp.sp_api_scenarios_compare` | `sp_api_scenarios_compare` | Seçilen plan yılları/senaryoları için vizyon skorlarını salt-okunur hesaplar. |
| `/sp/api/sihirbaz/yeni-yil/preview` | `POST` | `app_bp.sp_api_sihirbaz_preview` | `sp_api_sihirbaz_preview` | Sihirbaz adım 1: yeni yıl ön izleme (mevcut KPI sayısı, süreç sayısı). |
| `/sp/api/sihirbaz/yeni-yil/uygula` | `POST` | `app_bp.sp_api_sihirbaz_uygula` | `sp_api_sihirbaz_uygula` | Sihirbaz adım 3: plan yılı klonlama işlemini uygular. |
| `/sp/api/strategies` | `GET` | `app_bp.sp_api_strategies_list` | `sp_api_strategies_list` | Ana strateji + alt strateji listesi (OKR vb. dropdown'ları için). Aktif kurum/plan yılı. |
| `/sp/api/strategy-project-matrix` | `GET` | `app_bp.sp_api_strategy_project_matrix` | `sp_api_strategy_project_matrix` | Aktif plan yılı için ana strateji × proje hizalama matrisi. |
| `/sp/api/strategy/add` | `POST` | `app_bp.sp_add_strategy` | `sp_add_strategy` | Ana strateji ekle. |
| `/sp/api/strategy/delete/<int:strategy_id>` | `POST` | `app_bp.sp_delete_strategy` | `sp_delete_strategy` | Ana strateji sil (soft delete). |
| `/sp/api/strategy/update/<int:strategy_id>` | `POST` | `app_bp.sp_update_strategy` | `sp_update_strategy` | Ana strateji güncelle. |
| `/sp/api/strateji-haritasi` | `GET` | `app_bp.sp_api_strateji_haritasi` | `sp_api_strateji_haritasi` | Strateji haritası için ağaç verisi döner (SP ile aynı strateji filtresi). |
| `/sp/api/sub-strategy/add` | `POST` | `app_bp.sp_add_sub_strategy` | `sp_add_sub_strategy` | Alt strateji ekle. |
| `/sp/api/sub-strategy/delete/<int:sub_id>` | `POST` | `app_bp.sp_delete_sub_strategy` | `sp_delete_sub_strategy` | Alt strateji soft delete. |
| `/sp/api/sub-strategy/update/<int:sub_id>` | `POST` | `app_bp.sp_update_sub_strategy` | `sp_update_sub_strategy` | Alt strateji güncelle. |
| `/sp/api/swot` | `GET` | `app_bp.sp_api_swot_get` | `sp_api_swot_get` | Aktif plan year için SWOT verisini döner. |
| `/sp/api/swot` | `POST` | `app_bp.sp_api_swot_save` | `sp_api_swot_save` | SWOT verisini kaydet (upsert). |
| `/sp/api/templates` | `GET` | `app_bp.sp_api_templates_list` | `sp_api_templates_list` | Açıklama yok. |
| `/sp/api/templates/<code>` | `GET` | `app_bp.sp_api_template_get` | `sp_api_template_get` | Açıklama yok. |
| `/sp/api/templates/<code>/apply` | `POST` | `app_bp.sp_api_template_apply` | `sp_api_template_apply` | Açıklama yok. |
| `/sp/api/tenant-identity` | `POST` | `app_bp.sp_api_tenant_identity` | `sp_api_tenant_identity` | Tenant amaç/vizyon/değerler/etik alanları. |
| `/sp/api/tows` | `GET` | `app_bp.sp_api_tows_get` | `sp_api_tows_get` | Aktif plan year için TOWS verisini döner. |
| `/sp/api/tows` | `POST` | `app_bp.sp_api_tows_save` | `sp_api_tows_save` | TOWS verisini kaydet (upsert). |
| `/sp/api/vrio` | `GET` | `app_bp.sp_api_vrio_list` | `sp_api_vrio_list` | Açıklama yok. |
| `/sp/api/vrio` | `POST` | `app_bp.sp_api_vrio_create` | `sp_api_vrio_create` | Açıklama yok. |
| `/sp/api/vrio/<int:rid>` | `PATCH` | `app_bp.sp_api_vrio_update` | `sp_api_vrio_update` | Açıklama yok. |
| `/sp/api/vrio/<int:rid>` | `DELETE` | `app_bp.sp_api_vrio_delete` | `sp_api_vrio_delete` | Açıklama yok. |
| `/sp/api/xmatrix` | `GET` | `app_bp.sp_api_xmatrix` | `sp_api_xmatrix` | Açıklama yok. |
| `/sp/ayarlar/ai` | `GET` | `app_bp.sp_ai_settings_page` | `sp_ai_settings_page` | Açıklama yok. |
| `/sp/blue-ocean` | `GET` | `app_bp.sp_blue_ocean_page` | `sp_blue_ocean_page` | Açıklama yok. |
| `/sp/ceyreklik-review` | `GET` | `app_bp.sp_quarterly_review_page` | `sp_quarterly_review_page` | Çeyreklik review sayfası. |
| `/sp/degerler` | `GET` | `app_bp.sp_degerler` | `sp_degerler` | Açıklama yok. |
| `/sp/digest/weekly.html` | `GET` | `app_bp.sp_digest_html` | `sp_digest_html` | Açıklama yok. |
| `/sp/digest/weekly.pdf` | `GET` | `app_bp.sp_digest_pdf` | `sp_digest_pdf` | Açıklama yok. |
| `/sp/donemler` | `GET` | `app_bp.sp_donemler` | `sp_donemler` | SP Dönem yönetimi sayfası. |
| `/sp/exec-dashboard` | `GET` | `app_bp.sp_exec_dashboard` | `sp_exec_dashboard` | Açıklama yok. |
| `/sp/flow` | `GET` | `app_bp.sp_flow` | `sp_flow` | Stratejik planlama akış özet sayfası. |
| `/sp/flow/dynamic` | `GET` | `app_bp.sp_flow_dynamic` | `sp_flow_dynamic` | İnteraktif node-edge görselleştirme sayfası. |
| `/sp/initiatives` | `GET` | `app_bp.sp_initiatives_page` | `sp_initiatives_page` | Açıklama yok. |
| `/sp/llm-usage` | `GET` | `app_bp.sp_llm_usage_page` | `sp_llm_usage_page` | Açıklama yok. |
| `/sp/menu` | `GET` | `app_bp.sp_menu` | `sp_menu` | Stratejik Planlama hub — alt modüller kart görünümünde. |
| `/sp/misyon` | `GET` | `app_bp.sp_misyon` | `sp_misyon` | Açıklama yok. |
| `/sp/okr` | `GET` | `app_bp.sp_okr` | `sp_okr` | OKR (Objectives + Key Results) yönetim sayfası. |
| `/sp/rapor/donemsel` | `GET` | `app_bp.sp_rapor_donemsel` | `sp_rapor_donemsel` | Dönemsel karşılaştırma raporunu Excel olarak indirir. |
| `/sp/replan-triggers` | `GET` | `app_bp.sp_replan_triggers_page` | `sp_replan_triggers_page` | Açıklama yok. |
| `/sp/scenarios` | `GET` | `app_bp.sp_scenarios_page` | `sp_scenarios_page` | Açıklama yok. |
| `/sp/scenarios/kiyas` | `GET` | `app_bp.sp_scenarios_compare_page` | `sp_scenarios_compare_page` | Baseline ⟷ senaryo yan yana kıyas ekranı. |
| `/sp/sihirbaz/yeni-yil` | `GET` | `app_bp.sp_sihirbaz_yeni_yil` | `sp_sihirbaz_yeni_yil` | Plan yılı geçiş sihirbazı sayfası. |
| `/sp/strateji-haritasi` | `GET` | `app_bp.sp_strateji_haritasi` | `sp_strateji_haritasi` | Strateji → Alt Strateji → Süreç → KPI hiyerarşisi görsel haritası. |
| `/sp/strateji-proje-matris` | `GET` | `app_bp.sp_strategy_project_matrix` | `sp_strategy_project_matrix` | Açıklama yok. |
| `/sp/templates` | `GET` | `app_bp.sp_templates_page` | `sp_templates_page` | Açıklama yok. |
| `/sp/tv` | `GET` | `app_bp.sp_tv_mode` | `sp_tv_mode` | Tam ekran TV / war-room KPI duvarı (exec-snapshot verisini döngüyle gösterir). |
| `/sp/vizyon` | `GET` | `app_bp.sp_vizyon` | `sp_vizyon` | Açıklama yok. |
| `/sp/vrio` | `GET` | `app_bp.sp_vrio_page` | `sp_vrio_page` | Açıklama yok. |
| `/sp/xmatrix` | `GET` | `app_bp.sp_xmatrix_page` | `sp_xmatrix_page` | Açıklama yok. |
| `/surec` | `GET` | `app_bp.surec_legacy_index_redirect` | `surec_legacy_index_redirect` | Açıklama yok. |
| `/surec/` | `GET` | `app_bp.surec_legacy_index_redirect` | `surec_legacy_index_redirect` | Açıklama yok. |
| `/surec/<path:subpath>` | `GET` | `app_bp.surec_legacy_path_redirect` | `surec_legacy_path_redirect` | Açıklama yok. |
| `/takvim` | `GET` | `app_bp.kurum_takvim` | `kurum_takvim` | Kurum geneli takvim sayfası. |
| `/tenant-logo/<int:tenant_id>` | `GET` | `app_bp.tenant_logo` | `tenant_logo` | Oturum açan kullanıcı yalnızca kendi kurumunun logosunu veya Admin tüm kurumları görebilir. |

---

### 📦 Blueprint: `auth_bp`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/api/user/delete-my-account` | `POST` | `auth_bp.kvkk_user_delete` | `kvkk_user_delete` | KVKK Madde 7 (silinme hakkı): kullanıcı kendi hesabını anonimleştirir. |
| `/api/user/export-my-data` | `GET` | `auth_bp.kvkk_user_data_export` | `kvkk_user_data_export` | KVKK Madde 11 (veri taşınabilirliği): kullanıcı kendi verisini JSON olarak alır. |
| `/login` | `GET, POST` | `auth_bp.login` | `login` | Handle login form - GET shows form, POST validates credentials. |
| `/logout` | `GET` | `auth_bp.logout` | `logout` | Log out user and redirect to login. |
| `/profile` | `GET, POST` | `auth_bp.profile` | `profile` | Profil sayfası - GET gösterir, POST günceller. |
| `/profile/upload-photo` | `POST` | `auth_bp.upload_profile_photo` | `upload_profile_photo` | Profil fotoğrafı yükle - JSON yanıt. |
| `/settings` | `GET, POST` | `auth_bp.settings` | `settings` | Ayarlar sayfası - GET gösterir, POST günceller. |

---

### 📦 Blueprint: `core_bp`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/kule/send` | `POST` | `core_bp.kule_send` | `kule_send` | Kullanıcıların Kuleye bilet (ticket) gönderme rotası. |
| `/offline.html` | `GET` | `core_bp.offline` | `offline` | PWA offline fallback page. |

---

### 📦 Blueprint: `dataconn_bp`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/api/v1/dataconn/kpi-data` | `GET` | `dataconn_bp.dataconn_kpi_data` | `dataconn_kpi_data` | KPI Data flat JSON — Power BI/Tableau için uygun denormalized format. |
| `/api/v1/dataconn/kpis` | `GET` | `dataconn_bp.dataconn_kpis` | `dataconn_kpis` | KPI tanım listesi. |
| `/api/v1/dataconn/metadata` | `GET` | `dataconn_bp.dataconn_metadata` | `dataconn_metadata` | OData-style metadata + token info (Power BI bağlantı için). |
| `/api/v1/dataconn/processes` | `GET` | `dataconn_bp.dataconn_processes` | `dataconn_processes` | Süreç listesi (Power BI için master data). |

---

### 📦 Blueprint: `hgs_bp`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/` | `GET` | `hgs_bp.index` | `index` | Açıklama yok. |
| `/login/<int:user_id>` | `GET` | `hgs_bp.quick_login` | `quick_login` | Açıklama yok. |

---

### 📦 Blueprint: `kokpitim_project_api`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/api/activities` | `GET` | `kokpitim_project_api.get_user_activities` | `get_user_activities` | Kullanıcının atandığı görevleri ve aktiviteleri getir |
| `/api/admin/users` | `GET` | `kokpitim_project_api.api_admin_users` | `api_admin_users` | Admin panel için kullanıcı listesi |
| `/api/admin/users/<int:user_id>` | `GET` | `kokpitim_project_api.api_admin_user_detail` | `api_admin_user_detail` | Kullanıcı detay bilgisi - Sadece kendi kurumundaki kullanıcılar |
| `/api/admin/users/add` | `POST` | `kokpitim_project_api.api_admin_add_user` | `api_admin_add_user` | Yeni kullanıcı ekle (admin veya kurum_yoneticisi). |
| `/api/admin/users/delete/<int:user_id>` | `DELETE, POST` | `kokpitim_project_api.api_admin_delete_user` | `api_admin_delete_user` | Kullanıcı sil (soft delete) - Admin veya kurum yöneticisi silebilir |
| `/api/admin/users/update/<int:user_id>` | `POST` | `kokpitim_project_api.api_admin_update_user` | `api_admin_update_user` | Admin panel aracılığıyla kullanıcı bilgilerini güncelle |
| `/api/ai-coach/analyze` | `GET, POST` | `kokpitim_project_api.api_ai_coach_analyze` | `api_ai_coach_analyze` | Skor motoru verilerini hesaplayıp AI Coach (Gemini) ile analiz ettirir; Markdown yanıt döner. |
| `/api/ai/insights` | `GET` | `kokpitim_project_api.get_ai_insights` | `get_ai_insights` | AI Insights - Placeholder endpoint |
| `/api/ai/kabul-et` | `POST` | `kokpitim_project_api.api_ai_kabul_et` | `api_ai_kabul_et` | AI önerisini kabul et (mock). |
| `/api/ai/stratejik-oneri` | `POST` | `kokpitim_project_api.api_ai_stratejik_oneri` | `api_ai_stratejik_oneri` | Stratejik AI önerisi (mock). |
| `/api/ai/yeni-oneri` | `POST` | `kokpitim_project_api.api_ai_yeni_oneri` | `api_ai_yeni_oneri` | Yeni AI önerisi (mock). |
| `/api/dashboard/ai-advisor` | `GET` | `kokpitim_project_api.api_ai_advisor` | `api_ai_advisor` | AI Stratejik Danışman verilerini getir |
| `/api/dashboard/ai-advisor/notify` | `POST` | `kokpitim_project_api.api_ai_advisor_notify` | `api_ai_advisor_notify` | AI tavsiyesini ilgili sorumluya bildir |
| `/api/dashboard/executive` | `GET` | `kokpitim_project_api.api_executive_dashboard` | `api_executive_dashboard` | Executive Dashboard verilerini getir |
| `/api/dokuman-merkezi` | `GET, POST` | `kokpitim_project_api.api_dokuman_merkezi` | `api_dokuman_merkezi` | Kurumsal dosya yönetimi API |
| `/api/dokuman-merkezi/<int:file_id>` | `DELETE` | `kokpitim_project_api.api_dokuman_merkezi_sil` | `api_dokuman_merkezi_sil` | Kurumsal dosyayı sil (soft delete) |
| `/api/dokuman-merkezi/<int:file_id>/indir` | `GET` | `kokpitim_project_api.api_dokuman_merkezi_indir` | `api_dokuman_merkezi_indir` | Kurumsal dosyayı indir |
| `/api/kurum/<int:kurum_id>/alt-stratejiler` | `GET` | `kokpitim_project_api.api_kurum_alt_stratejiler` | `api_kurum_alt_stratejiler` | Kurumun tüm alt stratejilerini getir (isteğe bağlı olarak süreçle ilgili olanları filtrele) |
| `/api/kurum/<int:kurum_id>/stratejik-profil` | `GET, POST` | `kokpitim_project_api.api_kurum_stratejik_profil` | `api_kurum_stratejik_profil` | Stratejik profil kaydet/getir (mock/cache). |
| `/api/kurum/toggle-guide-system` | `POST` | `kokpitim_project_api.api_kurum_toggle_guide_system` | `api_kurum_toggle_guide_system` | Kurum için rehber sistemini aç/kapat |
| `/api/kurum/update-logo` | `POST` | `kokpitim_project_api.api_kurum_update_logo` | `api_kurum_update_logo` | Kurum logo URL'sini güncelle |
| `/api/kurum/upload-logo` | `POST` | `kokpitim_project_api.api_kurum_upload_logo` | `api_kurum_upload_logo` | Kurum logosunu yükle |
| `/api/notifications` | `GET` | `kokpitim_project_api.api_notifications` | `api_notifications` | Kullanıcının bildirimlerini getir |
| `/api/notifications` | `GET` | `kokpitim_project_api.api_get_notifications` | `api_get_notifications` | Kullanıcının bildirimlerini getir |
| `/api/notifications/<int:notification_id>/mark-read` | `POST` | `kokpitim_project_api.api_notification_mark_read` | `api_notification_mark_read` | Tek bir bildirimi okundu işaretle |
| `/api/notifications/<int:notification_id>/mark-read` | `POST` | `kokpitim_project_api.api_mark_notification_read` | `api_mark_notification_read` | Bildirimi okundu olarak işaretle |
| `/api/notifications/count` | `GET` | `kokpitim_project_api.api_notifications_count` | `api_notifications_count` | Okunmamış bildirim sayısını getir |
| `/api/notifications/count` | `GET` | `kokpitim_project_api.api_get_notification_count` | `api_get_notification_count` | Okunmamış bildirim sayısını getir |
| `/api/notifications/mark-all-read` | `POST` | `kokpitim_project_api.api_notifications_mark_all_read` | `api_notifications_mark_all_read` | Tüm bildirimleri okundu işaretle |
| `/api/notifications/mark-all-read` | `POST` | `kokpitim_project_api.api_mark_all_notifications_read` | `api_mark_all_notifications_read` | Tüm bildirimleri okundu olarak işaretle |
| `/api/pg-veri/proje-gorevleri` | `GET` | `kokpitim_project_api.api_pg_veri_proje_gorevleri` | `api_pg_veri_proje_gorevleri` | PG veri proje görevleri (mock). |
| `/api/pg-veri/sil/<int:veri_id>` | `DELETE` | `kokpitim_project_api.api_pg_veri_sil` | `api_pg_veri_sil` | PG veri silme (mock/gerçek). |
| `/api/portfoy/ozet` | `GET` | `kokpitim_project_api.api_portfoy_ozet` | `api_portfoy_ozet` | Açıklama yok. |
| `/api/project/<int:project_id>/simulate` | `GET` | `kokpitim_project_api.simulate_project` | `simulate_project` | Proje bazlı What-If simülasyonu (Beta) |
| `/api/projeler` | `GET, POST` | `kokpitim_project_api.api_projeler_list` | `api_projeler_list` | Kullanıcının kurumundaki tüm projeleri getir veya yeni proje oluştur |
| `/api/projeler/<int:project_id>` | `PUT, GET` | `kokpitim_project_api.api_proje_detay` | `api_proje_detay` | Proje detayını getir veya güncelle |
| `/api/projeler/<int:project_id>` | `PUT` | `kokpitim_project_api.api_proje_guncelle` | `api_proje_guncelle` | Proje güncelle |
| `/api/projeler/<int:project_id>/ai-tahmin` | `GET` | `kokpitim_project_api.api_ai_tahmin` | `api_ai_tahmin` | AI destekli gecikme olasılığı tahmini |
| `/api/projeler/<int:project_id>/bagimlilik-matrisi` | `GET` | `kokpitim_project_api.api_proje_bagimlilik_matrisi` | `api_proje_bagimlilik_matrisi` | Açıklama yok. |
| `/api/projeler/<int:project_id>/baseline` | `GET, POST` | `kokpitim_project_api.api_proje_baseline` | `api_proje_baseline` | Açıklama yok. |
| `/api/projeler/<int:project_id>/burn` | `GET` | `kokpitim_project_api.api_proje_burn` | `api_proje_burn` | Açıklama yok. |
| `/api/projeler/<int:project_id>/calisma-gunleri` | `GET, POST` | `kokpitim_project_api.api_proje_calisma_gunleri` | `api_proje_calisma_gunleri` | Açıklama yok. |
| `/api/projeler/<int:project_id>/cpm` | `GET` | `kokpitim_project_api.api_proje_cpm` | `api_proje_cpm` | Açıklama yok. |
| `/api/projeler/<int:project_id>/digest/weekly` | `GET` | `kokpitim_project_api.api_proje_digest` | `api_proje_digest` | Açıklama yok. |
| `/api/projeler/<int:project_id>/dosyalar` | `GET, POST` | `kokpitim_project_api.api_proje_dosyalar` | `api_proje_dosyalar` | Proje dosyalarını getir veya yeni dosya yükle |
| `/api/projeler/<int:project_id>/dosyalar/<int:file_id>` | `DELETE` | `kokpitim_project_api.api_proje_dosya_sil` | `api_proje_dosya_sil` | Proje dosyasını soft-delete ile sil |
| `/api/projeler/<int:project_id>/dosyalar/<int:file_id>/indir` | `GET` | `kokpitim_project_api.api_proje_dosya_indir` | `api_proje_dosya_indir` | Proje dosyasını indir |
| `/api/projeler/<int:project_id>/ekip` | `GET` | `kokpitim_project_api.api_proje_ekip` | `api_proje_ekip` | Açıklama yok. |
| `/api/projeler/<int:project_id>/evm` | `GET` | `kokpitim_project_api.api_proje_evm` | `api_proje_evm` | Proje için basit EVM metriklerini (PV/EV/AC/SPI/CPI) döndür. |
| `/api/projeler/<int:project_id>/gorevler` | `GET` | `kokpitim_project_api.api_proje_gorevler` | `api_proje_gorevler` | Projenin görevlerini getir |
| `/api/projeler/<int:project_id>/gorevler` | `POST` | `kokpitim_project_api.api_gorev_olustur` | `api_gorev_olustur` | Yeni görev oluştur |
| `/api/projeler/<int:project_id>/gorevler/<int:task_id>` | `PUT` | `kokpitim_project_api.api_gorev_guncelle` | `api_gorev_guncelle` | Görev güncelle |
| `/api/projeler/<int:project_id>/gorevler/<int:task_id>` | `DELETE` | `kokpitim_project_api.api_gorev_sil` | `api_gorev_sil` | Görev sil |
| `/api/projeler/<int:project_id>/gorevler/<int:task_id>/asiri-yukleme-kontrol` | `GET` | `kokpitim_project_api.api_asiri_yukleme_kontrol` | `api_asiri_yukleme_kontrol` | Görev atamasının aşırı yükleme yapıp yapmadığını kontrol et |
| `/api/projeler/<int:project_id>/gorevler/<int:task_id>/bagimliliklar` | `GET` | `kokpitim_project_api.api_gorev_bagimliliklar_get` | `api_gorev_bagimliliklar_get` | Bir görevin öncül (predecessor) görevlerini listele (tip ve lag ile). |
| `/api/projeler/<int:project_id>/gorevler/<int:task_id>/bagimliliklar` | `POST` | `kokpitim_project_api.api_gorev_bagimliliklar_set` | `api_gorev_bagimliliklar_set` | Bir görevin öncül (predecessor) görevlerini güncelle (tip ve lag ile). |
| `/api/projeler/<int:project_id>/gorevler/<int:task_id>/yorumlar` | `GET` | `kokpitim_project_api.api_gorev_yorumlari_get` | `api_gorev_yorumlari_get` | Görev yorumlarını getir (task_form.html AJAX) |
| `/api/projeler/<int:project_id>/gorevler/<int:task_id>/yorumlar` | `POST` | `kokpitim_project_api.api_gorev_yorumlari_post` | `api_gorev_yorumlari_post` | Göreve yorum ekle (task_form.html AJAX) |
| `/api/projeler/<int:project_id>/ical` | `GET` | `kokpitim_project_api.api_proje_ical` | `api_proje_ical` | Açıklama yok. |
| `/api/projeler/<int:project_id>/integrations` | `GET, POST` | `kokpitim_project_api.api_proje_integrations` | `api_proje_integrations` | Açıklama yok. |
| `/api/projeler/<int:project_id>/integrations/<int:hook_id>` | `DELETE` | `kokpitim_project_api.api_proje_integration_delete` | `api_proje_integration_delete` | Açıklama yok. |
| `/api/projeler/<int:project_id>/integrations/<int:hook_id>` | `PUT` | `kokpitim_project_api.api_proje_integration_update` | `api_proje_integration_update` | Açıklama yok. |
| `/api/projeler/<int:project_id>/kapasite` | `GET, POST` | `kokpitim_project_api.api_proje_kapasite` | `api_proje_kapasite` | Açıklama yok. |
| `/api/projeler/<int:project_id>/kapasite/<int:plan_id>` | `DELETE` | `kokpitim_project_api.api_proje_kapasite_delete` | `api_proje_kapasite_delete` | Açıklama yok. |
| `/api/projeler/<int:project_id>/kapasite/<int:plan_id>` | `PUT` | `kokpitim_project_api.api_proje_kapasite_update` | `api_proje_kapasite_update` | Açıklama yok. |
| `/api/projeler/<int:project_id>/kaynak-isi-haritasi` | `GET` | `kokpitim_project_api.api_kaynak_isi_haritasi` | `api_kaynak_isi_haritasi` | Proje için kaynak ısı haritası |
| `/api/projeler/<int:project_id>/klonla` | `POST` | `kokpitim_project_api.api_proje_klonla` | `api_proje_klonla` | Projeyi klonla (derin kopyalama) |
| `/api/projeler/<int:project_id>/kurallar` | `GET, POST` | `kokpitim_project_api.api_proje_kurallar` | `api_proje_kurallar` | Açıklama yok. |
| `/api/projeler/<int:project_id>/kurallar/<int:rule_id>` | `DELETE` | `kokpitim_project_api.api_proje_kural_delete` | `api_proje_kural_delete` | Açıklama yok. |
| `/api/projeler/<int:project_id>/kurallar/<int:rule_id>` | `PUT` | `kokpitim_project_api.api_proje_kural_update` | `api_proje_kural_update` | Açıklama yok. |
| `/api/projeler/<int:project_id>/raid` | `GET, POST` | `kokpitim_project_api.api_proje_raid` | `api_proje_raid` | Açıklama yok. |
| `/api/projeler/<int:project_id>/raid/<int:item_id>` | `PUT, DELETE` | `kokpitim_project_api.api_proje_raid_item` | `api_proje_raid_item` | Açıklama yok. |
| `/api/projeler/<int:project_id>/riskler` | `GET` | `kokpitim_project_api.api_proje_riskleri` | `api_proje_riskleri` | Projenin risklerini getir |
| `/api/projeler/<int:project_id>/riskler` | `POST` | `kokpitim_project_api.api_risk_ekle` | `api_risk_ekle` | Yeni risk ekle |
| `/api/projeler/<int:project_id>/riskler/<int:risk_id>` | `PUT` | `kokpitim_project_api.api_risk_guncelle` | `api_risk_guncelle` | Risk güncelle |
| `/api/projeler/<int:project_id>/riskler/<int:risk_id>` | `DELETE` | `kokpitim_project_api.api_risk_sil` | `api_risk_sil` | Risk sil |
| `/api/projeler/<int:project_id>/sla` | `GET, POST` | `kokpitim_project_api.api_proje_sla` | `api_proje_sla` | Açıklama yok. |
| `/api/projeler/<int:project_id>/sla/<int:sla_id>` | `DELETE` | `kokpitim_project_api.api_proje_sla_delete` | `api_proje_sla_delete` | Açıklama yok. |
| `/api/projeler/<int:project_id>/sla/<int:sla_id>` | `PUT` | `kokpitim_project_api.api_proje_sla_update` | `api_proje_sla_update` | Açıklama yok. |
| `/api/projeler/<int:project_id>/tekrarlayan` | `GET, POST` | `kokpitim_project_api.api_proje_tekrarlayan` | `api_proje_tekrarlayan` | Açıklama yok. |
| `/api/projeler/<int:project_id>/tekrarlayan/<int:recurring_id>` | `DELETE` | `kokpitim_project_api.api_proje_tekrarlayan_delete` | `api_proje_tekrarlayan_delete` | Açıklama yok. |
| `/api/projeler/<int:project_id>/tekrarlayan/<int:recurring_id>` | `PUT` | `kokpitim_project_api.api_proje_tekrarlayan_update` | `api_proje_tekrarlayan_update` | Açıklama yok. |
| `/api/rol-matrisi` | `GET` | `kokpitim_project_api.api_rol_matrisi` | `api_rol_matrisi` | Yetki paneli için rol matrisi |
| `/api/rol-matrisi2` | `GET` | `kokpitim_project_api.api_rol_matrisi2` | `api_rol_matrisi2` | Rol matrisi v2 - rol bazlı filtreleme |
| `/api/rol-matrisi2/update` | `POST` | `kokpitim_project_api.api_rol_matrisi2_update` | `api_rol_matrisi2_update` | Kullanıcı bazlı yetki güncelleme (v2) |
| `/api/simulation/what-if` | `POST` | `kokpitim_project_api.api_what_if_simulation` | `api_what_if_simulation` | What-If simülasyonu çalıştır |
| `/api/surec/<int:surec_id>/performans-gostergesi/<int:pg_id>/dagit` | `POST` | `kokpitim_project_api.api_surec_pg_hedef_dagit` | `api_surec_pg_hedef_dagit` | Süreç PG hedefini seçili kullanıcılara dağıt (bireysel hedefler oluşturur/günceller). |
| `/api/surec/<int:surec_id>/saglik-skoru` | `GET` | `kokpitim_project_api.api_surec_saglik_skoru` | `api_surec_saglik_skoru` | Süreç sağlık skorunu hesapla ve döndür |
| `/api/surec/<int:surec_id>/uyeler` | `GET` | `kokpitim_project_api.api_surec_uyeler` | `api_surec_uyeler` | Sürecin üyelerini/liderlerini getir (hedef dağıtım modali için). |
| `/api/task/<int:task_id>/complete` | `POST` | `kokpitim_project_api.api_task_complete` | `api_task_complete` | Görevi tamamla ve proje ilerlemesini güncelle |
| `/api/user/layout` | `POST` | `kokpitim_project_api.api_user_layout` | `api_user_layout` | Kullanıcı layout tercihini kaydet |
| `/api/user/theme` | `POST` | `kokpitim_project_api.api_user_theme` | `api_user_theme` | Kullanıcı tema tercihini kaydet |
| `/api/vision-score` | `GET` | `kokpitim_project_api.api_vision_score` | `api_vision_score` | Point-in-time Vizyon puanı (0-100). as_of_date: YYYY-MM-DD (opsiyonel, varsayılan bugün). |
| `/api/vision-score/recalc` | `POST` | `kokpitim_project_api.api_vision_score_recalc` | `api_vision_score_recalc` | Tüm hiyerarşide vizyon puanını yeniden hesapla ve PG calculated_score alanlarını güncelle (Skor Motoru aktif). |

---

### 📦 Blueprint: `main`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/` | `GET` | `main.index` | `index` | Kök — oturum varsa launcher; yoksa tanıtım (marketing), doğrudan /login değil. |
| `/admin-panel` | `GET` | `main.admin_panel` | `admin_panel` | Admin Panel sayfası - Sistem yöneticileri ve kurum yöneticileri için |
| `/admin/add-organization` | `POST` | `main.admin_add_organization` | `admin_add_organization` | Yeni kurum ekle - Admin tüm kurumları oluşturabilir |
| `/admin/add-process` | `POST` | `main.admin_add_process` | `admin_add_process` | Admin panel için uyumlu süreç ekleme endpoint'i. |
| `/admin/create-process` | `POST` | `main.admin_create_process` | `admin_create_process` | Süreç ekle - admin panel / surec panel modal için |
| `/admin/delete-organization/<int:org_id>` | `DELETE` | `main.admin_delete_organization` | `admin_delete_organization` | Kurum sil (soft delete) - Sadece sistem admini (kurum_id=1) kurumları silebilir |
| `/admin/delete-process/<int:process_id>` | `DELETE` | `main.admin_delete_process` | `admin_delete_process` | Süreç soft-delete - admin panel için |
| `/admin/deleted-organizations` | `GET` | `main.admin_deleted_organizations` | `admin_deleted_organizations` | Silinmiş kurumlar listesi - Sadece sistem admini görebilir |
| `/admin/download-user-template` | `GET` | `main.admin_download_user_template` | `admin_download_user_template` | Kullanıcı içe aktarma şablonunu indir (XLSX). |
| `/admin/feedback` | `GET` | `main.admin_feedback` | `admin_feedback` | Admin - Kule İletişim Modülü Geri Bildirim Yönetimi |
| `/admin/feedback/<int:feedback_id>/detail` | `GET` | `main.get_feedback_detail` | `get_feedback_detail` | Geri bildirim detaylarını getir |
| `/admin/feedback/<int:feedback_id>/update-status` | `POST` | `main.update_feedback_status` | `update_feedback_status` | Geri bildirim durumunu güncelle |
| `/admin/fix-bsc-schema` | `GET` | `main.fix_bsc_schema` | `fix_bsc_schema` | BSC kolonlarını ve bağlantı tablosunu veri kaybı olmadan ekler. |
| `/admin/get-organization/<kisa_ad>` | `GET` | `main.admin_get_organization` | `admin_get_organization` | Kurum bilgilerini getir |
| `/admin/get-process/<int:process_id>` | `GET` | `main.admin_get_process` | `admin_get_process` | Süreç bilgilerini getir - editProcess fonksiyonu için |
| `/admin/restore-organization/<int:org_id>` | `POST` | `main.admin_restore_organization` | `admin_restore_organization` | Kurum geri getir (restore) - Sadece sistem admini restore edebilir |
| `/admin/seed_db` | `GET` | `main.seed_db` | `seed_db` | Veritabanına demo veri ekle - Sadece admin için |
| `/admin/update-organization` | `POST` | `main.admin_update_organization` | `admin_update_organization` | Kurum bilgilerini güncelle - Admin tüm kurumları düzenleyebilir |
| `/admin/update-process/<int:process_id>` | `PUT` | `main.admin_update_process` | `admin_update_process` | Süreç güncelle - updateProcess fonksiyonu için |
| `/admin/upload-logo` | `POST` | `main.admin_upload_logo` | `admin_upload_logo` | Admin tarafından kurum logosu yükleme. |
| `/admin/upload-profile-photo` | `POST` | `main.admin_upload_profile_photo` | `admin_upload_profile_photo` | Admin tarafından kullanıcı profil fotoğrafı yükleme. |
| `/admin/upload-users-excel` | `POST` | `main.admin_upload_users_excel` | `admin_upload_users_excel` | Toplu kullanıcı yükleme (Excel .xlsx). |
| `/ai-chat` | `GET` | `main.ai_chat` | `ai_chat` | AI Chat sayfası |
| `/ai-coach` | `GET` | `main.ai_coach_page` | `ai_coach_page` | AI Coach sayfası - Skor motoru verilerini Gemini ile analiz ettirir. |
| `/akilli-planlama` | `GET` | `main.akilli_planlama` | `akilli_planlama` | Akıllı Planlama sayfası - Geciken görevler için otomatik tarih güncelleme |
| `/api/ai/ask` | `POST` | `main.api_ai_ask` | `api_ai_ask` | AI'ya soru sor |
| `/api/ai/insights` | `GET` | `main.api_ai_insights` | `api_ai_insights` | AI Insight'ları getir |
| `/api/guide/reset-walkthroughs` | `POST` | `main.reset_walkthroughs` | `reset_walkthroughs` | Tüm completed walkthroughs'u sıfırla |
| `/api/guide/update-preferences` | `POST` | `main.update_guide_preferences` | `update_guide_preferences` | Kullanıcının guide tercihlerini güncelle |
| `/api/guide/update-settings` | `POST` | `main.update_guide_settings` | `update_guide_settings` | Kullanıcının guide ayarlarını güncelle (settings sayfasından) |
| `/api/kullanici/sureclerim` | `GET` | `main.api_kullanici_surecleri` | `api_kullanici_surecleri` | Kullanıcının üye/lider olduğu süreçleri getir - Kurum yöneticileri tüm süreçleri görür |
| `/api/muda-hunter/analyze/<int:surec_id>` | `POST` | `main.muda_analyze` | `muda_analyze` | Süreç verimsizlik analizi API |
| `/api/muda-hunter/efficiency-score` | `GET` | `main.muda_efficiency_score` | `muda_efficiency_score` | Genel verimlilik skoru API |
| `/api/strategic-planning/graph` | `GET` | `main.api_strategic_planning_graph` | `api_strategic_planning_graph` | Dinamik SP akışı için graf verisini döndürür (nodes/edges + skorlar). |
| `/black-swan` | `GET` | `main.black_swan` | `black_swan` | Siyah Kuğu Simülatörü (Doomsday Prepper) sayfası |
| `/competencies` | `GET` | `main.competencies` | `competencies` | Yetkinlik Matrisi sayfası |
| `/crisis` | `GET` | `main.crisis` | `crisis` | Kriz Komuta Merkezi sayfası |
| `/crisis/add` | `POST` | `main.crisis_add` | `crisis_add` | Yeni kriz ekle |
| `/dashboard` | `GET` | `main.dashboard` | `dashboard` | Dashboard sayfası - Ana gösterge paneli (V67 - Güncel) |
| `/dashboard/executive` | `GET` | `main.executive_dashboard` | `executive_dashboard` | Yönetim Kokpiti - Executive Dashboard |
| `/debug/fix_and_reset` | `GET` | `main.debug_fix_and_reset` | `debug_fix_and_reset` | Test ortamını sıfırla ve eksik referansları tamamla |
| `/debug/force_trigger/<int:task_id>` | `GET` | `main.debug_force_trigger` | `debug_force_trigger` | Manuel otomasyon tetikleme testi |
| `/debug/init_strategy_db` | `GET` | `main.debug_init_strategy_db` | `debug_init_strategy_db` | Stratejik Planlama V3.0 veritabanı migration - Yeni tabloları ve ilişkileri oluşturur |
| `/debug/init_strategy_v3` | `GET` | `main.debug_init_strategy_v3` | `debug_init_strategy_v3` | Stratejik Planlama V3.0 veritabanı initialization - Excel yapısına göre tabloları oluşturur |
| `/debug/monitor` | `GET` | `main.debug_monitor` | `debug_monitor` | Canlı izleme paneli - Son görevler ve PG verileri |
| `/debug/schema_check` | `GET` | `main.debug_schema_check` | `debug_schema_check` | Veritabanı şema kontrolü - Task tablosu sütunlarını kontrol et |
| `/debug/surec-data` | `GET` | `main.debug_surec_data` | `debug_surec_data` | Debug endpoint - kullanıcının süreçlerini ve PG sayılarını göster |
| `/deep-work/toggle` | `POST` | `main.deep_work_toggle` | `deep_work_toggle` | Deep Work oturumu başlat/durdur |
| `/dokuman-merkezi` | `GET` | `main.dokuman_merkezi` | `dokuman_merkezi` | Kurumsal dosya yönetimi sayfası |
| `/executive-report` | `GET` | `main.executive_report` | `executive_report` | Yönetim Kurulu Özeti sayfası |
| `/game-theory` | `GET` | `main.game_theory` | `game_theory` | Oyun Teorisi (Game Theory Grid) sayfası |
| `/game-theory/scenario/<int:scenario_id>/calculate-nash` | `POST` | `main.calculate_nash_for_scenario` | `calculate_nash_for_scenario` | Belirli bir senaryo için Nash dengesi hesapla |
| `/gemba` | `GET` | `main.gemba` | `gemba` | Gemba Walk sayfası - Dijital Gemba |
| `/gemba/add` | `POST` | `main.gemba_add` | `gemba_add` | Yeni Gemba Walk kaydı ekleme |
| `/gorev-aktivite-log` | `GET` | `main.gorev_aktivite_log` | `gorev_aktivite_log` | Görev Aktivite Log sayfası - Görev değişiklik geçmişi |
| `/gorevlerim` | `GET` | `main.gorevlerim` | `gorevlerim` | Görevlerim sayfası - Kullanıcıya atanmış faaliyetler |
| `/governance` | `GET` | `main.governance` | `governance` | DAO Yönetimi sayfası |
| `/hgs` | `GET` | `main.hizli_giris` | `hizli_giris` | Hızlı giriş sayfası - Şifresiz direkt giriş paneli |
| `/knowledge-graph` | `GET` | `main.knowledge_graph` | `knowledge_graph` | Bilgi Grafığı sayfası |
| `/kurum-paneli` | `GET` | `main.kurum_paneli` | `kurum_paneli` | Stratejik Yönetim Kokpiti |
| `/kurum-yonetim` | `GET` | `main.kurum_yonetim_page` | `kurum_yonetim_page` | Kurum Yönetimi sayfası |
| `/kurum/alt-stratejiler/add` | `POST` | `main.add_alt_strateji` | `add_alt_strateji` | Yeni alt strateji ekle |
| `/kurum/alt-stratejiler/delete/<int:id>` | `POST` | `main.delete_alt_strateji` | `delete_alt_strateji` | Alt stratejiyi sil |
| `/kurum/alt-stratejiler/update/<int:id>` | `POST` | `main.update_alt_strateji` | `update_alt_strateji` | Alt stratejiyi güncelle |
| `/kurum/ana-stratejiler/add` | `POST` | `main.add_ana_strateji` | `add_ana_strateji` | Yeni ana strateji ekle |
| `/kurum/ana-stratejiler/delete/<int:id>` | `POST` | `main.delete_ana_strateji` | `delete_ana_strateji` | Ana stratejiyi sil |
| `/kurum/ana-stratejiler/update/<int:id>` | `POST` | `main.update_ana_strateji` | `update_ana_strateji` | Ana stratejiyi güncelle |
| `/kurum/degerler/add` | `POST` | `main.add_deger` | `add_deger` | Yeni kurum değeri ekle |
| `/kurum/degerler/delete/<int:id>` | `POST` | `main.delete_deger` | `delete_deger` | Kurum değerini sil |
| `/kurum/degerler/update/<int:id>` | `POST` | `main.update_deger` | `update_deger` | Kurum değerini güncelle |
| `/kurum/etik-kurallari/add` | `POST` | `main.add_etik_kural` | `add_etik_kural` | Yeni etik kural ekle |
| `/kurum/etik-kurallari/delete/<int:id>` | `POST` | `main.delete_etik_kural` | `delete_etik_kural` | Etik kuralı sil |
| `/kurum/etik-kurallari/update/<int:id>` | `POST` | `main.update_etik_kural` | `update_etik_kural` | Etik kuralı güncelle |
| `/kurum/kalite-politikalari/add` | `POST` | `main.add_kalite_politikasi` | `add_kalite_politikasi` | Yeni kalite politikası ekle |
| `/kurum/kalite-politikalari/delete/<int:id>` | `POST` | `main.delete_kalite_politikasi` | `delete_kalite_politikasi` | Kalite politikasını sil |
| `/kurum/kalite-politikalari/update/<int:id>` | `POST` | `main.update_kalite_politikasi` | `update_kalite_politikasi` | Kalite politikasını güncelle |
| `/kurum/update-amac-vizyon` | `POST` | `main.update_amac_vizyon` | `update_amac_vizyon` | Kurum amaç ve vizyonunu güncelle |
| `/legacy-chat` | `GET` | `main.legacy_chat` | `legacy_chat` | Kurucu Miras AI sayfası |
| `/library` | `GET` | `main.library` | `library` | Omega'nın Kitabı (Auto-Biography) sayfası |
| `/market-watch` | `GET` | `main.market_watch` | `market_watch` | Market Watcher sayfası |
| `/metaverse` | `GET` | `main.metaverse` | `metaverse` | Metaverse Departman İkizi sayfası |
| `/mtbp` | `GET` | `main.mtbp` | `mtbp` | Mid-Term Business Plan (MTBP) sayfası |
| `/mtbp/add` | `POST` | `main.mtbp_add` | `mtbp_add` | Yeni MTBP planı ekleme |
| `/muda-hunter` | `GET` | `main.muda_hunter` | `muda_hunter` | Muda Hunter sayfası - Süreç Verimsizlik Analizi |
| `/offline` | `GET` | `main.offline` | `offline` | Offline sayfası - PWA için |
| `/okr/<int:objective_id>/comment` | `POST` | `main.okr_comment` | `okr_comment` | OKR/Hedef yorum ekleme - Hoshin Catchball |
| `/ona` | `GET` | `main.ona` | `ona` | ONA (Organizasyonel Ağ Analizi) sayfası |
| `/performans-kartim` | `GET` | `main.performans_kartim` | `performans_kartim` | Performans Kartım sayfası - Bireysel performans göstergeleri |
| `/portfoy-ozeti` | `GET` | `main.portfolio_summary` | `portfolio_summary` | Açıklama yok. |
| `/proje-analitik` | `GET` | `main.proje_analitik` | `proje_analitik` | Proje Analitik sayfası - Süreç sağlık skoru ve analitik raporlar |
| `/projeler` | `GET` | `main.projeler` | `projeler` | Kök /kok/projeler → Micro proje listesi (/project). |
| `/projeler/<int:project_id>` | `GET` | `main.proje_detay` | `proje_detay` | Proje detay → Micro (/project/<id>). |
| `/projeler/<int:project_id>/bagimlilik-matrisi` | `GET` | `main.project_dependency_matrix` | `project_dependency_matrix` | Açıklama yok. |
| `/projeler/<int:project_id>/baseline` | `GET` | `main.project_baseline` | `project_baseline` | Açıklama yok. |
| `/projeler/<int:project_id>/calisma-gunleri` | `GET` | `main.project_workdays` | `project_workdays` | Açıklama yok. |
| `/projeler/<int:project_id>/cpm` | `GET` | `main.project_cpm` | `project_cpm` | Açıklama yok. |
| `/projeler/<int:project_id>/duzenle` | `GET` | `main.proje_duzenle` | `proje_duzenle` | Proje düzenleme → Micro (/project/<id>/edit). |
| `/projeler/<int:project_id>/gantt` | `GET` | `main.project_gantt` | `project_gantt` | Açıklama yok. |
| `/projeler/<int:project_id>/gorevler/<int:task_id>` | `GET` | `main.gorev_detay` | `gorev_detay` | Görev detay → Micro (/project/<pid>/task/<tid>). |
| `/projeler/<int:project_id>/gorevler/yeni` | `GET` | `main.gorev_yeni` | `gorev_yeni` | Yeni görev → Micro (/project/<id>/task/new). |
| `/projeler/<int:project_id>/integrations` | `GET` | `main.project_integrations` | `project_integrations` | Açıklama yok. |
| `/projeler/<int:project_id>/kanban` | `GET` | `main.project_kanban` | `project_kanban` | Açıklama yok. |
| `/projeler/<int:project_id>/kapasite` | `GET` | `main.project_capacity` | `project_capacity` | Açıklama yok. |
| `/projeler/<int:project_id>/kurallar` | `GET` | `main.project_rules` | `project_rules` | Açıklama yok. |
| `/projeler/<int:project_id>/raid` | `GET` | `main.project_raid` | `project_raid` | Açıklama yok. |
| `/projeler/<int:project_id>/sla` | `GET` | `main.project_sla` | `project_sla` | Açıklama yok. |
| `/projeler/<int:project_id>/takvim` | `GET` | `main.project_calendar` | `project_calendar` | Açıklama yok. |
| `/projeler/<int:project_id>/tekrarlayan` | `GET` | `main.project_recurring` | `project_recurring` | Açıklama yok. |
| `/projeler/yeni` | `GET` | `main.proje_yeni` | `proje_yeni` | Yeni proje → Micro form (/project/new). |
| `/redmine` | `GET` | `main.redmine` | `redmine` | Faaliyetler Sayfası (V67 - Güncel) |
| `/reorg` | `GET` | `main.reorg` | `reorg` | Dinamik Organizasyon Tasarımcısı sayfası |
| `/risks` | `GET` | `main.risks` | `risks` | Stratejik Risk Yönetimi sayfası |
| `/risks/add` | `POST` | `main.risks_add` | `risks_add` | Yeni risk ekle |
| `/setup_test_pg_automation` | `GET` | `main.setup_test_pg_automation` | `setup_test_pg_automation` | Test için PG otomasyonu hazırlama route'u (Geçici) |
| `/simulation` | `GET` | `main.simulation` | `simulation` | Monte Carlo Simülatörü sayfası |
| `/simulation/<int:scenario_id>/run` | `POST` | `main.simulation_run` | `simulation_run` | Simülasyon çalıştır |
| `/simulation/add` | `POST` | `main.simulation_add` | `simulation_add` | Yeni simülasyon senaryosu ekle |
| `/sistem-degisiklik-gunlugu` | `GET` | `main.sistem_degisiklik_gunlugu` | `sistem_degisiklik_gunlugu` | Sistem Değişiklik Günlüğü - Audit Trail UI |
| `/strategy/kpi/add` | `POST` | `main.strategy_kpi_add` | `strategy_kpi_add` | Yeni KPI ekle |
| `/strategy/kpis` | `GET` | `main.strategy_kpis` | `strategy_kpis` | KPI Yönetim Paneli - Performans Göstergeleri Listesi |
| `/strategy/matrix` | `GET` | `main.strategy_matrix` | `strategy_matrix` | Strateji-Süreç Matrisi görüntüleme sayfası |
| `/strategy/project/<int:id>` | `GET` | `main.strategy_project_detail` | `strategy_project_detail` | Stratejik Proje Detay Sayfası - Projenin stratejik uyum analizi |
| `/strategy/project/<int:id>/clone` | `POST` | `main.strategy_project_clone` | `strategy_project_clone` | Projeyi klonla (kopyala) |
| `/strategy/project/<int:id>/delete` | `POST` | `main.strategy_project_delete` | `strategy_project_delete` | Projeyi sil |
| `/strategy/project/<int:id>/edit` | `POST` | `main.strategy_project_edit` | `strategy_project_edit` | Proje bilgilerini güncelle |
| `/strategy/project/<int:id>/update_processes` | `POST` | `main.strategy_project_update_processes` | `strategy_project_update_processes` | Proje-Süreç ilişkilerini güncelle |
| `/strategy/project/add` | `POST` | `main.strategy_project_add` | `strategy_project_add` | Yeni proje oluştur |
| `/strategy/projects` | `GET` | `main.strategy_projects` | `strategy_projects` | Stratejik Proje Portföyü - Projeleri stratejik puana göre sırala |
| `/strategy/update_cell` | `POST` | `main.update_strategy_cell` | `update_strategy_cell` | Strateji-Süreç matris hücresini güncelle (Toggle: Yok->9->3->Sil) |
| `/stratejik-asistan` | `GET` | `main.stratejik_asistan` | `stratejik_asistan` | Stratejik Asistan sayfası |
| `/stratejik-planlama-akisi` | `GET` | `main.stratejik_planlama_akisi` | `stratejik_planlama_akisi` | SP Akış Diyagramı sayfası |
| `/stratejik-planlama-akisi/dinamik` | `GET` | `main.stratejik_planlama_akisi_dinamik` | `stratejik_planlama_akisi_dinamik` | Dinamik SP Akış (graf) sayfası |
| `/submit-feedback` | `POST` | `main.submit_feedback` | `submit_feedback` | Kule İletişim Modülü - Geri Bildirim Gönderme |
| `/succession` | `GET` | `main.succession` | `succession` | Halefiyet Planlaması sayfası |
| `/surec-karnesi` | `GET` | `main.surec_karnesi` | `surec_karnesi` | Süreç Karnesi sayfası - Kullanıcı sadece kendi süreçlerini görür |
| `/surec-paneli` | `GET` | `main.surec_paneli` | `surec_paneli` | Süreç Paneli sayfası - Süreç yönetimi ve listesi |
| `/surec/<int:surec_id>` | `GET` | `main.get_surec` | `get_surec` | Süreç detaylarını getir - viewSurec fonksiyonu için |
| `/surec/<int:surec_id>/faaliyet/<int:faaliyet_id>` | `GET` | `main.get_surec_faaliyet_detay` | `get_surec_faaliyet_detay` | Süreç faaliyeti detayını getir - surec_karnesi.html editFaaliyet() için |
| `/surec/<int:surec_id>/faaliyet/<int:faaliyet_id>/delete` | `DELETE` | `main.delete_surec_faaliyet` | `delete_surec_faaliyet` | Süreç faaliyeti sil - surec_karnesi.html deleteFaaliyet() için |
| `/surec/<int:surec_id>/faaliyet/<int:faaliyet_id>/update` | `POST` | `main.update_surec_faaliyet` | `update_surec_faaliyet` | Süreç faaliyeti güncelle - surec_karnesi.html updateFaaliyet() için |
| `/surec/<int:surec_id>/faaliyet/add` | `POST` | `main.add_surec_faaliyet` | `add_surec_faaliyet` | Süreç faaliyeti ekle - surec_karnesi.html addFaaliyet() için |
| `/surec/<int:surec_id>/faaliyetler` | `GET` | `main.get_surec_faaliyetler` | `get_surec_faaliyetler` | Süreç faaliyetlerini getir |
| `/surec/<int:surec_id>/performans-gostergesi/<int:pg_id>` | `GET` | `main.surec_performans_gostergesi_get` | `surec_performans_gostergesi_get` | Süreç için performans göstergesi bilgilerini getir |
| `/surec/<int:surec_id>/performans-gostergesi/<int:pg_id>/delete` | `DELETE` | `main.surec_performans_gostergesi_delete` | `surec_performans_gostergesi_delete` | Süreç için performans göstergesini sil |
| `/surec/<int:surec_id>/performans-gostergesi/<int:pg_id>/update` | `POST` | `main.surec_performans_gostergesi_update` | `surec_performans_gostergesi_update` | Süreç için performans göstergesini güncelle |
| `/surec/<int:surec_id>/performans-gostergesi/add` | `POST` | `main.surec_performans_gostergesi_add` | `surec_performans_gostergesi_add` | Süreç için yeni performans göstergesi ekle |
| `/surec/add-simple` | `POST` | `main.surec_add_simple` | `surec_add_simple` | Süreç ekle - surec_panel.html form submit için |
| `/surec/delete/<int:surec_id>` | `DELETE` | `main.surec_delete` | `surec_delete` | Süreç soft-delete |
| `/surec/get/<int:surec_id>` | `GET` | `main.surec_get_for_edit` | `surec_get_for_edit` | Süreç bilgilerini getir - surec_panel.html editSurec() için |
| `/surec/update/<int:surec_id>` | `POST` | `main.update_surec` | `update_surec` | Süreç güncelle - updateSurec fonksiyonu için |
| `/synthetic-lab` | `GET` | `main.synthetic_lab` | `synthetic_lab` | Sentetik Müşteri Laboratuvarı sayfası |
| `/v3/kurum-paneli` | `GET` | `main.kurum_paneli_v3` | `kurum_paneli_v3` | Stratejik Yönetim Kokpiti V3 (Dual Mode: Standard + Visual) |
| `/v3/kurum-paneli/visual` | `GET` | `main.kurum_paneli_visual` | `kurum_paneli_visual` | Stratejik Yönetim Kokpiti - Görsel Mod (Sadece ECharts) |
| `/v3/skor-motoru` | `GET` | `main.skor_motoru_detay` | `skor_motoru_detay` | Skor Motoru detay sayfası: Vizyon puanı, ana/alt strateji, süreç ve PG skorları (API'den). |
| `/wellbeing` | `GET` | `main.wellbeing` | `wellbeing` | Tükenmişlik Kalkanı sayfası |
| `/yardim-merkezi` | `GET` | `main.help_center` | `help_center` | İnteraktif Yardım Merkezi |
| `/zaman-takibi` | `GET` | `main.zaman_takibi` | `zaman_takibi` | Zaman Takibi (Timesheet) sayfası |

---

### 📦 Blueprint: `marketing_bp`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/` | `GET` | `marketing_bp.index` | `index` | Açıklama yok. |
| `/blog` | `GET` | `marketing_bp.blog_index` | `blog_index` | Açıklama yok. |
| `/blog/<slug>` | `GET` | `marketing_bp.blog_post` | `blog_post` | Açıklama yok. |
| `/demo-talep` | `GET, POST` | `marketing_bp.demo_talep` | `demo_talep` | Açıklama yok. |
| `/home` | `GET` | `marketing_bp.index` | `index` | Açıklama yok. |
| `/iletisim` | `GET, POST` | `marketing_bp.iletisim` | `iletisim` | Açıklama yok. |
| `/nasil-calisir` | `GET` | `marketing_bp.nasil_calisir` | `nasil_calisir` | Açıklama yok. |
| `/ozellikler` | `GET` | `marketing_bp.ozellikler` | `ozellikler` | Açıklama yok. |
| `/ozellikler/analiz-merkezi` | `GET` | `marketing_bp.analiz_merkezi` | `analiz_merkezi` | Açıklama yok. |
| `/ozellikler/performans-takibi` | `GET` | `marketing_bp.performans_takibi` | `performans_takibi` | Açıklama yok. |
| `/ozellikler/proje-yonetimi` | `GET` | `marketing_bp.proje_yonetimi` | `proje_yonetimi` | Açıklama yok. |
| `/ozellikler/stratejik-planlama` | `GET` | `marketing_bp.stratejik_planlama` | `stratejik_planlama` | Açıklama yok. |
| `/ozellikler/surec-yonetimi` | `GET` | `marketing_bp.surec_yonetimi` | `surec_yonetimi` | Açıklama yok. |
| `/robots.txt` | `GET` | `marketing_bp.robots` | `robots` | Açıklama yok. |
| `/sitemap.xml` | `GET` | `marketing_bp.sitemap` | `sitemap` | Açıklama yok. |

---

### 📦 Blueprint: `process_performance_api`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/api/export/surec_karnesi/excel` | `GET` | `process_performance_api.route_export_surec_karnesi_excel` | `route_export_surec_karnesi_excel` | Açıklama yok. |
| `/api/faaliyet/<int:faaliyet_id>/takip` | `POST` | `process_performance_api.api_faaliyet_takip_kaydet` | `api_faaliyet_takip_kaydet` | Bireysel faaliyetin aylık takibini kaydet (Process API Controller). |
| `/api/pg-veri/detay/<int:veri_id>` | `GET` | `process_performance_api.route_get_pg_veri_detay` | `route_get_pg_veri_detay` | Açıklama yok. |
| `/api/pg-veri/detay/toplu` | `POST` | `process_performance_api.route_get_pg_veri_detay_toplu` | `route_get_pg_veri_detay_toplu` | Açıklama yok. |
| `/api/pg-veri/guncelle/<int:veri_id>` | `PUT` | `process_performance_api.route_update_pg_veri` | `route_update_pg_veri` | Açıklama yok. |
| `/api/surec/<int:surec_id>/faaliyet/<int:surec_faaliyet_id>/create-bireysel` | `POST` | `process_performance_api.api_create_bireysel_faaliyet_from_surec` | `api_create_bireysel_faaliyet_from_surec` | Açıklama yok. |
| `/api/surec/<int:surec_id>/karne/faaliyetler` | `GET` | `process_performance_api.api_surec_karne_faaliyetler` | `api_surec_karne_faaliyetler` | Açıklama yok. |
| `/api/surec/<int:surec_id>/karne/kaydet` | `POST` | `process_performance_api.api_surec_karne_kaydet` | `api_surec_karne_kaydet` | Süreç karnesi verilerini kaydet (Process API Controller). |
| `/api/surec/<int:surec_id>/karne/performans` | `GET` | `process_performance_api.api_surec_karne_performans` | `api_surec_karne_performans` | Sürecin performans göstergelerini ve çeyreklik verilerini getirir. |
| `/api/surec/karne/pg-veri-detay` | `GET` | `process_performance_api.route_get_pg_veri_detay_list` | `route_get_pg_veri_detay_list` | Açıklama yok. |

---

### 📦 Blueprint: `push_api`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/subscribe` | `POST` | `push_api.subscribe` | `subscribe` | Subscribe to push notifications |
| `/test` | `POST` | `push_api.test_notification` | `test_notification` | Send test push notification |
| `/unsubscribe` | `POST` | `push_api.unsubscribe` | `unsubscribe` | Unsubscribe from push notifications |
| `/vapid-key` | `GET` | `push_api.get_vapid_key` | `get_vapid_key` | Get VAPID public key for push subscription |

---

### 📦 Blueprint: `sso_bp`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/sso/google` | `GET` | `sso_bp.sso_google` | `sso_google` | Google OAuth akışını başlat. |
| `/sso/google/callback` | `GET` | `sso_bp.sso_google_callback` | `sso_google_callback` | Google OAuth callback — token al, kullanıcıyı login et. |

---

### 📦 Blueprint: `swagger_ui`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/api/docs/` | `GET` | `swagger_ui.show` | `show` | Açıklama yok. |
| `/api/docs/<path:path>` | `GET` | `swagger_ui.show` | `show` | Açıklama yok. |

---

### 📦 Blueprint: `totp_bp`

| Rota (URL Path) | HTTP Metotları | Endpoint | Fonksiyon | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| `/2fa/challenge` | `GET, POST` | `totp_bp.totp_challenge` | `totp_challenge` | Login sırasında 2FA enabled kullanıcı için ek doğrulama. |
| `/2fa/disable` | `POST` | `totp_bp.totp_disable` | `totp_disable` | 2FA devre dışı bırak — şifre confirm zorunlu. |
| `/2fa/init` | `POST` | `totp_bp.totp_init` | `totp_init` | JSON: yeni secret + QR base64 üret (DB'ye yazma — kullanıcı verify edene kadar bekle). |
| `/2fa/setup` | `GET` | `totp_bp.totp_setup` | `totp_setup` | Setup başlat — secret üret + QR göster. |
| `/2fa/status` | `GET` | `totp_bp.totp_status` | `totp_status` | JSON: 2FA durumu — profil sayfasında kullanılır. |
| `/2fa/verify-setup` | `POST` | `totp_bp.totp_verify_setup` | `totp_verify_setup` | Setup doğrulama — kullanıcı authenticator'dan gelen kodu girer. |

---


✅ Sayfa tarayıcıda açıldı, konsol hatası taranmadı ve görsel olarak doğrulandı.
