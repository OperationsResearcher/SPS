# KOKPİTİM — KONUMLANDIRMA VE DEĞER HARİTASI
> Tarih: 2026-07-15 · Kaynak: [`OZELLIK-ONERILERI-2026-07.md`](OZELLIK-ONERILERI-2026-07.md) §4 · [`IS-PLANI-2026-H2.md`](IS-PLANI-2026-H2.md) Faz 4
> **Kod işi değil** — var olanı anlatma işi. Yayın'da henüz müşteri yok (pilot).

---

## 0. NEDEN BU BELGE

Denetimde en çarpıcı bulgu: **"kimsede yok" listesinin yarısı bizde zaten çalışıyor ama anlatılmıyor.**

Bu bir geliştirme boşluğu değil, **konumlandırma boşluğu** — ve müşteri yokken en ucuz kazanç.

Aşağıdaki her iddia **canlı veriyle doğrulandı** (2026-07-15, yerel DB). Doğrulanmayanlar açıkça işaretli.

---

## 1. AÇILIŞ — hangi problemi çözüyoruz

### Kategorinin gerçek sorunu: strateji yazılımı raf malı oluyor

**En güçlü kanıt satıcının kendisinden geliyor.** Microsoft, Viva Goals'u 31.12.2025'te kapattı ve resmi dokümanında yazdı:

> *"While some customers have recognized value, **overall adoption and usage of Viva Goals across the Viva Suite customer base hasn't grown. Microsoft has been unable to reach the scale and impact needed to continue further investment**..."*
> — [learn.microsoft.com/viva/goals/goals-retirement-faq](https://learn.microsoft.com/en-us/viva/goals/goals-retirement-faq)

Aynı FAQ'da Viva'nın **geri kalanı** için: *"With more than **66 million active users**, we see strong adoption and have increased investment."*

**Anlamı:** Aynı satıcı, aynı müşteri tabanı, aynı paket, aynı satış ekibi — **özellikle OKR ürünü tutmadı.** 66 milyon kullanıcılı bir paketin içinde. Bir rakip bunu çürütemez.

### İkinci sağlam iddia: yanlış eksende hizalama satılıyor

**Sull (MIT Sloan):** Yöneticilerin yalnızca **%28'i** kurumunun üç stratejik önceliğini sayabiliyor. Daha önemlisi: asıl kırık olan **dikey kaskad değil, yatay/birimler-arası koordinasyon**.

Kategori neredeyse tamamen **dikey kaskad** satıyor (org şemasından aşağı akan hedefler). Sull'un verisi dikeyin **zaten çalışan kısım** olduğunu söylüyor.

### ⛔ KULLANMAYIN — çürütülmüş istatistikler

Bilgili bir alıcı veya rakip bunları anında yıkar:

| İstatistik | Neden kullanılmaz |
|---|---|
| "Stratejilerin **%90'ı** başarısız" | Çarpıtılmış. Kaplan & Norton *"hedeflerinin **tamamını** teslim etmekte"* demişti; popüler versiyon "tamamını"yı düşürüp anlamı tersine çeviriyor |
| "%82 hizalı sanıyordu, %23'ü hizalıydı" | Primary araştırmayla uyuşmuyor |
| "Çalışanların %95'i stratejiyi bilmiyor" | Gerçek ama zayıf — örneklem/metodoloji açıklanmamış, üstelik **BSC'nin yazarlarının** teşhisi (ilacı satanlar) |
| Genel başarısızlık oranı (%50-90) | **Cândido & Santos (2015)** çürüttü: tahminler *"outdated, fragmentary, fragile or just absent"*, gerçek oran **belirlenmemiş** |

**Tersine kullanım:** Cândido & Santos'u alıntılayıp *"bu yüzden %90 istatistiğini kullanmıyoruz"* demek başlı başına güvenilirlik hamlesidir.

---

## 2. FARKLILAŞTIRICILAR — bizde çalışan, rakiplerde bulunmayan

### 🏆 2.1 Hedef Manipülasyonu Radarı (TASK-262, 2026-07-15)

**Ne yapar:** *"Bu KPI'ın hedefi 3 kez aşağı çekildi — sonuncusu dönem kapanışına 4 gün kala."*

**Neden benzersiz:** Rakipler *"hedefe ulaştın mı?"* sorar. Bu radar *"hedefin kendisi dürüst mü?"* sorar.

**Rakip kanıtı:** **AI OKR kalite skorlama 16 üründe de yok** — ClearPoint dokümanı yapmadığını açıkça yazıyor. Herkes hedef *yazdırıyor*, kimse *not vermiyor*. Bizimki bir adım öteye gidiyor: hedefin **dürüstlüğünü** denetlemek.

**Neden kimse yapmaz:** Ürünün kendi müşterisini denetlemesi ticari cesaret ister.

**Dürüst sınır:** Radar niyet okumaz — hedef düşürmenin meşru sebepleri olabilir (pazar, kapsam). Çıktı suçlama değil **soru** üretir; bu ekrana da yazılı. İz 2026-07-15'te açıldı, geçmiş revizyonlar kayıtlı değil → **bugün boş görünür**, 1 dönem sonra anlam kazanır.

**Durum:** ✅ Çalışıyor · uçtan uca doğrulandı (hedef 280→210 → radar "aşağı -25.0%")

### 🏆 2.2 KVKK-güvenli AI — "veriniz yurt dışına çıkmıyor" (TASK-265)

**Ne yapar:** `provider=openai` + `base_url=<kurumun kendi sunucusu>` → AI analizi kurumun ağından **hiç çıkmaz** (Ollama/vLLM).

**Neden benzersiz:** KVKK'nın **hiçbir ülkeye yeterlilik kararı yok** ([kvkk.gov.tr](https://www.kvkk.gov.tr/Icerik/2053/Yurtdisina-Aktarim): *"Bu konuda Kurul tarafından henüz bir belirleme yapılmamıştır"*). Bu, her yurt dışı LLM çağrısını "uygun güvence + **5 iş günü içinde Kurum'a bildirim**" yüküne sokar.

**Global rakipler bunu yapısal olarak veremez** — iş modelleri merkezi buluta bağlı. En yakın örnek **Spider Impact 5.8** "metadata-only" mimarisi (ham veri müşteri ortamından çıkmıyor, FedRAMP/GovCloud) — ama **Türkiye'de barındırma yok**.

**Durum:** ✅ Çalışıyor (%100 hazır, 6 test) · BYOK + PII maskeleme + şifreli key + kota

### 2.3 K-Vektör — vizyon 1000 ölçeği

**Ne yapar:** PG → Süreç → Alt Strateji → Ana Strateji → **Vizyon**'u tek sayıya indirger.

**Neden farklı:** Rakipler BSC/OKR skoru verir; *"vizyonunuz kaç puan"* demez.

**Durum:** ✅ Çalışıyor — 108 ağırlık kaydı, 6 config snapshot (canlı veri)

### 2.4 KOE — Kurumsal Olgunluk Endeksi (veri girmeden)

**Ne yapar:** *"PGV (performans verisi) YOKKEN, mevcut yapısal veriden kurumun olgunluğunu hesaplar"* — 4 boyut, saf okuma + AI yapı-danışmanı.

**Neden önemli (satış açısından):** Yeni müşteri **veri girmeden** ilk günden değer görür. Klasik "önce 6 ay veri gir, sonra konuşuruz" engelini aşar.

**Rakip kanıtı:** **EFQM şablonu global vendor'larda bulunamadı** (Corporater BSC ve OKR'yi açıkça sayıyor, EFQM'i saymıyor). EFQM'in kendi aracı **AssessBase** var ama o bir *denetim* aracı — günlük KPI yönetimine bağlı değil. **Köprü boşluğu gerçek.**

**Durum:** ✅ Çalışıyor — 340 olgunluk kaydı

### 2.5 Otonom kılavuz/video üreteci

**Ne yapar:** Ürün kendi kullanım videosunu üretiyor — ekran görüntüsü alıp anlatarak.

**Durum:** ✅ Çalışıyor (`kilavuz_olusturucu_executor`) · Hiçbir SPM ürününde bulunamadı

### 2.6 Otonom hata kontrol senaryoları

**Ne yapar:** Ürün kendi kendini gezip hata arıyor.

**Durum:** ✅ Çalışıyor (`hata_kontrol_executor`) · Hiçbir SPM ürününde bulunamadı

---

## 3. TÜRKİYE HENDEĞİ

### ❌ Türkçe UI hendek DEĞİL — bu varsayım çürüdü

**Spider Impact resmen Türkçe destekliyor.** FAQ'sinden birebir doğrulandı (2026-07-15):

> *"We maintain translations of Spider Impact for the following languages: English, Arabic, Spanish, Portuguese, French, **Turkish**"*
> — [spiderstrategies.com/faq](https://www.spiderstrategies.com/faq/)

**Dil üzerinden konumlanmayın.**

### ✅ Gerçek hendek: mevzuat formatı + veri yerleşikliği

**Kamu uyum pazarı — yasayla garantili:**
- **5018** + Stratejik Planlama Yönetmeliği: planlar **idarenin kendi çalışanlarınca** hazırlanmak zorunda → danışmanlık değil, **araç** satılacak alan
- **5393 md.41:** Başkan seçimden itibaren **6 ay içinde** stratejik plan sunmalı (nüfus 50.000+ zorunlu)
- ~1.389 belediye · **5 yıllık seçim döngüsü = yenilenen pazar**
- **Global oyuncuların hiçbiri bu formatı bilmiyor**

**Veri yerleşikliği:** §2.2 (KVKK + yerel LLM)

### ⚠️ Yerli rakibi hafife almayın
**Vadi — DIGIKENT Stratejik Planlama** kamu/belediye segmentinde doğrudan rakip; 5018/5393/5216/5302'ye açıkça atıf yapıyor. Özel sektör OKR'de Twiser, Devokr, Perfx kalabalık.
**Boş görünen alan:** e-Belediye/KAYSİS entegre strateji yazılımı (araştırılmadı).

---

## 4. FİYAT MODELİ — kritik uyarı

**Bulgu:** Per-seat fiyatlama, ürünün iddia ettiği şeyin **tam tersini** teşvik ediyor.

Strateji org genelinde anlaşılmalı — ama her ek okuyucu $8-16/ay tutuyorsa, alıcı rasyonel olarak koltukları **rapor verenlerle** sınırlar, **işi yapanlarla** değil. Araç böylece küçük bir yönetici çevresinin raporlama katmanına dönüşür = **shelf-ware deseninin kendisi.**

**Kendi verimiz bunu doğruluyor** (TASK-263, 90 gün): **27 kullanıcı giriş yapıyor ama yalnız 7'si veri giriyor.** Yani %74 sadece bakıyor. Per-seat fiyatlasak bu 27 kişinin çoğu lisanslanmazdı.

**Bunu kabul eden iki ürün:** **ESM** ($1.000/ay sınırsız kullanıcı) · **Perdoo** (€1,50 izleyici koltuğu).

→ Paketleme belgesindeki fiyat kararı bu bulguyu dikkate almalı.

---

## 5. DEMO AKIŞI (Faz 4.3)

**Sorun:** Full-set demo overwhelm ediyor (paketleme belgesi §7-8).

**Kendi verimizle önerilen persona sırası** (TASK-263 kullanım verisi):

| Persona | Göster | Neden |
|---|---|---|
| **Üst yönetim** | Yönetim Özeti → **Hedef Radarı** → K-Vektör | "5 saniyede durum" + kimsede olmayan soru |
| **Kalite/Strateji** | KOE (veri girmeden olgunluk) → strateji ağacı | İlk günden değer, veri engeli yok |
| **Süreç sahibi** | PG Veri Girişi → karne | **270 işlem/90 gün** — ürünün gerçek kalbi |
| **Kamu/belediye** | 5018/5393 formatı → KVKK yerel LLM | Global rakiplerin veremediği |

**Göstermeyin:** `mock_*` lab ekranları (metaverse, DAO, oyun teorisi) — 29 tablo, hepsi boş, route'ları kırık (TASK-258 kararı bekliyor).

---

## 6. DOĞRULAMA NOTU

- **İç veriler:** 2026-07-15 yerel PostgreSQL ölçümü. K-Vektör 108/6, KOE 340, LLM 279 çağrı, audit 27/7 kullanıcı.
- **Rakip/pazar:** web araştırması. İki kritik iddia **birincil kaynaktan bizzat doğrulandı** (Microsoft FAQ, Spider Impact FAQ).
- **Doğrulanmayan:** G2/Capterra/TrustRadius/Gartner/Reddit hepsi 403 → orta-segment rakipler (Cascade, ClearPoint, Perdoo, Betterworks) için **gerçek kullanıcı yorumu kanıtı yok**.
- **Çürüyen kendi varsayımımız:** "Türkçe UI hendektir" → Spider Impact zaten destekliyor.
