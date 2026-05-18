# D6 — SİNAPS VERİ MODELİ TASLAĞI v1.0
> 30+ ana tablo · RLS policy örnekleri · tenant_path · indeks stratejisi
> Tarih: 2026-05-16
> Durum: TASLAK — onay bekliyor
> Bağımlılık: D1–D5

---

## 0. Genel Kurallar

### 0.1 Her Tabloda Zorunlu Kolonlar
```sql
id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
tenant_path   ltree NOT NULL,
created_at    timestamptz NOT NULL DEFAULT now(),
updated_at    timestamptz NOT NULL DEFAULT now(),
created_by    uuid NOT NULL REFERENCES users(id),
updated_by    uuid NOT NULL REFERENCES users(id),
deleted_at    timestamptz NULL,
version       integer NOT NULL DEFAULT 1
```

### 0.2 RLS Politikası Şablonu (her tabloya)
```sql
ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;

CREATE POLICY tenant_isolation_select ON {table}
  FOR SELECT USING (
    tenant_path <@ current_setting('app.tenant_path')::ltree
    AND deleted_at IS NULL
  );

CREATE POLICY tenant_isolation_modify ON {table}
  FOR ALL USING (
    tenant_path <@ current_setting('app.tenant_path')::ltree
  )
  WITH CHECK (
    tenant_path <@ current_setting('app.tenant_path')::ltree
  );
```

### 0.3 İndeks Standartı
```sql
CREATE INDEX idx_{t}_tenant_path ON {table} USING GIST (tenant_path);
CREATE INDEX idx_{t}_active ON {table} (id) WHERE deleted_at IS NULL;
```

### 0.4 Şema Bölünmesi
- `core.*`         → CORE bağlamı
- `strategy.*`     → STRATEGY
- `execution.*`    → EXECUTION
- `process.*`      → PROCESS
- `risk.*`         → RISK
- `esg.*`          → ESG
- `audit.*`        → AuditEvent partitioned
- `outbox.*`       → Outbox pattern (ADR-17)

---

## 1. CORE Şeması

### 1.1 `core.organizations`
```sql
id              uuid PK
name            text NOT NULL
slug            text NOT NULL UNIQUE
tenant_path     ltree NOT NULL  -- kök: 'tomofil'
brand           text CHECK (brand IN ('kokpitim','sinaps'))
tier            text CHECK (tier IN ('starter','pro','enterprise','enterprise_plus'))
billing_email   text
+ ortak kolonlar
```

### 1.2 `core.tenants`
```sql
id                  uuid PK
organization_id     uuid FK → core.organizations
parent_tenant_id    uuid FK → core.tenants NULL
tenant_path         ltree NOT NULL UNIQUE  -- 'tomofil.eu.berlin'
name                text NOT NULL
slug                text NOT NULL
locale_default      text NOT NULL DEFAULT 'tr'
timezone            text NOT NULL DEFAULT 'Europe/Istanbul'
package_id          uuid FK → core.packages
enabled_modules     text[] NOT NULL DEFAULT '{}'
status              text CHECK (status IN ('active','suspended','provisioning'))
+ ortak
UNIQUE (organization_id, slug)
```

### 1.3 `core.workspaces`
```sql
id           uuid PK
tenant_id    uuid FK → core.tenants
tenant_path  ltree NOT NULL
name         text
slug         text
+ ortak
```

### 1.4 `core.users`
```sql
id              uuid PK
email           citext UNIQUE NOT NULL
keycloak_sub    text UNIQUE NOT NULL
display_name    text
locale          text DEFAULT 'tr'
default_tenant_id uuid FK → core.tenants
status          text CHECK (status IN ('active','disabled','invited'))
+ ortak (tenant_path = kullanıcının default tenant path'i; cross-tenant erişim memberships üzerinden)
```
> Not: `users` global; RLS yerine app katmanı kullanıcının kendi kaydını + memberships'teki user_id'leri filtreler.

### 1.5 `core.memberships`
```sql
id            uuid PK
user_id       uuid FK → core.users
tenant_path   ltree NOT NULL  -- bu path ve alt-path'lerde erişim
role_set      text[] NOT NULL  -- ['org_admin','strategy_editor',...]
status        text DEFAULT 'active'
+ ortak
UNIQUE (user_id, tenant_path)
```

### 1.6 `core.packages`
```sql
id            uuid PK
code          text UNIQUE  -- 'starter','pro','enterprise','enterprise_plus'
name          text
module_codes  text[] NOT NULL
limits        jsonb  -- {max_users:50, max_kpis:200, ...}
```

### 1.7 `core.documents`
```sql
id            uuid PK
tenant_path   ltree
workspace_id  uuid FK NULL
owner_user_id uuid FK → core.users
filename      text
mime_type     text
size_bytes    bigint
s3_key        text NOT NULL
s3_bucket     text NOT NULL
checksum_sha256 text
version       integer
+ ortak
```

### 1.8 `core.notifications`
```sql
id              uuid PK
tenant_path     ltree
recipient_user_id uuid FK
channel         text CHECK (channel IN ('inapp','email','push','webhook'))
title           text
body            text
payload         jsonb
read_at         timestamptz NULL
delivered_at    timestamptz NULL
+ ortak
```

### 1.9 `core.ai_sessions`
```sql
id            uuid PK
tenant_path   ltree
user_id       uuid FK
model         text  -- 'claude-opus-4-7', 'gpt-4o', 'local-llama'
messages      jsonb  -- chat history
total_tokens  integer
cost_usd      numeric(10,4)
+ ortak
```

### 1.10 `core.feature_flag_overrides` *(GrowthBook ile sync)*
```sql
id            uuid PK
tenant_path   ltree
flag_key      text
value         jsonb
+ ortak
```

---

## 2. STRATEGY Şeması

### 2.1 `strategy.plans`
```sql
id           uuid PK
tenant_path  ltree
name         text                -- 'Tomofil 2026-2035 Stratejik Plan'
period_start date
period_end   date
status       text CHECK (status IN ('draft','active','archived'))
vision       jsonb   -- translatable {tr:'...', en:'...'}
mission      jsonb
values       jsonb   -- [{title, description}]
+ ortak
```

### 2.2 `strategy.pillars`
```sql
id           uuid PK
plan_id      uuid FK → strategy.plans
tenant_path  ltree
code         text  -- 'H1'..'H6'
title        jsonb (translatable)
description  jsonb
owner_user_id uuid FK
sort_order   integer
+ ortak
```

### 2.3 `strategy.strategies`
```sql
id                  uuid PK
pillar_id           uuid FK
parent_strategy_id  uuid FK NULL  -- alt-strateji
tenant_path         ltree
code                text
title               jsonb
type                text CHECK (type IN ('main','sub'))
owner_user_id       uuid FK
+ ortak
```

### 2.4 `strategy.analyses` *(SWOT/TOWS/PESTEL/Porter5/VRIO ortak)*
```sql
id           uuid PK
plan_id      uuid FK
tenant_path  ltree
framework    text CHECK (framework IN ('swot','tows','pestel','porter5','vrio','value_chain','stakeholder'))
items        jsonb  -- esnek yapı (her framework kendi şeması)
+ ortak
```

### 2.5 `strategy.hoshin_xmatrix`
```sql
id                       uuid PK
plan_id                  uuid FK
tenant_path              ltree
breakthrough_objectives  jsonb
annual_objectives        jsonb
improvement_priorities   jsonb
metrics                  jsonb  -- KPI id referansları
owners                   jsonb
+ ortak
```

### 2.6 `strategy.catchball_channels`
```sql
id            uuid PK
xmatrix_id    uuid FK
tenant_path   ltree
channel_type  text CHECK (channel_type IN ('survey','town_hall','workshop','digital_form','one_on_one'))
participants  jsonb
rounds        jsonb
status        text
+ ortak
```

### 2.7 `strategy.efqm_assessments`
```sql
id              uuid PK
plan_id         uuid FK
tenant_path     ltree
version         text DEFAULT '2025'
criteria_scores jsonb  -- {direction:{...}, execution:{...}, results:{...}}
baseline_score  integer
target_score    integer
assessed_at     timestamptz
assessor_id     uuid FK
+ ortak
```

### 2.8 `strategy.bsc_perspectives`
```sql
id           uuid PK
plan_id      uuid FK
tenant_path  ltree
perspective  text CHECK (perspective IN ('financial','customer','process','learning'))
objectives   jsonb
+ ortak
```

### 2.9 `strategy.okrs`
```sql
id              uuid PK
plan_id         uuid FK
tenant_path     ltree
parent_okr_id   uuid FK NULL
level           text CHECK (level IN ('org','bu','facility','team','individual'))
owner_id        uuid FK  -- user veya workspace
owner_type      text CHECK (owner_type IN ('user','workspace','tenant'))
objective       jsonb (translatable)
period          text  -- '2026-Q1', '2026-H1', '2026'
status          text
+ ortak
```

### 2.10 `strategy.key_results`
```sql
id            uuid PK
okr_id        uuid FK
tenant_path   ltree
title         jsonb
metric_id     uuid FK → strategy.kpis NULL
baseline      numeric
target        numeric
current_value numeric
unit          text
confidence    integer CHECK (confidence BETWEEN 0 AND 100)
+ ortak
```

### 2.11 `strategy.kpis` *(KPI Master — paylaşılan)*
```sql
id            uuid PK
tenant_path   ltree
code          text
name          jsonb
description   jsonb
formula       text     -- 'SUM(x)/COUNT(y)' DSL veya null
unit          text
direction     text CHECK (direction IN ('higher_better','lower_better','target_range'))
frequency     text CHECK (frequency IN ('daily','weekly','monthly','quarterly','annual'))
owner_user_id uuid FK
threshold_green numeric
threshold_amber numeric
threshold_red   numeric
+ ortak
UNIQUE (tenant_path, code)
```

### 2.12 `strategy.kpi_measurements`
```sql
id            uuid PK
kpi_id        uuid FK
tenant_path   ltree
period        date  -- ölçüm dönemi başlangıcı
value         numeric NOT NULL
note          text
source        text  -- 'manual','api','formula'
+ ortak
UNIQUE (kpi_id, period)
```

### 2.13 `strategy.scenarios`
```sql
id            uuid PK
plan_id       uuid FK
tenant_path   ltree
name          jsonb
probability   numeric CHECK (probability BETWEEN 0 AND 1)
assumptions   jsonb
narrative     jsonb
+ ortak
```

### 2.14 `strategy.early_warning_signals`
```sql
id            uuid PK
scenario_id   uuid FK
tenant_path   ltree
indicator     text
threshold     numeric
current_value numeric
status        text CHECK (status IN ('normal','watch','triggered'))
+ ortak
```

### 2.15 `strategy.decision_tree_nodes`
```sql
id              uuid PK
scenario_id     uuid FK
parent_node_id  uuid FK NULL
tenant_path     ltree
condition       jsonb
action          jsonb
+ ortak
```

---

## 3. EXECUTION Şeması

### 3.1 `execution.initiatives`
```sql
id            uuid PK
strategy_id   uuid FK → strategy.strategies
tenant_path   ltree
name          jsonb
sponsor_id    uuid FK → core.users
owner_id      uuid FK → core.users
status        text CHECK (status IN ('proposed','active','on_hold','completed','cancelled'))
start_date    date
end_date      date
health        text CHECK (health IN ('green','amber','red'))
+ ortak
```

### 3.2 `execution.stage_gates`
```sql
id            uuid PK
initiative_id uuid FK
tenant_path   ltree
gate          text CHECK (gate IN ('G0','G1','G2','G3','G4','G5'))
criteria      jsonb
decision      text CHECK (decision IN ('pass','hold','kill','recycle'))
decided_at    timestamptz
reviewer_ids  uuid[]
notes         jsonb
+ ortak
UNIQUE (initiative_id, gate)
```

### 3.3 `execution.real_options`
```sql
id            uuid PK
initiative_id uuid FK
tenant_path   ltree
option_type   text CHECK (option_type IN ('defer','expand','abandon','switch'))
strike        numeric
volatility    numeric
time_horizon  numeric  -- yıl
npv_base      numeric
option_value  numeric
+ ortak
```

### 3.4 `execution.abc_costing_entries`
```sql
id            uuid PK
tenant_path   ltree
initiative_id uuid FK NULL
process_id    uuid FK NULL
activity      text
driver        text
unit_cost     numeric
quantity      numeric
total_cost    numeric
period        date
+ ortak
```

### 3.5 `execution.capex_opex_plans`
```sql
id            uuid PK
initiative_id uuid FK
tenant_path   ltree
type          text CHECK (type IN ('capex','opex'))
year          integer
amount        numeric
currency      char(3) DEFAULT 'EUR'
+ ortak
```

### 3.6 `execution.individual_performance`
```sql
id            uuid PK
user_id       uuid FK
tenant_path   ltree
period        text  -- '2026-H1'
rating        numeric
feedback_360  jsonb
competencies  jsonb
+ ortak
UNIQUE (user_id, period)
```

---

## 4. PROCESS Şeması

### 4.1 `process.processes`
```sql
id            uuid PK
tenant_path   ltree
code          text  -- 'S2E','R2M',... veya tenant-özel
name          jsonb
type          text CHECK (type IN ('e2e_standard','custom'))
owner_id      uuid FK
version       integer
status        text
+ ortak
UNIQUE (tenant_path, code, version)
```

### 4.2 `process.process_steps`
```sql
id            uuid PK
process_id    uuid FK
tenant_path   ltree
sequence      integer
name          jsonb
description   jsonb
sla_target    interval
+ ortak
```

### 4.3 `process.raci_assignments`
```sql
id            uuid PK
step_id       uuid FK
tenant_path   ltree
assignee_type text CHECK (assignee_type IN ('user','role','workspace'))
assignee_id   uuid
raci_role     char(1) CHECK (raci_role IN ('R','A','C','I'))
+ ortak
```

### 4.4 `process.cmmi_assessments`
```sql
id            uuid PK
process_id    uuid FK
tenant_path   ltree
level         integer CHECK (level BETWEEN 1 AND 5)
evidence      jsonb
assessed_at   timestamptz
assessor_id   uuid FK
+ ortak
```

### 4.5 `process.sla_definitions`
```sql
id              uuid PK
process_id      uuid FK
tenant_path     ltree
metric          text
target_value    numeric
threshold_amber numeric
threshold_red   numeric
breach_action   jsonb
+ ortak
```

### 4.6 `process.process_kpi_links`
```sql
id            uuid PK
process_id    uuid FK
kpi_id        uuid FK → strategy.kpis
tenant_path   ltree
weight        numeric DEFAULT 1.0
+ ortak
```

---

## 5. RISK Şeması

### 5.1 `risk.registers`
```sql
id            uuid PK
tenant_path   ltree
name          text
framework     text CHECK (framework IN ('coso_erm','iso_31000','custom'))
+ ortak
```

### 5.2 `risk.risks`
```sql
id                    uuid PK
register_id           uuid FK
tenant_path           ltree
code                  text
title                 jsonb
category              text
owner_id              uuid FK
inherent_likelihood   integer CHECK (BETWEEN 1 AND 5)
inherent_impact       integer CHECK (BETWEEN 1 AND 5)
residual_likelihood   integer
residual_impact       integer
linked_strategy_id    uuid NULL
linked_process_id     uuid NULL
linked_initiative_id  uuid NULL
status                text CHECK (status IN ('open','mitigating','accepted','closed'))
+ ortak
```

### 5.3 `risk.appetite_statements`
```sql
id              uuid PK
register_id     uuid FK
tenant_path     ltree
category        text
threshold_green numeric
threshold_amber numeric
threshold_red   numeric
narrative       jsonb
+ ortak
```

### 5.4 `risk.kris`
```sql
id              uuid PK
risk_id         uuid FK
tenant_path     ltree
metric          text
threshold_amber numeric
threshold_red   numeric
current_value   numeric
kpi_id          uuid FK NULL  -- KPI Master'a bağlanabilir
+ ortak
```

### 5.5 `risk.controls`
```sql
id            uuid PK
risk_id       uuid FK
tenant_path   ltree
type          text CHECK (type IN ('preventive','detective','corrective'))
description   jsonb
effectiveness integer CHECK (BETWEEN 1 AND 5)
owner_id      uuid FK
+ ortak
```

### 5.6 `risk.events`
```sql
id            uuid PK
risk_id       uuid FK
tenant_path   ltree
occurred_at   timestamptz
impact_actual numeric
root_cause    jsonb
lesson        jsonb
+ ortak
```

---

## 6. ESG Şeması

### 6.1 `esg.plans`
```sql
id            uuid PK
tenant_path   ltree
name          text
period_start  date
period_end    date
+ ortak
```

### 6.2 `esg.tcfd_reports`
```sql
id            uuid PK
esg_plan_id   uuid FK
tenant_path   ltree
year          integer
governance    jsonb
strategy      jsonb
risk_mgmt     jsonb
metrics       jsonb
+ ortak
```

### 6.3 `esg.sbti_targets`
```sql
id              uuid PK
esg_plan_id     uuid FK
tenant_path     ltree
scope           integer CHECK (scope IN (1,2,3))
baseline_year   integer
baseline_value  numeric
target_year     integer
reduction_pct   numeric
+ ortak
```

### 6.4 `esg.carbon_inventory`
```sql
id            uuid PK
esg_plan_id   uuid FK
tenant_path   ltree
year          integer
scope         integer
source        text
ton_co2e      numeric
+ ortak
```

### 6.5 `esg.sdg_mappings`
```sql
id                  uuid PK
esg_plan_id         uuid FK
tenant_path         ltree
sdg_number          integer CHECK (BETWEEN 1 AND 17)
linked_strategy_id  uuid NULL
contribution_score  integer
+ ortak
```

---

## 7. AUDIT Şeması (Partitioned)

### 7.1 `audit.events` *(parent — RANGE partition aylık)*
```sql
id            uuid DEFAULT gen_random_uuid()
tenant_path   ltree NOT NULL
actor_user_id uuid NOT NULL
action        text NOT NULL  -- 'create','update','delete','login',...
entity_type   text NOT NULL
entity_id     uuid
before        jsonb
after         jsonb
ip_address    inet
user_agent    text
occurred_at   timestamptz NOT NULL DEFAULT now()
PRIMARY KEY (id, occurred_at)
PARTITION BY RANGE (occurred_at);
```
- 90 gün partition tutulur; daha eskisi S3 WORM'a dump → DROP
- INSERT-only; UPDATE/DELETE policy ile yasak

---

## 8. OUTBOX Şeması

### 8.1 `outbox.events`
```sql
id            uuid PK
tenant_path   ltree NOT NULL
aggregate_type text NOT NULL  -- 'okr','risk',...
aggregate_id  uuid NOT NULL
event_type    text NOT NULL  -- 'okr.updated'
payload       jsonb NOT NULL
created_at    timestamptz DEFAULT now()
published_at  timestamptz NULL  -- relay set ediyor
```
- `apps/relay` 1sn'de bir `WHERE published_at IS NULL` poll eder, NATS'a basar, set eder
- Index: `(published_at NULLS FIRST, created_at)` partial

---

## 9. tenant_path Örnekleri

```
tomofil                            ← organization root
tomofil.holding                    ← holding tenant
tomofil.eu                         ← region workspace
tomofil.eu.berlin                  ← facility sub-tenant
tomofil.eu.berlin.rd_team          ← workspace
tomofil.eu.berlin.rd_team.alice    ← individual scope (OKR L5)
```

Erişim örnekleri (federasyon top-down):
- `app.tenant_path = 'tomofil'` → her şeyi görür (org_admin)
- `app.tenant_path = 'tomofil.eu.berlin'` → Berlin tesis + altı; Münih'i göremez
- `app.tenant_path = 'tomofil.eu.berlin.rd_team.alice'` → sadece kendi
- Çok-tenant veri paylaşımı (Enterprise+): `app.tenant_paths` set'i (array) → policy `tenant_path && array` ile genişletilir (özel rol gerekli)

---

## 10. RLS Bypass Test Suite (ADR-13)

Her PR'da çalışan testler:

1. **Cross-tenant SELECT** — Tenant A user'ı Tenant B kaydını SELECT'leyemez
2. **Cross-tenant INSERT** — Tenant A user'ı Tenant B path'iyle INSERT atamaz
3. **Sub-tenant escalation** — Sub-tenant user üst tenant kaydını göremez
4. **Federation downward** — Org admin alt tenant kaydını görür ✅
5. **Soft-delete invisibility** — `deleted_at IS NOT NULL` SELECT'te gelmez
6. **Connection pool reset** — Transaction commit/rollback sonrası `app.tenant_path` reset olur (PgBouncer transaction mode)
7. **Audit immutability** — `audit.events` UPDATE/DELETE reddedilir
8. **Outbox idempotency** — Aynı event 2 kez publish edilse de consumer bir kez işler

---

## 11. Migration Stratejisi

- Her modül kendi Alembic migration'ını yönetir (`modules/strategy/.../migrations/`)
- Root `apps/api/alembic.ini` `version_locations` ile birleştirir
- Naming: `YYYYMMDD_HHMM_{module}_{short}.py`
- ADR-14 expand-contract zorunlu
- `init` migration'da: `CREATE EXTENSION IF NOT EXISTS ltree, pgcrypto, citext, btree_gist;`

---

## 12. İlk MVP Tablo Sayım Özeti

| Şema | Tablo sayısı |
|------|:---:|
| core | 10 |
| strategy | 15 |
| execution | 6 |
| process | 6 |
| risk | 6 |
| esg | 5 |
| audit | 1 (partitioned) |
| outbox | 1 |
| **Toplam** | **50** |

(D1'de "30+" denmişti; gerçek MVP'de ~50 — modüller arası bağ tabloları dahil)

---

## 13. Onay

Onaylanırsa **D7 — API Tasarım Standartları** (REST/OpenAPI, versiyonlama, hata formatı, pagination, idempotency, rate limit) yazılır.

Kullanıcı onayı: ☐ Onaylandı ☐ Revizyon istendi
