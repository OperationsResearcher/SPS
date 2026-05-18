# P6 — TEST STRATEJİSİ · TOMOFİL KABUL PROTOKOLÜ
> Tarih: 2026-05-16 · Durum: TASLAK · Bağımlılık: D1 (kabul kriteri), D2 (ADR-13), D6 (RLS)

---

## 1. Test Felsefesi

1. **Hızlı geri bildirim > kapsam yüzdesi.** %70 hızlı koşan testler, %95 yavaş testlerden iyidir.
2. **Tenant izolasyonu hayat-memat.** Her PR'da çalışan ayrı suite, taviz yok.
3. **Test data = production data değil.** Sentetik veri (Faker + Tomofil seed).
4. **Flaky test = bug.** Kuarantine yok; düzelt veya sil.
5. **Test = dokümantasyon.** Test isimleri davranışı anlatır.

---

## 2. Test Piramidi

```
              ╱╲
             ╱E2E╲              ~50 senaryo (Playwright)
            ╱──────╲             "kabul testi yolları"
           ╱ Contract╲           ~80 (OpenAPI + Pact)
          ╱──────────╲
         ╱Integration ╲          ~400 (Testcontainers)
        ╱──────────────╲          "modül × DB × event"
       ╱  Component UI  ╲        ~250 (Vitest + RTL + Storybook)
      ╱──────────────────╲
     ╱       Unit         ╲     ~2500 (pytest + Vitest)
    ╱──────────────────────╲     "saf fonksiyon, domain"
                ⊥
       ╔════════════════╗
       ║ Tenant Isolation║  ← AYRI suite, her PR'da, %100 geçmeli
       ║   Suite (TIS)   ║
       ╚════════════════╝
```

### 2.1 Hedef Kapsam
| Katman | Hedef |
|--|--|
| Unit (backend) | Domain layer %85+, app layer %70+ |
| Unit (frontend) | Utils/hook %80+, component %60+ |
| Integration | Kritik path %95 (auth, RLS, tenant, billing) |
| Component (UI) | Tasarım sistemi %90+ (Storybook + Chromatic) |
| Contract | OpenAPI'deki her endpoint en az 1 happy + 1 sad |
| E2E | 12 kritik journey (P3 §2) |
| TIS | 8 zorunlu (D6 §10) |

---

## 3. Araç Yığını

| Katman | Araç |
|--|--|
| Unit (Python) | pytest + pytest-asyncio + hypothesis (property test) |
| Unit (TS) | Vitest |
| Integration (Python) | pytest + Testcontainers (Postgres/NATS/Redis) |
| Component (React) | Vitest + Testing Library + MSW |
| Visual regression | Chromatic (Storybook bağlı) |
| Contract | Schemathesis (OpenAPI fuzz) + Pact (consumer-driven) |
| E2E | Playwright (web) + Maestro (mobile) |
| Load | k6 (Grafana ekosistem) |
| Security | OWASP ZAP scheduled, Burp manual, semgrep static |
| Accessibility | axe-core (CI) + Pa11y (smoke) |
| Mutation | mutmut (Python) — kritik domain için opsiyonel |

---

## 4. Test Ortamları

| Ortam | Amaç | Veri |
|--|--|--|
| local | Geliştirici makinası | docker-compose, faker seed |
| CI ephemeral | PR test koşumu | Testcontainers, izole |
| dev cluster | Trunk doğrulama | merge sonrası, mock LLM |
| staging | Pre-prod, demo | Tomofil seed + sentetik tenant'lar |
| sandbox | Sales demo / POC | müşteri-izole tenant, refresh haftalık |
| production | Müşteri | gerçek veri |

---

## 5. Tenant Isolation Suite (TIS) — Hayat-Memat

### 5.1 Test Listesi (her PR'da)
1. **Cross-tenant SELECT reddi** — A user, B record sorgular → 0 satır
2. **Cross-tenant INSERT reddi** — A user, B path INSERT → 403/exception
3. **Cross-tenant UPDATE reddi** — A user, B record UPDATE → 0 satır etkilenir
4. **Cross-tenant DELETE reddi** — aynı
5. **Sub-tenant escalation reddi** — child user parent path okuyamaz
6. **Federation downward izin** — org_admin alt tenant'ı görür (positive test)
7. **Soft-delete invisibility** — `deleted_at IS NOT NULL` SELECT'te gelmez
8. **Connection pool reset** — PgBouncer transaction mode `app.tenant_path` reset
9. **Audit immutability** — UPDATE/DELETE `audit.events` reddedilir
10. **Outbox idempotency** — Aynı event_id 2 kez → consumer 1 kez işler
11. **JWT tenant_path tampering** — manipüle edilmiş claim → 403
12. **OPA deny override** — RLS izin verse de OPA deny → 403

### 5.2 Çalışma Kuralları
- main branch'e merge engelleyici (required check)
- < 2 dakika koşmalı (paralel)
- Yeni tenant-aware tablo eklenirse 1-12'nin her biri otomatik kapsar (parametrized)

---

## 6. CI Pipeline

```
PR open / push
  ├─ Lint (ESLint + Ruff + Black) — 30s
  ├─ Typecheck (TS + mypy) — 60s
  ├─ Unit (parallel, sharded) — 90s
  ├─ Component UI (Vitest + Storybook build) — 90s
  ├─ Integration (Testcontainers, sharded) — 180s
  ├─ Tenant Isolation Suite — 120s
  ├─ Contract (Schemathesis subset) — 60s
  ├─ Build (Turborepo cache, sadece etkilenen) — 60-180s
  └─ Preview deploy (PR namespace) — 90s

Total target: < 12 dakika
```

**Nightly:**
- Full Schemathesis fuzz (1h)
- Playwright E2E full suite (30dk)
- k6 load smoke (15dk)
- OWASP ZAP scan (1h)
- Mutation test kritik domain (2-3h)
- Chromatic visual diff

---

## 7. Test Verisi Stratejisi

### 7.1 Sentetik Veri
- **Faker** + custom provider (TR isim, KPI adı, OKR objective)
- **Builder pattern:** `OrgBuilder().with_tenants(3).with_users(50).build()`
- Deterministik seed (test reproducibility)

### 7.2 Tomofil Fixture
- `ops/seeds/tomofil.sql` — kapsamlı seed (12 tesis, 5000 KPI, 24 OKR, 50 risk)
- Test-only flag: production'a yüklenemez
- "Demo tenant" sandbox'ta haftalık refresh

### 7.3 Veri Hassasiyeti
- Prod veri test ortamlarına asla kopyalanmaz
- "Production-like" load test: sentetik, mass-generated

---

## 8. Tomofil Kabul Protokolü (MVP DoD)

### 8.1 Yaklaşım
- D1 §6'daki 11 madde = **11 kabul testi**
- Her madde için: otomatik test + insan onayı
- Sign-off: PM + CTO + ürün liderliği (Tomofil hayali müşteri sahibi)

### 8.2 11 Madde — Test Matrisi

| # | Tomofil maddesi | Otomatik test | Manuel onay | Stage-Gate |
|--|--|--|--|--|
| 1 | Organization "Tomofil Group N.V." yaratıldı | API integration | UI smoke | G1 |
| 2 | 12 tesis sub-tenant federe | API + RLS test | Org chart UI | G2 |
| 3 | 4 kıta region workspace | API | UI tree | G2 |
| 4 | H1-H6 + EFQM baseline 579 | Integration | Strategist gözden geçir | G2 |
| 5 | 24 OKR 5 seviye cascade | E2E + cascade check | Sample 5 OKR | G3 |
| 6 | Hoshin X-Matrix + Catchball 5 kanal | Integration | Workshop simülasyon | G3 |
| 7 | 14 E2E süreç RACI+CMMI | E2E + assessment | Sample 3 süreç | G3 |
| 8 | 4 senaryo + 8 EWS + karar ağacı | Integration | Senaryo planı incele | G3 |
| 9 | COSO ERM 50+ risk + KRI eşik | Integration + alert | Heat map | G4 |
| 10 | TCFD + SBTi hedef vs gerçek | Integration | Rapor PDF | G4 |
| 11 | AI Concierge stratejik soru doğru | E2E + golden answer | İnsan değerlendirme | G4 |

### 8.3 Golden Answer Test (AI için)
- 30 önceden hazırlanmış soru + beklenen kavramsal cevap
- LLM-as-judge skor (Claude tarafından değerlendirme) + insan spot-check
- Geçer: %85+ skor

### 8.4 Performance Kabul
| Metrik | Hedef | Test |
|--|--|--|
| Tomofil dashboard p95 | <1.5s | k6 |
| 5000 KPI listele | <2s | k6 |
| 24 OKR cascade render | <1s | Playwright |
| Audit log son 90 gün sorgu | <500ms | Integration |
| Cross-tenant probing | 0 sızıntı | TIS |

---

## 9. QA Rolü

- **F1-F2:** Geliştiriciler kendi testlerini yazar (dedicated QA yok)
- **F3:** İlk QA Engineer (1) — test stratejisi, otomasyon, kabul testi
- **F4:** + Manual QA / Test Lead (1) — Tomofil kabul testi koordinasyon
- **Y2:** QA Lead + 2 QA Eng

**QA değil; "Quality Engineer"** — geliştiriciye test yaptırmak yerine, kalite altyapısını sahiplenir.

---

## 10. Hata Geri Bildirim Döngüsü

- Prod bug yakalandı → Linear/Jira issue → root cause analysis → test eksiği var mı?
- Eksikse: regresyon testi yaz, sonra fix → "test first"
- Postmortem'lerde test-eksikliği ayrı kategori

---

## 11. Test Metrikleri (gözleyeceğimiz)

| Metrik | Hedef |
|--|--|
| CI baseline duration | <12 dk |
| CI flake rate | <%1 |
| Coverage (domain) | >85% |
| Escaped bug (prod sev1/ay) | <0.5 |
| Test-bug ratio (yeni test yazımı / kapatılan bug) | >1.5 |
| TIS pass rate | %100 (taviz yok) |

---

## 12. Açık Sorular
- OS-1: Chromatic (~$149/ay) F1 mı F2 mi? — Önerim: F2 (UI istikrar kazandıktan sonra)
- OS-2: Mutation test gerekli mi? — Önerim: opsiyonel, sadece kritik domain
- OS-3: Müşteri-tarafı sandbox test (POC sırasında) ayrı tooling? — Önerim: aynı staging, sadece data izole
- OS-4: Performance bütçesi (Lighthouse) PR'da blocking mi? — Önerim: warning F1, blocking F3
