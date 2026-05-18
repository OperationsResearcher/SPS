# SİNAPS — TOPLU AÇIK SORU LİSTESİ
> Tüm Faz-0 dokümanlarından toplanmış, kategorize edilmiş
> Tarih: 2026-05-16
> Toplam: 64 soru
>
> **DURUM: 64/64 KAPATILDI — 2026-05-16**
> Kurucu tüm açık sorularda tavsiyeleri onayladı.
> Canonical karar dosyası: [DecisionLog.md](DecisionLog.md)

Format: **[KOD]** Soru — *Tavsiyem* — Karar: ☐

---

## A. MİMARİ & TEKNİK (D-serisi)

### A1 — Veri & Bulut

**[A1.1]** (D2-ADR-01) `tenant_path` ltree mi materialized path string mi?
*Tavsiye:* ltree (zaten karar).
Karar: ☐ ltree ☐ string ☐ diğer

**[A1.2]** (D2-ADR-02) RLS DB seviyesinde mi, app seviyesinde mi?
*Tavsiye:* İkisi de (defense in depth).
Karar: ☐ Onaylandı

**[A1.3]** (D2-ADR-03) Event bus: Kafka / NATS JetStream / Redis Streams?
*Tavsiye:* NATS JetStream.
Karar: ☐

**[A1.4]** (D2-ADR-07) Active-Active multi-region ne zaman?
*Tavsiye:* MVP Active-Passive; Active-Active F5+ (NRR >110% veya regülasyon zorlarsa).
Karar: ☐ F5+ ☐ Daha erken ☐ Asla

**[A1.5]** (D3 §11) KPI Master tablosu hangi context'in?
*Tavsiye:* STRATEGY context owner, paylaşımlı şema.
Karar: ☐

**[A1.6]** (D5 §10) ETL spec ne kadar detaylı F0'da?
*Tavsiye:* P2 yeterli, kod F2'de yazılır.
Karar: ☐

### A2 — Frontend & State

**[A2.1]** (D2-ADR-05) FE state: TanStack+Zustand mı, Redux mu, Jotai mı?
*Tavsiye:* TanStack + Zustand.
Karar: ☐

**[A2.2]** (D2-ADR-06) Ayrı BFF mı, Next.js Route Handler mı?
*Tavsiye:* Yok, Next.js yeterli.
Karar: ☐

**[A2.3]** (D2-ADR-15) Mobile: React Native+Expo mı Flutter mu?
*Tavsiye:* RN+Expo (TS ekibi paylaşımı).
Karar: ☐

### A3 — Yardımcı Servisler

**[A3.1]** (D2-ADR-08) Secret yönetimi: Vault mu cloud KMS mü?
*Tavsiye:* Vault self-host (cloud-agnostic).
Karar: ☐

**[A3.2]** (D2-ADR-09) Lisans denetimi: OPA mı Casbin mi hardcoded mu?
*Tavsiye:* OPA sidecar.
Karar: ☐

**[A3.3]** (D2-ADR-16) Feature flag: GrowthBook mu LaunchDarkly mı Unleash mi?
*Tavsiye:* GrowthBook self-host.
Karar: ☐

**[A3.4]** (D2-ADR-18) Monorepo: Turborepo mu Nx mi Bazel mi?
*Tavsiye:* Turborepo + pnpm + uv.
Karar: ☐

---

## B. ÜRÜN & MVP KAPSAMI

**[B1]** (D1 §4.3) MVP'de "kapsam dışı" listesi yeterli mi?
*Tavsiye:* Evet — ERP/forecast/marketplace/offline-mobile/AI-co-author/white-label F5+.
Karar: ☐

**[B2]** (D4 §2.B) Hoshin X-Matrix'in MVP Enterprise paketinde olması zorunlu mu yoksa "premium add-on" mı?
*Tavsiye:* Enterprise paketinde — Tomofil için zorunlu.
Karar: ☐

**[B3]** (D4 §3) Stage-Gate sadece Enterprise mi, Pro'da da olmalı mı?
*Tavsiye:* Enterprise+. Pro daha sade kalmalı.
Karar: ☐

**[B4]** (D4 §6) ESG modülünün Pro paketinde "light" versiyonu yeterli mi?
*Tavsiye:* Evet, SBTi/TCFD Enterprise.
Karar: ☐

---

## C. MARKA & KONUMLANDIRMA (D8)

**[C1]** (D8-OS-1) Mevcut Kokpitim varlığı Kokpit Group'a mı dönüştürülecek, yoksa yeni varlık + devir mi?
*Tavsiye:* Hukuk/muhasebe danışmanlığı gerekli; tercih: yeni "Kokpit Group A.Ş." + Kokpitim devri.
Karar: ☐ Dönüştür ☐ Yeni varlık ☐ Hukuk görüşü bekle

**[C2]** (D8-OS-2) Sinaps tagline EN-only mi, yerelleştirilecek mi?
*Tavsiye:* EN birincil, TR/DE/FR/AR lokalize varyant.
Karar: ☐

**[C3]** (D8-OS-3) Logo/görsel kimlik: iç tasarım mı, dış stüdyo mu?
*Tavsiye:* Dış stüdyo (€20-40K) — Sinaps Enterprise için kalite kritik.
Karar: ☐ İç ☐ Dış ☐ Hybrid

**[C4]** (D8-OS-4) "by Kokpit Group" endorsement her ekranda mı?
*Tavsiye:* Sadece login + footer + about.
Karar: ☐

**[C5]** (D8-OS-5) Enterprise+ white-label F5+ mi yoksa hiç mi?
*Tavsiye:* F5+ değerlendirme; şimdi karar verme.
Karar: ☐

---

## D. FİYATLANDIRMA & GTM (P1)

**[D1]** (P1-OS-1) AB B.V. ne zaman kurulur?
*Tavsiye:* İlk AB müşteri sözleşmesinden 60 gün önce, proaktif olarak F3.
Karar: ☐ F1 ☐ F3 ☐ Müşteriye kadar bekle

**[D2]** (P1-OS-2) Kokpitim free trial 14 mü 30 gün mü?
*Tavsiye:* Mevcut conversion datasına bak; bilinmiyorsa 14 gün başla.
Karar: ☐ 14 ☐ 30 ☐ Veriye bak

**[D3]** (P1-OS-3) Sinaps "freemium" var mı?
*Tavsiye:* Hayır, POC modeli yeterli.
Karar: ☐

**[D4]** (P1-OS-4) Sinaps TR fiyatı TL'ye sabitlensin mi?
*Tavsiye:* Hayır — € fiyat üzerinden TL hesaplanır (kur riski).
Karar: ☐

**[D5]** (P1-OS-5) Partner komisyon modeli?
*Tavsiye:* Referral %15 / Reseller %25 / Sistem entegratörü görüşmeli.
Karar: ☐

**[D6]** (P1 §1) Fiyat seviyeleri (₺350/₺850 KOBİ, €24K/€60K Enterprise) onaylı mı?
*Tavsiye:* Müşteri görüşmesi + benchmark sonrası kesinleştir.
Karar: ☐ Onayla ☐ Revize

---

## E. ETL & MİGRASYON (P2)

**[E1]** (P2-OS-1) Migration paid mi ücretsiz mi?
*Tavsiye:* Implementation Pack'e dahil; bağımsız €5K eklenti.
Karar: ☐ Pack içinde ☐ Eklenti ☐ Y1 ücretsiz promo

**[E2]** (P2-OS-2) Birden çok Kokpitim tenant tek org çatısı altında birleşir mi?
*Tavsiye:* Müşteri tercihi; default ayrı tenant.
Karar: ☐

**[E3]** (P2-OS-3) Keycloak user import sırasında MFA reset zorunlu mu?
*Tavsiye:* Evet — güvenlik için.
Karar: ☐

**[E4]** (P2-OS-4) 30 gün sonra Kokpitim verisi otomatik silinsin mi?
*Tavsiye:* Müşteri onayıyla, sessiz silme yok.
Karar: ☐

**[E5]** (P2 §3) BCG/Ansoff/Proje/Görev kayıpları kabul mü?
*Tavsiye:* PDF arşiv yeterli; custom modül talebi €25K+.
Karar: ☐

---

## F. DESIGN & UX (P3)

**[F1]** (P3-OS-1) Figma team plan F1'de mi (€150/ay)?
*Tavsiye:* Evet, F1'de gerekli (tasarım-eng paylaşımı).
Karar: ☐

**[F2]** (P3-OS-2) Marka studio iç mi dış mı?
*Tavsiye:* Dış (€20-40K) — bkz C3.
Karar: ☐

**[F3]** (P3-OS-3) SweetAlert2 Sinaps'ta yer alır mı?
*Tavsiye:* Hayır — Cortex Toast yeterli.
Karar: ☐

**[F4]** (P3-OS-4) Dark theme Sinaps'ta default mı?
*Tavsiye:* User preference, sistem tercihini izle.
Karar: ☐ Default dark ☐ User pref ☐ Default light

---

## G. SRE & FINOPS (P4)

**[G1]** (P4-OS-1) PagerDuty mu Grafana OnCall mı?
*Tavsiye:* Grafana OnCall F1 (free), gerekirse upgrade.
Karar: ☐

**[G2]** (P4-OS-2) Status page Enterprise-only mı public mi?
*Tavsiye:* Public (güven sinyali).
Karar: ☐

**[G3]** (P4-OS-3) SLA credit otomatik mi manuel mi?
*Tavsiye:* F1 manuel, F3 otomatik.
Karar: ☐

**[G4]** (P4 §1.1) Uptime SLA seviyeleri (99.5/99.9/99.95) müşteriye söylenebilir mi?
*Tavsiye:* Evet, conservative; iç hedef daha yüksek.
Karar: ☐

---

## H. GÜVENLİK & UYUM (P5)

**[H1]** (P5-OS-1) DPO inhouse mı dış mı?
*Tavsiye:* F1 outsource (€600/ay), F4+ inhouse.
Karar: ☐

**[H2]** (P5-OS-2) Compliance platform: Vanta mı Drata mı?
*Tavsiye:* Drata (UI modern).
Karar: ☐ Vanta ☐ Drata ☐ Karşılaştır

**[H3]** (P5-OS-3) Bug bounty ne zaman?
*Tavsiye:* F5+ (yeterli olgunluk).
Karar: ☐

**[H4]** (P5-OS-4) Enterprise+ HYOK (customer encryption key) ne zaman?
*Tavsiye:* F5+ talep gelirse.
Karar: ☐

**[H5]** (P5-OS-5) AB Cloud Code of Conduct?
*Tavsiye:* F3'te adhere.
Karar: ☐

**[H6]** (P5 §5) SOC2 Type I 12. ay sonu mu erteleyebiliriz mi?
*Tavsiye:* AB Enterprise için zorunlu sinyal, kaymasın.
Karar: ☐

---

## I. TEST & KALİTE (P6)

**[I1]** (P6-OS-1) Chromatic F1 mi F2 mi?
*Tavsiye:* F2 (UI istikrar sonrası).
Karar: ☐

**[I2]** (P6-OS-2) Mutation test?
*Tavsiye:* Opsiyonel, sadece kritik domain.
Karar: ☐

**[I3]** (P6-OS-3) Müşteri POC sandbox ayrı tool mı?
*Tavsiye:* Aynı staging, sadece data izole.
Karar: ☐

**[I4]** (P6-OS-4) Performance bütçesi (Lighthouse) blocking mi?
*Tavsiye:* F1 warning, F3 blocking.
Karar: ☐

---

## J. ORG & HIRING (P7)

**[J1]** (P7-OS-1) Y1'de TR-only mu, AB hire açar mıyız?
*Tavsiye:* AB hire ay 4'ten, TR çoğunluk.
Karar: ☐

**[J2]** (P7-OS-2) ESOP havuzu yüzdesi?
*Tavsiye:* %10-15 — VC sözleşmesine bağlı.
Karar: ☐

**[J3]** (P7-OS-3) Maaş bandı kamuya açık mı?
*Tavsiye:* Dahili tam açık, JD'de range.
Karar: ☐

**[J4]** (P7-OS-4) Founding CSM ne zaman?
*Tavsiye:* Kurucular ay 6'ya kadar CS yapar, sonra hire.
Karar: ☐

**[J5]** (P7 §2) Y1 sonu 18 kişi hedefi gerçekçi mi?
*Tavsiye:* Funding'e bağlı; €1.1M burn karşılanabilirse evet.
Karar: ☐

---

## K. MOBILE & BETA (P8)

**[K1]** (P8-OS-1) Flutter alternatifi yeniden değerlendirilsin mi?
*Tavsiye:* Hayır — RN+Expo (kod paylaşımı).
Karar: ☐

**[K2]** (P8-OS-2) Mobile için ayrı brand?
*Tavsiye:* Hayır, tek "Sinaps".
Karar: ☐

**[K3]** (P8-OS-3) Kokpitim mobile yapılacak mı?
*Tavsiye:* Y2'de talep varsa.
Karar: ☐

**[K4]** (P8-OS-4) Founding customer programı (lifetime discount)?
*Tavsiye:* 5 closed beta'ya Y1 ücretsiz + Y2-3 %30.
Karar: ☐

**[K5]** (P8-OS-5) Open beta limit kaç (15 mi 25 mi)?
*Tavsiye:* CSM kapasitesine bağlı; başla 15, ölç, genişlet.
Karar: ☐

---

## L. GLOSSARY & DOCS & ANALYTICS (P9)

**[L1]** (P9-OS-1) Doküman çeviri sırası?
*Tavsiye:* TR/EN → AR (Körfez beta) → DE → ES/FR.
Karar: ☐

**[L2]** (P9-OS-2) PostHog F1 mi F2 mi?
*Tavsiye:* F1 sonu (geliştirici-tarafı, event şeması erken).
Karar: ☐

**[L3]** (P9-OS-3) Session replay default açık mı?
*Tavsiye:* Kapalı default, tenant opt-in.
Karar: ☐

**[L4]** (P9-OS-4) "PG" vs "KPI" terim standardı?
*Tavsiye:* Kokpitim "PG", Sinaps "KPI" — paket bazlı.
Karar: ☐

---

## ÖZET

**Toplam: 64 açık soru**
- A. Mimari: 13
- B. MVP kapsam: 4
- C. Marka: 5
- D. Fiyatlandırma: 6
- E. ETL: 5
- F. Design: 4
- G. SRE: 4
- H. Güvenlik: 6
- I. Test: 4
- J. Org: 5
- K. Mobile/Beta: 5
- L. Docs/Analytics: 4

---

## YOL HARITASI — KAPATMA ÖNCELİĞİ

**P0 (S0 bootstrap'den önce kapatılmalı):**
- A1.3, A1.4 (event bus, region topology)
- A2.3 (mobile framework)
- A3.1, A3.2, A3.3, A3.4 (Vault, OPA, GrowthBook, Turborepo)
- C1 (yasal yapı — uzun süreç)

**P1 (F1 başında — ilk 2 hafta):**
- B serisi (MVP kapsam onayı)
- D1, D2, D6 (AB B.V., free trial, fiyat seviyeleri)
- F serisi (Figma, brand studio)
- G1, G4 (PagerDuty/Grafana, uptime SLA)
- H1, H2 (DPO, compliance platform)
- L2 (PostHog F1 mi F2 mi)

**P2 (F2 öncesi — ay 3 sonu):**
- C2, C3, C4 (tagline, logo studio, endorsement)
- E serisi (ETL detayları)
- I serisi (test araçları)
- J serisi (org)

**P3 (F3-F4'te):**
- K serisi (mobile + beta detayları)
- H3, H4, H5 (bug bounty, HYOK, Cloud CoC)
- L1, L3 (çeviri sırası, session replay)

---

## ÖNERİLEN İŞLEM

1. Bu listeyi PDF/print → kurucu(lar) bir oturumda P0'ı tek tek karara bağlar (yaklaşık 60-90 dk)
2. P1'ler F1 başlangıcında haftalık review'larda kapanır
3. Karar verilen her madde "☐ → ☑ [karar]" işaretlenip, ilgili D/P doküman güncellenir
4. Karar günlüğü `docs/sinaps/DecisionLog.md` (her kararın tarihi + gerekçesi)
