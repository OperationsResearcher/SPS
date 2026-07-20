# BÜYÜK KEŞİF — YÖNETİCİ ÖZETİ

> **Tarih:** 2026-07-21 · **Kapsam:** 132.000 satır (328 Python + 88 JS + 167 şablon + 858 route + 170 tablo)
> **Yöntem:** 6 paralel uzman denetimi (backend/hesap · frontend · güvenlik · SP metodolojisi · i18n/veri · uçtan uca kullanıcı testi) + ana oturumda bağımsız doğrulama
> **Kural:** Hiçbir kod değiştirilmedi. Her bulgu DB'den veya kodu çalıştırarak teyit edildi.

---

## Tek cümlede

Sistem **çökmüyor, veri kaybetmiyor ve güvenlik mimarisi sanılandan sağlam** — ama
**sessizce yanlış sayı gösteriyor**, ve bunun tek bir kök nedeni var: *hesaplama başarısız
olduğunda hiçbir yerde iz bırakmıyor.*

---

## En kritik 8 bulgu

| # | Bulgu | Etki | Kanıt |
|---|---|---|---|
| **1** | **Gerçek müşteri verisinin %100'ü skorsuz** | KMF 334/334, Eskişehir 289/289 satır `status_percentage = NULL`. Tomofil (seed) 0/91.408 — **demo verisi hatayı maskeliyor** | K1 · DB + kod |
| **2** | **Yayın DB parolası public GitHub'da, 3,5 aydır** | `private: false` doğrulandı. 5432 dışarı kapalı olduğu için henüz sömürülmemiş — *gecikmeli bomba* | S1 |
| **3** | **Üretim yanlış hesap kopyasını çalıştırıyor** | `"4,5-9,5"` → `(45.0, 95.0)` olmalıyken `(4.5, 9.5)`. **9 üretim dosyası hatalı kopyada, 6 testin tamamı doğru kopyada** → testler yeşil, üretim yanlış | B2 · çalıştırıldı |
| **4** | **Başarı puanı bantlarının %64,6'sı okunamıyor** | 1240 PG'nin JSON'u parser'a uymuyor → `{}` → puan `None`. Format **yalnız JS'te üretiliyor**, backend haberdar değil | M1 · gerçek kayıtla test |
| **5** | **Vizyon skoru 24 puan yanlış** | Bağlantısız alt strateji "0 puan" sayılıyor. Tomofil: **55.78 görünüyor, gerçek 80.02**. KMF: 6.48 görünüyor, ölçülenlerin ortalaması 27.73 | B1/M4 |
| **6** | **94 uç yıl seçicisini yok sayıyor** | 193 uçtan 94'ü 2024↔2026'da **byte-byte aynı**. Tüm K-Radar teşhis radarları, BI dışa aktarımı, zaman serisi raporları dahil | K2/K3/F4/B4 |
| **7** | **604 gösterge hâlâ ters hesaplanıyor** | `k_radar_service.py:1224` ve `analytics_service.py:178` — bu oturumda `k_rapor`'da düzeltilen hatanın **aynısı iki dosyada daha** | B3/B7 |
| **8** | **Yeni müşterinin ilk sayfası 500 veriyor** | `/k-plan/strategy` boş kurumda `UndefinedError: current_app`. Strateji girilir girilmez kayboluyor → mevcut müşterilerde görünmüyor | K4 |

---

## Ortak kök neden: sessiz başarısızlık

Bulguların çoğu tek bir desende buluşuyor. **Bugün kullanıcıya hiçbir uyarı vermeden yanlış
sonuç üreten veri hacmi:**

| Durum | Kayıt |
|---|---|
| Skorsuz `kpi_data` (gerçek müşteriler) | **972** |
| Başarı aralığı okunamayan PG | **1.235** |
| Süreci olmayan alt strateji (0 puan sayılıyor) | **210** |
| Hedefi sayıya çevrilemeyen PG | **427** |
| Ağırlığı 0 olan aktif PG | **469** |
| Ters hesaplanan `Decreasing` PG | **604** |

> **Hiçbiri kullanıcıya hata olarak görünmüyor.** Ekranlar hatasız çalışıyor, sadece sayılar yanlış.

Aynı desen bu oturumda iki kez daha karşımıza çıktı: `lower_is_better` ölü koşulu (604 gösterge)
ve bozuk Türkçe çeviri dosyası (1004 yanlış eşleşme). İkisi de aylarca fark edilmedi çünkü
**hata log'a düşmüyordu.**

---

## Neden şimdiye kadar fark edilmedi

Üç mekanizma birlikte çalışıyor:

**1. Demo verisi gerçeği maskeliyor.** Tomofil'in 91.408 satırı seed script'iyle skor **dolu**
geldiği için ekranlar sağlıklı görünüyor. Elle veri giren gerçek müşteride sistem skorsuz.
K1, K4 ve K5'in üçü de bu yüzden gözden kaçmış.

**2. Testler yanlış kopyayı test ediyor.** 6 test dosyasının tamamı `app/utils/`'i test ediyor,
9 üretim dosyası `utils/`'i çalıştırıyor. **755 test yeşil ama üretim yanlış hesaplıyor.**

**3. Sessiz `except` blokları.** 124 noktada hata yutuluyor; 3'ü doğrudan güvenlik kararı veriyor
(`tenant_scope.py:250` — rol çözümlemesi patlarsa **sessizce düşük yetkiye düşüyor**).

---

## Sağlam olanlar (doğrulandı)

Bunları da ölçtük — aksi varsayılabilirdi:

| Konu | Sonuç |
|---|---|
| **SQL injection** | ❌ **Yok.** ~1318 ham SQL noktası tarandı, hepsi parametre bağlı. Dinamik `ORDER BY` enterpolasyonu sıfır |
| **Yetim kayıt** | ❌ **Yok.** 259 FK kısıtı sorgulandı, ebeveynsiz satır yok |
| **Mühür (K8)** | ✅ **Doğru çalışıyor.** Mühürlü yıla veri → 423 + açıklayıcı mesaj |
| **Yıl-varlık bütünlüğü** | ✅ 2020 PG'sine 2026 verisi → 409 + net mesaj |
| **EVM formülleri** | ✅ `CPI=EV/AC`, `SPI=EV/PV`, `EAC=BAC/CPI` — literatüre uygun, sıfıra bölme korumalı |
| **VRIO karar ağacı** | ✅ Barney (1991) ile birebir |
| **EFQM ağırlıkları** | ✅ EFQM 2025 dağılımıyla örtüşüyor |
| **Migration zinciri** | ✅ 16 dosya, tek head, kopuk yok |
| **Model ↔ DB uyumu** | ✅ Modelde olup DB'de olmayan: 0 |
| **`.env` git'te mi** | ❌ Hayır. SSH anahtarı da repoda değil |
| **JS hata yönetimi** | ✅ 88 dosyanın 86'sında var |

---

## Önerilen sıra

### Bu hafta — güvenlik ve veri doğruluğu

| # | İş | Neden önce |
|---|---|---|
| 1 | **Yayın DB parolasını döndür** (S1) | 3,5 aydır public; firewall tek savunma |
| 2 | **`status_percentage` hesaplanıp yazılsın** (K1) | Gerçek müşterilerde skor hiç üretilmiyor |
| 3 | **9 üretim dosyasını doğru kopyaya çevir** (B2) | 10-100 kat hesap hatası, testler yakalayamıyor |
| 4 | **EVM sahiplik kontrolü** (S3) | Kurumlar arası bütçe sızıntısı — tek satır |
| 5 | **XSS: `_esc()` 4 alana** (F2) | Yetki yükseltme; sömürü zinciri uçtan uca doğrulandı |
| 6 | **`NameError: today`** (K5) | Tek satır; projesi olan her kurumda 4 uç çöküyor |
| 7 | **Sequence `setval`** (S5) | Sonraki rol/bileşen eklemede kesin çakışma |

### Bu ay — hesap doğruluğu

| # | İş |
|---|---|
| 8 | Başarı puanı parser'ına yeni format (M1) + **parse boş dönerse log** |
| 9 | Bağlantısız alt strateji `None` olsun (B1/M4) + **kapsam yüzdesi göster** |
| 10 | `lower_is_better` kalıntısı 2 dosyada daha (B7) + `analytics_service` `direction` (B3) |
| 11 | `analytics_service`'e `year` filtresi (B4) — 118 KPI hâlâ 2020 verisiyle puanlanıyor |
| 12 | 94 tepkisiz uca `resolve_request_year()` (K2/K3/F4) |
| 13 | `kpi_year_configs` içindeki 35 `AVG` satırı normalize (D2) |

### Bu çeyrek — yapısal

| # | İş |
|---|---|
| 14 | `TENANT_GUARD_MODE=enforce` kademeli açılsın (S2) |
| 15 | EN `.po`'daki 45 kaymış fuzzy kayıt (I2) — `--use-fuzzy` bir gün çalışırsa yayına çıkar |
| 16 | JS i18n benimsenmesi 36/88 → tamamı (I6) |
| 17 | 121 noktada `str(e)` istemciye dönüyor (S6) — merkezî handler zaten doğru yazılmış, atlanıyor |
| 18 | "CMMI" ve "EFQM seviyesi" ibareleri düzeltilsin (M11/M12) |

---

## En değerli üç öneri (yeni yetenek)

**1. Skor sağlığı paneli** — Vizyon skorunun yanında sürekli görünen kapsam göstergesi:

> *"Vizyon 68,4 — 294 stratejinin 210'unda süreç bağı yok, 1.235 PG'de başarı aralığı
> okunamıyor. **Kapsam: %41**"*

Bu tek ekran hem kullanıcıyı veri kalitesine yönlendirir hem **bu tür hataların bir daha
aylarca gizli kalmasını imkânsız kılar.** Skorun kendisinden değerli olabilir.

**2. Nedensellik katmanı** — 366.604 satır `kpi_data` elinizde. Kullanıcının çizdiği
"Öğrenme → İç Süreç → Müşteri → Finansal" oklarını **gerçek veriyle sınayan** bir modül,
piyasadaki BSC araçlarının neredeyse hiçbirinde yok. Kaplan-Norton'un kendi ifadesiyle strateji
haritası bir *hipotezler kümesidir* — hipotezi test edebilen ilk araç olmak güçlü bir konum.

**3. Metodolojik dürüstlük etiketleri** — Sistem şu an olmadığı bir şey olduğunu ima ediyor
("resmî EFQM seviyesi", "CMMI"). Kurumsal müşteride bunu bilen bir kalite yöneticisi çıktığında
güven kaybı, kazanılan pazarlama etkisinden büyük olur. `system_cards.description` altyapısı hazır.
**"Türetilmiş, resmî değil" demek aracı zayıflatmaz — metodolojik olgunluk sinyali verir.**

---

## Ham raporlar

| Dosya | İçerik |
|---|---|
| [`ham/01-frontend.md`](ham/01-frontend.md) | 15 bulgu + 5 UX önerisi · JS/şablon |
| [`ham/02-guvenlik.md`](ham/02-guvenlik.md) | 10 bulgu + doğrulanan olumlular · güvenlik/veri |
| [`ham/03-backend-hesap.md`](ham/03-backend-hesap.md) | 14 bulgu + 4 şüpheli · hesaplama motorları |
| [`ham/04-metodoloji.md`](ham/04-metodoloji.md) | 12 bulgu + 5 stratejik öneri · SP literatürü |
| [`ham/05-i18n-veri.md`](ham/05-i18n-veri.md) | 14 bulgu · çeviri + model tutarlılığı |
| [`ham/06-kullanici-yolculugu.md`](ham/06-kullanici-yolculugu.md) | 15 bulgu + 2 özet tablo · uçtan uca test |

---

## Yöntem notu — uzman raporlarında düzeltilenler

Ham raporlar ana oturumda çapraz doğrulandı; **üç yanlış bulgu düzeltildi**:

| İddia | Gerçek |
|---|---|
| *"11 `alert()` kural ihlali"* | 9'u SweetAlert2 yedeği — **iyi mühendislik**. Gerçek ihlal: 2 |
| *"19 Jinja-in-JS ihlali"* | 18'i kuralı alıntılayan **yorum satırı**. Gerçek ihlal: **0** |
| *"JS'de i18n mekanizması hiç yok"* | `window.t()` **var** ve 36/88 dosyada kullanılıyor. Sorun: benimsenme yarım |

> Bu düzeltmeler önemli: yanlış alarm veren bir denetim, denetim yapmamak kadar zararlıdır.
