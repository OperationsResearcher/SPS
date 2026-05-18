# P1 — FİYATLANDIRMA · GTM · SÖZLEŞME · SUPPORT
> Tarih: 2026-05-16 · Durum: TASLAK · Bağımlılık: D1, D4, D8

---

## 1. Fiyatlandırma Modeli

### 1.1 Kokpitim (KOBİ — TL birincil)
| Paket | Aylık (kullanıcı başına) | Min kullanıcı | Ana sınırlar |
|-------|--:|--:|--|
| **Starter** | ₺350 | 3 | 50 KPI, 1 plan, 5 GB belge |
| **Pro** | ₺850 | 5 | 200 KPI, 3 plan, 25 GB, AI Concierge |

- Yıllık peşin %15 indirim
- Ödeme: kredi kartı (iyzico) + havale
- KDV hariç

### 1.2 Sinaps (Enterprise — EUR/USD)
| Paket | Yıllık platform | Seat (yıllık) | Min seat | Ana sınırlar |
|-------|--:|--:|--:|--|
| **Enterprise** | €24.000 | €180 | 50 | 5 tenant, 10 GB/tenant, Full STRATEGY+EXECUTION+PROCESS |
| **Enterprise+** | €60.000 | €240 | 100 | Sınırsız tenant, federasyon, on-prem opsiyon, custom SLA |

- Platform fee + seat fee birlikte
- 3 yıllık taahhüt %20 indirim
- Ödeme: yıllık peşin (default), çeyreklik opsiyonu Enterprise+'ta
- Custom: Enterprise+ üstü "Strategic Partner" → görüşme

### 1.3 Eklentiler (her iki ürün)
| Eklenti | Fiyat |
|--------|--:|
| AI Concierge cost cap aşımı | $0.02/1K token (LiteLLM passthrough +%20) |
| Ek 100 GB belge | €40/ay (Enterprise), ₺200/ay (Kokpitim) |
| Premium Support (24/7 + 1h response) | %20 platform fee üzerine |
| Dedicated CSM | €18.000/yıl |
| Implementation pack (kickoff workshop + seed) | €15.000 tek seferlik |

### 1.4 Fiyatlandırma Disiplini
- **Liste fiyatı her zaman yayında** (kokpitim.com), Sinaps fiyatları yarı-açık (talep formu)
- İskonto onay matrisi: %0-10 satış · %10-20 CRO · %20+ CEO
- Yıllık enflasyon revizesi: TÜFE-2 (TR) / CPI EU (€), her Ocak

---

## 2. GTM (Go-to-Market) Stratejisi

### 2.1 Segment Önceliği (12-18 ay)
1. **Kokpitim — TR KOBİ** (devam): mevcut müşteri tabanı, content marketing, ortak ağ
2. **Sinaps — TR Holding** (F4 sonrası beta): Türkiye'nin 100 büyük holdingi, doğrudan satış
3. **Sinaps — AB DACH bölgesi** (F4+6): Almanya/Avusturya orta-üst sanayi, partner-led
4. **Sinaps — Körfez** (F4+12): BAE/SA, Arapça destek avantajı, partner-led

### 2.2 GTM Motoru
| Segment | Motor | Lead source | Sales cycle |
|---------|------|-------------|--|
| Kokpitim KOBİ | Product-Led Growth + Inbound | SEO, içerik, partner muhasebe ofisleri | 7-21 gün |
| Sinaps TR Enterprise | Sales-Led + ABM | LinkedIn ABM, sektör etkinlikleri | 3-6 ay |
| Sinaps AB | Partner-Led + ABM | Sistem entegratörü partneri | 6-9 ay |
| Sinaps Körfez | Partner-Led | Bölgesel danışmanlık ortağı | 6-12 ay |

### 2.3 Satış Akışı (Sinaps Enterprise)
```
1. MQL (LinkedIn/web/event) → SDR qualification (BANT+)
2. Discovery (1h) — pain + budget + decision tree
3. Demo (90dk) — kişiselleştirilmiş, müşteri verisiyle
4. POC (4-8 hafta) — Tomofil benzeri sandbox + müşterinin 1-2 OKR'ı
5. Commercial proposal — paket + seat + implementation
6. Legal (NDA → MSA → DPA) — 2-4 hafta
7. Kickoff + onboarding (4-6 hafta)
8. Go-live + QBR (3 ay sonra)
```

### 2.4 Content / Marketing Pillar'ları
- "Strateji icra etmek" — OKR, Hoshin, Stage-Gate (haftalık blog)
- "Risk + ESG entegrasyon" — TCFD, SBTi, COSO ERM (aylık derin makale)
- "AI + strateji" — AI Concierge kullanım örnekleri
- Tomofil case study (sanal ama metodolojik) — beyaz kitap

### 2.5 Etkinlik Takvimi (yıllık)
- Q1: Kokpit Strategy Summit (kendi etkinliğimiz, Ankara/İstanbul)
- Q2: Hannover Messe (AB sanayi)
- Q3: GITEX (Dubai)
- Q4: Sektör sponsorlukları

---

## 3. Sözleşme Paketi

### 3.1 Kokpitim (KOBİ)
- **ToS** (Terms of Service) — site içi click-wrap, TR hukuku, KVKK uyumlu
- **Gizlilik Politikası** — KVKK + GDPR ortak
- **Çerez Politikası**
- **DPA** (Data Processing Agreement) — opsiyonel, B2B müşteri talep ederse
- **Faturalama şartları** — aylık otomatik, başarısız ödeme 3 gün grace

### 3.2 Sinaps (Enterprise)
- **MSA** (Master Service Agreement) — özel sözleşme şablonu
- **Order Form** — paket, seat sayısı, başlangıç, taahhüt süresi
- **SLA** — bkz P4 §1; credit mekanizması
- **DPA + SCC** (Standard Contractual Clauses) — AB/UK transfer
- **Sub-processor List** — şeffaf, public sayfa, 30 gün önceden bildirim
- **Security Annex** — bkz P5; SOC2/ISO certs referans
- **AUP** (Acceptable Use Policy)
- **NDA** (POC öncesi karşılıklı)
- **Termination clause** — data export 90 gün, hard delete 30 gün sonrası

### 3.3 Hukuki Yapı
- Yasal varlık: Türkiye A.Ş. (ana) + AB B.V. (gerektiğinde, AB müşteri faturalama)
- Data Controller: müşteri / Data Processor: Kokpit Group
- Geçerli hukuk: TR (Kokpitim) / NL veya müşteri seçimi (Sinaps Enterprise+)

---

## 4. Support Modeli

### 4.1 Destek Katmanları
| Katman | Kokpitim | Sinaps Ent. | Sinaps Ent.+ | Premium add-on |
|--|--|--|--|--|
| **Yanıt süresi (P1 critical)** | 24h | 4h | 1h | 1h |
| **Yanıt süresi (P2 high)** | 48h | 1 iş günü | 4h | 2h |
| **Yanıt süresi (P3 normal)** | 5 iş günü | 2 iş günü | 1 iş günü | 8h |
| **Kanal** | E-posta + in-app | + Slack Connect | + telefon | + 24/7 on-call |
| **Saat** | 09-18 TR | 09-18 TR | 24/5 | 24/7 |
| **CSM** | yok | shared | dedicated | dedicated |
| **Yıllık QBR** | yok | 2 | 4 | 4 |

### 4.2 Severity Tanımları
- **P1 Critical** — Üretim down, tüm tenant etkilenir, veri kaybı riski
- **P2 High** — Major özellik bozuk, workaround zor, tek tenant etkilenir
- **P3 Normal** — Hata var, workaround mevcut
- **P4 Low** — Kozmetik, soru, feature request

### 4.3 Araçlar
- Helpdesk: **Plain** (modern, dev-friendly) veya **Pylon** — alternatif: Zendesk
- In-app guide: **Userflow** (mobile + web) veya inhouse minimal
- Status page: **Statuspage.io** veya self-host **Cachet**
- Community: Discord (Sinaps) / Telegram (Kokpitim TR)

### 4.4 Onboarding Akışı
**Kokpitim:** Sign-up → in-app wizard (5 adım) → 30dk tutorial video → 7 gün e-posta nurture
**Sinaps:** Kickoff workshop (1 gün, on-site/remote) → ilk plan-tenant-setup → Tomofil benzeri seed → 4 hafta hands-on → go-live → QBR

---

## 5. KPI'lar (Bizim İç Ölçümlerimiz)

| Boyut | Metrik | Hedef Y1 | Y2 |
|--|--|--|--|
| Acquisition | Kokpitim MAU | 500 | 2000 |
|  | Sinaps active tenant | 5 (beta) | 25 |
| Conversion | Kokpitim trial→paid | 18% | 25% |
|  | Sinaps POC→paid | 40% | 55% |
| Revenue | ARR | €400K | €2.5M |
|  | Sinaps ortalama ACV | €60K | €90K |
| Retention | NRR (Sinaps) | 100% | 115% |
|  | Logo churn (Kokpitim) | <3%/ay | <2%/ay |
| Efficiency | CAC payback (Kokpitim) | 6 ay | 4 ay |
|  | CAC payback (Sinaps) | 14 ay | 11 ay |
| Support | CSAT | >90% | >92% |
|  | Median ilk yanıt (P2) | <2h | <1h |

---

## 6. Açık Sorular
- OS-1: AB varlığı (B.V.) ne zaman kurulur? — AB müşteri kazanılınca veya proaktif F3'te?
- OS-2: Free trial Kokpitim'de 14 mü 30 gün mü? — Mevcut datayla karar
- OS-3: Sinaps "freemium" var mı? — Önerim: yok, POC modeli yeterli
- OS-4: Sinaps Türkiye fiyatı TL'ye sabitleyelim mi? — Kur riski; önerim: hayır, € fiyat üzerinden TL hesaplanır
- OS-5: Partner komisyon modeli (referral %15 / reseller %25)?
