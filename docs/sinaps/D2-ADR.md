# D2 — SİNAPS ADR SET v1.0
> Architecture Decision Records
> Tarih: 2026-05-16
> Durum: TASLAK — onay bekliyor
> Format: Her ADR = Bağlam / Karar / Alternatifler / Sonuçlar / Durum

---

## ADR-01 — Tenant Hiyerarşisi: ltree (PostgreSQL)

**Bağlam:** 4 seviye (Organization → Tenant → Sub-tenant → Workspace) + Tomofil-ölçek federasyon (12 tesis × 4 kıta).
**Karar:** PostgreSQL **ltree** tipi + GiST index. Her satırda `tenant_path ltree` kolonu (örn. `tomofil.eu.berlin.rd_team`).
**Alternatifler:** (a) Materialized path string + LIKE — index zayıf; (b) Closure table — yazım maliyeti 3x; (c) Adjacency list — recursive CTE her sorguda.
**Sonuçlar:** Hızlı subtree query (`@>`, `<@`), index destekli, RLS policy'sinde doğrudan kullanılabilir. Postgres-lock-in kabul ediliyor (zaten Postgres-only kararı var).
**Durum:** ✅ Kabul

---

## ADR-02 — Veri İzolasyonu: Postgres RLS + App-Layer Defense in Depth

**Bağlam:** Tek DB'de çok kiracı; sızıntı = ürün ölümü.
**Karar:** **DB seviyesinde RLS asıl bariyer** (her sorgu `current_setting('app.tenant_path')` ile filtrelenir). App seviyesinde ikinci kontrol (middleware tenant context). İki katman zorunlu.
**Alternatifler:** (a) Sadece app-layer — bir bug=tüm veri sızar; (b) Tenant per schema — 1000+ tenant'ta migration cehennemi; (c) Tenant per DB — Enterprise+ için ileride opsiyon.
**Sonuçlar:** Otomatik test suite: "RLS bypass test" her PR'da. Connection pool tenant context'i sıfırlamalı (PgBouncer transaction mode dikkat).
**Durum:** ✅ Kabul

---

## ADR-03 — Event Bus: NATS JetStream

**Bağlam:** Modüller arası asenkron iletişim (KPI değişti → dashboard refresh, OKR güncellendi → cascade), audit log streaming.
**Karar:** **NATS JetStream**. Kafka'ya göre 1/10 operasyonel maliyet; Redis Streams'e göre durable + replay.
**Alternatifler:** (a) Kafka — Tomofil ölçeği için overkill, K8s'de ağır; (b) Redis Streams — durable garanti zayıf; (c) RabbitMQ — ölçek limitleri; (d) Postgres LISTEN/NOTIFY — sadece dev.
**Sonuçlar:** Cloud-agnostic (NATS her yerde container), HA cluster 3-node, JetStream durable subject'leri tenant_path ile prefixlenir.
**Durum:** ✅ Kabul

---

## ADR-04 — API Protokolü: REST + OpenAPI 3.1 (Mobile/3rd Party) + tRPC İç Web

**Bağlam:** Web (Next.js), Mobile (Expo), 3rd party entegrasyon hepsi API tüketecek.
**Karar:** **Public API = REST + OpenAPI 3.1** (FastAPI otomatik üretir). **Next.js ↔ FastAPI iç çağrılar = REST** (tRPC'ye gitmiyoruz — backend Python, tRPC TS-only). GraphQL yok.
**Alternatifler:** (a) GraphQL — N+1 ve cache karmaşası; (b) tRPC — sadece TS backend'de mantıklı; (c) gRPC — browser desteği zayıf.
**Sonuçlar:** OpenAPI'den Mobile + Web SDK otomatik üretilir (openapi-typescript). Versiyon: URL path (`/api/v1/...`).
**Durum:** ✅ Kabul

---

## ADR-05 — Frontend State: TanStack Query (server) + Zustand (client)

**Bağlam:** Next.js App Router + RSC + dinamik dashboard'lar.
**Karar:** **Server state = TanStack Query** (cache, invalidation, optimistic update). **Client state = Zustand** (UI toggle, modal, filtre). Redux yok.
**Alternatifler:** (a) Redux Toolkit + RTK Query — boilerplate ağır; (b) Jotai — atom mental model takım için yeni; (c) sadece Context — performans dipte.
**Sonuçlar:** Form state için React Hook Form. URL state için `nuqs`.
**Durum:** ✅ Kabul

---

## ADR-06 — BFF Katmanı: Yok (Next.js Route Handler yeterli)

**Bağlam:** Web özel veri shape'i lazım olursa.
**Karar:** **Ayrı BFF servisi YOK.** Next.js Route Handler / Server Action gerektiğinde FastAPI'yi sarar. Mobile direkt FastAPI'ye konuşur (token üzerinden).
**Alternatifler:** Ayrı Node BFF — bir servis daha = operasyonel maliyet.
**Sonuçlar:** Web'e özel agregasyon ihtiyacı çıkarsa Next.js route handler'da çözülür; backend bozulmaz.
**Durum:** ✅ Kabul

---

## ADR-07 — Bölge Topolojisi: Multi-Region Active-Passive (MVP), Active-Active (Faz 5+)

**Bağlam:** Enterprise SLA 99.9%, AB GDPR data residency.
**Karar:** **MVP = Active-Passive** (primary EU, warm standby). Postgres logical replication. RPO 5dk, RTO 30dk.
**Alternatifler:** Active-Active çok-bölge — CRDT/conflict resolution maliyeti MVP'yi 6 ay uzatır.
**Sonuçlar:** Enterprise+ müşteri active-active isterse Faz 5+ roadmap'inde.
**Durum:** ✅ Kabul

---

## ADR-08 — Şifreleme Anahtar Yönetimi: HashiCorp Vault (Self-Host)

**Bağlam:** Encryption at rest + secrets + cloud-agnostic kuralı.
**Karar:** **Vault self-host** (KMS-agnostic). Her bulut KMS'i Vault'un seal mechanism'i olarak kullanılır (auto-unseal). Uygulama hep Vault'la konuşur.
**Alternatifler:** AWS KMS / GCP KMS direkt — bulut lock-in.
**Sonuçlar:** Vault HA cluster 3-node K8s'de. Transit secrets engine ile app-level field encryption.
**Durum:** ✅ Kabul

---

## ADR-09 — Çok-Kiracı Lisans Denetimi: Runtime Policy (OPA)

**Bağlam:** Tenant admin modül aktif/pasif yapar; paket-tier farkı runtime'da denetlenmeli.
**Karar:** **Open Policy Agent (OPA)** sidecar. Her API çağrısı OPA'ya sorulur: "tenant X, paket Y, modül Z aktif mi, kullanıcı U yetkili mi?" Yanıt < 5ms.
**Alternatifler:** Hard-coded `if` zinciri — değişikliğe kapalı; Casbin — Rego kadar olgun değil.
**Sonuçlar:** Lisans/paket değişikliği policy bundle deploy'u, kod deploy'u değil.
**Durum:** ✅ Kabul

---

## ADR-10 — Audit Log: Append-Only + WORM (NATS → S3 + Postgres Partition)

**Bağlam:** EFQM, COSO ERM, SOC2 hazırlığı denetim izi şart.
**Karar:** Her domain event NATS'a basılır → 2 hedef: (1) **Postgres partitioned tablo** (90 gün, sorgu için), (2) **S3 WORM bucket** (7 yıl, immutable).
**Alternatifler:** Sadece DB — disk şişer; sadece S3 — sorgu zor.
**Sonuçlar:** Partition rotate aylık; eski partition S3'e dump → drop.
**Durum:** ✅ Kabul

---

## ADR-11 — AI Erişimi: LiteLLM Proxy Tek Kapı

**Bağlam:** Claude + OpenAI + yerel model (Ollama/vLLM); tenant başına policy.
**Karar:** Hiçbir servis doğrudan LLM SDK'sı kullanmaz. **LiteLLM proxy** üzerinden geçer. Tenant başına: model whitelist, rate limit, redaction (PII), cost cap.
**Alternatifler:** Direkt SDK — kontrol yok, audit yok.
**Sonuçlar:** Enterprise+ "verim AB'den çıkmasın" derse → policy ile yalnız yerel/AB model.
**Durum:** ✅ Kabul

---

## ADR-12 — i18n: next-intl + Veri-Seviyesi Lokalizasyon

**Bağlam:** 23 dil, RTL, kullanıcı içerikleri (OKR adı vs.) çok dilli olabilir.
**Karar:** UI string = **next-intl** (ICU MessageFormat). Kullanıcı içeriği = `translatable_field` JSONB (`{tr: ..., en: ..., ar: ...}`).
**Alternatifler:** i18next — App Router uyumu zayıf; ayrı çeviri tablosu — JOIN cehennemi.
**Sonuçlar:** RTL için Tailwind `rtl:` variant. Tarih/sayı: `Intl` API.
**Durum:** ✅ Kabul

---

## ADR-13 — Test Stratejisi: Test Piramidi + Tenant İzolasyon Suite

**Bağlam:** RLS bug = ürün ölümü.
**Karar:** Unit (Vitest/pytest) ≥ %70 / Integration (Testcontainers Postgres) ≥ %50 kritik path / E2E (Playwright) sadece kabul testi yolları. **Ayrıca: "Tenant Isolation Suite"** her PR'da çalışır — 2 tenant yaratır, çapraz erişim dener, 0 sızıntı bekler.
**Alternatifler:** %100 coverage hedefi — boş çabalama.
**Sonuçlar:** CI'da test suite < 10dk hedef.
**Durum:** ✅ Kabul

---

## ADR-14 — Migration: Alembic + Zero-Downtime Pattern

**Bağlam:** 4 saat bakım penceresi Enterprise için kabul edilemez.
**Karar:** Alembic + **expand-contract pattern**: 1) kolon ekle nullable, 2) çift yaz, 3) backfill, 4) okuma cut-over, 5) eski kolon drop. Forward-only.
**Alternatifler:** Downgrade script'leri — prod'da uygulanmıyor zaten.
**Sonuçlar:** Her migration için checklist; breaking schema değişikliği 2 deploy.
**Durum:** ✅ Kabul

---

## ADR-15 — Soft Delete + Audit: `deleted_at` Sütunu, Hard Delete Yok

**Bağlam:** KURALLAR-MASTER §3 zaten zorunlu.
**Karar:** Her domain tablosunda `deleted_at timestamptz NULL`. Partial index `WHERE deleted_at IS NULL`. RLS policy delete'i de filtreler.
**Alternatifler:** `is_active boolean` — zaman bilgisi yok; ayrı archive tablosu — JOIN karmaşası.
**Sonuçlar:** Hard delete sadece GDPR "right to be forgotten" job'ında, anonymize tercih.
**Durum:** ✅ Kabul

---

## ADR-16 — Feature Flag: GrowthBook Self-Host

**Bağlam:** Faz geçişlerinde modül kademeli açılır; A/B test ilerleyen fazda.
**Karar:** **GrowthBook self-host** (open source). Tenant/paket/kullanıcı boyutunda flag.
**Alternatifler:** LaunchDarkly — SaaS lock-in + maliyet; Unleash — UI zayıf; env var — runtime yok.
**Sonuçlar:** SDK Next.js + FastAPI. Flag tanımları Git'te.
**Durum:** ✅ Kabul

---

## ADR-17 — Domain Event Modeli: Outbox Pattern

**Bağlam:** "DB yazıldı ama event basılmadı" tutarsızlığı.
**Karar:** Her domain yazımı + outbox tablo INSERT aynı transaction'da. Ayrı relay (Debezium veya custom poll) outbox → NATS.
**Alternatifler:** İki-fazlı commit — karmaşık; en iyi çaba event — tutarsızlık.
**Sonuçlar:** At-least-once delivery; consumer idempotent olmalı (idempotency key zorunlu).
**Durum:** ✅ Kabul

---

## ADR-18 — Monorepo Tooling: Turborepo + pnpm + uv (Python)

**Bağlam:** apps/web (Next), apps/mobile (Expo), apps/api (FastAPI), packages/shared (TS types, OpenAPI client).
**Karar:** **Turborepo** task graph + **pnpm** workspace + **uv** Python paket yönetimi. Python uygulamaları monorepo içinde `apps/api/` ama kendi `pyproject.toml`.
**Alternatifler:** Nx — kurulum ağır; Bazel — overkill; ayrı repo'lar — versiyon sync acısı.
**Sonuçlar:** CI cache ile sadece etkilenen paket build edilir.
**Durum:** ✅ Kabul

---

## Özet Tablo

| # | Konu | Karar |
|---|------|-------|
| 01 | Tenant path | Postgres ltree |
| 02 | İzolasyon | RLS + app-layer (defense in depth) |
| 03 | Event bus | NATS JetStream |
| 04 | API | REST + OpenAPI 3.1 |
| 05 | FE state | TanStack Query + Zustand |
| 06 | BFF | Yok — Next.js Route Handler |
| 07 | Bölge | Active-Passive (MVP) |
| 08 | Secrets | Vault self-host |
| 09 | Lisans | OPA policy |
| 10 | Audit | NATS → Postgres partition + S3 WORM |
| 11 | AI | LiteLLM proxy |
| 12 | i18n | next-intl + JSONB |
| 13 | Test | Piramit + Tenant Isolation Suite |
| 14 | Migration | Alembic expand-contract |
| 15 | Delete | Soft delete (deleted_at) |
| 16 | Flag | GrowthBook self-host |
| 17 | Event | Outbox pattern |
| 18 | Monorepo | Turborepo + pnpm + uv |

---

## Onay

Onaylanırsa **D3 — Domain Model (DDD bounded contexts + entities)** yazılır.

Kullanıcı onayı: ☐ Onaylandı ☐ Revizyon istendi
