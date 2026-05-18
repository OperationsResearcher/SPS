# D3 — SİNAPS DOMAIN MODEL v1.0
> Domain-Driven Design — Bounded Contexts + Entities
> Tarih: 2026-05-16
> Durum: TASLAK — onay bekliyor
> Bağımlılık: D1 (PRD), D2 (ADR)

---

## 1. Stratejik Tasarım — Bounded Context Haritası

```
┌──────────────────────────────────────────────────────────────────┐
│                      CORE PLATFORM (zorunlu)                     │
│  Identity · Tenancy · Document · Notification · Audit · AI-Base │
└──────────────────────────────────────────────────────────────────┘
        ▲                  ▲                  ▲                ▲
        │                  │                  │                │
┌───────┴────────┐ ┌───────┴────────┐ ┌───────┴────────┐ ┌─────┴──────┐
│   STRATEGY     │ │   EXECUTION    │ │    PROCESS     │ │    RISK    │
│  Vision/SWOT   │ │  Initiative    │ │  E2E Process   │ │  COSO/ISO  │
│  Hoshin/EFQM   │ │  Stage-Gate    │ │  RACI/CMMI     │ │  KRI/Reg.  │
│  OKR Cascade   │ │  ABC/Real Opt  │ │  SLA/KPI link  │ │  Appetite  │
│  Scenario      │ │  Indiv. Perf.  │ │                │ │            │
└────────────────┘ └────────────────┘ └────────────────┘ └────────────┘
                                                              ▲
                                          ┌───────────────────┴────────┐
                                          │           ESG              │
                                          │  TCFD / SBTi / BMSKA       │
                                          │  Carbon / Sustainability   │
                                          └────────────────────────────┘
```

**Bağlam ilişki tipleri (Context Map):**
- CORE → diğer hepsi: **Shared Kernel** (User, Tenant, AuditEvent ortak tip)
- STRATEGY → EXECUTION: **Customer/Supplier** (Initiative, Strategy ID'sini tüketir)
- STRATEGY → PROCESS: **Conformist** (Process KPI'ı Strategy KPI'ını referanslar)
- RISK → STRATEGY, EXECUTION, PROCESS: **Partnership** (her yerden risk bağlanabilir)
- ESG → STRATEGY, PROCESS: **Customer/Supplier** (ESG hedefi strateji hedefi referanslar)
- Bütün context'ler → CORE.AuditEvent: **Published Language** (event şeması ortak)

---

## 2. CORE — Platform Bounded Context

### 2.1 Aggregate'ler

#### Organization (root)
- `id: uuid`
- `name: text`
- `tenant_path: ltree` (root: `org_slug`)
- `brand: enum(kokpitim, sinaps)`
- `tier: enum(starter, pro, enterprise, enterprise_plus)`
- `created_at, deleted_at`

#### Tenant (root)
- `id: uuid`
- `organization_id: uuid → Organization`
- `parent_tenant_id: uuid?` (sub-tenant ise)
- `tenant_path: ltree`
- `name, slug, locale_default, timezone`
- `enabled_modules: text[]` (tenant admin pasifleştirebilir)
- `package_id: uuid → Package`

#### Workspace (root)
- `id, tenant_id, name, tenant_path`
- Birim/departman seviyesi konteyner; entity'ler workspace'e bağlanır

#### User (root)
- `id, email, keycloak_sub, locale, status`
- `default_tenant_id`

#### Membership (root)
- `user_id, tenant_path, role_set: text[]` (RBAC)
- Federasyon top-down: üst tenant_path'te `role=org_admin` alt'ı görür

#### Package (root)
- `id, name (Starter/Pro/Enterprise/Enterprise+), module_codes: text[]`

#### Document (root) — belge yönetimi
- `id, tenant_path, owner_user_id, mime, size, s3_key, version`

#### Notification (root)
- `id, recipient_user_id, channel, payload, read_at`

#### AuditEvent (root)
- `id, tenant_path, actor_user_id, action, entity_type, entity_id, before, after, occurred_at`
- Append-only, outbox üzerinden NATS → S3 WORM

#### AISession (root) — AI Concierge temel
- `id, tenant_path, user_id, model, messages: jsonb, cost_usd, tokens`

---

## 3. STRATEGY — Bounded Context

### Aggregate'ler

#### StrategicPlan (root)
- `id, tenant_path, name, period_start, period_end, status`
- Tomofil 2026–2035 örneği
- Children: Vision, Mission, Pillars (H1–H6), Strategies, OKRSet

#### Vision / Mission / Value
- `text translatable_field (jsonb i18n)`

#### Pillar (Strategic Goal, H1–H6)
- `id, plan_id, code, title, owner_user_id`

#### Strategy (ana / alt)
- `id, pillar_id, parent_strategy_id?, code, title, type (main/sub)`
- 18 ana + 55 alt (Tomofil)

#### SWOT / TOWS / PESTEL / Porter5 / VRIO (analiz aggregate'leri)
- Hepsi `tenant_path, plan_id, items: jsonb` ortak yapı
- VRIO her kaynak için `value, rare, inimitable, organized` bool + skor

#### HoshinXMatrix (root)
- `id, plan_id, breakthrough_objectives[], annual_objectives[], improvement_priorities[], metrics[], owners[]`
- Catchball kanalları (child)

#### CatchballChannel
- `id, x_matrix_id, channel_type, participants, rounds: jsonb`

#### EFQMAssessment (root)
- `id, plan_id, version (2025), criteria_scores: jsonb` (Direction, Execution, Results)
- `baseline_score, target_score` (Tomofil 579 → 820)

#### BSC (Balanced Scorecard)
- `id, plan_id, perspective: enum(financial, customer, process, learning)`
- KPI bağlantıları

#### OKRSet (root) — 5 seviye cascade
- `id, plan_id, level: enum(org, bu, facility, team, individual), parent_okr_id?, owner_id`
- Children: Objective + KeyResult[]

#### KeyResult
- `id, okr_id, title, metric_id?, target, current, unit, confidence (0-100)`

#### Scenario (root)
- `id, plan_id, name, probability, assumptions: jsonb, narrative`
- 4 senaryo (Tomofil)

#### EarlyWarningSignal
- `id, scenario_id, indicator, threshold, current_value, status`

#### DecisionTreeNode
- `id, scenario_id, parent_node_id?, condition, action`

#### KPI (Master) — paylaşılan
- `id, tenant_path, code, name, formula, unit, owner_user_id, frequency`
- Strategy/Process/Risk/ESG hepsi bu master KPI'a bağlanır

---

## 4. EXECUTION — Bounded Context

### Aggregate'ler

#### Initiative (root) — Stratejik Girişim
- `id, strategy_id, name, sponsor_id, owner_id, status, start_date, end_date`
- 24 girişim (Tomofil)

#### StageGate
- `id, initiative_id, gate: enum(G0,G1,G2,G3,G4,G5), criteria: jsonb, decision, decided_at, reviewer_ids[]`

#### RealOptionValuation
- `id, initiative_id, type (defer/expand/abandon), strike, volatility, npv_base, option_value`

#### ABCCostingEntry
- `id, initiative_id?, process_id?, activity, driver, cost_amount`

#### CAPEXPlan / OPEXPlan
- `id, initiative_id, year, amount, currency`

#### IndividualPerformance (root)
- `id, user_id, period, okrs[], rating, feedback_360: jsonb`

---

## 5. PROCESS — Bounded Context

### Aggregate'ler

#### Process (root) — E2E
- `id, tenant_path, code (S2E, R2M, ...), name, owner_id, version`
- 14 E2E süreç (Tomofil)

#### ProcessStep
- `id, process_id, sequence, name, description, sla_target`

#### RACIAssignment
- `step_id, user_or_role_id, role: enum(R,A,C,I)`

#### CMMIAssessment
- `process_id, level: 1..5, evidence: jsonb, assessed_at, assessor_id`

#### SLADefinition
- `process_id, metric, target, threshold, breach_action`

#### ProcessKPILink
- `process_id, kpi_id, weight`

---

## 6. RISK — Bounded Context

### Aggregate'ler

#### RiskRegister (root)
- `id, tenant_path, name, framework: enum(coso_erm, iso_31000)`

#### Risk
- `id, register_id, code, title, category, owner_id`
- `inherent_likelihood, inherent_impact, residual_likelihood, residual_impact`
- `linked_strategy_id?, linked_process_id?, linked_initiative_id?`

#### RiskAppetiteStatement
- `id, register_id, category, threshold_green, threshold_amber, threshold_red`

#### KRI (Key Risk Indicator)
- `id, risk_id, metric, threshold_amber, threshold_red, current_value`

#### Control
- `id, risk_id, type (preventive/detective), effectiveness, owner_id`

#### RiskEvent (gerçekleşmiş olay)
- `id, risk_id, occurred_at, impact_actual, root_cause, lesson`

---

## 7. ESG — Bounded Context

### Aggregate'ler

#### ESGPlan (root)
- `id, tenant_path, name, period`

#### TCFDReport
- `id, esg_plan_id, year, governance, strategy, risk_mgmt, metrics: jsonb`

#### SBTiTarget
- `id, esg_plan_id, scope: enum(1,2,3), target_year, baseline_year, reduction_pct`

#### CarbonInventoryEntry
- `id, esg_plan_id, year, scope, source, ton_co2e`

#### BMSKAMapping (BM Sürdürülebilir Kalkınma Amaçları)
- `id, esg_plan_id, sdg_number (1..17), linked_strategy_id?, contribution_score`

#### SustainabilityReport
- `id, esg_plan_id, framework (GRI/CSRD/...), year, file_document_id`

---

## 8. Domain Event Kataloğu (özet)

| Event | Yayınlayan | Tüketen | Kullanım |
|-------|-----------|---------|---------|
| `tenant.provisioned` | CORE | tüm modüller | İlk veri seed |
| `okr.updated` | STRATEGY | EXECUTION, dashboard | Cascade refresh |
| `kpi.threshold_breached` | STRATEGY/PROCESS | RISK, Notification | KRI tetikleme |
| `stagegate.decision_made` | EXECUTION | STRATEGY, audit | Initiative ilerle |
| `risk.escalated` | RISK | STRATEGY, Notification | Risk iştahı aşıldı |
| `process.cmmi_assessed` | PROCESS | STRATEGY (EFQM), dashboard | EFQM skor güncelleme |
| `esg.target_progress` | ESG | STRATEGY, BSC | BSC sürdürülebilirlik perspektifi |
| `document.uploaded` | CORE | AI-Base | AI indexleme |

Hepsi outbox pattern (ADR-17) üzerinden NATS JetStream'e basılır.

---

## 9. Ortak Çapraz Kesim (Cross-Cutting)

**Tüm aggregate'lerde zorunlu kolonlar:**
- `id uuid primary key default gen_random_uuid()`
- `tenant_path ltree not null` (RLS hedefi)
- `created_at, updated_at timestamptz`
- `created_by, updated_by uuid → User`
- `deleted_at timestamptz null` (ADR-15 soft delete)
- `version int default 1` (optimistic locking)

**RLS policy şablonu (her tabloya):**
```sql
CREATE POLICY tenant_isolation ON {table}
  USING (tenant_path <@ current_setting('app.tenant_path')::ltree);
```
Federasyon yukarıdan aşağı: org_admin için `app.tenant_path = 'tomofil'` set edilir → tüm alt path görünür.

---

## 10. Aggregate Boyut Disiplini

- **Bir aggregate = bir transaction sınırı.** İki aggregate arasındaki güncelleme = domain event + eventual consistency.
- Aggregate referansı **sadece ID ile** (entity referansı değil).
- Aggregate çocuğu 1000 satırı aşıyorsa → ayrı aggregate (örn. AuditEvent zaten ayrı).

---

## 11. Açık Sorular (D4–D6'ya taşınan)

- D4: Modül kataloğunda bu context'ler hangi alt-modüllere bölünecek?
- D5: Repo'da `packages/domain/` ortak tipler mi, her context kendi paketinde mi?
- D6: KPI Master tablosu cross-context — hangi context "owner"?  (Öneri: ortak `kpi` schema'sında, STRATEGY context içinde DDD bakımı)

---

## 12. Onay

Onaylanırsa **D4 — Modül Kataloğu v1** (80+ alt-modül, paket eşleme, faz dağılımı) yazılır.

Kullanıcı onayı: ☐ Onaylandı ☐ Revizyon istendi
