# HAM BULGU — Stratejik Planlama Metodolojisi

> Kaynak: paralel SP gurusu (BSC, Hoshin, OKR, EFQM, SWOT/TOWS, VRIO, Blue Ocean, EVM)
> Tarih: 2026-07-21 · **M1 ana oturumda gerçek DB kaydıyla çalıştırılarak doğrulandı**

**Genel değerlendirme:** Çerçevelerin **veri modeli şaşırtıcı derecede sağlam** — VRIO karar
ağacı, EVM formülleri, EFQM 2025 ağırlıkları kitabına uygun. Sorunlar modelde değil,
**hesap katmanında ve kavramların birbirine bağlanmamasında**.

---

## M1 — Başarı puanı aralıklarının %64,6'sı sessizce ölü ✅ ANA OTURUMDA DOĞRULANDI · KRİTİK

`app/utils/karne_hesaplamalar.py:11-62`

İki JSON formatı yan yana yaşıyor; parser yalnız eskiyi tanıyor.

### Ana oturumda gerçek DB kaydıyla test

```
YENİ format (1240 kayıt):
  ham     : [{"min": 132.0, "max": null, "puan": 100}, {"min": 120, ...
  parse   : {}                      ← BOŞ
  puan(50): None                    ← PUAN ÜRETMİYOR

ESKİ format (680 kayıt):
  ham     : {"1":"%71-80","2":"81-90","3":"91-100","4":"-","5":"-"}
  parse   : {1:'%71-80', 2:'81-90', ...}
  puan(50): 1                       ← ÇALIŞIYOR
```

| Format | Kayıt | Durum |
|---|---|---|
| `[` ile başlayan (yeni) | **1240** | ❌ puan üretmiyor |
| `{` ile başlayan (eski) | 680 | ✅ çalışıyor |

**%64,6'sı ölü.**

`_normalize_basari_cell` bu sözlüklerde `aralik`/`range` anahtarını arıyor, bulamıyor, `None` dönüyor.

> **Kritik ayrıntı:** Hiçbir Python dosyası `min`/`max`/`puan` anahtarlarını yazmıyor ya da
> okumuyor — format yalnızca **JS tarafında** (`pg_tablo_modal.js`, `surec.js`) üretilip
> kaydedilmiş. Backend bu formatın varlığından habersiz.

**Etki:** Kullanıcı performans bandı tanımlıyor, sistem yok sayıyor. Hata **iz bırakmadığı için**
sessiz kaldı.

**Öneri:** `_normalize_basari_cell`'e `min`/`max`/`puan` şeklini ekle. **Kritik olarak:** parse
boş dönerken kaynak string doluysa `app.logger.warning` bırak — bu hata iki yıl sessiz kaldı
çünkü hiçbir yerde iz düşmüyordu.

---

## M2 — `data_collection_method='AVG'` hiçbir dala düşmüyor · YÜKSEK

`score_engine_service.py:~205` — toplulaştırma üç Türkçe etikete göre seçiliyor:

```python
if method in ('Toplama','Toplam'): actual = sum(...)
elif method == 'Son Değer':        actual = actual_values[0]
else:                              actual = ortalama
```

DB'de **dördüncü değer var: `AVG` (35 aktif PG)** → `else` dalına düşüp **tesadüfen** doğru
sonuç veriyor. Birisi `SUM` yazarsa sessizce ortalama alınır ve kimse fark etmez.

**DB:** `Ortalama` 1747 · `Toplama` 493 · `Son Değer` 124 · **`AVG` 35**

> Yanlış toplulaştırma stok-akım karışmasına yol açar: "yıllık satış" göstergesini
> ortalamak 12 kat küçültür.

---

## M3 — Ağırlıklar hiyerarşinin üst üç katmanında yok sayılıyor · YÜKSEK

Ağırlıklandırma yalnız **en alt iki katmanda** uygulanıyor. Yukarısı düz ortalama:

```python
sub_strategy_scores[ss.id] = round(total / n_linked, 2)   # süreç ağırlığı yok
strategy_scores[st.id]     = round(total / n_alts,   2)   # alt strateji ağırlığı yok
vision                     = round(total / n_strat,  2)   # strateji ağırlığı yok
```

40 süreçle desteklenen ana strateji ile tek süreçli strateji vizyona **eşit** katkı yapıyor.
`contribution_pct` alanı klasik motorda hiç okunmuyor.

**DB:** 13 kurumun yalnız **4'ünde** `k_vektor_enabled=true` → çoğunluk ağırlıksız ölçülüyor.

> Kaplan & Norton'da ve çok kriterli karar analizinde hedef ağırlıkları stratejik önceliğin
> birincil ifadesidir. Eşit ağırlık *bir seçimdir* ama bilinçli ve görünür olmalı.

---

## M4 — "Ölçüm yok" ile "başarısız" ayrılmıyor · YÜKSEK

Süreç katmanında doğru yapılmış (KPI'sız süreç `None` → dışlanıyor), üst katmanlara taşınmamış:

```python
if not linked_processes: sub_strategy_scores[ss.id] = 0.0
if not alts:             strategy_scores[st.id]     = 0.0
```

**DB:** Aktif alt stratejilerin **210'unda** hiç süreç bağı yok → her biri vizyona **0** olarak giriyor.

> Eksik veri ile sıfır performans farklı şeylerdir. Ölçülmemişi sıfır saymak, kurumu
> **yapılandırma eksikliği için cezalandırır** ve skoru yorumlanamaz kılar.

*(B1 ile aynı kök neden — iki uzman bağımsız olarak buldu.)*

**Öneri:** `None` semantiğini yukarı yay + yanına **`kapsam_yuzdesi`** döndürüp UI'da göster.

---

## M5 — BSC: dört perspektif var, neden-sonuç zinciri yok · YÜKSEK

`BscKpiPerspective` bir KPI'ya perspektif **etiketi** yapıştırmaktan ibaret (tek `String(30)`).
"strategy_map" adıyla dönen yapı Strateji→Alt Strateji→KPI **hiyerarşi ağacı** — perspektifler
arası hiçbir ok yok.

> Kaplan & Norton'da perspektifler bir liste değil **nedensellik zinciridir**:
> Öğrenme & Gelişim → İç Süreçler → Müşteri → Finansal. *Strategy Maps* (2004) tam olarak
> bu okların çizildiği araçtır. Oklar olmadan BSC, dört kovaya bölünmüş KPI listesine indirgenir
> — bu, BSC'ye yöneltilen **en yaygın uygulama eleştirisidir**.

**DB:** 840 satır — perspektifler **aktif kullanılıyor** (İç Süreç 404 · Finansal 204 ·
Müşteri 116 · Öğrenme 116). Kurumlar aracı benimsemiş; eksik olan **bağlantı katmanı**.

> Dağılım dengesiz: Öğrenme & Gelişim %14 — literatürde bu perspektifin ihmali klasik uyarı işareti.

---

## M6 — Lead / Lag gösterge ayrımı hiç yok · YÜKSEK

`ProcessKpi`'da yön, tür, hedef yöntemi var — ama göstergenin **öncü (lead)** mi
**artçı (lag)** mı olduğunu belirten alan yok.

> Kaplan & Norton'a göre yalnız artçılardan oluşan scorecard "nasıl başarılacağını" anlatmaz;
> yalnız öncülerden oluşan sonuca bağlanmaz. **Her hedefte en az bir öncü + bir artçı** bulunmalı
> — "balanced" sıfatının iki ekseninden biri budur.

Mevcut `gosterge_turu` bunu karşılamıyor: `İyileştirme (1426) / Azaltma (480) / Bilgi Amaçlı (183)`
— bunlar yön ve amaç ifade ediyor. Üstelik "Azaltma" `direction='Decreasing'` ile örtüşüyor
(**iki alan aynı bilgiyi tutuyor**).

---

## M7 — TOWS, SWOT'tan türetilmiyor · ORTA

`TowsAnalysis` dört serbest JSON metin alanı; kaydetme kodu payload'ı `json.dumps` ediyor —
**SWOT kaydına hiçbir referans yok**. Kullanıcı SWOT'u boş bırakıp TOWS yazabilir.

> TOWS (Weihrich, 1982) tanımı gereği bir **eşleştirme** egzersizidir: her SO stratejisi
> *belirli bir* güçlü yön ile *belirli bir* fırsatın kesişiminden doğar. İzlenebilirlik
> kaybolursa geriye "dört kutuya bölünmüş fikir listesi" kalır.

**DB:** 39 SWOT'a karşılık **18 TOWS** — yarısından azı geçmiş, araç kılavuzsuz bırakılınca terk edilmiş.

> *Terminoloji notu:* Kodda SWOT için köken atfı yapılmamış — bu iyi. UI'ya açıklama eklenirse:
> yaygın "Albert Humphrey" atfı çürütüldü (Puyt, Lie & Wilderom, 2023). Güvenli ifade:
> *"1960'larda SRI'da SOFT yöntemi olarak geliştirildi."*

---

## M8 — VRIO: model kusursuz, kullanım sıfır · ORTA

Metodolojik hata **yok** — `competitive_label` Barney'nin karar ağacını doğru sırada uyguluyor
(Değerli değil → Dezavantaj; nadir değil → Parite; taklit edilebilir → Geçici; örgütlenmemiş →
Kullanılmayan; hepsi → Sürdürülebilir Avantaj). Barney (1991, 1995) ile birebir.

**DB:** `vrio_resources` → **0 satır**. Tek kayıt yok.
Blue Ocean da neredeyse boş: 6 kanvas, 9 faktör, **3 ERRC öğesi**.

> ERRC dört eylemin **birlikte** düşünülmesini gerektirir — 3 öğe tek ızgarayı bile doldurmuyor.
> Maliyet düşürme ile değer artırma eşzamanlı olmadıkça "değer inovasyonu" oluşmaz.

**Öneri:** Ya onboarding'e katıp canlandır ya menüden kaldır — **boş modül ürüne güven kaybettirir**.

---

## M9 — OKR: yapı doğru, "esnek hedef" ve derecelendirme yok · ORTA

Objective/KR ayrımı doğru, `progress` 0-1'e doğru kırpıyor, PG'ye bağlanabiliyor. Eksikler:

1. **KR ölçülebilirliği zorunlu değil** — `target_value` nullable; boşsa KR sessizce ölçümsüz kalır.
   OKR'nin tek katı kuralı KR'lerin sayısal olmasıdır.
2. **Commit / stretch ayrımı yok** — Google uygulamasında ~0,7 "başarılı" sayılır. Bu ayrım
   olmadığı için %70 tamamlanan stretch KR "kısmi başarısızlık" gibi okunuyor.
3. **KR sayısı sınırsız** — yaygın kılavuz 3-5.

**DB:** 42 Objective / 126 KR → **3,0 KR/Objective**. Kullanıcılar disiplini kendiliğinden
koruyor; sistem yardım etmiyor ama zarar da vermiyor.

---

## M10 — `target_method` kayıtlı ama hesaba hiç girmiyor · ORTA

UI'da altı yöntem sunuluyor (RG/HKY/HK/SH/DH/SGH), değer kaydediliyor, plan yılları arasında
kopyalanıyor — ama **hiçbir hesaplamada okunmuyor**. Tüm kullanımlar taşıma/serileştirme.

İki somut sorun:

- **`HK` (Hedef Konulamaz)** — tanımı gereği hedefsiz gösterge. Ama motor `None` görünce
  M4'teki `sc = 0.0` ile **sıfır başarı** sayıyor. "Hedef konulamaz" dediğiniz gösterge
  kurumu **cezalandırıyor**. *(DB'de HK seçili kayıt yok ama seçenek açık — tuzak duruyor.)*
- **`DH` (Dalgalı Hedef)** — 193 PG ile en yaygın ikinci yöntem. "Dalgalı" hedef dönemsel
  değişen hedef demek; ama `target_value` tek alan ve B14'teki "en kolay uç" seçimi devreye giriyor.

**DB:** `DH 193 · HKY 179 · SH 69 · RG 1 · NULL 1955`

---

## M11 — EFQM: ağırlıklar doğru, seviye eşikleri uydurma · ORTA

`app/services/efqm_assessment.py:14-80`

Kriter ağırlıkları **doğru** — EFQM 2025'in 1000 puanlık dağılımıyla örtüşüyor.
Dosya başlığı modülün "türev" olduğunu dürüstçe belirtiyor — bu iyi.

Sorun `_level_for()`'da: docstring **dört** seviye tanımlıyor, fonksiyon **yedi** seviye
döndürüyor + "Rol Model Performansı" gibi etiketler ve 1-7 yıldız veriyor.

```
Docstring:  0-299 Başlangıç | 300-499 İyi | 500-699 Mükemmel | 700+ Dünya Lideri
Kod:        <200, 200+, 300+, 400+, 500+, 600+, 700+  →  7 seviye, "stars": 1..7
```

> EFQM skorları RADAR mantığıyla üretilir ve **tanınma seviyeleri kurumun kendi hesabı değildir**
> — bağımsız değerlendiriciler tarafından verilir. Türetilmiş gösterge "EFQM benzeri olgunluk
> göstergesi" olarak sunulabilir; "resmî EFQM seviyesi" olarak sunulamaz.

---

## M12 — "CMMI olgunluk" deniyor ama CMMI değil · ORTA

`raporlar/routes_faz2.py:200-203` · `routes_faz3.py:481` · `koe_service.py:155-170`

Rapor metinleri *"Süreçler CMMI olgunluk seviyesinde izlenmektedir"* diyor, değişken adı
`avg_cmmi`. Ama arkadaki `process_maturity` 1-5 arası serbest **öz-değerlendirme** integer'ı;
hiçbir CMMI süreç alanı, jenerik/spesifik hedef ya da değerlendirme yordamı yok.

> `koe_service.py`'nin kendi yorumu daha dürüst: *"öz-değerlendirme ortalaması (hafif öznel)"*

Ayrıca **seviye ortalaması alınıyor** (`func.avg`) → "3,4" gibi sayı üretiliyor.

> İki ayrı sorun: (1) CMMI staged temsilinde seviyeler **ordinal** ve *eşiklidir* — alt seviyenin
> tüm gereklerini karşılamadan üste geçilemez. Ordinal seviyelerin **aritmetik ortalaması ölçek
> teorisi açısından geçersizdir**. (2) CMMI değerlendirmesi (SCAMPI) yetkili lead appraiser
> gerektirir; öz-değerlendirmeye CMMI adı verilemez.

**DB:** `1:40 · 2:105 · 3:85 · 4:90 · 5:20` (340 değerlendirme). Kavram canlı, sadece yanlış adlandırılmış.
Dağılım 4'te ikinci tepe yapıyor → öz-değerlendirmelerde beklenen **iyimserlik yanlılığı**.

**Öneri:** "CMMI" ibaresini kaldır → *"Süreç Olgunluk Öz-Değerlendirmesi (1-5)"*.
Ortalama yerine **dağılım + medyan** göster; ya da "seviye 3 ve üzeri süreç oranı" gibi eşikli gösterge.

---

# STRATEJİK İYİLEŞTİRME ÖNERİLERİ

**1. Nedensellik katmanı — ürünün en büyük farklılaşma fırsatı**
366.604 satır `kpi_data` var. `bsc_causal_links` tablosu kurulduğunda kullanıcının çizdiği
"Öğrenme → İç Süreç → Müşteri → Finansal" oklarını **gerçek veriyle sınayabilirsiniz**:
gecikmeli korelasyonla *"eğitim saati ile müşteri memnuniyeti arasında varsaydığınız 3 aylık
ilişki veride görünmüyor"* diyebilen bir modül piyasadaki BSC araçlarının neredeyse hiçbirinde yok.
Kaplan-Norton'un kendi ifadesiyle strateji haritası bir **hipotezler kümesidir** — hipotezi test
edebilen ilk araç olmak güçlü bir konum. *(Nedensellik değil korelasyon olduğunu UI'da dürüstçe belirtmek şartıyla.)*

**2. "Skor sağlığı" paneli — sessiz hataları yüzeye çıkarın**
M1, M2, M4 ortak kök nedeni paylaşıyor: hesaplama sessizce başarısız oluyor, kimse görmüyor.
Vizyon skorunun yanında sürekli görünen kapsam göstergesi:
> *"Vizyon 68,4 — 294 stratejinin 210'unda süreç bağı yok, 1.240 PG'de başarı aralığı okunamıyor. Kapsam: %41."*

Bu tek ekran hem kullanıcıyı veri kalitesine yönlendirir hem bu tür hataların iki yıl gizli
kalmasını imkânsız kılar. **Skorun kendisinden daha değerli olabilir.**

**3. Çerçeveleri birbirine bağlayın — şu an dokuz ada var**
Doğal zincir literatürde belli: **PESTEL + Porter (dış) + VRIO (iç) → SWOT → TOWS → Strateji →
Alt Strateji → PG → Girişim/Proje (EVM)**. Her adımda bir öncekine referans alanı olsun.
En somut kazanç: bir stratejiye tıklayınca *"bu strateji hangi TOWS eşleşmesinden doğdu, hangi
VRIO kaynağına dayanıyor?"* sorusunun yanıtlanabilmesi. M8'deki boş VRIO tablosu, aracın hiçbir
şeye bağlanmamasının sonucu.

**4. Öncü/artçı dengesi teşhisi**
`kpi_nature` eklendiğinde alt strateji başına otomatik kontrol: *"Bu alt stratejinin 6
göstergesinin tamamı artçı — sonucu ölçüyorsunuz ama sürücüsünü değil."* Danışmanların manuel
yaptığı teşhisin otomatikleşmiş hali; kurumsal müşteriye anlatması kolay somut değer.

**5. Metodolojik dürüstlük etiketleri — güven ürünün parçasıdır**
M11 ve M12 aynı riski taşıyor: sistem olmadığı bir şey olduğunu ima ediyor ("resmî EFQM
seviyesi", "CMMI"). Kurumsal müşteride bunu bilen bir kalite yöneticisi çıktığında güven kaybı
kazanılan pazarlama etkisinden büyük olur. Her türetilmiş göstergenin yanına (i) ile "nasıl
hesaplandı + neye dayanıyor + **neye dayanmıyor**" koyun. `system_cards.description` altyapısı hazır.
**"Türetilmiş, resmî değil" demek aracı zayıflatmaz — metodolojik olgunluk sinyali verir.**
