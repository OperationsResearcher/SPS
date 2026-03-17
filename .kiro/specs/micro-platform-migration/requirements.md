# Gereksinimler Belgesi

## Giriş

Bu belge, mevcut Flask SaaS danışmanlık yönetim platformunun `app/` katmanındaki tüm bileşenlerinin `micro/` modüler mimarisine taşınması için gereksinimleri tanımlar.

Mevcut `micro/` yapısı; `micro_bp` adlı tek bir Blueprint üzerinden çalışan, `app/models/` ve `app/services/` katmanlarını paylaşımlı kullanan, her modülün kendi `routes.py` dosyasına sahip olduğu bir mimaridir. Bu geçiş; Süreç Yönetimi, Stratejik Planlama, Kurum Paneli, Admin, HGS, API Katmanı, Servisler ve Bireysel Performans bileşenlerini kapsar.

Geçiş sonrasında `app/routes/` altındaki Blueprint'ler devre dışı bırakılacak; tüm kullanıcı arayüzü trafiği `/micro/` prefix'i üzerinden yönlendirilecektir.

---

## Sözlük

- **Micro_Platform**: `micro/` dizini altında çalışan, `micro_bp` Blueprint'ini kullanan modüler uygulama katmanı.
- **Micro_BP**: `micro/__init__.py` içinde tanımlanan, tüm modül route'larını barındıran tek Flask Blueprint nesnesi.
- **Module_Registry**: `micro/core/module_registry.py` içindeki modül tanım ve erişim kontrol sistemi.
- **Tenant**: Platforma kayıtlı kurum/organizasyon birimi.
- **PG**: Performans Göstergesi — `ProcessKpi` veya `IndividualPerformanceIndicator` modeli.
- **Karne**: Bir sürecin PG ve faaliyet verilerini dönemsel olarak gösteren özet ekranı.
- **Soft_Delete**: `is_active=False` yapılarak kaydın mantıksal olarak silinmesi; fiziksel silme yasaktır.
- **Score_Engine**: `app/services/score_engine_service.py` içindeki vizyon skoru hesaplama servisi.
- **HGS**: Hızlı Giriş Sistemi — geliştirme ortamında şifresiz kullanıcı geçişi sağlayan yardımcı modül.
- **Tenant_Admin**: Kurum düzeyinde yönetici rolü.
- **Executive_Manager**: Üst yönetici rolü.
- **Standard_User**: Standart kullanıcı rolü.
- **Admin**: Platform düzeyinde süper yönetici rolü.

---

## Gereksinimler

### Gereksinim 1: Mimari Temel — Tek Blueprint Yapısı

**Kullanıcı Hikayesi:** Bir platform geliştirici olarak, tüm modüllerin tek bir `micro_bp` Blueprint üzerinden çalışmasını istiyorum; böylece Flask uygulama kayıt sürecini basit tutabilir ve modüller arası çakışmaları önleyebilirim.

#### Kabul Kriterleri

1. THE Micro_Platform SHALL register all module routes exclusively through the `micro_bp` Blueprint defined in `micro/__init__.py`.
2. THE Micro_BP SHALL use the URL prefix `/micro` for all registered routes.
3. WHEN a new module is added to `micro/modules/`, THE Micro_BP SHALL import its `routes.py` file in `micro/__init__.py` to activate the routes.
4. THE Micro_Platform SHALL share `app/models/` and `app/services/` without duplicating or modifying them.
5. IF a route in `micro/` conflicts with an existing `app/routes/` route, THEN THE Micro_Platform SHALL take precedence and the `app/routes/` version SHALL be disabled.
6. THE Micro_Platform SHALL serve templates from `micro/templates/micro/` and static files from `micro/static/micro/`.

---

### Gereksinim 2: Kimlik Doğrulama ve Oturum Yönetimi

**Kullanıcı Hikayesi:** Bir kullanıcı olarak, tüm micro modüllerine erişmeden önce oturum açmamı istiyorum; böylece yetkisiz erişim engellensin.

#### Kabul Kriterleri

1. THE Micro_Platform SHALL protect every route with `@login_required` decorator without exception.
2. WHEN an unauthenticated user attempts to access any `/micro/` route, THE Micro_Platform SHALL redirect the user to the login page.
3. THE Micro_Platform SHALL use `current_user.tenant_id` to scope all database queries to the authenticated user's tenant.
4. WHEN `current_user.tenant_id` is `None`, THE Micro_Platform SHALL return an appropriate error response without raising an unhandled exception.
5. THE Auth_Module SHALL provide login, logout, and profile routes under `/micro/auth/` path.
6. WHEN a user logs out, THE Auth_Module SHALL invalidate the session and redirect to the login page.

---

### Gereksinim 3: Süreç Yönetimi Modülü — Tam Geçiş

**Kullanıcı Hikayesi:** Bir süreç yöneticisi olarak, süreçleri, PG'leri ve faaliyetleri micro platform üzerinden yönetmek istiyorum; böylece eski `app/routes/process.py` bağımlılığından kurtulabileyim.

#### Kabul Kriterleri

1. THE Surec_Module SHALL provide a process list page at `/micro/surec` displaying all active processes for the current tenant, ordered by process code.
2. WHEN a user navigates to `/micro/surec/<process_id>/karne`, THE Surec_Module SHALL render the process scorecard (karne) page with all active KPIs and activities for that process.
3. THE Surec_Module SHALL expose a JSON API at `/micro/surec/api/add` (POST) to create a new process with fields: `code`, `name`, `english_name`, `description`, `document_no`, `revision_no`, `status`, `progress`, `parent_id`, `start_boundary`, `end_boundary`, `leader_ids`, `member_ids`.
4. THE Surec_Module SHALL expose a JSON API at `/micro/surec/api/update/<process_id>` (POST) to update an existing process, including reassignment of leaders, members, and sub-strategy links with contribution percentages.
5. WHEN a process delete request is received at `/micro/surec/api/delete/<process_id>`, THE Surec_Module SHALL set `is_active=False` and record `deleted_at` and `deleted_by` fields (Soft_Delete).
6. THE Surec_Module SHALL expose KPI CRUD APIs at `/micro/surec/api/kpi/add`, `/micro/surec/api/kpi/update/<kpi_id>`, `/micro/surec/api/kpi/delete/<kpi_id>`, and `/micro/surec/api/kpi/list/<process_id>`.
7. THE Surec_Module SHALL expose activity CRUD APIs at `/micro/surec/api/activity/add`, `/micro/surec/api/activity/update/<act_id>`, `/micro/surec/api/activity/delete/<act_id>`.
8. WHEN a KPI data entry is submitted to `/micro/surec/api/kpi-data/add`, THE Surec_Module SHALL persist the entry, trigger `score_engine_service.recalc_on_pg_data_change`, and trigger `process_deviation_service.check_pg_performance_deviation`.
9. THE Surec_Module SHALL expose `/micro/surec/api/karne/<process_id>` (GET) returning aggregated KPI data and activity monthly tracking for a given year.
10. THE Surec_Module SHALL support hierarchical process tree display, showing root processes and their children using `parent_id` relationships.
11. WHEN loading the process list, THE Surec_Module SHALL use eager loading (`joinedload`/`selectinload`) to prevent N+1 query problems.
12. THE Surec_Module SHALL support activity monthly tracking via `/micro/surec/api/activity/track/<act_id>` (POST) to toggle monthly completion status.

---

### Gereksinim 4: Stratejik Planlama Modülü — Genişletme

**Kullanıcı Hikayesi:** Bir kurum yöneticisi olarak, stratejik planlama araçlarının tamamına micro platform üzerinden erişmek istiyorum; böylece SWOT analizi, strateji yönetimi ve dinamik graf görünümünü tek bir arayüzden kullanabileyim.

#### Kabul Kriterleri

1. THE SP_Module SHALL provide a strategic planning overview page at `/micro/sp` showing tenant strategies, sub-strategies, and SWOT item counts.
2. THE SP_Module SHALL provide a SWOT analysis page at `/micro/sp/swot` displaying items grouped by category: `strength`, `weakness`, `opportunity`, `threat`.
3. THE SP_Module SHALL expose `/micro/sp/api/swot/add` (POST) and `/micro/sp/api/swot/delete/<item_id>` (POST) for SWOT item management with Soft_Delete.
4. THE SP_Module SHALL expose `/micro/sp/api/strategy/add` (POST) and `/micro/sp/api/strategy/delete/<strategy_id>` (POST) restricted to roles: `tenant_admin`, `executive_manager`, `Admin`.
5. THE SP_Module SHALL expose `/micro/sp/api/sub-strategy/add` (POST) and `/micro/sp/api/sub-strategy/update/<sub_id>` (POST) and `/micro/sp/api/sub-strategy/delete/<sub_id>` (POST).
6. THE SP_Module SHALL provide a strategic planning flow page at `/micro/sp/flow` showing tenant vision, strategy counts, SWOT counts, and process counts.
7. THE SP_Module SHALL provide a dynamic graph page at `/micro/sp/flow/dynamic` rendering an interactive node-edge visualization.
8. WHEN `/micro/sp/api/graph` (GET) is called, THE SP_Module SHALL return nodes and edges data by invoking `score_engine_service.compute_vision_score` and building the graph structure with vision, main strategies, sub-strategies, processes, and KPIs as nodes.
9. IF `current_user.role.name == "Admin"`, THEN THE SP_Module SHALL allow passing a `tenant_id` query parameter to view another tenant's strategic graph.
10. WHEN a strategy or sub-strategy is deleted, THE SP_Module SHALL apply Soft_Delete (`is_active=False`) without physically removing the record.

---

### Gereksinim 5: Kurum Paneli ve Masaüstü Modülleri

**Kullanıcı Hikayesi:** Bir kurum yöneticisi olarak, kurum performans özetini ve stratejik kimlik bilgilerini micro platform üzerinden görmek ve düzenlemek istiyorum.

#### Kabul Kriterleri

1. THE Masaustu_Module SHALL display at `/micro/masaustu` a personal summary including: active individual PGs (last 5), ongoing individual activities (last 5), process KPIs from processes where the user is a leader or member (last 5), and unread notifications (last 5).
2. THE Masaustu_Module SHALL display summary counts: total active individual PGs, total ongoing activities, total unread notifications, total process KPIs.
3. WHILE `current_user.role.name` is in `("tenant_admin", "executive_manager", "Admin")`, THE Masaustu_Module SHALL additionally display the tenant's top 3 active strategies.
4. THE Kurum_Panel_Module SHALL provide a tenant dashboard at `/micro/kurum` showing user count, active support tickets, package usage percentage, and recent activity log.
5. THE Kurum_Panel_Module SHALL expose `/micro/kurum/api/update-strategy` (POST) to update tenant strategic identity fields: `purpose`, `vision`, `core_values`, `code_of_ethics`, `quality_policy`, restricted to `tenant_admin` and `executive_manager` roles.
6. THE Kurum_Panel_Module SHALL expose strategy and sub-strategy CRUD APIs at `/micro/kurum/api/` mirroring the existing `dashboard_bp` endpoints.
7. WHEN a tenant strategic identity field is updated, THE Kurum_Panel_Module SHALL commit the change and return a JSON success response.

---

### Gereksinim 6: Admin Modülü — Kullanıcı, Kurum ve Paket Yönetimi

**Kullanıcı Hikayesi:** Bir platform yöneticisi olarak, kullanıcıları, kurumları ve abonelik paketlerini micro platform üzerinden yönetmek istiyorum.

#### Kabul Kriterleri

1. THE Admin_Module SHALL provide a user management page at `/micro/admin/users` listing all users for `Admin` role, or only tenant users for `tenant_admin` and `executive_manager` roles.
2. THE Admin_Module SHALL expose `/micro/admin/users/add` (POST), `/micro/admin/users/edit/<user_id>` (POST), and `/micro/admin/users/toggle/<user_id>` (POST) for user lifecycle management.
3. WHEN a user is deactivated via `/micro/admin/users/toggle/<user_id>`, THE Admin_Module SHALL set `is_active=False` (Soft_Delete) and SHALL NOT physically delete the record.
4. IF a `tenant_admin` role is being assigned and the tenant already has an active `tenant_admin`, THEN THE Admin_Module SHALL return an error response preventing duplicate tenant admins.
5. THE Admin_Module SHALL provide a tenant management page at `/micro/admin/tenants` with add, edit, and archive (soft delete) operations.
6. THE Admin_Module SHALL provide a package management page at `/micro/admin/packages` for managing `SubscriptionPackage` and `SystemModule` records.
7. THE Admin_Module SHALL expose `/micro/admin/components/sync` (POST) to discover and register all Flask URL rules into `RouteRegistry`.
8. THE Admin_Module SHALL expose `/micro/admin/components/update` (POST) to assign `component_slug` values to registered routes.
9. WHEN a user bulk import file is uploaded to `/micro/admin/users/bulk-import`, THE Admin_Module SHALL parse Excel/CSV, skip duplicate emails, and create new users with default `standard_user` role.
10. THE Admin_Module SHALL restrict all admin routes to authenticated users with `Admin`, `tenant_admin`, or `executive_manager` roles, returning HTTP 403 for unauthorized access.

---

### Gereksinim 7: Bireysel Performans Modülü

**Kullanıcı Hikayesi:** Bir standart kullanıcı olarak, bireysel performans göstergelerimi ve faaliyetlerimi micro platform üzerinden takip etmek istiyorum; böylece kişisel karnemi görebilir ve veri girişi yapabilirim.

#### Kabul Kriterleri

1. THE Bireysel_Module SHALL provide a personal scorecard page at `/micro/bireysel/karne` displaying the current user's active `IndividualPerformanceIndicator` records.
2. THE Bireysel_Module SHALL expose CRUD APIs at `/micro/bireysel/api/pg/add`, `/micro/bireysel/api/pg/update/<pg_id>`, `/micro/bireysel/api/pg/delete/<pg_id>` for individual PG management.
3. WHEN an individual PG is deleted, THE Bireysel_Module SHALL set `is_active=False` (Soft_Delete).
4. THE Bireysel_Module SHALL expose CRUD APIs at `/micro/bireysel/api/faaliyet/add`, `/micro/bireysel/api/faaliyet/update/<act_id>`, `/micro/bireysel/api/faaliyet/delete/<act_id>` for individual activity management.
5. THE Bireysel_Module SHALL expose `/micro/bireysel/api/veri/add` (POST) to record `IndividualKpiData` entries with year, period type, period number, and actual value.
6. THE Bireysel_Module SHALL expose `/micro/bireysel/api/faaliyet/track/<act_id>` (POST) to toggle monthly completion status for `IndividualActivityTrack`.
7. THE Bireysel_Module SHALL expose `/micro/bireysel/api/karne` (GET) returning aggregated individual PG data and activity tracking for a given year, scoped to `current_user.id`.
8. WHEN a process KPI is marked as a favorite via `/micro/bireysel/api/favori/toggle/<kpi_id>`, THE Bireysel_Module SHALL create or soft-delete the `FavoriteKpi` record for the current user.

---

### Gereksinim 8: Analiz Merkezi Modülü

**Kullanıcı Hikayesi:** Bir yönetici olarak, süreç performans analizlerini, trend grafiklerini ve anomali raporlarını micro platform üzerinden görüntülemek istiyorum.

#### Kabul Kriterleri

1. THE Analiz_Module SHALL provide an analysis center page at `/micro/analiz` showing summary analytics for the current tenant.
2. THE Analiz_Module SHALL expose `/micro/analiz/api/trend/<kpi_id>` (GET) by delegating to `AnalyticsService.get_performance_trend` with `start_date`, `end_date`, and `frequency` parameters.
3. THE Analiz_Module SHALL expose `/micro/analiz/api/health/<process_id>` (GET) by delegating to `AnalyticsService.get_process_health_score`.
4. THE Analiz_Module SHALL expose `/micro/analiz/api/forecast/<kpi_id>` (GET) by delegating to `AnalyticsService.get_forecast` with `periods` and `method` parameters.
5. THE Analiz_Module SHALL expose `/micro/analiz/api/comparison` (POST) by delegating to `AnalyticsService.get_comparative_analysis` for multi-process comparison.
6. THE Analiz_Module SHALL expose `/micro/analiz/api/report/<process_id>` (GET) by delegating to `ReportService.generate_performance_report` supporting `json` and `excel` output formats.
7. WHEN the `excel` format is requested, THE Analiz_Module SHALL return the file as a downloadable attachment with appropriate MIME type.
8. THE Analiz_Module SHALL expose `/micro/analiz/api/anomalies` (GET) by delegating to `AnomalyService` for the current tenant's processes.

---

### Gereksinim 9: HGS Modülü — Hızlı Giriş Sistemi

**Kullanıcı Hikayesi:** Bir geliştirici olarak, geliştirme ortamında farklı kullanıcı hesaplarına hızlıca geçiş yapabilmek istiyorum; böylece test süreçlerini hızlandırabilirim.

#### Kabul Kriterleri

1. THE HGS_Module SHALL provide a quick login page at `/micro/hgs` listing all active users grouped by tenant, without requiring prior authentication.
2. WHEN a user clicks a quick login link at `/micro/hgs/login/<user_id>`, THE HGS_Module SHALL authenticate the selected user via `login_user` and redirect to `/micro/`.
3. IF the requested `user_id` does not exist or `is_active=False`, THEN THE HGS_Module SHALL redirect back to `/micro/hgs` without raising an error.
4. THE HGS_Module SHALL display users ordered by tenant name, then by first name and email within each tenant group.

---

### Gereksinim 10: REST API Katmanı — micro/api Modülü

**Kullanıcı Hikayesi:** Bir entegrasyon geliştiricisi olarak, platformun verilerine RESTful API üzerinden erişmek istiyorum; böylece dış sistemlerle entegrasyon kurabileyim.

#### Kabul Kriterleri

1. THE API_Module SHALL expose process list and detail endpoints at `/micro/api/v1/processes` (GET) and `/micro/api/v1/processes/<process_id>` (GET) with tenant-scoped filtering.
2. THE API_Module SHALL expose KPI data CRUD endpoints at `/micro/api/v1/kpi-data` (POST), `/micro/api/v1/kpi-data/<id>` (GET, PATCH, DELETE).
3. WHEN a KPI data record is deleted via the API, THE API_Module SHALL apply Soft_Delete (`is_active=False`) and log the action via `AuditLogger`.
4. THE API_Module SHALL expose analytics endpoints: `/micro/api/v1/analytics/trend/<kpi_id>`, `/micro/api/v1/analytics/health/<process_id>`, `/micro/api/v1/analytics/comparison`, `/micro/api/v1/analytics/forecast/<kpi_id>`.
5. THE API_Module SHALL expose report endpoints at `/micro/api/v1/reports/performance/<process_id>` and `/micro/api/v1/reports/dashboard`.
6. THE API_Module SHALL expose AI endpoints at `/micro/api/v1/ai/` by delegating to the existing `app/api/ai.py` logic.
7. THE API_Module SHALL expose push notification endpoints at `/micro/api/v1/push/` by delegating to the existing `app/api/push.py` logic.
8. THE API_Module SHALL expose a Swagger/OpenAPI documentation page at `/micro/api/docs`.
9. WHEN an API request is received without authentication, THE API_Module SHALL return HTTP 401 with a JSON error body.
10. WHEN an API request results in a server error, THE API_Module SHALL return HTTP 500 with a JSON error body and log the exception via `current_app.logger.error`.

---

### Gereksinim 11: Bildirim ve Ayarlar Modülleri

**Kullanıcı Hikayesi:** Bir kullanıcı olarak, sistem bildirimlerimi ve hesap ayarlarımı micro platform üzerinden yönetmek istiyorum.

#### Kabul Kriterleri

1. THE Bildirim_Module SHALL provide a notification center page at `/micro/bildirim` listing all notifications for the current user, ordered by creation date descending.
2. THE Bildirim_Module SHALL expose `/micro/bildirim/api/mark-read/<notification_id>` (POST) to mark a single notification as read (`is_read=True`).
3. THE Bildirim_Module SHALL expose `/micro/bildirim/api/mark-all-read` (POST) to mark all unread notifications for the current user as read.
4. THE Ayarlar_Module SHALL provide a settings page at `/micro/ayarlar` for managing user profile, theme preferences, notification preferences, and locale preferences.
5. WHEN a user updates their profile via `/micro/ayarlar/api/profil` (POST), THE Ayarlar_Module SHALL update `first_name`, `last_name`, `phone_number`, `job_title`, `department` fields and return a JSON success response.
6. WHEN a user updates their password via `/micro/ayarlar/api/sifre` (POST), THE Ayarlar_Module SHALL verify the current password before applying the new password hash.
7. THE Ayarlar_Module SHALL expose `/micro/ayarlar/api/tercihler` (POST) to save `theme_preferences`, `layout_preference`, `notification_preferences`, and `locale_preferences` as JSON.

---

### Gereksinim 12: Modül Kayıt Sistemi ve Erişim Kontrolü

**Kullanıcı Hikayesi:** Bir platform yöneticisi olarak, hangi modüllerin hangi kullanıcılara görüneceğini merkezi olarak kontrol etmek istiyorum; böylece paket bazlı erişim kısıtlaması uygulayabileyim.

#### Kabul Kriterleri

1. THE Module_Registry SHALL define all available modules with fields: `id`, `name`, `url`, `icon`, `description`.
2. WHEN `get_accessible_modules(user)` is called, THE Module_Registry SHALL return only the modules accessible to the given user based on their tenant's subscription package and assigned roles.
3. THE Module_Registry SHALL check `SubscriptionPackage` → `SystemModule` → `ModuleComponentSlug` chain to determine module accessibility.
4. IF a user's tenant has no package assigned, THEN THE Module_Registry SHALL return a default minimal set of modules (at minimum: `masaustu`, `bildirim`, `ayarlar`).
5. THE Launcher_Page SHALL display accessible modules at `/micro/` using the Module_Registry output, rendering the `micro/launcher.html` template.
6. WHEN a user attempts to access a module route they are not authorized for, THE Micro_Platform SHALL return HTTP 403 with a Türkçe error message.

---

### Gereksinim 13: Veri Bütünlüğü ve Soft Delete Standardı

**Kullanıcı Hikayesi:** Bir veri yöneticisi olarak, hiçbir verinin fiziksel olarak silinmemesini istiyorum; böylece denetim izleri korunabilsin ve veri kurtarma mümkün olsun.

#### Kabul Kriterleri

1. THE Micro_Platform SHALL apply Soft_Delete on all delete operations by setting `is_active=False` without executing SQL `DELETE` statements.
2. WHEN querying any entity in the Micro_Platform, THE Micro_Platform SHALL always include `.filter_by(is_active=True)` or equivalent condition to exclude soft-deleted records.
3. WHEN a process is soft-deleted, THE Surec_Module SHALL also record `deleted_at=datetime.now(timezone.utc)` and `deleted_by=current_user.id`.
4. THE Micro_Platform SHALL never expose soft-deleted records in list or detail API responses.
5. FOR ALL entities with `is_active` field, querying then soft-deleting then querying again SHALL return a result set that excludes the deleted record (round-trip soft delete property).

---

### Gereksinim 14: Hata Yönetimi ve Loglama

**Kullanıcı Hikayesi:** Bir geliştirici olarak, tüm hataların loglandığını ve kullanıcıya anlamlı Türkçe geri bildirim verildiğini bilmek istiyorum; böylece boş `except: pass` bloklarından kaynaklanan sessiz hatalar önlensin.

#### Kabul Kriterleri

1. THE Micro_Platform SHALL log all unhandled exceptions using `current_app.logger.error(message, exc_info=True)`.
2. IF a database operation fails, THEN THE Micro_Platform SHALL call `db.session.rollback()` before returning an error response.
3. THE Micro_Platform SHALL return JSON error responses with `{"success": False, "message": "<Türkçe hata mesajı>"}` structure for all API endpoints.
4. THE Micro_Platform SHALL never use bare `except: pass` constructs; every exception handler SHALL log the error and return a meaningful response.
5. WHEN a requested resource is not found (404), THE Micro_Platform SHALL return a JSON response with HTTP 404 status for API routes and render a Türkçe error page for HTML routes.

---

### Gereksinim 15: Frontend Standartları — SweetAlert2 ve Katman Ayrımı

**Kullanıcı Hikayesi:** Bir kullanıcı olarak, tüm onay ve bildirim pencerelerinin tutarlı ve profesyonel görünmesini istiyorum; böylece tarayıcının varsayılan `alert()` pencereleri yerine SweetAlert2 kullanılsın.

#### Kabul Kriterleri

1. THE Micro_Platform SHALL use SweetAlert2 (`Swal.fire`) for all user-facing confirmation dialogs, success messages, and error notifications in the frontend.
2. THE Micro_Platform SHALL NOT use native browser `alert()`, `confirm()`, or `prompt()` functions anywhere in the frontend code.
3. THE Micro_Platform SHALL place all JavaScript code in `micro/static/micro/js/` files and all CSS code in `micro/static/micro/css/` files.
4. THE Micro_Platform SHALL NOT embed `<script>` or `<style>` blocks directly inside HTML template files.
5. WHEN passing data from Flask templates to JavaScript, THE Micro_Platform SHALL use `data-*` HTML attributes instead of inline Jinja2 `{{ }}` expressions inside `.js` files.
6. THE Micro_Platform SHALL display success notifications with green theme and error notifications with red theme in SweetAlert2.
