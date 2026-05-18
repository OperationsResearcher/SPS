# FAZ 2 — STRATEJİ SPRINT PLANI
> M-STRATEGY (tam) + KPI Master derinleştirme + AI Concierge RAG
> Süre: 12 hafta (6 × 2-haftalık sprint, S7-S12)
> Tarih: 2026-05-16 · Bağımlılık: F1 G1 geçti

---

## 0. Faz-2 Hedefi

**"Tomofil için strateji oluşturma tam ürün olarak çalışır: vizyon → pillar → strateji → SWOT/PESTEL/Porter → Hoshin X-Matrix + Catchball → EFQM baseline → BSC → 5-seviye OKR cascade → senaryo+EWS+karar ağacı. KPI Master formül motoru ve eşik alarm dahil. AI Concierge belge+veri üzerinden RAG ile soru cevaplıyor."**

F2 sonunda **strateji modülü Beta hazır**, F3'te icra/süreç eklenecek.

---

## 1. Kapsam (M-STRATEGY 2.1-2.28 + AI derinleştirme)

| Kod | Alt-Modül | Sprint |
|--|--|:--:|
| 2.1 | Vision/Mission/Values | S7 |
| 2.2-2.4 | SWOT, TOWS, PESTEL | S7, S8 |
| 2.5-2.8 | Porter5, VRIO, Value Chain, Stakeholder | S8 |
| 2.9-2.11 | Strategic Plan, Pillars, Strategies | S7 |
| 2.12-2.13 | Hoshin X-Matrix + Catchball | S9 |
| 2.14 | EFQM 2025 Assessment | S10 |
| 2.15-2.16 | BSC + Strategy Map | S10 |
| 2.17-2.22 | OKR 5-seviye cascade + check-in | S8, S9 |
| 2.23-2.25 | Scenario + EWS + Decision Tree | S11 |
| 2.26-2.28 | KPI Master + Formula Engine + Threshold | S7, S11 |
| 1.9 (deep) | AI Concierge RAG + multi-doc | S12 |
| 1.11 (deep) | Search pgvector hybrid | S12 |
| X.4 (deep) | Export PDF/PPTX | S10 |
| X.5 | Import Wizard (Excel) | S11 |

---

## 2. Sprint S7 — Plan + Pillar + Strategy + Vision + SWOT + KPI Master temeli

**Hedef:** Strateji ana çatısı çalışsın; KPI Master ilk girişler olsun.

| # | Görev | Modül |
|--|--|--|
| S7.1 | `strategy.plans` + Plan CRUD + lifecycle (draft/active/archived) | 2.9 |
| S7.2 | `strategy.pillars` + drag-drop sıralama UI | 2.10 |
| S7.3 | `strategy.strategies` (main/sub) + parent-child | 2.11 |
| S7.4 | Vision/Mission/Values multi-lang editor | 2.1 |
| S7.5 | `strategy.analyses` generic table + SWOT editor (4 quadrant) | 2.2 |
| S7.6 | `strategy.kpis` (KPI Master) + CRUD | 2.26 |
| S7.7 | `strategy.kpi_measurements` + manuel ölçüm girişi | 2.26 |
| S7.8 | Plan dashboard widget'ları (pillar progress, KPI tile) | 1.8 |
| S7.9 | Audit event'leri (plan/pillar/strategy lifecycle) | 1.7 |
| S7.10 | E2E test: plan oluştur → 3 pillar → 5 strateji → kaydet | test |

**DoD:** Tomofil seed'inde H1-H6 + 18 ana strateji girilebilir.

---

## 3. Sprint S8 — Analiz Araçları (TOWS/PESTEL/Porter/VRIO/Value Chain/Stakeholder) + OKR Temeli

| # | Görev | Modül |
|--|--|--|
| S8.1 | TOWS matrix (SWOT cross-product UI) | 2.3 |
| S8.2 | PESTEL editor + skor + ısı haritası | 2.4 |
| S8.3 | Porter 5 Forces editor + skorlama | 2.5 |
| S8.4 | VRIO assessment + sürdürülebilir avantaj çıktısı | 2.6 |
| S8.5 | Value Chain editor (Porter düzeni) | 2.7 |
| S8.6 | Stakeholder Map (power/interest matrisi) | 2.8 |
| S8.7 | `strategy.okrs` + `strategy.key_results` schema + Org-level CRUD | 2.17 |
| S8.8 | OKR detail view + KR list + confidence | 2.17 |
| S8.9 | BU-level OKR + parent referansı | 2.18 |
| S8.10 | Analysis export PDF (basit template) | X.4 |

**DoD:** Tomofil tüm 5 analiz (SWOT/TOWS/PESTEL/Porter/VRIO) doldurulur, PDF olarak alınabilir.

---

## 4. Sprint S9 — OKR Cascade Tam + Hoshin X-Matrix + Catchball

| # | Görev | Modül |
|--|--|--|
| S9.1 | OKR Facility-level + workspace bağlama | 2.19 |
| S9.2 | OKR Team-level + workspace.users | 2.20 |
| S9.3 | OKR Individual-level + atama UI | 2.21 |
| S9.4 | "Cascade Builder" — parent OKR'dan child taslak otomatik | 2.17-2.21 |
| S9.5 | OKR Check-in modal (KR slider + confidence + 1-line note) | 2.22 |
| S9.6 | Check-in hatırlatma cron + bildirim | 2.22, 1.6 |
| S9.7 | Hoshin X-Matrix 4-quadrant editor | 2.12 |
| S9.8 | X-Matrix view modu (görsel matrix render) | 2.12 |
| S9.9 | Catchball channels (5 tip) + round yönetimi | 2.13 |
| S9.10 | Catchball notification + lock mekanizması | 2.13 |

**DoD:** Tomofil 24 OKR 5 seviyeye cascade edilir; Hoshin X-Matrix + Catchball 1 round tamamlanır.

---

## 5. Sprint S10 — EFQM + BSC + Strategy Map + Export Premium

| # | Görev | Modül |
|--|--|--|
| S10.1 | EFQM 2025 framework seed (Direction/Execution/Results criteria tree) | 2.14 |
| S10.2 | EFQM assessment editor (kriter bazlı skorlama) | 2.14 |
| S10.3 | EFQM baseline vs target + gap radar chart | 2.14 |
| S10.4 | BSC 4-perspective editor | 2.15 |
| S10.5 | BSC perspective ↔ KPI bağlama | 2.15 |
| S10.6 | Strategy Map (cause-effect, drag-drop) | 2.16 |
| S10.7 | PDF export — Plan tam dokümanı (vision→OKR) | X.4 |
| S10.8 | PPTX export — board sunumu şablonu | X.4 |
| S10.9 | Plan publish lifecycle (draft → review → published, lock kuralları) | 2.9 |
| S10.10 | Plan version history + diff görüntüleme | 2.9, 1.7 |

**DoD:** Tomofil EFQM baseline 579 kaydedilir, hedef 820 görselleşir; BSC 4 perspektif + Strategy Map çalışır; Board-ready PDF + PPTX üretilir.

---

## 6. Sprint S11 — Senaryo + EWS + Karar Ağacı + KPI Formula + Import

| # | Görev | Modül |
|--|--|--|
| S11.1 | `strategy.scenarios` CRUD + olasılık | 2.23 |
| S11.2 | Scenario narrative editor (rich text, multi-lang) | 2.23 |
| S11.3 | Early Warning Signal + threshold + status update | 2.24 |
| S11.4 | EWS otomatik tetikleme job (KPI ölçümünden) | 2.24, 1.6 |
| S11.5 | Decision Tree editor (node-based, react-flow) | 2.25 |
| S11.6 | KPI Formula DSL (parser, evaluator) | 2.27 |
| S11.7 | Türev KPI hesaplama job (nightly) | 2.27 |
| S11.8 | KPI Threshold + 3 renk alarm + bildirim | 2.28 |
| S11.9 | Import Wizard (Excel→KPI/OKR/Strategy) | X.5 |
| S11.10 | Import validation + error report + dry-run | X.5 |

**DoD:** Tomofil 4 senaryo + 8 EWS + karar ağacı çalışır; formula KPI türetir; Excel'den 100 KPI içeri alınabilir.

---

## 7. Sprint S12 — AI Concierge RAG + Search Hybrid + Sertleştirme

| # | Görev | Modül |
|--|--|--|
| S12.1 | Document embedding pipeline (NATS event → embedding) | 1.11 |
| S12.2 | pgvector index + hybrid search (FTS + vector) | 1.11 |
| S12.3 | AI Concierge RAG: tenant verisinden bağlam getir | 1.9 |
| S12.4 | "Golden answer" test suite (30 soru, LLM-as-judge) | 1.9, test |
| S12.5 | AI cost tracking + tenant cap policy | 1.9 |
| S12.6 | AI response source citation UI | 1.9 |
| S12.7 | AI "rate helpful" feedback loop | 1.9 |
| S12.8 | Tomofil seed v2 (tam strateji datası — 5000 KPI, 24 OKR, EFQM scores) | X.6 |
| S12.9 | Performance: 5000 KPI listele p95 <2s | perf |
| S12.10 | Faz-2 demo + G2 gate prep | mgmt |

**DoD:** Tomofil "EFQM skorumu 720'ye çıkarmak için en yüksek katkı sağlayacak 3 girişim?" sorusuna AI doğru kavramsal yanıt verir.

---

## 8. G2 Stage-Gate (Faz-2 sonu)

**G2 kriterleri:**
1. M-STRATEGY 28 alt-modülü canlı staging ✓
2. Tomofil senaryosu maddeler 4-6 (H1-H6+EFQM, 24 OKR, Hoshin+Catchball) %100 ✓
3. KPI Master 5000 KPI scale test geçti ✓
4. AI Concierge "golden answer" %85+ skor ✓
5. p95 dashboard <1.5s 5000 KPI yüklü ✓
6. SOC 2 hazırlık %60 ✓
7. Compliance: KVKK uyum %100, GDPR ROPA tamamlandı ✓
8. Alpha beta başlatıldı (içeride 5-8 kullanıcı, "kendi şirketimizi yönet" senaryosu)

**Karar:** Pass → F3 başlar / Hold → S13 tampon

---

## 9. Riskler

| # | Risk | Olasılık | Etki | Önlem |
|--|--|:--:|:--:|--|
| R1 | OKR 5-seviye cascade UI karmaşık | Y | Y | Cascade Builder wizard, S9 başında prototype |
| R2 | EFQM 2025 framework değişirse | D | O | Versiyonlu schema, esnek criteria tree |
| R3 | AI RAG yanlış cevap verirse | O | Y | Source citation zorunlu + "draft" disclaimer |
| R4 | KPI formula DSL güvenlik (eval) | O | Y | AST-based parser, eval yasak, sandbox |
| R5 | Tomofil seed gerçekçi değilse | O | O | Domain uzmanı (CSO emekli) review |
| R6 | Hoshin/EFQM/BSC tek sprint'te bitmeyebilir | O | O | S10 tampon, gerekirse S13 kullan |

---

## 10. Paralel İş Kolları (F2 boyunca)

- **Beta hazırlık:** Closed beta müşteri seçimi başlasın (5-8 müşteri pipeline)
- **Marka studio:** F2 ortasında brand book v1 PDF + Figma library
- **DPO + Drata:** SOC2 kontrol envanteri toplanır
- **Content:** OKR + Hoshin + EFQM 3 derin makale yayın
- **Hire:** F1 sonu hire'lar (PM, Designer, SRE) onboard; F2 ortası 4 yeni hire (Senior BE, Senior FE, Sales Lead, CSM)
