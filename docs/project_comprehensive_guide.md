# Kokpitim Kurumsal Performans ve Strateji Yönetim Platformu
## Kapsamlı Tanıtım ve Yetenekler Kılavuzu

---

## 1. VİZYON VE PROJE TANIMI

**Kokpitim**, modern kurumların **Stratejik Planlama**, **Süreç Yönetimi**, **Proje Portföyü** ve **Bireysel Performans** yönetim süreçlerini tek bir çatı altında birleştiren, Türkiye pazarına özel olarak geliştirilmiş bulut tabanlı (multi-tenant SaaS) bir kurumsal performans yönetim platformudur.

Piyasadaki diğer kurumsal yazılımlar strateji, süreç ve performans yönetimini birbirinden kopuk, bağımsız modüller halinde sunarken; **Kokpitim’in benzersiz değeri (Unique Value Proposition), "Strateji ➔ Süreç ➔ Performans Göstergesi (KPI) ➔ Bireysel Karne ➔ Proje/Faaliyet" zincirini uçtan uca birbirine entegre ve dinamik olarak izleyebilmesidir.**

### Sistem Kullanıcı Rolleri:
Sistemde yetkilendirme ve veri izolasyonu, rol tabanlı erişim kontrolü (RBAC) ile sağlanır:
- **Super Admin:** Platform geneli paket, tenant (kurum) ve genel sistem ayarlarını yönetir.
- **Tenant Admin (Kurum Yöneticisi):** İlgili kuruma ait kullanıcıları, rolleri, modül yetkilerini ve organizasyonel yapıyı yönetir.
- **Executive Manager (Yönetici):** Süreç sahipliği, departman performans takibi, onay zincirleri ve kurumsal raporlama yetkilerine sahiptir.
- **Standard User (Çalışan):** Kendisine atanan süreçleri, faaliyetleri, projeleri, görevleri ve bireysel performans karnesini takip eder.

---

## 2. SAAS MİMARİSİ VE PAKETLEME MODELİ

Platform, esnek ve ölçeklenebilir bir **Paket ➔ Modül ➔ Bileşen** hiyerarşisine dayanmaktadır. Kurumların (Tenant) satın aldıkları abonelik paketine göre erişebilecekleri modüller ve bu modüllerin altındaki bileşenler dinamik olarak sınırlandırılır.

### 2.1. Kart Bileşenleri (System Cards) ve Dinamik Arayüz Yönetimi
Kurumsal yapıda en küçük görsel ve işlevsel birimleri temsil eden **Sistem Kartları (System Cards)**, SaaS hiyerarşisinin en alt işlevsel katmanıdır. 
* **Rolü ve Amacı:** Ekranlardaki grafikler, veri tabloları veya özet panoları gibi her bir görsel bileşen birer "System Card" olarak tanımlanır. Bu yapı, arayüzün modüler, esnek ve kişiselleştirilebilir olmasını sağlar.
* **Bilgi (i) Butonu ve Dinamik Açıklamalar:** Her kartın üzerinde kullanıcı dostu bir **"i" (bilgi/info) butonu** bulunur. Bu buton, veritabanındaki `SystemCard.description` (kart açıklaması) alanını dinamik olarak okuyarak kullanıcıya o kartın ne işe yaradığı, hangi amaca hizmet ettiği ve nasıl okunması gerektiği hakkında anlık bilgi/tooltip sunar. Böylece kullanıcılar ekrandan ayrılmadan entegre yardım alabilirler.
* **Paket ve Yetki Entegrasyonu:** Her kartın altında tanımlı veri kaynakları (`CardDataSource`), lisans yetkilerine duyarlıdır. Eğer kullanıcının paketinde ilgili kartın gerektirdiği yetki (component slug) yoksa, veri veya kart arayüzden otomatik olarak gizlenir.
* **Teknik İzlenebilirlik:** Her kartın benzersiz bir uzun kodu (`code`) ve yöneticilerin kolayca referans verebileceği kısa bir kimliği (`short_id`, örn: MA13, SP09, PR07) bulunur. Bu sayede hata bildirimlerinde ve loglarda nokta atışı izleme yapılabilir.

### Abonelik Paketleri:
Sistemde aktif olarak tanımlanmış 4 ana abonelik paketi mevcuttur:

1. **Master Package (`master_package`):** Platformdaki tüm modülleri ve ileri düzey özellikleri sınırsız olarak barındıran en üst paket seviyesidir.
2. **Başlangıç Paketi (`baslangic` - L1):** Kurumların platforma ilk adımı atmasını sağlayan temel düzeydir. Kurumsal kimlik (Vizyon, Misyon vb.) ve temel Stratejik Planlama modüllerini içerir.
3. **Yönetim Paketi (`yonetim` - L2):** Süreç, Performans Göstergesi (KPI), bireysel performans takibi, temel proje yönetimi ve operasyonel raporlama yeteneklerini barındırır.
4. **Strateji Paketi (`strateji` - L3):** Yönetim paketindeki tüm özelliklere ek olarak, ileri düzey analiz modülleri, yapay zeka destekli karar destek mekanizmaları ve **K-Radar** ileri analitik modülünü içerir.

---

## 3. AKTİF SİSTEM MODÜLLERİ VE YETENEKLERİ

Platform, kullanıcılara modern bir arayüz sunan 11 ana modülden oluşmaktadır. Bu modüller ve içerdikleri anahtar yetenekler şunlardır:

### 3.1. Stratejik Planlama Modülü (`sp`)
Kurumun uzun vadeli stratejik hedeflerini, vizyon ve misyonunu belirleyip takip ettiği modüldür.
* **Dengeli Karne (Balanced Scorecard - BSC):** Stratejiyi; Finansal, Müşteri, İç Süreçler ve Öğrenme/Gelişme olmak üzere 4 temel perspektifte dengeler.
* **OKR Yönetimi (Objectives and Key Results):** Çevik hedef yönetimini sağlar. Hedefler ve anahtar sonuçlar arasındaki kademelendirmeyi ve hizalamayı izler.
* **Strateji Haritası:** Hedefler arasındaki neden-sonuç ilişkilerini görselleştirir.
* **Dönem Mühürleme ve Revizyon Yönetimi:** Belirli stratejik dönemleri mühürler veya kontrollü revizyon süreçleri başlatır.
* **Yapay Zeka Destekli Stratejik Asistan:** Stratejik planlama adımlarında yapay zekadan öneriler ve yönlendirmeler alır.

### 3.2. İleri Stratejik Planlama Modülü (`ileri_sp`)
Kurumların makro çevre ve iç durum analizlerini bilimsel metodolojilerle yapmasını sağlayan modüldür.
* **SWOT & TOWS Analizleri:** Kurum içi güçlü/zayıf yönler ile dış çevredeki fırsat/tehditlerin analizi ve bunlardan strateji üretilmesi.
* **PESTEL Analizi:** Politik, Ekonomik, Sosyal, Teknolojik, Çevresel ve Yasal faktörlerin analizi.
* **Porter'ın 5 Güç Analizi:** Sektörel rekabet yapısının analizi.
* **VRIO Analizi:** Kurumsal kaynakların Değer, Nadirlik, Taklit Edilemezlik ve Organizasyon boyutlarında değerlendirilmesi.
* **Diğer Matrisler:** BCG (Büyüme/Pazar Payı), Ansoff (Pazar Nüfuz/Ürün Geliştirme) ve Değer Zinciri Analizleri.

### 3.3. Süreç Yönetimi Modülü (`surec`)
Kurumun iş süreçlerini, performans göstergelerini (KPI) ve faaliyetlerini tanımlayıp yönettiği kalbidir.
* **Süreç Karneleri:** Süreç sahipleri, liderleri ve üyelerinin tanımlanması, süreçlerin performans skorlarının anlık takibi.
* **Performans Göstergesi (KPI) & Veri Girişi:** KPI'ların hedeflerinin tanımlanması, manuel veya API entegrasyonuyla periyodik veri girişleri yapılması.
* **Süreç Faaliyetleri:** Süreç iyileştirme faaliyetleri, sorumlular, termin tarihleri ve otomatik hatırlatma e-postaları.

### 3.4. İleri Süreç Yönetimi Modülü (`ileri_surec`)
* **Süreç Verimlilik ve Trend Analizleri:** Süreçlerin ve KPI'ların zaman içindeki gidişatını, darboğazlarını ve verimlilik kayıplarını izler.
* **OEE (Toplam Ekipman Etkinliği) & SLA Takibi:** Operasyonel mükemmellik göstergelerinin analizi.

### 3.5. Proje Yönetimi Modülü (`proje`)
Stratejik hedeflerle doğrudan ilişkili projelerin ve bu projelere bağlı görevlerin yönetilmesini sağlar.
* **Proje Kanban ve Gantt Şeması:** Projelerin görsel takibi, kritik yol analizi (CPM) ve zaman çizelgesi yönetimi.
* **RAID Yönetimi:** Projelerdeki Riskler (Risks), Varsayımlar (Assumptions), Sorunlar (Issues) ve Bağımlılıkların (Dependencies) takibi.
* **Strateji-Proje Hizalama Matrisi:** Projelerin stratejik hedeflere yaptığı katkı oranlarının skorlanması.

### 3.6. Performans Analitiği Modülü (`analiz`)
Verileri işleyerek ileri düzey analitik öngörüler üreten modüldür.
* **Sağlık Skoru ve Tahminleme (Forecasting):** KPI geçmiş verilerini analiz ederek gelecek dönem performansını tahmin eder.
* **Anomali Tespiti (ML Anomaly Detection):** Z-skoru, IQR ve hareketli ortalamalar kullanarak KPI verilerindeki beklenmedik dalgalanmaları (anomalileri) tespit eder.
* **ESG (Çevresel, Sosyal ve Yönetişim) Raporlama:** Karbon ayak izi ve sosyal sorumluluk metriklerini izler.
* **BI Entegrasyonu (BI Connector):** Verilerin Power BI veya Tableau gibi harici iş zekası araçlarına aktarımı için veri bağlayıcıları.

### 3.7. K-Radar Modülü (`k_radar`)
Üst yönetimin kararlarını desteklemek için tasarlanmış çapraz analitik ve radar ekranıdır.
* **Balanced Scorecard Radarı / EFQM Olgunluk Modeli:** Kurumsal mükemmellik seviyesinin ölçümü.
* **Strateji-Süreç Kapsama Analizi:** Hangi stratejik hedefin hangi süreçlerle desteklendiğini, açıkta kalan süreç veya strateji olup olmadığını gösterir.
* **Kazanılmış Değer Analizi (Earned Value Management - EVM):** Projelerin bütçe ve zaman performansının entegre analizi.

### 3.8. K-Rapor Modülü (`k_rapor`)
* **Executive Manager Özet Raporları (Executive Dashboards):** CFO, COO, CHRO ve Yatırımcılar için özelleştirilmiş performans göstergeleri ve raporlama panelleri.
* **AI Koç & AI Danışman Raporları:** Yapay zekanın tüm kurum verisini tarayarak hazırladığı yönetici özetleri ve aksiyon önerileri.

### 3.9. K-Vektör Metriği ve Matematiksel Vizyon Skoru
Kokpitim'in en özgün yeteneklerinden biri olan **K-Vektör**, stratejik planlama, süreçler ve performans göstergeleri (KPI) arasındaki bağımsız başarı skorlarını bütünleştirerek kurumun genel **Vizyon Skoru**nu hesaplayan gelişmiş bir matematiksel modeldir.
* **1000 Puan Hedefi:** K-Vektör aktif edildiğinde, en tepedeki kurumsal vizyon **1000 puanlık** bir hedef olarak tanımlanır. Kurumun tüm stratejilerinin başarısı bu 1000 puan içinden pay alır.
* **Hiyerarşik Ağırlık Dağılımı:**
  * **Ana Stratejiler:** Vizyonun 1000 puanlık bütçesinden kendi ham ağırlıklarına göre oransal olarak pay alır.
  * **Alt Stratejiler:** Bağlı oldukları ana stratejinin kotasını yine kendi ham ağırlıklarına göre oransal bölüşür.
  * **Süreçler:** Belirlenen katkı yüzdeleriyle (%) alt stratejileri besler.
  * **KPI'lar:** Süreç skorunu belirleyen en alt veri girdileridir.
* **Eksik ve Ağırlıksız Durum Yönetimi:** Ağırlık girilmeyen alanlarda eşit dağıtım ilkesi uygulanırken, veri girilmemiş veya eksik bırakılmış strateji kollarının katkısı **0** kabul edilerek vizyon skoru gerçeğe en yakın şekilde hesaplanır.
* **Geriye Dönük İzlenebilirlik:** Yapılan her ağırlık ve yüzde değişikliği veritabanında snapshot (`k_vektor_config_snapshots`) olarak saklanarak geçmişe dönük denetim izi oluşturulur.

---

## 4. VERİ MİMARİSİ VE İŞLEME SÜREÇLERİ

Kokpitim platformu, verileri toplama, işleme, sunma ve raporlama aşamalarında tam entegre bir veri boru hattına sahiptir:

### 4.1. Veri Nasıl Saklanıyor? (Veri Modeli)
* **Multi-Tenant İzolasyon:** Her kurumun verileri `tenant_id` veya `kurum_id` bazında mantıksal olarak izole edilmiştir.
* **Zaman Serisi ve Geçmiş İzleme:** KPI değerleri (`kpi_data`), faaliyet takipleri (`activity_tracks`) ve denetim izleri (`audit_logs`) zaman damgalarıyla saklanarak geçmişe dönük analizlerin yapılmasına olanak tanır.
* **Soft Delete:** Sistemde kritik veriler (`User`, `Process`, `Strategy` vb.) silindiğinde veritabanından kalıcı olarak temizlenmez (hard-delete yapılmaz). Bunun yerine `is_active=False` veya `is_deleted=True` yapılarak veri kaybı önlenir ve arşivlenir.

### 4.2. Veri Nasıl İşleniyor? (Servis Katmanı)
* **Merkezi Analitik Motoru (`AnalyticsService`):** Trend hesaplamaları, sağlık skorları ve karşılaştırmalar tek bir servis üzerinden yönetilir.
* **Zamanlanmış ve Asenkron İşlemler:** Celery ve Redis altyapısı sayesinde gece çalışan otomatik yedeklemeler, periyodik e-posta bildirim özetleri (digest) ve anomali taramaları sisteme yük bindirmeden asenkron olarak gerçekleştirilir.
* **Olay Tabanlı Tetikleyiciler:** Süreçlerde veya projelerde atanan yeni görevler, geciken faaliyetler veya girilen yeni KPI değerleri anında WebSocket üzerinden tarayıcı bildirimlerini ve e-posta servislerini tetikler.

### 4.3. Veri Nasıl Raporlanıyor? (Çıktı Motoru)
* **Dinamik Excel İhracı:** Pandas ve openpyxl kütüphaneleri kullanılarak süreç karneleri, KPI listeleri ve performans özetleri tek tuşla biçimlendirilmiş Excel tablolarına dönüştürülür.
* **Yapay Zeka Destekli Sunum Üretimi:** Kurum performans verilerinden yola çıkarak yöneticilere özel PowerPoint sunum taslakları veya PDF formatında yatırımcı sunumları üretilebilir.

---

## 5. TEKNOLOJİK ALTYAPI VE STACK

Platform, performans, güvenlik ve kararlılık odaklı modern bir teknoloji stack'ine sahiptir:

* **Backend:** Python 3.11 tabanlı Flask mikro-çerçevesi. Nesne-ilişkisel eşleme (ORM) için **Flask-SQLAlchemy** kullanılmaktadır. Mimari olarak genişleyebilirliği sağlayan **Application Factory** deseni uygulanmıştır.
* **Veritabanı:** Üretim ortamında yüksek performanslı ve ilişkisel **PostgreSQL** kullanılırken; yerel geliştirme ve hafif test senaryoları için **SQLite** kullanılabilmektedir.
* **Frontend:** Hızlı ve modern bir kullanıcı deneyimi (UX) için **Tailwind CSS** tasarım kütüphanesi, kullanıcı etkileşimleri için hafif ve reaktif **Alpine.js**, görsel grafikler için **Chart.js 4.4.0** ve şık bildirim pencereleri için **SweetAlert2** kullanılmıştır.
* **Güvenlik ve Sınırlandırma:** CSRF koruması (`Flask-WTF`), HTTP güvenlik başlıkları (`Flask-Talisman`), brute-force koruması (`Flask-Limiter` ile rate limiting) ve iki faktörlü kimlik doğrulama (2FA/TOTP) sistemin temel güvenlik duvarlarını oluşturur.

---

## 6. ÖLÇEKLENEBİLİRLİK VE YAYIN DURUMU

* **Altyapı:** Platform, bulut ortamında (Oracle Cloud VM) dockerize edilmiş konteynerler (`kokpitim-web`) halinde ve PostgreSQL veritabanı eşliğinde çalışmaktadır.
* **Kapasite ve Performans:** Gunicorn worker yapısı ve asenkron Celery kuyrukları sayesinde sistem, kurumsal düzeyde yüzlerce eşzamanlı kullanıcıyı ve binlerce KPI veri girişini sıfır gecikmeyle işleyebilecek kapasitededir.

---
*Bu kılavuz, Kokpitim platformunun mevcut durumunu, mimari yeteneklerini ve operasyonel gücünü kurumsal standartlarda yansıtmak amacıyla hazırlanmıştır.*


---

## 7. SİSTEM KARTLARI VE DETAYLI AÇIKLAMALARI (SYSTEM CARDS INVENTORY)
Aşağıdaki listede, platformda yer alan tüm işlevsel kartlar, benzersiz kodları, kısa kimlikleri (Short ID) ve veritabanında (`SystemCard.description`) tanımlanmış detaylı açıklamaları bileşen (component) bazında listelenmiştir.

### 🎴 Süreç Performansı kartı Bileşeni Kartları (`surec_performansi_karti`)
**Bileşen:** Süreç Performansı kartı | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PR03` | **process.ortalama_skor** | `process.ortalama_skor` | Tüm süreçlerin performans skorlarının ortalamasını yüzde olarak gösterir. Renk eşiği: ≥%80 yeşil, %50-79 amber, <%50 kırmızı. |
| `-` | **Kurum Özet Kartları** | `kurum_ozet_kartlar` | *Açıklama girilmemiş* |
| `PR07` | **process.surecler** | `process.surecler` | Kurumun tüm süreçlerini Ağaç veya Kanban görünümünde listeleyen ana kart. Başlığında süreçlerin performans durumu özetlenir: Hedefte (skor ≥%80), Risk altında (%50-79), Hedef dışı (<%50) ve Veri yok (PG/skor girilmemiş). Görünüm sağ üstteki Ağaç/Kanban düğmeleriyle değiştirilir. |


### 🎴 Stratejik İlerleme kartı Bileşeni Kartları (`stratejik_ilerleme_karti`)
**Bileşen:** Stratejik İlerleme kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA13` | **masaustu.stratejik_hedefler** | `masaustu.stratejik_hedefler` | Kurumun stratejik hedeflerini (ana stratejiler) kod ve başlıkla özet liste halinde gösterir. Stratejik Planlama sayfasına kısayol içerir. Yalnızca strateji verisi olan kurumlarda görünür. |


### 🎴 SWOT Analizi Bileşeni Kartları (`swot_analizi`)
**Bileşen:** SWOT Analizi | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR46` | **k_rapor_stratejik_analiz.swot_analizi** | `k_rapor_stratejik_analiz.swot_analizi` | SWOT Analizi — k-rapor analiz kartı. |
| `KD05` | **k_radar_ks.swot_analizi** | `k_radar_ks.swot_analizi` | Güçlü/Zayıf yönler ve Fırsat/Tehditleri 4 kadranda özetleyen analiz kartı. Tıklayınca detay modalı açılır. |
| `SPSW01` | **sp_swot.sayfa** | `sp_swot.sayfa` | SWOT analizi sayfasının tamamı — güçlü yönler, zayıf yönler, fırsatlar ve tehditlerin listelendiği tek kart görünümü. |


### 🎴 PESTEL Analizi Bileşeni Kartları (`pestel_analizi`)
**Bileşen:** PESTEL Analizi | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KD07` | **k_radar_ks.pestle_analizi** | `k_radar_ks.pestle_analizi` | Politik/Ekonomik/Sosyal/Teknolojik/Yasal/Çevresel dış faktör analizini özetleyen kart. Tıklayınca detay modalı açılır. |
| `KR44` | **k_rapor_stratejik_analiz.pestel_analizi** | `k_rapor_stratejik_analiz.pestel_analizi` | PESTEL Analizi — k-rapor analiz kartı. |
| `SPPE01` | **sp_pestel.sayfa** | `sp_pestel.sayfa` | PESTEL analizi sayfası; Politik, Ekonomik, Sosyal, Teknolojik, Çevresel ve Yasal dış çevre faktörlerini aktif plan yılı bazında listeler ve düzenlenmesine izin verir. |


### 🎴 TOWS Analizi Bileşeni Kartları (`tows_analizi`)
**Bileşen:** TOWS Analizi | **Kart Sayısı:** 6

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPTW03` | **sp_tows.wo** | `sp_tows.wo` | WO — İyileştirici (Zayıf×Fırsat) strateji kombinasyonu kartı. |
| `KD06` | **k_radar_ks.tows_matrisi** | `k_radar_ks.tows_matrisi` | SWOT bulgularından üretilen SO/ST/WO/WT strateji kombinasyonlarını gösteren analiz kartı. Tıklayınca detay modalı açılır. |
| `KR47` | **k_rapor_stratejik_analiz.tows_matrisi** | `k_rapor_stratejik_analiz.tows_matrisi` | TOWS Matrisi — k-rapor analiz kartı. |
| `SPTW04` | **sp_tows.wt** | `sp_tows.wt` | WT — Geri Çekilmeci (Zayıf×Tehdit) strateji kombinasyonu kartı. |
| `SPTW01` | **sp_tows.so** | `sp_tows.so` | SO — Saldırgan (Güç×Fırsat) strateji kombinasyonu kartı. |
| `SPTW02` | **sp_tows.st** | `sp_tows.st` | ST — Savunmacı (Güç×Tehdit) strateji kombinasyonu kartı. |


### 🎴 Porter 5 Kuvvet Analizi Bileşeni Kartları (`porter_5_kuvvet_analizi`)
**Bileşen:** Porter 5 Kuvvet Analizi | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPPO01` | **sp_porter.sayfa** | `sp_porter.sayfa` | Porter 5 Güç analizinin tamamını içeren, her güç için puan ve madde listesi girilen ana kart; içerik JavaScript ile dinamik olarak oluşturulur. |
| `KR45` | **k_rapor_stratejik_analiz.porter_5_kuvvet** | `k_rapor_stratejik_analiz.porter_5_kuvvet` | Porter 5 Kuvvet — k-rapor analiz kartı. |


### 🎴 VRIO Analizi Bileşeni Kartları (`vrio_analizi`)
**Bileşen:** VRIO Analizi | **Kart Sayısı:** 6

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPVR01` | **sp_vrio.aciklama_degerli** | `sp_vrio.aciklama_degerli` | VRIO çerçevesinin 'Değerli mi?' sorusunu ve anlamını açıklayan bilgi kartı. |
| `SPVR02` | **sp_vrio.aciklama_nadir** | `sp_vrio.aciklama_nadir` | VRIO çerçevesinin 'Nadir mi?' sorusunu ve anlamını açıklayan bilgi kartı. |
| `SPVR06` | **sp_vrio.sonuc_siniflandirmasi** | `sp_vrio.sonuc_siniflandirmasi` | VRIO analizinin çıkabileceği beş rekabet avantajı sonucunu (Dezavantaj, Parite, Geçici, Kullanılmayan, Sürdürülebilir Avantaj) açıklayan lejant kartı. |
| `SPVR04` | **sp_vrio.aciklama_organize** | `sp_vrio.aciklama_organize` | VRIO çerçevesinin 'Organize mi?' sorusunu ve anlamını açıklayan bilgi kartı. |
| `SPVR03` | **sp_vrio.aciklama_taklit_edilemez** | `sp_vrio.aciklama_taklit_edilemez` | VRIO çerçevesinin 'Taklit Edilemez mi?' sorusunu ve anlamını açıklayan bilgi kartı. |
| `SPVR05` | **sp_vrio.kaynak_tablosu** | `sp_vrio.kaynak_tablosu` | Kurumun eklediği tüm kaynak/yeteneklerin VRIO kriterlerine göre işaretlendiği ve rekabet avantajı sonucunun görüldüğü tablo. |


### 🎴 Değer Zinciri Analizi Bileşeni Kartları (`deger_zinciri_analizi`)
**Bileşen:** Değer Zinciri Analizi | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDV01` | **k_radar_kp_deger_zinciri.ozet** | `k_radar_kp_deger_zinciri.ozet` | Eşlenen süreç sayısı, muda riski ve 30 günlük trendi özetleyen kart. |
| `KDV02` | **k_radar_kp_deger_zinciri.faaliyetler** | `k_radar_kp_deger_zinciri.faaliyetler` | Porter değer zinciri birincil ve destek faaliyetlerinin listelendiği ve yönetildiği kart. |


### 🎴 Hızlı Erişim Menüsü Kartı Bileşeni Kartları (`hizli_erisim_menusu_karti`)
**Bileşen:** Hızlı Erişim Menüsü Kartı | **Kart Sayısı:** 18

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPMN13` | **sp_menu.sp-porter** | `sp_menu.sp-porter` | Porter 5 Güç — sektörel rekabet yoğunluğu analizi kısayolu. |
| `SPMN17` | **sp_menu.sp-templates** | `sp_menu.sp-templates` | Plan Şablonları — hazır plan yılı şablonlarından başlama kısayolu. |
| `SPMN16` | **sp_menu.sp-settings-ai** | `sp_menu.sp-settings-ai` | Yapay Zeka Ayarları — AI sağlayıcı, anahtar ve kota yapılandırması kısayolu. |
| `SPMN15` | **sp_menu.sp-digest-weekly.pdf** | `sp_menu.sp-digest-weekly.pdf` | Haftalık Rapor (PDF) — haftalık strateji özet raporu kısayolu. |
| `SPMN14` | **sp_menu.sp-bsc** | `sp_menu.sp-bsc` | Dengeli Karne (BSC) — 4 perspektifte KPI dengesi kısayolu. |
| `SPMN12` | **sp_menu.sp-pestel** | `sp_menu.sp-pestel` | PESTEL Analizi kısayolu. |
| `SPMN11` | **sp_menu.sp-tows** | `sp_menu.sp-tows` | TOWS Matrisi — SWOT türevli 4 strateji kombinasyonu kısayolu. |
| `SPMN10` | **sp_menu.sp-swot** | `sp_menu.sp-swot` | SWOT Analizi — güçlü/zayıf yön, fırsat/tehdit kısayolu. |
| `SPMN09` | **sp_menu.sp-vrio** | `sp_menu.sp-vrio` | VRIO Analizi — kaynak ve yetenek sınıflandırması kısayolu. |
| `SPMN08` | **sp_menu.sp-blue-ocean** | `sp_menu.sp-blue-ocean` | Mavi Okyanus — strateji tuvali ve ERRC tablosu kısayolu. |
| `SPMN07` | **sp_menu.sp-xmatrix** | `sp_menu.sp-xmatrix` | Hoshin X-Matrisi — strateji/hedef/girişim/KPI korelasyon kısayolu. |
| `SPMN06` | **sp_menu.sp-replan-triggers** | `sp_menu.sp-replan-triggers` | Yeniden Planlama Tetikleyicileri — otomatik strateji yeniden değerlendirme kuralları kısayolu. |
| `SPMN05` | **sp_menu.sp-scenarios** | `sp_menu.sp-scenarios` | Senaryolar — iyimser/kötümser/temel senaryo varyasyonları kısayolu. |
| `SPMN04` | **sp_menu.sp-initiatives** | `sp_menu.sp-initiatives` | Girişimler — çok yıllık stratejik girişim listesi kısayolu. |
| `SPMN03` | **sp_menu.sp-ceyreklik-review** | `sp_menu.sp-ceyreklik-review` | Çeyreklik Değerlendirme — üç aylık strateji değerlendirme döngüsü kısayolu. |
| `SPMN02` | **sp_menu.sp-exec-dashboard** | `sp_menu.sp-exec-dashboard` | Yönetici Paneli — stratejik sağlık göstergeleri ve özet panel kısayolu. |
| `SPMN01` | **sp_menu.sp** | `sp_menu.sp` | Stratejik Planlama genel bakış: vizyon, misyon, stratejiler ve K-Vektör paneli kısayolu. |
| `MA06` | **masaustu.hizli_islemler** | `masaustu.hizli_islemler` | En sık kullanılan sayfalara (Bireysel karne, Bildirimler, Süreçler, Stratejik plan, Projeler, Kurum) tek tıkla giden kısayol butonları. |


### 🎴 Stratejik Asistan Kartı Bileşeni Kartları (`stratejik_asistan_karti`)
**Bileşen:** Stratejik Asistan Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PK01` | **process_karne.ai_yonetici_ozeti** | `process_karne.ai_yonetici_ozeti` | Süreç karnesinin en üstünde, yapay zeka tarafından üretilen yönetici özeti. Sürecin performansını, dikkat çeken noktaları ve önerileri kısa bir metinle özetler. AI içeriği yüklendiğinde görünür. |


### 🎴 Dinamik Stratejik Planlama Bileşeni Kartları (`dinamik_stratejik_planlama`)
**Bileşen:** Dinamik Stratejik Planlama | **Kart Sayısı:** 13

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SP11` | **sp.strateji_listesi_ana_stratejiler_alt_stratejiler** | `sp.strateji_listesi_ana_stratejiler_alt_stratejiler` | Burada ana stratejiler detaylandırılır ve her ana strateji altında alt stratejiler tanımlanır. Böylece stratejik plan, yönetilebilir parçalara ayrılır.

• Ana strateji: geniş başlık ve yön
• Alt strateji: somut aksiyon ve ölçülebilir adımlar için temel |
| `SPFL03` | **sp_flow.surec_sayisi** | `sp_flow.surec_sayisi` | Stratejilere bağlı süreç sayısını gösterir. |
| `SPFL02` | **sp_flow.alt_strateji_sayisi** | `sp_flow.alt_strateji_sayisi` | Tanımlı alt strateji sayısını gösterir. |
| `SPFL01` | **sp_flow.ana_strateji_sayisi** | `sp_flow.ana_strateji_sayisi` | Tanımlı ana strateji sayısını gösterir. |
| `SPDF02` | **sp_dynamic_flow.strateji_grafigi** | `sp_dynamic_flow.strateji_grafigi` | Vizyondan performans göstergelerine kadar tüm stratejik hiyerarşiyi görsel bir ağaç grafiği olarak sunan ana kart. |
| `SPDF01` | **sp_dynamic_flow.renk_lejandi** | `sp_dynamic_flow.renk_lejandi` | Grafikteki renk kodlarının (Vizyon, Strateji, Alt Strateji, Süreç, PG) neyi temsil ettiğini gösteren araç çubuğu. |
| `KUA04` | **kurum_ayarlar.yillik_plan_donemleri** | `kurum_ayarlar.yillik_plan_donemleri` | Stratejik Planlama sayfasında yıl bazlı KPI hedefleri ve ağırlıkların kullanılmasını sağlayan yıllık plan dönemi ayarının yönetildiği kart. |
| `SP05` | **sp.etiketsiz_strateji** | `sp.etiketsiz_strateji` | plan_year_id alanı boş olan stratejilerin sayısı. Bunlar hiçbir plan yılına bağlı olmayan eski/legacy kayıtlardır.

Sıfır olması iyidir. Sıfırdan büyükse strateji düzenleme modalı ile her birine bir plan yılı atayın; aksi halde yıl bazlı raporlarda atlanırlar. |
| `SP04` | **sp.plan_donemi** | `sp.plan_donemi` | Şu an aktif olan stratejik plan yılı. Stratejiler, KPI hedefleri ve süreç bağları bu yıla göre filtrelenir.

Yıl değiştirmek için masaüstü veya SP menüsü üzerindeki yıl seçicisini kullanın. Yıl değiştiğinde tüm SP modülleri (X-Matrix, Strateji Haritası, Karne vb.) otomatik olarak hizalanır. |
| `SP02` | **sp.akis_olgunlugu** | `sp.akis_olgunlugu` | Stratejik planlama akışının dört temel adımının (Misyon · Vizyon · Değerler · Strateji listesi) tamamlanma yüzdesidir.

• %75 ve üstü: planlama omurgası hazır
• %50–%74: bazı temel kararlar eksik
• %50 altı: temel tanımları öncelikle tamamlayın |
| `SP01` | **sp.ana_strateji** | `sp.ana_strateji` | Aktif plan döneminde tanımlanmış ana strateji sayısını ve bunların altındaki alt strateji toplamını gösterir.

Yetkin örgütlerde tipik aralık: 4–8 ana strateji ve her ana strateji altında 2–4 alt strateji. Çok az olması yön belirsizliği, çok fazlası odak dağılımı işaretidir. |
| `SPFL05` | **sp_flow.interaktif_grafik** | `sp_flow.interaktif_grafik` | Strateji-süreç-PG bağlantılarını interaktif grafik olarak açan yönlendirme kartı. |
| `SPFL04` | **sp_flow.vizyon** | `sp_flow.vizyon` | Kurumun tanımlı vizyon metnini gösterir. |


### 🎴 Revizyon başlatma Bileşeni Kartları (`revizyon_baslatma`)
**Bileşen:** Revizyon başlatma | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADH04` | **admin_hata_kontrolu.tarama_gecmisi** | `admin_hata_kontrolu.tarama_gecmisi` | Önceki otomatik tarayıcı testi koşularının geçmişini listeler. |
| `ADH06` | **admin_hata_kontrolu.senaryo_gecmisi** | `admin_hata_kontrolu.senaryo_gecmisi` | Önceki CRUD senaryo koşularının geçmişini listeler. |
| `ADH01` | **admin_hata_kontrolu.izole_test_kurumu** | `admin_hata_kontrolu.izole_test_kurumu` | tomofiltest izole test kurumunun durumunu gösterir ve kur/yenile işlemini başlatır. |
| `ADH02` | **admin_hata_kontrolu.kesif_taranacak_sayfalar** | `admin_hata_kontrolu.kesif_taranacak_sayfalar` | Aktif uygulamada güvenli (GET, parametresiz) taranacak sayfaları keşfeder ve listeler. |
| `ADH03` | **admin_hata_kontrolu.otomatik_tarayici_testi** | `admin_hata_kontrolu.otomatik_tarayici_testi` | Gerçek tarayıcı ile tomofiltest üzerinde her sayfayı açıp HTTP/JS/AJAX hatalarını tarar. |


### 🎴 Performans Göstergesi Verisi Bileşeni Kartları (`performans_gostergesi_verisi`)
**Bileşen:** Performans Göstergesi Verisi | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PK06` | **process_karne.risk_altinda** | `process_karne.risk_altinda` | Süreç Karnesi kartı içinde, hedefe yakın ama risk taşıyan (orta seviye) performans göstergelerini listeleyen kanban kolonu. |
| `PK05` | **process_karne.hedefte** | `process_karne.hedefte` | Süreç Karnesi kartı içinde, hedefe ulaşmış (başarı ≥ eşik) performans göstergelerini listeleyen kanban kolonu. |
| `PK07` | **process_karne.hedef_disi** | `process_karne.hedef_disi` | Süreç Karnesi kartı içinde, hedefin altında kalan (kritik) performans göstergelerini listeleyen kanban kolonu. |


### 🎴 Performans Göstergesi Bileşeni Kartları (`performans_gostergesi`)
**Bileşen:** Performans Göstergesi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PK04` | **process_karne.surec_karnesi** | `process_karne.surec_karnesi` | Sürecin tüm performans göstergelerini yıl/periyot filtreli olarak listeleyen ana karne kartı. PG'ler durumlarına göre (Hedefte/Risk/Hedef dışı) kanban kolonlarında gruplanır. Başlık doküman no + süreç adını taşır. |


### 🎴 Performans Trend Analizi  Kartı Bileşeni Kartları (`performans_trend_analizi_karti`)
**Bileşen:** Performans Trend Analizi  Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PK03` | **process_karne.kpi_performans_trend_analizi** | `process_karne.kpi_performans_trend_analizi` | Seçilen bir performans göstergesinin zaman içindeki gerçekleşme trendini çizgi grafikle gösteren açılır/kapanır kart. PG seçimine göre güncellenir. |


### 🎴 Süreç Faaliyetleri Bileşeni Kartları (`surec_faaliyetleri`)
**Bileşen:** Süreç Faaliyetleri | **Kart Sayısı:** 7

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PK12` | **process_karne.faaliyet_devam_edenler** | `process_karne.faaliyet_devam_edenler` | Süreç Faaliyetleri kartı içinde, üzerinde çalışılan (devam eden) faaliyetleri listeleyen kanban kolonu. |
| `SP12` | **sp.surec_iyilestirme_faaliyetleri** | `sp.surec_iyilestirme_faaliyetleri` | Bu kart; stratejilerin sahada hayata geçmesi için süreç bazlı iyileştirme ve operasyonel faaliyetleri temsil eder. Amaç; tanımlı süreçler üzerinden verimlilik, kalite ve süreklilik sağlamaktır.

Strateji ile günlük iş akışı arasında bağ kurar. |
| `PK13` | **process_karne.faaliyet_tamamlanan_iptal** | `process_karne.faaliyet_tamamlanan_iptal` | Süreç Faaliyetleri kartı içinde, tamamlanmış veya iptal edilmiş faaliyetleri listeleyen kanban kolonu. |
| `PK08` | **process_karne.faaliyet_toplam** | `process_karne.faaliyet_toplam` | Süreç faaliyetleri sekmesinde, sürece tanımlı toplam faaliyet sayısını gösteren mini istatistik kartı. |
| `PK09` | **process_karne.faaliyet_tamamlanan** | `process_karne.faaliyet_tamamlanan` | Süreç faaliyetlerinin tamamlanma yüzdesini özetleyen mini istatistik kartı. |
| `PK10` | **process_karne.surec_faaliyetleri** | `process_karne.surec_faaliyetleri` | Sürecin tüm faaliyetlerini Kanban veya aylık takip tablosu görünümünde listeleyen ana kart. Faaliyetler durumlarına göre (Planlananlar/Devam Edenler/Tamamlanan) kolonlara ayrılır. Başlık doküman no + süreç adını taşır. |
| `PK11` | **process_karne.faaliyet_planlananlar** | `process_karne.faaliyet_planlananlar` | Süreç Faaliyetleri kartı içinde, henüz başlamamış (planlanmış) faaliyetleri listeleyen kanban kolonu. |


### 🎴 Misyon Kartı Bileşeni Kartları (`misyon_karti`)
**Bileşen:** Misyon Kartı | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPMS01` | **sp_misyon.misyon** | `sp_misyon.misyon` | Kurumun misyon metnini gösteren kart; sayfa şu anda yapım aşamasındadır. |
| `SP06` | **sp.kimlik** | `sp.kimlik` | Misyon · Vizyon · Değerler üçlüsünün tanımlanma durumunu özetler. Her kalem için ✓ dolu, ○ boş anlamına gelir.

Üçü de tanımlı olduğunda strateji çıkarımı (X-Matrix, OKR, Strateji Haritası gibi) çok daha tutarlı çalışır. |
| `SP07` | **sp.misyon** | `sp.misyon` | Bu adımda kurumun neden var olduğu ve temel görevi netleştirilir. Misyon; paydaşlara “biz kimiz, hangi ihtiyaca cevap veriyoruz?” sorusunun kısa ve tutarlı yanıtıdır.

Burada yazılanlar; vizyon, strateji ve süreç kararlarının üstünde duran referans noktasıdır. |


### 🎴 Değerler Kartı Bileşeni Kartları (`degerler_karti`)
**Bileşen:** Değerler Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SP09` | **sp.degerler_ve_etik_kurallar** | `sp.degerler_ve_etik_kurallar` | Bu kartta kurumun davranış ilkeleri (temel değerler) ve etik çerçeve tanımlanır. Değerler “nasıl çalışırız?”; etik kurallar ise “hangi sınırlar içinde hareket ederiz?” sorusuna cevap verir.

Bunlar; karar alma, iletişim ve performans değerlendirmede ortak dil oluşturur. |


### 🎴 Admin Hata Kontrolü Aracı Bileşeni Kartları (`admin_arac_hata_kontrolu`)
**Bileşen:** Admin Hata Kontrolü Aracı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADA01` | **admin_araclar.hata_kontrolu** | `admin_araclar.hata_kontrolu` | Uygulamanın sayfalarını ve özelliklerini izole test kurumu üzerinde otomatik gezip çalışmayanları raporlayan araç kartı. |


### 🎴 Admin İstatistikler Aracı Bileşeni Kartları (`admin_arac_istatistikler`)
**Bileşen:** Admin İstatistikler Aracı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADA02` | **admin_araclar.istatistikler** | `admin_araclar.istatistikler` | Sistemdeki kurum, kullanıcı, strateji, süreç, performans göstergesi ve proje sayılarını kurum bazında gösteren araç kartı. |


### 🎴 Admin Loglar Aracı Bileşeni Kartları (`admin_arac_loglar`)
**Bileşen:** Admin Loglar Aracı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADA03` | **admin_araclar.loglar** | `admin_araclar.loglar` | Kurum bazında ve genel giriş kayıtlarını, son veri hareketlerini ve hiç giriş yapmamış kullanıcıları listeleyen araç kartı. |


### 🎴 Admin Yedekleme Aracı Bileşeni Kartları (`admin_arac_yedekleme`)
**Bileşen:** Admin Yedekleme Aracı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADA04` | **admin_araclar.yedekleme** | `admin_araclar.yedekleme` | Otomatik gece yedekleri ve manuel indirilebilir DB/kod yedeklerini yönetmeye, geri yüklemeye yarayan araç kartı. |


### 🎴 Admin Hata Kontrolü Paneli Bileşeni Kartları (`admin_hata_kontrolu_paneli`)
**Bileşen:** Admin Hata Kontrolü Paneli | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADH05` | **admin_hata_kontrolu.aktif_crud_senaryolari** | `admin_hata_kontrolu.aktif_crud_senaryolari` | tomofiltest üzerinde gerçek UI etkileşimiyle CRUD senaryolarını çalıştırır. |


### 🎴 Kart Hiyerarşisi Görünümü Bileşeni Kartları (`admin_kart_hiyerarsisi`)
**Bileşen:** Kart Hiyerarşisi Görünümü | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADY01` | **admin_hierarchy.sayfa** | `admin_hierarchy.sayfa` | Paket → Modül → Bileşen → Kart → Veri kaynağı hiyerarşisinin tamamını gösteren tek sayfa görünümü. |


### 🎴 Holding Dashboard Bileşeni Kartları (`holding_dashboard`)
**Bileşen:** Holding Dashboard | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `HLD03` | **admin_holding_dashboard.yuksek_anomali** | `admin_holding_dashboard.yuksek_anomali` | Tüm alt kurumlar genelinde yüksek şiddetli KPI anomali sayısını gösterir. |
| `HLD01` | **admin_holding_dashboard.ozet_skor** | `admin_holding_dashboard.ozet_skor` | Holdinge bağlı tüm alt kurumların ortalama sağlık skoru ile toplam kurum, kullanıcı, KPI ve girişim sayılarını gösteren özet kart. |
| `HLD05` | **admin_holding_dashboard.karsilastirma_grafik** | `admin_holding_dashboard.karsilastirma_grafik` | Alt kurumların sağlık skorlarını yan yana karşılaştıran çubuk grafik. |
| `HLD04` | **admin_holding_dashboard.gecikmis_faaliyet** | `admin_holding_dashboard.gecikmis_faaliyet` | Tüm alt kurumlar genelinde gecikmiş faaliyet/girişim sayısını gösterir. |
| `HLD02` | **admin_holding_dashboard.kritik_risk** | `admin_holding_dashboard.kritik_risk` | Tüm alt kurumlar genelinde toplam kritik risk sayısını gösterir. |


### 🎴 Holding Alt Kurum Detayı Bileşeni Kartları (`holding_drilldown`)
**Bileşen:** Holding Alt Kurum Detayı | **Kart Sayısı:** 9

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `HLT07` | **admin_holding_drilldown.kullanici_senaryo** | `admin_holding_drilldown.kullanici_senaryo` | Alt kurumdaki kullanıcı ve senaryo sayısını gösteren istatistik kutusu. |
| `HLT06` | **admin_holding_drilldown.yuksek_anomali** | `admin_holding_drilldown.yuksek_anomali` | Yüksek seviyeli anomali sayısını orta seviye anomali sayısıyla birlikte gösteren istatistik kutusu. |
| `HLT05` | **admin_holding_drilldown.kritik_risk** | `admin_holding_drilldown.kritik_risk` | Kritik risk sayısını ve açık risk sayısını gösteren istatistik kutusu. |
| `HLT04` | **admin_holding_drilldown.gecikmis_faaliyet** | `admin_holding_drilldown.gecikmis_faaliyet` | Gecikmiş faaliyet sayısını toplam faaliyet sayısıyla birlikte gösteren istatistik kutusu. |
| `HLT03` | **admin_holding_drilldown.girisim_ortalamasi** | `admin_holding_drilldown.girisim_ortalamasi` | Devam eden girişimlerin ortalama ilerleme yüzdesini gösteren istatistik kutusu. |
| `HLT02` | **admin_holding_drilldown.kpi_hedef_ustu** | `admin_holding_drilldown.kpi_hedef_ustu` | Hedef üstü performans gösteren KPI oranını gösteren istatistik kutusu. |
| `HLT01` | **admin_holding_drilldown.saglik_skoru** | `admin_holding_drilldown.saglik_skoru` | Alt kurumun strateji sağlık skorunu, KPI/strateji/girişim özet sayılarını gösteren üst özet kartı. |
| `HLT09` | **admin_holding_drilldown.risk_listesi** | `admin_holding_drilldown.risk_listesi` | Alt kurumun risk kayıtlarını olasılık, etki ve skor bilgisiyle listeleyen tablo kartı. |
| `HLT08` | **admin_holding_drilldown.girisimler** | `admin_holding_drilldown.girisimler` | Alt kurumun stratejik girişimlerini durum, öncelik ve ilerleme bilgisiyle listeleyen tablo kartı. |


### 🎴 Sistem İstatistikleri Bileşeni Kartları (`admin_sistem_istatistikleri`)
**Bileşen:** Sistem İstatistikleri | **Kart Sayısı:** 10

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADI09` | **admin_istatistikler.ozet_proje_task** | `admin_istatistikler.ozet_proje_task` | Tüm kurumlardaki toplam proje görevi (task) sayısını gösterir. |
| `ADI01X2` | **admin_istatistikler.ozet_kurum** | `admin_istatistikler.ozet_kurum` | Sistemde kayıtlı aktif kurum sayısını gösterir. |
| `ADI02` | **admin_istatistikler.ozet_kullanici** | `admin_istatistikler.ozet_kullanici` | Sistemdeki toplam aktif kullanıcı sayısını gösterir. |
| `ADI03` | **admin_istatistikler.ozet_ana_strateji** | `admin_istatistikler.ozet_ana_strateji` | Tüm kurumlardaki toplam ana strateji sayısını gösterir. |
| `ADI01` | **admin_istatistikler.kurum_dagilim_tablosu** | `admin_istatistikler.kurum_dagilim_tablosu` | Her kurum ve alt kurum için kullanıcı, strateji, süreç, PG ve proje sayılarını kırılım halinde gösteren tablo. |
| `ADI04` | **admin_istatistikler.ozet_alt_strateji** | `admin_istatistikler.ozet_alt_strateji` | Tüm kurumlardaki toplam alt strateji sayısını gösterir. |
| `ADI05` | **admin_istatistikler.ozet_surec** | `admin_istatistikler.ozet_surec` | Tüm kurumlardaki toplam süreç sayısını gösterir. |
| `ADI06` | **admin_istatistikler.ozet_pg** | `admin_istatistikler.ozet_pg` | Tüm kurumlardaki toplam performans göstergesi (PG) sayısını gösterir. |
| `ADI07` | **admin_istatistikler.ozet_pg_verisi** | `admin_istatistikler.ozet_pg_verisi` | Performans göstergelerine girilen toplam veri kaydı sayısını gösterir. |
| `ADI08` | **admin_istatistikler.ozet_proje** | `admin_istatistikler.ozet_proje` | Tüm kurumlardaki toplam proje sayısını gösterir. |


### 🎴 Kılavuz ve Video Oluşturucu Bileşeni Kartları (`admin_kilavuz_olusturucu`)
**Bileşen:** Kılavuz ve Video Oluşturucu | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADK05` | **admin_kilavuz_olusturucu.kilavuz_pdf_indirme** | `admin_kilavuz_olusturucu.kilavuz_pdf_indirme` | En güncel derlenmiş kılavuz PDF dosyasının indirilebildiği kart. |
| `ADK03` | **admin_kilavuz_olusturucu.video_galerisi** | `admin_kilavuz_olusturucu.video_galerisi` | Üretilen kısa konu anlatım videolarının listelendiği galeri kartı. |
| `ADK01` | **admin_kilavuz_olusturucu.kontrol_paneli** | `admin_kilavuz_olusturucu.kontrol_paneli` | Otonom çekimi başlatma/durdurma butonları ile ilerleme çubuğunu gösteren kontrol paneli kartı. |
| `ADK02` | **admin_kilavuz_olusturucu.calisma_loglari** | `admin_kilavuz_olusturucu.calisma_loglari` | Otonom çekim sürecinin canlı terminal log çıktısını gösteren kart. |
| `ADK04` | **admin_kilavuz_olusturucu.yenitomofil_durumu** | `admin_kilavuz_olusturucu.yenitomofil_durumu` | YeniTomofil örnek kurumunun kurulum durumunu (strateji, süreç, PG/KPI sayıları) gösteren bilgi kartı. |


### 🎴 Giriş ve Aktivite Logları Bileşeni Kartları (`admin_giris_loglari`)
**Bileşen:** Giriş ve Aktivite Logları | **Kart Sayısı:** 7

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADL06` | **admin_loglar.hic_giris_yapmamis_kullanicilar** | `admin_loglar.hic_giris_yapmamis_kullanicilar` | Hesabı aktif ama hiç oturum açmamış kullanıcıların listesini gösteren katlanabilir kart. |
| `ADL04` | **admin_loglar.hic_giris_yapmamis** | `admin_loglar.hic_giris_yapmamis` | Hesabı aktif olup hiç oturum açmamış kullanıcı sayısını gösterir. |
| `ADL03` | **admin_loglar.son_veri_hareketi** | `admin_loglar.son_veri_hareketi` | En son yapılan veri değişikliğini ve kimin yaptığını gösterir. |
| `ADL02` | **admin_loglar.son_giris** | `admin_loglar.son_giris` | En son kimin, hangi kurumdan, ne zaman giriş yaptığını gösterir. |
| `ADL01` | **admin_loglar.toplam_giris** | `admin_loglar.toplam_giris` | Sistemdeki toplam giriş sayısını gösterir. |
| `ADL07` | **admin_loglar.son_hareketler** | `admin_loglar.son_hareketler` | Genel giriş ve veri değişikliği hareketlerinin kronolojik akışını gösteren katlanabilir kart. |
| `ADL05` | **admin_loglar.kurum_bazinda** | `admin_loglar.kurum_bazinda` | Her aktif kurumun giriş ve veri hareketi özetini tablo olarak listeler. |


### 🎴 Bildirim Yönetimi Bileşeni Kartları (`admin_bildirim_yonetimi`)
**Bileşen:** Bildirim Yönetimi | **Kart Sayısı:** 6

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADN02` | **admin_notifications.okunmamis_bildirim** | `admin_notifications.okunmamis_bildirim` | Henüz okunmamış bildirim sayısını gösterir. |
| `ADN06` | **admin_notifications.bildirim_listesi** | `admin_notifications.bildirim_listesi` | Tüm bildirimlerin başlık, mesaj, tip, alıcı, tarih ve durum bilgileriyle listelendiği tablo. |
| `ADN05` | **admin_notifications.filtre** | `admin_notifications.filtre` | Bildirimleri başlık/mesaj, tip ve okunma durumuna göre filtrelemeyi sağlar. |
| `ADN04` | **admin_notifications.yayin_bildirimi** | `admin_notifications.yayin_bildirimi` | Toplu yayın (system_broadcast) türündeki bildirim sayısını gösterir. |
| `ADN03` | **admin_notifications.okunmus_bildirim** | `admin_notifications.okunmus_bildirim` | Okunmuş bildirim sayısını gösterir. |
| `ADN01` | **admin_notifications.toplam_bildirim** | `admin_notifications.toplam_bildirim` | Sistemde kayıtlı toplam bildirim sayısını gösterir. |


### 🎴 Paket ve Modül Yönetimi Bileşeni Kartları (`admin_paket_modul_yonetimi`)
**Bileşen:** Paket ve Modül Yönetimi | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADP01` | **admin_packages.abonelik_paketleri** | `admin_packages.abonelik_paketleri` | Tanımlı abonelik paketlerini listeler; paket ekleme, düzenleme, modül atama ve aktif/pasif durumu değiştirme işlemlerini sağlar. |
| `ADP02` | **admin_packages.sistem_modulleri** | `admin_packages.sistem_modulleri` | Sistemdeki modülleri listeler; yeni modül ekleme ve modüllerin aktif/pasif durumunu değiştirme işlemlerini sağlar. |


### 🎴 Alt Kurum Yönetimi Bileşeni Kartları (`admin_alt_kurum_yonetimi`)
**Bileşen:** Alt Kurum Yönetimi | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADS02` | **admin_sub_tenants.alt_kurum_listesi** | `admin_sub_tenants.alt_kurum_listesi` | Tüm alt kurumları; ilk admin, paket, kullanıcı sayısı, durum ve işlem butonlarıyla birlikte listeleyen tablo kartı. |
| `ADS01` | **admin_sub_tenants.ozet_kart** | `admin_sub_tenants.ozet_kart` | Üst kurumun adı, tipi (holding/bayi), aktif alt kurum sayısı ve kota bilgisini gösteren özet kart. |


### 🎴 Alt Kurum Kullanım Raporu Bileşeni Kartları (`admin_alt_kurum_kullanim_raporu`)
**Bileşen:** Alt Kurum Kullanım Raporu | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADSU02` | **admin_sub_tenants_usage.paket_dagilimi** | `admin_sub_tenants_usage.paket_dagilimi` | Alt kurumların hangi pakete sahip olduğunu oransal çubuklarla gösteren dağılım kartı. |
| `ADSU03` | **admin_sub_tenants_usage.detay_tablosu** | `admin_sub_tenants_usage.detay_tablosu` | Her alt kurumun paket, kullanıcı doluluğu, KPI, girişim ve LLM kullanım detaylarını satır satır listeleyen tablo kartı. |
| `ADSU01` | **admin_sub_tenants_usage.ozet_toplam** | `admin_sub_tenants_usage.ozet_toplam` | Seçili döneme ait toplam kurum, kullanıcı, KPI, LLM çağrı ve maliyet özetini gösteren üst bilgi kartı. |


### 🎴 Kurum Yönetimi Bileşeni Kartları (`admin_kurum_yonetimi`)
**Bileşen:** Kurum Yönetimi | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADT04` | **admin_tenants.toplam_kullanici** | `admin_tenants.toplam_kullanici` | Tüm kurumlardaki toplam kullanıcı sayısını gösterir. |
| `ADT03` | **admin_tenants.arsivlenmis_kurum** | `admin_tenants.arsivlenmis_kurum` | Arşivlenmiş (pasif) kurum sayısını gösterir. |
| `ADT02` | **admin_tenants.aktif_kurum** | `admin_tenants.aktif_kurum` | Aktif (arşivlenmemiş) durumdaki kurum sayısını gösterir. |
| `ADT01` | **admin_tenants.toplam_kurum** | `admin_tenants.toplam_kurum` | Sistemde kayıtlı toplam kurum sayısını gösterir. |
| `ADT05` | **admin_tenants.kurum_listesi** | `admin_tenants.kurum_listesi` | Kurumların adı, tipi, sektörü, paketi, lisans bitiş tarihi ve durumunu listeleyen tablodur. |


### 🎴 Kullanıcı Yönetimi Bileşeni Kartları (`admin_kullanici_yonetimi`)
**Bileşen:** Kullanıcı Yönetimi | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADU02` | **admin_users.toplam_kullanici** | `admin_users.toplam_kullanici` | Sistemdeki toplam kullanıcı sayısını gösteren özet kart. |
| `ADU03` | **admin_users.aktif_kullanici** | `admin_users.aktif_kullanici` | Aktif durumdaki kullanıcı sayısını gösteren özet kart. |
| `ADU04` | **admin_users.pasif_kullanici** | `admin_users.pasif_kullanici` | Pasif durumdaki kullanıcı sayısını gösteren özet kart. |
| `ADU01` | **admin_users.arama_filtre** | `admin_users.arama_filtre` | Kullanıcıları isim, e-posta, rol veya kurum bilgisine göre arama ve kuruma göre filtreleme alanı. |
| `ADU05` | **admin_users.kullanici_listesi** | `admin_users.kullanici_listesi` | Ad, e-posta, rol, kurum ve durum bilgileriyle birlikte tüm kullanıcıların listelendiği ve düzenlenebildiği tablo. |


### 🎴 Yedekleme Aracı Bileşeni Kartları (`admin_yedekleme_araci`)
**Bileşen:** Yedekleme Aracı | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADY203` | **admin_yedekleme.yedek_listesi** | `admin_yedekleme.yedek_listesi` | Otomatik olarak üretilmiş tüm DB ve kod yedeklerinin listesini, boyutunu ve indirme bağlantısını gösterir. |
| `ADY201` | **admin_yedekleme.manuel_yedek** | `admin_yedekleme.manuel_yedek` | Anlık DB (.dump) veya kod (.tar.gz) yedeği üretip bu makineye indirmeyi sağlar. |
| `ADY202` | **admin_yedekleme.otomatik_yedek_durumu** | `admin_yedekleme.otomatik_yedek_durumu` | Her gece 02:00'de çalışan otomatik yedeğin son çalışma zamanını gösterir ve manuel olarak hemen tetiklemeyi sağlar. |
| `ADY204` | **admin_yedekleme.db_geri_yukleme** | `admin_yedekleme.db_geri_yukleme` | Yüklenen bir .dump dosyasını mevcut veritabanının üzerine geri yükleyen, şifre ve onay metni gerektiren yıkıcı işlem kartı. |


### 🎴 Yönetim Paneli Özeti Bileşeni Kartları (`admin_yonetim_paneli_ozet`)
**Bileşen:** Yönetim Paneli Özeti | **Kart Sayısı:** 10

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `ADYP05` | **admin_yonetim_paneli.son_24_saat** | `admin_yonetim_paneli.son_24_saat` | Son 24 saatte giriş yapan tekil kullanıcı sayısını gösterir. |
| `ADYP10` | **admin_yonetim_paneli.son_aktiviteler** | `admin_yonetim_paneli.son_aktiviteler` | Sistemdeki son kullanıcı aktivitelerinin audit log kayıtlarını listeler. |
| `ADYP09` | **admin_yonetim_paneli.kullanici_durumu** | `admin_yonetim_paneli.kullanici_durumu` | Kullanıcıların rol, hesap durumu ve son giriş bilgilerini listeleyen tablo kartı. |
| `ADYP08` | **admin_yonetim_paneli.tum_zamanlar** | `admin_yonetim_paneli.tum_zamanlar` | Tüm zamanlarda giriş yapmış tekil kullanıcı sayısını gösterir. |
| `ADYP01` | **admin_yonetim_paneli.bakim_modu** | `admin_yonetim_paneli.bakim_modu` | Sistemi bakım moduna alıp yalnızca Admin rolüne izin veren kontrol kartı. |
| `ADYP02` | **admin_yonetim_paneli.kurum_secimi** | `admin_yonetim_paneli.kurum_secimi` | İstatistiklerin hangi kurum için gösterileceğini seçmeye yarayan filtre kartı. |
| `ADYP07` | **admin_yonetim_paneli.son_30_gun** | `admin_yonetim_paneli.son_30_gun` | Son 30 günde giriş yapan tekil kullanıcı sayısını gösterir. |
| `ADYP06` | **admin_yonetim_paneli.son_7_gun** | `admin_yonetim_paneli.son_7_gun` | Son 7 günde giriş yapan tekil kullanıcı sayısını gösterir. |
| `ADYP03` | **admin_yonetim_paneli.cevrimici** | `admin_yonetim_paneli.cevrimici` | Son 30 dakikada aktif olan çevrimiçi kullanıcı sayısını gösterir. |
| `ADYP04` | **admin_yonetim_paneli.aktif_hesap** | `admin_yonetim_paneli.aktif_hesap` | Toplam kayıtlı kullanıcı sayısını gösterir. |


### 🎴 E-posta Bildirim Ayarları Bileşeni Kartları (`eposta_bildirim_ayarlari`)
**Bileşen:** E-posta Bildirim Ayarları | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `AYE02` | **ayarlar_eposta.bildirim_tercihleri** | `ayarlar_eposta.bildirim_tercihleri` | Hangi olaylarda (süreç atama, PG değişikliği, faaliyet ekleme, görev atama) e-posta bildirimi gönderileceğini belirleyen tercihler kartı. |
| `AY07` | **ayarlar.eposta_bildirimleri** | `ayarlar.eposta_bildirimleri` | SMTP yapılandırması ve e-posta bildirim tercihlerine götüren bağlantı kartı. |


### 🎴 Hesap Ayarları Bileşeni Kartları (`hesap_ayarlari`)
**Bileşen:** Hesap Ayarları | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `AY05` | **ayarlar.hesap_ayarlari** | `ayarlar.hesap_ayarlari` | Bildirim tercihleri, tema, dil ve saat dilimi ayarlarına götüren bağlantı kartı. |
| `AY06` | **ayarlar.profil_bilgileri** | `ayarlar.profil_bilgileri` | Ad, unvan, departman ve profil fotoğrafı düzenleme sayfasına götüren bağlantı kartı. |


### 🎴 Kurum Ayarları Bileşeni Kartları (`kurum_ayarlari`)
**Bileşen:** Kurum Ayarları | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `AY09` | **ayarlar.kurum_ayarlari** | `ayarlar.kurum_ayarlari` | Kurumun iletişim bilgileri ve logo ayarlarını düzenleme sayfasına götüren bağlantı kartı (kurum yöneticisine özel). |


### 🎴 Yönetim Paneli (Admin) Bileşeni Kartları (`admin_yonetim_paneli`)
**Bileşen:** Yönetim Paneli (Admin) | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `AY10` | **ayarlar.yonetim_paneli** | `ayarlar.yonetim_paneli` | Platform genelinde login istatistikleri ve aktivite kayıtlarını görüntüleme sayfasına götüren bağlantı kartı (yalnız Admin). |


### 🎴 Zamanlanmış Raporlar Bileşeni Kartları (`zamanlanmis_raporlar`)
**Bileşen:** Zamanlanmış Raporlar | **Kart Sayısı:** 6

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `AYZ02` | **ayarlar_zamanlanmis_raporlar.sabah_operasyonel_ozeti** | `ayarlar_zamanlanmis_raporlar.sabah_operasyonel_ozeti` | Bugüne ait bekleyen faaliyet, görev ve kritik PG'lerin sabah e-posta özetinin gönderim saatini ayarlar. |
| `AYZ01` | **ayarlar_zamanlanmis_raporlar.haftalik_strateji_ozeti** | `ayarlar_zamanlanmis_raporlar.haftalik_strateji_ozeti` | Haftalık strateji sağlık skoru, PG performansı ve risk özetinin PDF olarak e-posta ile otomatik gönderimini ayarlar. |
| `AY08` | **ayarlar.zamanlanmis_raporlar** | `ayarlar.zamanlanmis_raporlar` | Haftalık özet, sabah operasyonel, risk uyarısı ve aylık PG raporu aboneliklerini yönetme sayfasına götüren bağlantı kartı. |
| `AY04` | **ayarlar.zamanlanmis_rapor_ozeti** | `ayarlar.zamanlanmis_rapor_ozeti` | Kullanıcının aktif zamanlanmış rapor aboneliği sayısını gösteren özet kart. |
| `AYZ03` | **ayarlar_zamanlanmis_raporlar.risk_anomali_uyarisi** | `ayarlar_zamanlanmis_raporlar.risk_anomali_uyarisi` | Açık kritik riskler ve PG anomalilerine ilişkin uyarı e-postasının sıklığını ayarlar. |
| `AYZ04` | **ayarlar_zamanlanmis_raporlar.aylik_pg_raporu** | `ayarlar_zamanlanmis_raporlar.aylik_pg_raporu` | Ay sonu tüm PG durumunu özetleyen Excel ekli raporun otomatik gönderim gününü ve saatini ayarlar. |


### 🎴 Özel SMTP Yapılandırması Bileşeni Kartları (`ozel_smtp_yapilandirmasi`)
**Bileşen:** Özel SMTP Yapılandırması | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `AYE01` | **ayarlar_eposta.ozel_smtp** | `ayarlar_eposta.ozel_smtp` | Kurumun kendi SMTP sunucusunu tanımlayıp e-posta gönderimini bu sunucu üzerinden yapmasını sağlayan kart. |


### 🎴 Bireysel Karne AI Özeti Bileşeni Kartları (`bireysel_karne_ai_ozet`)
**Bileşen:** Bireysel Karne AI Özeti | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `BR201` | **bireysel_karne.ai_ozet** | `bireysel_karne.ai_ozet` | Seçili yıla göre otomatik veya yapay zeka destekli kısa performans özetini gösteren şerit. |


### 🎴 Bireysel Karne Özet Görselleri Bileşeni Kartları (`bireysel_karne_ozet_gorseller`)
**Bileşen:** Bireysel Karne Özet Görselleri | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `BR203` | **bireysel_karne.ilerleme_halkalari** | `bireysel_karne.ilerleme_halkalari` | PG veri kapsamı ve faaliyet tamamlama oranlarını gösteren dairesel ilerleme grafikleri. |
| `BR208` | **bireysel_karne.yil_ozeti** | `bireysel_karne.yil_ozeti` | Seçili yıldaki veri kapsamı ve göstergelere ilişkin kısa özet ile dikkat çeken uyarıları listeleyen kart. |


### 🎴 Bireysel Karne İstatistikleri Bileşeni Kartları (`bireysel_karne_istatistikleri`)
**Bileşen:** Bireysel Karne İstatistikleri | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `BR204` | **bireysel_karne.stat_toplam_pg** | `bireysel_karne.stat_toplam_pg` | Kullanıcıya atanmış toplam performans göstergesi sayısını gösteren istatistik kartı. |
| `BR206` | **bireysel_karne.stat_faaliyetler** | `bireysel_karne.stat_faaliyetler` | Kullanıcının toplam faaliyet sayısını gösteren istatistik kartı. |
| `BR205` | **bireysel_karne.stat_veri_girilen** | `bireysel_karne.stat_veri_girilen` | Veri girişi yapılmış performans göstergesi sayısını gösteren istatistik kartı. |
| `BR207` | **bireysel_karne.stat_tamamlanan** | `bireysel_karne.stat_tamamlanan` | Faaliyetlerin tamamlanma yüzdesini gösteren istatistik kartı. |


### 🎴 Bireysel Karne Zaman Çizelgesi Bileşeni Kartları (`bireysel_karne_zaman_cizelgesi`)
**Bileşen:** Bireysel Karne Zaman Çizelgesi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `BR209` | **bireysel_karne.zaman_cizelgesi** | `bireysel_karne.zaman_cizelgesi` | Seçili yıl içinde girilen PG verisi ve işaretlenen faaliyetlerin kronolojik dökümünü gösteren kart. |


### 🎴 Bireysel Karne Detay Tabloları Bileşeni Kartları (`bireysel_karne_detay_tablolari`)
**Bileşen:** Bireysel Karne Detay Tabloları | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `BR210` | **bireysel_karne.pg_tablosu** | `bireysel_karne.pg_tablosu` | Kullanıcının performans göstergelerini aylık bazda hedef, gerçekleşen ve veri durumu ile listeleyen tablo kartı. |
| `BR211` | **bireysel_karne.faaliyet_tablosu** | `bireysel_karne.faaliyet_tablosu` | Kullanıcının faaliyetlerini aylık bazda durum ve tamamlanma bilgisiyle listeleyen tablo kartı. |


### 🎴 K-Radar Çapraz Risk Analizi Bileşeni Kartları (`k_radar_cross_risk_analizi`)
**Bileşen:** K-Radar Çapraz Risk Analizi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDC01` | **k_radar_cross.risk_isi_haritasi** | `k_radar_cross.risk_isi_haritasi` | Radar bazlı olasılık ve etki noktalarının etkileşimli risk ısı haritası özetini gösterir. |


### 🎴 K-Radar A3 Raporları Bileşeni Kartları (`k_radar_cross_a3`)
**Bileşen:** K-Radar A3 Raporları | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDCA01` | **k_radar_cross_a3.a3_ozeti** | `k_radar_cross_a3.a3_ozeti` | A3 raporlarının toplam sayısını ve kök neden kapsam oranını gösteren özet kartı. |


### 🎴 K-Radar Çapraz Anket Bileşeni Kartları (`k_radar_cross_anket`)
**Bileşen:** K-Radar Çapraz Anket | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDCK01` | **k_radar_cross_anket.anket_ozeti** | `k_radar_cross_anket.anket_ozeti` | Cross anket sayısı ve ortalama skoru özetleyen kart. |


### 🎴 K-Radar Paydaş Yönetimi Bileşeni Kartları (`k_radar_cross_paydas`)
**Bileşen:** K-Radar Paydaş Yönetimi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDCP01` | **k_radar_cross_paydas.paydas_listesi** | `k_radar_cross_paydas.paydas_listesi` | Paydaşların ad, rol, etki, ilgi ve strateji bilgilerini listeleyen ve yönetimini sağlayan kart. |


### 🎴 K-Radar Rekabet Analizi Bileşeni Kartları (`k_radar_cross_rekabet`)
**Bileşen:** K-Radar Rekabet Analizi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDCR01` | **k_radar_cross_rekabet.rekabet_ozeti** | `k_radar_cross_rekabet.rekabet_ozeti` | Kayıt sayısı ve ortalama rekabet gap değerini gösteren özet kart. |


### 🎴 KP-Radar Skoru Bileşeni Kartları (`k_radar_kp_skoru`)
**Bileşen:** KP-Radar Skoru | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KD23` | **k_radar_kp.kritik_pg** | `k_radar_kp.kritik_pg` | Hedef altında kalan kritik süreç PG sayısını gösteren mini istatistik kartı. |
| `KD22` | **k_radar_kp.band** | `k_radar_kp.band` | KP-Radar skorunun renk/durum bandını gösteren mini istatistik kartı. |
| `KD21` | **k_radar_kp.toplam_skor** | `k_radar_kp.toplam_skor` | KP-Radar (süreç) PG ağırlıklı toplam skorunu gösteren mini istatistik kartı. |
| `KD24` | **k_radar_kp.hesaplanan_pg** | `k_radar_kp.hesaplanan_pg` | KP-Radar skoruna giren aktif hesaplanan PG sayısını gösteren mini istatistik kartı. |


### 🎴 KP-Radar Kıyaslama Bileşeni Kartları (`k_radar_kp_benchmark`)
**Bileşen:** KP-Radar Kıyaslama | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDB01` | **k_radar_kp_benchmark.benchmark_ozeti** | `k_radar_kp_benchmark.benchmark_ozeti` | Karşılaştırılabilirlik skoru, dönem satır sayısı ve 30 günlük trendi gösteren özet kart. |


### 🎴 KP-Radar Darboğaz Analizi Bileşeni Kartları (`k_radar_kp_darbogaz`)
**Bileşen:** KP-Radar Darboğaz Analizi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDD01` | **k_radar_kp_darbogaz.ozet** | `k_radar_kp_darbogaz.ozet` | Kritik PG, şiddet endeksi ve 30 günlük trend bilgilerini gösteren darboğaz özet kartı. |


### 🎴 KP-Radar Kapasite Analizi Bileşeni Kartları (`k_radar_kp_kapasite`)
**Bileşen:** KP-Radar Kapasite Analizi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDA01` | **k_radar_kp_kapasite.kapasite_ozeti** | `k_radar_kp_kapasite.kapasite_ozeti` | Kullanım tahmini, kaynak baskısı ve 30 günlük trend değerlerini özetleyen kart. |


### 🎴 KP-Radar OEE Analizi Bileşeni Kartları (`k_radar_kp_oee`)
**Bileşen:** KP-Radar OEE Analizi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDO01` | **k_radar_kp_oee.ozet** | `k_radar_kp_oee.ozet` | OEE, kullanılabilirlik, performans ve kalite değerleriyle 30 günlük trendi gösteren özet kartı. |


### 🎴 KP-Radar Süreç Olgunluğu Bileşeni Kartları (`k_radar_kp_olgunluk`)
**Bileşen:** KP-Radar Süreç Olgunluğu | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDM01` | **k_radar_kp_olgunluk.olgunluk_takip** | `k_radar_kp_olgunluk.olgunluk_takip` | Süreçlerin olgunluk seviyesi kayıtlarını ekleme, filtreleme ve listeleme kartı. |


### 🎴 KP-Radar Pareto Analizi Bileşeni Kartları (`k_radar_kp_pareto`)
**Bileşen:** KP-Radar Pareto Analizi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDPA01` | **k_radar_kp_pareto.ozet** | `k_radar_kp_pareto.ozet` | Pareto analizinin özet kartı: en yüksek etkili dilim, toplam KPI sayısı ve son 30 günlük trend bilgisini gösterir. |


### 🎴 KP-Radar SLA Analizi Bileşeni Kartları (`k_radar_kp_sla`)
**Bileşen:** KP-Radar SLA Analizi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDSL01` | **k_radar_kp_sla.ozet** | `k_radar_kp_sla.ozet` | SLA ihlal riski, gözlenen satır sayısı ve 30 günlük trend özetini gösterir. |


### 🎴 KP-Radar Değer Akışı (VSM) Bileşeni Kartları (`k_radar_kp_vsm`)
**Bileşen:** KP-Radar Değer Akışı (VSM) | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDVS01` | **k_radar_kp_vsm.vsm_ozeti** | `k_radar_kp_vsm.vsm_ozeti` | Akış verimliliği, israf baskısı ve 30 günlük trend değerlerini gösteren VSM özet kartı. |


### 🎴 KPR Proje Radarı Bileşeni Kartları (`k_radar_kpr_proje_radari`)
**Bileşen:** KPR Proje Radarı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KPR01` | **k_radar_kpr.proje_radari** | `k_radar_kpr.proje_radari` | Proje sağlık skoru, bandı, kritik proje ve aktif proje sayısını özetleyen radar kartı. |


### 🎴 KPR Kritik Yol Analizi Bileşeni Kartları (`k_radar_kpr_cpm`)
**Bileşen:** KPR Kritik Yol Analizi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KPC01` | **k_radar_kpr_cpm.cpm_analizi** | `k_radar_kpr_cpm.cpm_analizi` | Proje seçip kritik yol analizini (görev, bağımlılık, kritik başlangıç sayıları ve liste) görüntülemeyi sağlayan tek kart. |


### 🎴 KPR Kazanılmış Değer Analizi Bileşeni Kartları (`k_radar_kpr_evm`)
**Bileşen:** KPR Kazanılmış Değer Analizi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KPE01` | **k_radar_kpr_evm.ozet** | `k_radar_kpr_evm.ozet` | Son EVM snapshot sayısı ile ortalama SPI ve CPI değerlerini özetleyen kart. |


### 🎴 KPR Gantt Takibi Bileşeni Kartları (`k_radar_kpr_gantt`)
**Bileşen:** KPR Gantt Takibi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KPG01` | **k_radar_kpr_gantt.gantt_ozeti** | `k_radar_kpr_gantt.gantt_ozeti` | Zaman çizelgeli görev sayısı ve zamanında tamamlanma oranını özetleyen kart. |


### 🎴 KPR Kaynak Kapasitesi Bileşeni Kartları (`k_radar_kpr_kaynak_kapasite`)
**Bileşen:** KPR Kaynak Kapasitesi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KPK01` | **k_radar_kpr_kaynak_kapasite.ozet** | `k_radar_kpr_kaynak_kapasite.ozet` | Kaynak yükü, gecikmiş açık görev ve aktif görev sayısını özetleyen kart. |


### 🎴 KPR Risk Yönetimi Bileşeni Kartları (`k_radar_kpr_risk`)
**Bileşen:** KPR Risk Yönetimi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KPRI01` | **k_radar_kpr_risk.risk_ozeti** | `k_radar_kpr_risk.risk_ozeti` | Açık risk sayısı, ortalama RPN ve yüksek risk sayısını gösteren özet kart. |


### 🎴 K-Radar Balanced Scorecard Bileşeni Kartları (`k_radar_ks_bsc`)
**Bileşen:** K-Radar Balanced Scorecard | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KD10` | **k_radar_ks.bsc** | `k_radar_ks.bsc` | Balanced Scorecard 4 perspektifini (Finansal/Müşteri/İç Süreç/Öğrenme) özetleyen kart. Tıklayınca detay modalı açılır. |


### 🎴 K-Radar EFQM Olgunluk Modeli Bileşeni Kartları (`k_radar_ks_efqm`)
**Bileşen:** K-Radar EFQM Olgunluk Modeli | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KD11` | **k_radar_ks.efqm** | `k_radar_ks.efqm` | EFQM 2025 mükemmellik modeli kriter kapsamı ve hazırlık skorunu gösteren olgunluk kartı. Tıklayınca detay modalı açılır. |


### 🎴 K-Radar Hedef Gap Analizi Bileşeni Kartları (`k_radar_ks_gap_analizi`)
**Bileşen:** K-Radar Hedef Gap Analizi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KD08` | **k_radar_ks.gap_analizi** | `k_radar_ks.gap_analizi` | PG hedef-gerçekleşme açıklarını Hedefte/Riskli/Kritik olarak özetleyen analiz kartı. Tıklayınca detay modalı açılır. |


### 🎴 K-Radar Kurumsal Strateji Skoru Bileşeni Kartları (`k_radar_ks_skoru`)
**Bileşen:** K-Radar Kurumsal Strateji Skoru | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KD03` | **k_radar_ks.genel_pg_basarisi** | `k_radar_ks.genel_pg_basarisi` | Tüm performans göstergelerinin genel başarı ortalamasını gösteren mini istatistik kartı. |
| `KD04` | **k_radar_ks.ks_skoru** | `k_radar_ks.ks_skoru` | Kurumsal Strateji (KS) bütüncül skorunu ve performans bandını gösteren mini istatistik kartı. |
| `KD01` | **k_radar_ks.strateji_kapsami** | `k_radar_ks.strateji_kapsami` | Stratejilerin süreçlerle ne ölçüde kapsandığını yüzde olarak gösteren mini istatistik kartı. |
| `KD02` | **k_radar_ks.toplam_strateji** | `k_radar_ks.toplam_strateji` | Toplam ana strateji ve alt strateji sayısını gösteren mini istatistik kartı. |


### 🎴 K-Radar OKR Takibi Bileşeni Kartları (`k_radar_ks_okr`)
**Bileşen:** K-Radar OKR Takibi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KD09` | **k_radar_ks.okr** | `k_radar_ks.okr` | Hedefler ve Anahtar Sonuçlar (OKR) hiyerarşisini, çeyrek bazlı ilerleme takibini gösteren kart. Tıklayınca detay modalı açılır. |


### 🎴 K-Radar Strateji-Süreç Kapsama Bileşeni Kartları (`k_radar_ks_strateji_surec_kapsama`)
**Bileşen:** K-Radar Strateji-Süreç Kapsama | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KD12` | **k_radar_ks.strateji_surec_kapsama_ozeti** | `k_radar_ks.strateji_surec_kapsama_ozeti` | Her ana/alt stratejinin hangi süreçlerle kapsandığını sıralı liste halinde gösteren ana kart. |


### 🎴 K-Radar Risk Yönetimi Bileşeni Kartları (`k_radar_risk_yonetimi`)
**Bileşen:** K-Radar Risk Yönetimi | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KDR01` | **k_radar_risk_management.risk_matrisi** | `k_radar_risk_management.risk_matrisi` | Olasılık ve etkiye göre 5x5 risk sayısını renk kodlu ısı haritası olarak gösteren matris. |
| `KDR02` | **k_radar_risk_management.risk_listesi** | `k_radar_risk_management.risk_listesi` | Şiddet ve duruma göre filtrelenebilen, RPN ve önem seviyesiyle listelenen risk kayıtları tablosu. |


### 🎴 K-Rapor Aktivite Takvimi Bileşeni Kartları (`k_rapor_aktivite_takvim`)
**Bileşen:** K-Rapor Aktivite Takvimi | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR72` | **Toplam Giriş** | `k_rapor_aktivite_takvim.toplam_giris` | Toplam Giriş — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR09` | **k_rapor_aktivite_takvim.son_30_gun_trend** | `k_rapor_aktivite_takvim.son_30_gun_trend` | Son 30 Gün Trend — k-rapor analiz kartı. |
| `KR08` | **k_rapor_aktivite_takvim.gunluk_veri_giris_aktivitesi** | `k_rapor_aktivite_takvim.gunluk_veri_giris_aktivitesi` | Günlük Veri Giriş Aktivitesi — k-rapor analiz kartı. |
| `KR73` | **Aktif Gün** | `k_rapor_aktivite_takvim.aktif_gun` | Aktif Gün — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR74` | **Günlük Ort.** | `k_rapor_aktivite_takvim.gunluk_ort` | Günlük Ort. — k-rapor özet istatistik kartı (canlı veriyle dolar). |


### 🎴 K-Rapor Anomali Tespiti Bileşeni Kartları (`k_rapor_anomali_tespiti`)
**Bileşen:** K-Rapor Anomali Tespiti | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KRAN03` | **k_rapor_anomalies.anomali_listesi** | `k_rapor_anomalies.anomali_listesi` | Tespit edilen her bir KPI anomalisinin detaylarını (son değer, ortalama, z-score, yön) kart kart listeleyen alan. |
| `KRAN02` | **k_rapor_anomalies.ozet** | `k_rapor_anomalies.ozet` | Bulunan anomalilerin önem derecesine göre (yüksek/orta/düşük) sayısal özetini gösteren kart. |
| `KRAN01` | **k_rapor_anomalies.tarama_filtreleri** | `k_rapor_anomalies.tarama_filtreleri` | Z-score eşiği, Slack webhook ve önem eşiği gibi anomali tarama parametrelerinin ayarlandığı filtre paneli. |


### 🎴 K-Rapor Bildirim Analizi Bileşeni Kartları (`k_rapor_bildirim_analiz`)
**Bileşen:** K-Rapor Bildirim Analizi | **Kart Sayısı:** 8

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR80` | **Okunmayan** | `k_rapor_bildirim_analiz.okunmayan` | Okunmayan — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR10` | **k_rapor_bildirim_analiz.bildirim_turu_dagilimi** | `k_rapor_bildirim_analiz.bildirim_turu_dagilimi` | Bildirim Türü Dağılımı — k-rapor analiz kartı. |
| `KR11` | **k_rapor_bildirim_analiz.en_cok_bildirim_alan_kullanicilar** | `k_rapor_bildirim_analiz.en_cok_bildirim_alan_kullanicilar` | En Çok Bildirim Alan Kullanıcılar — k-rapor analiz kartı. |
| `KR79` | **Okunan** | `k_rapor_bildirim_analiz.okunan` | Okunan — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR78` | **Toplam Bildirim** | `k_rapor_bildirim_analiz.toplam_bildirim` | Toplam Bildirim — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR13` | **k_rapor_bildirim_analiz.son_30_gun_bildirim_trendi** | `k_rapor_bildirim_analiz.son_30_gun_bildirim_trendi` | Son 30 Gün Bildirim Trendi — k-rapor analiz kartı. |
| `KR12` | **k_rapor_bildirim_analiz.okunmayan_bildirimlerin_yaslanmasi** | `k_rapor_bildirim_analiz.okunmayan_bildirimlerin_yaslanmasi` | Okunmayan Bildirimlerin Yaşlanması — k-rapor analiz kartı. |
| `KR81` | **Son 7 Gün** | `k_rapor_bildirim_analiz.son_7_gun` | Son 7 Gün — k-rapor özet istatistik kartı (canlı veriyle dolar). |


### 🎴 K-Rapor Bireysel PG Analizi Bileşeni Kartları (`k_rapor_bireysel_pg`)
**Bileşen:** K-Rapor Bireysel PG Analizi | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR15` | **k_rapor_bireysel.kullanici_bazli_pg_basari_tablosu** | `k_rapor_bireysel.kullanici_bazli_pg_basari_tablosu` | Kullanıcı Bazlı PG Başarı Tablosu — k-rapor analiz kartı. |
| `KR14` | **k_rapor_bireysel.bireysel_pg_detay_listesi** | `k_rapor_bireysel.bireysel_pg_detay_listesi` | Bireysel PG Detay Listesi — k-rapor analiz kartı. |


### 🎴 K-Rapor Denetim Analizi Bileşeni Kartları (`k_rapor_denetim`)
**Bileşen:** K-Rapor Denetim Analizi | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR18` | **k_rapor_denetim.son_islemler** | `k_rapor_denetim.son_islemler` | Son İşlemler — k-rapor analiz kartı. |
| `KR17` | **k_rapor_denetim.islem_dagilimi** | `k_rapor_denetim.islem_dagilimi` | İşlem Dağılımı — k-rapor analiz kartı. |
| `KR16` | **k_rapor_denetim.en_aktif_kullanicilar** | `k_rapor_denetim.en_aktif_kullanicilar` | En Aktif Kullanıcılar — k-rapor analiz kartı. |


### 🎴 K-Rapor Kazanılmış Değer Analizi Bileşeni Kartları (`k_rapor_evm`)
**Bileşen:** K-Rapor Kazanılmış Değer Analizi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR19` | **k_rapor_evm.kazanilmis_deger_evm_proje_snapshot_tablosu** | `k_rapor_evm.kazanilmis_deger_evm_proje_snapshot_tablosu` | Kazanılmış Değer (EVM) — Proje Snapshot Tablosu — k-rapor analiz kartı. |


### 🎴 K-Rapor Faaliyet Analizi Bileşeni Kartları (`k_rapor_faaliyet`)
**Bileşen:** K-Rapor Faaliyet Analizi | **Kart Sayısı:** 7

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR61` | **Toplam** | `k_rapor_faaliyet.toplam` | Toplam — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR22` | **k_rapor_faaliyet.proje_portfoy_durumu** | `k_rapor_faaliyet.proje_portfoy_durumu` | Proje Portföy Durumu — k-rapor analiz kartı. |
| `KR21` | **k_rapor_faaliyet.geciken_faaliyetler** | `k_rapor_faaliyet.geciken_faaliyetler` | Geciken Faaliyetler — k-rapor analiz kartı. |
| `KR20` | **k_rapor_faaliyet.aylik_tamamlanan** | `k_rapor_faaliyet.aylik_tamamlanan` | Aylık Tamamlanan — k-rapor analiz kartı. |
| `KR60` | **Geciken** | `k_rapor_faaliyet.geciken` | Geciken — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR59` | **Devam Ediyor** | `k_rapor_faaliyet.devam_ediyor` | Devam Ediyor — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR58` | **Tamamlanan** | `k_rapor_faaliyet.tamamlanan` | Tamamlanan — k-rapor özet istatistik kartı (canlı veriyle dolar). |


### 🎴 K-Rapor K-Vektör Ağırlıkları Bileşeni Kartları (`k_rapor_k_vektor`)
**Bileşen:** K-Rapor K-Vektör Ağırlıkları | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR25` | **k_rapor_k_vektor.ana_strateji_agirliklari** | `k_rapor_k_vektor.ana_strateji_agirliklari` | Ana Strateji Ağırlıkları — k-rapor analiz kartı. |
| `KR24` | **k_rapor_k_vektor.alt_strateji_agirliklari** | `k_rapor_k_vektor.alt_strateji_agirliklari` | Alt Strateji Ağırlıkları — k-rapor analiz kartı. |
| `KR23` | **k_rapor_k_vektor.agirlik_tablosu** | `k_rapor_k_vektor.agirlik_tablosu` | Ağırlık Tablosu — k-rapor analiz kartı. |


### 🎴 K-Rapor Kurum Karşılaştırma Bileşeni Kartları (`k_rapor_kurum_karsilastirma`)
**Bileşen:** K-Rapor Kurum Karşılaştırma | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR26` | **k_rapor_kurum_karsilastirma.kurum_detay_tablosu** | `k_rapor_kurum_karsilastirma.kurum_detay_tablosu` | Kurum Detay Tablosu — k-rapor analiz kartı. |
| `KR27` | **k_rapor_kurum_karsilastirma.kurum_performans_karsilastirmasi** | `k_rapor_kurum_karsilastirma.kurum_performans_karsilastirmasi` | Kurum Performans Karşılaştırması — k-rapor analiz kartı. |


### 🎴 K-Rapor Kurumsal Özet Bileşeni Kartları (`k_rapor_kurumsal_ozet`)
**Bileşen:** K-Rapor Kurumsal Özet | **Kart Sayısı:** 7

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR06` | **k_rapor_kurumsal.en_iyi_5_surec** | `k_rapor_kurumsal.en_iyi_5_surec` | En yüksek performanslı ilk 5 süreci sıralı liste halinde gösteren kart. |
| `KR03` | **Hedefte** | `k_rapor_kurumsal.hedefte` | Başarısı ≥%80 olan (hedefte) PG sayısını ve oranını gösteren mini istatistik kartı. |
| `KR05` | **Kritik** | `k_rapor_kurumsal.kritik` | Başarısı <%50 olan (kritik) PG sayısını ve oranını gösteren mini istatistik kartı. |
| `KR02` | **k_rapor_kurumsal.strateji_bazli_basari** | `k_rapor_kurumsal.strateji_bazli_basari` | Her ana strateji için ağırlıklı ortalama başarıyı yatay çubuklarla gösteren kart. |
| `KR04` | **Riskli** | `k_rapor_kurumsal.riskli` | Başarısı %50-79 arası (riskli) PG sayısını ve oranını gösteren mini istatistik kartı. |
| `KR01` | **k_rapor_kurumsal.vizyon_skoru** | `k_rapor_kurumsal.vizyon_skoru` | Kurumun vizyon başarı skorunu büyük gösterge (gauge) olarak gösteren kart. |
| `KR07` | **k_rapor_kurumsal.en_dusuk_5_surec** | `k_rapor_kurumsal.en_dusuk_5_surec` | En düşük performanslı 5 süreci sıralı liste halinde gösteren kart. |


### 🎴 K-Rapor Paydaş Analizi Bileşeni Kartları (`k_rapor_paydas`)
**Bileşen:** K-Rapor Paydaş Analizi | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR28` | **k_rapor_paydas.paydas_anket_ozeti** | `k_rapor_paydas.paydas_anket_ozeti` | Paydaş Anket Özeti — k-rapor analiz kartı. |
| `KR29` | **k_rapor_paydas.paydas_haritasi** | `k_rapor_paydas.paydas_haritasi` | Paydaş Haritası — k-rapor analiz kartı. |


### 🎴 K-Rapor PG Dağılım Analizi Bileşeni Kartları (`k_rapor_pg_dagilim`)
**Bileşen:** K-Rapor PG Dağılım Analizi | **Kart Sayısı:** 7

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR30` | **k_rapor_pg_dagilim.basari_yuzdesi_dagilimi_histogram** | `k_rapor_pg_dagilim.basari_yuzdesi_dagilimi_histogram` | Başarı Yüzdesi Dağılımı (Histogram) — k-rapor analiz kartı. |
| `KR32` | **k_rapor_pg_dagilim.pg_dagilim_grafigi** | `k_rapor_pg_dagilim.pg_dagilim_grafigi` | PG Dağılım Grafiği — k-rapor analiz kartı. |
| `KR31` | **k_rapor_pg_dagilim.en_dusuk_performansli_pg_ler** | `k_rapor_pg_dagilim.en_dusuk_performansli_pg_ler` | En Düşük Performanslı PG'ler — k-rapor analiz kartı. |
| `KR68` | **Toplam PG** | `k_rapor_pg_dagilim.toplam_pg` | Toplam PG — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR69` | **Ort. Başarı** | `k_rapor_pg_dagilim.ort_basari` | Ort. Başarı — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR70` | **Hedefte (≥%80)** | `k_rapor_pg_dagilim.hedefte_80` | Hedefte (≥%80) — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR71` | **Kritik (<%50)** | `k_rapor_pg_dagilim.kritik_50` | Kritik (<%50) — k-rapor özet istatistik kartı (canlı veriyle dolar). |


### 🎴 K-Rapor Rekabet ve A3 Analizi Bileşeni Kartları (`k_rapor_rekabet`)
**Bileşen:** K-Rapor Rekabet ve A3 Analizi | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR33` | **k_rapor_rekabet.a3_raporlari** | `k_rapor_rekabet.a3_raporlari` | A3 Raporları — k-rapor analiz kartı. |
| `KR34` | **k_rapor_rekabet.rekabetci_analiz** | `k_rapor_rekabet.rekabetci_analiz` | Rekabetçi Analiz — k-rapor analiz kartı. |


### 🎴 K-Rapor Risk ve Süreç Analizi Bileşeni Kartları (`k_rapor_risk`)
**Bileşen:** K-Rapor Risk ve Süreç Analizi | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR35` | **k_rapor_risk.darbogaz_gecmisi** | `k_rapor_risk.darbogaz_gecmisi` | Darboğaz Geçmişi — k-rapor analiz kartı. |
| `KR36` | **k_rapor_risk.risk_tablosu_rpn_sirali** | `k_rapor_risk.risk_tablosu_rpn_sirali` | Risk Tablosu (RPN Sıralı) — k-rapor analiz kartı. |
| `KR37` | **k_rapor_risk.surec_olgunluk_seviyeleri** | `k_rapor_risk.surec_olgunluk_seviyeleri` | Süreç Olgunluk Seviyeleri — k-rapor analiz kartı. |


### 🎴 K-Rapor Sorumlu Analizi Bileşeni Kartları (`k_rapor_sorumlu_analiz`)
**Bileşen:** K-Rapor Sorumlu Analizi | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR38` | **k_rapor_sorumlu_analiz.en_cok_geciken_kisiler** | `k_rapor_sorumlu_analiz.en_cok_geciken_kisiler` | En Çok Geciken Kişiler — k-rapor analiz kartı. |
| `KR39` | **k_rapor_sorumlu_analiz.kisi_basina_faaliyet_yuku** | `k_rapor_sorumlu_analiz.kisi_basina_faaliyet_yuku` | Kişi Başına Faaliyet Yükü — k-rapor analiz kartı. |
| `KR40` | **k_rapor_sorumlu_analiz.sorumlu_detay_tablosu** | `k_rapor_sorumlu_analiz.sorumlu_detay_tablosu` | Sorumlu Detay Tablosu — k-rapor analiz kartı. |


### 🎴 K-Rapor Strateji Kapsama Analizi Bileşeni Kartları (`k_rapor_strateji_kapsama`)
**Bileşen:** K-Rapor Strateji Kapsama Analizi | **Kart Sayısı:** 6

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR77` | **Boş Strateji** | `k_rapor_strateji_kapsama.bos_strateji` | Boş Strateji — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR42` | **k_rapor_strateji_kapsama.strateji_kapsama_durumu** | `k_rapor_strateji_kapsama.strateji_kapsama_durumu` | Strateji Kapsama Durumu — k-rapor analiz kartı. |
| `KR43` | **k_rapor_strateji_kapsama.stratejisiz_surecler** | `k_rapor_strateji_kapsama.stratejisiz_surecler` | Stratejisiz Süreçler — k-rapor analiz kartı. |
| `KR41` | **k_rapor_strateji_kapsama.strateji_bazli_kapsama_tablosu** | `k_rapor_strateji_kapsama.strateji_bazli_kapsama_tablosu` | Strateji Bazlı Kapsama Tablosu — k-rapor analiz kartı. |
| `KR75` | **Tam Kapsamlı** | `k_rapor_strateji_kapsama.tam_kapsamli` | Tam Kapsamlı — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR76` | **Kısmi** | `k_rapor_strateji_kapsama.kismi` | Kısmi — k-rapor özet istatistik kartı (canlı veriyle dolar). |


### 🎴 K-Rapor Süreç-PG Analizi Bileşeni Kartları (`k_rapor_surec_pg`)
**Bileşen:** K-Rapor Süreç-PG Analizi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR48` | **k_rapor_surec_pg.surec_donem_isi_haritasi** | `k_rapor_surec_pg.surec_donem_isi_haritasi` | Süreç × Dönem Isı Haritası — k-rapor analiz kartı. |


### 🎴 K-Rapor SWOT/TOWS Trend Analizi Bileşeni Kartları (`k_rapor_swot_trend`)
**Bileşen:** K-Rapor SWOT/TOWS Trend Analizi | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR49` | **k_rapor_swot_trend.swot_madde_sayisi_trendi** | `k_rapor_swot_trend.swot_madde_sayisi_trendi` | SWOT Madde Sayısı Trendi — k-rapor analiz kartı. |
| `KR50` | **k_rapor_swot_trend.tows_strateji_sayisi_trendi** | `k_rapor_swot_trend.tows_strateji_sayisi_trendi` | TOWS Strateji Sayısı Trendi — k-rapor analiz kartı. |
| `KR51` | **k_rapor_swot_trend.yillik_swot_tows_ozet_tablosu** | `k_rapor_swot_trend.yillik_swot_tows_ozet_tablosu` | Yıllık SWOT/TOWS Özet Tablosu — k-rapor analiz kartı. |


### 🎴 K-Rapor Uyarı Paneli Bileşeni Kartları (`k_rapor_uyari`)
**Bileşen:** K-Rapor Uyarı Paneli | **Kart Sayısı:** 6

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR67` | **Yüksek Risk** | `k_rapor_uyari.yuksek_risk` | Yüksek Risk — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR65` | **Kritik PG** | `k_rapor_uyari.kritik_pg` | Kritik PG — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR66` | **Geciken Faaliyet** | `k_rapor_uyari.geciken_faaliyet` | Geciken Faaliyet — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR54` | **k_rapor_uyari.yuksek_riskler** | `k_rapor_uyari.yuksek_riskler` | Yüksek Riskler — k-rapor analiz kartı. |
| `KR53` | **k_rapor_uyari.kritik_performans_gostergeleri** | `k_rapor_uyari.kritik_performans_gostergeleri` | Kritik Performans Göstergeleri — k-rapor analiz kartı. |
| `KR52` | **k_rapor_uyari.geciken_faaliyetler** | `k_rapor_uyari.geciken_faaliyetler` | Geciken Faaliyetler — k-rapor analiz kartı. |


### 🎴 K-Rapor Strateji-Süreç Uyum Ağacı Bileşeni Kartları (`k_rapor_uyum`)
**Bileşen:** K-Rapor Strateji-Süreç Uyum Ağacı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR55` | **k_rapor_uyum.strateji_surec_katki_agaci** | `k_rapor_uyum.strateji_surec_katki_agaci` | Strateji → Süreç Katkı Ağacı — k-rapor analiz kartı. |


### 🎴 K-Rapor Veri Durumu Bileşeni Kartları (`k_rapor_veri_durumu`)
**Bileşen:** K-Rapor Veri Durumu | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KR57` | **k_rapor_veri_durumu.veri_girilmeyen_pg_ler** | `k_rapor_veri_durumu.veri_girilmeyen_pg_ler` | Veri Girilmeyen PG'ler — k-rapor analiz kartı. |
| `KR62` | **Toplam PG** | `k_rapor_veri_durumu.toplam_pg` | Toplam PG — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR63` | **Veri Girilmiş** | `k_rapor_veri_durumu.veri_girilmis` | Veri Girilmiş — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR64` | **Eksik** | `k_rapor_veri_durumu.eksik` | Eksik — k-rapor özet istatistik kartı (canlı veriyle dolar). |
| `KR56` | **k_rapor_veri_durumu.veri_girilen_pg_ler** | `k_rapor_veri_durumu.veri_girilen_pg_ler` | Veri Girilen PG'ler — k-rapor analiz kartı. |


### 🎴 Benim Görevlerim Kartı Bileşeni Kartları (`benim_gorevlerim_karti`)
**Bileşen:** Benim Görevlerim Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA04` | **masaustu.benim_gorevlerim** | `masaustu.benim_gorevlerim` | Kullanıcıya atanmış tüm görevleri (proje görevi, bireysel faaliyet, süreç faaliyeti) tek listede toplayan kart. Tümü/Gecikmiş/Bugün/Bu hafta filtreleri ve toplam-gecikmiş-bugün-bu hafta özet sayaçları içerir. Veriyi /api/my-tasks uç noktasından canlı çeker. |


### 🎴 Benim Masam Kartı Bileşeni Kartları (`benim_masam_karti`)
**Bileşen:** Benim Masam Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA08` | **masaustu.benim_masam** | `masaustu.benim_masam` | Kullanıcının kişisel faaliyetlerini Bugün / 7 gün / Geciken sekmelerinde gösteren çalışma masası kartı. Bitiş tarihi ve ilerleme yüzdesiyle birlikte listeler. Karneye kısayol içerir. |


### 🎴 Bildirimler Kartı Bileşeni Kartları (`bildirimler_karti`)
**Bileşen:** Bildirimler Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA12` | **masaustu.bildirimler** | `masaustu.bildirimler` | Kullanıcının okunmamış bildirimlerini başlık, mesaj özeti ve tarihle listeler. Her satırda 'Okundu' işaretleme butonu vardır. Tüm bildirimlere kısayol içerir. |


### 🎴 Mini İstatistik Şeridi Bileşeni Kartları (`mini_istatistik_seridi`)
**Bileşen:** Mini İstatistik Şeridi | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA16` | **masaustu.devam_eden_faaliyet** | `masaustu.devam_eden_faaliyet` | Kullanıcının üzerindeki aktif/devam eden faaliyet sayısını gösteren mini istatistik kartı. |
| `MA18` | **masaustu.okunmamis_bildirim** | `masaustu.okunmamis_bildirim` | Kullanıcının bekleyen (okunmamış) bildirim sayısını gösteren mini istatistik kartı. |
| `MA15` | **masaustu.bireysel_pg** | `masaustu.bireysel_pg` | Kullanıcının sahip olduğu aktif bireysel performans göstergesi (PG) sayısını gösteren mini istatistik kartı. İstatistik şeridinin parçasıdır. |
| `MA17` | **masaustu.surec_pg** | `masaustu.surec_pg` | Kullanıcının üye veya lider olduğu süreçlerdeki toplam aktif performans göstergesi sayısını gösteren mini istatistik kartı. |
| `MA14` | **masaustu.mini_kartlar** | `masaustu.mini_kartlar` | Masaüstünün üst kısmındaki 4'lü istatistik şeridinin kapsayıcısı. İçinde Bireysel PG, Devam Eden Faaliyet, Süreç PG ve Okunmamış Bildirim mini kartları yer alır. Kullanıcının kişisel rakamlarını tek satırda özetler. |


### 🎴 Bugünün Özeti Kartı Bileşeni Kartları (`bugunun_ozeti_karti`)
**Bileşen:** Bugünün Özeti Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA03` | **masaustu.bugunun_ozeti** | `masaustu.bugunun_ozeti` | Kullanıcının bugün dikkat etmesi gereken 4 hızlı eylem sayacını gösterir: okunmamış bildirim, bu ay eksik PG verisi, geciken faaliyet ve önümüzdeki 7 günde biten işler. Her biri ilgili sayfaya kısayoldur. Acil bir şey yoksa olumlu bir mesaj gösterir. |


### 🎴 Dikkat: Dönem Verisi Kartı Bileşeni Kartları (`dikkat_donem_verisi_karti`)
**Bileşen:** Dikkat: Dönem Verisi Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA09` | **masaustu.dikkat_donem_verisi** | `masaustu.dikkat_donem_verisi` | Kullanıcının içinde bulunulan ay/dönem için henüz veri girmediği bireysel performans göstergelerini uyarı olarak listeler. Eksik PG'ler varsa karnede veri girme kısayolu sunar; yoksa olumlu mesaj gösterir. Kart başlığındaki ay dinamiktir. |


### 🎴 Favori PG'lerim Kartı Bileşeni Kartları (`favori_pglerim_karti`)
**Bileşen:** Favori PG'lerim Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA19` | **masaustu.favori_pglerim** | `masaustu.favori_pglerim` | Kullanıcının süreç karnelerinden yıldızladığı (favori) performans göstergelerini son ölçüm değerleri ve başarı yüzdeleriyle tek listede toplayan kart. Her satır ilgili sürecin karnesine kısayoldur. Yalnızca en az bir favori PG varsa görünür. Favoriler kişiye özeldir. |


### 🎴 Favori ve Son Ziyaretlerim Kartı Bileşeni Kartları (`favori_ve_son_ziyaretlerim_karti`)
**Bileşen:** Favori ve Son Ziyaretlerim Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA05` | **masaustu.favori_ve_son_ziyaretlerim** | `masaustu.favori_ve_son_ziyaretlerim` | Kullanıcının sabitlediği (pinlediği) sayfalar ile son gezdiği sayfaların kısayollarını gösterir. Sık kullanılan sayfalara hızlı erişim sağlar. Veri yalnızca tarayıcıda (localStorage) tutulur, sunucuya yazılmaz. |


### 🎴 Karalama Defteri Kartı Bileşeni Kartları (`karalama_defteri_karti`)
**Bileşen:** Karalama Defteri Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA10` | **masaustu.karalama_defteri** | `masaustu.karalama_defteri` | Kullanıcının hızlı not alabileceği serbest metin alanı. Notlar yalnızca bu tarayıcıda (localStorage) tutulur, sunucuya gönderilmez ve başka cihazda görünmez. |


### 🎴 Kurumsal Olgunluk Endeksi Kartı Bileşeni Kartları (`kurumsal_olgunluk_endeksi_karti`)
**Bileşen:** Kurumsal Olgunluk Endeksi Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA02` | **masaustu.kurumsal_olgunluk_endeksi** | `masaustu.kurumsal_olgunluk_endeksi` | Kurumun yapısal olgunluğunu 0-100 arası tek skorla ve 4 boyutta (Kimlik & Strateji Netliği, Süreç Mimarisi, Olgunluk, İcra Disiplini) gösterir. Performans verisi (PGV) girilmeden, mevcut yapıdan hesaplanır — yani veri girişi olmadan da kurumun ne kadar 'kurulu' olduğunu ölçer. İsteğe bağlı AI danışman önerileri içerir. L1 paketinden itibaren yönetime sunulur. |


### 🎴 Özet Listeler Kartı Bileşeni Kartları (`ozet_listeler_karti`)
**Bileşen:** Özet Listeler Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA11` | **masaustu.ozet_listeler** | `masaustu.ozet_listeler` | İki kolonda kullanıcının Bireysel PG'lerini (durum rozetiyle) ve Devam Eden Faaliyetlerini (ilerleme çubuğuyla) özetleyen kart. Her kolon ilgili karne sayfasına 'Tümünü Gör' kısayolu içerir. |


### 🎴 Süreç PG'lerim Kartı Bileşeni Kartları (`surec_pglerim_karti`)
**Bileşen:** Süreç PG'lerim Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA20` | **masaustu.surec_pglerim** | `masaustu.surec_pglerim` | Üye/lider olduğunuz süreçlerin son güncellenen göstergeleri. |


### 🎴 Takvimim Kartı Bileşeni Kartları (`takvimim_karti`)
**Bileşen:** Takvimim Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA07` | **masaustu.takvimim** | `masaustu.takvimim` | Kullanıcının süreç faaliyetleri, proje görevleri ve kişisel görevlerini renk kodlu bir takvimde gösterir. Boş güne tıklayarak veya aralık seçerek hızlı görev/faaliyet ekleme yapılabilir (Kurum Takvimi ile aynı hızlı ekleme akışı). |


### 🎴 Yönetici Sabah Özeti Kartı Bileşeni Kartları (`yonetici_sabah_ozeti_karti`)
**Bileşen:** Yönetici Sabah Özeti Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `MA01` | **masaustu.yonetici_sabah_ozeti** | `masaustu.yonetici_sabah_ozeti` | Yönetici ve üst yönetime özel günlük durum kartı. Sabah girişinde o güne dair en kritik başlıkları (geciken işler, dikkat isteyen göstergeler, gündem) tek bakışta özetler. Yalnızca tenant_admin / executive_manager / Admin rollerine gösterilir. Veriyi /api/morning-summary uç noktasından çeker. |


### 🎴 Süreç Özet İstatistikleri Bileşeni Kartları (`surec_ozet_istatistikleri`)
**Bileşen:** Süreç Özet İstatistikleri | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PR01` | **process.toplam_surec** | `process.toplam_surec` | Kurumda tanımlı toplam süreç sayısını ve bunların kaç tanesinin kök (en üst) süreç olduğunu gösteren mini istatistik kartı. |
| `PR02` | **process.toplam_pg** | `process.toplam_pg` | Tüm süreçlerdeki toplam performans göstergesi (PG) sayısını ve henüz hiç PG tanımlanmamış süreç sayısını gösterir. |
| `PR04` | **process.yuksek_performans** | `process.yuksek_performans` | Performans skoru %80 ve üzerinde olan, yüksek performanslı süreçlerin sayısını gösterir. |
| `PR05` | **process.kritik_surec** | `process.kritik_surec` | Performans skoru %50 altında olan, dikkat/müdahale gerektiren kritik süreçlerin sayısını gösterir. |
| `PR06` | **process.k_vektor** | `process.k_vektor` | K-Vektör ağırlıklı skorlama sisteminin bu kurumda aktif olup olmadığını gösterir. Aktifse süreç skorları stratejik ağırlıklarla hesaplanır. |


### 🎴 Süreç Karnesi Genel Bilgiler Bileşeni Kartları (`surec_karnesi_genel_bilgiler`)
**Bileşen:** Süreç Karnesi Genel Bilgiler | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PK02` | **process_karne.genel_bilgiler** | `process_karne.genel_bilgiler` | Sürecin genel sağlık skoru, PG başarı dağılımı (donut grafik) ve faaliyet/PG veri doluluk ilerlemesini özetleyen kart. Başlık seçili sürecin adını taşır. |


### 🎴 Proje Özet İstatistikleri Bileşeni Kartları (`proje_ozet_istatistikleri`)
**Bileşen:** Proje Özet İstatistikleri | **Kart Sayısı:** 6

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PJ01` | **project.toplam_proje** | `project.toplam_proje` | Kurumdaki toplam proje sayısını ve projelerin ortalama sağlık skorunu gösteren mini istatistik kartı. |
| `PJ06` | **project.kritik_saglik** | `project.kritik_saglik` | Sağlık skoru 50 altında olan, kritik durumdaki proje sayısını gösteren mini istatistik kartı. |
| `PJ05` | **project.acik_raid** | `project.acik_raid` | Açık RAID kayıtlarını (Risk, Varsayım, Sorun, Bağımlılık) tür dağılımıyla mini donut grafikte gösteren kart. |
| `PJ04` | **project.bu_hafta_biten** | `project.bu_hafta_biten` | Önümüzdeki 7 gün içinde bitecek görev ve proje sayısını gösteren mini istatistik kartı. |
| `PJ03` | **project.gecikmis_gorev** | `project.gecikmis_gorev` | Bitiş tarihi geçmiş, acil eylem gerektiren gecikmiş görev sayısını gösteren mini istatistik kartı. |
| `PJ02` | **project.acik_gorev** | `project.acik_gorev` | Tüm projelerdeki açık (tamamlanmamış) görev sayısını ve toplam görev sayısını gösteren mini istatistik kartı. |


### 🎴 Proje Operasyon Özeti Bileşeni Kartları (`proje_operasyon_ozeti`)
**Bileşen:** Proje Operasyon Özeti | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PJ08` | **project.operasyon_ozeti** | `project.operasyon_ozeti` | Proje portföyünün operasyonel özetini (RAID dağılımı, görev durumları, grafikler) toplu gösteren kart. |


### 🎴 Proje Listesi Yönetimi Bileşeni Kartları (`proje_listesi_yonetimi`)
**Bileşen:** Proje Listesi Yönetimi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PJ07` | **project.proje_listesi** | `project.proje_listesi` | Kurumun tüm projelerini kaydırılabilir liste halinde gösteren ana kart. Her proje sağlık, ilerleme ve durum bilgisiyle listelenir. |


### 🎴 Proje Takvim Görünümü Bileşeni Kartları (`proje_takvim_gorunumu`)
**Bileşen:** Proje Takvim Görünümü | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PJC01` | **project_calendar.takvim** | `project_calendar.takvim` | Projeye ait görevleri aylık/haftalık/günlük takvim görünümünde listeler; görevlere tıklayarak detaya gidilebilir, sürükleyerek tarihleri değiştirilebilir. |


### 🎴 Proje Detay Özeti Bileşeni Kartları (`proje_detay_ozeti`)
**Bileşen:** Proje Detay Özeti | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PJD03` | **project_detail.gorev_ozeti** | `project_detail.gorev_ozeti` | Projenin görevlerini durumlarına göre sütunlar halinde özetleyen mini kanban kartı. |
| `PJD02` | **project_detail.proje_ozeti** | `project_detail.proje_ozeti` | Projenin yöneticisi, önceliği, bağlı stratejik girişimi, açıklaması ve ekip/gözlemci listesini gösteren özet kartı. |
| `PJD01` | **project_detail.geciken_gorev_uyarisi** | `project_detail.geciken_gorev_uyarisi` | Projede gecikmiş görev sayısını vurgulayan uyarı kartı. |


### 🎴 Proje Formu Bileşeni Kartları (`proje_formu`)
**Bileşen:** Proje Formu | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PJF01` | **project_form.sayfa** | `project_form.sayfa` | Proje bilgilerini, liderlerini, üyelerini, gözlemcilerini ve bildirim ayarlarını içeren tek parça proje formu. |


### 🎴 Proje Gantt Şeması Bileşeni Kartları (`proje_gantt_semasi`)
**Bileşen:** Proje Gantt Şeması | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PJG01` | **project_gantt.gantt_semasi** | `project_gantt.gantt_semasi` | Proje görevlerinin başlangıç/bitiş tarihlerini ve ilerlemesini gösteren, kritik yoldaki görevleri vurgulayan Gantt zaman çizelgesi. |


### 🎴 Proje Kanban Panosu Bileşeni Kartları (`proje_kanban_panosu`)
**Bileşen:** Proje Kanban Panosu | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PJK01` | **project_kanban.yapilacak** | `project_kanban.yapilacak` | Henüz başlanmamış görevlerin listelendiği Kanban sütunu. |
| `PJK02` | **project_kanban.devam_beklemede** | `project_kanban.devam_beklemede` | Üzerinde çalışılan veya beklemede olan görevlerin listelendiği Kanban sütunu. |
| `PJK03` | **project_kanban.tamamlandi** | `project_kanban.tamamlandi` | Tamamlanmış görevlerin listelendiği Kanban sütunu. |


### 🎴 Proje Kapasite Yönetimi Bileşeni Kartları (`proje_kapasite_yonetimi`)
**Bileşen:** Proje Kapasite Yönetimi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PJA01` | **project_kapasite.sayfa** | `project_kapasite.sayfa` | Ekip üyelerine ait haftalık kapasite kayıtlarını (kişi, saat, başlangıç/bitiş dönemi) listeleyen ve yeni kapasite eklemeyi sağlayan tablo. |


### 🎴 Proje Portföy Yönetimi Bileşeni Kartları (`proje_portfoy_yonetimi`)
**Bileşen:** Proje Portföy Yönetimi | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PJP02` | **project_portfolio.portfoy_listesi** | `project_portfolio.portfoy_listesi` | Projelerin stratejik skoruna göre sıralandığı, bağlı süreçleri ve işlem bağlantılarını gösteren portföy listesi tablosu. |
| `PJP01` | **project_portfolio.program_gantt** | `project_portfolio.program_gantt` | Başlangıç/bitiş tarihi tanımlı tüm projelerin tek bir Gantt çizelgesinde gösterildiği program zaman çizelgesi kartı. |


### 🎴 Proje RAID Yönetimi Bileşeni Kartları (`proje_raid_yonetimi`)
**Bileşen:** Proje RAID Yönetimi | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PJR01` | **project_raid.riskler** | `project_raid.riskler` | Projeye ait tanımlanmış risklerin listesini gösterir. |
| `PJR02` | **project_raid.varsayimlar** | `project_raid.varsayimlar` | Proje için yapılan varsayımların listesini gösterir. |
| `PJR03` | **project_raid.sorunlar** | `project_raid.sorunlar` | Projede tespit edilen sorunların listesini gösterir. |
| `PJR04` | **project_raid.bagimliliklar** | `project_raid.bagimliliklar` | Projenin diğer görev/işlerle olan bağımlılıklarının listesini gösterir. |


### 🎴 Proje Stratejik İlişki Bileşeni Kartları (`proje_stratejik_iliski`)
**Bileşen:** Proje Stratejik İlişki | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PJS02` | **project_strategy_detail.stratejik_skor** | `project_strategy_detail.stratejik_skor` | Projenin toplam stratejik skorunu ve güçlü/zayıf ilişki sayılarını gösteren kart. |
| `PJS03` | **project_strategy_detail.bagli_surecler** | `project_strategy_detail.bagli_surecler` | Projeye bağlı süreçlerin kod, ad ve puan bilgilerini listeleyen tablo kartı. |
| `PJS01` | **project_strategy_detail.proje_bilgisi** | `project_strategy_detail.proje_bilgisi` | Projenin adını ve açıklamasını gösteren özet kartı. |


### 🎴 Proje Görev Yönetimi Bileşeni Kartları (`proje_gorev_yonetimi`)
**Bileşen:** Proje Görev Yönetimi | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `PJT01` | **project_task_detail.sayfa** | `project_task_detail.sayfa` | Görevin başlığı, durumu, önceliği, teslim tarihi, açıklaması ve bağlı Performans Göstergesi bilgisini gösteren tek kart. |
| `PJTF01` | **project_task_form.sayfa** | `project_task_form.sayfa` | Görevin başlık, açıklama, durum, öncelik, atanan kişi, bitiş tarihi ve bağlı süreç PG bilgilerinin girildiği tek form kartı. |


### 🎴 AI Koç Raporu Bileşeni Kartları (`rapor_ai_coach_grubu`)
**Bileşen:** AI Koç Raporu | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPI24` | **raporlar_index.ai_coach** | `raporlar_index.ai_coach` | Raporlar merkezinde 'ai_coach' raporuna giden kısayol kartı. |
| `RP153` | **raporlar_ai_coach.en_dusuk_performansli_3_strateji** | `raporlar_ai_coach.en_dusuk_performansli_3_strateji` | 🎯 En Düşük Performanslı 3 Strateji — rapor kartı. |
| `RP154` | **raporlar_ai_coach.ai_onerisi** | `raporlar_ai_coach.ai_onerisi` | AI Önerisi — rapor kartı. |
| `RP151` | **Analiz Edilen Strateji** | `raporlar_ai_coach.analiz_edilen_strateji` | Analiz Edilen Strateji — rapor kartı. |
| `RP152` | **En Düşük 3** | `raporlar_ai_coach.en_dusuk_3` | En Düşük 3 — rapor kartı. |


### 🎴 AI Danışman Raporu Bileşeni Kartları (`rapor_ai_danisman_grubu`)
**Bileşen:** AI Danışman Raporu | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPI23` | **raporlar_index.ai_danisman** | `raporlar_index.ai_danisman` | Raporlar merkezinde 'ai_danisman' raporuna giden kısayol kartı. |
| `RPAD01` | **raporlar_ai_danisman.sayfa** | `raporlar_ai_danisman.sayfa` | AI'nın sistem verilerinden ürettiği strateji pivot önerilerini (refocus, sunset, accelerate) listeleyen sayfanın tamamı. |


### 🎴 AI Sunum Oluşturucu Bileşeni Kartları (`rapor_ai_sunum_grubu`)
**Bileşen:** AI Sunum Oluşturucu | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP157` | **raporlar_ai_sunum.slayt_yapisi** | `raporlar_ai_sunum.slayt_yapisi` | Slayt Yapısı — rapor kartı. |
| `RP156` | **raporlar_ai_sunum.sunumda_kullanilacak_veriler** | `raporlar_ai_sunum.sunumda_kullanilacak_veriler` | Sunumda Kullanılacak Veriler — rapor kartı. |
| `RP155` | **raporlar_ai_sunum.sunum_hazir** | `raporlar_ai_sunum.sunum_hazir` | SUNUM HAZIR — rapor kartı. |
| `RPI11` | **raporlar_index.ai_sunum** | `raporlar_index.ai_sunum` | Raporlar merkezinde 'ai_sunum' raporuna giden kısayol kartı. |


### 🎴 Denetim Paketi Raporu Bileşeni Kartları (`rapor_audit_paketi_grubu`)
**Bileşen:** Denetim Paketi Raporu | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPI34` | **raporlar_index.audit_paketi** | `raporlar_index.audit_paketi` | Raporlar merkezinde 'audit_paketi' raporuna giden kısayol kartı. |
| `RP94` | **raporlar_audit_paketi.denetci_icin_hazir_pdf** | `raporlar_audit_paketi.denetci_icin_hazir_pdf` | DENETÇİ İÇİN HAZIR · PDF — rapor kartı. |
| `RP95` | **raporlar_audit_paketi.pdf_bolumleri** | `raporlar_audit_paketi.pdf_bolumleri` | PDF Bölümleri — rapor kartı. |
| `RP96` | **raporlar_audit_paketi.kullanim_amaci** | `raporlar_audit_paketi.kullanim_amaci` | Kullanım Amacı — rapor kartı. |


### 🎴 BI Bağlayıcı Bileşeni Kartları (`rapor_bi_connector_grubu`)
**Bileşen:** BI Bağlayıcı | **Kart Sayısı:** 6

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP163` | **raporlar_bi_connector.tableau_baglanti_rehberi** | `raporlar_bi_connector.tableau_baglanti_rehberi` | Tableau Bağlantı Rehberi — rapor kartı. |
| `RP162` | **raporlar_bi_connector.power_bi_baglanti_rehberi** | `raporlar_bi_connector.power_bi_baglanti_rehberi` | Power BI Bağlantı Rehberi — rapor kartı. |
| `RP160` | **KPI Ölçümleri (CSV)** | `raporlar_bi_connector.kpi_olcumleri_csv` | KPI Ölçümleri (CSV) — rapor kartı. |
| `RP161` | **Stratejiler (JSON)** | `raporlar_bi_connector.stratejiler_json` | Stratejiler (JSON) — rapor kartı. |
| `RPI40` | **raporlar_index.bi_connector** | `raporlar_index.bi_connector` | Raporlar merkezinde 'bi_connector' raporuna giden kısayol kartı. |
| `RP164` | **raporlar_bi_connector.excel_google_sheets** | `raporlar_bi_connector.excel_google_sheets` | Excel / Google Sheets — rapor kartı. |


### 🎴 Bireysel Hizalama Raporu Bileşeni Kartları (`rapor_bireysel_hizalama_grubu`)
**Bileşen:** Bireysel Hizalama Raporu | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP21` | **PG'si Olan Kullanıcı** | `raporlar_bireysel_hizalama.pg_si_olan_kullanici` | PG'si Olan Kullanıcı — rapor kartı. |
| `RP20` | **Genel Hizalama** | `raporlar_bireysel_hizalama.genel_hizalama` | Genel Hizalama — rapor kartı. |
| `RPI19` | **raporlar_index.bireysel_hizalama** | `raporlar_index.bireysel_hizalama` | Raporlar merkezinde 'bireysel_hizalama' raporuna giden kısayol kartı. |
| `RP23` | **raporlar_bireysel_hizalama.bireysel_pg_ler** | `raporlar_bireysel_hizalama.bireysel_pg_ler` | Bireysel PG'ler — rapor kartı. |
| `RP22` | **Toplam Kullanıcı** | `raporlar_bireysel_hizalama.toplam_kullanici` | Toplam Kullanıcı — rapor kartı. |


### 🎴 Toplu Bireysel Karne Üretimi Bileşeni Kartları (`rapor_bireysel_karne_batch_grubu`)
**Bileşen:** Toplu Bireysel Karne Üretimi | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPI35` | **raporlar_index.bireysel_karne_batch** | `raporlar_index.bireysel_karne_batch` | Raporlar merkezinde 'bireysel_karne_batch' raporuna giden kısayol kartı. |
| `RP177` | **raporlar_bireysel_karne_batch.toplu_uretim_zip** | `raporlar_bireysel_karne_batch.toplu_uretim_zip` | TOPLU ÜRETIM · ZIP — rapor kartı. |
| `RP178` | **raporlar_bireysel_karne_batch.her_karne_icerigi** | `raporlar_bireysel_karne_batch.her_karne_icerigi` | ⚙ Her Karne İçeriği — rapor kartı. |


### 🎴 Karbon Trend Raporu Bileşeni Kartları (`rapor_carbon_trend_grubu`)
**Bileşen:** Karbon Trend Raporu | **Kart Sayısı:** 6

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPI22` | **raporlar_index.carbon_trend** | `raporlar_index.carbon_trend` | Raporlar merkezinde 'carbon_trend' raporuna giden kısayol kartı. |
| `RP147` | **Veri Yılı** | `raporlar_carbon_trend.veri_yili` | Veri Yılı — rapor kartı. |
| `RP150` | **raporlar_carbon_trend.yillik_trend** | `raporlar_carbon_trend.yillik_trend` | Yıllık Trend — rapor kartı. |
| `RP146` | **Metrik Sayısı** | `raporlar_carbon_trend.metrik_sayisi` | Metrik Sayısı — rapor kartı. |
| `RP149` | **İlk Yıla Göre** | `raporlar_carbon_trend.ilk_yila_gore` | İlk Yıla Göre — rapor kartı. |
| `RP148` | **Son Yıl Toplam** | `raporlar_carbon_trend.son_yil_toplam` | Son Yıl Toplam — rapor kartı. |


### 🎴 CFO Panosu Bileşeni Kartları (`rapor_cfo_dashboard_grubu`)
**Bileşen:** CFO Panosu | **Kart Sayısı:** 10

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP116` | **Bütçe Aşan** | `raporlar_cfo_dashboard.butce_asan` | Bütçe Aşan — yönetici panosu kartı. |
| `RP121` | **raporlar_cfo_dashboard.strateji_bazli_butce_atifi** | `raporlar_cfo_dashboard.strateji_bazli_butce_atifi` | Strateji Bazlı Bütçe Atıfı — yönetici panosu kartı. |
| `RP113` | **Toplam Bütçe** | `raporlar_cfo_dashboard.toplam_butce` | Toplam Bütçe — yönetici panosu kartı. |
| `RP117` | **LLM Maliyet (30g)** | `raporlar_cfo_dashboard.llm_maliyet_30g` | LLM Maliyet (30g) — yönetici panosu kartı. |
| `RP119` | **raporlar_cfo_dashboard.en_buyuk_5_stratejik_girisim** | `raporlar_cfo_dashboard.en_buyuk_5_stratejik_girisim` | En Büyük 5 Stratejik Girişim — yönetici panosu kartı. |
| `RP120` | **raporlar_cfo_dashboard.durum_dagilimi** | `raporlar_cfo_dashboard.durum_dagilimi` | Durum Dağılımı — yönetici panosu kartı. |
| `RP118` | **Recurring Task** | `raporlar_cfo_dashboard.recurring_task` | Recurring Task — yönetici panosu kartı. |
| `RPI26` | **raporlar_index.cfo_dashboard** | `raporlar_index.cfo_dashboard` | Raporlar merkezinde 'cfo_dashboard' raporuna giden kısayol kartı. |
| `RP114` | **Harcanan** | `raporlar_cfo_dashboard.harcanan` | Harcanan — yönetici panosu kartı. |
| `RP115` | **Kalan** | `raporlar_cfo_dashboard.kalan` | Kalan — yönetici panosu kartı. |


### 🎴 CHRO Panosu Bileşeni Kartları (`rapor_chro_dashboard_grubu`)
**Bileşen:** CHRO Panosu | **Kart Sayısı:** 10

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP135` | **raporlar_chro_dashboard.departman_dagilimi** | `raporlar_chro_dashboard.departman_dagilimi` | Departman Dağılımı — yönetici panosu kartı. |
| `RP134` | **2FA Oranı** | `raporlar_chro_dashboard.2fa_orani` | 2FA Oranı — yönetici panosu kartı. |
| `RP136` | **raporlar_chro_dashboard.rol_dagilimi** | `raporlar_chro_dashboard.rol_dagilimi` | Rol Dağılımı — yönetici panosu kartı. |
| `RP131` | **Departman** | `raporlar_chro_dashboard.departman` | Departman — yönetici panosu kartı. |
| `RPI28` | **raporlar_index.chro_dashboard** | `raporlar_index.chro_dashboard` | Raporlar merkezinde 'chro_dashboard' raporuna giden kısayol kartı. |
| `RP137` | **raporlar_chro_dashboard.en_cok_bireysel_pg_sahibi_top_10** | `raporlar_chro_dashboard.en_cok_bireysel_pg_sahibi_top_10` | 🏆 En Çok Bireysel PG Sahibi (Top 10) — yönetici panosu kartı. |
| `RP133` | **Ort. PG / Kişi** | `raporlar_chro_dashboard.ort_pg_kisi` | Ort. PG / Kişi — yönetici panosu kartı. |
| `RP132` | **Bireysel PG** | `raporlar_chro_dashboard.bireysel_pg` | Bireysel PG — yönetici panosu kartı. |
| `RP138` | **raporlar_chro_dashboard.en_cok_surec_uyeligi_top_5** | `raporlar_chro_dashboard.en_cok_surec_uyeligi_top_5` | 📌 En Çok Süreç Üyeliği (Top 5) — yönetici panosu kartı. |
| `RP130` | **Çalışan** | `raporlar_chro_dashboard.calisan` | Çalışan — yönetici panosu kartı. |


### 🎴 CMMI Isı Haritası Bileşeni Kartları (`rapor_cmmi_heatmap_grubu`)
**Bileşen:** CMMI Isı Haritası | **Kart Sayısı:** 9

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP13` | **raporlar_cmmi_heatmap.seviye_dagilimi_ve_aciklamalar** | `raporlar_cmmi_heatmap.seviye_dagilimi_ve_aciklamalar` | Seviye Dağılımı ve Açıklamalar — rapor kartı. |
| `RP12` | **raporlar_cmmi_heatmap.ortalama_olgunluk** | `raporlar_cmmi_heatmap.ortalama_olgunluk` | Ortalama Olgunluk — rapor kartı. |
| `RPI17` | **raporlar_index.cmmi_heatmap** | `raporlar_index.cmmi_heatmap` | Raporlar merkezinde 'cmmi_heatmap' raporuna giden kısayol kartı. |
| `RP11` | **Düşük Seviye (L1-L2)** | `raporlar_cmmi_heatmap.dusuk_seviye_l1_l2` | Düşük Seviye (L1-L2) — rapor kartı. |
| `RP10` | **Optimize Eden (L5)** | `raporlar_cmmi_heatmap.optimize_eden_l5` | Optimize Eden (L5) — rapor kartı. |
| `RP09` | **Ortalama Seviye** | `raporlar_cmmi_heatmap.ortalama_seviye` | Ortalama Seviye — rapor kartı. |
| `RP08` | **Ölçülmemiş** | `raporlar_cmmi_heatmap.olculmemis` | Ölçülmemiş — rapor kartı. |
| `RP07` | **Ölçülen Süreç** | `raporlar_cmmi_heatmap.olculen_surec` | Ölçülen Süreç — rapor kartı. |
| `RP14` | **raporlar_cmmi_heatmap.surec_bazli_olgunluk** | `raporlar_cmmi_heatmap.surec_bazli_olgunluk` | Süreç Bazlı Olgunluk — rapor kartı. |


### 🎴 COO Panosu Bileşeni Kartları (`rapor_coo_dashboard_grubu`)
**Bileşen:** COO Panosu | **Kart Sayısı:** 9

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP127` | **raporlar_coo_dashboard.surec_saglik_dagilimi** | `raporlar_coo_dashboard.surec_saglik_dagilimi` | Süreç Sağlık Dağılımı — yönetici panosu kartı. |
| `RP129` | **raporlar_coo_dashboard.aktif_darbogazlar** | `raporlar_coo_dashboard.aktif_darbogazlar` | ⚠ Aktif Darboğazlar — yönetici panosu kartı. |
| `RP122` | **Süreç** | `raporlar_coo_dashboard.surec` | Süreç — yönetici panosu kartı. |
| `RP123` | **Ort. Sağlık** | `raporlar_coo_dashboard.ort_saglik` | Ort. Sağlık — yönetici panosu kartı. |
| `RP124` | **Geciken Faaliyet** | `raporlar_coo_dashboard.geciken_faaliyet` | Geciken Faaliyet — yönetici panosu kartı. |
| `RP125` | **Aktif Darboğaz** | `raporlar_coo_dashboard.aktif_darbogaz` | Aktif Darboğaz — yönetici panosu kartı. |
| `RP128` | **raporlar_coo_dashboard.surecler_saglik_skoru** | `raporlar_coo_dashboard.surecler_saglik_skoru` | Süreçler (Sağlık Skoru) — yönetici panosu kartı. |
| `RPI27` | **raporlar_index.coo_dashboard** | `raporlar_index.coo_dashboard` | Raporlar merkezinde 'coo_dashboard' raporuna giden kısayol kartı. |
| `RP126` | **Ort. CMMI** | `raporlar_coo_dashboard.ort_cmmi` | Ort. CMMI — yönetici panosu kartı. |


### 🎴 Departman Performans Raporu Bileşeni Kartları (`rapor_departman_performans_grubu`)
**Bileşen:** Departman Performans Raporu | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPI06` | **raporlar_index.departman_performans** | `raporlar_index.departman_performans` | Raporlar merkezinde 'departman_performans' raporuna giden kısayol kartı. |
| `RP02` | **Toplam Çalışan** | `raporlar_departman_performans.toplam_calisan` | Toplam Çalışan — rapor kartı. |
| `RP04` | **raporlar_departman_performans.departman_karti** | `raporlar_departman_performans.departman_karti` | Departman Kartı — rapor kartı. |
| `RP01` | **Departman** | `raporlar_departman_performans.departman` | Departman — rapor kartı. |
| `RP03` | **Toplam Bireysel PG** | `raporlar_departman_performans.toplam_bireysel_pg` | Toplam Bireysel PG — rapor kartı. |


### 🎴 Erken Uyarı Raporu Bileşeni Kartları (`rapor_early_warning_grubu`)
**Bileşen:** Erken Uyarı Raporu | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP72` | **Kontrol Edilen PG** | `raporlar_early_warning.kontrol_edilen_pg` | Kontrol Edilen PG — rapor kartı. |
| `RPI25` | **raporlar_index.early_warning** | `raporlar_index.early_warning` | Raporlar merkezinde 'early_warning' raporuna giden kısayol kartı. |
| `RP74` | **Yüksek Öncelik** | `raporlar_early_warning.yuksek_oncelik` | Yüksek Öncelik — rapor kartı. |
| `RP75` | **raporlar_early_warning.uyari_listesi** | `raporlar_early_warning.uyari_listesi` | Uyarı Listesi — rapor kartı. |
| `RP73` | **Uyarı Sayısı** | `raporlar_early_warning.uyari_sayisi` | Uyarı Sayısı — rapor kartı. |


### 🎴 ESG Raporu Bileşeni Kartları (`rapor_esg_rapor_grubu`)
**Bileşen:** ESG Raporu | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP175` | **raporlar_esg_rapor.yatirimci_denetci_hazir_pdf** | `raporlar_esg_rapor.yatirimci_denetci_hazir_pdf` | YATIRIMCI / DENETÇI HAZIR · PDF — rapor kartı. |
| `RPI33` | **raporlar_index.esg_rapor** | `raporlar_index.esg_rapor` | Raporlar merkezinde 'esg_rapor' raporuna giden kısayol kartı. |
| `RP176` | **raporlar_esg_rapor.rapor_icerigi** | `raporlar_esg_rapor.rapor_icerigi` | 📋 Rapor İçeriği — rapor kartı. |


### 🎴 ESG Yönetim Sayfası Bileşeni Kartları (`rapor_esg_yonetim_grubu`)
**Bileşen:** ESG Yönetim Sayfası | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPEY01` | **raporlar_esg_yonetim.sayfa** | `raporlar_esg_yonetim.sayfa` | ESG metriklerinin listelendiği, eklenip düzenlendiği tüm sayfa içeriği. |


### 🎴 Yıllar Arası Evrim Filmi Bileşeni Kartları (`rapor_evrim_filmi_grubu`)
**Bileşen:** Yıllar Arası Evrim Filmi | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP139` | **raporlar_evrim_filmi.yillar_arasi_evrim_filmi** | `raporlar_evrim_filmi.yillar_arasi_evrim_filmi` | Yıllar Arası Evrim Filmi — rapor kartı. |
| `RPI10` | **raporlar_index.evrim_filmi** | `raporlar_index.evrim_filmi` | Raporlar merkezinde 'evrim_filmi' raporuna giden kısayol kartı. |


### 🎴 Hedef Revizyon Raporu Bileşeni Kartları (`rapor_hedef_revizyon_grubu`)
**Bileşen:** Hedef Revizyon Raporu | **Kart Sayısı:** 6

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP18` | **raporlar_hedef_revizyon.yillara_gore_revizyon** | `raporlar_hedef_revizyon.yillara_gore_revizyon` | Yıllara Göre Revizyon — rapor kartı. |
| `RPI05` | **raporlar_index.hedef_revizyon** | `raporlar_index.hedef_revizyon` | Raporlar merkezinde 'hedef_revizyon' raporuna giden kısayol kartı. |
| `RP15` | **Toplam Plan Dönemi** | `raporlar_hedef_revizyon.toplam_plan_donemi` | Toplam Plan Dönemi — rapor kartı. |
| `RP17` | **Toplam Revizyon** | `raporlar_hedef_revizyon.toplam_revizyon` | Toplam Revizyon — rapor kartı. |
| `RP19` | **raporlar_hedef_revizyon.revize_edilen_pg_ler** | `raporlar_hedef_revizyon.revize_edilen_pg_ler` | Revize Edilen PG'ler — rapor kartı. |
| `RP16` | **Revizyon Yapılan Yıl** | `raporlar_hedef_revizyon.revizyon_yapilan_yil` | Revizyon Yapılan Yıl — rapor kartı. |


### 🎴 Hizalama Sankey Diyagramı Bileşeni Kartları (`rapor_hizalama_sankey_grubu`)
**Bileşen:** Hizalama Sankey Diyagramı | **Kart Sayısı:** 8

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP169` | **Bağlantı** | `raporlar_hizalama_sankey.baglanti` | Bağlantı — rapor kartı. |
| `RP165` | **Ana Strateji** | `raporlar_hizalama_sankey.ana_strateji` | Ana Strateji — rapor kartı. |
| `RP167` | **Süreç** | `raporlar_hizalama_sankey.surec` | Süreç — rapor kartı. |
| `RP166` | **Alt Strateji** | `raporlar_hizalama_sankey.alt_strateji` | Alt Strateji — rapor kartı. |
| `RPI04` | **raporlar_index.hizalama_sankey** | `raporlar_index.hizalama_sankey` | Raporlar merkezinde 'hizalama_sankey' raporuna giden kısayol kartı. |
| `RPHS01` | **raporlar_hizalama_sankey.akis_gorseli** | `raporlar_hizalama_sankey.akis_gorseli` | Vizyon-Strateji-Alt Strateji-Sürec-PG hiyerarşisini bant kalınlığı ve renk koduyla gösteren Sankey akış diyagramı. |
| `RP168` | **PG** | `raporlar_hizalama_sankey.pg` | PG — rapor kartı. |
| `RP170` | **Hizalanmamış** | `raporlar_hizalama_sankey.hizalanmamis` | Hizalanmamış — rapor kartı. |


### 🎴 2FA Güvenlik Raporu Bileşeni Kartları (`rapor_iki_fa_grubu`)
**Bileşen:** 2FA Güvenlik Raporu | **Kart Sayısı:** 7

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP88` | **Toplam Kullanıcı** | `raporlar_iki_fa.toplam_kullanici` | Toplam Kullanıcı — rapor kartı. |
| `RP90` | **2FA Yok** | `raporlar_iki_fa.2fa_yok` | 2FA Yok — rapor kartı. |
| `RP91` | **Etkinlik %** | `raporlar_iki_fa.etkinlik` | Etkinlik % — rapor kartı. |
| `RP92` | **raporlar_iki_fa.2fa_dagilim** | `raporlar_iki_fa.2fa_dagilim` | 2FA Dağılım — rapor kartı. |
| `RP93` | **raporlar_iki_fa.2fa_si_olmayan_yoneticiler_kritik_guvenlik_acigi** | `raporlar_iki_fa.2fa_si_olmayan_yoneticiler_kritik_guvenlik_acigi` | ⚠ 2FA'sı Olmayan Yöneticiler (kritik güvenlik açığı) — rapor kartı. |
| `RPI21` | **raporlar_index.iki_fa** | `raporlar_index.iki_fa` | Raporlar merkezinde 'iki_fa' raporuna giden kısayol kartı. |
| `RP89` | **2FA Etkin** | `raporlar_iki_fa.2fa_etkin` | 2FA Etkin — rapor kartı. |


### 🎴 Girişim Balon Grafiği Bileşeni Kartları (`rapor_initiative_bubble_grubu`)
**Bileşen:** Girişim Balon Grafiği | **Kart Sayısı:** 12

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP30` | **Toplam Bütçe** | `raporlar_initiative_bubble.toplam_butce` | Toplam Bütçe — rapor kartı. |
| `RP24` | **raporlar_initiative_bubble.yatay_eksen_x** | `raporlar_initiative_bubble.yatay_eksen_x` | Yatay Eksen (X) — rapor kartı. |
| `RP25` | **raporlar_initiative_bubble.dikey_eksen_y** | `raporlar_initiative_bubble.dikey_eksen_y` | Dikey Eksen (Y) — rapor kartı. |
| `RP26` | **raporlar_initiative_bubble.daire_boyutu** | `raporlar_initiative_bubble.daire_boyutu` | Daire Boyutu — rapor kartı. |
| `RP27` | **raporlar_initiative_bubble.daire_rengi** | `raporlar_initiative_bubble.daire_rengi` | Daire Rengi — rapor kartı. |
| `RP28` | **raporlar_initiative_bubble.4_kadran_nasil_yorumlanir** | `raporlar_initiative_bubble.4_kadran_nasil_yorumlanir` | 4 Kadran nasıl yorumlanır? — rapor kartı. |
| `RP33` | **raporlar_initiative_bubble.portfoy_balon_grafigi** | `raporlar_initiative_bubble.portfoy_balon_grafigi` | Portföy Balon Grafiği — rapor kartı. |
| `RP34` | **raporlar_initiative_bubble.detay_tablosu** | `raporlar_initiative_bubble.detay_tablosu` | Detay Tablosu — rapor kartı. |
| `RP29` | **Toplam Girişim** | `raporlar_initiative_bubble.toplam_girisim` | Toplam Girişim — rapor kartı. |
| `RP31` | **Harcanan Bütçe** | `raporlar_initiative_bubble.harcanan_butce` | Harcanan Bütçe — rapor kartı. |
| `RP32` | **Ortalama İlerleme** | `raporlar_initiative_bubble.ortalama_ilerleme` | Ortalama İlerleme — rapor kartı. |
| `RPI08` | **raporlar_index.initiative_bubble** | `raporlar_index.initiative_bubble` | Raporlar merkezinde 'initiative_bubble' raporuna giden kısayol kartı. |


### 🎴 Girişim Yol Haritası Bileşeni Kartları (`rapor_initiative_roadmap_grubu`)
**Bileşen:** Girişim Yol Haritası | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPI15` | **raporlar_index.initiative_roadmap** | `raporlar_index.initiative_roadmap` | Raporlar merkezinde 'initiative_roadmap' raporuna giden kısayol kartı. |
| `RP36` | **Yıl Aralığı** | `raporlar_initiative_roadmap.yil_araligi` | Yıl Aralığı — rapor kartı. |
| `RP35` | **Toplam Stratejik Girişim** | `raporlar_initiative_roadmap.toplam_stratejik_girisim` | Toplam Stratejik Girişim — rapor kartı. |
| `RP38` | **raporlar_initiative_roadmap.stratejik_girisimler** | `raporlar_initiative_roadmap.stratejik_girisimler` | Stratejik Girişimler — rapor kartı. |
| `RP37` | **Milestone** | `raporlar_initiative_roadmap.milestone` | Milestone — rapor kartı. |


### 🎴 KV Çarpıklık Raporu Bileşeni Kartları (`rapor_kv_carpiklik_grubu`)
**Bileşen:** KV Çarpıklık Raporu | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPKV01` | **raporlar_kv_carpiklik.ozet_kartlari** | `raporlar_kv_carpiklik.ozet_kartlari` | Toplam strateji sayısı, dengeli/dengesiz strateji dağılımı ve aktif plan yılını özetleyen kartlar. |
| `RPKV02` | **raporlar_kv_carpiklik.agirlik_skor_karsilastirma** | `raporlar_kv_carpiklik.agirlik_skor_karsilastirma` | Her strateji için stratejik ağırlık yüzdesi ile ortalama süreç skorunu yan yana çubuklarla karşılaştırır. |
| `RPKV03` | **raporlar_kv_carpiklik.detay_tablosu** | `raporlar_kv_carpiklik.detay_tablosu` | Strateji bazında ağırlık, ortalama skor, çarpıklık değeri, değerlendirme ve bağlı süreç sayısını listeleyen detay tablosu. |
| `RPI03` | **raporlar_index.kv_carpiklik** | `raporlar_index.kv_carpiklik` | Raporlar merkezinde 'kv_carpiklik' raporuna giden kısayol kartı. |


### 🎴 ML Anomali Tespiti Bileşeni Kartları (`rapor_ml_anomaly_grubu`)
**Bileşen:** ML Anomali Tespiti | **Kart Sayısı:** 5

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP77` | **Yetersiz Veri (Atlandı)** | `raporlar_ml_anomaly.yetersiz_veri_atlandi` | Yetersiz Veri (Atlandı) — rapor kartı. |
| `RP76` | **Analiz Edilen PG** | `raporlar_ml_anomaly.analiz_edilen_pg` | Analiz Edilen PG — rapor kartı. |
| `RP78` | **Anomali Tespit Edildi** | `raporlar_ml_anomaly.anomali_tespit_edildi` | Anomali Tespit Edildi — rapor kartı. |
| `RP79` | **raporlar_ml_anomaly.tespit_edilen_anomaliler** | `raporlar_ml_anomaly.tespit_edilen_anomaliler` | Tespit Edilen Anomaliler — rapor kartı. |
| `RPI41` | **raporlar_index.ml_anomaly** | `raporlar_index.ml_anomaly` | Raporlar merkezinde 'ml_anomaly' raporuna giden kısayol kartı. |


### 🎴 Mobile Hub Raporu Bileşeni Kartları (`rapor_mobile_grubu`)
**Bileşen:** Mobile Hub Raporu | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP179` | **raporlar_mobile.mobile_hub** | `raporlar_mobile.mobile_hub` | Mobile Hub — rapor kartı. |
| `RPI39` | **raporlar_index.mobile** | `raporlar_index.mobile` | Raporlar merkezinde 'mobile' raporuna giden kısayol kartı. |


### 🎴 Muda (İsraf) Analizi Bileşeni Kartları (`rapor_muda_analizi_grubu`)
**Bileşen:** Muda (İsraf) Analizi | **Kart Sayısı:** 6

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPI16` | **raporlar_index.muda_analizi** | `raporlar_index.muda_analizi` | Raporlar merkezinde 'muda_analizi' raporuna giden kısayol kartı. |
| `RP64` | **raporlar_muda_analizi.7_muda_turu_bulgu_sayilari_aciklamalar** | `raporlar_muda_analizi.7_muda_turu_bulgu_sayilari_aciklamalar` | 7 Muda Türü — Bulgu Sayıları + Açıklamalar — rapor kartı. |
| `RP65` | **raporlar_muda_analizi.bulgu_saptanan_surecler** | `raporlar_muda_analizi.bulgu_saptanan_surecler` | Bulgu Saptanan Süreçler — rapor kartı. |
| `RP61` | **Analiz Edilen Süreç** | `raporlar_muda_analizi.analiz_edilen_surec` | Analiz Edilen Süreç — rapor kartı. |
| `RP62` | **Bulgu Olan Süreç** | `raporlar_muda_analizi.bulgu_olan_surec` | Bulgu Olan Süreç — rapor kartı. |
| `RP63` | **Toplam Bulgu** | `raporlar_muda_analizi.toplam_bulgu` | Toplam Bulgu — rapor kartı. |


### 🎴 Doğal Dil Sorgulama Bileşeni Kartları (`rapor_nlp_query_grubu`)
**Bileşen:** Doğal Dil Sorgulama | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPI37` | **raporlar_index.nlp_query** | `raporlar_index.nlp_query` | Raporlar merkezinde 'nlp_query' raporuna giden kısayol kartı. |
| `RP159` | **raporlar_nlp_query.cevap** | `raporlar_nlp_query.cevap` | Cevap — rapor kartı. |
| `RP158` | **raporlar_nlp_query.hazir_sorular** | `raporlar_nlp_query.hazir_sorular` | ⚡ Hazır Sorular — rapor kartı. |


### 🎴 OKR Kademelendirme Raporu Bileşeni Kartları (`rapor_okr_cascade_grubu`)
**Bileşen:** OKR Kademelendirme Raporu | **Kart Sayısı:** 7

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP51` | **Key Result** | `raporlar_okr_cascade.key_result` | Key Result — rapor kartı. |
| `RP50` | **Objective** | `raporlar_okr_cascade.objective` | Objective — rapor kartı. |
| `RPOC01` | **raporlar_okr_cascade.okr_aciklama** | `raporlar_okr_cascade.okr_aciklama` | OKR kavramını (Objective/Key Result) kısaca açıklayan bilgilendirme kartı. |
| `RPOC02` | **raporlar_okr_cascade.hizalama_listesi** | `raporlar_okr_cascade.hizalama_listesi` | OKR özet istatistikleri ve her Anahtar Sonucun strateji bağlantısı ile ilerleme yüzdesini listeleyen kart (içerik JS ile doldurulur). |
| `RP53` | **Plan Yılı** | `raporlar_okr_cascade.plan_yili` | Plan Yılı — rapor kartı. |
| `RPI14` | **raporlar_index.okr_cascade** | `raporlar_index.okr_cascade` | Raporlar merkezinde 'okr_cascade' raporuna giden kısayol kartı. |
| `RP52` | **Ort. Tamamlanma** | `raporlar_okr_cascade.ort_tamamlanma` | Ort. Tamamlanma — rapor kartı. |


### 🎴 Onay Zinciri Raporu Bileşeni Kartları (`rapor_onay_zinciri_grubu`)
**Bileşen:** Onay Zinciri Raporu | **Kart Sayısı:** 6

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP97` | **Toplam** | `raporlar_onay_zinciri.toplam` | Toplam — rapor kartı. |
| `RPI42` | **raporlar_index.onay_zinciri** | `raporlar_index.onay_zinciri` | Raporlar merkezinde 'onay_zinciri' raporuna giden kısayol kartı. |
| `RP100` | **Reddedilen** | `raporlar_onay_zinciri.reddedilen` | Reddedilen — rapor kartı. |
| `RP101` | **raporlar_onay_zinciri.stratejik_girisim_ler** | `raporlar_onay_zinciri.stratejik_girisim_ler` | 📝 Stratejik Girişim'ler — rapor kartı. |
| `RP98` | **Onay Bekliyor** | `raporlar_onay_zinciri.onay_bekliyor` | Onay Bekliyor — rapor kartı. |
| `RP99` | **Onaylanmış** | `raporlar_onay_zinciri.onaylanmis` | Onaylanmış — rapor kartı. |


### 🎴 PG-Proje Etki Raporu Bileşeni Kartları (`rapor_pg_proje_etki_grubu`)
**Bileşen:** PG-Proje Etki Raporu | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPPE03` | **raporlar_pg_proje_etki.proje_listesi** | `raporlar_pg_proje_etki.proje_listesi` | Her projenin bağlı süreç ve PG sayılarını, hedef üstü performans oranını listeleyen ve satır tıklanınca detay açan tablo kartıdır. |
| `RPPE02` | **raporlar_pg_proje_etki.ozet_kartlari** | `raporlar_pg_proje_etki.ozet_kartlari` | Toplam proje, PG'ye bağlı proje, bağsız proje, etkilenen PG sayısı ve ortalama hedef üstü oranını özetleyen istatistik kartlarıdır. |
| `RPPE01` | **raporlar_pg_proje_etki.nasil_okunur** | `raporlar_pg_proje_etki.nasil_okunur` | Rapordaki sütunların ve satır genişletme özelliğinin nasıl yorumlanacağını açıklayan bilgi kartıdır. |
| `RPI02` | **raporlar_index.pg_proje_etki** | `raporlar_index.pg_proje_etki` | Raporlar merkezinde 'pg_proje_etki' raporuna giden kısayol kartı. |


### 🎴 Çeyreklik Review Raporu Bileşeni Kartları (`rapor_quarterly_review_grubu`)
**Bileşen:** Çeyreklik Review Raporu | **Kart Sayısı:** 8

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPI29` | **raporlar_index.quarterly_review** | `raporlar_index.quarterly_review` | Raporlar merkezinde 'quarterly_review' raporuna giden kısayol kartı. |
| `RP45` | **raporlar_quarterly_review.on_calisma_sorulari** | `raporlar_quarterly_review.on_calisma_sorulari` | ❓ Ön Çalışma Soruları — rapor kartı. |
| `RP44` | **raporlar_quarterly_review.onerilen_agenda** | `raporlar_quarterly_review.onerilen_agenda` | 📋 Önerilen Agenda — rapor kartı. |
| `RP43` | **raporlar_quarterly_review.ai_yonetici_ozeti** | `raporlar_quarterly_review.ai_yonetici_ozeti` | AI Yönetici Özeti — rapor kartı. |
| `RP39` | **raporlar_quarterly_review.ceyreklik_review_toplantisi** | `raporlar_quarterly_review.ceyreklik_review_toplantisi` | Çeyreklik Review Toplantısı — rapor kartı. |
| `RP40` | **Ölçüm Hacmi (Q)** | `raporlar_quarterly_review.olcum_hacmi_q` | Ölçüm Hacmi (Q) — rapor kartı. |
| `RP41` | **Yeni Stratejik Girişim** | `raporlar_quarterly_review.yeni_stratejik_girisim` | Yeni Stratejik Girişim — rapor kartı. |
| `RP42` | **Tamamlanan Stratejik Girişim** | `raporlar_quarterly_review.tamamlanan_stratejik_girisim` | Tamamlanan Stratejik Girişim — rapor kartı. |


### 🎴 Risk Isı Haritası Bileşeni Kartları (`rapor_risk_heatmap_grubu`)
**Bileşen:** Risk Isı Haritası | **Kart Sayısı:** 7

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP66` | **Toplam Risk** | `raporlar_risk_heatmap.toplam_risk` | Toplam Risk — rapor kartı. |
| `RP71` | **raporlar_risk_heatmap.en_yuksek_rpn_ilk_10** | `raporlar_risk_heatmap.en_yuksek_rpn_ilk_10` | En Yüksek RPN — İlk 10 — rapor kartı. |
| `RP68` | **Azaltıldı** | `raporlar_risk_heatmap.azaltildi` | Azaltıldı — rapor kartı. |
| `RP67` | **Açık** | `raporlar_risk_heatmap.acik` | Açık — rapor kartı. |
| `RP69` | **Kritik (≥15)** | `raporlar_risk_heatmap.kritik_15` | Kritik (≥15) — rapor kartı. |
| `RPI20` | **raporlar_index.risk_heatmap** | `raporlar_index.risk_heatmap` | Raporlar merkezinde 'risk_heatmap' raporuna giden kısayol kartı. |
| `RP70` | **raporlar_risk_heatmap.5_5_risk_matrisi** | `raporlar_risk_heatmap.5_5_risk_matrisi` | 5×5 Risk Matrisi — rapor kartı. |


### 🎴 Sabah Özeti Raporu Bileşeni Kartları (`rapor_sabah_ozeti_grubu`)
**Bileşen:** Sabah Özeti Raporu | **Kart Sayısı:** 8

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP56` | **Önümüzdeki 7 Gün** | `raporlar_sabah_ozeti.onumuzdeki_7_gun` | Önümüzdeki 7 Gün — rapor kartı. |
| `RP59` | **Son 7 Gün Ölçüm** | `raporlar_sabah_ozeti.son_7_gun_olcum` | Son 7 Gün Ölçüm — rapor kartı. |
| `RP58` | **Bugün Ölçüm** | `raporlar_sabah_ozeti.bugun_olcum` | Bugün Ölçüm — rapor kartı. |
| `RP57` | **Son 7 Gün Tamamlanan** | `raporlar_sabah_ozeti.son_7_gun_tamamlanan` | Son 7 Gün Tamamlanan — rapor kartı. |
| `RP55` | **Bugün Bitiş** | `raporlar_sabah_ozeti.bugun_bitis` | Bugün Bitiş — rapor kartı. |
| `RPI09` | **raporlar_index.sabah_ozeti** | `raporlar_index.sabah_ozeti` | Raporlar merkezinde 'sabah_ozeti' raporuna giden kısayol kartı. |
| `RP54` | **Geciken Faaliyet** | `raporlar_sabah_ozeti.geciken_faaliyet` | Geciken Faaliyet — rapor kartı. |
| `RP60` | **raporlar_sabah_ozeti.son_veri_girisleri** | `raporlar_sabah_ozeti.son_veri_girisleri` | Son Veri Girişleri — rapor kartı. |


### 🎴 Sektör Kıyaslama Raporu Bileşeni Kartları (`rapor_sektor_benchmark_grubu`)
**Bileşen:** Sektör Kıyaslama Raporu | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP143` | **raporlar_sektor_benchmark.sektor_otomotiv_yan_sanayi** | `raporlar_sektor_benchmark.sektor_otomotiv_yan_sanayi` | SEKTÖR: Otomotiv / Yan Sanayi — rapor kartı. |
| `RPI38` | **raporlar_index.sektor_benchmark** | `raporlar_index.sektor_benchmark` | Raporlar merkezinde 'sektor_benchmark' raporuna giden kısayol kartı. |
| `RP144` | **raporlar_sektor_benchmark.sektor_ortalamalari** | `raporlar_sektor_benchmark.sektor_ortalamalari` | Sektör Ortalamaları — rapor kartı. |
| `RP145` | **raporlar_sektor_benchmark.ai_sektor_degerlendirmesi** | `raporlar_sektor_benchmark.ai_sektor_degerlendirmesi` | AI Sektör Değerlendirmesi — rapor kartı. |


### 🎴 Sektörel Plan Paketleri Bileşeni Kartları (`rapor_sektorel_grubu`)
**Bileşen:** Sektörel Plan Paketleri | **Kart Sayısı:** 9

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPSK06` | **raporlar_sektorel.sektor_perakende** | `raporlar_sektorel.sektor_perakende` | 'perakende' sektörüne özel hazır plan paketi kartı. |
| `RPSK07` | **raporlar_sektorel.sektor_insaat** | `raporlar_sektorel.sektor_insaat` | 'insaat' sektörüne özel hazır plan paketi kartı. |
| `RPI36` | **raporlar_index.sektorel** | `raporlar_index.sektorel` | Raporlar merkezinde 'sektorel' raporuna giden kısayol kartı. |
| `RPSK01` | **raporlar_sektorel.sektor_otomotiv** | `raporlar_sektorel.sektor_otomotiv` | 'otomotiv' sektörüne özel hazır plan paketi kartı. |
| `RPSK08` | **raporlar_sektorel.sektor_hizmet** | `raporlar_sektorel.sektor_hizmet` | 'hizmet' sektörüne özel hazır plan paketi kartı. |
| `RPSK02` | **raporlar_sektorel.sektor_saglik** | `raporlar_sektorel.sektor_saglik` | 'saglik' sektörüne özel hazır plan paketi kartı. |
| `RPSK03` | **raporlar_sektorel.sektor_finans** | `raporlar_sektorel.sektor_finans` | 'finans' sektörüne özel hazır plan paketi kartı. |
| `RPSK04` | **raporlar_sektorel.sektor_egitim** | `raporlar_sektorel.sektor_egitim` | 'egitim' sektörüne özel hazır plan paketi kartı. |
| `RPSK05` | **raporlar_sektorel.sektor_kamu** | `raporlar_sektorel.sektor_kamu` | 'kamu' sektörüne özel hazır plan paketi kartı. |


### 🎴 Strateji Hikayesi Raporu Bileşeni Kartları (`rapor_strateji_hikayesi_grubu`)
**Bileşen:** Strateji Hikayesi Raporu | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP141` | **raporlar_strateji_hikayesi.yillik_snapshot** | `raporlar_strateji_hikayesi.yillik_snapshot` | 📊 Yıllık Snapshot — rapor kartı. |
| `RP140` | **raporlar_strateji_hikayesi.hikaye** | `raporlar_strateji_hikayesi.hikaye` | Hikaye — rapor kartı. |
| `RPI30` | **raporlar_index.strateji_hikayesi** | `raporlar_index.strateji_hikayesi` | Raporlar merkezinde 'strateji_hikayesi' raporuna giden kısayol kartı. |
| `RP142` | **raporlar_strateji_hikayesi.kirilim_noktalari** | `raporlar_strateji_hikayesi.kirilim_noktalari` | ⚡ Kırılım Noktaları — rapor kartı. |


### 🎴 Stratejik Yıllık Rapor Bileşeni Kartları (`rapor_stratejik_yillik_grubu`)
**Bileşen:** Stratejik Yıllık Rapor | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP173` | **raporlar_stratejik_yillik.premium_pdf_35_sayfa** | `raporlar_stratejik_yillik.premium_pdf_35_sayfa` | PREMIUM PDF · ~35 SAYFA — rapor kartı. |
| `RPI31` | **raporlar_index.stratejik_yillik** | `raporlar_index.stratejik_yillik` | Raporlar merkezinde 'stratejik_yillik' raporuna giden kısayol kartı. |
| `RP174` | **raporlar_stratejik_yillik.bolum_yapisi** | `raporlar_stratejik_yillik.bolum_yapisi` | 📚 Bölüm Yapısı — rapor kartı. |


### 🎴 Stratejik Hiyerarşi Sunburst Bileşeni Kartları (`rapor_sunburst_grubu`)
**Bileşen:** Stratejik Hiyerarşi Sunburst | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPI12` | **raporlar_index.sunburst** | `raporlar_index.sunburst` | Raporlar merkezinde 'sunburst' raporuna giden kısayol kartı. |
| `RP112` | **raporlar_sunburst.stratejik_hiyerarsi_sunburst** | `raporlar_sunburst.stratejik_hiyerarsi_sunburst` | Stratejik Hiyerarşi Sunburst — rapor kartı. |


### 🎴 Veri Kalitesi Raporu Bileşeni Kartları (`rapor_veri_kalitesi_grubu`)
**Bileşen:** Veri Kalitesi Raporu | **Kart Sayısı:** 9

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP87` | **raporlar_veri_kalitesi.surec_bazli_doluluk** | `raporlar_veri_kalitesi.surec_bazli_doluluk` | Süreç Bazlı Doluluk — rapor kartı. |
| `RP81` | **Toplam PG** | `raporlar_veri_kalitesi.toplam_pg` | Toplam PG — rapor kartı. |
| `RP84` | **Sağlıklı** | `raporlar_veri_kalitesi.saglikli` | Sağlıklı — rapor kartı. |
| `RP82` | **Kritik** | `raporlar_veri_kalitesi.kritik` | Kritik — rapor kartı. |
| `RPI01` | **raporlar_index.veri_kalitesi** | `raporlar_index.veri_kalitesi` | Raporlar merkezinde 'veri_kalitesi' raporuna giden kısayol kartı. |
| `RP83` | **Orta Risk** | `raporlar_veri_kalitesi.orta_risk` | Orta Risk — rapor kartı. |
| `RP80` | **Genel Skor** | `raporlar_veri_kalitesi.genel_skor` | Genel Skor — rapor kartı. |
| `RP86` | **raporlar_veri_kalitesi.orta_risk_pg_ler** | `raporlar_veri_kalitesi.orta_risk_pg_ler` | Orta Risk PG'ler — rapor kartı. |
| `RP85` | **raporlar_veri_kalitesi.kritik_pg_ler** | `raporlar_veri_kalitesi.kritik_pg_ler` | Kritik PG'ler — rapor kartı. |


### 🎴 VRIO Portföy Raporu Bileşeni Kartları (`rapor_vrio_portfoy_grubu`)
**Bileşen:** VRIO Portföy Raporu | **Kart Sayısı:** 12

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP103` | **Sürdürülebilir** | `raporlar_vrio_portfoy.surdurulebilir` | Sürdürülebilir — rapor kartı. |
| `RP102` | **Toplam Kaynak** | `raporlar_vrio_portfoy.toplam_kaynak` | Toplam Kaynak — rapor kartı. |
| `RP104` | **Geçici** | `raporlar_vrio_portfoy.gecici` | Geçici — rapor kartı. |
| `RP105` | **Kullanılmayan** | `raporlar_vrio_portfoy.kullanilmayan` | Kullanılmayan — rapor kartı. |
| `RP106` | **Dezavantaj** | `raporlar_vrio_portfoy.dezavantaj` | Dezavantaj — rapor kartı. |
| `RPVP01` | **raporlar_vrio_portfoy.sayfa** | `raporlar_vrio_portfoy.sayfa` | Kaynakların VRIO kriterlerine göre gruplandığı özet sayaçlar ve sınıflandırma kutularının bulunduğu tüm sayfa içeriği. |
| `RP111` | **Rekabetçi Dezavantaj 0** | `raporlar_vrio_portfoy.rekabetci_dezavantaj_0` | Rekabetçi Dezavantaj 0 — rapor kartı. |
| `RP110` | **Rekabet Paritesi 0** | `raporlar_vrio_portfoy.rekabet_paritesi_0` | Rekabet Paritesi 0 — rapor kartı. |
| `RP109` | **Kullanılmayan Avantaj 0** | `raporlar_vrio_portfoy.kullanilmayan_avantaj_0` | Kullanılmayan Avantaj 0 — rapor kartı. |
| `RP108` | **Geçici Rekabet Avantajı 0** | `raporlar_vrio_portfoy.gecici_rekabet_avantaji_0` | Geçici Rekabet Avantajı 0 — rapor kartı. |
| `RP107` | **Sürdürülebilir Rekabet Avantajı 0** | `raporlar_vrio_portfoy.surdurulebilir_rekabet_avantaji_0` | Sürdürülebilir Rekabet Avantajı 0 — rapor kartı. |
| `RPI13` | **raporlar_index.vrio_portfoy** | `raporlar_index.vrio_portfoy` | Raporlar merkezinde 'vrio_portfoy' raporuna giden kısayol kartı. |


### 🎴 Yatırımcı Sunumu Bileşeni Kartları (`rapor_yatirimci_sunum_grubu`)
**Bileşen:** Yatırımcı Sunumu | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPI32` | **raporlar_index.yatirimci_sunum** | `raporlar_index.yatirimci_sunum` | Raporlar merkezinde 'yatirimci_sunum' raporuna giden kısayol kartı. |
| `RP172` | **raporlar_yatirimci_sunum.slayt_yapisi** | `raporlar_yatirimci_sunum.slayt_yapisi` | 🎯 Slayt Yapısı — rapor kartı. |
| `RP171` | **raporlar_yatirimci_sunum.pptx_sunum_16_9** | `raporlar_yatirimci_sunum.pptx_sunum_16_9` | PPTX SUNUM · 16:9 — rapor kartı. |


### 🎴 Yönetici Liderlik Raporu Bileşeni Kartları (`rapor_yonetici_liderlik_grubu`)
**Bileşen:** Yönetici Liderlik Raporu | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP05` | **Yönetici Sayısı** | `raporlar_yonetici_liderlik.yonetici_sayisi` | Yönetici Sayısı — rapor kartı. |
| `RPI07` | **raporlar_index.yonetici_liderlik** | `raporlar_index.yonetici_liderlik` | Raporlar merkezinde 'yonetici_liderlik' raporuna giden kısayol kartı. |
| `RP06` | **raporlar_yonetici_liderlik.yoneticiler_karti** | `raporlar_yonetici_liderlik.yoneticiler_karti` | Yöneticiler Kartı — rapor kartı. |


### 🎴 Operasyon İstatistikleri Bileşeni Kartları (`rapor_operasyon_istatistik_grubu`)
**Bileşen:** Operasyon İstatistikleri | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RP47` | **Toplam PG** | `raporlar_operasyon_istatistik.toplam_pg` | Toplam PG — rapor kartı. |
| `RP48` | **Toplam Faaliyet** | `raporlar_operasyon_istatistik.toplam_faaliyet` | Toplam Faaliyet — rapor kartı. |
| `RP49` | **raporlar_operasyon_istatistik.surecler** | `raporlar_operasyon_istatistik.surecler` | Süreçler — rapor kartı. |
| `RP46` | **Toplam Süreç** | `raporlar_operasyon_istatistik.toplam_surec` | Toplam Süreç — rapor kartı. |


### 🎴 Sektörel Paket Detayı Bileşeni Kartları (`rapor_sektorel_detay_grubu`)
**Bileşen:** Sektörel Paket Detayı | **Kart Sayısı:** 7

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `RPSD07` | **raporlar_sektorel_detay.paketi_uygula_bilgi** | `raporlar_sektorel_detay.paketi_uygula_bilgi` | Paketi tek tıkla uygulama özelliğinin yakında geleceğini belirten bilgilendirme kutusu. |
| `RPSD06` | **raporlar_sektorel_detay.performans_gostergeleri** | `raporlar_sektorel_detay.performans_gostergeleri` | Pakete dahil performans göstergelerini birim, hedef, periyot ve yön bilgisiyle listeler. |
| `RPSD05` | **raporlar_sektorel_detay.riskler** | `raporlar_sektorel_detay.riskler` | Pakete dahil riskleri kategori ve RPN skoruyla listeler. |
| `RPSD04` | **raporlar_sektorel_detay.surecler** | `raporlar_sektorel_detay.surecler` | Pakete dahil süreçleri kod, ad ve ağırlık bilgisiyle tablo halinde listeler. |
| `RPSD01` | **raporlar_sektorel_detay.ozet_istatistik** | `raporlar_sektorel_detay.ozet_istatistik` | Paketin strateji, süreç, PG, risk, ESG metrik sayıları ve tahmini kurulum süresini özetleyen istatistik şeridi. |
| `RPSD03` | **raporlar_sektorel_detay.stratejiler** | `raporlar_sektorel_detay.stratejiler` | Pakete dahil stratejileri ve alt stratejilerini ağırlıklarıyla listeler. |
| `RPSD02` | **raporlar_sektorel_detay.uyum_standartlari** | `raporlar_sektorel_detay.uyum_standartlari` | Paketin uyumlu olduğu regülasyon/standart etiketlerini listeler. |


### 🎴 Yapay Zeka Ayarları Bileşeni Kartları (`ai_ayarlari`)
**Bileşen:** Yapay Zeka Ayarları | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPAI01` | **sp_ai_settings.kaynak_modu** | `sp_ai_settings.kaynak_modu` | Tenant'ın Kokpitim sistem AI'sını mı yoksa kendi API anahtarını (BYOK) mı kullanacağını seçtiği kart. |
| `SPAI02` | **sp_ai_settings.api_anahtari_bilgileri** | `sp_ai_settings.api_anahtari_bilgileri` | BYOK modu seçildiğinde sağlayıcı, model, API anahtarı ve KVKK maskeleme ayarlarının girildiği kart. |


### 🎴 Mavi Okyanus Analizi Bileşeni Kartları (`mavi_okyanus_analizi`)
**Bileşen:** Mavi Okyanus Analizi | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPBO04` | **sp_blue_ocean.errc_tablosu** | `sp_blue_ocean.errc_tablosu` | Kaldır, Azalt, Yükselt ve Yarat eylemlerine göre gruplanan ERRC öğelerini gösteren tablo kartı. |
| `SPBO03` | **sp_blue_ocean.deger_egrisi** | `sp_blue_ocean.deger_egrisi` | Kurumun ve rakiplerin faktör bazlı puanlarını çizgi grafik olarak karşılaştıran değer eğrisi kartı. |
| `SPBO01` | **sp_blue_ocean.tuval_listesi** | `sp_blue_ocean.tuval_listesi` | Oluşturulan Mavi Okyanus tuvallerinin listesini gösteren kart. |
| `SPBO02` | **sp_blue_ocean.tuval_detay** | `sp_blue_ocean.tuval_detay` | Seçilen tuvalin adı, sektörü ve açıklamasını gösteren üst detay kartı. |


### 🎴 Dengeli Karne (BSC) Bileşeni Kartları (`dengeli_karne_bsc`)
**Bileşen:** Dengeli Karne (BSC) | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPBS01` | **sp_bsc.sayfa** | `sp_bsc.sayfa` | Dengeli Karne sayfasının genel başlık ve açıklama alanı; perspektif kartları bu alanın altında JS ile dinamik olarak listelenir. |
| `SPBS02` | **sp_bsc.atanmamis_gostergeler** | `sp_bsc.atanmamis_gostergeler` | Henüz bir BSC perspektifine atanmamış performans göstergelerinin listelendiği kart. |


### 🎴 Çeyreklik Değerlendirme Bileşeni Kartları (`ceyreklik_degerlendirme`)
**Bileşen:** Çeyreklik Değerlendirme | **Kart Sayısı:** 8

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPQR04` | **sp_ceyreklik_review.okr_ilerleme** | `sp_ceyreklik_review.okr_ilerleme` | OKR ortalama ilerleme yüzdesini ve objektif sayısını gösteren mini kart. |
| `SPQR03` | **sp_ceyreklik_review.strateji** | `sp_ceyreklik_review.strateji` | Aktif ana strateji ve alt strateji sayısını, bu çeyrekte eklenen yeni strateji sayısını gösteren mini kart. |
| `SPQR02` | **sp_ceyreklik_review.pg_durumu** | `sp_ceyreklik_review.pg_durumu` | Seçili dönemde PG hedef üstü oranı ve veri girişi olan PG sayısını gösteren mini kart. Veri kalitesi raporuna kısayol. |
| `SPQR01` | **sp_ceyreklik_review.donem_secici** | `sp_ceyreklik_review.donem_secici` | Değerlendirilecek yıl ve çeyreği seçip yeni değerlendirme oluşturma formu. |
| `SPQR06` | **sp_ceyreklik_review.risk** | `sp_ceyreklik_review.risk` | Açık risk sayısı ve bunların kaçının kritik olduğunu gösteren mini kart. Risk ısı haritasına kısayol. |
| `SPQR05` | **sp_ceyreklik_review.faaliyet** | `sp_ceyreklik_review.faaliyet` | Aktif faaliyet sayısı, gecikmiş faaliyet sayısı ve bu çeyrekte kapanan faaliyet sayısını gösteren mini kart. |
| `SPQR08` | **sp_ceyreklik_review.aksiyon_onerileri** | `sp_ceyreklik_review.aksiyon_onerileri` | Seçili dönemin verilerine göre otomatik üretilen aksiyon önerileri listesi. |
| `SPQR07` | **sp_ceyreklik_review.anomali** | `sp_ceyreklik_review.anomali` | Yüksek ve orta öncelikli PG anomali sayısını gösteren mini kart. ML anomali raporuna kısayol. |


### 🎴 Stratejik Plan Dönemleri Bileşeni Kartları (`sp_plan_donemleri`)
**Bileşen:** Stratejik Plan Dönemleri | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPDN02` | **sp_donemler.aktif_donem** | `sp_donemler.aktif_donem` | Kurumun o an aktif olan stratejik plan dönemini ve kapatma işlemini gösteren vurgu kartı. |
| `SPDN04` | **sp_donemler.donem_karsilastir** | `sp_donemler.donem_karsilastir` | İki stratejik plan dönemi arasındaki strateji, süreç ve KPI hedefi farklarını karşılaştıran panel kartı. |
| `SPDN03` | **sp_donemler.tum_donemler** | `sp_donemler.tum_donemler` | Tüm stratejik plan dönemlerini yıl, ad, durum ve seçim işlemiyle listeleyen tablo kartı. |
| `SPDN01` | **sp_donemler.bos_durum** | `sp_donemler.bos_durum` | Henüz plan dönemi tanımlanmadığında gösterilen, yeni dönem oluşturmaya yönlendiren boş durum kartı. |


### 🎴 SP Yönetici Paneli Bileşeni Kartları (`sp_yonetici_paneli`)
**Bileşen:** SP Yönetici Paneli | **Kart Sayısı:** 13

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPED03` | **sp_exec_dashboard.pg_hedef_ustu** | `sp_exec_dashboard.pg_hedef_ustu` | PG hedef üstü oranını ve veri girişi olan PG sayısını gösteren mini kart. Süreç & PG yönetimine kısayol. |
| `SPED13` | **sp_exec_dashboard.ai_pivot_onerileri** | `sp_exec_dashboard.ai_pivot_onerileri` | AI veya kural motoru tarafından üretilen stratejik pivot önerileri paneli (odak daraltma, sonlandırma, hızlandırma, yeni girişim, risk mitigasyon). |
| `SPED12` | **sp_exec_dashboard.otomatik_vurgular** | `sp_exec_dashboard.otomatik_vurgular` | Sağlık skoru, PG oranı, gecikme, risk ve anomali eşiklerine göre otomatik üretilen dikkat uyarıları listesi. |
| `SPED11` | **sp_exec_dashboard.strateji_siralamasi** | `sp_exec_dashboard.strateji_siralamasi` | En iyi 5 ve en düşük 5 stratejiyi PG hedef üstü oranına göre sıralayan kart çifti. |
| `SPED10` | **sp_exec_dashboard.aylik_saglik_trendi** | `sp_exec_dashboard.aylik_saglik_trendi` | Son 12 ayın PG hedef üstü oranı trendini çizgi grafikle gösteren kart. |
| `SPED09` | **sp_exec_dashboard.kvektor_gelisimi** | `sp_exec_dashboard.kvektor_gelisimi` | K-Vektör vizyon puanının günlük/aylık/çeyreklik/yıllık gelişim grafiklerini gösteren kart. |
| `SPED08` | **sp_exec_dashboard.aktif_tetikleyici** | `sp_exec_dashboard.aktif_tetikleyici` | Aktif replan tetikleyici sayısını ve son 7 günde ateşlenen tetikleyici sayısını gösteren mini kart. |
| `SPED07` | **sp_exec_dashboard.yuksek_anomali** | `sp_exec_dashboard.yuksek_anomali` | Yüksek öncelikli PG anomali sayısını gösteren mini kart. Anomali analizine kısayol. |
| `SPED06` | **sp_exec_dashboard.kritik_risk** | `sp_exec_dashboard.kritik_risk` | Açık kritik risk sayısını gösteren mini kart. Risk yönetimine kısayol. |
| `SPED05` | **sp_exec_dashboard.gecikmis_faaliyet** | `sp_exec_dashboard.gecikmis_faaliyet` | Gecikmiş faaliyet sayısını ve toplam faaliyet sayısını gösteren mini kart. Süreçlere kısayol. |
| `SPED04` | **sp_exec_dashboard.girisim_sagligi** | `sp_exec_dashboard.girisim_sagligi` | Devam eden girişimlerin ortalama ilerleme yüzdesini gösteren mini kart. Girişim listesine kısayol. |
| `SPED02` | **sp_exec_dashboard.saglik_skoru** | `sp_exec_dashboard.saglik_skoru` | Strateji sağlık skoru, aktif PG/Strateji/Girişim toplamlarını gösteren hero kart. |
| `SPED01` | **sp_exec_dashboard.ai_yonetici_ozeti** | `sp_exec_dashboard.ai_yonetici_ozeti` | Tenant genelinde AI tarafından üretilen kısa yönetici özeti şeridi. Seçili SP yılına göre güncellenir. |


### 🎴 Stratejik Girişimler Bileşeni Kartları (`stratejik_girisimler`)
**Bileşen:** Stratejik Girişimler | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPIN01` | **sp_initiatives.girisim_listesi** | `sp_initiatives.girisim_listesi` | Çok yıllık stratejik girişimlerin listesi — durum, öncelik, ilerleme yüzdesi ve bağlı projelerle birlikte gösterir. |


### 🎴 Yapay Zeka Kullanım Raporu Bileşeni Kartları (`ai_kullanim_raporu`)
**Bileşen:** Yapay Zeka Kullanım Raporu | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPLU02` | **sp_llm_usage.son_cagrilar** | `sp_llm_usage.son_cagrilar` | Kuruma ait en son yapay zeka API çağrılarının tarih, uç nokta, model, token ve durum bilgilerini listeler. |
| `SPLU01` | **sp_llm_usage.kota_ozeti** | `sp_llm_usage.kota_ozeti` | Bu kurumun günlük ve aylık yapay zeka çağrı/maliyet kotalarını özetleyen kartlar. |


### 🎴 OKR Yönetimi Bileşeni Kartları (`okr_yonetimi`)
**Bileşen:** OKR Yönetimi | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPOK01` | **sp_okr.ozet** | `sp_okr.ozet` | Toplam hedef sayısı, toplam anahtar sonuç sayısı ve tüm hedeflerin ortalama ilerleme yüzdesini gösteren özet şeridi. |
| `SPOK02` | **sp_okr.hedef_karti** | `sp_okr.hedef_karti` | Tek bir hedefi (Objective), açıklamasını, sorumlusunu, bağlı stratejisini ve altındaki anahtar sonuçların ilerleme çubuklarını gösteren kart. |


### 🎴 Yeniden Planlama Tetikleyicileri Bileşeni Kartları (`yeniden_planlama_tetikleyicileri`)
**Bileşen:** Yeniden Planlama Tetikleyicileri | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPRT01` | **sp_replan_triggers.aktif_tetikleyiciler** | `sp_replan_triggers.aktif_tetikleyiciler` | Tanımlanmış ve aktif olan yeniden planlama tetikleyicilerinin listesini gösterir. |
| `SPRT02` | **sp_replan_triggers.son_ateslemeler** | `sp_replan_triggers.son_ateslemeler` | Tetikleyicilerin en son ne zaman ve hangi aksiyonla ateşlendiğini gösteren olay kaydı. |


### 🎴 Senaryo Planlama Bileşeni Kartları (`senaryo_planlama`)
**Bileşen:** Senaryo Planlama | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPSK02` | **sp_scenarios_kiyas.vizyon_skoru_karsilastirma** | `sp_scenarios_kiyas.vizyon_skoru_karsilastirma` | Seçilen plan yılları/senaryoların vizyon skorlarını çubuk grafikle ve what-if harman kaydırıcısıyla karşılaştıran sonuç kartı. |
| `SPSC02` | **sp_scenarios.senaryo_listesi** | `sp_scenarios.senaryo_listesi` | Mevcut plan yılları ve bunlara bağlı senaryo dallarının listelendiği kart. |
| `SPSC01` | **sp_scenarios.senaryo_olustur** | `sp_scenarios.senaryo_olustur` | Kaynak plan yılı ve senaryo etiketi seçilerek yeni bir senaryo dalı oluşturulan form kartı. |
| `SPSK01` | **sp_scenarios_kiyas.secim_listesi** | `sp_scenarios_kiyas.secim_listesi` | Karşılaştırmaya dahil edilecek plan yılı ve senaryoların seçildiği liste kartı. |


### 🎴 Yeni Plan Yılı Sihirbazı Bileşeni Kartları (`yeni_plan_yili_sihirbazi`)
**Bileşen:** Yeni Plan Yılı Sihirbazı | **Kart Sayısı:** 3

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPWZ01` | **sp_sihirbaz_yeni_yil.yil_secimi** | `sp_sihirbaz_yeni_yil.yil_secimi` | Kaynak (taşınacak verilerin bulunduğu) yıl ile hedef (yeni) plan yılının ve isteğe bağlı adının seçildiği kart. |
| `SPWZ03` | **sp_sihirbaz_yeni_yil.sonuc** | `sp_sihirbaz_yeni_yil.sonuc` | Yıl geçiş işleminin tamamlandığını ve sonucunu gösteren kart. |
| `SPWZ02` | **sp_sihirbaz_yeni_yil.onizleme** | `sp_sihirbaz_yeni_yil.onizleme` | Seçilen yıllar arasında taşınacak süreç ve KPI sayılarını özetleyen önizleme kartı. |


### 🎴 Strateji-Proje Hizalama Matrisi Bileşeni Kartları (`strateji_proje_hizalama_matrisi`)
**Bileşen:** Strateji-Proje Hizalama Matrisi | **Kart Sayısı:** 8

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPSM02` | **sp_strategy_project_matrix.hizalama_matrisi** | `sp_strategy_project_matrix.hizalama_matrisi` | Stratejiler ile projeler arasındaki bağ sayısını ısı haritası olarak gösteren ana matris tablosu. |
| `SPSM03` | **sp_strategy_project_matrix.ozet_strateji** | `sp_strategy_project_matrix.ozet_strateji` | Toplam ana strateji sayısını gösteren özet kartı. |
| `SPSM05` | **sp_strategy_project_matrix.ozet_en_guclu_hizalama** | `sp_strategy_project_matrix.ozet_en_guclu_hizalama` | Matristeki en yüksek hizalama (bağ) değerini gösteren özet kartı. |
| `SPSM08` | **sp_strategy_project_matrix.stratejisi_olmayan_projeler** | `sp_strategy_project_matrix.stratejisi_olmayan_projeler` | Kendisine bağlı proje bulunmayan stratejilerin listesini gösteren uyarı kartı. |
| `SPSM01` | **sp_strategy_project_matrix.nasil_okunur** | `sp_strategy_project_matrix.nasil_okunur` | Matrisin nasıl okunacağını açıklayan bilgilendirme kartı. |
| `SPSM07` | **sp_strategy_project_matrix.hizalanmamis_projeler** | `sp_strategy_project_matrix.hizalanmamis_projeler` | Herhangi bir stratejiye bağlanmamış projelerin listesini gösteren uyarı kartı. |
| `SPSM04` | **sp_strategy_project_matrix.ozet_proje** | `sp_strategy_project_matrix.ozet_proje` | Toplam proje sayısını gösteren özet kartı. |
| `SPSM06` | **sp_strategy_project_matrix.ozet_hizalama_kapsama** | `sp_strategy_project_matrix.ozet_hizalama_kapsama` | Boş olmayan hücre yüzdesiyle genel hizalama kapsamını gösteren özet kartı. |


### 🎴 Strateji Haritası Bileşeni Kartları (`strateji_haritasi`)
**Bileşen:** Strateji Haritası | **Kart Sayısı:** 6

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SP18` | **sp_strateji_haritasi.str_girisim** | `sp_strateji_haritasi.str_girisim` | Str. Girişim — strateji haritası kartı. |
| `SP14` | **sp_strateji_haritasi.ana_strateji** | `sp_strateji_haritasi.ana_strateji` | Ana Strateji — strateji haritası kartı. |
| `SP15` | **sp_strateji_haritasi.alt_strateji** | `sp_strateji_haritasi.alt_strateji` | Alt Strateji — strateji haritası kartı. |
| `SP16` | **sp_strateji_haritasi.surec** | `sp_strateji_haritasi.surec` | Süreç — strateji haritası kartı. |
| `SP17` | **sp_strateji_haritasi.pg** | `sp_strateji_haritasi.pg` | PG — strateji haritası kartı. |
| `SP19` | **sp_strateji_haritasi.strateji_haritasi** | `sp_strateji_haritasi.strateji_haritasi` | Strateji Haritası — strateji haritası kartı. |


### 🎴 Plan Şablonları Bileşeni Kartları (`plan_sablonlari`)
**Bileşen:** Plan Şablonları | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPTM01` | **sp_templates.sablon_karti** | `sp_templates.sablon_karti` | Sektör, süre, strateji/KPI sayısı ve uygula butonunu gösteren tek bir hazır plan şablonu kartı. |


### 🎴 Savaş Odası TV Panosu Bileşeni Kartları (`savas_odasi_tv_panosu`)
**Bileşen:** Savaş Odası TV Panosu | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPTV01` | **sp_tv.sayfa** | `sp_tv.sayfa` | Tüm sayfayı kapsayan tek kart: canlı verilerle beslenen, otomatik dönen sahnelerden oluşan Savaş Odası TV panosu. |


### 🎴 Hoshin X-Matrix Bileşeni Kartları (`hoshin_x_matrix`)
**Bileşen:** Hoshin X-Matrix | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SPXM01` | **sp_xmatrix.sayfa** | `sp_xmatrix.sayfa` | Strateji, alt strateji, girişim ve PG eksenlerini tek tabloda birleştiren Hoshin Kanri X-Matrix görünümü. |


### 🎴 Anomali Tespiti Bileşeni Kartları (`anomali_tespiti`)
**Bileşen:** Anomali Tespiti | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `AN05` | **analiz.anomali_ozet** | `analiz.anomali_ozet` | Seçili süreçte tespit edilen anomali sayısını gösteren kart. |
| `AN08` | **analiz.anomali_listesi** | `analiz.anomali_listesi` | Taranan süreç veya süreçlerde tespit edilen anomalilerin listelendiği kart. |


### 🎴 Süreç Sağlık Skoru Bileşeni Kartları (`surec_saglik_skoru`)
**Bileşen:** Süreç Sağlık Skoru | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `AN02` | **analiz.saglik_skoru** | `analiz.saglik_skoru` | Seçili sürecin genel sağlık skorunu gösteren kart. |


### 🎴 Trend ve Tahmin Analizi Bileşeni Kartları (`trend_tahmin_analizi`)
**Bileşen:** Trend ve Tahmin Analizi | **Kart Sayısı:** 4

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `AN07` | **analiz.tahmin_grafigi** | `analiz.tahmin_grafigi` | Önümüzdeki 3 dönem için yapılan tahminleri grafik olarak gösteren kart. |
| `AN06` | **analiz.trend_grafigi** | `analiz.trend_grafigi` | Sürecin zaman içindeki performans trendini grafik olarak gösteren ve Excel'e aktarma imkanı sunan kart. |
| `AN04` | **analiz.tahmin_ozet** | `analiz.tahmin_ozet` | Önümüzdeki dönem için hesaplanan tahmin değerini gösteren kart. |
| `AN03` | **analiz.trend_yonu** | `analiz.trend_yonu` | Seçili sürecin son dönemdeki trend yönünü özetleyen kart. |


### 🎴 API Erişimi Bileşeni Kartları (`api_erisimi`)
**Bileşen:** API Erişimi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `APD01` | **api_docs.endpoint_listesi** | `api_docs.endpoint_listesi` | Tüm REST API endpoint'lerini metod, URL ve açıklama sütunlarıyla gösteren tablo kartı. |


### 🎴 Kurum Takvimi Bileşeni Kartları (`kurum_takvimi`)
**Bileşen:** Kurum Takvimi | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `CA01` | **calendar.kurum_takvimi** | `calendar.kurum_takvimi` | Süreç faaliyeti, proje görevi ve kişisel etkinlikleri renklerle ayırarak gösteren kurum takvimi. |


### 🎴 K-Vektör Vizyon Skoru Bileşeni Kartları (`k_vektor_vizyon_skoru`)
**Bileşen:** K-Vektör Vizyon Skoru | **Kart Sayısı:** 2

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `KUA03` | **kurum_ayarlar.k_vektor** | `kurum_ayarlar.k_vektor` | Vizyon skorunu hiyerarşik olarak hesaplayan K-Vektör özelliğinin açılıp kapatıldığı kart. |
| `SP03` | **sp.k_vektor_vizyon** | `sp.k_vektor_vizyon` | K-Vektör, ağırlıklandırılmış strateji + alt strateji + PG performansından üretilen 0–100 ölçekli bütüncül skordur. Vizyonun ne kadarına yaklaştığınızı tek sayıyla özetler.

Hesap; ana strateji ağırlığı × alt strateji ağırlığı × PG performansı çarpımının toplamına dayanır. Yüksek puan stratejik hizalama ve gerçekleşme uyumunu gösterir. |


### 🎴 Bireysel Hedef Hizalama Bileşeni Kartları (`bireysel_hedef_hizalama`)
**Bileşen:** Bireysel Hedef Hizalama | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SP13` | **sp.bireysel_hedefler** | `sp.bireysel_hedefler` | Kurumsal hedeflerin bireysel düzeyde karşılığı burada izlenir. Çalışanların rolüne uygun hedefler; performans görüşmeleri ve gelişim planlarıyla ilişkilendirilebilir.

Amaç; kurum stratejisi ile kişisel katkıyı hizalamaktır. |


### 🎴 Vizyon Kartı Bileşeni Kartları (`vizyon_karti`)
**Bileşen:** Vizyon Kartı | **Kart Sayısı:** 1

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `SP08` | **sp.vizyon** | `sp.vizyon` | Vizyon; kurumun orta-uzun vadede ulaşmak istediği istenen durumu ifade eder. Misyonun “ne iş yapıyoruz?” sorusuna karşılık, vizyon “nereye evrilmek istiyoruz?” sorusuna yanıt verir.

İyi bir vizyon, ekiplere yön verir ve önceliklendirme yapmayı kolaylaştırır. |


### 🎴 Bileşensiz / Genel Kartlar Bileşeni Kartları (`general`)
**Bileşen:** Bileşensiz / Genel Kartlar | **Kart Sayısı:** 27

| Kısa Kod | Kart Adı | Kart Kodu | Veritabanı Açıklaması (i-butonu içeriği) |
| :--- | :--- | :--- | :--- |
| `AY01` | **ayarlar.kullanici_ozeti** | `ayarlar.kullanici_ozeti` | Oturum açan kullanıcının e-posta adresi ve rolünü özetleyen kart. |
| `AUP03` | **auth_profil.iki_faktorlu_dogrulama** | `auth_profil.iki_faktorlu_dogrulama` | Hesap için iki faktörlü kimlik doğrulamayı (2FA) etkinleştirme/devre dışı bırakma kartı. |
| `AY02` | **ayarlar.kurum_ozeti** | `ayarlar.kurum_ozeti` | Kullanıcının bağlı olduğu kurumun adını ve kurum numarasını gösteren kart. |
| `AUP02` | **auth_profil.kisisel_bilgiler** | `auth_profil.kisisel_bilgiler` | Kullanıcının ad, soyad, e-posta, telefon, unvan, departman bilgilerini ve şifresini düzenlediği kart. |
| `AUA01` | **auth_ayarlar.bildirim_ayarlari** | `auth_ayarlar.bildirim_ayarlari` | E-posta, süreç, görev ve son tarih bildirimlerinin açık/kapalı durumunu ayarlayan kart. |
| `AUP01` | **auth_profil.profil_ozeti** | `auth_profil.profil_ozeti` | Kullanıcının profil fotoğrafı, adı ve rolünü gösteren özet kartı. |
| `AUA03` | **auth_ayarlar.gorunum** | `auth_ayarlar.gorunum` | Karanlık mod ve genel görünüm tercihlerine dair bilgi veren kart. |
| `AUA02` | **auth_ayarlar.dil_ve_bolge** | `auth_ayarlar.dil_ve_bolge` | Arayüz dili, saat dilimi ve tarih formatı tercihlerinin seçildiği kart. |
| `AY03` | **ayarlar.tema_durumu** | `ayarlar.tema_durumu` | Aktif görünüm temasını (aydınlık/karanlık) ve cihazlar arası senkron durumunu gösteren kart. |
| `BI01` | **bildirim.liste** | `bildirim.liste` | Kullanıcıya ait tüm bildirimlerin okunma durumuna göre listelendiği kart. |
| `BR202` | **bireysel_karne.ust_bar** | `bireysel_karne.ust_bar` | Sayfa başlığı, alt açıklama ve görüntülenecek yılı seçme alanını içeren üst bar. |
| `KRAN04` | **k_rapor_anomalies.bos_durum** | `k_rapor_anomalies.bos_durum` | Hiç anomali bulunamadığında gösterilen, tüm KPI'ların normal aralıkta olduğunu belirten bilgi kartı. |
| `KUA01` | **kurum_ayarlar.kurum_bilgileri** | `kurum_ayarlar.kurum_bilgileri` | Kurum adı, sektör ve vergi numarası gibi temel kurum bilgilerinin düzenlendiği kart. |
| `KUA02` | **kurum_ayarlar.iletisim** | `kurum_ayarlar.iletisim` | Kurumun adres, telefon, e-posta ve web sitesi iletişim bilgilerinin girildiği kart. |
| `KUA05` | **kurum_ayarlar.kurum_logosu** | `kurum_ayarlar.kurum_logosu` | Kurum logosunun görüntülendiği ve yeni logo yüklenebildiği kart. |
| `KDH04` | **k_radar_hub.grup_strateji** | `k_radar_hub.grup_strateji` | K-Radar hub'ında çapraz stratejik analiz araçları grubu (A3, anket, paydaş, rekabet). |
| `KDH03` | **k_radar_hub.grup_risk** | `k_radar_hub.grup_risk` | K-Radar hub'ında risk yönetimi araçları grubu. |
| `KDH02` | **k_radar_hub.grup_yurutme** | `k_radar_hub.grup_yurutme` | K-Radar hub'ında yürütme takip araçları grubu (KPR — proje/kaynak/risk yürütme raporları). |
| `RPI18` | **raporlar_index.op_istatistik** | `raporlar_index.op_istatistik` | Raporlar merkezinde 'op_istatistik' raporuna giden kısayol kartı. |
| `KDH01` | **k_radar_hub.grup_performans** | `k_radar_hub.grup_performans` | K-Radar hub'ında performans ölçüm araçları grubu (5 boyutta süreç sağlığı, KP-Radar vb.). |
| `SPVZ01` | **sp_vizyon.vizyon** | `sp_vizyon.vizyon` | Kurumun vizyon ifadesini gösteren kart; şu an yapım aşamasında. |
| `SPDG01` | **sp_degerler.sayfa** | `sp_degerler.sayfa` | Değerler ve Etik Kurallar sayfasının tamamını temsil eden kart; içerik henüz yapım aşamasındadır. |
| `AN01` | **analiz.secim_araclari** | `analiz.secim_araclari` | Analiz edilecek sürecin seçildiği ve trend frekansı, tahmin yöntemi gibi analiz araçlarının bulunduğu kontrol çubuğu. |
| `ADLK01` | **admin_loglar_kurum.kategoriler** | `admin_loglar_kurum.kategoriler` | *Açıklama girilmemiş* |
| `ADA05` | **admin_araclar.yeni_arac_yer_tutucu** | `admin_araclar.yeni_arac_yer_tutucu` | İleride eklenecek yeni yönetim araçları için ayrılmış boş yer tutucu kart. |
| `SP10` | **sp.strateji_agirlik_skor_gorsellestirme** | `sp.strateji_agirlik_skor_gorsellestirme` | *Açıklama girilmemiş* |
| `KDH05` | **k_radar_hub.grup_ai** | `k_radar_hub.grup_ai` | K-Radar hub'ında AI destekli rapor ve araçlar grubu. |

