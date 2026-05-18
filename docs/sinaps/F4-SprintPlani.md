# FAZ 4 — RİSK + ESG + MOBILE + BETA RELEASE SPRINT PLANI
> M-RISK (tam) + M-ESG (tam) + Mobile (RN+Expo) + Open Beta + GA hazırlık
> Süre: 12 hafta (6 × 2-haftalık sprint, S19-S24)
> Tarih: 2026-05-16 · Bağımlılık: F3 G3 geçti

---

## 0. Faz-4 Hedefi

**"COSO ERM + ISO 31000 risk register, KRI eşik alarm, risk-strateji bağlama tam çalışır. ESG: TCFD raporu, SBTi hedef, karbon envanteri, BMSKA (SDG) eşleme. Mobile uygulama (iOS+Android) 12 ekranla TestFlight + Play Internal beta'da. Open beta (15 müşteri) canlı. Real Options değerleme. GA için son sertleştirme + lansman hazırlık."**

F4 sonu = **GA-ready** (General Availability). Lansman Y1 sonu / Y2 başı.

---

## 1. Kapsam

### M-RISK (5.1-5.10)
Tüm 10 alt-modül F4'te (COSO ERM, ISO 31000, register, heatmap, appetite, KRI, controls, events, link, dashboards)

### M-ESG (6.1-6.5, 6.7)
6.6 GRI/CSRD F5+'a taşındı

### Mobile (X.1)
12 ekran: Auth, Tenant picker, Today, OKR list/detail, KPI quick, Notifications, Activity, Search, Profile, AI chat, Approval inbox

### Yardımcı
3.6 Real Options · GA hazırlık (sertleştirme, dokümantasyon, marka)

---

## 2. Sprint S19 — Risk Register + COSO ERM + ISO 31000

| # | Görev | Modül |
|--|--|--|
| S19.1 | `risk.registers` + framework seçimi | 5.1 |
| S19.2 | `risk.risks` CRUD + kategori taxonomy | 5.1, 5.2 |
| S19.3 | COSO ERM framework seed (8 component) | 5.2 |
| S19.4 | ISO 31000 framework seed (principles + process) | 5.3 |
| S19.5 | Risk lifecycle (open → mitigating → accepted → closed) | 5.1 |
| S19.6 | Inherent vs Residual L×I 5x5 heatmap | 5.4 |
| S19.7 | Heatmap interactive (click → risk list) | 5.4 |
| S19.8 | `risk.appetite_statements` + 3-tier threshold | 5.5 |
| S19.9 | Risk-Strategy/Process/Initiative bağlama UI | 5.9 |
| S19.10 | Tomofil seed: 50+ risk, 6 kategori | X.6 |

**DoD:** Tomofil 50 risk yüklenir, heatmap görselleşir, risk-strateji eşlenir.

---

## 3. Sprint S20 — KRI + Controls + Risk Events + Risk Dashboards

| # | Görev | Modül |
|--|--|--|
| S20.1 | `risk.kris` + threshold + current value | 5.6 |
| S20.2 | KRI-KPI bağlama (otomatik tetikleme) | 5.6 |
| S20.3 | KRI breach event → notification + escalation | 5.6, 1.6 |
| S20.4 | `risk.controls` (preventive/detective/corrective) | 5.7 |
| S20.5 | Control effectiveness rating + owner | 5.7 |
| S20.6 | `risk.events` (gerçekleşen) + root cause | 5.8 |
| S20.7 | Lessons learned + linked KPI/process | 5.8 |
| S20.8 | Risk dashboard (heatmap + KRI trafik ışığı + top 10 risk) | 5.10 |
| S20.9 | Risk report export PDF (kurul sunumu) | X.4 |
| S20.10 | Webhook outbound: risk.escalated, kri.breached | X.3 |

**DoD:** Tomofil KRI eşik aşıldığında bildirim + escalation tam akar; risk raporu PDF.

---

## 4. Sprint S21 — ESG Plan + TCFD + SBTi + Carbon + SDG

| # | Görev | Modül |
|--|--|--|
| S21.1 | `esg.plans` + period | 6.1 |
| S21.2 | TCFD report 4-pillar form (Gov/Strategy/Risk/Metrics) | 6.2 |
| S21.3 | TCFD auto-pull (risk register + KPI'dan) | 6.2 |
| S21.4 | TCFD PDF export (yıllık rapor formatı) | 6.2 |
| S21.5 | SBTi target (Scope 1/2/3 baseline + target + reduction %) | 6.3 |
| S21.6 | SBTi progress chart (yıllar üzerinden) | 6.3 |
| S21.7 | Carbon Inventory entry (yıl × kapsam × kaynak × tonCO2e) | 6.4 |
| S21.8 | Carbon dashboard (Scope breakdown, trend) | 6.4, 6.7 |
| S21.9 | BMSKA (17 SDG) mapping + strategy referans | 6.5 |
| S21.10 | Sustainability Dashboard (TCFD+SBTi+Carbon+SDG widget'lar) | 6.7 |

**DoD:** Tomofil TCFD raporu otomatik üretilir, SBTi hedefe gerçek karşılaştırma yapılır.

---

## 5. Sprint S22 — Mobile App (RN+Expo) Temel

| # | Görev | Modül |
|--|--|--|
| S22.1 | Expo bootstrap + EAS Build pipeline | X.1 |
| S22.2 | Keycloak OAuth in-app browser flow | X.1, 1.1 |
| S22.3 | Tenant picker ekran + federasyon | X.1, 1.2 |
| S22.4 | Today / Home ekran (bekleyen check-in, son bildirim) | X.1 |
| S22.5 | OKR list + detail ekran | X.1, 2.17 |
| S22.6 | OKR Check-in (KR slider + confidence + note) | X.1, 2.22 |
| S22.7 | KPI Quick View ekran | X.1, 2.26 |
| S22.8 | Push notification (Expo Notifications + deeplink) | X.1, 1.6 |
| S22.9 | Profile + Settings + locale/MFA | X.1 |
| S22.10 | Sentry crash + perf monitoring | X.1 |

**DoD:** iOS + Android build TestFlight + Play Internal'da, 10 dahili test kullanıcısı.

---

## 6. Sprint S23 — Mobile Tamamlama + Real Options + Open Beta Hazırlık

| # | Görev | Modül |
|--|--|--|
| S23.1 | Mobile: Notifications + Activity Feed ekranları | X.1, 1.6, 1.12 |
| S23.2 | Mobile: Search + AI Concierge chat | X.1, 1.11, 1.9 |
| S23.3 | Mobile: Approval Inbox (stage-gate + catchball onay) | X.1, 3.2, 2.13 |
| S23.4 | Mobile: offline cache (Expo SQLite) + write queue | X.1 |
| S23.5 | OTA update channel (staging vs prod) | X.1 |
| S23.6 | App Store + Play Store metadata + screenshots | X.1 |
| S23.7 | `execution.real_options` schema + Black-Scholes evaluator | 3.6 |
| S23.8 | Real Options UI (defer/expand/abandon/switch + NPV) | 3.6 |
| S23.9 | Open Beta tenant provisioning (15 müşteri) | ops |
| S23.10 | Open Beta sözleşme + onboarding wave | sales |

**DoD:** Mobile beta TestFlight + Play Internal'da müşteri kullanımına açılır; Open beta ilk 5 müşteri canlı.

---

## 7. Sprint S24 — GA Sertleştirme + Lansman Hazırlık + G4

| # | Görev | Alan |
|--|--|--|
| S24.1 | Pen test external (3rd party) | sec |
| S24.2 | Load test: 100 concurrent tenant, 10K r/s | perf |
| S24.3 | DR drill (cross-region restore) | ops |
| S24.4 | SOC 2 Type I report alındı | compliance |
| S24.5 | ISO 27001 Stage 1 audit | compliance |
| S24.6 | Help Center 130 makale tamam | docs |
| S24.7 | Trust Center sayfası canlı (security.kokpitgroup.com) | docs |
| S24.8 | Status page public canlı | ops |
| S24.9 | Marketing site sinaps.app GA hazırlık | marketing |
| S24.10 | Lansman PR + LinkedIn kampanya + case study (Tomofil-virtual + 2 beta) | marketing |
| S24.11 | G4 Stage-Gate review | mgmt |
| S24.12 | GA Go/No-Go kararı | mgmt |

**DoD:** GA-ready; tüm uyum + güvenlik + dokümantasyon + marketing kapısı yeşil.

---

## 8. G4 Stage-Gate (Faz-4 sonu — GA Karar)

**G4 kriterleri:**
1. Tüm MVP modüller (CORE+STRATEGY+EXECUTION+PROCESS+RISK+ESG) canlı ✓
2. Tomofil 11-madde kabul testi %100 ✓
3. Mobile app App Store + Play Store onaylı ✓
4. Open beta 15 müşteri, son 30 gün DAU > 60 ✓
5. NPS > 40 (closed beta cumulative) ✓
6. SOC 2 Type I report alındı ✓
7. KVKK + GDPR uyum tam ✓
8. SLA 99.9% son 90 gün ✓
9. Bug: P1 = 0, P2 < 5 (son 30 gün) ✓
10. ISO 27001 Stage 1 yeşil (sertifika 6 ay sonra) ✓
11. Documentation: 130+ Help Center makalesi (TR+EN) ✓
12. Trust Center + Status Page + DPA + Sub-processor list public ✓

**Karar:** Pass → GA Lansman (lansman tarihi 2-4 hafta sonra) / Hold → 4-6 hafta tampon

---

## 9. Riskler

| # | Risk | Olasılık | Etki | Önlem |
|--|--|:--:|:--:|--|
| R1 | Apple/Google review reddedebilir | O | Y | S22 sonu submit, 4 hafta tampon |
| R2 | TCFD/SBTi framework değişebilir | D | O | Versiyonlu schema |
| R3 | Pen test major bulguya yol açabilir | O | Y | S24 başı yap, mitigation 2 hafta tampon |
| R4 | SOC 2 Type I gecikirse GA gecikir | O | Y | Drata + danışmanla erken kanıt toplama |
| R5 | Open beta müşterileri churn ederse | D | Y | Dedicated CSM + günlük check-in |
| R6 | KRI auto-tetikleme false-positive | O | O | Threshold tuning, "snooze" mekanizması |
| R7 | Mobile bandwidth/perf düşük | O | O | Offline cache + cursor pagination |

---

## 10. Paralel İş Kolları

- **Sales:** Open beta sözleşmeler + Q1 next-year pipeline kuru
- **CSM:** 15 müşteri onboarding + dedicated kanal başına haftalık check-in
- **Marketing:** Lansman kampanya (PR + LinkedIn + event + case study)
- **Brand:** Lansman varlıkları (anahtar mesaj + sosyal medya kit + video)
- **Compliance:** ISO 27001 Stage 2 hazırlık (F5+ Q1)
- **Hire:** F4 sonu — Security Eng (tam zamanlı), Finance/Ops Manager
- **Product:** F5 roadmap (Forecast, ERP connector, GRI/CSRD, HYOK) planlama

---

## 11. GA Sonrası 90 Gün (F4 + Q1 Y2)

- Haftalık metrik review (sales + product + ops)
- Hızlı iter (bug + müşteri-kritik feature)
- F5 sprint planı yazılır (S25-S30)
- CRO + COO hire (eğer F4'te yapılmadıysa)
- ISO 27001 sertifika
- SOC 2 Type II observation window devam
- Mobile v1.5 (offline + ek dil)
- 3 yeni dil canlı: AR, DE, ES

---

## 12. F5+ Roadmap Özeti (referans)

GA sonrası 6-12 ay öncelikler:
- **Forecast Engine** (zaman serisi tahmin) — KPI + finansal
- **ERP Connector katalogu** (SAP, Oracle, Workday, NetSuite, Salesforce, HRIS)
- **GRI/CSRD Report Builder** (ESG genişletme)
- **HYOK** (customer-managed encryption key) — Enterprise+
- **Process Mining** (light)
- **Document AI Co-author** (PDF üreteci)
- **Marketplace SDK** (3rd party plugin)
- **White-label / partner portal**
- **Multi-region Active-Active** (Enterprise+ talep ederse)
- **Strategic Partner tier** (Enterprise+ üstü, custom)
