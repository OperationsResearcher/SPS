# D1 — SİNAPS PRD v1.0
> Ürün Gereksinim Dokümanı
> Tarih: 2026-05-16
> Durum: TASLAK — onay bekliyor
> Bağlam: Sinaps, Kokpitim'in yeni nesil versiyonudur. Kokpitim (mevcut, KOBİ) yaşamaya devam eder; Sinaps (Enterprise) paralel ürün olarak konumlanır. Tomofil sanal şirketi, Sinaps'ın doğrulama (dogfooding) senaryosudur.

---

## 1. Vizyon

**"Strateji, icra ve risk yönetimini tek bir bilişsel platformda birleştiren; KOBİ'den çok uluslu holdinge kadar ölçeklenen, bulut-bağımsız, modüler kurumsal strateji işletim sistemi."**

Kokpit Group çatısı altında:
- **Kokpitim** → KOBİ segmenti, sadeleştirilmiş, hızlı kurulum, paket-temelli SaaS
- **Sinaps** → Enterprise segmenti, çok-kiracı federasyon, ileri analitik, AI Concierge, derin süreç–strateji–risk entegrasyonu

İki ürün ortak bir **CORE** üzerinde durur; üst paketler ayrışır.

---

## 2. Problem Tanımı

Mevcut Kokpitim:
- Tek-kiracı zihniyetiyle başladı, çok-kiracı federasyon yapısı yok
- Flask monolit + SQLite/PG karışık veri modeli — yatay ölçek zor
- Güvenlik borcu (S1–S5): rate limit kapalı, SECRET_KEY fallback, CSP pasif, login bypass riski
- Front'ta Jinja+JS karışımı, modal/SweetAlert tutarsızlığı kalıntıları
- Strateji modülleri (OKR, Hoshin, EFQM, TCFD, RACI, CMMI, ABC, Stage-Gate, Real Options, Catchball, COSO ERM, ISO 31000) ya yok ya da yarım
- Enterprise müşteri (Tomofil ölçeği: 12 tesis, 4 kıta, 847 tedarikçi, 387 metrik, 24 OKR, 18 ana strateji) için yetersiz

Sinaps bu borçları taşımadan, sıfırdan, modern stack ile inşa edilir.

---

## 3. Hedef Kullanıcı (Persona) Seti

| # | Persona | Segment | Temel İhtiyaç |
|---|---------|---------|---------------|
| P1 | KOBİ Yöneticisi (Kokpitim) | 10–250 çalışan | Hızlı strateji+KPI takibi, az modül, sade UX |
| P2 | Enterprise C-Suite (CEO/CFO/CSO) | 1000+ çalışan | Holding görünümü, OKR cascading, risk-strateji bağlantısı, ESG raporlama |
| P3 | Holding/Org Admin | Çok-kiracı | Tenant yönetimi, paket atama, federasyon kontrolü, veri paylaşım kuralı |
| P4 | Tenant Admin | Bağlı şirket | Kendi modül aktifleştirme, alt-kiracı (sub-tenant) yaratma |
| P5 | Strateji Ofisi (PMO/SPO) | Enterprise | Hoshin X-Matrix, Catchball, Stage-Gate, OKR 5-seviye cascading |
| P6 | Süreç Sahibi | Tüm segment | 14 uçtan uca süreç (S2E, R2M, R2R, C2L, F2D, P2M, S2P, O2C, A2R, I2R, B2R, H2R, D2I, W2R), RACI, CMMI ölçümü |
| P7 | Risk/Uyum Yöneticisi | Enterprise | COSO ERM, ISO 31000, KRI eşikleri, risk iştahı |
| P8 | ESG/Sürdürülebilirlik Lideri | Enterprise | TCFD, SBTi, BMSKA mapping, karbon raporu |
| P9 | Bireysel Çalışan | Tüm segment | Kendi OKR/PG, bireysel performans, bildirim |
| P10 | Platform SRE/Admin (bizim) | Sinaps ekibi | Çok-bulut deploy, gözlemlenebilirlik, SLO |

---

## 4. Ürün Kapsamı (MVP — 12–14 ay)

### 4.1 Paket Mimarisi (4-tier)

| Paket | Hedef | İçerik |
|-------|-------|--------|
| **Starter** | Mikro/KOBİ | CORE + STRATEGY (sade) + EXECUTION (sade) |
| **Pro** | Orta KOBİ | + PROCESS + RISK (light) + ESG (light) |
| **Enterprise** | Büyük şirket | + Tam STRATEGY (Hoshin, EFQM, Scenario), tam RISK (COSO/ISO31000), tam ESG (TCFD/SBTi), AI Concierge |
| **Enterprise+** | Holding/Çok-tenant | + Federasyon, çok-tenant veri paylaşımı, özel AI policy, on-prem opsiyon |

### 4.2 Modül Paketleri (MVP içinde)

1. **M-CORE** (zorunlu — her pakette): Kimlik, Org, Belge, Bildirim, Audit, Dashboard, AI temel (7 alt-modül)
2. **M-STRATEGY**: Vizyon-Misyon, SWOT/TOWS, PESTEL, Porter 5, VRIO, Hoshin X-Matrix, EFQM 2025, BSC, OKR (5-seviye), Scenario+Decision Tree, Catchball
3. **M-EXECUTION**: Initiative, Stage-Gate, Real Options, ABC Costing, CAPEX takip, Bireysel Performans
4. **M-PROCESS**: 14 E2E süreç şablonu, RACI, CMMI ölçer, SLA, KPI bağlama
5. **M-RISK**: COSO ERM, ISO 31000, Risk register, KRI eşik, Risk iştahı
6. **M-ESG**: TCFD, SBTi, BMSKA mapping, Karbon envanteri, Sürdürülebilirlik raporu

### 4.3 Kapsam Dışı (Faz 5+)

- ERP/CRM/HRIS derin entegrasyonu (SAP, Oracle, Workday)
- İleri ML/forecast (zaman serisi tahmin motoru)
- Marketplace / üçüncü taraf eklenti SDK'sı
- Offline mobil sync
- Belge AI co-author (PDF üretici)
- White-label / partner reseller portal

---

## 5. Başarı Kriterleri

### 5.1 İşlevsel
- **Tomofil senaryosu %100 çalışır:** 6 stratejik hedef, 24 OKR, 18 ana + 55 alt strateji, 14 E2E süreç, 4 senaryo + 8 erken uyarı, EFQM 579→820 skorlama, 387 metrik dashboard, Catchball 5 kanal
- KOBİ "ilk kullanım"dan strateji+5 KPI'a 30 dakikada ulaşır
- Enterprise pilot (Tomofil) tüm modüllerle prod-equivalent ortamda çalışır

### 5.2 Teknik
- p95 sayfa yükleme < 1.5 s (Enterprise dashboard'da bile)
- 99.9% uptime SLO
- RLS testleri: hiçbir tenant başka tenant verisini göremez (otomatik test suite)
- Cloud-agnostic: GCP/AWS/Azure'da aynı Helm chart ile 1 günde kurulum
- 23 dil + RTL desteği test edilmiş

### 5.3 Ürün
- 4 tier paket aktif, lisans denetimi runtime'da çalışır
- Tenant admin modül aktif/pasif geçişi <30sn
- Mobile (React Native+Expo) iOS+Android beta build
- AI Concierge tek tıkla LiteLLM proxy üzerinden çalışır (Claude/OpenAI/yerel seçilebilir)

---

## 6. Tomofil Doğrulama Senaryosu (MVP Kabul Testi)

MVP "biter" demek için Tomofil sanal şirketinde şunlar tamamlanmalı:

1. Organization: "Tomofil Group N.V." yaratılır
2. 12 tesis = 12 sub-tenant olarak federe edilir
3. 4 kıta = 4 ara seviye (region) workspace
4. 6 stratejik hedef H1–H6 girilir, EFQM 2025 baseline 579 hesaplanır
5. 24 OKR 5 seviyeye cascade edilir (Org → BU → Tesis → Takım → Birey)
6. Hoshin X-Matrix üretilir, Catchball 5 kanal aktif
7. 14 E2E süreç şablonu RACI+CMMI ile yüklenir
8. 4 senaryo + 8 erken uyarı sinyali + karar ağacı çalışır
9. COSO ERM register'a 50+ risk, KRI eşikleri tanımlı
10. TCFD raporu otomatik üretilir, SBTi hedef vs gerçek
11. AI Concierge "Tomofil EFQM skorumu 720'ye çıkarmak için en yüksek katkı sağlayacak 3 girişim?" sorusuna doğru cevap verir

---

## 7. Olmayacak (Out-of-Scope, Kesin)

- Kokpitim eski monolitin Sinaps'a "köprülenmesi" (sadece ETL one-time)
- SQLite (sadece local dev için; prod = Postgres-only)
- Cloud-native lock-in: Lambda, BigQuery, Cosmos, DynamoDB, App Engine — yasak
- Jinja2 template (Next.js SSR/RSC kullanılacak)
- Flask (FastAPI'ye geçiş kesin)
- jQuery / vanilla DOM cocktail (React/Next only)

---

## 8. Bağımlılıklar ve Varsayımlar

- Tomofil PDF'leri (Şirket Dosyası + Stratejik Plan) referans tasarım kaynağıdır; modül kataloğu bu dokümandan türetilir
- Kokpit Group marka mimarisi onaylı (D8'de detaylandırılacak)
- 16 mimari karar (D2 ADR set'inde) kilitli — değişirse PRD revize edilir
- Geliştirme ekibi Stage-Gate disiplini ile çalışır (3 ay × 4 faz)

---

## 9. Faz Özeti

| Faz | Süre | Çıktı |
|-----|------|-------|
| F0 | 4-6 hf | D1–D8 dokümanlar, repo iskeleti, CI/CD |
| F1 | 3 ay | M-CORE + Keycloak + i18n + multi-tenant infra |
| F2 | 3 ay | M-STRATEGY + KPI Master + AI Concierge |
| F3 | 3 ay | M-EXECUTION + M-PROCESS + Tomofil 24 OKR pilot |
| F4 | 3 ay | M-RISK + M-ESG + Mobile + Beta release |

Her faz sonu Stage-Gate review (kendi ürünümüzü kendimize uyguluyoruz).

---

## 10. Açık Sorular (D2 ADR'de cevaplanacak)

- ADR-01: tenant_path ltree mi, materialized path string mi?
- ADR-02: RLS policy'leri DB seviyesinde mi, app seviyesinde mi (yoksa ikisi)?
- ADR-03: Event bus (Kafka/NATS/Redis Streams) hangisi?
- ADR-04: API protokol (REST + OpenAPI vs GraphQL vs tRPC)?
- ADR-05: Frontend state (Zustand/Redux/React Query)?
- ADR-06: BFF (Backend-for-Frontend) gerekli mi?
- ADR-07: Multi-region active-active mi, active-passive mi?
- ADR-08: Encryption at rest key yönetimi (KMS-agnostic nasıl)?
- ... (15–18 ADR toplam)

---

## 11. Onay

Bu PRD onaylanırsa **D2 — ADR Set** yazılmaya başlanır.

Kullanıcı onayı: ☐ Onaylandı ☐ Revizyon istendi
