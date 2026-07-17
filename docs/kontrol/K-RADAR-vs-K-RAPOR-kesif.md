# K-Radar ↔ K-Rapor ↔ K-Analiz / Performans Analitiği — Keşif Raporu

> Soru: Bu modüllerin farkı nedir? Anlamlı bir bölünme olmuş mu? Öneriler?
> Yöntem: Modüller paralel ajanlarla derinlemesine okundu (kod, tahmin değil),
> bulgular DB + route + template + SIDEBAR ölçümüyle çapraz doğrulandı.
> Tarih: 2026-07-17 · Ölçek: K-Radar 88 route / 7 dosya · K-Rapor 35 route · analiz 7 route

---

## BÜTÜN RESİM: 3 katmanlı görünüm mimarisi (üretici → teşhis → rapor)

Keşif derinleştikçe ortaya çıktı: bu bir "iki modül" meselesi değil. Aynı veri
(SWOT, EVM, paydaş, risk…) **üç katmanda** görünüyor, her katmanın rolü farklı:

```
SP (Stratejik Planlama, 127 route)     ÜRETİR + YÖNETİR (CRUD)
  └─ SWOT/TOWS/PESTEL/OKR/BSC yazar    → db.session.add (routes_analysis.py:232)
        │
        ▼
K-Radar (88 route)                     TEŞHİS EDER (canlı gösterir)
  └─ /k-radar/ks aynı SWOT'u sp_api ile çeker (routes_ks.py:142, get_ks_swot_real)
        │  "neredeyiz, neyi düzeltelim?"
        ▼
K-Rapor (35 route)                     RAPORLAR + DAĞITIR
  └─ /k-rapor?tab=stratejik-analiz konsolide eder, PDF/Slack ile dışa aktarır
```

**Kanıt (SWOT örneği):** SP yazar (`sp/routes_analysis.py:232` `db.session.add`),
K-Radar okur (`k_radar/routes_ks.py:142` salt query), K-Rapor konsolide eder.
Aynı kalıp EVM (`EvmSnapshot`), paydaş (`StakeholderMap`) için de doğrulandı.

**Bu örtüşme DEĞİL, katmanlı mimari** — teknik olarak sağlam. Sorun: kullanıcı
aynı SWOT'u üç yerde görüp "neden üç kez var?" diyor. Katmanların rolü isimde
görünmüyor.

---

## "K-Analiz" diye ayrı bir modül YOK

Sidebar'da kullanıcının gördüğü üç giriş, gerçekte iki modüle gidiyor:

| Menüde görünen isim | Gittiği route | Gerçekte ne |
|---|---|---|
| **"K-Radar"** | `k_radar_hub` | K-Radar hub |
| **"K-Analiz"** | `k_radar_ks` | **Yine K-Radar** (strateji girişi) — AYRI MODÜL DEĞİL |
| **"Performans Analitiği"** | `/analysis` (`analiz` modülü) | Ayrı 7-route modül (bugünkü `/analysis`) |

**"K-Analiz" = K-Radar'ın ikinci bir menü adı.** `base.html:217` sidebar girişi
`k_radar_ks`'e gidiyor; K-Radar'ın breadcrumb'ları da (`cross.html`, `kp.html`,
`kpr.html`) "K-Analiz" diyor. Yani K-Radar kod içinde bir yerde "K-Radar", başka
yerde "K-Analiz" olarak anılıyor — **tek modül, iki isim, iki sidebar girişi.**

Ayrıca `/analysis` modülü de kendi içinde (`analiz/index.html:63`) "K-Analiz"
butonu taşıyor ama o da `k_radar_ks`'e link veriyor. Ve sidebar'daki adı
"Performans Analitiği", sayfa başlığı "Performans Göstergeleri" (bugünkü soru).
→ **Bir sayfa üç ad taşıyor; bir modül iki menü girişiyle görünüyor.**

Bu, "anlamlı bölünme mi" sorusunun asıl cevabı: **modüllerin işi ayrık, ama
isimlendirme katmanı çökmüş.** Kullanıcı üç isim görüp üç ürün sanıyor; altında
iki modül var.

---

## Kısa cevap

**Bölünme ANLAMLI — ama isimlendirme çökmüş, sınır kullanıcıya görünmüyor.**

Modüller aynı işi yapmıyor; gerçek bir **üretici → tüketici** ilişkisi var:

- **K-Radar** (menüde "K-Radar" + "K-Analiz") = veriyi *üretir, teşhis eder* → "neredeyiz, neyi düzeltelim?"
- **K-Rapor** = o veriyi *kurum geneli konsolide eder, dışa aktarır* → "tüm resmi göster, raporla, dağıt"
- **Performans Analitiği** (`/analysis`) = süreç bazlı health/trend/forecast/anomali → kimliği en zayıf, ikisiyle de örtüşüyor

Sorun ayrımın kendisinde değil, **isimlendirmede ve kullanıcının bu ayrımı görememesinde.**

---

## Kanıtlanmış farklar (ölçümle)

| Eksen | K-Radar | K-Rapor |
|---|---|---|
| **Rol** | Üretici — veri yazar (CRUD) | Tüketici — okur, konsolide eder |
| **Girdi birimi** | Süreç / proje / strateji (derin dalış) | **Kurum geneli** (tenant); hatta tenant-arası |
| **Çıktı** | Canlı teşhis paneli (radar, heatmap, örümcek grafik) | 33 canlı JSON ekran + **Excel/PDF export + Slack/mail dağıtım** |
| **Zaman ekseni** | Şimdi + trend ("neredeyiz") | Geçmiş + şimdi + **gelecek** (forecast, anomali) |
| **Analiz motoru** | Canlı SQL + skor formülleri; forecast/anomali YOK | Aynı motorları + **forecast_service, anomaly_service** |
| **Kendi hub'ı** | Var (`/k-radar`) | **YOK** — tab'sız `/k-rapor` K-Radar'a redirect eder |

## Çakışma gerçek mi? — HAYIR, katmanlı

Yüzeyde aynı konular iki yerde: EVM, paydaş, rekabet, risk, SWOT. Ama ölçüldü:

- **EVM**: `EvmSnapshot` modeli K-Radar'ın domain'i. K-Radar üretir; K-Rapor sadece **okur** (`k_rapor/routes.py:1166`, salt query).
- **Paydaş**: K-Radar **CRUD yapar** (`k_radar/routes_cross.py:169`); K-Rapor sadece **okur** (`k_rapor/routes.py:1314`).

Yani örtüşme değil — **K-Radar veriyi üretir, K-Rapor tüketir.** Sınır teknik olarak temiz.

---

## Ne yapar? (tek cümlelik kimlikler)

**K-Radar:** Kurumun strateji (KS) · süreç-performans (KP) · proje (KPR) · risk katmanlarını 20+ yönetim çerçevesiyle (SWOT, EFQM, OEE, VSM, EVM, CPM, BCG…) canlı SQL üzerinden skorlayıp örümcek-grafik/heatmap gösteren, kural-tabanlı yönetici aksiyonu öneren **kurumsal olgunluk & risk teşhis paneli**.

**K-Rapor:** Aynı verileri kurum (tenant) geneli için ~33 canlı ekranda konsolide eden, üzerine **forecast/anomali** ekleyen ve **Excel/PDF/Slack/mail** ile dışa aktaran **raporlama & dağıtım katmanı**.

### K harfleri (netlik için)
- **KS** = K-Strateji · **KP** = K-Performans/Süreç · **KPR** = K-Proje · **cross** = katmanlar-arası · **risk** = RAID

---

## Sorun: bölünme anlamlı ama kullanıcı göremiyor

1. **İsimler ayrımı anlatmıyor.** "Radar" ve "Rapor" kulağa benzer/eşdüzey geliyor; oysa biri *teşhis*, diğeri *konsolidasyon+dağıtım*. Kullanıcı "trendime nereden bakayım?" diye soruyor (bugün `/analysis` sorusu tam buydu).

2. **Sidebar'da iç içe.** `base.html:207` — tek koşul hem `k_radar` hem `k_rapor`'u kontrol ediyor; menüde ayrımları bulanık.

3. **K-Rapor'un hub'ı yok**, K-Radar'a redirect ediyor → zaten yarı-birleşmişler ama bu belirsiz, yarım kalmış bir birleşme.

4. **Üçüncü bir kopya var: `/analysis` (Analiz).** Bugün ölçtük — health/trend/forecast/anomali'yi süreç bazında yapıyor; K-Rapor'un `kpi_id` bazlı forecast/trend'iyle ve K-Radar'ın süreç teşhisiyle örtüşüyor. Kimliği en zayıf olan bu.

---

## Öneriler (öncelik sırasıyla)

### 1. İsim kazasını çöz — EN ÖNCELİKLİ, en ucuz, en etkili
Asıl sorun bu. Üç ad, iki modül, çakışan etiketler. Karar verilmesi gereken:
- **"K-Analiz" menü girişi ne olacak?** K-Radar'a giden ikinci giriş. Ya kaldır
  (K-Radar zaten var), ya da K-Radar'ın alt-bölümü olduğu belli olacak şekilde
  girintili yap. Bugünkü hali kullanıcıyı "ayrı ürün" sanmaya itiyor.
- **`/analysis` sayfasının tek adı olsun.** Şu an üç ad: sidebar "Performans
  Analitiği", başlık "Performans Göstergeleri", iç buton "K-Analiz". Biri seçilip
  üçü de ona eşitlenmeli.
- **K-Radar ↔ K-Rapor rolleri isimde görünsün:** ör. K-Radar → "Teşhis",
  K-Rapor → "Raporlar & Dağıtım". Kod değişmez, sadece etiket.

### 2. `/analysis` (Performans Analitiği) sayfasını KARARA bağla — kimliği en zayıf
Süreç bazlı health/trend/forecast/anomali yapıyor; hem K-Radar (süreç teşhisi)
hem K-Rapor (forecast/anomali) ile örtüşüyor. Üç seçenek:
- K-Radar'ın "süreç" sekmesine taşı, **veya**
- K-Rapor'un forecast/anomali'siyle birleştir (aynı motoru çağırıyorlar), **veya**
- Net bir adla ("Süreç Analitiği") kimlik verip yerinde bırak.
Öneri: **paketleme turunda** karara bağla — üçü de aynı motorları paylaşıyor,
kör silme kayıp olur.

### 3. Sidebar yapısını düzelt
- `base.html:217` — "K-Analiz" girişi K-Radar'a gidiyor; ayrı giriş gibi durmasın.
- `base.html:207` — iç içe `k_radar`/`k_rapor` koşulunu ayır; K-Radar ile K-Rapor
  menüde ayrı, rolleri belli iki giriş olsun.

### 4. K-Rapor'un hub redirect'ini bilinçli karara bağla
`k_rapor/routes.py:88` — tab'sız `/k-rapor` K-Radar'a redirect ediyor. Ya tam
birleştir (K-Rapor = K-Radar'ın bir sekmesi), ya kendi hub'ını ver. Şu anki
"yarı redirect" belirsiz, yarım kalmış bir birleşme.

---

## Yapılmaması gereken

**Modülleri kör birleştirme/silme.** Ölçüldü: ayrım teknik olarak temiz (üretici→tüketici). Sorun mimari değil, **sunum**. Kodu yeniden yazmak değil, etiketleri ve navigasyonu düzeltmek gerekiyor. Bu ayrıca kullanıcının süregelen **paketleme/segmentasyon** işinin parçası — orada bütün olarak ele alınmalı.
