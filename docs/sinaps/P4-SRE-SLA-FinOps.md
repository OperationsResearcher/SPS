# P4 — SRE · SLA/SLO · RUNBOOK · DR/BCP · CAPACITY · FINOPS
> Tarih: 2026-05-16 · Durum: TASLAK · Bağımlılık: D2, D5

---

## 1. SLA Sözleşme (Müşteriye Söz)

### 1.1 Uptime SLA
| Paket | Aylık uptime | Credit |
|--|--|--|
| Kokpitim Starter/Pro | 99.5% | — (best effort) |
| Sinaps Enterprise | 99.9% | <99.9 → %10, <99.5 → %25 |
| Sinaps Enterprise+ | 99.95% (custom) | <99.95 → %15, <99.5 → %50 |

**Exclude:** Planlı bakım (max 4h/ay, 72h önceden bildirim, off-peak), force majeure, müşteri kaynaklı.

### 1.2 Yanıt Süresi SLA (Support — P1 §4 ile uyumlu)
- P1: 1h (Ent+), 4h (Ent)
- P2: 4h / 1 iş günü
- P3: 1 iş günü / 2 iş günü

### 1.3 Resolution Hedefleri (best effort)
- P1: 4h
- P2: 1 iş günü
- P3: 5 iş günü

### 1.4 Veri Kaybı
- RPO ≤ 5 dakika
- RTO ≤ 30 dakika

---

## 2. SLO (İç Hedefler)

### 2.1 Kullanıcı Yolculuğu SLO'ları
| Yolculuk | SLI | Hedef (28-day rolling) |
|--|--|--|
| Login | success rate | 99.95% |
| Login | p95 latency | <1.0s |
| Dashboard load | p95 latency | <1.5s |
| API CRUD | p95 latency | <250ms |
| API CRUD | error rate | <0.1% |
| Search | p95 latency | <800ms |
| AI Concierge | p95 first-token | <2.0s |
| Document upload | success | 99.9% |
| Webhook delivery | success (24h retry) | 99.5% |
| Background job | completion | 99.5% |

### 2.2 Hata Bütçesi
- 99.9% → aylık 43dk 49sn izinli kesinti
- %50 tüketildi → release hızı yarıya iner
- %75 tüketildi → release dondurulur, yalnız bug-fix
- %100 → "war room" + postmortem zorunlu

---

## 3. Observability Yığını (ADR-13 detay)

| Sinyal | Araç | Saklama |
|--|--|--|
| Trace | OTEL → Tempo | 14 gün |
| Log | OTEL → Loki | 30 gün, S3 arşiv 1 yıl |
| Metric | Prometheus → Mimir | 90 gün, downsample 2 yıl |
| Profile | Pyroscope | 7 gün |
| Synthetic | Grafana k6 | sürekli, 5dk freq |
| Real User | Grafana Faro (web) + Expo SDK (mobile) | 30 gün |
| Uptime | Statuspage + external prober | sürekli |

**Dashboard'lar:**
- Service overview (her servis için template)
- Tenant health (her tenant'ın p95, error, request hacmi)
- Customer-facing status page (genel)
- Business KPI (DAU, ARR, churn — Grafana iş paneli)

---

## 4. Alerting Politikası

### 4.1 Severity Mapping
| Sev | Kim alır | Kanal | SLA |
|--|--|--|--|
| Critical | On-call primary + manager | PagerDuty + telefon | 5dk ack |
| Warning | On-call primary | Slack channel | 30dk ack |
| Info | Channel | Slack channel | — |

### 4.2 Alarm Örnekleri
- p95 latency > SLO × 1.5 — 5dk sürekli → Critical
- Error rate > 1% — 5dk → Critical
- Disk %85 — Warning · %95 → Critical
- Cert expiry < 14 gün → Warning
- Backup last_success > 25h → Critical
- RLS bypass test failed in prod → Critical (P0)

### 4.3 Anti-spam
- Alert deduplication 10dk
- Silencer for planned maintenance
- Runbook URL her alarm yükünde

---

## 5. On-Call

### 5.1 Rotasyon
- F1: 3 kişi haftalık (Mon-Mon)
- F2+: 5 kişi haftalık
- Primary + Secondary (yedek)
- Mesai sonrası uyandırma = compensation (gün izni veya ödenek)

### 5.2 Eskalasyon Zinciri
Primary (5dk) → Secondary (10dk) → Eng Manager (15dk) → CTO (30dk) → CEO (P0 only)

### 5.3 On-call Toolkit
- Runbook'lar (ops/runbooks/)
- Read-only prod DB erişim
- kubectl ile prod cluster
- LogQL/PromQL şablonları
- Customer comms şablonları

---

## 6. Runbook Seti (F1 sonu — 12 runbook)

| RB | Senaryo |
|--|--|
| RB-01 | Postgres primary down — failover |
| RB-02 | RLS bypass tespit edildi |
| RB-03 | NATS JetStream cluster split-brain |
| RB-04 | Keycloak login %100 fail |
| RB-05 | LiteLLM proxy unreachable |
| RB-06 | S3 endpoint down (cloud-specific) |
| RB-07 | Disk dolması — Postgres / Loki |
| RB-08 | Cert renewal failed |
| RB-09 | Deploy rollback (ArgoCD) |
| RB-10 | Tenant data leak suspicion |
| RB-11 | DDoS / rate limit floods |
| RB-12 | Backup restore drill |

Her runbook formatı: **Tetik · Triage · Mitigation · Verification · Communication · Postmortem trigger**.

---

## 7. Backup & DR

### 7.1 Backup Politikası
| Veri | Yöntem | Sıklık | Saklama |
|--|--|--|--|
| Postgres | WAL-G continuous + nightly base | 5dk RPO | 30 gün hot, 1 yıl cold (S3 Glacier) |
| Postgres | Logical (pg_dump) | Haftalık | 6 ay |
| S3 documents | Cross-region replication | Sürekli | versiyon 90 gün |
| S3 audit WORM | Object Lock | INSERT-time | 7 yıl |
| Vault | Snapshot + Raft | 6 saat | 30 gün |
| Keycloak | DB içinde + export | Haftalık | 6 ay |
| Helm release | GitOps repo (ArgoCD) | Her deploy | sürekli |

### 7.2 DR Senaryoları
**S1 — Primary region kaybı (RTO 30dk):**
1. Standby region promote (Postgres logical replica → primary)
2. DNS swap (Route53 / Cloud DNS)
3. NATS failover (standby cluster)
4. App servisleri zaten standby'da scale up
5. Smoke test + müşteri bildirim

**S2 — Veri silme/yanlışlık (RPO 5dk):**
1. PITR (Point-in-Time Restore) yeni instance
2. Sorunlu satırlar bulunur, target DB'ye merge
3. Audit log ile doğrula

**S3 — Cloud provider kaybı (1-2 gün):**
- Helm chart başka buluta apply (önceden test edilmiş)
- Backup S3 → yeni cloud blob restore
- DNS güncelleme
- Müşteriye 24h heads-up

### 7.3 DR Drill Takvimi
- Postgres failover: aylık
- Cross-region restore: çeyreklik
- Tam cloud taşıma: yıllık (Tabletop + 1 ortamda gerçek deneme)

---

## 8. Capacity & Sizing Modeli

### 8.1 Tek Tenant Tahmini Yük
| Metrik | KOBİ (Kokpitim Pro) | Mid Enterprise | Tomofil ölçeği |
|--|--:|--:|--:|
| Kullanıcı | 50 | 500 | 12.000 |
| KPI sayısı | 50 | 500 | 5.000 |
| KPI ölçüm/ay | 200 | 3.000 | 40.000 |
| OKR sayısı | 30 | 300 | 3.500 |
| Audit event/gün | 500 | 8.000 | 120.000 |
| Document GB | 5 | 50 | 800 |
| Aylık API request | 50K | 800K | 12M |

### 8.2 Altyapı Sizing
- **Postgres:** 100 tenant ≈ 200 GB DB, 8 vCPU / 32 GB RAM yeterli. 1000 tenant → shard veya read replica
- **Redis:** 2 GB her zaman yeterli (cache + rate limit)
- **NATS:** 3-node, 4 GB RAM her, JetStream 200 GB disk
- **App pod:** her tenant ≈ 10 r/s peak; 1 pod 200 r/s; HPA hedef CPU %70
- **Cost target (Enterprise tenant):** $50-80/ay infra (Y1), $30-50 (Y2 optimizasyon)

### 8.3 Yatay Ölçek Tetikleri
- Postgres connection pool %70 → read replica ekle
- Postgres CPU %60 sürekli → vertical scale veya partition strategy
- 1000+ tenant → tenant pool sharding (her shard ayrı DB instance)

---

## 9. FinOps

### 9.1 Maliyet Modeli (Y1 tahmini, GCP baz)
| Kalem | Aylık | Yıllık |
|--|--:|--:|
| Compute (10 node, e2-standard-4) | $1,400 | $16.8K |
| Postgres (Cloud SQL HA) | $900 | $10.8K |
| Object storage (S3/GCS) | $200 | $2.4K |
| Egress | $300 | $3.6K |
| Observability (self-host Grafana) | $200 | $2.4K |
| LLM API (LiteLLM passthrough) | $800 | $9.6K |
| Keycloak/Vault/NATS run-cost | $400 | $4.8K |
| Backup/DR cross-region | $250 | $3K |
| **Toplam (10-20 Ent tenant)** | **~$4.5K** | **~$54K** |

### 9.2 Kontrol Mekanizmaları
- Budget alert: $5K (warn), $6K (critical) → CFO
- Tenant başına cost-per-tenant raporu (haftalık)
- LLM cost cap policy (ADR-11) — tenant başına aylık limit
- Idle dev/staging cluster gece kapatma (cron)
- Reserved capacity (1 yıl) prod baseline için → %30 indirim

### 9.3 Unit Economics
- Hedef gross margin: %75 (SaaS standart)
- Customer infra cost / ACV oran: < %15

---

## 10. CI/CD Operasyonel

### 10.1 Release Cadansı
- main → staging: her merge, otomatik
- staging → production: manuel onay (Eng Manager + CSM heads-up)
- Hotfix: cherry-pick + fast-track approval

### 10.2 Deployment Strategy
- Blue/Green (web, api) — ArgoCD ile
- Canary %5 → %50 → %100, otomatik rollback SLO breach'inde
- DB migration: expand-contract (ADR-14)
- Feature flag (GrowthBook) yeni özellik için default off

### 10.3 Change Management
- Production change: ArgoCD PR + reviewer
- DB schema change: migration PR + DBA review + drill
- Vault policy change: 2-person rule

---

## 11. Açık Sorular
- OS-1: PagerDuty (~$200/kullanıcı/yıl) mı Grafana OnCall (free) mı? — Önerim: Grafana OnCall F1, gerekirse upgrade
- OS-2: Status page açık mı (Statuspage.io) yoksa yalnız Enterprise mı görür?
- OS-3: SLA credit hesabı otomatik mi manuel mi? — Önerim: F1'de manuel, F3'te otomatik
- OS-4: Multi-region active-active'e ne zaman geçiş? — Önerim: NRR > 110% olunca veya AB regülasyon zorlarsa
