# SİNAPS — KARAR GÜNLÜĞÜ
> Tek gerçek kaynak: tüm Faz-0 kararları kilitli
> Tarih: 2026-05-16
> Onaylayan: Kurucu (tüm açık sorularda tavsiyeyi onayladı)
> 64 / 64 karar kapatıldı

---

## A. MİMARİ & TEKNİK

| Kod | Karar | Tarih |
|--|--|--|
| A1.1 | tenant_path = PostgreSQL **ltree** + GIST index | 2026-05-16 |
| A1.2 | RLS **DB seviyesi (asıl) + App seviyesi (ikincil)** — defense in depth | 2026-05-16 |
| A1.3 | Event bus = **NATS JetStream** (3-node HA) | 2026-05-16 |
| A1.4 | Multi-region = **Active-Passive MVP** · Active-Active F5+ değerlendirme | 2026-05-16 |
| A1.5 | KPI Master = STRATEGY context owner, paylaşımlı şema | 2026-05-16 |
| A1.6 | ETL detayları P2'de yeterli; kod F2'de yazılır | 2026-05-16 |
| A2.1 | FE state = **TanStack Query (server) + Zustand (client)** | 2026-05-16 |
| A2.2 | BFF YOK — Next.js Route Handler yeterli | 2026-05-16 |
| A2.3 | Mobile = **React Native + Expo** | 2026-05-16 |
| A3.1 | Secrets = **HashiCorp Vault self-host** | 2026-05-16 |
| A3.2 | Lisans/yetki = **OPA sidecar** + Rego policy | 2026-05-16 |
| A3.3 | Feature flag = **GrowthBook self-host** | 2026-05-16 |
| A3.4 | Monorepo = **Turborepo + pnpm + uv** | 2026-05-16 |

## B. ÜRÜN & MVP

| Kod | Karar |
|--|--|
| B1 | MVP kapsam dışı listesi onaylı (ERP/forecast/marketplace/offline/AI-co-author/white-label = F5+) |
| B2 | Hoshin X-Matrix = Enterprise paketinde zorunlu |
| B3 | Stage-Gate = Enterprise+ only (Pro sade kalır) |
| B4 | ESG Pro'da "light", tam ESG (TCFD/SBTi/Carbon) Enterprise |

## C. MARKA

| Kod | Karar |
|--|--|
| C1 | **Yeni "Kokpit Group A.Ş." varlığı kurulur + Kokpitim devri**; hukuk danışmanlığı başlat |
| C2 | Sinaps tagline = EN birincil + TR/DE/FR/AR lokalize varyantlar |
| C3 | Görsel kimlik = **Dış marka stüdyo (€20-40K bütçe)** |
| C4 | "by Kokpit Group" endorsement = sadece login + footer + about |
| C5 | Enterprise+ white-label = F5+ değerlendirme, şimdi karar yok |

## D. FİYATLANDIRMA & GTM

| Kod | Karar |
|--|--|
| D1 | AB B.V. = F3'te proaktif kuruluş |
| D2 | Kokpitim free trial = **14 gün** başla, conversion verisi sonrası revize |
| D3 | Sinaps freemium = **YOK**, POC modeli |
| D4 | Sinaps TR fiyatı = € baz, TL kura göre hesaplanır (sabitlenmez) |
| D5 | Partner komisyon = **Referral %15 / Reseller %25 / Sistem entegratörü görüşmeli** |
| D6 | Fiyat seviyeleri (₺350/₺850 KOBİ, €24K/€60K Enterprise) = **başlangıç olarak onaylı**, müşteri görüşmesi sonrası kalibre |

## E. ETL

| Kod | Karar |
|--|--|
| E1 | Migration = **Implementation Pack'e dahil**; bağımsız €5K eklenti |
| E2 | Çoklu Kokpitim tenant = default ayrı, müşteri tercihiyle birleştirilebilir |
| E3 | Keycloak import sırasında **MFA reset zorunlu** |
| E4 | 30 gün sonra Kokpitim verisi = **müşteri onayıyla silinir**, sessiz silme yok |
| E5 | BCG/Ansoff/Proje/Görev kayıpları = **PDF arşiv yeterli**; custom modül talebi €25K+ |

## F. DESIGN & UX

| Kod | Karar |
|--|--|
| F1 | Figma team plan = F1'de açılır (€150/ay) |
| F2 | Marka studio = dış (C3 ile aynı karar) |
| F3 | SweetAlert2 Sinaps'ta **YOK**, Cortex Toast |
| F4 | Dark theme = **user preference, sistem tercihini izle** (default light, Sinaps premium dark seçenek) |

## G. SRE & FINOPS

| Kod | Karar |
|--|--|
| G1 | On-call = **Grafana OnCall F1** (free), PagerDuty F3+ değerlendirme |
| G2 | Status page = **public** (status.kokpitgroup.com) |
| G3 | SLA credit = F1 manuel, F3'te otomatikleştir |
| G4 | Uptime SLA seviyeleri (99.5/99.9/99.95) = müşteriye söylenir, iç hedef daha yüksek |

## H. GÜVENLİK & UYUM

| Kod | Karar |
|--|--|
| H1 | DPO = F1'de outsource (€600/ay), F4+ inhouse |
| H2 | Compliance platform = **Drata** |
| H3 | Bug bounty = F5+ |
| H4 | HYOK (customer key) = F5+ talep gelirse |
| H5 | AB Cloud Code of Conduct = F3'te adhere |
| H6 | SOC2 Type I = **12. ay sonu hedefi kayma yasak** (AB Enterprise satış için kritik) |

## I. TEST

| Kod | Karar |
|--|--|
| I1 | Chromatic = F2'de açılır |
| I2 | Mutation test = opsiyonel, sadece kritik domain |
| I3 | POC sandbox = aynı staging, data izole |
| I4 | Lighthouse bütçesi = F1 warning, F3 blocking |

## J. ORG & HIRING

| Kod | Karar |
|--|--|
| J1 | Y1 = TR çoğunluk + AB hire ay 4'ten |
| J2 | ESOP havuzu = %10-15 (VC sözleşmesine göre kesinleştir) |
| J3 | Maaş bandı = dahili tam açık, JD'de range yayın |
| J4 | Founding CSM = kurucular ay 6'ya kadar CS, sonra hire |
| J5 | Y1 18 kişi = **funding'e bağlı koşullu hedef** (€1.1M burn) |

## K. MOBILE & BETA

| Kod | Karar |
|--|--|
| K1 | RN+Expo (Flutter değil) — kilit |
| K2 | Mobile için ayrı brand YOK — tek "Sinaps" |
| K3 | Kokpitim mobile = Y2'de talep değerlendirmesi |
| K4 | Founding customer programı = 5 closed beta'ya Y1 ücretsiz + Y2-3 %30 indirim |
| K5 | Open beta = **15 ile başla**, CSM kapasitesi izin verirse genişlet |

## L. GLOSSARY & DOCS & ANALYTICS

| Kod | Karar |
|--|--|
| L1 | Doküman çeviri sırası = TR/EN → AR → DE → ES/FR |
| L2 | PostHog = F1 sonu açılır (event şeması erken) |
| L3 | Session replay = default **kapalı**, tenant opt-in |
| L4 | "PG" Kokpitim'de, "KPI" Sinaps'ta — paket bazlı, çakışma yok |

---

## ÖZET — KİLİTLİ TEKNİK YIĞIN

| Boyut | Karar |
|--|--|
| DB | PostgreSQL + ltree + RLS + pgvector |
| Backend | FastAPI (Python) + SQLAlchemy + Alembic |
| Frontend | Next.js 15 App Router + TS + Shadcn/ui + Tailwind + TanStack Query + Zustand |
| Mobile | React Native + Expo |
| Auth | Keycloak self-host (OIDC + RS256 + MFA) |
| Yetki | OPA sidecar |
| Secrets | Vault self-host |
| Event | NATS JetStream + Outbox pattern |
| AI | LiteLLM proxy + Claude/OpenAI/yerel |
| i18n | next-intl + JSONB translatable + 23 dil hedef |
| Observability | OTEL + Grafana (Loki/Tempo/Mimir/Pyroscope/Faro) |
| On-call | Grafana OnCall |
| Status page | Statuspage.io public |
| Feature flag | GrowthBook self-host |
| CI/CD | GitHub Actions + ArgoCD + Helm |
| Monorepo | Turborepo + pnpm + uv |
| Test | pytest + Vitest + Playwright + Schemathesis + k6 + TIS (zorunlu) |
| Analytics | PostHog self-host |
| Compliance | Drata + KVKK → GDPR → SOC2 Type I (ay 12) → ISO 27001 (ay 18) |
| Marka | Kokpit Group umbrella + Kokpitim (KOBİ) + Sinaps (Enterprise) |
| Yasal | Yeni Kokpit Group A.Ş. + Kokpitim devri + F3 AB B.V. |

---

## KİLİTLİ İŞLETİM PARAMETRELERİ

| Boyut | Değer |
|--|--|
| Faz takvimi | F0 (4-6 hf) → F1 (12 hf) → F2 (12 hf) → F3 (12 hf) → F4 (12 hf) = ~14 ay |
| Hedef GA | Y1 sonu / Y2 başı (Sinaps) |
| Y1 ekip | ~18 kişi (TR çoğunluk + AB) |
| Y1 burn | ~€1.0-1.2M |
| Y1 ARR hedef | €400K |
| Y2 ARR hedef | €2.5M |
| MVP doğrulama | Tomofil 11-madde kabul testi (G4 gate) |
| Beta | Alpha (F2 içi) → Closed (F4 başı, 5-8 müşteri) → Open (F4 sonu, 15 müşteri) |
| SLA | 99.5 (Starter/Pro) / 99.9 (Enterprise) / 99.95 (Enterprise+) |
| RPO / RTO | 5dk / 30dk |

---

## DEĞİŞİKLİK YÖNETİMİ

Bu kararlar **kilitli** olarak kabul edilir. Değişiklik isteği:
1. PR ile bu doküman güncellenir
2. Etkilenen D/P doküman(lar)ı revize edilir
3. Karar tarihi + gerekçesi eklenir
4. Major karar (mimari/yığın) değişimi → ADR olarak yeniden işlenir

---

## SONRAKI ADIM

**S0 Bootstrap** (Faz-1 öncesi, 1 hafta):

D5 §11 + F1 §2'deki 10 maddelik checklist — kararlar kilitlendiği için doğrudan uygulamaya başlanabilir.

1. `gh repo create kokpit/sinaps --private`
2. Turborepo + pnpm + uv workspace iskelet
3. `packages/config` (ESLint/Prettier/TS/Tailwind base)
4. `apps/api` minimum FastAPI + /health + OTEL
5. `apps/web` minimum Next.js + Keycloak login stub
6. `infra/docker/` multi-stage Dockerfile
7. `infra/helm/sinaps/` iskelet chart
8. `.github/workflows/ci.yml` (lint + typecheck + test + build)
9. `make dev` docker-compose stack (PG+Redis+NATS+Keycloak+Vault)
10. `python/sinaps_db` ltree + RLS test fixture

Paralel iş kolları (hukuk + tasarım + uyum):
- C1 → Hukuk danışmanı görüşmesi başlat
- C3/F2 → Marka studio brief + 3 stüdyo teklif al
- H1 → DPO outsource sözleşmesi imzala
- H2 → Drata onboarding başlat
- D1 → Müşteri görüşmesi & benchmark fiyat doğrulaması
