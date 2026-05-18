# D5 — SİNAPS REPO YAPISI v1.0
> Turborepo monorepo · pnpm + uv · klasör hiyerarşisi
> Tarih: 2026-05-16
> Durum: TASLAK — onay bekliyor
> Bağımlılık: D1–D4

---

## 1. Üst-Seviye Layout

```
sinaps/                              ← yeni repo (Kokpitim'den bağımsız)
├── apps/
│   ├── web/                         Next.js 15 App Router (kullanıcı arayüzü)
│   ├── admin/                       Next.js — bizim platform admin paneli
│   ├── mobile/                      React Native + Expo
│   ├── api/                         FastAPI (Python) — ana backend
│   ├── worker/                      FastAPI/Arq — async job worker
│   └── relay/                       Outbox → NATS relay (Python)
│
├── packages/                        Paylaşılan TS/JS paketler
│   ├── ui/                          Shadcn/ui tabanlı bileşen kütüphanesi
│   ├── config/                      ESLint, Prettier, TS, Tailwind base
│   ├── api-client/                  OpenAPI'den üretilen TS SDK
│   ├── i18n/                        next-intl mesaj bundle'ları (23 dil)
│   ├── icons/                       Lucide wrapper + özel ikonlar
│   ├── analytics/                   Telemetry wrapper (OTEL)
│   └── feature-flags/               GrowthBook SDK wrapper
│
├── python/                          Paylaşılan Python paketler
│   ├── sinaps_core/                 Domain primitives (Tenant, User, AuditEvent)
│   ├── sinaps_db/                   SQLAlchemy base, RLS yardımcıları, ltree
│   ├── sinaps_events/               NATS publisher/consumer + outbox
│   ├── sinaps_auth/                 Keycloak + OPA istemcileri
│   ├── sinaps_observability/        OpenTelemetry kurulum
│   └── sinaps_testing/              Pytest fixtures + Tenant Isolation Suite
│
├── modules/                         Domain modülleri (D3'teki bounded context'ler)
│   ├── core/                        M-CORE (Python paketi + UI parçaları)
│   ├── strategy/                    M-STRATEGY
│   ├── execution/                   M-EXECUTION
│   ├── process/                     M-PROCESS
│   ├── risk/                        M-RISK
│   └── esg/                         M-ESG
│
├── contracts/
│   ├── openapi/                     OpenAPI 3.1 spec'leri (versiyonlu)
│   ├── events/                      Domain event JSON Schema'ları
│   └── policies/                    OPA Rego policy bundle'ları
│
├── infra/
│   ├── helm/                        Helm chart (cloud-agnostic deploy)
│   ├── terraform/                   IaC modülleri (GCP/AWS/Azure)
│   ├── docker/                      Dockerfile'lar
│   └── k8s/                         Manifests, Kustomize overlay'leri
│
├── ops/
│   ├── argocd/                      ArgoCD Application manifest'leri
│   ├── observability/               Grafana dashboard JSON, Loki/Tempo config
│   ├── runbooks/                    İncident runbook'ları (markdown)
│   └── seeds/                       Tomofil seed data (X.6)
│
├── docs/
│   ├── sinaps/                      D1–D8 (bu klasör)
│   ├── adr/                         Yeni ADR'lar (D2 sonrası)
│   ├── api/                         API kullanıcı dokümanları
│   └── architecture/                Diyagramlar (Mermaid)
│
├── scripts/                         CLI yardımcıları (TS + Python)
├── .github/
│   └── workflows/                   CI/CD (test, build, deploy)
├── turbo.json
├── pnpm-workspace.yaml
├── package.json                     root
├── pyproject.toml                   root Python workspace (uv)
└── README.md
```

---

## 2. Modül Klasör Şablonu (her bounded context için aynı)

```
modules/strategy/
├── pyproject.toml                   uv paket: "sinaps-module-strategy"
├── src/
│   └── sinaps_module_strategy/
│       ├── __init__.py
│       ├── domain/                  Aggregate'ler, value objects (saf Python)
│       │   ├── plan.py
│       │   ├── okr.py
│       │   └── hoshin.py
│       ├── application/             Use case'ler / command handler'lar
│       │   ├── commands/
│       │   └── queries/
│       ├── infrastructure/          SQLAlchemy modelleri, repository impl
│       │   ├── models.py
│       │   ├── repositories.py
│       │   └── migrations/          Alembic — modül kendi migration'ı
│       ├── api/                     FastAPI router'lar
│       │   ├── routes.py
│       │   └── schemas.py           Pydantic
│       ├── events/                  Yayınlanan + tüketilen event handler'ları
│       └── policies/                Rego policy'ler (OPA)
├── tests/
│   ├── unit/
│   ├── integration/
│   └── isolation/                   Tenant izolasyon testleri
└── ui/                              Modüle özel UI parçaları
    ├── components/
    └── pages/                       Web app'e import edilecek route segment'ler
```

**Neden modül başına `ui/` klasörü?** Web/admin app'leri bu klasörden import eder; modül kapatılırsa hem backend hem UI birlikte devre dışı.

---

## 3. apps/web Detayı (Next.js 15)

```
apps/web/
├── src/
│   ├── app/                         App Router
│   │   ├── (auth)/                  Keycloak redirect, callback
│   │   ├── (platform)/              Tenant context'li ana ürün
│   │   │   ├── [tenantSlug]/
│   │   │   │   ├── strategy/        ← modules/strategy/ui'dan import
│   │   │   │   ├── execution/
│   │   │   │   ├── process/
│   │   │   │   ├── risk/
│   │   │   │   ├── esg/
│   │   │   │   └── dashboard/
│   │   │   └── layout.tsx
│   │   └── api/                     Route Handler (BFF gerekirse — ADR-06)
│   ├── lib/
│   │   ├── auth.ts                  Keycloak helper
│   │   ├── api.ts                   api-client wrapper
│   │   └── tenant-context.tsx       Tenant path provider
│   └── middleware.ts                i18n + auth + tenant resolve
├── messages/                        next-intl JSON (23 dil)
├── public/
├── next.config.mjs
├── tailwind.config.ts
└── package.json
```

---

## 4. apps/api Detayı (FastAPI)

```
apps/api/
├── src/
│   └── sinaps_api/
│       ├── main.py                  FastAPI app, lifecycle, OTEL init
│       ├── settings.py              pydantic-settings (env-based)
│       ├── deps.py                  Dependency injection (db session, tenant ctx)
│       ├── middleware/
│       │   ├── tenant_context.py    JWT → app.tenant_path SET
│       │   ├── audit.py             Her request audit event
│       │   └── opa.py               Policy check
│       └── routers/                 Modül router'larını mount
│           └── __init__.py          for module in modules: app.include_router(...)
├── alembic.ini                      Birden çok modül migration'ı yönetir
├── tests/
└── pyproject.toml
```

---

## 5. Turborepo Pipeline (turbo.json özet)

```json
{
  "tasks": {
    "build":   { "dependsOn": ["^build"], "outputs": ["dist/**", ".next/**"] },
    "lint":    { "dependsOn": ["^lint"] },
    "test":    { "dependsOn": ["^build"], "outputs": ["coverage/**"] },
    "test:isolation": { "cache": false },
    "typecheck": { "dependsOn": ["^build"] },
    "dev":     { "cache": false, "persistent": true }
  }
}
```

Remote cache: GitHub Actions cache veya self-host Turborepo remote (cloud-agnostic).

---

## 6. Python Workspace (uv)

Root `pyproject.toml`:

```toml
[tool.uv.workspace]
members = [
  "apps/api", "apps/worker", "apps/relay",
  "python/*",
  "modules/*",
]
```

Modüller arası bağımlılık: `sinaps-module-strategy` → `sinaps-core`, `sinaps-db`, `sinaps-events` (path dependency, sürüm yok).

---

## 7. Adlandırma Kuralları

| Tür | Kural | Örnek |
|-----|-------|-------|
| TS paket | `@sinaps/<name>` kebab-case | `@sinaps/ui`, `@sinaps/api-client` |
| Python paket (dist) | `sinaps-<scope>` kebab-case | `sinaps-core`, `sinaps-module-strategy` |
| Python import | `sinaps_<scope>` snake_case | `import sinaps_core` |
| Klasör (modül) | tek kelime, küçük | `strategy/`, `execution/` |
| Docker image | `ghcr.io/kokpit/sinaps-<service>` | `sinaps-api`, `sinaps-web` |
| Helm release | `sinaps-<env>` | `sinaps-prod`, `sinaps-staging` |

---

## 8. Branch & Versiyon

- Default branch: `main` (deploy edilebilir)
- Feature: `feat/<modül>-<kısa>`, Fix: `fix/...`, Chore: `chore/...`
- Tag: `v<MAJOR>.<MINOR>.<PATCH>` semver — uygulama bazlı değil, repo bazlı
- Release notes: Changesets (TS) + towncrier (Python) — birleşik CHANGELOG

---

## 9. CI/CD Akış Özeti

```
PR açıldı
  ├─ turbo lint + typecheck + test (affected only)
  ├─ uv run pytest (affected python paketler)
  ├─ Tenant Isolation Suite (mutlaka)
  ├─ Docker build (changed apps only)
  └─ Preview deploy (PR namespace, K8s)
PR merged → main
  ├─ Full build
  ├─ Helm chart bump
  ├─ ArgoCD sync → staging
  └─ Manual promote → production
```

---

## 10. Kokpitim Repo İle İlişki

- Sinaps **ayrı repo** (yeni). Kokpitim mevcut repo'sunda yaşamaya devam eder.
- ETL one-time migration script'i `ops/migration-from-kokpitim/` altında — sadece müşteri taşımak isterse çalışır.
- Ortak hiçbir kod paylaşılmaz (temiz başlangıç).

---

## 11. İlk Hafta Bootstrap Checklist

1. `gh repo create kokpit/sinaps --private`
2. Root `package.json`, `pnpm-workspace.yaml`, `turbo.json`, `pyproject.toml`
3. `.github/workflows/ci.yml` (lint+test+build)
4. `packages/config` (ESLint/Prettier/TS/Tailwind base)
5. `infra/docker/` temel Dockerfile (Python+Node multi-stage)
6. `infra/helm/sinaps/` iskelet chart (postgres, redis, nats, vault placeholder)
7. `apps/api` minimum FastAPI + health endpoint + OTEL
8. `apps/web` minimum Next.js + Keycloak login stub
9. `python/sinaps_db` ltree + RLS test fixture
10. `modules/core/` Identity + Tenant aggregate iskeleti

Bu 10 madde = F1'in ilk 2 haftası.

---

## 12. Onay

Onaylanırsa **D6 — Veri Modeli Taslağı** (30+ ana tablo, RLS policy örnekleri, tenant_path migration) yazılır.

Kullanıcı onayı: ☐ Onaylandı ☐ Revizyon istendi
