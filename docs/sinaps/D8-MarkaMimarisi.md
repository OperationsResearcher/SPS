# D8 — SİNAPS MARKA MİMARİSİ ÖNERİSİ v1.0
> Kokpit Group umbrella + Kokpitim (KOBİ) + Sinaps (Enterprise)
> Tarih: 2026-05-16
> Durum: TASLAK — onay bekliyor
> Bağımlılık: D1 (PRD), D4 (Modül Kataloğu), D5 (Repo)

---

## 1. Marka Mimarisi Modeli

**Seçilen model: Branded House + Endorsed Sub-Brands** ("Kokpit Group" çatısı altında iki ayrı ürün markası, kurumsal endorsement ile).

```
                  ┌──────────────────────┐
                  │     KOKPİT GROUP     │  ← Kurumsal (B2B/B2I)
                  │   (umbrella brand)   │     Yatırımcı, kurumsal ortaklık, hukuk
                  └──────────┬───────────┘
                             │ endorses
              ┌──────────────┴──────────────┐
              ▼                             ▼
   ┌────────────────────┐         ┌────────────────────┐
   │     KOKPİTİM       │         │      SİNAPS        │
   │ "by Kokpit Group"  │         │ "by Kokpit Group"  │
   │ Segment: KOBİ      │         │ Segment: Enterprise│
   │ Ton: yakın, hızlı  │         │ Ton: kurumsal, güç │
   └────────────────────┘         └────────────────────┘
```

**Neden bu model (House of Brands veya tek monolit yerine):**
- Kokpitim'in mevcut müşteri ilişkisi ve ismi korunur — yeniden adlandırma maliyeti yok
- Sinaps Enterprise alıcısına net konum: "bu KOBİ ürününün büyük versiyonu değil; ayrı bir ürün"
- Aynı şirketin güveni iki ürüne taşınır (endorsement)
- Gelecekte ek ürün eklenebilir (Kokpit Insights, Kokpit Compliance…)

---

## 2. Kurum Adı: Kokpit Group

| | |
|-|-|
| **Yasal ad (öneri)** | "Kokpit Group" + ülke uzantısı (A.Ş./B.V./Inc., yasal yapılanmaya göre) |
| **Marka kullanımı** | "Kokpit Group" — kurumsal iletişim, sözleşme, fatura kafası, GitHub org, çalışan email domain'i |
| **Tagline** | "Strategy. Execution. Sustainability." (EN birincil) / "Stratejiyi yönetilebilir kılar." (TR) |
| **Domain** | `kokpitgroup.com` (kurumsal site), `kokpit.io` (developer/blog) |
| **GitHub org** | `kokpit` (sade) |
| **Email** | `*@kokpitgroup.com` |

> İsim notu: "Kokpitim" Türkçe karakter (i) ve sahiplik eki içerir; uluslararası kurumsal kimlikte "Kokpit Group" daha temiz okunur. Ürün markaları yerel/uluslararası farkını taşır.

---

## 3. Ürün Markaları

### 3.1 Kokpitim

| | |
|-|-|
| **Tam ad** | "Kokpitim — by Kokpit Group" |
| **Segment** | KOBİ (10–250 çalışan), Türkiye birincil pazar |
| **Konum** | "KOBİ'nin strateji & icra panosu. Bir kahve molasında planını kur." |
| **Paket** | Starter, Pro |
| **Dil önceliği** | Türkçe birinci |
| **Ton** | Yakın, sade, hızlı, dürüst |
| **Renk paleti** | Sıcak, dinamik (turuncu/lacivert spektrumu — mevcut kimliği koru) |
| **Domain** | `kokpitim.com` (mevcut) |
| **Hedef müşteri** | Aile şirketleri, sektör KOBİ'leri, mikro ihracatçılar, küçük serv. firmaları |

### 3.2 Sinaps

| | |
|-|-|
| **Tam ad** | "Sinaps — by Kokpit Group" |
| **Segment** | Enterprise (1000+ çalışan), holding, çok uluslu |
| **Konum** | "Stratejiden risk yönetimine, sürdürülebilirlikten icraya — kurumun bilişsel işletim sistemi." |
| **Paket** | Enterprise, Enterprise+ |
| **Dil önceliği** | İngilizce birinci (TR/AR/DE/FR/ES… 23 dil) |
| **Ton** | Kurumsal, kanıt-odaklı, güven, derin |
| **Renk paleti** | Soğuk, derin (lacivert/grafit + tek vurgu rengi — neon morumsu mavi önerisi) |
| **Domain** | `sinaps.app` (ana ürün), `sinaps.kokpitgroup.com` (kurumsal sayfa) |
| **Hedef müşteri** | Holding HQ, CSO/CFO ofisleri, kurumsal strateji birimleri, ESG ekipleri |

**İsim "Sinaps" anlam yükü:** sinaps (synapse) = nöronlar arası bağlantı; ürünün "strateji–icra–süreç–risk–ESG modüllerini birbirine bağlayan dokular" konumlandırmasıyla örtüşür. Telaffuzu TR/EN ortak, alan adı temiz (`.app`).

---

## 4. Tek Cümle Konumlandırma (Positioning Statement)

**Kokpitim:**
> "KOBİ yöneticileri için, strateji ve KPI takibini 30 dakikada başlatan; tek sayfa pano, tek kişi giriş ihtiyacı duyan, Türkçe-birinci SaaS strateji panosudur."

**Sinaps:**
> "Çok-kiracı holding ve çok uluslu kurumlar için; OKR cascading, Hoshin Kanri, EFQM, COSO ERM, TCFD/SBTi ve 14 uçtan uca süreci tek RLS-izole platformda birleştiren; bulut-bağımsız ve AI-Concierge destekli kurumsal strateji işletim sistemidir."

---

## 5. Müşteri Konuşmasında Net Sınırlar

| Soru | Cevap |
|------|-------|
| "Kokpitim Sinaps'ın küçük versiyonu mu?" | Hayır. İki ayrı ürün. Aynı şirketin (Kokpit Group) iki segmenti. |
| "Kokpitim'den Sinaps'a yükseltebilir miyiz?" | Evet — one-time ETL migration. Ama otomatik upgrade yok; karar müşterinin. |
| "Aynı kullanıcı her ikisinde de var mı?" | Hayır. SSO mümkün ama lisans ayrı. |
| "Sinaps'ı 50 kişilik şirket alabilir mi?" | Teknik olarak evet, fiyatlandırma uygun değil. Kokpitim Pro öner. |
| "Kokpitim'i 5000 kişilik holding alabilir mi?" | Hayır. Federasyon yok. Sinaps Enterprise+. |

---

## 6. Görsel Kimlik İlkeleri (yön — final tasarımcı işi)

### 6.1 Kokpit Group (umbrella)
- Logo: kelime markası (wordmark) + minimal sembol (kokpit metaforu — daire/gösterge motifi)
- Renk: nötr, kurumsal (grafit + beyaz + tek vurgu)
- Tipografi: modern grotesk (Inter, Söhne, ya da custom)
- Kullanım: sadece kurumsal context (about, careers, investors, legal footer)

### 6.2 Kokpitim
- Mevcut görsel kimlik korunur; sadece "by Kokpit Group" endorsement satırı eklenir
- Marketing toninde değişiklik yok (yakın, hızlı)

### 6.3 Sinaps
- Yeni görsel kimlik
- "Sinaps bağlantı/nöron" metaforu — minimal grafiksel ifade
- Çok-dilli kullanım için tipografi: Latin + Arabic + CJK desteği
- Karanlık tema birinci sınıf (Enterprise C-suite alışkanlığı)

---

## 7. Marka Hiyerarşisi Kullanım Kuralları

### 7.1 Üründe (Sinaps UI)
- Login ekranı: "Sinaps" büyük + "by Kokpit Group" küçük altyazı
- Footer: "© 2026 Kokpit Group. All rights reserved."
- About sayfası: Kokpit Group + Sinaps ilişkisi anlatımı

### 7.2 Hukuki / Faturalama
- Müşteri sözleşmesi: "Kokpit Group [yasal varlık]"
- Fatura kafası: Kokpit Group
- Ürün adı sözleşme metninde: "Sinaps" / "Kokpitim"

### 7.3 İletişim / Sosyal
- @KokpitGroup — kurumsal hesap (LinkedIn, X)
- @Sinaps_App — ürün hesabı (X, LinkedIn product page)
- @Kokpitim_TR — Türkiye/KOBİ pazarı hesabı

### 7.4 Repo / GitHub
- Org: `kokpit`
- Repo: `kokpit/sinaps` (Sinaps codebase)
- Repo: mevcut Kokpitim repo'sunun ismi/sahipliği değiştirilecekse ayrı karar (D8 dışı)

### 7.5 Email Subdomain
- `noreply@kokpitgroup.com` — kurumsal sistem
- `noreply@sinaps.app` — Sinaps transactional (kullanıcı içeride bunu görür)
- `noreply@kokpitim.com` — Kokpitim transactional

---

## 8. Çoklu Marka Risklerine Karşı

| Risk | Önlem |
|------|-------|
| İki ürün karıştırılır | Hiçbir landing page'de "diğer ürünümüz X" yan yana gösterilmez; segment ayrımı net |
| İki kod tabanı = iki ekip = iki katı maliyet | İlk yıl: aynı çekirdek ekip; F1–F4 sonrası ürün-odaklı küçük ayrım |
| Kokpit Group adının pazarda tanınmaması | İlk 12 ay umbrella marka düşük profilli; ürünler öne; sonra umbrella iletişimi |
| Domain karmaşası | Tek "marka sayfası" `kokpitgroup.com` → her iki ürüne yönlendirme |
| Müşteri "fiyat fark yok niye iki marka" der | Modül kataloğu × paket matrisi (D4 §10) net cevap — özellik seti açıkça farklı |

---

## 9. Migrasyon: Eski "Kokpitim" Görseli → Yeni Mimari

- **Adım 1 (hemen):** Mevcut Kokpitim sitesine ufak "by Kokpit Group" endorsement bandı ekle (kod değişikliği minimal)
- **Adım 2 (F0 sonu):** `kokpitgroup.com` ana kurumsal site canlı — Kokpitim ve Sinaps ürün sayfalarına yönlendirme
- **Adım 3 (F2):** Sinaps marketing sitesi → `sinaps.app` canlı
- **Adım 4 (F4):** Tam marka geçişi tamamlanır; iletişim & basın materyali güncel

---

## 10. Tescil ve Yasal Adımlar (kontrol listesi)

- [ ] "Kokpit Group" şirket adı uygunluk (Türkiye Ticaret Sicili)
- [ ] "Kokpit Group" wordmark — TR + EUIPO + USPTO marka başvurusu
- [ ] "Sinaps" wordmark — TR + EUIPO + USPTO (sınıf 9, 42)
- [ ] "Kokpitim" mevcut tescil durumu inceleme & yenileme
- [ ] Domain alımları: `kokpitgroup.com`, `sinaps.app`, defensive (`.io`, `.co`, yaygın TR/AB TLDs)
- [ ] Sosyal medya handle rezervasyonu
- [ ] Marka kullanım kılavuzu (brand guidelines PDF — F0 sonu)

---

## 11. Açık Sorular

- **OS-1:** Mevcut "Kokpitim" yasal varlığı Kokpit Group'a mı dönüştürülecek, yeni varlık kurulup Kokpitim ürünü buraya devredilecek mi? (Hukuk/muhasebe tavsiyesi gerekli)
- **OS-2:** Sinaps tagline'ı EN-only mı, yerelleştirilecek mi?
- **OS-3:** Logo/görsel kimlik için iç tasarım mı, dış stüdyo mu?
- **OS-4:** Sinaps "by Kokpit Group" endorsement gerçekten her ekranda mı, yoksa sadece login/footer'da mı? (Enterprise C-suite "umbrella" görmeyi sever — önerim: footer + about)
- **OS-5:** Premium tier "Sinaps Enterprise+" için custom branding (white-label benzeri) ileride mi? (Şimdilik: hayır, F5+)

---

## 12. Faz-0 Kapanışı

D1 → D8 tamamlandı. Sıradaki adımlar (Faz-1 başlangıcı):

1. **Repo bootstrap** — D5 §11 checklist (10 madde, ilk 2 hafta)
2. **D8 §11 açık soruları** kullanıcı ile kapatma
3. **Marka tescil başlangıcı** (paralel, yasal süreç uzun)
4. **F1 sprint planı** — M-CORE 1.1–1.12 alt-modülleri 12 haftaya bölme
5. **OPA Rego policy bundle iskeleti** (ADR-09)
6. **Helm chart iskeleti** (cloud-agnostic deploy)

---

## 13. Onay

Onaylanırsa **Faz-0 tamamlanır**; Faz-1 (Platform — multi-tenant infra, CORE, Keycloak, i18n, DevOps) başlar.

Kullanıcı onayı: ☐ Onaylandı ☐ Revizyon istendi
