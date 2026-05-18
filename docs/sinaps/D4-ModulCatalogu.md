# D4 — SİNAPS MODÜL KATALOĞU v1.0
> 80+ alt-modül · paket eşleme · faz dağılımı · bağımlılıklar
> Tarih: 2026-05-16
> Durum: TASLAK — onay bekliyor
> Bağımlılık: D1 (PRD), D2 (ADR), D3 (Domain)

---

## 0. Okuma Anahtarı

- **Paket:** S = Starter · P = Pro · E = Enterprise · E+ = Enterprise+
- **Faz:** F1 (ay 1–3) · F2 (4–6) · F3 (7–9) · F4 (10–12) · F5+ (MVP sonrası)
- **Bağımlılık:** [M-X.Y] kodlarıyla referans
- **Brand:** KP = Kokpitim'e de açık · SIN = Sinaps-only

---

## 1. M-CORE — Platform Çekirdeği (zorunlu — her pakette)

| Kod | Alt-Modül | Paket | Faz | Bağ. | Brand | Amaç |
|-----|-----------|-------|-----|------|-------|------|
| 1.1 | Identity & SSO | S/P/E/E+ | F1 | — | KP | Keycloak entegrasyon, login, MFA, SCIM |
| 1.2 | Organization & Tenant | S/P/E/E+ | F1 | 1.1 | KP | Org/Tenant/Sub-tenant/Workspace CRUD, ltree |
| 1.3 | RBAC & Membership | S/P/E/E+ | F1 | 1.1, 1.2 | KP | Rol, üyelik, federasyon |
| 1.4 | License & Package | S/P/E/E+ | F1 | 1.2 | KP | OPA policy, paket atama, modül aktif/pasif |
| 1.5 | Document Vault | S/P/E/E+ | F1 | 1.2 | KP | S3 belge, versiyon, paylaşım |
| 1.6 | Notification Center | S/P/E/E+ | F1 | 1.1 | KP | E-posta, in-app, webhook, push |
| 1.7 | Audit Log | S/P/E/E+ | F1 | 1.2 | KP | Append-only, Postgres partition + S3 WORM |
| 1.8 | Dashboard Framework | S/P/E/E+ | F1 | 1.2 | KP | Widget, layout, paylaş, embed |
| 1.9 | AI Concierge (temel) | P/E/E+ | F2 | 1.1, 1.5 | KP | LiteLLM proxy, RAG, tenant policy |
| 1.10 | Localization Engine | S/P/E/E+ | F1 | — | KP | 23 dil, RTL, JSONB translatable |
| 1.11 | Search (global) | P/E/E+ | F2 | 1.5 | KP | Postgres FTS + pgvector |
| 1.12 | Activity Feed | S/P/E/E+ | F1 | 1.7 | KP | Kullanıcı zaman akışı |

**Toplam: 12 alt-modül** (PRD'de "7 alt-modül" başlangıç minimum'uydu — F1 dahil tam dökümü budur).

---

## 2. M-STRATEGY — Strateji Bağlamı

### 2.A Analiz Araçları

| Kod | Alt-Modül | Paket | Faz | Bağ. | Amaç |
|-----|-----------|-------|-----|------|------|
| 2.1 | Vision/Mission/Values | S/P/E/E+ | F2 | 1.2 | Çok dilli vizyon-misyon-değer |
| 2.2 | SWOT | S/P/E/E+ | F2 | 2.1 | Klasik SWOT matrisi |
| 2.3 | TOWS | P/E/E+ | F2 | 2.2 | SWOT'tan strateji üretimi |
| 2.4 | PESTEL | P/E/E+ | F2 | 2.1 | Makro çevre analizi |
| 2.5 | Porter 5 Forces | E/E+ | F2 | 2.1 | Sektör çekiciliği |
| 2.6 | VRIO | E/E+ | F3 | 2.1 | Kaynak temelli analiz |
| 2.7 | Value Chain | E/E+ | F3 | 2.1 | Porter değer zinciri |
| 2.8 | Stakeholder Map | P/E/E+ | F3 | 2.1 | Paydaş matrisi |

### 2.B Strateji Tasarımı

| Kod | Alt-Modül | Paket | Faz | Bağ. | Amaç |
|-----|-----------|-------|-----|------|------|
| 2.9 | Strategic Plan (root) | S/P/E/E+ | F2 | 2.1 | Plan ana çatısı, dönemler |
| 2.10 | Pillars / H1–Hn | S/P/E/E+ | F2 | 2.9 | Stratejik hedefler |
| 2.11 | Strategies (main/sub) | S/P/E/E+ | F2 | 2.10 | Ana + alt stratejiler |
| 2.12 | Hoshin X-Matrix | E/E+ | F2 | 2.10 | Breakthrough + annual + metrics |
| 2.13 | Catchball Channels | E/E+ | F2 | 2.12 | 5 kanal bottom-up |
| 2.14 | EFQM 2025 Assessment | E/E+ | F3 | 2.10 | Direction/Execution/Results skor |
| 2.15 | BSC (4 perspektif) | P/E/E+ | F2 | 2.10 | Balanced Scorecard |
| 2.16 | Strategy Map | E/E+ | F3 | 2.15 | Sebep-sonuç haritası |

### 2.C OKR Cascade

| Kod | Alt-Modül | Paket | Faz | Bağ. | Amaç |
|-----|-----------|-------|-----|------|------|
| 2.17 | OKR Org Level | S/P/E/E+ | F2 | 2.10 | Üst düzey OKR |
| 2.18 | OKR BU Level | P/E/E+ | F2 | 2.17 | İş birimi cascade |
| 2.19 | OKR Facility Level | E/E+ | F3 | 2.18 | Tesis seviyesi |
| 2.20 | OKR Team Level | P/E/E+ | F3 | 2.18 | Takım seviyesi |
| 2.21 | OKR Individual Level | P/E/E+ | F3 | 2.20 | Bireysel OKR |
| 2.22 | OKR Check-in & Confidence | P/E/E+ | F3 | 2.17 | Düzenli güven puanı |

### 2.D Senaryo & Karar

| Kod | Alt-Modül | Paket | Faz | Bağ. | Amaç |
|-----|-----------|-------|-----|------|------|
| 2.23 | Scenario Planning | E/E+ | F3 | 2.9 | 4 senaryo + olasılık |
| 2.24 | Early Warning Signals | E/E+ | F3 | 2.23 | 8+ EWS, eşik takibi |
| 2.25 | Decision Tree | E/E+ | F3 | 2.23 | Karar ağacı görselleştirme |

### 2.E KPI Master

| Kod | Alt-Modül | Paket | Faz | Bağ. | Amaç |
|-----|-----------|-------|-----|------|------|
| 2.26 | KPI Master | S/P/E/E+ | F2 | 1.2 | Tüm modüllerin referansı |
| 2.27 | KPI Formula Engine | P/E/E+ | F2 | 2.26 | Hesap formülü, türev KPI |
| 2.28 | KPI Threshold & Alert | P/E/E+ | F2 | 2.26, 1.6 | Yeşil/sarı/kırmızı |

**M-STRATEGY toplam: 28 alt-modül**

---

## 3. M-EXECUTION — İcra Bağlamı

| Kod | Alt-Modül | Paket | Faz | Bağ. | Amaç |
|-----|-----------|-------|-----|------|------|
| 3.1 | Initiative Registry | S/P/E/E+ | F3 | 2.11 | Stratejik girişim CRUD |
| 3.2 | Stage-Gate (G0–G5) | E/E+ | F3 | 3.1 | 6-gate karar süreci |
| 3.3 | Initiative Roadmap | P/E/E+ | F3 | 3.1 | Gantt + bağımlılık |
| 3.4 | CAPEX/OPEX Plan | E/E+ | F3 | 3.1 | Bütçe takip |
| 3.5 | ABC Costing | E/E+ | F4 | 3.1, 4.1 | Aktivite tabanlı maliyet |
| 3.6 | Real Options Valuation | E+ | F4 | 3.1 | Defer/Expand/Abandon değerlemesi |
| 3.7 | Initiative Health Score | P/E/E+ | F3 | 3.1, 2.26 | Otomatik sağlık |
| 3.8 | Individual Performance | P/E/E+ | F3 | 2.21 | Bireysel değerlendirme |
| 3.9 | 360° Feedback | E/E+ | F4 | 3.8 | Çok kaynaklı geri bildirim |
| 3.10 | Competency Matrix | E/E+ | F4 | 3.8 | Yetkinlik haritası |

**M-EXECUTION toplam: 10 alt-modül**

---

## 4. M-PROCESS — Süreç Bağlamı

| Kod | Alt-Modül | Paket | Faz | Bağ. | Amaç |
|-----|-----------|-------|-----|------|------|
| 4.1 | Process Registry | P/E/E+ | F3 | 1.2 | Süreç CRUD, versiyon |
| 4.2 | E2E Process Templates (14) | E/E+ | F3 | 4.1 | S2E, R2M, R2R, C2L, F2D, P2M, S2P, O2C, A2R, I2R, B2R, H2R, D2I, W2R |
| 4.3 | Process Step Designer | P/E/E+ | F3 | 4.1 | Adım editörü |
| 4.4 | RACI Assignment | P/E/E+ | F3 | 4.3 | R/A/C/I matris |
| 4.5 | CMMI Assessment (L1–L5) | E/E+ | F4 | 4.1 | Olgunluk skoru |
| 4.6 | SLA Definition & Monitor | E/E+ | F4 | 4.1, 2.26 | SLA + ihlal aksiyonu |
| 4.7 | Process–KPI Link | P/E/E+ | F3 | 4.1, 2.26 | KPI ağırlıklı bağ |
| 4.8 | Process Mining (light) | E+ | F5+ | 4.1 | Olay log analizi |

**M-PROCESS toplam: 8 alt-modül**

---

## 5. M-RISK — Risk Bağlamı

| Kod | Alt-Modül | Paket | Faz | Bağ. | Amaç |
|-----|-----------|-------|-----|------|------|
| 5.1 | Risk Register | P/E/E+ | F4 | 1.2 | Risk CRUD, kategori |
| 5.2 | COSO ERM Framework | E/E+ | F4 | 5.1 | COSO yapılandırma |
| 5.3 | ISO 31000 Framework | E/E+ | F4 | 5.1 | ISO yapılandırma |
| 5.4 | Inherent vs Residual | E/E+ | F4 | 5.1 | Olasılık×Etki ısı haritası |
| 5.5 | Risk Appetite Statement | E/E+ | F4 | 5.1 | Eşik yeşil/sarı/kırmızı |
| 5.6 | KRI (Key Risk Indicators) | E/E+ | F4 | 5.1, 2.26 | KRI takibi |
| 5.7 | Control Library | E/E+ | F4 | 5.1 | Preventive/Detective kontrol |
| 5.8 | Risk Event Log | E/E+ | F4 | 5.1 | Gerçekleşen olay + lesson |
| 5.9 | Risk–Strategy Link | E/E+ | F4 | 5.1, 2.11 | Risk-strateji eşleme |
| 5.10 | Risk Heatmap & Reports | P/E/E+ | F4 | 5.1 | Pano + ihracat |

**M-RISK toplam: 10 alt-modül**

---

## 6. M-ESG — Sürdürülebilirlik Bağlamı

| Kod | Alt-Modül | Paket | Faz | Bağ. | Amaç |
|-----|-----------|-------|-----|------|------|
| 6.1 | ESG Plan | P/E/E+ | F4 | 1.2 | ESG plan ana çatısı |
| 6.2 | TCFD Report | E/E+ | F4 | 6.1 | Governance/Strategy/Risk/Metrics |
| 6.3 | SBTi Targets | E/E+ | F4 | 6.1 | Scope 1/2/3 hedef |
| 6.4 | Carbon Inventory | E/E+ | F4 | 6.1 | Scope-bazlı envanter |
| 6.5 | BMSKA (SDG) Mapping | P/E/E+ | F4 | 6.1, 2.11 | 17 SDG eşleme |
| 6.6 | GRI/CSRD Report Builder | E+ | F5+ | 6.1 | Otomatik rapor |
| 6.7 | Sustainability Dashboard | P/E/E+ | F4 | 6.1, 1.8 | Pano |

**M-ESG toplam: 7 alt-modül**

---

## 7. Yardımcı / Çapraz Modüller (MVP içi)

| Kod | Alt-Modül | Paket | Faz | Amaç |
|-----|-----------|-------|-----|------|
| X.1 | Mobile App (RN+Expo) | P/E/E+ | F4 | iOS+Android OKR check-in, bildirim |
| X.2 | Public API Gateway | P/E/E+ | F2 | OpenAPI 3.1, rate limit, key mgmt |
| X.3 | Webhook Outbound | P/E/E+ | F3 | Tenant'a outbound event |
| X.4 | Data Export (CSV/XLSX/PDF) | S/P/E/E+ | F2 | Her listede dışa aktarım |
| X.5 | Import Wizard | P/E/E+ | F3 | Excel'den KPI/OKR/Process yükleme |
| X.6 | Tomofil Seed Data | iç | F3 | Kabul testi sanal verisi |
| X.7 | Feature Flag Admin (GrowthBook) | iç | F1 | Yönetim UI'ı |
| X.8 | Tenant Provisioning UI | iç | F1 | Bizim admin paneli |

**Yardımcı toplam: 8 alt-modül**

---

## 8. Faz Sonrası (Kapsam Dışı — F5+)

- ERP/CRM/HRIS connector kataloğu (SAP, Oracle, Workday, Salesforce, NetSuite)
- Forecast Engine (zaman serisi tahmin)
- Marketplace SDK (3rd party plugin)
- White-label / partner portal
- Offline mobile sync
- Document AI co-author

---

## 9. Toplam Özet

| Bağlam | Alt-Modül | Faz dağılımı |
|--------|-----------|--------------|
| M-CORE | 12 | F1: 11, F2: 1 |
| M-STRATEGY | 28 | F2: 18, F3: 10 |
| M-EXECUTION | 10 | F3: 7, F4: 3 |
| M-PROCESS | 8 | F3: 4, F4: 3, F5+: 1 |
| M-RISK | 10 | F4: 10 |
| M-ESG | 7 | F4: 6, F5+: 1 |
| Yardımcı | 8 | F1: 2, F2: 2, F3: 3, F4: 1 |
| **TOPLAM** | **83** | **F1: 13 · F2: 21 · F3: 24 · F4: 23 · F5+: 2** |

---

## 10. Paket × Modül Görünümü

| Modül grubu | Starter | Pro | Enterprise | Enterprise+ |
|-------------|:---:|:---:|:---:|:---:|
| M-CORE (temel) | ✅ | ✅ | ✅ | ✅ |
| AI Concierge | — | ✅ | ✅ | ✅ |
| Strateji (sade: 2.1, 2.2, 2.9–2.11, 2.17, 2.26) | ✅ | ✅ | ✅ | ✅ |
| Strateji (orta: +TOWS, PESTEL, BSC, OKR BU/Team/Ind, KPI Formula) | — | ✅ | ✅ | ✅ |
| Strateji (tam: +Porter, VRIO, Hoshin, EFQM, Strategy Map, OKR Facility, Scenario, EWS, DecTree) | — | — | ✅ | ✅ |
| İcra (sade: 3.1, 3.7, 3.8) | — | ✅ | ✅ | ✅ |
| İcra (tam: +Stage-Gate, CAPEX, ABC, 360°, Competency) | — | — | ✅ | ✅ |
| Real Options | — | — | — | ✅ |
| Süreç (sade: 4.1, 4.3, 4.4, 4.7) | — | ✅ | ✅ | ✅ |
| Süreç (tam: +14 E2E template, CMMI, SLA) | — | — | ✅ | ✅ |
| Process Mining | — | — | — | ✅ |
| Risk (sade: 5.1, 5.10) | — | ✅ | ✅ | ✅ |
| Risk (tam) | — | — | ✅ | ✅ |
| ESG (sade: 6.1, 6.5, 6.7) | — | ✅ | ✅ | ✅ |
| ESG (tam: TCFD/SBTi/Carbon) | — | — | ✅ | ✅ |
| GRI/CSRD Report | — | — | — | ✅ |
| Mobile App | — | ✅ | ✅ | ✅ |
| Federasyon çok-tenant veri paylaşımı | — | — | — | ✅ |
| On-prem deploy seçeneği | — | — | — | ✅ |

---

## 11. Tomofil Kabul Testi → Modül Eşleme

Tomofil senaryosunun 11 maddesi (D1 §6) hangi modüllerle karşılanır:

| Tomofil maddesi | Modül(ler) |
|-----------------|------------|
| Org "Tomofil Group N.V." | 1.2 |
| 12 tesis sub-tenant | 1.2, 1.3 |
| 4 kıta region workspace | 1.2 |
| H1–H6 + EFQM 579 baseline | 2.10, 2.14 |
| 24 OKR 5-seviye cascade | 2.17–2.22 |
| Hoshin X-Matrix + Catchball 5 kanal | 2.12, 2.13 |
| 14 E2E süreç RACI+CMMI | 4.2, 4.4, 4.5 |
| 4 senaryo + 8 EWS + karar ağacı | 2.23, 2.24, 2.25 |
| COSO ERM 50+ risk + KRI eşik | 5.1, 5.2, 5.5, 5.6 |
| TCFD + SBTi hedef vs gerçek | 6.2, 6.3, 6.4 |
| AI Concierge stratejik soru | 1.9 |

Hepsi MVP içinde (F1–F4) yer alır. ✅

---

## 12. Onay

Onaylanırsa **D5 — Repo Yapısı** (Turborepo layout, paket isimleri, klasör hiyerarşisi) yazılır.

Kullanıcı onayı: ☐ Onaylandı ☐ Revizyon istendi
