# Tenant Veri Envanteri

> Bir tenant için Kokpitim DB'sine yazılan tüm bilgilerin tam dökümü.
> Kapsam: aktif tablolar (`app/models/` + `micro/` zinciri). Legacy `models/` dışarıda.
> Gruplama: modüle göre. Detay: tablo + her kolon + FK + index + unique.
> Üretildi: 2026-05-26 · Kaynak: `app/models/*.py`

---

## İçindekiler
1. [Kurum & Kullanıcı (Çekirdek)](#1-kurum--kullanıcı-çekirdek)
2. [Stratejik Planlama — Ağaç (Vizyon → PG)](#2-stratejik-planlama--ağaç-vizyon--pg)
3. [Plan Year (Yıllık Dönem Sistemi)](#3-plan-year-yıllık-dönem-sistemi)
4. [K-Vektör (Ağırlık Motoru)](#4-k-vektör-ağırlık-motoru)
5. [K-Radar (Olgunluk & Risk)](#5-k-radar-olgunluk--risk)
6. [Stratejik Analiz Çerçeveleri](#6-stratejik-analiz-çerçeveleri)
7. [Initiative (Çok Yıllık Girişim)](#7-initiative-çok-yıllık-girişim)
8. [BSC / OKR / ESG](#8-bsc--okr--esg)
9. [SP Projeleri (Plan Year Bazlı)](#9-sp-projeleri-plan-year-bazlı)
10. [Portföy Projeleri (Operasyonel)](#10-portföy-projeleri-operasyonel)
11. [Bildirim & İletişim](#11-bildirim--iletişim)
12. [Denetim & Log](#12-denetim--log)
13. [LLM / AI Kullanımı](#13-llm--ai-kullanımı)
14. [SaaS / Paket / Sistem](#14-saas--paket--sistem)
15. [Yardımcı (Tour, vb.)](#15-yardımcı-tour-vb)

---

## 1. Kurum & Kullanıcı (Çekirdek)

### `tenants` — Kurum
Tenant'ın tüm kimlik, lisans ve özellik bayrakları.

| Kolon | Tip | NN | Default | Index/Unique | FK | Açıklama |
|---|---|---|---|---|---|---|
| id | Integer | ✓ | PK | PK | | |
| name | String(255) | ✓ | | | | Kurum adı |
| short_name | String(64) | | | | | Kısa ad |
| is_active | Boolean | ✓ | True | | | Soft delete |
| package_id | Integer | | | | → subscription_packages.id | Abonelik paketi |
| created_at | DateTime | | now() | | | |
| activity_area | String(200) | | | | | Faaliyet alanı |
| sector | String(100) | | | | | Sektör |
| employee_count | Integer | | | | | Çalışan sayısı |
| contact_email | String(120) | | | | | Kurum e-posta |
| phone_number | String(20) | | | | | Telefon |
| website_url | String(200) | | | | | Web adresi |
| tax_office | String(100) | | | | | Vergi dairesi |
| tax_number | String(20) | | | | | Vergi numarası |
| max_user_count | Integer | | 5 | | | Maks kullanıcı |
| license_end_date | Date | | | | | Lisans bitiş |
| purpose | Text | | | | | **Amaç** (stratejik kimlik) |
| vision | Text | | | | | **Vizyon** |
| core_values | Text | | | | | Değerler |
| code_of_ethics | Text | | | | | Etik kurallar |
| quality_policy | Text | | | | | Kalite politikası |
| logo_path | String(500) | | | | | `instance/uploads/tenant_logos/` altı |
| logo_updated_at | DateTime | | | | | |
| k_vektor_enabled | Boolean | ✓ | False | | | K-Vektör modülü açık mı |
| k_radar_enabled | Boolean | ✓ | False | | | K-Radar modülü |
| plan_year_enabled | Boolean | ✓ | False | | | Yıllık plan dönemi |
| plan_year_start | Integer | | | | | Geçmiş yıl başlangıcı |
| tenant_type | String(20) | ✓ | "normal" | | | normal / dealer / holding |
| parent_tenant_id | Integer | | | idx | → tenants.id (SET NULL) | Üst kurum |
| sub_tenant_limit | Integer | | | | | Bayi/holding alt kurum tavanı |

### `roles` — Roller
| Kolon | Tip | NN | Unique | Açıklama |
|---|---|---|---|---|
| id | Integer | ✓ PK | | |
| name | String(64) | ✓ | ✓ | Admin, tenant_admin, executive_manager, yonetici, calisan, izleyici |
| description | String(255) | | | |

### `users` — Kullanıcı
| Kolon | Tip | NN | Default | Index | FK | Açıklama |
|---|---|---|---|---|---|---|
| id | Integer | ✓ PK | | | | |
| email | String(255) | ✓ | | unique | | |
| password_hash | String(255) | ✓ | | | | |
| first_name | String(64) | | | | | |
| last_name | String(64) | | | | | |
| is_active | Boolean | ✓ | True | | | |
| tenant_id | Integer | | | | → tenants.id | |
| role_id | Integer | | | | → roles.id | |
| created_at | DateTime | | now() | | | |
| phone_number | String(20) | | | | | |
| job_title | String(100) | | | | | Unvan |
| department | String(100) | | | | | Departman |
| profile_picture | String(500) | | | | | |
| theme_preferences | Text | | | | | JSON: tema/renk |
| layout_preference | String(20) | ✓ | "classic" | | | classic / sidebar |
| notification_preferences | Text | | | | | JSON |
| locale_preferences | Text | | | | | JSON: dil/timezone |
| show_page_guides | Boolean | ✓ | True | | | |
| guide_character_style | String(50) | ✓ | "professional" | | | |
| totp_secret | String(64) | | | | | 2FA secret (base32) |
| totp_enabled | Boolean | ✓ | False | | | |
| totp_backup_codes_json | Text | | | | | |

### `tickets` — Kule İletişim (destek talepleri)
| Kolon | Tip | NN | Index | FK |
|---|---|---|---|---|
| id PK | Integer | ✓ | | |
| user_id | Integer | ✓ | ✓ | → users.id |
| tenant_id | Integer | | ✓ | → tenants.id |
| page_url | String(500) | | | |
| subject | String(50) | ✓ | | |
| message | Text | ✓ | | |
| screenshot_path | String(500) | | | |
| status | String(50) | ✓ "Bekliyor" | | |
| admin_note | Text | | | |
| created_at / updated_at | DateTime | ✓ | | |

---

## 2. Stratejik Planlama — Ağaç (Vizyon → PG)

> Hiyerarşi: **Tenant.vision** → `strategies` (Ana) → `sub_strategies` (Alt) → `processes` (Süreç) → `process_kpis` (PG) → `kpi_data` (Ölçüm).
> Bağ: `process_sub_strategy_links` (M:N, katkı %), `process_kpis.sub_strategy_id` (1:1).

### `strategies` — Ana Strateji
| Kolon | Tip | NN | Default | Index | FK |
|---|---|---|---|---|---|
| id PK | Integer | ✓ | | | |
| tenant_id | Integer | ✓ | | ✓ | → tenants.id |
| code | String(20) | | | ✓ | örn. ST1 |
| title | String(200) | ✓ | | | |
| description | Text | | | | |
| is_active | Boolean | ✓ | True | ✓ | |
| created_at / updated_at | DateTime | ✓ | | | |
| plan_year_id | Integer | | | ✓ | → plan_years.id (CASCADE) — Full Clone |
| source_strategy_id | Integer | | | | → strategies.id (SET NULL) — klon kaynağı |

### `sub_strategies` — Alt Strateji
| Kolon | Tip | NN | Index | FK |
|---|---|---|---|---|
| id PK | Integer | ✓ | | |
| strategy_id | Integer | ✓ | ✓ | → strategies.id |
| code | String(20) | | ✓ | ST1.1 |
| title | String(200) | ✓ | | |
| description | Text | | | |
| is_active | Boolean | ✓ True | ✓ | |
| created_at / updated_at | DateTime | ✓ | | |
| plan_year_id | Integer | | ✓ | → plan_years.id (CASCADE) |
| source_sub_strategy_id | Integer | | | → sub_strategies.id (SET NULL) |

### `processes` — Süreç
| Kolon | Tip | NN | Default | Index | FK |
|---|---|---|---|---|---|
| id PK | Integer | ✓ | | | |
| tenant_id | Integer | ✓ | | ✓ | → tenants.id |
| parent_id | Integer | | | ✓ | → processes.id (SET NULL) hiyerarşi |
| code | String(20) | | | ✓ | SR1 |
| name | String(200) | ✓ | | ✓ | TR ad |
| english_name | String(200) | | | | |
| weight | Float | | | | 0-100 skor motoru |
| document_no | String(50) | | | | KYS |
| revision_no | String(20) | | | | |
| revision_date | Date | | | | |
| first_publish_date | Date | | | | |
| status | String(50) | | "Aktif" | | |
| progress | Integer | | 0 | | |
| start_boundary / end_boundary | Text | | | | Kapsam |
| start_date / end_date | Date | | | | |
| description | Text | | | | |
| plan_year_id | Integer | | | ✓ | → plan_years.id (CASCADE) |
| source_process_id | Integer | | | | → processes.id (SET NULL) |
| is_active | Boolean | ✓ True | | ✓ | |
| deleted_at | DateTime | | | | |
| deleted_by | Integer | | | | → users.id |
| created_at / updated_at | DateTime | | | | |

**M:N tabloları (assoc):**
- `process_members(process_id PK, user_id PK)` — üyeler
- `process_leaders(process_id PK, user_id PK)` — liderler
- `process_owners_table(process_id PK, user_id PK)` — sahipler

### `process_sub_strategy_links` — Süreç ↔ Alt Strateji
| Kolon | Tip | NN | PK | FK |
|---|---|---|---|---|
| process_id | Integer | ✓ | ✓ | → processes.id (CASCADE) |
| sub_strategy_id | Integer | ✓ | ✓ | → sub_strategies.id (CASCADE) |
| contribution_pct | Float | | | 0-100 katkı yüzdesi |

### `process_kpis` — Performans Göstergesi (PG)
| Kolon | Tip | NN | Default | Index | FK |
|---|---|---|---|---|---|
| id PK | Integer | ✓ | | | |
| process_id | Integer | ✓ | | ✓ | → processes.id (CASCADE) |
| name | String(200) | ✓ | | | |
| description | Text | | | | |
| code | String(50) | | | | PG-01 |
| target_value | String(100) | | | | |
| unit | String(50) | | | | |
| period | String(50) | | | | Aylık/Çeyreklik/Yıllık |
| data_source | String(200) | | | | Veri kaynağı |
| target_setting_method | String(200) | | | | Hedef belirleme yöntemi |
| data_collection_method | String(50) | | "Ortalama" | | Toplama/Ortalama/Son Değer |
| calculation_method | String(20) | | "AVG" | | |
| gosterge_turu | String(50) | | | | İyileştirme/Koruma/Bilgi |
| target_method | String(10) | | | | RG/HKY/HK/SH/DH/SGH |
| basari_puani_araliklari | Text | | | | JSON aralık dizisi |
| onceki_yil_ortalamasi | Float | | | | |
| weight | Float | | 0 | | |
| is_important | Boolean | | False | | |
| direction | String(20) | | "Increasing" | | Inc/Decreasing |
| calculated_score | Float | | | | |
| is_active | Boolean | ✓ True | | ✓ | |
| sub_strategy_id | Integer | | | ✓ | → sub_strategies.id (SET NULL) |
| plan_year_id | Integer | | | ✓ | → plan_years.id (CASCADE) |
| source_kpi_id | Integer | | | | → process_kpis.id (SET NULL) |
| start_date / end_date | Date | | | | |
| created_at / updated_at | DateTime | | | | |

### `kpi_data` — PG Veri (Ölçüm)
| Kolon | Tip | NN | Index | FK |
|---|---|---|---|---|
| id PK | Integer | ✓ | | |
| process_kpi_id | Integer | ✓ | ✓ | → process_kpis.id (CASCADE) |
| year | Integer | ✓ | ✓ | |
| data_date | Date | ✓ | ✓ | |
| period_type | String(20) | | | yillik/ceyrek/aylik |
| period_no | Integer | | | |
| period_month | Integer | | | |
| target_value | String(100) | | | |
| actual_value | String(100) | ✓ | | |
| status | String(50) | | | |
| status_percentage | Float | | | |
| description | Text | | | |
| user_id | Integer | ✓ | | → users.id (giren) |
| created_at / updated_at | DateTime | | | |
| is_active | Boolean | ✓ True | ✓ | Soft delete |
| deleted_at | DateTime | | ✓ | |
| deleted_by_id | Integer | | ✓ | → users.id (SET NULL) |

Composite index: `idx_kpi_data_lookup (process_kpi_id, year, data_date)`

### `kpi_data_audits` — PG Veri değişiklik geçmişi
| Kolon | Tip | NN | Index | FK |
|---|---|---|---|---|
| id PK | Integer | ✓ | | |
| kpi_data_id | Integer | ✓ | ✓ | → kpi_data.id (CASCADE) |
| action_type | String(20) | ✓ | | CREATE/UPDATE/DELETE |
| old_value | Text | | | |
| new_value | Text | | | |
| action_detail | Text | | | |
| user_id | Integer | ✓ | | → users.id |
| created_at | DateTime | | | |

### `process_activities` — Süreç Faaliyeti
| Kolon | Tip | NN | Default | Index | FK |
|---|---|---|---|---|---|
| id PK | Integer | ✓ | | | |
| process_id | Integer | ✓ | | ✓ | → processes.id (CASCADE) |
| process_kpi_id | Integer | | | ✓ | → process_kpis.id (SET NULL) |
| name | String(200) | ✓ | | | |
| description | Text | | | | |
| start_date / end_date | Date | | | | Legacy |
| start_at / end_at | DateTime | | | ✓/✓ | V2 zaman planı |
| status | String(50) | | "Planlandı" | | |
| progress | Integer | | 0 | | |
| notify_email | Boolean | ✓ False | | | |
| auto_complete_enabled | Boolean | ✓ True | | | |
| auto_pgv_created | Boolean | ✓ False | ✓ | | |
| auto_pgv_kpi_data_id | Integer | | | ✓ | → kpi_data.id (SET NULL) |
| completed_at / cancelled_at / postponed_at | DateTime | | | | |
| plan_year_id | Integer | | | ✓ | → plan_years.id (CASCADE) |
| source_activity_id | Integer | | | | → process_activities.id (SET NULL) |
| is_active | Boolean | ✓ True | | ✓ | |
| created_at / updated_at | DateTime | | | | |

### `process_activity_assignees` — Çoklu atama
| Kolon | Tip | NN | PK | FK |
|---|---|---|---|---|
| activity_id | Integer | ✓ | ✓ | → process_activities.id (CASCADE) |
| user_id | Integer | ✓ | ✓ | → users.id (CASCADE) |
| order_no | Integer | ✓ 1 | | |
| assigned_by | Integer | | | → users.id (SET NULL) |
| assigned_at / created_at | DateTime | ✓ | | |

### `process_activity_reminders` — Hatırlatmalar
| Kolon | Tip | NN | Index | FK |
|---|---|---|---|---|
| id PK | Integer | ✓ | | |
| activity_id | Integer | ✓ | ✓ | → process_activities.id (CASCADE) |
| minutes_before | Integer | ✓ | | |
| remind_at | DateTime | ✓ | ✓ | |
| channel_email | Boolean | ✓ False | | |
| sent_at | DateTime | | ✓ | |
| created_at | DateTime | ✓ | | |

Unique: `(activity_id, minutes_before)`

### `activity_tracks` — Aylık Faaliyet Takip (checkbox)
| Kolon | Tip | NN | Index | FK |
|---|---|---|---|---|
| id PK | Integer | ✓ | | |
| activity_id | Integer | ✓ | ✓ | → process_activities.id (CASCADE) |
| year | Integer | ✓ | | |
| month | Integer | ✓ | | 1-12 |
| completed | Boolean | ✓ False | | |
| user_id | Integer | | | → users.id |
| created_at / updated_at | DateTime | | | |

Unique: `(activity_id, year, month)`

### Bireysel Performans

#### `individual_performance_indicators` — Bireysel PG
| Kolon | Tip | NN | Index | FK |
|---|---|---|---|---|
| id PK | Integer | ✓ | | |
| user_id | Integer | ✓ | ✓ | → users.id (CASCADE) |
| name | String(200) | ✓ | ✓ | |
| description | Text | | | |
| code | String(50) | | | |
| target_value / actual_value | String(100) | | | |
| unit | String(50) | | | |
| period | String(50) | | | |
| weight | Float | | | 0 |
| is_important | Boolean | | False | |
| start_date / end_date | Date | | | |
| status | String(50) | | "Devam Ediyor" | |
| source | String(50) | | "Bireysel" | |
| source_process_id | Integer | | ✓ | → processes.id (SET NULL) |
| source_process_kpi_id | Integer | | ✓ | → process_kpis.id (SET NULL) |
| direction | String(20) | | "Increasing" | |
| basari_puani_araliklari | Text | | | JSON |
| plan_year_id | Integer | | ✓ | → plan_years.id (CASCADE) |
| source_individual_kpi_id | Integer | | | → individual_performance_indicators.id |
| is_active | Boolean | ✓ True | ✓ | |
| created_at / updated_at | DateTime | | | |

Index: `idx_indiv_pg_user_source (user_id, source)`

#### `individual_activities` — Bireysel Faaliyet
Benzer şema: id, user_id, name, description, start/end_date, status, progress, source, source_process_id, source_process_activity_id, is_active, created/updated.

#### `individual_kpi_data` — Bireysel Ölçüm
| Kolon | Tip | NN | FK |
|---|---|---|---|
| id PK | Integer | ✓ | |
| individual_pg_id | Integer | ✓ | → individual_performance_indicators.id (CASCADE) |
| year / data_date / period_type / period_no / period_month | | | |
| target_value / actual_value / status / status_percentage / description | | | |
| user_id | Integer | ✓ | → users.id |

Index: `(individual_pg_id, year, data_date)`, `(user_id, year)`

#### `individual_kpi_data_audits` — Audit log
Aynı pattern: id, individual_kpi_data_id (CASCADE), action_type, old/new_value, action_detail, user_id, created_at.

#### `individual_activity_tracks` — Aylık takip
id, individual_activity_id (CASCADE), user_id, year, month, completed, note, completed_date, created/updated.
Unique: `(individual_activity_id, year, month)`

#### `favorite_kpis` — Favori PG
| Kolon | Tip | NN | FK |
|---|---|---|---|
| id PK | Integer | ✓ | |
| user_id | Integer | ✓ | → users.id (CASCADE) |
| process_kpi_id | Integer | ✓ | → process_kpis.id (CASCADE) |
| sort_order | Integer | 0 | |
| is_active | Boolean | ✓ True | |
| created_at | DateTime | | |

Unique: `(user_id, process_kpi_id)`

---

## 3. Plan Year (Yıllık Dönem Sistemi)

> Strateji ağacı tek "şu an" görüntüsü; yıla göre dahiliyet/ağırlık/hedef değişikliği bu tablolarla overlay yapılır.
> **Full Clone** sistemi: ağaç elemanlarındaki `plan_year_id` + `source_*_id` (klon kaynağı). Yıllar bağımsız ağaçlar şeklinde de saklanabilir.

### `plan_years` — Plan Yılı
| Kolon | Tip | NN | Default | Index | FK |
|---|---|---|---|---|---|
| id PK | Integer | ✓ | | | |
| tenant_id | Integer | ✓ | | ✓ | → tenants.id (CASCADE) |
| year | Integer | ✓ | | ✓ | |
| name | String(200) | | | | "2025 Stratejik Planı" |
| status | String(20) | ✓ | "active" | | draft/active/closed/archived |
| template_source_id | Integer | | | | → plan_years.id (SET NULL) |
| created_at | DateTime | ✓ now() | | | |
| closed_at | DateTime | | | | |
| scenario_of_id | Integer | | | ✓ | → plan_years.id (CASCADE) — Sprint 56 senaryo dalı |
| scenario_label | String(80) | | | | baseline/optimistic/pessimistic |

Unique: `(tenant_id, year)` · Index: `(tenant_id, status)`, `(scenario_of_id)`

### `kpi_year_configs` — Yıllık PG Override
| Kolon | Tip | NN | FK |
|---|---|---|---|
| id PK | Integer | ✓ | |
| plan_year_id | Integer | ✓ | → plan_years.id (CASCADE) |
| process_kpi_id | Integer | ✓ | → process_kpis.id (CASCADE) |
| target_value / unit / period / direction / target_method / calculation_method / basari_puani_araliklari / onceki_yil_ortalamasi | | | |
| weight | Float | | |
| is_included | Boolean | ✓ True | |
| created_at / updated_at | DateTime | | |

Unique: `(plan_year_id, process_kpi_id)`

### `strategy_year_configs` — Yıllık Ana Strateji Override
plan_year_id (CASCADE), strategy_id (CASCADE), title/code/description override, is_included, weight, timestamps. Unique: `(plan_year_id, strategy_id)`

### `sub_strategy_year_configs` — Yıllık Alt Strateji Override
plan_year_id, sub_strategy_id, title/code/description, is_included, timestamps. Unique: `(plan_year_id, sub_strategy_id)`

### `process_year_configs` — Yıllık Süreç Override
plan_year_id, process_id, name/weight override, is_included, timestamps. Unique: `(plan_year_id, process_id)`

### `individual_kpi_year_configs` — Yıllık Bireysel PG Override
plan_year_id, individual_performance_id (CASCADE), target_value/unit/period/direction/target_method/calculation_method/basari_puani_araliklari/weight/is_included, timestamps. Unique: `(plan_year_id, individual_performance_id)`

### `tenant_year_identities` — Yıllık Misyon/Vizyon
| Kolon | Tip | NN | Unique | FK |
|---|---|---|---|---|
| id PK | Integer | ✓ | | |
| plan_year_id | Integer | ✓ | ✓ | → plan_years.id (CASCADE) |
| tenant_id | Integer | ✓ | | → tenants.id (CASCADE) |
| purpose / vision / core_values / code_of_ethics / quality_policy | Text | | | |

---

## 4. K-Vektör (Ağırlık Motoru)

### `k_vektor_strategy_weights` — Ana strateji ham ağırlık
id, tenant_id (CASCADE), strategy_id (CASCADE), weight_raw. Unique: `(tenant_id, strategy_id)`

### `k_vektor_sub_strategy_weights` — Alt strateji ham ağırlık
id, tenant_id, sub_strategy_id, weight_raw. Unique: `(tenant_id, sub_strategy_id)`

### `k_vektor_config_snapshots` — Yapılandırma anlık görüntüsü
id, tenant_id (CASCADE), user_id (SET NULL), snapshot_type, payload_json (Text), created_at.

---

## 5. K-Radar (Olgunluk & Risk)

### `process_maturity` — Süreç olgunluk
id, tenant_id, process_id, maturity_level (Int), dimension, assessed_by (→ users), assessed_at, is_active, timestamps.

### `bottleneck_log` — Darboğaz logu
id, tenant_id, process_id, kpi_id (→ process_kpis), severity, note, triggered_at, resolved_at, is_active, timestamps.

### `value_chain_items` — Değer zinciri öğeleri
id, tenant_id, category (primary/support), linked_process_id, muda_type, title, note, is_active.

### `evm_snapshots` — Earned Value
id, tenant_id, project_id (→ project), snapshot_date, pv, ev, ac, spi, cpi, is_active.

### `risk_heatmap_items` — Risk haritası
id, tenant_id, plan_year_id (SET NULL), title, probability, impact, rpn, owner_id (→ users), status, source_type, is_active.

### `stakeholder_maps` — Paydaş haritası
id, tenant_id, plan_year_id, name, role, influence, interest, strategy, is_active.

### `stakeholder_surveys` — Paydaş anketleri
id, tenant_id, stakeholder_type, period, score, comment, source, is_active.

### `a3_reports` — A3 raporları
id, tenant_id, source_type, source_id, problem (Text), root_cause_json, countermeasures (Text), is_active.

### `competitor_analyses` — Rakip analizleri
id, tenant_id, plan_year_id, competitor_name, dimension, our_score, their_score, is_active.

### `k_radar_recommendation_actions` — Öneri aksiyonları
id, tenant_id, user_id, recommendation_key, recommendation_text, state (pending/approved/rejected), timestamps.
Unique: `(tenant_id, user_id, recommendation_key)`

---

## 6. Stratejik Analiz Çerçeveleri

### `swot_analyses` — SWOT
id, plan_year_id (CASCADE), tenant_id (CASCADE), source_swot_id, strengths/weaknesses/opportunities/threats (Text JSON array), timestamps.
Unique: `(plan_year_id, tenant_id)`

### `tows_analyses` — TOWS
Aynı yapı; so/st/wo/wt_strategies (Text JSON). Unique: `(plan_year_id, tenant_id)`

### `pestel_analyses` — PESTEL
political / economic / social / technological / environmental / legal (her biri Text JSON). Unique: `(plan_year_id, tenant_id)`

### `porter_analyses` — Porter 5 Forces
rivalry_intensity / supplier_power / buyer_power / new_entrant_threat / substitute_threat (Text JSON: score + items). Unique: `(plan_year_id, tenant_id)`

### `blue_ocean_canvases` — Blue Ocean ana kanvas
id, tenant_id (CASCADE), name, industry, description, competitor_names (CSV), is_active, timestamps.

### `blue_ocean_factors` — Rekabet faktörleri (1-10 puan)
id, canvas_id (CASCADE), name, order_index, self_score (Float), competitor_scores (Text JSON).

### `blue_ocean_errc_items` — ERRC öğeleri
id, canvas_id (CASCADE), action (eliminate/reduce/raise/create), text, rationale, impact, order_index.

### `vrio_resources` — VRIO kaynak
id, tenant_id (CASCADE), name, category, description, is_valuable / is_rare / is_inimitable / is_organized (Bool), note, is_active, timestamps.

---

## 7. Initiative (Çok Yıllık Girişim)

### `initiatives`
| Kolon | Tip | NN | Default | Index | FK |
|---|---|---|---|---|---|
| id PK | Integer | ✓ | | | |
| tenant_id | Integer | ✓ | | ✓ | → tenants.id (CASCADE) |
| code | String(40) | | | | |
| name | String(300) | ✓ | | | |
| description | Text | | | | |
| strategy_id | Integer | | | ✓ | → strategies.id (SET NULL) |
| sub_strategy_id | Integer | | | | → sub_strategies.id (SET NULL) |
| start_year / end_year | Integer | ✓ | | | Çok yıllık aralık |
| start_date / end_date | Date | | | | |
| status | String(30) | ✓ | "planned" | | planned/in_progress/on_hold/completed/cancelled |
| priority | String(20) | ✓ | "medium" | | critical/high/medium/low |
| budget_total / budget_spent | Numeric(18,2) | | 0 | | |
| progress_pct | Float | ✓ 0.0 | | | |
| owner_user_id | Integer | | | | → users.id (SET NULL) |
| is_active | Boolean | ✓ True | | | |
| created_at / updated_at | DateTime | ✓ | | | |

### `initiative_milestones`
id, initiative_id (CASCADE), name, target_date, completed_date, status (pending/in_progress/done/missed), note, order_index, created_at.

---

## 8. BSC / OKR / ESG

### `bsc_kpi_perspectives` — BSC Perspektif ataması
id, tenant_id (CASCADE), plan_year_id (CASCADE), process_kpi_id (CASCADE), perspective (finansal/musteri/ic_surec/ogrenme), timestamps.
Unique: `(plan_year_id, process_kpi_id)` · Index: `(tenant_id, plan_year_id, perspective)`

### `okr_objectives`
id, tenant_id (CASCADE), plan_year_id (CASCADE), title, description, quarter (1-4 veya null), owner, order_no, linked_strategy_id (SET NULL), linked_sub_strategy_id (SET NULL), is_active, timestamps.

### `okr_key_results`
id, objective_id (CASCADE), title, metric, start_value/target_value/current_value (Float), order_no, linked_process_kpi_id (→ process_kpis SET NULL), is_active, timestamps.

### `esg_metrics`
id, tenant_id (CASCADE), code, name, description, category (E/S/G), scope (scope1/2/3), unit, sdg_codes (CSV), target_value, baseline_year, baseline_value, is_active, timestamps.

### `esg_metric_values`
id, metric_id (CASCADE), year, period_type, period_no, value, source, notes, user_id (SET NULL), created_at.

---

## 9. SP Projeleri (Plan Year Bazlı)

### `plan_projects`
id, plan_year_id (CASCADE), tenant_id (CASCADE), source_project_id (SET NULL), name, description, status ("Planlandı"), progress (Int), start_date/end_date, is_active, timestamps.

### `plan_project_tasks`
id, project_id (→ plan_projects CASCADE), plan_year_id (CASCADE), assignee_id (→ users SET NULL), name, description, status, start/end_date, is_active, progress_pct (Float), planned_budget/actual_cost (Numeric 18,2 — EVM), depends_on_task_id (→ plan_project_tasks SET NULL), timestamps.

### `plan_project_activities`
id, project_id (CASCADE), plan_year_id (CASCADE), name, description, status, is_active, timestamps.

### `replan_triggers` — Otomatik yeniden planlama tetikleyici
id, tenant_id (CASCADE), name, description, trigger_type (kpi_below_target/risk_score/...), target_kpi_id (CASCADE), threshold_value/threshold_operator/consecutive_periods, action (notify/suggest_pivot/...), severity, is_active, last_fired_at, fire_count, timestamps.

### `replan_trigger_events`
id, trigger_id (CASCADE), tenant_id, fired_at, payload (Text JSON), action_taken, acknowledged_at, acknowledged_by_user_id (SET NULL).

---

## 10. Portföy Projeleri (Operasyonel)

> Bu blok `models/project.py` legacy ile bridge edilmiştir (`Kurum` viewonly). Aktif yüzey: micro `/proje`.

### `project`
| Kolon | Tip | NN | Default | Index | FK |
|---|---|---|---|---|---|
| id PK | | ✓ | | | |
| tenant_id | Integer | ✓ | | ✓ | → tenants.id |
| name | String(200) | ✓ | | ✓ | |
| description | Text | | | | |
| manager_id | Integer | ✓ | | ✓ | → users.id |
| start_date / end_date | Date | | | ✓ | |
| priority | String(50) | | "Orta" | | |
| is_archived | Boolean | | False | ✓ | |
| is_active | Boolean | ✓ True | | ✓ | Soft delete |
| deleted_at / deleted_by | DateTime / Int | | | | → users.id |
| health_score | Integer | | 100 | | V67 |
| health_status | String(50) | | "İyi" | | |
| notification_settings | Text | | | | JSON |
| created_at / updated_at | DateTime | | | | |

**Assoc:** `project_members`, `project_observers`, `project_leaders`, `project_related_processes (project_id, surec_id→processes.id)`

### `task`
id, project_id, title, description, assignee_id, reporter_id, external_assignee_name, parent_id, estimated_time/actual_time, progress, completed_at, is_measurable, planned_output_value, related_indicator_id, process_kpi_id (SET NULL), status, priority, is_archived, due_date, start_date, reminder_date, created_at.
Assoc: `task_predecessors(task_id, predecessor_id)`

### `task_impact`, `task_comment`, `task_mention`, `task_subtask`, `task_activity`, `task_dependency` (project_id, predecessor_id, successor_id, dependency_type FS/SS/FF/SF, lag_days), `task_baseline` (planned_start/end/effort), `task_sprint` (task↔sprint)
### `project_file` (filename, file_path, file_type, uploader_id)
### `project_risk` (title, description, probability/impact Low/Med/High, status Open/Mitigated/Closed)
### `time_entry` (task_id, user_id, duration_minutes, description, date)
### `integration_hook` (project_id, provider slack/teams/outlook, url, is_active)
### `rule_definition` (trigger, condition_json, actions_json) · `sla` (target_hours, breach_policy)
### `recurring_task` (cron_expr, template_task_id, next_run_at) · `working_day` (date, is_working)
### `capacity_plan` (project_id, user_id, weekly_hours, start/end_date)
### `raid_item` — Risk/Assumption/Issue/Dependency: item_type, title, description, owner_id, status, probability/impact (1-5), mitigation_plan, assumption_validation_date/validated/notes, issue_urgency/affected_work, dependency_task_id/type, created_at
### `tag`, `project_template`, `task_template`, `sprint` (project_id, name, start/end_date, status)

---

## 11. Bildirim & İletişim

### `notifications` — Sistem bildirim (legacy adı; aktif)
id, user_id, tenant_id, notification_type (pg_performance_deviation, task_assigned, ...), title, message, link, is_read, process_id, related_user_id, created_at.

### `notifications_ext` — Real-Time bildirim
id, user_id, type, title, message, priority (low/medium/high/urgent), action_url, extra_data (JSON), is_read, read_at, created_at.
Indexler: `(user_id, is_read, created_at)`, `(type, created_at)`, `(priority, is_read)`

### `notification_preferences`
id, user_id (unique), 14 adet Boolean: email_*, inapp_*, push_*, daily_digest, weekly_digest, updated_at.

### `push_subscriptions`
id, user_id, endpoint (Text), p256dh, auth (Web Push keys), is_active, created/updated.
Index: `(user_id, is_active)`, `(endpoint)`

### `tenant_email_configs` — Kurum SMTP
id, tenant_id (unique), use_custom_smtp, smtp_host/port/use_tls/use_ssl/username/password, sender_name/email, notify_on_process_assign/kpi_change/activity_add/task_assign, updated_by, timestamps.

---

## 12. Denetim & Log

### `audit_logs`
id, user_id, username, tenant_id, action (CREATE/UPDATE/DELETE/LOGIN/LOGOUT), resource_type, resource_id, description, old_values/new_values (JSON), ip_address, user_agent, request_method, request_path, created_at.
Indexler: `(user_id, created_at)`, `(tenant_id, created_at)`, `(action, created_at)`, `(resource_type, resource_id)`

### `kpi_data_audits` ve `individual_kpi_data_audits` — Veri-spesifik audit (yukarıda)
### `k_vektor_config_snapshots` — Ağırlık değişikliği audit (yukarıda)

---

## 13. LLM / AI Kullanımı

### `llm_usage_logs`
id (BigInt), tenant_id (CASCADE), user_id (SET NULL), endpoint (ai_pivot/ai_coach/ai_summary/ai_early_warning), provider (gemini/openai/...), model, prompt_tokens, output_tokens, total_tokens, cost_usd (Numeric 10,6), status (ok/error/rate_limited/quota_exceeded), error_msg, duration_ms, created_at.

### `llm_quota_overrides`
id, tenant_id (unique CASCADE), daily_call_limit, monthly_call_limit, monthly_cost_limit_usd (Numeric 10,2), is_paused, note, updated_at.

### `tenant_llm_configs` — BYOK
id, tenant_id (unique CASCADE), provider, model, api_key_encrypted (Fernet, SECRET_KEY türevli), base_url, is_active, pii_mask_enabled, last_test_at/status/message, timestamps.

---

## 14. SaaS / Paket / Sistem

### `subscription_packages` — Paket
id, name, code (unique), description, is_active. M:N → `system_modules` via `package_modules(package_id, module_id)`

### `system_modules` — Sistem modülü
id, name, code (unique), description, is_active. 1:N → `module_component_slugs(module_id, component_slug)`

### `system_components` — Sistem bileşeni
id, name, code (unique), description, is_active.

### `route_registry` — Dinamik rota kaydı
id, endpoint (unique), url_rule, methods, component_slug.

### `system_settings` — Global ayar
key (String PK), value (Text), updated_at. Örn: maintenance_mode.

---

## 15. Yardımcı (Tour, vb.)

### `user_tour_progress` — Kule turu durumu
id, user_id (CASCADE), tour_key, status (pending/completed/dismissed), seen_count, completed_at, dismissed_at, updated_at.
Unique: `(user_id, tour_key)`

---

## 📊 Sayıca Özet (modül başına tablo)

| Modül | Tablo sayısı |
|---|---|
| 1. Kurum & Kullanıcı | 4 |
| 2. SP Ağaç | 14 |
| 3. Plan Year | 7 |
| 4. K-Vektör | 3 |
| 5. K-Radar | 10 |
| 6. Stratejik Analiz | 8 |
| 7. Initiative | 2 |
| 8. BSC/OKR/ESG | 5 |
| 9. SP Projeleri | 5 |
| 10. Portföy | ~25 |
| 11. Bildirim | 5 |
| 12. Audit | 1 (+ 3 spesifik) |
| 13. LLM/AI | 3 |
| 14. SaaS | 5 |
| 15. Yardımcı | 1 |
| **Toplam** | **~96 tablo** |

---

## 🔑 Tenant-bağlılık deseni

- **Doğrudan `tenant_id` taşıyan tablolar (28)**: Tenant silinince CASCADE/zincirle gider.
- **Dolaylı (FK üzerinden)**: `kpi_data` → `process_kpis` → `processes.tenant_id`; `individual_kpi_data` → `individual_performance_indicators` → `users.tenant_id`.
- **Şifreli alanlar**: `tenant_llm_configs.api_key_encrypted` (Fernet, `SECRET_KEY` türevli).
- **JSON alanları**: Strateji analizleri (SWOT/TOWS/PESTEL/Porter) `Text` olarak JSON saklar — DB'den sorgulanmaz, app katmanında parse edilir.

## 🌐 Plan Year ile etkileşim

Plan Year overlay sistemi 5 ana ağaç elemanı için override sağlar:
1. Strateji → `strategy_year_configs`
2. Alt Strateji → `sub_strategy_year_configs`
3. Süreç → `process_year_configs`
4. PG → `kpi_year_configs`
5. Bireysel PG → `individual_kpi_year_configs`

Ek olarak **Full Clone** modu: ağaç elemanlarının `plan_year_id` + `source_*_id` kolonları sayesinde her yıl için ayrı ağaç versiyonu fiziksel saklanabilir (klon zinciri).
