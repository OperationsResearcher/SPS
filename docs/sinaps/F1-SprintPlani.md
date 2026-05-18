# FAZ 1 — PLATFORM SPRINT PLANI v1.0
> M-CORE + multi-tenant infra + Keycloak + i18n + DevOps
> Süre: 12 hafta (6 × 2-haftalık sprint)
> Tarih: 2026-05-16
> Durum: TASLAK — onay bekliyor
> Bağımlılık: D1–D8

---

## 0. Faz-1 Hedefi

**"Sinaps platformu üzerinde boş bir tenant yaratıldığında: kullanıcı Keycloak ile giriş yapabiliyor, tenant context'i RLS ile izole, paket bazlı modül aktif/pasif çalışıyor, audit log akıyor, AI Concierge ping atıyor, sistem 3 farklı bulutta deploy edilebiliyor."**

Faz-1 sonunda **iş mantığı yok**, ama **iskelet üretime hazır**. F2 strateji modüllerini bu zemine kuracak.

---

## 1. Kapsam (M-CORE 1.1 → 1.12)

| Kod | Alt-Modül | Sprint |
|-----|-----------|:------:|
| 1.1 | Identity & SSO (Keycloak) | S1, S2 |
| 1.2 | Organization & Tenant + ltree | S1, S2 |
| 1.3 | RBAC & Membership | S2, S3 |
| 1.4 | License & Package + OPA | S3, S4 |
| 1.5 | Document Vault | S4 |
| 1.6 | Notification Center | S5 |
| 1.7 | Audit Log + Outbox | S2, S3 |
| 1.8 | Dashboard Framework (iskelet) | S5 |
| 1.9 | AI Concierge (LiteLLM bağlantı) | S6 |
| 1.10 | Localization Engine | S1 (paralel) |
| 1.11 | Search (Postgres FTS + pgvector) | S6 |
| 1.12 | Activity Feed | S5 |

**Yardımcı:** X.2 API Gateway (S2), X.4 Data Export (S5), X.7 Feature Flag Admin (S4), X.8 Tenant Provisioning UI (S4)

---

## 2. Sprint S0 — Bootstrap (Hafta 0, 1 hafta)

**Amaç:** Repo + CI + infra iskeleti çalışsın.

| # | Görev | Çıktı |
|---|-------|-------|
| S0.1 | GitHub org `kokpit` + repo `kokpit/sinaps` private | repo |
| S0.2 | Turborepo + pnpm + uv workspace iskelet | `package.json`, `pyproject.toml`, `turbo.json` |
| S0.3 | `packages/config` (ESLint, Prettier, TS, Tailwind base) | paket |
| S0.4 | `apps/api` minimum FastAPI + `/health` | endpoint |
| S0.5 | `apps/web` minimum Next.js 15 + landing | sayfa |
| S0.6 | `infra/docker/Dockerfile.api`, `.web` multi-stage | docker build geçer |
| S0.7 | `infra/helm/sinaps/` iskelet chart | helm lint geçer |
| S0.8 | `.github/workflows/ci.yml` (lint+typecheck+test+build) | yeşil CI |
| S0.9 | Local dev stack: docker-compose (Postgres+Redis+NATS+Keycloak+Vault) | `make dev` çalışır |
| S0.10 | `python/sinaps_db` ltree + RLS helper iskeleti | paket |

**Çıkış kriteri:** PR açıldığında CI yeşil; localde `make dev` ile 7 servis ayağa kalkar.

---

## 3. Sprint S1 — Identity + Tenant Çekirdeği (Hafta 1-2)

| # | Görev | Modül |
|---|-------|-------|
| S1.1 | Keycloak realm konfig (OIDC, MFA, password policy) | 1.1 |
| S1.2 | `core.users`, `core.organizations`, `core.tenants` migration | 1.2 |
| S1.3 | ltree extension + tenant_path GIST index | 1.2 |
| S1.4 | RLS policy şablonu (Postgres function ile DRY) | 1.2 |
| S1.5 | FastAPI middleware: JWT → `SET LOCAL app.tenant_path` | 1.1, 1.2 |
| S1.6 | `POST /v1/organizations` (platform admin only) | 1.2 |
| S1.7 | `POST /v1/tenants` + sub-tenant create | 1.2 |
| S1.8 | Web: Keycloak login redirect + callback + session | 1.1 |
| S1.9 | next-intl kurulum + 3 dil seed (tr, en, ar) | 1.10 |
| S1.10 | RLS Bypass Test Suite v1 (8 test — D6 §10) | test |

**Çıkış kriteri:** İki farklı tenant'tan kullanıcı login olur, hiçbiri diğerinin verisini göremez (otomatik test yeşil).

---

## 4. Sprint S2 — RBAC + Audit + Outbox (Hafta 3-4)

| # | Görev | Modül |
|---|-------|-------|
| S2.1 | `core.memberships` + role_set | 1.3 |
| S2.2 | Role catalog seed (org_admin, tenant_admin, strategy_editor, viewer, ...) | 1.3 |
| S2.3 | FastAPI `require_role()` dependency | 1.3 |
| S2.4 | `audit.events` partitioned tablo + monthly partition job | 1.7 |
| S2.5 | Audit middleware: her mutating request → outbox INSERT | 1.7 |
| S2.6 | `outbox.events` + relay servis (`apps/relay`) → NATS publish | 1.7 |
| S2.7 | S3 WORM bucket setup (MinIO local, gerçek cloud F1 sonu) | 1.7 |
| S2.8 | Audit → S3 rollover job (90+ gün partition) | 1.7 |
| S2.9 | API Gateway: rate limit middleware (Redis token bucket) | X.2 |
| S2.10 | OpenAPI spec auto-export + commit hook | X.2 |

**Çıkış kriteri:** Tüm mutating action audit'lenir, NATS'a basılır, 90 günden eski S3'e gider. RBAC ihlali 403.

---

## 5. Sprint S3 — Package + OPA + Federation (Hafta 5-6)

| # | Görev | Modül |
|---|-------|-------|
| S3.1 | `core.packages` seed (Starter/Pro/Enterprise/Enterprise+) | 1.4 |
| S3.2 | Tenant.enabled_modules + paket vs override mantığı | 1.4 |
| S3.3 | OPA sidecar deploy (Docker + Helm) | 1.4 |
| S3.4 | Rego policy bundle: paket+modül+rol erişim | 1.4 |
| S3.5 | FastAPI OPA middleware (cache 60sn) | 1.4 |
| S3.6 | Federasyon top-down: org_admin alt tenant'ı görür test | 1.3, 1.4 |
| S3.7 | Çok-tenant erişim (Enterprise+) — `tenant_paths` array claim | 1.3 |
| S3.8 | Tenant admin UI: modül aktif/pasif toggle | 1.4, X.8 |
| S3.9 | Audit Log Query API (read-only) | 1.7 |
| S3.10 | Tenant Isolation Suite v2 (federasyon dahil) | test |

**Çıkış kriteri:** Enterprise tenant Hoshin modülü görür; Starter aynı endpoint'i çağırınca 403. Tenant admin modülü kapatır → 30sn'de etki.

---

## 6. Sprint S4 — Document Vault + Provisioning + Flags (Hafta 7-8)

| # | Görev | Modül |
|---|-------|-------|
| S4.1 | `core.documents` + S3 presigned upload | 1.5 |
| S4.2 | Mime sniff + virus scan hook (clamav opsiyonel) | 1.5 |
| S4.3 | Versiyonlama + soft delete | 1.5 |
| S4.4 | Document UI: list, upload, preview | 1.5 |
| S4.5 | Tenant Provisioning UI (bizim admin) — `apps/admin` | X.8 |
| S4.6 | "New Organization wizard" — org+root tenant+admin user create | 1.2, X.8 |
| S4.7 | GrowthBook self-host deploy + SDK wire (web+api) | X.7 |
| S4.8 | Feature Flag Admin UI iskelet | X.7 |
| S4.9 | Tomofil seed script v1 (org + 2 sub-tenant + 5 user) | X.6 |
| S4.10 | E2E test: yeni org provisioned → admin login → modül aktif | test |

**Çıkış kriteri:** Bizim admin panelinden 5 dakikada yeni Enterprise tenant açılır, admin email'i ile login eder, dashboard görür (boş).

---

## 7. Sprint S5 — Notifications + Dashboard + Feed + Export (Hafta 9-10)

| # | Görev | Modül |
|---|-------|-------|
| S5.1 | `core.notifications` + channel adapter (email, in-app, webhook) | 1.6 |
| S5.2 | NATS consumer: domain event → notification rules | 1.6 |
| S5.3 | Web: in-app notification bell + read state | 1.6 |
| S5.4 | Email template engine (MJML) + Postmark/SES adapter | 1.6 |
| S5.5 | Webhook outbound + HMAC signing | X.3 |
| S5.6 | Dashboard framework (widget container, grid layout) | 1.8 |
| S5.7 | 3 temel widget: KPI Tile, Counter, Last Activity | 1.8 |
| S5.8 | Activity Feed (audit-derived, user-friendly) | 1.12 |
| S5.9 | Data Export (CSV/XLSX) — generic list endpoint | X.4 |
| S5.10 | i18n: tüm UI string'ler tr/en/ar tamamlandı | 1.10 |

**Çıkış kriteri:** Tenant'a yeni kullanıcı eklendi → admin in-app + email bildirim; dashboard widget'lar render, CSV export çalışır.

---

## 8. Sprint S6 — AI Concierge + Search + Sertleştirme (Hafta 11-12)

| # | Görev | Modül |
|---|-------|-------|
| S6.1 | LiteLLM proxy deploy (Helm) + Claude/OpenAI provider | 1.9 |
| S6.2 | Tenant başına model whitelist + cost cap policy | 1.9 |
| S6.3 | `core.ai_sessions` + chat API | 1.9 |
| S6.4 | Web: AI Concierge drawer (basit chat, RAG'siz) | 1.9 |
| S6.5 | pgvector extension + embedding pipeline iskelet | 1.11 |
| S6.6 | Global FTS search endpoint (tenant filtreli) | 1.11 |
| S6.7 | Helm chart 3 cloud-prov test (GCP, AWS, Azure) | infra |
| S6.8 | ArgoCD staging environment kurulum | infra |
| S6.9 | OpenTelemetry → Grafana Stack uçtan uca trace | observability |
| S6.10 | Yük testi: 100 concurrent tenant context switch, RLS doğru | test |
| S6.11 | Pen test mini: RLS bypass, JWT tampering, OPA bypass | sec |
| S6.12 | Faz-1 demo + Faz-2 kickoff dokümanı | mgmt |

**Çıkış kriteri:** Tenant kullanıcısı "merhaba" yazar, AI yanıt verir (LiteLLM üzerinden); search "user added today" arar, sonuç döner; 3 bulutta `helm install` 1 günde başarılı.

---

## 9. Sprint Bazlı Çıkış Kriterleri (Definition of Done)

Her sprint sonunda zorunlu:
- [ ] Tüm görevler merged + main yeşil
- [ ] Tenant Isolation Suite %100 geçer
- [ ] CI < 12 dk
- [ ] OpenAPI spec güncel + SDK regenerate
- [ ] CHANGELOG bumped
- [ ] Sprint demo (15dk, kullanıcıya canlı)
- [ ] Retro notları `ops/runbooks/sprint-retros/` altında

---

## 10. Stage-Gate (Faz-1 sonu — G1 Review)

Kendi ürünümüzü kendimize uyguluyoruz (D1 §9). Faz-1 sonunda **G1 Gate** kararı:

**G1 kriterleri:**
1. M-CORE 12 alt-modülü canlı staging'de çalışıyor ✓
2. RLS bypass testleri 0 başarısız ✓
3. 3-bulut deploy belgelenmiş (her biri için runbook) ✓
4. p95 < 200ms (boş tenant CRUD) ✓
5. Cost target: Enterprise tenant başına aylık altyapı < $80 (tahmini) ✓
6. SOC2 hazırlık checklist %40 ✓
7. Demo: Tomofil seed senaryo → login → tenant geçişi → audit görünür ✓

**Karar:** Pass → Faz-2 başlar / Hold → eksiklerin sprint S7'de kapatılması / Recycle → kapsam revize.

---

## 11. Riskler ve Hafifletme

| # | Risk | Olasılık | Etki | Önlem |
|---|------|:---:|:---:|-------|
| R1 | Keycloak self-host operasyonel karmaşa | O | Y | Helm chart, runbook, HA cluster |
| R2 | ltree + RLS perf düşük (büyük tenant) | D | Y | GIST index + benchmark S2'de |
| R3 | OPA latency > 20ms | D | O | Sidecar + sticky cache |
| R4 | NATS JetStream öğrenme eğrisi | O | O | İlk haftada 1 günlük workshop |
| R5 | 3-bulut paritesi (özellikle Azure ltree desteği) | O | Y | Azure Database for PostgreSQL Flexible Server doğrulama S6'da |
| R6 | LiteLLM rate limit / token cost tracking | D | O | Cost cap policy zorunlu |
| R7 | Sprint hızı düşük (12 hafta yetmez) | O | Y | S0+S6 buffer'lı; Stage-Gate hold opsiyonu var |

---

## 12. Kapasite Varsayımı

Bu plan **2 backend + 2 frontend + 1 SRE/DevOps + 1 ürün-tasarım = 6 kişi** ekiple yapılabilir hesabı içerir. Daha küçük ekipte sprint sayısı artar — kapsam aynı kalır, takvim genişler.

---

## 13. Onay & Sıradaki Çıktı

Bu sprint planı onaylanırsa **Sprint S0** kickoff'u olur:
- [ ] Repo create
- [ ] Bootstrap 10 madde (D5 §11)
- [ ] S1 hazırlık (Keycloak realm tasarımı + RLS policy fonksiyon önerisi)

Kullanıcı onayı: ☐ Onaylandı ☐ Revizyon istendi

---

## Ek — Faz-1 Sonrası Roadmap (kısa)

| Faz | Süre | İçerik | Stage-Gate |
|-----|------|--------|:---:|
| F2 | 12 hf | M-STRATEGY + KPI Master + AI Concierge derinleştirme | G2 |
| F3 | 12 hf | M-EXECUTION + M-PROCESS + Tomofil 24 OKR pilot | G3 |
| F4 | 12 hf | M-RISK + M-ESG + Mobile (RN+Expo) + Beta release | G4 |
| F5+ | — | Forecast, marketplace, ERP connector, white-label | — |
