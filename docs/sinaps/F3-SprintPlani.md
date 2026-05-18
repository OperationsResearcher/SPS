# FAZ 3 — İCRA + SÜREÇ SPRINT PLANI
> M-EXECUTION (tam) + M-PROCESS (tam) + Tomofil 24 OKR pilot + Closed Beta
> Süre: 12 hafta (6 × 2-haftalık sprint, S13-S18)
> Tarih: 2026-05-16 · Bağımlılık: F2 G2 geçti

---

## 0. Faz-3 Hedefi

**"Strateji → İcra zinciri tam çalışır: Stratejik girişimler Stage-Gate G0-G5 ile yönetilir, CAPEX/OPEX bütçe + ABC maliyetlenir; 14 uçtan uca süreç şablonu RACI + CMMI + SLA ile çalışır; bireysel performans OKR ile bağlı. Tomofil 24 OKR + 24 initiative + 14 süreç tam pilot. Closed Beta başlar (5-8 müşteri)."**

---

## 1. Kapsam

### M-EXECUTION (3.1-3.10)
3.1 Initiative · 3.2 Stage-Gate · 3.3 Roadmap · 3.4 CAPEX/OPEX · 3.5 ABC · 3.7 Health · 3.8 Individual Perf · 3.9 360° · 3.10 Competency
(3.6 Real Options F4'e taşındı)

### M-PROCESS (4.1-4.7)
4.1 Process Registry · 4.2 14 E2E Templates · 4.3 Step Designer · 4.4 RACI · 4.5 CMMI · 4.6 SLA · 4.7 KPI Link

### Yardımcı
X.3 Webhook outbound · Tomofil seed v3 (full pilot data)

---

## 2. Sprint S13 — Initiative Registry + Stage-Gate Temeli

| # | Görev | Modül |
|--|--|--|
| S13.1 | `execution.initiatives` CRUD + lifecycle | 3.1 |
| S13.2 | Initiative-Strategy bağlama UI | 3.1 |
| S13.3 | Sponsor + Owner + team atama | 3.1 |
| S13.4 | `execution.stage_gates` schema (G0-G5) | 3.2 |
| S13.5 | Gate criteria template seed (default checklist) | 3.2 |
| S13.6 | Gate decision UI (pass/hold/kill/recycle) | 3.2 |
| S13.7 | Reviewer atama + onay akışı | 3.2 |
| S13.8 | Initiative list view (filter by status, strategy, owner) | 3.1 |
| S13.9 | Initiative detail page + tabs (gates, budget, roadmap, risk) | 3.1 |
| S13.10 | E2E test: Strategy → Initiative → G1 decision | test |

**DoD:** Tomofil 24 girişim Stage-Gate sürecine alınabilir; G1 geçen ilk girişim test edilir.

---

## 3. Sprint S14 — Roadmap + CAPEX/OPEX + Health Score

| # | Görev | Modül |
|--|--|--|
| S14.1 | Initiative roadmap (Gantt benzeri timeline) | 3.3 |
| S14.2 | Bağımlılık (dependency) edge'leri | 3.3 |
| S14.3 | `execution.capex_opex_plans` + yıllık bütçe matrisi | 3.4 |
| S14.4 | Multi-currency support + FX rate cache | 3.4 |
| S14.5 | Budget vs Actual karşılaştırma | 3.4 |
| S14.6 | Initiative Health Score algoritması (schedule+budget+KPI) | 3.7 |
| S14.7 | Health badge (green/amber/red) listede ve detayda | 3.7 |
| S14.8 | Webhook outbound: stagegate.decision_made, initiative.health_changed | X.3 |
| S14.9 | Roadmap PDF export | X.4 |
| S14.10 | Tomofil 24 girişim için CAPEX €34Mr dağılımı seed | X.6 |

**DoD:** Tomofil €34Mr CAPEX plan yüklenir, health rengi otomatik hesaplanır.

---

## 4. Sprint S15 — Process Registry + 14 E2E Template + Step Designer

| # | Görev | Modül |
|--|--|--|
| S15.1 | `process.processes` CRUD + versiyon | 4.1 |
| S15.2 | `process.process_steps` + sequence | 4.2 |
| S15.3 | Step Designer (drag-drop, swimlane) | 4.3 |
| S15.4 | 14 E2E template seed (S2E, R2M, R2R, C2L, F2D, P2M, S2P, O2C, A2R, I2R, B2R, H2R, D2I, W2R) | 4.2 |
| S15.5 | Template'ten tenant-spesifik kopya oluşturma | 4.2 |
| S15.6 | Process detail page (steps + RACI + CMMI + SLA + KPI tabs) | 4.1 |
| S15.7 | Process diagram render (BPMN-light, görsel) | 4.3 |
| S15.8 | Process export PDF | X.4 |
| S15.9 | Process versioning + diff | 4.1 |
| S15.10 | Audit + activity feed entegrasyonu | 1.7, 1.12 |

**DoD:** Tomofil için 14 E2E süreç template'i tenant'a kopyalanır, adımlar düzenlenir.

---

## 5. Sprint S16 — RACI + CMMI + SLA + Process-KPI Link

| # | Görev | Modül |
|--|--|--|
| S16.1 | `process.raci_assignments` (R/A/C/I × step × user/role) | 4.4 |
| S16.2 | RACI matrix UI (steps × roles) | 4.4 |
| S16.3 | RACI validation (1 A per step, en az 1 R) | 4.4 |
| S16.4 | `process.cmmi_assessments` + Level 1-5 form | 4.5 |
| S16.5 | CMMI evidence upload + assessor sign-off | 4.5 |
| S16.6 | CMMI history + trend chart | 4.5 |
| S16.7 | `process.sla_definitions` + threshold | 4.6 |
| S16.8 | SLA breach detection job + bildirim | 4.6, 1.6 |
| S16.9 | `process.process_kpi_links` + weight | 4.7 |
| S16.10 | Process performance dashboard (CMMI+SLA+KPI özet) | 1.8 |

**DoD:** Tomofil 14 sürecin her birinde RACI dolu, CMMI baseline assessment yapılır, SLA tanımlanır.

---

## 6. Sprint S17 — Individual Performance + 360° + Competency + ABC

| # | Görev | Modül |
|--|--|--|
| S17.1 | `execution.individual_performance` + period bazlı | 3.8 |
| S17.2 | Individual OKR ↔ Performance bağlama | 3.8 |
| S17.3 | Self-assessment formu | 3.8 |
| S17.4 | Manager review formu | 3.8 |
| S17.5 | 360° feedback (peer/subordinate çoklu kaynak) | 3.9 |
| S17.6 | Feedback anonimleştirme + minimum N kuralı | 3.9 |
| S17.7 | `execution.competency_matrix` (rol × yetkinlik × seviye) | 3.10 |
| S17.8 | Competency gap analizi + öneri | 3.10 |
| S17.9 | `execution.abc_costing_entries` + activity-driver-cost | 3.5 |
| S17.10 | ABC raporu (initiative / process bazlı maliyet) | 3.5 |

**DoD:** Tomofil 1000+ çalışanın bireysel performans formu çalışır; 5 pilot 360°; 14 sürecin ABC maliyeti çıkar.

---

## 7. Sprint S18 — Closed Beta Onboarding + Tomofil Tam Pilot + Sertleştirme

| # | Görev | Modül |
|--|--|--|
| S18.1 | Closed beta tenant'ları provisioned (5-8) | ops |
| S18.2 | Customer-specific onboarding playbook | CSM |
| S18.3 | Beta tenant başına dedicated Slack Connect kanal | CSM |
| S18.4 | Tomofil seed v3: 24 OKR + 24 girişim + 14 süreç + 1000 user | X.6 |
| S18.5 | Tomofil performans testi (12000 user, 5000 KPI, 8000 audit/gün) | perf |
| S18.6 | Cross-context bağlama testi (Strategy→Execution→Process→KPI) | E2E |
| S18.7 | Bug bash week (tüm ekip) | test |
| S18.8 | Help Center makaleleri (~40 yeni, F2 sonu+F3) | docs |
| S18.9 | In-app product tour (Userflow veya inhouse) yeni özellikler | UX |
| S18.10 | G3 gate prep + demo | mgmt |

**DoD:** Closed beta canlı, ilk 2 müşteri tenant aktif kullanıyor; Tomofil pilot end-to-end senaryo çalışıyor.

---

## 8. G3 Stage-Gate

**G3 kriterleri:**
1. M-EXECUTION 9 alt-modül + M-PROCESS 7 alt-modül canlı ✓
2. Tomofil senaryosu maddeler 5,7,8 (24 OKR cascade, 14 süreç RACI+CMMI, senaryo+EWS) tam pilot ✓
3. Closed beta 5+ müşteri tenant onboarded ✓
4. Beta DAU > 30 kullanıcı (5 müşteri × 6 aktif user) ✓
5. P1 sev bug 0, P2 sev <3 (son 30 gün) ✓
6. SOC 2 Type I audit başlamış ✓
7. Webhook delivery success >99% ✓
8. p95 KPI cascade re-render <1s (24 OKR × 5 seviye) ✓

**Karar:** Pass → F4 / Hold → 2 hafta tampon

---

## 9. Riskler

| # | Risk | Olasılık | Etki | Önlem |
|--|--|:--:|:--:|--|
| R1 | 14 E2E template'in detayı tek sprint'te bitmez | O | O | Template "minimum viable" — sonra kullanıcı zenginleştirir |
| R2 | Stage-Gate süreci farklı sektörde farklı | O | O | Customizable criteria template (tenant override) |
| R3 | Closed beta yavaş onboard, bug feedback gecikir | O | Y | Beta-dedicated CSM + günlük standup |
| R4 | RACI validation sıkı kural müşteriyi blokluyor | D | O | Warning olarak başla, F4'te zorunlu |
| R5 | 360° anonimlik gerçek değil (küçük takım) | O | O | Minimum N=3, "anonim değil" disclaimer |
| R6 | ABC maliyetlemesi muhasebe doğru olmayabilir | O | O | "Yönetsel — denetim değil" UI uyarı |

---

## 10. Paralel İş Kolları

- **Sales:** Closed beta sözleşmeleri (MSA + Beta Annex) — F3 başı imzalar
- **CSM:** Beta onboarding playbook + weekly customer check-in
- **SOC 2:** Type I audit başlatma (denetçi seçimi + kontrol kanıt toplama)
- **Content:** Stage-Gate + RACI + CMMI 3 derin makale
- **Hire:** F3 sonu — QA Eng, Mobile Eng, SDR + Marketing Ops
- **Brand:** Brand book yayın + sosyal medya kampanya planı
- **Product analytics:** PostHog event coverage %80'e çıkar
