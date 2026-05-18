# P8 — MOBILE DETAY · BETA PROGRAM
> Tarih: 2026-05-16 · Durum: TASLAK · Bağımlılık: D2 (ADR-15 mobile), D4 (X.1)

---

## 1. Mobile App: Sinaps Mobile (Kokpitim Mobile ileride)

### 1.1 Felsefe
- **Companion app, not equivalent.** Mobile, web'in karbon kopyası değil.
- **3 use case birinci sınıf:** OKR check-in, bildirim, hızlı insight bakışı.
- **Offline tolerant, online-first.** Çağrı içinde okur, geri dönünce yazar.
- **Single binary, multi-tenant.** Tenant switcher app içinde.

### 1.2 Teknik
- React Native + Expo (managed workflow başlangıç)
- TypeScript + same `@sinaps/api-client`
- Tamagui veya NativeWind (Tailwind-style)
- Expo Notifications (push)
- Expo Secure Store (token)
- Sentry (crash + perf)
- EAS Build + Submit (CI/CD)
- OTA updates: Expo Updates (her merge → staging channel, manuel → prod)

### 1.3 Ekran Envanteri (MVP — 12 ekran)

| # | Ekran | Amaç |
|--|--|--|
| 1 | Splash + Auth | Keycloak OAuth (in-app browser) |
| 2 | Tenant Picker | Federasyon kullanıcı için |
| 3 | Home / Today | Bekleyen check-in, son bildirim, KPI özeti |
| 4 | OKR List | Kendi OKR'ları + cascading parent görüntüsü |
| 5 | OKR Detail + Check-in | KR slider, confidence, 1-cümle not |
| 6 | KPI Quick View | Top 5 KPI status (yeşil/sarı/kırmızı + ikon) |
| 7 | Notifications | In-app feed, mark read, deeplink |
| 8 | Activity Feed | Son etkinlikler (filtreli) |
| 9 | Search (Cmd+K) | Global arama, sonuç → web yönlendir |
| 10 | Profile + Settings | Locale, push pref, MFA, logout |
| 11 | AI Concierge (chat) | LiteLLM, RAG'siz minimum |
| 12 | Approval Inbox | Stage-Gate veya catchball onay isteği |

### 1.4 Out of Scope (mobile — F5+)
- Strateji oluşturma (plan, pillar) — web only
- Hoshin X-Matrix editor
- EFQM detay
- Belge yükleme (görüntüleme OK)
- Yönetici/Admin panel
- Rapor üretimi

### 1.5 Push Bildirim Stratejisi
- **Her bildirimin "deeplink" hedefi var.**
- Türler: KR check-in hatırlatma, approval bekliyor, KPI eşik aşımı, yorum mention, AI sonucu hazır
- Frequency cap: gün başına 8, "do not disturb" saat (kullanıcı pref)
- Opt-in iki seviyeli (OS + uygulama içi tip-bazlı)

### 1.6 Offline Davranışı
- Read: son fetch cache (SQLite via Expo)
- Write: OKR check-in optimistic + queue → online'da sync
- Conflict: server kazanır + kullanıcıya uyarı

### 1.7 Performans Hedefi
- App cold start <2s
- Liste render 100 item <300ms
- Crash-free session >99.5%
- Bundle size <12 MB (initial download)

### 1.8 Store Yayın Stratejisi
- **iOS:** App Store, ad: "Sinaps", kategori: Business
- **Android:** Play Store, aynı ad
- Erken erişim: TestFlight + Play Internal (beta kullanıcıları)
- Görsel: 5 screenshot + 30sn video
- Privacy nutrition label: data toplam minimum
- Apple/Google review süresi tampon: 7-14 gün

### 1.9 Geliştirme Takvimi
- **F1:** mobile yok (web odak)
- **F3 ortası:** PoC build (login + OKR list + check-in)
- **F4:** tam 12 ekran, OTA, beta TestFlight
- **F4 sonu / F5 başı:** Public release v1.0
- **Y2 Q1:** v1.5 (offline iyileştirme, ek dil)

### 1.10 Bakım
- Mobile eng (1 kişi F3+, F4'te tam zamanlı)
- iOS + Android paralel; %95 kod ortak
- 4 haftada 1 release tipik

---

## 2. Beta Program

### 2.1 Amaç
- Gerçek dünya doğrulaması (Tomofil + sentetik yetmez)
- Ürün-pazar uyumu sinyali
- Erken case study + referans
- Bug + UX feedback (sterilizede yakalayamadıklarımız)

### 2.2 Faz Yapısı

#### Alpha (kapalı, sadece içeride) — F2 sonu
- 5-8 kullanıcı (tamamen çalışanlar + kurucular)
- "Kendi şirketimizi yönet" senaryosu (gerçek OKR'ımız)
- Süre: 4 hafta
- Hedef: kritik bug yakalama, UX trip-up

#### Closed Beta (davetli, ücretsiz) — F4 başı (~ay 9)
- 5-8 müşteri (Sinaps Enterprise hedefli)
- TR'den 3-4 holding + AB'den 1-2 + 1 Tomofil-benzeri büyük müşteri
- NDA + heyecanlı CEO/CSO desteği
- Süre: 8 hafta
- Hedef: gerçek kapsamda kullanım, fiyatlandırma sinyali

#### Open Beta / Limited GA (ücretli, indirimli) — F4 sonu (~ay 12)
- 15-25 müşteri
- %50 indirim Y1 (early adopter)
- Logo kullanım izni karşılığında
- Süre: 12 hafta
- Hedef: ölçek doğrulama, GTM iyileştirme

#### General Availability — Y2 başı
- Tam fiyat
- Public launch

### 2.3 Beta Seçim Kriterleri
- Hedef segmentle uyum (Enterprise: 1000+ çalışan, holding yapı bonus)
- C-suite sponsor (CSO/COO/CFO destekçi)
- Strateji ofisi var (Hoshin/OKR aşinalığı bonus)
- Referans olmaya istekli
- Reasonable bug toleransı (sözleşmede beklenti net)

### 2.4 Beta Sözleşmesi
- Standart MSA + Beta Annex
- Ücret: closed = 0, open = %50
- SLA: best-effort (full SLA yok)
- Termination: 30 gün notice (her iki taraf)
- Data export: her zaman
- Beta sonunda: paid'e geçiş veya çıkış

### 2.5 Beta Operasyonu

**Onboarding (her beta müşteri):**
- Kickoff workshop (2 saat)
- Dedicated Slack Connect kanalı
- CSM weekly check-in
- Bug triage <24h
- Feature request log (Linear) — transparent

**Geri Bildirim Toplama:**
- In-app NPS survey (haftalık)
- 30-day deep interview (1h)
- Session replay (Pendo/FullStory) — opt-in
- Customer Advisory Board (CAB) — 3 ayda 1 (beta sonu)

**Communication Cadence:**
- Weekly update e-postası (yenilikler, bilinen sorunlar)
- Monthly roadmap özet
- Quarterly executive report

### 2.6 Beta Çıkış Kriterleri (Beta → GA)
1. Closed beta'da 5+ müşteri "günlük aktif" (haftada 3+ gün)
2. NPS >40
3. Sev1 bug 30 gün içinde 0
4. Tomofil kabul testi %100 (P6 §8)
5. SOC2 Type I in-progress
6. SLA 99.9% son 30 gün
7. At least 2 case study yayınlanabilir

### 2.7 Risk
| Risk | Önlem |
|--|--|
| Beta müşteri churn (ürün hazır değil) | Sıkı seçim + active hand-holding |
| Beta scope creep (her isteği yapma) | PM gate, "Y1 roadmap" disiplin |
| Beta = ücretsiz danışmanlık olur | Süre net, Implementation Pack ayrı |
| Beta feedback temsili değil | Çeşitli sektör + ülke + boy karışım |
| Beta müşteri public konuşmuyor | NDA muhafazakar; case study opt-in |

---

## 3. Lansman Planı (GA)

### 3.1 GA Tarihi Tahmini
- Sinaps: ~Y1 sonu / Y2 başı
- Kokpitim: zaten canlı, sürekli güncel

### 3.2 Lansman Aktiviteleri
- Public press release (TR + AB tech medya)
- LinkedIn lansman kampanya (CEO posts)
- ProductHunt launch (B2B SaaS değil ama awareness)
- 3 case study yayın (Tomofil-virtual + 2 gerçek beta)
- Lansman etkinliği: İstanbul + sanal (1 saat keynote + demo)
- 1 hafta promo: %20 ilk yıl indirim (Pro/Enterprise)

### 3.3 Lansman Sonrası 90 gün
- Haftalık metrik review (sales + product + ops)
- Hızlı iter, müşteri geri bildirimi → roadmap
- F5 planlama (forecast engine, ERP connector, vb.)

---

## 4. Açık Sorular
- OS-1: Flutter alternatif mi? — Karar: RN+Expo (D2 ADR-15)
- OS-2: Mobile için ayrı brand mi? — Hayır, "Sinaps" tek isim
- OS-3: Kokpitim mobile yapılacak mı? — Y2 değerlendirme (önce müşteri talep)
- OS-4: Beta için "founding customer" programı (lifetime discount)? — Önerim: 5 closed beta müşteriye Y1 ücretsiz + Y2-Y3 %30 indirim
- OS-5: Open beta limit ne (15 mi 25 mi)? — Operasyonel kapasiteye bağlı, CSM 1 → 12 müşteri ölçek
