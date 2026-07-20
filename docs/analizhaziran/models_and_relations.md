# Kokpitim Veritabanı Modelleri ve İlişkileri Analiz Raporu

**Analiz Tarihi:** 2026-06-09  
**Rapor Amacı:** Kokpitim projesinin SQLAlchemy ORM modellerinin, veritabanı tablolarının, veri tiplerinin ve tablolar arası ilişkilerin detaylı envanteri.  

## 📊 Genel Özet

| Metrik | Değer |
| :--- | :--- |
| **Toplam Model Sınıfı** | 152 |
| **Modül Sayısı (Dosya)** | 30 |
| **Toplam İlişkisel Tablo Sayısı** | 161 |

## 🗂 Modül Bazlı Model Dağılımı

| Modül Dosyası | Sınıf Sayısı | Modül Açıklaması |
| :--- | :---: | :--- |
| [`audit.py`](file:///c:/kokpitim/app/models/audit.py) | 1 | Sistem içi işlem ve denetim logları (Audit Logs) |
| [`bsc.py`](file:///c:/kokpitim/app/models/bsc.py) | 1 | Dengelenmiş Skor Kartı (BSC) perspektifleri |
| [`core.py`](file:///c:/kokpitim/app/models/core.py) | 7 | Temel sistem yönetimi (Kullanıcı, Rol, Tenant/Kurum, Bildirimler) |
| [`dashboard.py`](file:///c:/kokpitim/app/models/dashboard.py) | 1 | Diğer yardımcı veri modelleri |
| [`email_config.py`](file:///c:/kokpitim/app/models/email_config.py) | 1 | Tenant/Kurum SMTP ve e-posta bildirim ayarları |
| [`esg.py`](file:///c:/kokpitim/app/models/esg.py) | 2 | ESG (Çevresel, Sosyal, Yönetişim) metrikleri ve değer takipleri |
| [`feedback.py`](file:///c:/kokpitim/app/models/feedback.py) | 1 | Diğer yardımcı veri modelleri |
| [`initiative.py`](file:///c:/kokpitim/app/models/initiative.py) | 2 | Stratejik inisiyatifler ve kilometre taşları (milestones) |
| [`k_radar.py`](file:///c:/kokpitim/app/models/k_radar.py) | 1 | K-Radar önerileri ve aksiyon takipleri |
| [`k_radar_domain.py`](file:///c:/kokpitim/app/models/k_radar_domain.py) | 9 | K-Radar kurumsal olgunluk, darboğaz analizleri, değer zinciri ve risk ısı haritaları |
| [`k_vektor.py`](file:///c:/kokpitim/app/models/k_vektor.py) | 3 | K-Vektör stratejik hizalama katsayıları ve ağırlıkları |
| [`llm_usage.py`](file:///c:/kokpitim/app/models/llm_usage.py) | 2 | Yapay zeka asistanı (LLM) kullanım logları ve kota aşım tanımları |
| [`models.py`](file:///c:/kokpitim/app/models/models.py) | 32 | Diğer yardımcı veri modelleri |
| [`notification.py`](file:///c:/kokpitim/app/models/notification.py) | 3 | Gelişmiş bildirim tercihleri ve tarayıcı push abonelikleri |
| [`okr.py`](file:///c:/kokpitim/app/models/okr.py) | 2 | OKR (Hedef ve Anahtar Sonuçlar) yönetimi |
| [`plan_year.py`](file:///c:/kokpitim/app/models/plan_year.py) | 6 | Yıllık planlama, dönem hedefleri ve yıllık KPI/süreç konfigürasyonları |
| [`portfolio_project.py`](file:///c:/kokpitim/app/models/portfolio_project.py) | 24 | Proje portföy yönetimi, RAID analizleri, görevler, bağımlılıklar ve proje üyeleri |
| [`process.py`](file:///c:/kokpitim/app/models/process.py) | 15 | Süreç yönetimi, performans göstergeleri (KPI), faaliyet takipleri ve bireysel karneler |
| [`project.py`](file:///c:/kokpitim/app/models/project.py) | 3 | Basit planlama projeleri ve görev ilişkileri |
| [`replan_trigger.py`](file:///c:/kokpitim/app/models/replan_trigger.py) | 2 | Yeniden planlama tetikleyicileri ve olay kayıtları |
| [`saas.py`](file:///c:/kokpitim/app/models/saas.py) | 5 | SaaS abonelik paketleri, modüller, bileşenler ve rota kayıt yetkilendirmeleri |
| [`strategy.py`](file:///c:/kokpitim/app/models/strategy.py) | 4 | Diğer yardımcı veri modelleri |
| [`strategy_frameworks.py`](file:///c:/kokpitim/app/models/strategy_frameworks.py) | 4 | Mavi Okyanus Stratejisi (Kanvas, Faktörler, ERRC) ve VRIO kaynak analizleri |
| [`swot.py`](file:///c:/kokpitim/app/models/swot.py) | 4 | SWOT analizi, TOWS matrisi, PESTEL ve Porter'ın 5 Gücü analizleri |
| [`system_setting.py`](file:///c:/kokpitim/app/models/system_setting.py) | 1 | Genel sistem ayarları ve parametreleri |
| [`tenant_llm_config.py`](file:///c:/kokpitim/app/models/tenant_llm_config.py) | 1 | Tenant bazlı LLM modeli ve API anahtar ayarları |
| [`tenant_year.py`](file:///c:/kokpitim/app/models/tenant_year.py) | 1 | Tenant dönem ve yıl kimlik eşlemeleri |
| [`tour.py`](file:///c:/kokpitim/app/models/tour.py) | 1 | Kullanıcı ilk tur/kılavuz ilerleme durumu |
| [`user.py`](file:///c:/kokpitim/app/models/user.py) | 12 | Diğer yardımcı veri modelleri |
| [`user_year_assignment.py`](file:///c:/kokpitim/app/models/user_year_assignment.py) | 1 | Kullanıcıların plan yıllarına göre atamaları |

---

## 🔍 Detaylı Model Sınıfları ve Şema Tasarımları

### 📁 `audit.py` İçindeki Modeller

#### 🏷️ Sınıf: `AuditLog` (Tablo: `audit_logs`)
*Audit log tablosu*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Evet | users.id |
| `username` | `VARCHAR(100)` | - | Evet | - |
| `tenant_id` | `INTEGER` | - | Evet | tenants.id |
| `action` | `VARCHAR(50)` | - | Hayır | - |
| `resource_type` | `VARCHAR(50)` | - | Evet | - |
| `resource_id` | `INTEGER` | - | Evet | - |
| `description` | `TEXT` | - | Evet | - |
| `old_values` | `JSON` | - | Evet | - |
| `new_values` | `JSON` | - | Evet | - |
| `ip_address` | `VARCHAR(45)` | - | Evet | - |
| `user_agent` | `VARCHAR(500)` | - | Evet | - |
| `request_method` | `VARCHAR(10)` | - | Evet | - |
| `request_path` | `VARCHAR(500)` | - | Evet | - |
| `created_at` | `DATETIME` | - | Hayır | - |

---

### 📁 `bsc.py` İçindeki Modeller

#### 🏷️ Sınıf: `BscKpiPerspective` (Tablo: `bsc_kpi_perspectives`)
*ProcessKpi → BSC Perspektif ataması.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `process_kpi_id` | `INTEGER` | - | Hayır | process_kpis.id |
| `perspective` | `VARCHAR(30)` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `process_kpi` | `ProcessKpi` | `MANYTOONE` | Hayır |

---

### 📁 `core.py` İçindeki Modeller

#### 🏷️ Sınıf: `Notification` (Tablo: `notifications`)
*Sistem Bildirimleri (PG sapma, görev vb.).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `tenant_id` | `INTEGER` | - | Evet | tenants.id |
| `notification_type` | `VARCHAR(50)` | - | Hayır | - |
| `title` | `VARCHAR(200)` | - | Hayır | - |
| `message` | `TEXT` | - | Evet | - |
| `link` | `VARCHAR(500)` | - | Evet | - |
| `is_read` | `BOOLEAN` | - | Hayır | - |
| `process_id` | `INTEGER` | - | Evet | - |
| `related_user_id` | `INTEGER` | - | Evet | users.id |
| `created_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `user` | `User` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `Role` (Tablo: `roles`)
*Role model for user authorization.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `name` | `VARCHAR(64)` | - | Hayır | - |
| `description` | `VARCHAR(255)` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `users` | `User` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `Strategy` (Tablo: `strategies`)
*Main Strategy Model (Ana Strateji).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `code` | `VARCHAR(20)` | - | Evet | - |
| `title` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |
| `plan_year_id` | `INTEGER` | - | Evet | plan_years.id |
| `source_strategy_id` | `INTEGER` | - | Evet | strategies.id |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `source_strategy` | `Strategy` | `MANYTOONE` | Hayır |
| `sub_strategies` | `SubStrategy` | `ONETOMANY` | Evet |
| `k_vektor_weight_row` | `KVektorStrategyWeight` | `ONETOMANY` | Hayır |
| `year_configs` | `StrategyYearConfig` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `SubStrategy` (Tablo: `sub_strategies`)
*Sub Strategy Model (Alt Strateji).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `strategy_id` | `INTEGER` | - | Hayır | strategies.id |
| `code` | `VARCHAR(20)` | - | Evet | - |
| `title` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |
| `plan_year_id` | `INTEGER` | - | Evet | plan_years.id |
| `source_sub_strategy_id` | `INTEGER` | - | Evet | sub_strategies.id |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `strategy` | `Strategy` | `MANYTOONE` | Hayır |
| `source_sub_strategy` | `SubStrategy` | `MANYTOONE` | Hayır |
| `process_sub_strategy_links` | `ProcessSubStrategyLink` | `ONETOMANY` | Evet |
| `process_kpis` | `ProcessKpi` | `ONETOMANY` | Evet |
| `k_vektor_weight_row` | `KVektorSubStrategyWeight` | `ONETOMANY` | Hayır |
| `year_configs` | `SubStrategyYearConfig` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `Tenant` (Tablo: `tenants`)
*Tenant (organization) model.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `name` | `VARCHAR(255)` | - | Hayır | - |
| `short_name` | `VARCHAR(64)` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `package_id` | `INTEGER` | - | Evet | subscription_packages.id |
| `created_at` | `DATETIME` | - | Evet | - |
| `activity_area` | `VARCHAR(200)` | - | Evet | - |
| `sector` | `VARCHAR(100)` | - | Evet | - |
| `employee_count` | `INTEGER` | - | Evet | - |
| `contact_email` | `VARCHAR(120)` | - | Evet | - |
| `phone_number` | `VARCHAR(20)` | - | Evet | - |
| `website_url` | `VARCHAR(200)` | - | Evet | - |
| `tax_office` | `VARCHAR(100)` | - | Evet | - |
| `tax_number` | `VARCHAR(20)` | - | Evet | - |
| `max_user_count` | `INTEGER` | - | Evet | - |
| `license_end_date` | `DATE` | - | Evet | - |
| `purpose` | `TEXT` | - | Evet | - |
| `vision` | `TEXT` | - | Evet | - |
| `core_values` | `TEXT` | - | Evet | - |
| `code_of_ethics` | `TEXT` | - | Evet | - |
| `quality_policy` | `TEXT` | - | Evet | - |
| `logo_path` | `VARCHAR(500)` | - | Evet | - |
| `logo_updated_at` | `DATETIME` | - | Evet | - |
| `k_vektor_enabled` | `BOOLEAN` | - | Hayır | - |
| `k_radar_enabled` | `BOOLEAN` | - | Hayır | - |
| `plan_year_enabled` | `BOOLEAN` | - | Hayır | - |
| `plan_year_start` | `INTEGER` | - | Evet | - |
| `tenant_type` | `VARCHAR(20)` | - | Hayır | - |
| `parent_tenant_id` | `INTEGER` | - | Evet | tenants.id |
| `sub_tenant_limit` | `INTEGER` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `package` | `SubscriptionPackage` | `MANYTOONE` | Hayır |
| `users` | `User` | `ONETOMANY` | Evet |
| `parent_tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `sub_tenants` | `Tenant` | `ONETOMANY` | Evet |
| `tickets` | `Ticket` | `ONETOMANY` | Evet |
| `strategies` | `Strategy` | `ONETOMANY` | Evet |
| `processes` | `Process` | `ONETOMANY` | Evet |
| `email_config` | `TenantEmailConfig` | `ONETOMANY` | Hayır |
| `k_radar_actions` | `KRadarRecommendationAction` | `ONETOMANY` | Evet |
| `k_vektor_strategy_weights` | `KVektorStrategyWeight` | `ONETOMANY` | Evet |
| `k_vektor_sub_strategy_weights` | `KVektorSubStrategyWeight` | `ONETOMANY` | Evet |
| `k_vektor_snapshots` | `KVektorConfigSnapshot` | `ONETOMANY` | Evet |
| `plan_years` | `PlanYear` | `ONETOMANY` | Evet |
| `year_identities` | `TenantYearIdentity` | `ONETOMANY` | Evet |
| `user_year_assignments` | `UserYearAssignment` | `ONETOMANY` | Evet |
| `swot_analyses` | `SwotAnalysis` | `ONETOMANY` | Evet |
| `tows_analyses` | `TowsAnalysis` | `ONETOMANY` | Evet |
| `pestel_analyses` | `PestelAnalysis` | `ONETOMANY` | Evet |
| `porter_analyses` | `PorterFiveForcesAnalysis` | `ONETOMANY` | Evet |
| `okr_objectives` | `OkrObjective` | `ONETOMANY` | Evet |
| `bsc_kpi_perspectives` | `BscKpiPerspective` | `ONETOMANY` | Evet |
| `plan_projects` | `PlanProject` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `Ticket` (Tablo: `tickets`)
*Kule İletişim (Ticket) Modeli.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `tenant_id` | `INTEGER` | - | Evet | tenants.id |
| `page_url` | `VARCHAR(500)` | - | Evet | - |
| `subject` | `VARCHAR(50)` | - | Hayır | - |
| `message` | `TEXT` | - | Hayır | - |
| `screenshot_path` | `VARCHAR(500)` | - | Evet | - |
| `status` | `VARCHAR(50)` | - | Hayır | - |
| `admin_note` | `TEXT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `user` | `User` | `MANYTOONE` | Hayır |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `User` (Tablo: `users`)
*User model with Flask-Login support.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `email` | `VARCHAR(255)` | - | Hayır | - |
| `password_hash` | `VARCHAR(255)` | - | Hayır | - |
| `first_name` | `VARCHAR(64)` | - | Evet | - |
| `last_name` | `VARCHAR(64)` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `tenant_id` | `INTEGER` | - | Evet | tenants.id |
| `role_id` | `INTEGER` | - | Evet | roles.id |
| `created_at` | `DATETIME` | - | Evet | - |
| `phone_number` | `VARCHAR(20)` | - | Evet | - |
| `job_title` | `VARCHAR(100)` | - | Evet | - |
| `department` | `VARCHAR(100)` | - | Evet | - |
| `profile_picture` | `VARCHAR(500)` | - | Evet | - |
| `theme_preferences` | `TEXT` | - | Evet | - |
| `layout_preference` | `VARCHAR(20)` | - | Hayır | - |
| `notification_preferences` | `TEXT` | - | Evet | - |
| `locale_preferences` | `TEXT` | - | Evet | - |
| `show_page_guides` | `BOOLEAN` | - | Hayır | - |
| `guide_character_style` | `VARCHAR(50)` | - | Hayır | - |
| `totp_secret` | `VARCHAR(64)` | - | Evet | - |
| `totp_enabled` | `BOOLEAN` | - | Hayır | - |
| `totp_backup_codes_json` | `TEXT` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `role` | `Role` | `MANYTOONE` | Hayır |
| `tickets` | `Ticket` | `ONETOMANY` | Evet |
| `notifications` | `Notification` | `ONETOMANY` | Evet |
| `led_processes` | `Process` | `MANYTOMANY` | Evet |
| `member_processes` | `Process` | `MANYTOMANY` | Evet |
| `owned_processes` | `Process` | `MANYTOMANY` | Evet |
| `assigned_process_activities` | `ProcessActivity` | `MANYTOMANY` | Evet |
| `process_activity_assignments` | `ProcessActivityAssignee` | `ONETOMANY` | Evet |
| `assigned_process_activities_links` | `ProcessActivityAssignee` | `ONETOMANY` | Evet |
| `entered_kpi_data` | `KpiData` | `ONETOMANY` | Evet |
| `deleted_kpi_data_rows` | `KpiData` | `ONETOMANY` | Evet |
| `kpi_audits` | `KpiDataAudit` | `ONETOMANY` | Evet |
| `individual_performance_indicators` | `IndividualPerformanceIndicator` | `ONETOMANY` | Evet |
| `individual_activities` | `IndividualActivity` | `ONETOMANY` | Evet |
| `individual_kpi_audits` | `IndividualKpiDataAudit` | `ONETOMANY` | Evet |
| `individual_activity_tracks` | `IndividualActivityTrack` | `ONETOMANY` | Evet |
| `favorite_kpis` | `FavoriteKpi` | `ONETOMANY` | Evet |
| `k_radar_actions` | `KRadarRecommendationAction` | `ONETOMANY` | Evet |
| `k_vektor_snapshots` | `KVektorConfigSnapshot` | `ONETOMANY` | Evet |
| `year_assignments` | `UserYearAssignment` | `ONETOMANY` | Evet |
| `plan_project_tasks` | `PlanProjectTask` | `ONETOMANY` | Evet |
| `yonettigi_projeler` | `Project` | `ONETOMANY` | Evet |
| `lider_oldugu_projeler` | `Project` | `MANYTOMANY` | Evet |
| `uye_oldugu_projeler` | `Project` | `MANYTOMANY` | Evet |
| `gozlemci_oldugu_projeler` | `Project` | `MANYTOMANY` | Evet |
| `assigned_tasks` | `Task` | `ONETOMANY` | Evet |
| `reported_tasks` | `Task` | `ONETOMANY` | Evet |
| `task_comments` | `TaskComment` | `ONETOMANY` | Evet |

---

### 📁 `dashboard.py` İçindeki Modeller

#### 🏷️ Sınıf: `UserDashboardSettings` (Tablo: `user_dashboard_settings`)
*V3 Dashboard için kullanıcıya özel widget yerleşim ayarları.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | user.id |
| `layout_config` | `TEXT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `user` | `LegacyUser` | `MANYTOONE` | Hayır |

---

### 📁 `email_config.py` İçindeki Modeller

#### 🏷️ Sınıf: `TenantEmailConfig` (Tablo: `tenant_email_configs`)
*Tenant başına özel SMTP ayarları.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `use_custom_smtp` | `BOOLEAN` | - | Hayır | - |
| `smtp_host` | `VARCHAR(255)` | - | Evet | - |
| `smtp_port` | `INTEGER` | - | Evet | - |
| `smtp_use_tls` | `BOOLEAN` | - | Hayır | - |
| `smtp_use_ssl` | `BOOLEAN` | - | Hayır | - |
| `smtp_username` | `VARCHAR(255)` | - | Evet | - |
| `smtp_password` | `VARCHAR(512)` | - | Evet | - |
| `sender_name` | `VARCHAR(128)` | - | Evet | - |
| `sender_email` | `VARCHAR(255)` | - | Evet | - |
| `notify_on_process_assign` | `BOOLEAN` | - | Hayır | - |
| `notify_on_kpi_change` | `BOOLEAN` | - | Hayır | - |
| `notify_on_activity_add` | `BOOLEAN` | - | Hayır | - |
| `notify_on_task_assign` | `BOOLEAN` | - | Hayır | - |
| `updated_by` | `INTEGER` | - | Evet | users.id |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `updater` | `User` | `MANYTOONE` | Hayır |

---

### 📁 `esg.py` İçindeki Modeller

#### 🏷️ Sınıf: `EsgMetric` (Tablo: `esg_metrics`)
*ESG metric tanımı (tenant başına).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `code` | `VARCHAR(50)` | - | Evet | - |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `category` | `VARCHAR(50)` | - | Evet | - |
| `scope` | `VARCHAR(20)` | - | Evet | - |
| `unit` | `VARCHAR(50)` | - | Evet | - |
| `sdg_codes` | `VARCHAR(100)` | - | Evet | - |
| `target_value` | `FLOAT` | - | Evet | - |
| `baseline_year` | `INTEGER` | - | Evet | - |
| `baseline_value` | `FLOAT` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `values` | `EsgMetricValue` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `EsgMetricValue` (Tablo: `esg_metric_values`)
*ESG metric ölçüm (aylık/yıllık).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `metric_id` | `INTEGER` | - | Hayır | esg_metrics.id |
| `year` | `INTEGER` | - | Hayır | - |
| `period_type` | `VARCHAR(20)` | - | Evet | - |
| `period_no` | `INTEGER` | - | Evet | - |
| `value` | `FLOAT` | - | Evet | - |
| `source` | `VARCHAR(100)` | - | Evet | - |
| `notes` | `TEXT` | - | Evet | - |
| `user_id` | `INTEGER` | - | Evet | users.id |
| `created_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `metric` | `EsgMetric` | `MANYTOONE` | Hayır |

---

### 📁 `feedback.py` İçindeki Modeller

#### 🏷️ Sınıf: `Feedback` (Tablo: `feedback`)
*Geri Bildirim Modeli*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | user.id |
| `page_url` | `VARCHAR(500)` | - | Evet | - |
| `category` | `VARCHAR(50)` | - | Hayır | - |
| `description` | `TEXT` | - | Hayır | - |
| `screenshot_path` | `VARCHAR(500)` | - | Evet | - |
| `status` | `VARCHAR(50)` | - | Hayır | - |
| `admin_note` | `TEXT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `user` | `LegacyUser` | `MANYTOONE` | Hayır |

---

### 📁 `initiative.py` İçindeki Modeller

#### 🏷️ Sınıf: `Initiative` (Tablo: `initiatives`)
*Çok yıllık stratejik girişim (initiative).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `code` | `VARCHAR(40)` | - | Evet | - |
| `name` | `VARCHAR(300)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `strategy_id` | `INTEGER` | - | Evet | strategies.id |
| `sub_strategy_id` | `INTEGER` | - | Evet | sub_strategies.id |
| `start_year` | `INTEGER` | - | Hayır | - |
| `end_year` | `INTEGER` | - | Hayır | - |
| `start_date` | `DATE` | - | Evet | - |
| `end_date` | `DATE` | - | Evet | - |
| `status` | `VARCHAR(30)` | - | Hayır | - |
| `priority` | `VARCHAR(20)` | - | Hayır | - |
| `budget_total` | `NUMERIC(18, 2)` | - | Evet | - |
| `budget_spent` | `NUMERIC(18, 2)` | - | Evet | - |
| `progress_pct` | `FLOAT` | - | Hayır | - |
| `owner_user_id` | `INTEGER` | - | Evet | users.id |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `milestones` | `InitiativeMilestone` | `ONETOMANY` | Evet |
| `projects` | `Project` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `InitiativeMilestone` (Tablo: `initiative_milestones`)
*Initiative kilometre taşı.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `initiative_id` | `INTEGER` | - | Hayır | initiatives.id |
| `name` | `VARCHAR(300)` | - | Hayır | - |
| `target_date` | `DATE` | - | Evet | - |
| `completed_date` | `DATE` | - | Evet | - |
| `status` | `VARCHAR(30)` | - | Hayır | - |
| `note` | `TEXT` | - | Evet | - |
| `order_index` | `INTEGER` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `initiative` | `Initiative` | `MANYTOONE` | Hayır |

---

### 📁 `k_radar.py` İçindeki Modeller

#### 🏷️ Sınıf: `KRadarRecommendationAction` (Tablo: `k_radar_recommendation_actions`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `recommendation_key` | `VARCHAR(64)` | - | Hayır | - |
| `recommendation_text` | `TEXT` | - | Hayır | - |
| `state` | `VARCHAR(20)` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `user` | `User` | `MANYTOONE` | Hayır |

---

### 📁 `k_radar_domain.py` İçindeki Modeller

#### 🏷️ Sınıf: `A3Report` (Tablo: `a3_reports`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `source_type` | `VARCHAR(50)` | - | Evet | - |
| `source_id` | `INTEGER` | - | Evet | - |
| `problem` | `TEXT` | - | Evet | - |
| `root_cause_json` | `TEXT` | - | Evet | - |
| `countermeasures` | `TEXT` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

#### 🏷️ Sınıf: `BottleneckLog` (Tablo: `bottleneck_log`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `process_id` | `INTEGER` | - | Hayır | processes.id |
| `kpi_id` | `INTEGER` | - | Evet | process_kpis.id |
| `severity` | `VARCHAR(20)` | - | Evet | - |
| `note` | `TEXT` | - | Evet | - |
| `triggered_at` | `DATETIME` | - | Evet | - |
| `resolved_at` | `DATETIME` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

#### 🏷️ Sınıf: `CompetitorAnalysis` (Tablo: `competitor_analyses`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `plan_year_id` | `INTEGER` | - | Evet | plan_years.id |
| `competitor_name` | `VARCHAR(200)` | - | Hayır | - |
| `dimension` | `VARCHAR(100)` | - | Evet | - |
| `our_score` | `FLOAT` | - | Evet | - |
| `their_score` | `FLOAT` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

#### 🏷️ Sınıf: `EvmSnapshot` (Tablo: `evm_snapshots`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `project_id` | `INTEGER` | - | Hayır | project.id |
| `snapshot_date` | `DATE` | - | Hayır | - |
| `pv` | `FLOAT` | - | Evet | - |
| `ev` | `FLOAT` | - | Evet | - |
| `ac` | `FLOAT` | - | Evet | - |
| `spi` | `FLOAT` | - | Evet | - |
| `cpi` | `FLOAT` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

#### 🏷️ Sınıf: `ProcessMaturity` (Tablo: `process_maturity`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `process_id` | `INTEGER` | - | Hayır | processes.id |
| `maturity_level` | `INTEGER` | - | Hayır | - |
| `dimension` | `VARCHAR(100)` | - | Evet | - |
| `assessed_by` | `INTEGER` | - | Evet | users.id |
| `assessed_at` | `DATETIME` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

#### 🏷️ Sınıf: `RiskHeatmapItem` (Tablo: `risk_heatmap_items`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `plan_year_id` | `INTEGER` | - | Evet | plan_years.id |
| `title` | `VARCHAR(255)` | - | Hayır | - |
| `probability` | `INTEGER` | - | Hayır | - |
| `impact` | `INTEGER` | - | Hayır | - |
| `rpn` | `INTEGER` | - | Evet | - |
| `owner_id` | `INTEGER` | - | Evet | users.id |
| `status` | `VARCHAR(50)` | - | Evet | - |
| `source_type` | `VARCHAR(50)` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

#### 🏷️ Sınıf: `StakeholderMap` (Tablo: `stakeholder_maps`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `plan_year_id` | `INTEGER` | - | Evet | plan_years.id |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `role` | `VARCHAR(100)` | - | Evet | - |
| `influence` | `INTEGER` | - | Evet | - |
| `interest` | `INTEGER` | - | Evet | - |
| `strategy` | `VARCHAR(200)` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

#### 🏷️ Sınıf: `StakeholderSurvey` (Tablo: `stakeholder_surveys`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `stakeholder_type` | `VARCHAR(100)` | - | Hayır | - |
| `period` | `VARCHAR(50)` | - | Evet | - |
| `score` | `FLOAT` | - | Evet | - |
| `comment` | `TEXT` | - | Evet | - |
| `source` | `VARCHAR(100)` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

#### 🏷️ Sınıf: `ValueChainItem` (Tablo: `value_chain_items`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `category` | `VARCHAR(20)` | - | Hayır | - |
| `linked_process_id` | `INTEGER` | - | Evet | processes.id |
| `muda_type` | `VARCHAR(50)` | - | Evet | - |
| `title` | `VARCHAR(200)` | - | Hayır | - |
| `note` | `TEXT` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

### 📁 `k_vektor.py` İçindeki Modeller

#### 🏷️ Sınıf: `KVektorConfigSnapshot` (Tablo: `k_vektor_config_snapshots`)
*Yapılandırma / ağırlık değişikliği anı (denetim).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `user_id` | `INTEGER` | - | Evet | users.id |
| `snapshot_type` | `VARCHAR(64)` | - | Hayır | - |
| `payload_json` | `TEXT` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `user` | `User` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `KVektorStrategyWeight` (Tablo: `k_vektor_strategy_weights`)
*Ana strateji ham ağırlığı (K-Vektör kota bölüşümü).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `strategy_id` | `INTEGER` | - | Hayır | strategies.id |
| `weight_raw` | `FLOAT` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `strategy` | `Strategy` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `KVektorSubStrategyWeight` (Tablo: `k_vektor_sub_strategy_weights`)
*Alt strateji ham ağırlığı (ebeveyn ana strateji kotası içinde).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `sub_strategy_id` | `INTEGER` | - | Hayır | sub_strategies.id |
| `weight_raw` | `FLOAT` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `sub_strategy` | `SubStrategy` | `MANYTOONE` | Hayır |

---

### 📁 `llm_usage.py` İçindeki Modeller

#### 🏷️ Sınıf: `LLMQuotaOverride` (Tablo: `llm_quota_overrides`)
*Tenant'a özel kota overide (varsayılan paket limitlerini ezer).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `daily_call_limit` | `INTEGER` | - | Evet | - |
| `monthly_call_limit` | `INTEGER` | - | Evet | - |
| `monthly_cost_limit_usd` | `NUMERIC(10, 2)` | - | Evet | - |
| `is_paused` | `BOOLEAN` | - | Hayır | - |
| `note` | `TEXT` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

#### 🏷️ Sınıf: `LLMUsageLog` (Tablo: `llm_usage_logs`)
*Her LLM çağrısının ham kaydı.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `BIGINT` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `user_id` | `INTEGER` | - | Evet | users.id |
| `endpoint` | `VARCHAR(80)` | - | Hayır | - |
| `provider` | `VARCHAR(40)` | - | Hayır | - |
| `model` | `VARCHAR(80)` | - | Evet | - |
| `prompt_tokens` | `INTEGER` | - | Hayır | - |
| `output_tokens` | `INTEGER` | - | Hayır | - |
| `total_tokens` | `INTEGER` | - | Hayır | - |
| `cost_usd` | `NUMERIC(10, 6)` | - | Hayır | - |
| `status` | `VARCHAR(20)` | - | Hayır | - |
| `error_msg` | `VARCHAR(500)` | - | Evet | - |
| `duration_ms` | `INTEGER` | - | Evet | - |
| `created_at` | `DATETIME` | - | Hayır | - |

---

### 📁 `models.py` İçindeki Modeller

#### 🏷️ Sınıf: `Activity` (Tablo: `activity`)
*Genel Aktivite Modeli (V67)*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `source` | `VARCHAR(50)` | - | Hayır | - |
| `external_id` | `VARCHAR(100)` | - | Evet | - |
| `project_name` | `VARCHAR(200)` | - | Evet | - |
| `project_id` | `INTEGER` | - | Evet | project.id |
| `subject` | `VARCHAR(500)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `status` | `VARCHAR(50)` | - | Evet | - |
| `priority` | `VARCHAR(50)` | - | Evet | - |
| `assigned_to_id` | `INTEGER` | - | Evet | user.id |
| `date` | `DATETIME` | - | Evet | - |
| `due_date` | `DATE` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `project` | `Project` | `MANYTOONE` | Hayır |
| `assigned_to` | `LegacyUser` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `AuditLog` (Tablo: `audit_log`)
*Kullanıcı aksiyonlarına dayalı audit log.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | user.id |
| `user_name` | `VARCHAR(100)` | - | Evet | - |
| `action` | `VARCHAR(20)` | - | Hayır | - |
| `module` | `VARCHAR(100)` | - | Hayır | - |
| `record_id` | `INTEGER` | - | Hayır | - |
| `record_name` | `VARCHAR(255)` | - | Evet | - |
| `changes` | `JSON` | - | Evet | - |
| `timestamp` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `user` | `LegacyUser` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `Competency` (Tablo: `mock_competency`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `Competitor` (Tablo: `mock_competitor`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `CorporateIdentity` (Tablo: `corporate_identity`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |

---

#### 🏷️ Sınıf: `CrisisMode` (Tablo: `mock_crisismode`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `DaoProposal` (Tablo: `mock_daoproposal`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `DaoVote` (Tablo: `mock_daovote`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `DeepWorkSession` (Tablo: `mock_deepworksession`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `DoomsdayScenario` (Tablo: `mock_doomsdayscenario`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `GameScenario` (Tablo: `mock_gamescenario`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `GembaWalk` (Tablo: `mock_gembawalk`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `InfluenceScore` (Tablo: `mock_influencescore`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `LegacyKnowledge` (Tablo: `mock_legacyknowledge`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `MarketIntel` (Tablo: `mock_marketintel`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `MetaverseDepartment` (Tablo: `mock_metaversedepartment`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `MudaFinding` (Tablo: `mock_mudafinding`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `ObjectiveComment` (Tablo: `mock_objectivecomment`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `OrgChange` (Tablo: `mock_orgchange`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `OrgScenario` (Tablo: `mock_orgscenario`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `Persona` (Tablo: `mock_persona`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `PlanItem` (Tablo: `mock_planitem`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `ProductSimulation` (Tablo: `mock_productsimulation`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `SafetyCheck` (Tablo: `mock_safetycheck`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `SimulationScenario` (Tablo: `mock_simulationscenario`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `SmartContract` (Tablo: `mock_smartcontract`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `StrategicPlan` (Tablo: `mock_strategicplan`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `StrategicRisk` (Tablo: `mock_strategicrisk`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `SuccessionPlan` (Tablo: `mock_successionplan`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `UserCompetency` (Tablo: `mock_usercompetency`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `WellbeingScore` (Tablo: `mock_wellbeingscore`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

#### 🏷️ Sınıf: `YearlyChronicle` (Tablo: `mock_yearlychronicle`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |

---

### 📁 `notification.py` İçindeki Modeller

#### 🏷️ Sınıf: `Notification` (Tablo: `notifications_ext`)
*Bildirim tablosu*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Evet | users.id |
| `type` | `VARCHAR(50)` | - | Hayır | - |
| `title` | `VARCHAR(200)` | - | Hayır | - |
| `message` | `TEXT` | - | Hayır | - |
| `priority` | `VARCHAR(20)` | - | Evet | - |
| `action_url` | `VARCHAR(500)` | - | Evet | - |
| `extra_data` | `JSON` | - | Evet | - |
| `is_read` | `BOOLEAN` | - | Hayır | - |
| `read_at` | `DATETIME` | - | Evet | - |
| `created_at` | `DATETIME` | - | Hayır | - |

---

#### 🏷️ Sınıf: `NotificationPreference` (Tablo: `notification_preferences`)
*Bildirim tercihleri tablosu*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `email_performance_alerts` | `BOOLEAN` | - | Evet | - |
| `email_task_reminders` | `BOOLEAN` | - | Evet | - |
| `email_collaboration` | `BOOLEAN` | - | Evet | - |
| `email_achievements` | `BOOLEAN` | - | Evet | - |
| `email_system` | `BOOLEAN` | - | Evet | - |
| `inapp_performance_alerts` | `BOOLEAN` | - | Evet | - |
| `inapp_task_reminders` | `BOOLEAN` | - | Evet | - |
| `inapp_collaboration` | `BOOLEAN` | - | Evet | - |
| `inapp_achievements` | `BOOLEAN` | - | Evet | - |
| `inapp_system` | `BOOLEAN` | - | Evet | - |
| `push_enabled` | `BOOLEAN` | - | Evet | - |
| `push_performance_alerts` | `BOOLEAN` | - | Evet | - |
| `push_task_reminders` | `BOOLEAN` | - | Evet | - |
| `daily_digest` | `BOOLEAN` | - | Evet | - |
| `weekly_digest` | `BOOLEAN` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

---

#### 🏷️ Sınıf: `PushSubscription` (Tablo: `push_subscriptions`)
*Push notification subscription model*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Evet | users.id |
| `endpoint` | `TEXT` | - | Hayır | - |
| `p256dh` | `VARCHAR(255)` | - | Hayır | - |
| `auth` | `VARCHAR(255)` | - | Hayır | - |
| `is_active` | `BOOLEAN` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

---

### 📁 `okr.py` İçindeki Modeller

#### 🏷️ Sınıf: `OkrKeyResult` (Tablo: `okr_key_results`)
*Anahtar Sonuç (Key Result).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `objective_id` | `INTEGER` | - | Hayır | okr_objectives.id |
| `title` | `VARCHAR(300)` | - | Hayır | - |
| `metric` | `VARCHAR(100)` | - | Evet | - |
| `start_value` | `FLOAT` | - | Evet | - |
| `target_value` | `FLOAT` | - | Evet | - |
| `current_value` | `FLOAT` | - | Evet | - |
| `order_no` | `INTEGER` | - | Evet | - |
| `linked_process_kpi_id` | `INTEGER` | - | Evet | process_kpis.id |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `linked_process_kpi` | `ProcessKpi` | `MANYTOONE` | Hayır |
| `objective` | `OkrObjective` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `OkrObjective` (Tablo: `okr_objectives`)
*OKR Hedefi (Objective).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `title` | `VARCHAR(300)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `quarter` | `INTEGER` | - | Evet | - |
| `owner` | `VARCHAR(200)` | - | Evet | - |
| `order_no` | `INTEGER` | - | Evet | - |
| `linked_strategy_id` | `INTEGER` | - | Evet | strategies.id |
| `linked_sub_strategy_id` | `INTEGER` | - | Evet | sub_strategies.id |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `linked_strategy` | `Strategy` | `MANYTOONE` | Hayır |
| `linked_sub_strategy` | `SubStrategy` | `MANYTOONE` | Hayır |
| `key_results` | `OkrKeyResult` | `ONETOMANY` | Evet |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |

---

### 📁 `plan_year.py` İçindeki Modeller

#### 🏷️ Sınıf: `IndividualKpiYearConfig` (Tablo: `individual_kpi_year_configs`)
*Yıllık bireysel PG konfigürasyonu.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `individual_performance_id` | `INTEGER` | - | Hayır | individual_performance_indicators.id |
| `target_value` | `VARCHAR(100)` | - | Evet | - |
| `unit` | `VARCHAR(50)` | - | Evet | - |
| `period` | `VARCHAR(50)` | - | Evet | - |
| `direction` | `VARCHAR(20)` | - | Evet | - |
| `target_method` | `VARCHAR(10)` | - | Evet | - |
| `calculation_method` | `VARCHAR(20)` | - | Evet | - |
| `basari_puani_araliklari` | `TEXT` | - | Evet | - |
| `weight` | `FLOAT` | - | Evet | - |
| `is_included` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `individual_performance` | `IndividualPerformanceIndicator` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `KpiYearConfig` (Tablo: `kpi_year_configs`)
*Yıllık KPI konfigürasyonu.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `process_kpi_id` | `INTEGER` | - | Hayır | process_kpis.id |
| `target_value` | `VARCHAR(100)` | - | Evet | - |
| `unit` | `VARCHAR(50)` | - | Evet | - |
| `period` | `VARCHAR(50)` | - | Evet | - |
| `direction` | `VARCHAR(20)` | - | Evet | - |
| `target_method` | `VARCHAR(10)` | - | Evet | - |
| `calculation_method` | `VARCHAR(20)` | - | Evet | - |
| `basari_puani_araliklari` | `TEXT` | - | Evet | - |
| `onceki_yil_ortalamasi` | `FLOAT` | - | Evet | - |
| `weight` | `FLOAT` | - | Evet | - |
| `is_included` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `process_kpi` | `ProcessKpi` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `PlanYear` (Tablo: `plan_years`)
*Stratejik Plan Yılı.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `year` | `INTEGER` | - | Hayır | - |
| `name` | `VARCHAR(200)` | - | Evet | - |
| `status` | `VARCHAR(20)` | - | Hayır | - |
| `template_source_id` | `INTEGER` | - | Evet | plan_years.id |
| `created_at` | `DATETIME` | - | Hayır | - |
| `closed_at` | `DATETIME` | - | Evet | - |
| `scenario_of_id` | `INTEGER` | - | Evet | plan_years.id |
| `scenario_label` | `VARCHAR(80)` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `template_source` | `PlanYear` | `MANYTOONE` | Hayır |
| `derived_years` | `PlanYear` | `ONETOMANY` | Evet |
| `kpi_year_configs` | `KpiYearConfig` | `ONETOMANY` | Evet |
| `strategy_year_configs` | `StrategyYearConfig` | `ONETOMANY` | Evet |
| `sub_strategy_year_configs` | `SubStrategyYearConfig` | `ONETOMANY` | Evet |
| `process_year_configs` | `ProcessYearConfig` | `ONETOMANY` | Evet |
| `individual_kpi_year_configs` | `IndividualKpiYearConfig` | `ONETOMANY` | Evet |
| `tenant_year_identity` | `TenantYearIdentity` | `ONETOMANY` | Hayır |
| `user_assignments` | `UserYearAssignment` | `ONETOMANY` | Evet |
| `swot_analyses` | `SwotAnalysis` | `ONETOMANY` | Evet |
| `tows_analyses` | `TowsAnalysis` | `ONETOMANY` | Evet |
| `pestel_analyses` | `PestelAnalysis` | `ONETOMANY` | Evet |
| `porter_analyses` | `PorterFiveForcesAnalysis` | `ONETOMANY` | Evet |
| `okr_objectives` | `OkrObjective` | `ONETOMANY` | Evet |
| `bsc_kpi_perspectives` | `BscKpiPerspective` | `ONETOMANY` | Evet |
| `plan_projects` | `PlanProject` | `ONETOMANY` | Evet |
| `plan_project_tasks` | `PlanProjectTask` | `ONETOMANY` | Evet |
| `plan_project_activities` | `PlanProjectActivity` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `ProcessYearConfig` (Tablo: `process_year_configs`)
*Yıllık süreç override (ad, ağırlık, dahiliyet).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `process_id` | `INTEGER` | - | Hayır | processes.id |
| `name` | `VARCHAR(200)` | - | Evet | - |
| `weight` | `FLOAT` | - | Evet | - |
| `is_included` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `process` | `Process` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `StrategyYearConfig` (Tablo: `strategy_year_configs`)
*Yıllık strateji override (başlık, kod, açıklama, dahiliyet, ağırlık).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `strategy_id` | `INTEGER` | - | Hayır | strategies.id |
| `title` | `VARCHAR(200)` | - | Evet | - |
| `code` | `VARCHAR(20)` | - | Evet | - |
| `description` | `TEXT` | - | Evet | - |
| `is_included` | `BOOLEAN` | - | Hayır | - |
| `weight` | `FLOAT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `strategy` | `Strategy` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `SubStrategyYearConfig` (Tablo: `sub_strategy_year_configs`)
*Yıllık alt strateji override.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `sub_strategy_id` | `INTEGER` | - | Hayır | sub_strategies.id |
| `title` | `VARCHAR(200)` | - | Evet | - |
| `code` | `VARCHAR(20)` | - | Evet | - |
| `description` | `TEXT` | - | Evet | - |
| `is_included` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `sub_strategy` | `SubStrategy` | `MANYTOONE` | Hayır |

---

### 📁 `portfolio_project.py` İçindeki Modeller

#### 🏷️ Sınıf: `CapacityPlan` (Tablo: `capacity_plan`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `project_id` | `INTEGER` | - | Evet | project.id |
| `user_id` | `INTEGER` | - | Evet | users.id |
| `weekly_hours` | `FLOAT` | - | Hayır | - |
| `start_date` | `DATE` | - | Evet | - |
| `end_date` | `DATE` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `project` | `Project` | `MANYTOONE` | Hayır |
| `user` | `User` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `IntegrationHook` (Tablo: `integration_hook`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `project_id` | `INTEGER` | - | Hayır | project.id |
| `provider` | `VARCHAR(50)` | - | Hayır | - |
| `url` | `VARCHAR(500)` | - | Hayır | - |
| `is_active` | `BOOLEAN` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `project` | `Project` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `Project` (Tablo: `project`)
*Proje Modeli*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `manager_id` | `INTEGER` | - | Hayır | users.id |
| `start_date` | `DATE` | - | Evet | - |
| `end_date` | `DATE` | - | Evet | - |
| `priority` | `VARCHAR(50)` | - | Evet | - |
| `is_archived` | `BOOLEAN` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `deleted_at` | `DATETIME` | - | Evet | - |
| `deleted_by` | `INTEGER` | - | Evet | users.id |
| `health_score` | `INTEGER` | - | Evet | - |
| `health_status` | `VARCHAR(50)` | - | Evet | - |
| `notification_settings` | `TEXT` | - | Evet | - |
| `initiative_id` | `INTEGER` | - | Evet | initiatives.id |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `kurum` | `Kurum` | `MANYTOONE` | Hayır |
| `manager` | `User` | `MANYTOONE` | Hayır |
| `leaders` | `User` | `MANYTOMANY` | Evet |
| `members` | `User` | `MANYTOMANY` | Evet |
| `observers` | `User` | `MANYTOMANY` | Evet |
| `related_processes` | `Process` | `MANYTOMANY` | Evet |
| `initiative` | `Initiative` | `MANYTOONE` | Hayır |
| `tasks` | `Task` | `ONETOMANY` | Evet |
| `dependencies` | `TaskDependency` | `ONETOMANY` | Evet |
| `integration_hooks` | `IntegrationHook` | `ONETOMANY` | Evet |
| `rules` | `RuleDefinition` | `ONETOMANY` | Evet |
| `slas` | `SLA` | `ONETOMANY` | Evet |
| `recurring_tasks` | `RecurringTask` | `ONETOMANY` | Evet |
| `working_days` | `WorkingDay` | `ONETOMANY` | Evet |
| `capacity_plans` | `CapacityPlan` | `ONETOMANY` | Evet |
| `raid_items` | `RaidItem` | `ONETOMANY` | Evet |
| `activities` | `Activity` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `ProjectFile` (Tablo: `project_file`)
*Proje Dosyaları*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `project_id` | `INTEGER` | - | Hayır | project.id |
| `uploader_id` | `INTEGER` | - | Hayır | users.id |
| `filename` | `VARCHAR(255)` | - | Hayır | - |
| `file_path` | `VARCHAR(500)` | - | Hayır | - |
| `file_type` | `VARCHAR(50)` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |

---

#### 🏷️ Sınıf: `ProjectRisk` (Tablo: `project_risk`)
*Proje Riskleri*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `project_id` | `INTEGER` | - | Hayır | project.id |
| `title` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `probability` | `VARCHAR(20)` | - | Evet | - |
| `impact` | `VARCHAR(20)` | - | Evet | - |
| `status` | `VARCHAR(20)` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |

---

#### 🏷️ Sınıf: `ProjectTemplate` (Tablo: `project_template`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `structure` | `TEXT` | - | Evet | - |

---

#### 🏷️ Sınıf: `RaidItem` (Tablo: `raid_item`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `project_id` | `INTEGER` | - | Hayır | project.id |
| `item_type` | `VARCHAR(20)` | - | Hayır | - |
| `title` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `owner_id` | `INTEGER` | - | Evet | users.id |
| `status` | `VARCHAR(50)` | - | Evet | - |
| `probability` | `INTEGER` | - | Evet | - |
| `impact` | `INTEGER` | - | Evet | - |
| `mitigation_plan` | `TEXT` | - | Evet | - |
| `assumption_validation_date` | `DATE` | - | Evet | - |
| `assumption_validated` | `BOOLEAN` | - | Evet | - |
| `assumption_notes` | `TEXT` | - | Evet | - |
| `issue_urgency` | `VARCHAR(50)` | - | Evet | - |
| `issue_affected_work` | `VARCHAR(200)` | - | Evet | - |
| `dependency_task_id` | `INTEGER` | - | Evet | - |
| `dependency_type` | `VARCHAR(50)` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `project` | `Project` | `MANYTOONE` | Hayır |
| `owner` | `User` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `RecurringTask` (Tablo: `recurring_task`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `project_id` | `INTEGER` | - | Hayır | project.id |
| `title` | `VARCHAR(200)` | - | Hayır | - |
| `cron_expr` | `VARCHAR(100)` | - | Hayır | - |
| `template_task_id` | `INTEGER` | - | Evet | task.id |
| `next_run_at` | `DATETIME` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `project` | `Project` | `MANYTOONE` | Hayır |
| `template_task` | `Task` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `RuleDefinition` (Tablo: `rule_definition`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `project_id` | `INTEGER` | - | Evet | project.id |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `trigger` | `VARCHAR(100)` | - | Hayır | - |
| `condition_json` | `TEXT` | - | Evet | - |
| `actions_json` | `TEXT` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `project` | `Project` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `SLA` (Tablo: `sla`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `project_id` | `INTEGER` | - | Evet | project.id |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `target_hours` | `INTEGER` | - | Hayır | - |
| `breach_policy` | `VARCHAR(200)` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `project` | `Project` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `Sprint` (Tablo: `sprint`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `project_id` | `INTEGER` | - | Hayır | project.id |
| `name` | `VARCHAR(100)` | - | Hayır | - |
| `start_date` | `DATE` | - | Evet | - |
| `end_date` | `DATE` | - | Evet | - |
| `status` | `VARCHAR(20)` | - | Evet | - |

---

#### 🏷️ Sınıf: `Tag` (Tablo: `tag`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `name` | `VARCHAR(50)` | - | Hayır | - |
| `color` | `VARCHAR(20)` | - | Evet | - |

---

#### 🏷️ Sınıf: `Task` (Tablo: `task`)
*Görev Modeli*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `project_id` | `INTEGER` | - | Hayır | project.id |
| `title` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `assignee_id` | `INTEGER` | - | Evet | users.id |
| `reporter_id` | `INTEGER` | - | Hayır | users.id |
| `external_assignee_name` | `VARCHAR(200)` | - | Evet | - |
| `parent_id` | `INTEGER` | - | Evet | task.id |
| `estimated_time` | `FLOAT` | - | Evet | - |
| `actual_time` | `FLOAT` | - | Evet | - |
| `progress` | `INTEGER` | - | Evet | - |
| `completed_at` | `DATETIME` | - | Evet | - |
| `is_measurable` | `BOOLEAN` | - | Evet | - |
| `planned_output_value` | `FLOAT` | - | Evet | - |
| `related_indicator_id` | `INTEGER` | - | Evet | - |
| `process_kpi_id` | `INTEGER` | - | Evet | process_kpis.id |
| `status` | `VARCHAR(50)` | - | Evet | - |
| `priority` | `VARCHAR(50)` | - | Evet | - |
| `is_archived` | `BOOLEAN` | - | Evet | - |
| `due_date` | `DATE` | - | Evet | - |
| `start_date` | `DATE` | - | Evet | - |
| `reminder_date` | `DATETIME` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `project` | `Project` | `MANYTOONE` | Hayır |
| `assignee` | `User` | `MANYTOONE` | Hayır |
| `reporter` | `User` | `MANYTOONE` | Hayır |
| `parent` | `Task` | `MANYTOONE` | Hayır |
| `predecessors` | `Task` | `MANYTOMANY` | Evet |
| `dependencies_in` | `TaskDependency` | `ONETOMANY` | Evet |
| `dependencies_out` | `TaskDependency` | `ONETOMANY` | Evet |
| `children` | `Task` | `ONETOMANY` | Evet |
| `successors` | `Task` | `MANYTOMANY` | Evet |
| `impacts` | `TaskImpact` | `ONETOMANY` | Evet |
| `comments` | `TaskComment` | `ONETOMANY` | Evet |
| `baseline` | `TaskBaseline` | `ONETOMANY` | Hayır |

---

#### 🏷️ Sınıf: `TaskActivity` (Tablo: `task_activity`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `task_id` | `INTEGER` | - | Hayır | task.id |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `activity_type` | `VARCHAR(50)` | - | Evet | - |
| `details` | `TEXT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |

---

#### 🏷️ Sınıf: `TaskBaseline` (Tablo: `task_baseline`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `task_id` | `INTEGER` | - | Hayır | task.id |
| `planned_start` | `DATE` | - | Evet | - |
| `planned_end` | `DATE` | - | Evet | - |
| `planned_effort` | `FLOAT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `task` | `Task` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `TaskComment` (Tablo: `task_comment`)
*Görev Yorumları*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `task_id` | `INTEGER` | - | Hayır | task.id |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `comment` | `TEXT` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `task` | `Task` | `MANYTOONE` | Hayır |
| `user` | `User` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `TaskDependency` (Tablo: `task_dependency`)
*Görev bağımlılıkları (tip ve lag içeren).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `project_id` | `INTEGER` | - | Hayır | project.id |
| `successor_id` | `INTEGER` | - | Hayır | task.id |
| `predecessor_id` | `INTEGER` | - | Hayır | task.id |
| `dependency_type` | `VARCHAR(4)` | - | Evet | - |
| `lag_days` | `INTEGER` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `project` | `Project` | `MANYTOONE` | Hayır |
| `successor` | `Task` | `MANYTOONE` | Hayır |
| `predecessor` | `Task` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `TaskImpact` (Tablo: `task_impact`)
*Görev Etki Analizi Modeli*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `task_id` | `INTEGER` | - | Hayır | task.id |
| `related_pg_id` | `INTEGER` | - | Evet | - |
| `related_faaliyet_id` | `INTEGER` | - | Evet | - |
| `impact_value` | `VARCHAR(50)` | - | Evet | - |
| `description` | `TEXT` | - | Evet | - |
| `is_processed` | `BOOLEAN` | - | Evet | - |
| `processed_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `task` | `Task` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `TaskMention` (Tablo: `task_mention`)
*Görev içi kullanıcı etiketleme*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `task_id` | `INTEGER` | - | Hayır | task.id |
| `mentioned_user_id` | `INTEGER` | - | Hayır | users.id |
| `comment_id` | `INTEGER` | - | Evet | task_comment.id |
| `created_at` | `DATETIME` | - | Evet | - |

---

#### 🏷️ Sınıf: `TaskSprint` (Tablo: `task_sprint`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `task_id` | `INTEGER` | ✅ | Hayır | task.id |
| `sprint_id` | `INTEGER` | ✅ | Hayır | sprint.id |

---

#### 🏷️ Sınıf: `TaskSubtask` (Tablo: `task_subtask`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `task_id` | `INTEGER` | - | Hayır | task.id |
| `title` | `VARCHAR(200)` | - | Hayır | - |
| `is_completed` | `BOOLEAN` | - | Evet | - |

---

#### 🏷️ Sınıf: `TaskTemplate` (Tablo: `task_template`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |

---

#### 🏷️ Sınıf: `TimeEntry` (Tablo: `time_entry`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `task_id` | `INTEGER` | - | Hayır | task.id |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `duration_minutes` | `INTEGER` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `date` | `DATE` | - | Evet | - |

---

#### 🏷️ Sınıf: `WorkingDay` (Tablo: `working_day`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `project_id` | `INTEGER` | - | Evet | project.id |
| `date` | `DATE` | - | Hayır | - |
| `is_working` | `BOOLEAN` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `project` | `Project` | `MANYTOONE` | Hayır |

---

### 📁 `process.py` İçindeki Modeller

#### 🏷️ Sınıf: `ActivityTrack` (Tablo: `activity_tracks`)
*Monthly tracking for process activities (Aylık Faaliyet Takibi).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `activity_id` | `INTEGER` | - | Hayır | process_activities.id |
| `year` | `INTEGER` | - | Hayır | - |
| `month` | `INTEGER` | - | Hayır | - |
| `completed` | `BOOLEAN` | - | Hayır | - |
| `user_id` | `INTEGER` | - | Evet | users.id |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `activity` | `ProcessActivity` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `FavoriteKpi` (Tablo: `favorite_kpis`)
*Favori Performans Göstergesi*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `process_kpi_id` | `INTEGER` | - | Hayır | process_kpis.id |
| `sort_order` | `INTEGER` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `user` | `User` | `MANYTOONE` | Hayır |
| `process_kpi` | `ProcessKpi` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `IndividualActivity` (Tablo: `individual_activities`)
*Bireysel Faaliyet.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `start_date` | `DATE` | - | Evet | - |
| `end_date` | `DATE` | - | Evet | - |
| `status` | `VARCHAR(50)` | - | Evet | - |
| `progress` | `INTEGER` | - | Evet | - |
| `source` | `VARCHAR(50)` | - | Evet | - |
| `source_process_id` | `INTEGER` | - | Evet | processes.id |
| `source_process_activity_id` | `INTEGER` | - | Evet | process_activities.id |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `user` | `User` | `MANYTOONE` | Hayır |
| `source_process` | `Process` | `MANYTOONE` | Hayır |
| `source_process_activity` | `ProcessActivity` | `MANYTOONE` | Hayır |
| `tracks` | `IndividualActivityTrack` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `IndividualActivityTrack` (Tablo: `individual_activity_tracks`)
*Bireysel faaliyet aylık takibi (FaaliyetTakip)*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `individual_activity_id` | `INTEGER` | - | Hayır | individual_activities.id |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `year` | `INTEGER` | - | Hayır | - |
| `month` | `INTEGER` | - | Hayır | - |
| `completed` | `BOOLEAN` | - | Evet | - |
| `note` | `TEXT` | - | Evet | - |
| `completed_date` | `DATE` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `individual_activity` | `IndividualActivity` | `MANYTOONE` | Hayır |
| `user` | `User` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `IndividualKpiData` (Tablo: `individual_kpi_data`)
*Bireysel PG'ye bağlı performans verisi (PerformansGostergeVeri).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `individual_pg_id` | `INTEGER` | - | Hayır | individual_performance_indicators.id |
| `year` | `INTEGER` | - | Hayır | - |
| `data_date` | `DATE` | - | Hayır | - |
| `period_type` | `VARCHAR(20)` | - | Evet | - |
| `period_no` | `INTEGER` | - | Evet | - |
| `period_month` | `INTEGER` | - | Evet | - |
| `target_value` | `VARCHAR(100)` | - | Evet | - |
| `actual_value` | `VARCHAR(100)` | - | Hayır | - |
| `status` | `VARCHAR(50)` | - | Evet | - |
| `status_percentage` | `FLOAT` | - | Evet | - |
| `description` | `TEXT` | - | Evet | - |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `individual_pg` | `IndividualPerformanceIndicator` | `MANYTOONE` | Hayır |
| `user` | `User` | `MANYTOONE` | Hayır |
| `audits` | `IndividualKpiDataAudit` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `IndividualKpiDataAudit` (Tablo: `individual_kpi_data_audits`)
*Bireysel PG Veri Değişiklik Geçmişi (Audit Log)*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `individual_kpi_data_id` | `INTEGER` | - | Hayır | individual_kpi_data.id |
| `action_type` | `VARCHAR(20)` | - | Hayır | - |
| `old_value` | `TEXT` | - | Evet | - |
| `new_value` | `TEXT` | - | Evet | - |
| `action_detail` | `TEXT` | - | Evet | - |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `created_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `individual_kpi_data` | `IndividualKpiData` | `MANYTOONE` | Hayır |
| `user` | `User` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `IndividualPerformanceIndicator` (Tablo: `individual_performance_indicators`)
*Bireysel Performans Göstergesi (Bireysel PG).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `code` | `VARCHAR(50)` | - | Evet | - |
| `target_value` | `VARCHAR(100)` | - | Evet | - |
| `actual_value` | `VARCHAR(100)` | - | Evet | - |
| `unit` | `VARCHAR(50)` | - | Evet | - |
| `period` | `VARCHAR(50)` | - | Evet | - |
| `weight` | `FLOAT` | - | Evet | - |
| `is_important` | `BOOLEAN` | - | Evet | - |
| `start_date` | `DATE` | - | Evet | - |
| `end_date` | `DATE` | - | Evet | - |
| `status` | `VARCHAR(50)` | - | Evet | - |
| `source` | `VARCHAR(50)` | - | Evet | - |
| `source_process_id` | `INTEGER` | - | Evet | processes.id |
| `source_process_kpi_id` | `INTEGER` | - | Evet | process_kpis.id |
| `direction` | `VARCHAR(20)` | - | Evet | - |
| `basari_puani_araliklari` | `TEXT` | - | Evet | - |
| `plan_year_id` | `INTEGER` | - | Evet | plan_years.id |
| `source_individual_kpi_id` | `INTEGER` | - | Evet | individual_performance_indicators.id |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `user` | `User` | `MANYTOONE` | Hayır |
| `source_process` | `Process` | `MANYTOONE` | Hayır |
| `source_process_kpi` | `ProcessKpi` | `MANYTOONE` | Hayır |
| `data_entries` | `IndividualKpiData` | `ONETOMANY` | Evet |
| `year_configs` | `IndividualKpiYearConfig` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `KpiData` (Tablo: `kpi_data`)
*KPI Data Model (Performans Gösterge Veri)*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `process_kpi_id` | `INTEGER` | - | Hayır | process_kpis.id |
| `year` | `INTEGER` | - | Hayır | - |
| `data_date` | `DATE` | - | Hayır | - |
| `period_type` | `VARCHAR(20)` | - | Evet | - |
| `period_no` | `INTEGER` | - | Evet | - |
| `period_month` | `INTEGER` | - | Evet | - |
| `target_value` | `VARCHAR(100)` | - | Evet | - |
| `actual_value` | `VARCHAR(100)` | - | Evet | - |
| `status` | `VARCHAR(50)` | - | Evet | - |
| `status_percentage` | `FLOAT` | - | Evet | - |
| `description` | `TEXT` | - | Evet | - |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `deleted_at` | `DATETIME` | - | Evet | - |
| `deleted_by_id` | `INTEGER` | - | Evet | users.id |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `process_kpi` | `ProcessKpi` | `MANYTOONE` | Hayır |
| `user` | `User` | `MANYTOONE` | Hayır |
| `deleted_by` | `User` | `MANYTOONE` | Hayır |
| `audits` | `KpiDataAudit` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `KpiDataAudit` (Tablo: `kpi_data_audits`)
*KPI Data Audit Log*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `kpi_data_id` | `INTEGER` | - | Hayır | kpi_data.id |
| `action_type` | `VARCHAR(20)` | - | Hayır | - |
| `old_value` | `TEXT` | - | Evet | - |
| `new_value` | `TEXT` | - | Evet | - |
| `action_detail` | `TEXT` | - | Evet | - |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `created_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `kpi_data` | `KpiData` | `MANYTOONE` | Hayır |
| `user` | `User` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `Process` (Tablo: `processes`)
*Process Model (Süreç)*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `parent_id` | `INTEGER` | - | Evet | processes.id |
| `code` | `VARCHAR(20)` | - | Evet | - |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `english_name` | `VARCHAR(200)` | - | Evet | - |
| `weight` | `FLOAT` | - | Evet | - |
| `document_no` | `VARCHAR(50)` | - | Evet | - |
| `revision_no` | `VARCHAR(20)` | - | Evet | - |
| `revision_date` | `DATE` | - | Evet | - |
| `first_publish_date` | `DATE` | - | Evet | - |
| `status` | `VARCHAR(50)` | - | Evet | - |
| `progress` | `INTEGER` | - | Evet | - |
| `start_boundary` | `TEXT` | - | Evet | - |
| `end_boundary` | `TEXT` | - | Evet | - |
| `start_date` | `DATE` | - | Evet | - |
| `end_date` | `DATE` | - | Evet | - |
| `description` | `TEXT` | - | Evet | - |
| `plan_year_id` | `INTEGER` | - | Evet | plan_years.id |
| `source_process_id` | `INTEGER` | - | Evet | processes.id |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `deleted_at` | `DATETIME` | - | Evet | - |
| `deleted_by` | `INTEGER` | - | Evet | users.id |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `parent` | `Process` | `MANYTOONE` | Hayır |
| `leaders` | `User` | `MANYTOMANY` | Evet |
| `members` | `User` | `MANYTOMANY` | Evet |
| `owners` | `User` | `MANYTOMANY` | Evet |
| `process_sub_strategy_links` | `ProcessSubStrategyLink` | `ONETOMANY` | Evet |
| `sub_processes` | `Process` | `ONETOMANY` | Evet |
| `kpis` | `ProcessKpi` | `ONETOMANY` | Evet |
| `activities` | `ProcessActivity` | `ONETOMANY` | Evet |
| `year_configs` | `ProcessYearConfig` | `ONETOMANY` | Evet |
| `bagli_projeler` | `Project` | `MANYTOMANY` | Evet |
| `strategy_matrix_relations` | `StrategyProcessMatrix` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `ProcessActivity` (Tablo: `process_activities`)
*Process Activity Model (Süreç Faaliyeti/Aksiyon).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `process_id` | `INTEGER` | - | Hayır | processes.id |
| `process_kpi_id` | `INTEGER` | - | Evet | process_kpis.id |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `start_date` | `DATE` | - | Evet | - |
| `end_date` | `DATE` | - | Evet | - |
| `start_at` | `DATETIME` | - | Evet | - |
| `end_at` | `DATETIME` | - | Evet | - |
| `status` | `VARCHAR(50)` | - | Evet | - |
| `progress` | `INTEGER` | - | Evet | - |
| `notify_email` | `BOOLEAN` | - | Hayır | - |
| `auto_complete_enabled` | `BOOLEAN` | - | Hayır | - |
| `auto_pgv_created` | `BOOLEAN` | - | Hayır | - |
| `auto_pgv_kpi_data_id` | `INTEGER` | - | Evet | kpi_data.id |
| `completed_at` | `DATETIME` | - | Evet | - |
| `cancelled_at` | `DATETIME` | - | Evet | - |
| `postponed_at` | `DATETIME` | - | Evet | - |
| `plan_year_id` | `INTEGER` | - | Evet | plan_years.id |
| `source_activity_id` | `INTEGER` | - | Evet | process_activities.id |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `process` | `Process` | `MANYTOONE` | Hayır |
| `process_kpi` | `ProcessKpi` | `MANYTOONE` | Hayır |
| `auto_pgv_kpi_data` | `KpiData` | `MANYTOONE` | Hayır |
| `assignees` | `User` | `MANYTOMANY` | Evet |
| `assignment_links` | `ProcessActivityAssignee` | `ONETOMANY` | Evet |
| `reminders` | `ProcessActivityReminder` | `ONETOMANY` | Evet |
| `tracks` | `ActivityTrack` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `ProcessActivityAssignee` (Tablo: `process_activity_assignees`)
*V2: Süreç faaliyeti çoklu atama ilişkisi.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `activity_id` | `INTEGER` | ✅ | Hayır | process_activities.id |
| `user_id` | `INTEGER` | ✅ | Hayır | users.id |
| `order_no` | `INTEGER` | - | Hayır | - |
| `assigned_by` | `INTEGER` | - | Evet | users.id |
| `assigned_at` | `DATETIME` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `activity` | `ProcessActivity` | `MANYTOONE` | Hayır |
| `user` | `User` | `MANYTOONE` | Hayır |
| `assigner` | `User` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `ProcessActivityReminder` (Tablo: `process_activity_reminders`)
*V2: Süreç faaliyeti için çoklu hatırlatma satırları.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `activity_id` | `INTEGER` | - | Hayır | process_activities.id |
| `minutes_before` | `INTEGER` | - | Hayır | - |
| `remind_at` | `DATETIME` | - | Hayır | - |
| `channel_email` | `BOOLEAN` | - | Hayır | - |
| `sent_at` | `DATETIME` | - | Evet | - |
| `created_at` | `DATETIME` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `activity` | `ProcessActivity` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `ProcessKpi` (Tablo: `process_kpis`)
*Process Key Performance Indicator Model (Süreç PG)*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `process_id` | `INTEGER` | - | Hayır | processes.id |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `code` | `VARCHAR(50)` | - | Evet | - |
| `target_value` | `VARCHAR(100)` | - | Evet | - |
| `unit` | `VARCHAR(50)` | - | Evet | - |
| `period` | `VARCHAR(50)` | - | Evet | - |
| `data_source` | `VARCHAR(200)` | - | Evet | - |
| `target_setting_method` | `VARCHAR(200)` | - | Evet | - |
| `data_collection_method` | `VARCHAR(50)` | - | Evet | - |
| `calculation_method` | `VARCHAR(20)` | - | Evet | - |
| `gosterge_turu` | `VARCHAR(50)` | - | Evet | - |
| `target_method` | `VARCHAR(10)` | - | Evet | - |
| `basari_puani_araliklari` | `TEXT` | - | Evet | - |
| `onceki_yil_ortalamasi` | `FLOAT` | - | Evet | - |
| `weight` | `FLOAT` | - | Evet | - |
| `is_important` | `BOOLEAN` | - | Evet | - |
| `direction` | `VARCHAR(20)` | - | Evet | - |
| `calculated_score` | `FLOAT` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `sub_strategy_id` | `INTEGER` | - | Evet | sub_strategies.id |
| `plan_year_id` | `INTEGER` | - | Evet | plan_years.id |
| `source_kpi_id` | `INTEGER` | - | Evet | process_kpis.id |
| `start_date` | `DATE` | - | Evet | - |
| `end_date` | `DATE` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `process` | `Process` | `MANYTOONE` | Hayır |
| `sub_strategy` | `SubStrategy` | `MANYTOONE` | Hayır |
| `activities` | `ProcessActivity` | `ONETOMANY` | Evet |
| `data_entries` | `KpiData` | `ONETOMANY` | Evet |
| `favorited_by` | `FavoriteKpi` | `ONETOMANY` | Evet |
| `year_configs` | `KpiYearConfig` | `ONETOMANY` | Evet |
| `bsc_perspective` | `BscKpiPerspective` | `ONETOMANY` | Hayır |

---

#### 🏷️ Sınıf: `ProcessSubStrategyLink` (Tablo: `process_sub_strategy_links`)
*Süreç–Alt Strateji bağlantısı; her bağlantıya katkı yüzdesi atanabilir.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `process_id` | `INTEGER` | ✅ | Hayır | processes.id |
| `sub_strategy_id` | `INTEGER` | ✅ | Hayır | sub_strategies.id |
| `contribution_pct` | `FLOAT` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `process` | `Process` | `MANYTOONE` | Hayır |
| `sub_strategy` | `SubStrategy` | `MANYTOONE` | Hayır |

---

### 📁 `project.py` İçindeki Modeller

#### 🏷️ Sınıf: `PlanProject` (Tablo: `plan_projects`)
*SP Proje. Her PlanYear kapsaminda olusturulur/klonlanir.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `source_project_id` | `INTEGER` | - | Evet | plan_projects.id |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `status` | `VARCHAR(50)` | - | Hayır | - |
| `progress` | `INTEGER` | - | Hayır | - |
| `start_date` | `DATE` | - | Evet | - |
| `end_date` | `DATE` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `source_project` | `PlanProject` | `MANYTOONE` | Hayır |
| `tasks` | `PlanProjectTask` | `ONETOMANY` | Evet |
| `activities` | `PlanProjectActivity` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `PlanProjectActivity` (Tablo: `plan_project_activities`)
*SP Proje Faaliyeti.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `project_id` | `INTEGER` | - | Hayır | plan_projects.id |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `status` | `VARCHAR(50)` | - | Hayır | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `project` | `PlanProject` | `MANYTOONE` | Hayır |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `PlanProjectTask` (Tablo: `plan_project_tasks`)
*SP Proje Gorevi.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `project_id` | `INTEGER` | - | Hayır | plan_projects.id |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `assignee_id` | `INTEGER` | - | Evet | users.id |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `status` | `VARCHAR(50)` | - | Hayır | - |
| `start_date` | `DATE` | - | Evet | - |
| `end_date` | `DATE` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `progress_pct` | `FLOAT` | - | Hayır | - |
| `planned_budget` | `NUMERIC(18, 2)` | - | Evet | - |
| `actual_cost` | `NUMERIC(18, 2)` | - | Evet | - |
| `depends_on_task_id` | `INTEGER` | - | Evet | plan_project_tasks.id |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `project` | `PlanProject` | `MANYTOONE` | Hayır |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `assignee` | `User` | `MANYTOONE` | Hayır |

---

### 📁 `replan_trigger.py` İçindeki Modeller

#### 🏷️ Sınıf: `ReplanTrigger` (Tablo: `replan_triggers`)
*Stratejik yeniden planlama tetikleyicisi.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `description` | `TEXT` | - | Evet | - |
| `trigger_type` | `VARCHAR(40)` | - | Hayır | - |
| `target_kpi_id` | `INTEGER` | - | Evet | process_kpis.id |
| `threshold_value` | `FLOAT` | - | Evet | - |
| `threshold_operator` | `VARCHAR(5)` | - | Evet | - |
| `consecutive_periods` | `INTEGER` | - | Hayır | - |
| `action` | `VARCHAR(40)` | - | Hayır | - |
| `severity` | `VARCHAR(20)` | - | Hayır | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `last_fired_at` | `DATETIME` | - | Evet | - |
| `fire_count` | `INTEGER` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

#### 🏷️ Sınıf: `ReplanTriggerEvent` (Tablo: `replan_trigger_events`)
*Bir trigger'ın tetiklendiği olayın günlüğü.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `trigger_id` | `INTEGER` | - | Hayır | replan_triggers.id |
| `tenant_id` | `INTEGER` | - | Hayır | - |
| `fired_at` | `DATETIME` | - | Hayır | - |
| `payload` | `TEXT` | - | Evet | - |
| `action_taken` | `VARCHAR(40)` | - | Evet | - |
| `acknowledged_at` | `DATETIME` | - | Evet | - |
| `acknowledged_by_user_id` | `INTEGER` | - | Evet | users.id |

---

### 📁 `saas.py` İçindeki Modeller

#### 🏷️ Sınıf: `ModuleComponentSlug` (Tablo: `module_component_slugs`)
*Modül-Bileşen ilişkisi - bileşen = RouteRegistry.component_slug.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `module_id` | `INTEGER` | ✅ | Hayır | system_modules.id |
| `component_slug` | `VARCHAR(128)` | ✅ | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `module` | `SystemModule` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `RouteRegistry` (Tablo: `route_registry`)
*Dinamik rota kaydı - Auto-Discovery bileşen eşleştirmesi.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `endpoint` | `VARCHAR(255)` | - | Hayır | - |
| `url_rule` | `VARCHAR(512)` | - | Hayır | - |
| `methods` | `VARCHAR(128)` | - | Evet | - |
| `component_slug` | `VARCHAR(128)` | - | Evet | - |

---

#### 🏷️ Sınıf: `SubscriptionPackage` (Tablo: `subscription_packages`)
*Subscription package containing modules.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `name` | `VARCHAR(128)` | - | Hayır | - |
| `code` | `VARCHAR(64)` | - | Hayır | - |
| `description` | `VARCHAR(512)` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `modules` | `SystemModule` | `MANYTOMANY` | Evet |
| `tenants` | `Tenant` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `SystemComponent` (Tablo: `system_components`)
*Sistem bileşeni — tenant paketinde yetkilendirme için slug (code).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `name` | `VARCHAR(128)` | - | Hayır | - |
| `code` | `VARCHAR(64)` | - | Hayır | - |
| `description` | `VARCHAR(512)` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |

---

#### 🏷️ Sınıf: `SystemModule` (Tablo: `system_modules`)
*System module - bileşenler = RouteRegistry.component_slug (Bileşenler sekmesindeki Bileşen İsmi).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `name` | `VARCHAR(128)` | - | Hayır | - |
| `code` | `VARCHAR(64)` | - | Hayır | - |
| `description` | `VARCHAR(512)` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `component_slugs` | `ModuleComponentSlug` | `ONETOMANY` | Evet |
| `packages` | `SubscriptionPackage` | `MANYTOMANY` | Evet |

---

### 📁 `strategy.py` İçindeki Modeller

#### 🏷️ Sınıf: `AltStrateji` (Tablo: `alt_strateji`)
*Alt Strateji Modeli*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `ana_strateji_id` | `INTEGER` | - | Hayır | ana_strateji.id |
| `code` | `VARCHAR(20)` | - | Evet | - |
| `ad` | `VARCHAR(200)` | - | Hayır | - |
| `name` | `VARCHAR(200)` | - | Evet | - |
| `target_method` | `VARCHAR(10)` | - | Evet | - |
| `aciklama` | `TEXT` | - | Evet | - |
| `weight` | `FLOAT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `ana_strateji` | `AnaStrateji` | `MANYTOONE` | Hayır |
| `matrix_relations` | `StrategyProcessMatrix` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `AnaStrateji` (Tablo: `ana_strateji`)
*Ana Strateji Modeli*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `code` | `VARCHAR(20)` | - | Evet | - |
| `ad` | `VARCHAR(200)` | - | Hayır | - |
| `name` | `VARCHAR(200)` | - | Evet | - |
| `aciklama` | `TEXT` | - | Evet | - |
| `perspective` | `VARCHAR(20)` | - | Evet | - |
| `bsc_code` | `VARCHAR(10)` | - | Evet | - |
| `weight` | `FLOAT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `kurum` | `Kurum` | `MANYTOONE` | Hayır |
| `alt_stratejiler` | `AltStrateji` | `ONETOMANY` | Evet |
| `bsc_out_links` | `StrategyMapLink` | `ONETOMANY` | Evet |
| `bsc_in_links` | `StrategyMapLink` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `StrategyMapLink` (Tablo: `strategy_map_link`)
*BSC Strateji Haritası Bağlantı Modeli*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `source_id` | `INTEGER` | - | Hayır | ana_strateji.id |
| `target_id` | `INTEGER` | - | Hayır | ana_strateji.id |
| `connection_type` | `VARCHAR(30)` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `source` | `AnaStrateji` | `MANYTOONE` | Hayır |
| `target` | `AnaStrateji` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `StrategyProcessMatrix` (Tablo: `strategy_process_matrix`)
*Strateji-Süreç Matrisi Modeli*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `sub_strategy_id` | `INTEGER` | - | Hayır | alt_strateji.id |
| `process_id` | `INTEGER` | - | Hayır | processes.id |
| `relationship_strength` | `INTEGER` | - | Evet | - |
| `relationship_score` | `INTEGER` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `sub_strategy` | `AltStrateji` | `MANYTOONE` | Hayır |
| `process` | `Process` | `MANYTOONE` | Hayır |

---

### 📁 `strategy_frameworks.py` İçindeki Modeller

#### 🏷️ Sınıf: `BlueOceanCanvas` (Tablo: `blue_ocean_canvases`)
*Bir sektör/pazar için Strategy Canvas (Value Curve) ana kaydı.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `industry` | `VARCHAR(120)` | - | Evet | - |
| `description` | `TEXT` | - | Evet | - |
| `competitor_names` | `TEXT` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `factors` | `BlueOceanFactor` | `ONETOMANY` | Evet |
| `errc_items` | `BlueOceanERRC` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `BlueOceanERRC` (Tablo: `blue_ocean_errc_items`)
*ERRC (Eliminate / Reduce / Raise / Create) öğesi.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `canvas_id` | `INTEGER` | - | Hayır | blue_ocean_canvases.id |
| `action` | `VARCHAR(20)` | - | Hayır | - |
| `text` | `TEXT` | - | Hayır | - |
| `rationale` | `TEXT` | - | Evet | - |
| `impact` | `VARCHAR(20)` | - | Evet | - |
| `order_index` | `INTEGER` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `canvas` | `BlueOceanCanvas` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `BlueOceanFactor` (Tablo: `blue_ocean_factors`)
*Rekabet faktörü (Fiyat, Kalite, Hız vb.) + kendi & rakip puanları (1-10).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `canvas_id` | `INTEGER` | - | Hayır | blue_ocean_canvases.id |
| `name` | `VARCHAR(150)` | - | Hayır | - |
| `order_index` | `INTEGER` | - | Hayır | - |
| `self_score` | `FLOAT` | - | Hayır | - |
| `competitor_scores` | `TEXT` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `canvas` | `BlueOceanCanvas` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `VRIOResource` (Tablo: `vrio_resources`)
*Kurumsal kaynak/yetenek + VRIO değerlendirmesi.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `name` | `VARCHAR(200)` | - | Hayır | - |
| `category` | `VARCHAR(80)` | - | Evet | - |
| `description` | `TEXT` | - | Evet | - |
| `is_valuable` | `BOOLEAN` | - | Hayır | - |
| `is_rare` | `BOOLEAN` | - | Hayır | - |
| `is_inimitable` | `BOOLEAN` | - | Hayır | - |
| `is_organized` | `BOOLEAN` | - | Hayır | - |
| `note` | `TEXT` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

### 📁 `swot.py` İçindeki Modeller

#### 🏷️ Sınıf: `PestelAnalysis` (Tablo: `pestel_analyses`)
*PESTEL Analizi. Her PlanYear / Tenant için bir kayıt.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `source_pestel_id` | `INTEGER` | - | Evet | pestel_analyses.id |
| `political` | `TEXT` | - | Evet | - |
| `economic` | `TEXT` | - | Evet | - |
| `social` | `TEXT` | - | Evet | - |
| `technological` | `TEXT` | - | Evet | - |
| `environmental` | `TEXT` | - | Evet | - |
| `legal` | `TEXT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `source_pestel` | `PestelAnalysis` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `PorterFiveForcesAnalysis` (Tablo: `porter_analyses`)
*Porter's Five Forces Analizi.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `source_porter_id` | `INTEGER` | - | Evet | porter_analyses.id |
| `rivalry_intensity` | `TEXT` | - | Evet | - |
| `supplier_power` | `TEXT` | - | Evet | - |
| `buyer_power` | `TEXT` | - | Evet | - |
| `new_entrant_threat` | `TEXT` | - | Evet | - |
| `substitute_threat` | `TEXT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `source_porter` | `PorterFiveForcesAnalysis` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `SwotAnalysis` (Tablo: `swot_analyses`)
*SWOT Analizi. Her PlanYear / Tenant kombinasyonu için bir kayıt.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `source_swot_id` | `INTEGER` | - | Evet | swot_analyses.id |
| `strengths` | `TEXT` | - | Evet | - |
| `weaknesses` | `TEXT` | - | Evet | - |
| `opportunities` | `TEXT` | - | Evet | - |
| `threats` | `TEXT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `source_swot` | `SwotAnalysis` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `TowsAnalysis` (Tablo: `tows_analyses`)
*TOWS Matrisi. Her PlanYear / Tenant için SWOT'tan türetilen stratejiler.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `source_tows_id` | `INTEGER` | - | Evet | tows_analyses.id |
| `so_strategies` | `TEXT` | - | Evet | - |
| `st_strategies` | `TEXT` | - | Evet | - |
| `wo_strategies` | `TEXT` | - | Evet | - |
| `wt_strategies` | `TEXT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `source_tows` | `TowsAnalysis` | `MANYTOONE` | Hayır |

---

### 📁 `system_setting.py` İçindeki Modeller

#### 🏷️ Sınıf: `SystemSetting` (Tablo: `system_settings`)
*Örn. maintenance_mode — tek satır key/value.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `key` | `VARCHAR(64)` | ✅ | Hayır | - |
| `value` | `TEXT` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

### 📁 `tenant_llm_config.py` İçindeki Modeller

#### 🏷️ Sınıf: `TenantLLMConfig` (Tablo: `tenant_llm_configs`)
*Tenant'a özel LLM yapılandırması (BYOK).*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `provider` | `VARCHAR(40)` | - | Hayır | - |
| `model` | `VARCHAR(120)` | - | Evet | - |
| `api_key_encrypted` | `TEXT` | - | Evet | - |
| `base_url` | `VARCHAR(300)` | - | Evet | - |
| `is_active` | `BOOLEAN` | - | Hayır | - |
| `pii_mask_enabled` | `BOOLEAN` | - | Hayır | - |
| `last_test_at` | `DATETIME` | - | Evet | - |
| `last_test_status` | `VARCHAR(40)` | - | Evet | - |
| `last_test_message` | `VARCHAR(500)` | - | Evet | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

### 📁 `tenant_year.py` İçindeki Modeller

#### 🏷️ Sınıf: `TenantYearIdentity` (Tablo: `tenant_year_identities`)
*Kurumun stratejik kimlik alanlarının (misyon, vizyon, değerler vb.)*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `purpose` | `TEXT` | - | Evet | - |
| `vision` | `TEXT` | - | Evet | - |
| `core_values` | `TEXT` | - | Evet | - |
| `code_of_ethics` | `TEXT` | - | Evet | - |
| `quality_policy` | `TEXT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |

---

### 📁 `tour.py` İçindeki Modeller

#### 🏷️ Sınıf: `UserTourProgress` (Tablo: `user_tour_progress`)
*Bir kullanıcı + tur_key için durum kaydı.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `tour_key` | `VARCHAR(64)` | - | Hayır | - |
| `status` | `VARCHAR(16)` | - | Hayır | - |
| `seen_count` | `INTEGER` | - | Hayır | - |
| `completed_at` | `DATETIME` | - | Evet | - |
| `dismissed_at` | `DATETIME` | - | Evet | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

---

### 📁 `user.py` İçindeki Modeller

#### 🏷️ Sınıf: `DashboardLayout` (Tablo: `dashboard_layout`)
*Kullanıcı bazlı dashboard düzeni*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | user.id |
| `layout_name` | `VARCHAR(100)` | - | Evet | - |
| `is_default` | `BOOLEAN` | - | Evet | - |
| `layout_data` | `TEXT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `user` | `LegacyUser` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `Deger` (Tablo: `deger`)
*Kurum Değerleri*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `baslik` | `VARCHAR(200)` | - | Hayır | - |
| `aciklama` | `TEXT` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `kurum` | `Kurum` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `EtikKural` (Tablo: `etik_kural`)
*Kurum Etik Kuralları*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `baslik` | `VARCHAR(200)` | - | Hayır | - |
| `aciklama` | `TEXT` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `kurum` | `Kurum` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `KalitePolitikasi` (Tablo: `kalite_politikasi`)
*Kurum Kalite Politikası*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `baslik` | `VARCHAR(200)` | - | Hayır | - |
| `aciklama` | `TEXT` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `kurum` | `Kurum` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `KullaniciYetki` (Tablo: `kullanici_yetki`)
*Matris tabanlı yetki atamaları*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | user.id |
| `yetki_kodu` | `VARCHAR(100)` | - | Hayır | - |
| `aktif` | `BOOLEAN` | - | Evet | - |
| `atayan_user_id` | `INTEGER` | - | Evet | user.id |
| `created_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `user` | `LegacyUser` | `MANYTOONE` | Hayır |
| `atayan` | `LegacyUser` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `Kurum` (Tablo: `kurum`)
*Kurum Modeli*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `kisa_ad` | `VARCHAR(100)` | - | Hayır | - |
| `ticari_unvan` | `VARCHAR(200)` | - | Hayır | - |
| `faaliyet_alani` | `VARCHAR(200)` | - | Evet | - |
| `adres` | `TEXT` | - | Evet | - |
| `il` | `VARCHAR(100)` | - | Evet | - |
| `ilce` | `VARCHAR(100)` | - | Evet | - |
| `email` | `VARCHAR(120)` | - | Evet | - |
| `web_adresi` | `VARCHAR(200)` | - | Evet | - |
| `telefon` | `VARCHAR(20)` | - | Evet | - |
| `calisan_sayisi` | `INTEGER` | - | Evet | - |
| `sektor` | `VARCHAR(100)` | - | Evet | - |
| `vergi_dairesi` | `VARCHAR(100)` | - | Evet | - |
| `vergi_numarasi` | `VARCHAR(20)` | - | Evet | - |
| `logo_url` | `VARCHAR(500)` | - | Evet | - |
| `amac` | `TEXT` | - | Evet | - |
| `vizyon` | `TEXT` | - | Evet | - |
| `stratejik_profil` | `TEXT` | - | Evet | - |
| `stratejik_durum` | `VARCHAR(50)` | - | Evet | - |
| `stratejik_son_guncelleme` | `DATETIME` | - | Evet | - |
| `show_guide_system` | `BOOLEAN` | - | Hayır | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `silindi` | `BOOLEAN` | - | Hayır | - |
| `deleted_at` | `DATETIME` | - | Evet | - |
| `deleted_by` | `INTEGER` | - | Evet | user.id |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |
| `users` | `LegacyUser` | `ONETOMANY` | Evet |
| `deleter` | `LegacyUser` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `LegacyNotification` (Tablo: `notification`)
*Sistem Bildirimleri*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | user.id |
| `tip` | `VARCHAR(50)` | - | Hayır | - |
| `baslik` | `VARCHAR(200)` | - | Hayır | - |
| `mesaj` | `TEXT` | - | Evet | - |
| `link` | `VARCHAR(500)` | - | Evet | - |
| `okundu` | `BOOLEAN` | - | Evet | - |
| `email_sent` | `BOOLEAN` | - | Evet | - |
| `surec_id` | `INTEGER` | - | Evet | - |
| `project_id` | `INTEGER` | - | Evet | - |
| `task_id` | `INTEGER` | - | Evet | - |
| `ilgili_user_id` | `INTEGER` | - | Evet | user.id |
| `created_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `user` | `LegacyUser` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `LegacyUser` (Tablo: `user`)
*Kullanıcı Modeli*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `username` | `VARCHAR(80)` | - | Hayır | - |
| `email` | `VARCHAR(120)` | - | Hayır | - |
| `password_hash` | `VARCHAR(120)` | - | Hayır | - |
| `first_name` | `VARCHAR(50)` | - | Evet | - |
| `last_name` | `VARCHAR(50)` | - | Evet | - |
| `phone` | `VARCHAR(20)` | - | Evet | - |
| `title` | `VARCHAR(100)` | - | Evet | - |
| `department` | `VARCHAR(100)` | - | Evet | - |
| `sistem_rol` | `VARCHAR(50)` | - | Hayır | - |
| `surec_rol` | `VARCHAR(50)` | - | Evet | - |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `profile_photo` | `VARCHAR(500)` | - | Evet | - |
| `theme_preferences` | `TEXT` | - | Evet | - |
| `layout_preference` | `VARCHAR(20)` | - | Evet | - |
| `guide_character_style` | `VARCHAR(50)` | - | Evet | - |
| `show_page_guides` | `BOOLEAN` | - | Hayır | - |
| `completed_walkthroughs` | `TEXT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `silindi` | `BOOLEAN` | - | Hayır | - |
| `deleted_at` | `DATETIME` | - | Evet | - |
| `deleted_by` | `INTEGER` | - | Evet | user.id |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `kurum` | `Kurum` | `MANYTOONE` | Hayır |
| `deleter` | `LegacyUser` | `MANYTOONE` | Hayır |
| `deleted_kurumlar` | `Kurum` | `ONETOMANY` | Evet |
| `ozel_yetkiler` | `OzelYetki` | `ONETOMANY` | Evet |
| `yetkiler` | `KullaniciYetki` | `ONETOMANY` | Evet |
| `dashboard_layouts` | `DashboardLayout` | `ONETOMANY` | Evet |
| `bildirimler` | `LegacyNotification` | `ONETOMANY` | Evet |
| `aktivite_loglari` | `UserActivityLog` | `ONETOMANY` | Evet |
| `notes` | `Note` | `ONETOMANY` | Evet |
| `feedbacks` | `Feedback` | `ONETOMANY` | Evet |
| `dashboard_settings_v3` | `UserDashboardSettings` | `ONETOMANY` | Hayır |
| `audit_logs` | `AuditLog` | `ONETOMANY` | Evet |

---

#### 🏷️ Sınıf: `Note` (Tablo: `note`)
*Karalama Defteri (Scratchpad) Modeli*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | user.id |
| `title` | `VARCHAR(200)` | - | Hayır | - |
| `content` | `TEXT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `user` | `LegacyUser` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `OzelYetki` (Tablo: `ozel_yetki`)
*Kullanıcıya özel yetkiler*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `kullanici_id` | `INTEGER` | - | Hayır | user.id |
| `yetki_kodu` | `VARCHAR(100)` | - | Hayır | - |
| `aktif` | `BOOLEAN` | - | Evet | - |
| `veren_kullanici_id` | `INTEGER` | - | Hayır | user.id |
| `created_at` | `DATETIME` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `kullanici` | `LegacyUser` | `MANYTOONE` | Hayır |
| `veren_kullanici` | `LegacyUser` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `UserActivityLog` (Tablo: `user_activity_log`)
*Kullanıcı Aktivite Logları*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | user.id |
| `tip` | `VARCHAR(50)` | - | Hayır | - |
| `baslik` | `VARCHAR(200)` | - | Hayır | - |
| `aciklama` | `TEXT` | - | Evet | - |
| `link` | `VARCHAR(500)` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |
| `surec_id` | `INTEGER` | - | Evet | - |
| `ilgili_user_id` | `INTEGER` | - | Evet | user.id |
| `bireysel_pg_id` | `INTEGER` | - | Evet | - |
| `surec_pg_id` | `INTEGER` | - | Evet | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `user` | `LegacyUser` | `MANYTOONE` | Hayır |

---

#### 🏷️ Sınıf: `YetkiMatrisi` (Tablo: `yetki_matrisi`)
*Rol bazlı yetki tanımlamaları*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `rol` | `VARCHAR(50)` | - | Hayır | - |
| `yetki_kodu` | `VARCHAR(100)` | - | Hayır | - |
| `aktif` | `BOOLEAN` | - | Evet | - |
| `aciklama` | `VARCHAR(200)` | - | Evet | - |
| `created_at` | `DATETIME` | - | Evet | - |

---

### 📁 `user_year_assignment.py` İçindeki Modeller

#### 🏷️ Sınıf: `UserYearAssignment` (Tablo: `user_year_assignments`)
*Açıklama belirtilmemiş.*

**Sütunlar:**

| Sütun Adı | Veri Tipi | PK | Nullable | Yabancı Anahtar (FK) |
| :--- | :--- | :---: | :---: | :--- |
| `id` | `INTEGER` | ✅ | Hayır | - |
| `user_id` | `INTEGER` | - | Hayır | users.id |
| `plan_year_id` | `INTEGER` | - | Hayır | plan_years.id |
| `tenant_id` | `INTEGER` | - | Hayır | tenants.id |
| `job_title` | `VARCHAR(150)` | - | Evet | - |
| `department` | `VARCHAR(150)` | - | Evet | - |
| `role_label` | `VARCHAR(80)` | - | Evet | - |
| `note` | `TEXT` | - | Evet | - |
| `created_at` | `DATETIME` | - | Hayır | - |
| `updated_at` | `DATETIME` | - | Hayır | - |

**İlişkiler (Relationships):**

| İlişki Adı | İlişkili Sınıf | İlişki Tipi | Liste (uselist) |
| :--- | :--- | :--- | :---: |
| `user` | `User` | `MANYTOONE` | Hayır |
| `plan_year` | `PlanYear` | `MANYTOONE` | Hayır |
| `tenant` | `Tenant` | `MANYTOONE` | Hayır |

---


✅ Sayfa tarayıcıda açıldı, konsol hatası taranmadı ve görsel olarak doğrulandı.
