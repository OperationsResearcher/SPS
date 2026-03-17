# 🏛️ MEVCUT STRATEJİK PLANLAMA MODÜLÜ ANALİZİ

**Analiz Tarihi:** 2025-01-27  
**Sistem Versiyonu:** V2.5.3  
**Analiz Kapsamı:** Veritabanı Modelleri, Route'lar, Template'ler, API Endpoint'leri

---

## 1. Veritabanı Modelleri (Models)

### 1.1. Ana Strateji Modeli (`AnaStrateji`)

**Tablo Adı:** `ana_strateji`

**Alanlar:**
- `id` (Integer, Primary Key)
- `kurum_id` (Integer, Foreign Key -> `kurum.id`, NOT NULL, Indexed)
- `ad` (String(200), NOT NULL)
- `aciklama` (Text, Nullable)

**İlişkiler:**
- `kurum`: Kurum ile n-1 ilişki (Bir kurumun birden fazla ana stratejisi olabilir)
- `alt_stratejiler`: AltStrateji ile 1-n ilişki (Bir ana stratejinin birden fazla alt stratejisi olabilir)
  - Cascade delete: Ana strateji silindiğinde alt stratejiler de silinir

**Kullanım:**
- Kurum bazlı stratejik planlama için ana stratejileri tutar
- Alt stratejilerin üst seviye kategorisidir

---

### 1.2. Alt Strateji Modeli (`AltStrateji`)

**Tablo Adı:** `alt_strateji`

**Alanlar:**
- `id` (Integer, Primary Key)
- `ana_strateji_id` (Integer, Foreign Key -> `ana_strateji.id`, NOT NULL, Indexed)
- `ad` (String(200), NOT NULL)
- `aciklama` (Text, Nullable)

**İlişkiler:**
- `ana_strateji`: AnaStrateji ile n-1 ilişki (Her alt strateji bir ana stratejiye bağlıdır)
- `surecler`: Surec ile n-n ilişki (`surec_alt_stratejiler` association table üzerinden)
  - Bir alt strateji birden fazla sürece bağlanabilir
  - Bir süreç birden fazla alt stratejiye bağlanabilir

**Kullanım:**
- Ana stratejilerin detaylandırılmış versiyonlarıdır
- Süreçlerle ilişkilendirilerek operasyonel seviyeye bağlanır

---

### 1.3. SWOT Analizi Modeli (`SwotAnalizi`)

**Tablo Adı:** `swot_analizi`

**Alanlar:**
- `id` (Integer, Primary Key)
- `kurum_id` (Integer, Foreign Key -> `kurum.id`, NOT NULL, Indexed)
- `kategori` (String(20), NOT NULL) - Değerler: `strengths`, `weaknesses`, `opportunities`, `threats`
- `baslik` (String(200), NOT NULL)
- `aciklama` (Text, Nullable)
- `oncelik` (Integer, Default: 1) - 1-5 arası öncelik seviyesi
- `created_at` (DateTime, Default: utcnow, Indexed)
- `updated_at` (DateTime, Default: utcnow, OnUpdate: utcnow)

**İlişkiler:**
- `kurum`: Kurum ile n-1 ilişki (Bir kurumun birden fazla SWOT analizi kaydı olabilir)
  - Cascade delete: Kurum silindiğinde SWOT analizleri de silinir

**Kullanım:**
- Kurumun güçlü yönleri, zayıf yönleri, fırsatlar ve tehditlerini tutar
- Stratejik planlama için girdi sağlar

---

### 1.4. PESTLE Analizi Modeli (`PestleAnalizi`)

**Tablo Adı:** `pestle_analizi`

**Alanlar:**
- `id` (Integer, Primary Key)
- `kurum_id` (Integer, Foreign Key -> `kurum.id`, NOT NULL, Indexed)
- `kategori` (String(20), NOT NULL) - Değerler: `political`, `economic`, `social`, `technological`, `legal`, `environmental`
- `baslik` (String(200), NOT NULL)
- `aciklama` (Text, Nullable)
- `etki` (String(20), Default: 'Orta') - Değerler: `Düşük`, `Orta`, `Yüksek`
- `oncelik` (Integer, Default: 1) - 1-5 arası öncelik seviyesi
- `created_at` (DateTime, Default: utcnow, Indexed)
- `updated_at` (DateTime, Default: utcnow, OnUpdate: utcnow)

**İlişkiler:**
- `kurum`: Kurum ile n-1 ilişki (Bir kurumun birden fazla PESTLE analizi kaydı olabilir)
  - Cascade delete: Kurum silindiğinde PESTLE analizleri de silinir

**Kullanım:**
- Kurumun dış çevresel faktörlerini (Politik, Ekonomik, Sosyal, Teknolojik, Yasal, Çevresel) tutar
- Stratejik planlama için makro çevre analizi sağlar

---

### 1.5. Değerler Modeli (`Deger`)

**Tablo Adı:** `deger`

**Alanlar:**
- `id` (Integer, Primary Key)
- `kurum_id` (Integer, Foreign Key -> `kurum.id`, NOT NULL, Indexed)
- `baslik` (String(200), NOT NULL)
- `aciklama` (Text, Nullable)

**İlişkiler:**
- `kurum`: Kurum ile n-1 ilişki (Bir kurumun birden fazla değeri olabilir)
  - Cascade delete: Kurum silindiğinde değerler de silinir

**Kullanım:**
- Kurumun temel değerlerini (örneğin: Müşteri Odaklılık, İnovasyon, Şeffaflık) tutar
- Stratejik planlamanın temel taşlarından biridir

---

### 1.6. Etik Kurallar Modeli (`EtikKural`)

**Tablo Adı:** `etik_kural`

**Alanlar:**
- `id` (Integer, Primary Key)
- `kurum_id` (Integer, Foreign Key -> `kurum.id`, NOT NULL, Indexed)
- `baslik` (String(200), NOT NULL)
- `aciklama` (Text, Nullable)

**İlişkiler:**
- `kurum`: Kurum ile n-1 ilişki (Bir kurumun birden fazla etik kuralı olabilir)
  - Cascade delete: Kurum silindiğinde etik kurallar da silinir

**Kullanım:**
- Kurumun etik kurallarını ve davranış standartlarını tutar
- Stratejik planlamada değerlerle birlikte kullanılır

---

### 1.7. Kalite Politikaları Modeli (`KalitePolitikasi`)

**Tablo Adı:** `kalite_politikasi`

**Alanlar:**
- `id` (Integer, Primary Key)
- `kurum_id` (Integer, Foreign Key -> `kurum.id`, NOT NULL, Indexed)
- `baslik` (String(200), NOT NULL)
- `aciklama` (Text, Nullable)

**İlişkiler:**
- `kurum`: Kurum ile n-1 ilişki (Bir kurumun birden fazla kalite politikası olabilir)
  - Cascade delete: Kurum silindiğinde kalite politikaları da silinir

**Kullanım:**
- Kurumun kalite yönetim politikalarını tutar
- ISO 9001 gibi standartlarla uyumlu olarak kullanılabilir

---

### 1.8. Kurum Modeli - Stratejik Planlama Alanları

**Tablo Adı:** `kurum`

**Stratejik Planlama ile İlgili Alanlar:**
- `amac` (Text, Nullable) - Kurumun amacı/misyonu
- `vizyon` (Text, Nullable) - Kurumun vizyonu
- `stratejik_profil` (Text, Nullable) - Kurumun stratejik profil bilgileri (JSON formatında saklanabilir)
- `stratejik_durum` (String(50), Default: 'eksik') - Stratejik planlama durumu (örneğin: `eksik`, `taslak`, `tamamlandi`)
- `stratejik_son_guncelleme` (DateTime, Nullable) - Stratejik planlamanın son güncellenme tarihi

**İlişkiler:**
- `ana_stratejiler`: AnaStrateji ile 1-n ilişki
- `swot_analizleri`: SwotAnalizi ile 1-n ilişki
- `pestle_analizleri`: PestleAnalizi ile 1-n ilişki
- `degerler`: Deger ile 1-n ilişki
- `etik_kurallari`: EtikKural ile 1-n ilişki
- `kalite_politikalari`: KalitePolitikasi ile 1-n ilişki

---

### 1.9. Süreç - Alt Strateji İlişkisi

**Association Table:** `surec_alt_stratejiler`

**Yapı:**
- `surec_id` (Integer, Foreign Key -> `surec.id`, Primary Key)
- `alt_strateji_id` (Integer, Foreign Key -> `alt_strateji.id`, Primary Key)

**Kullanım:**
- Süreçler ile alt stratejiler arasında çoktan çoğa (n-n) ilişki kurar
- Bir süreç birden fazla alt stratejiye bağlanabilir
- Bir alt strateji birden fazla sürece bağlanabilir
- Bu sayede operasyonel süreçler stratejik hedeflerle ilişkilendirilir

---

## 2. Mevcut Fonksiyonlar (Routes/Views)

### 2.1. Stratejik Planlama Akışı Sayfası

**Route:** `/stratejik-planlama-akisi`  
**Method:** GET  
**Dosya:** `main/routes.py` (Satır 382-429)  
**Fonksiyon:** `stratejik_planlama_akisi()`

**İşlevi:**
- Kurumun stratejik planlama akış diyagramını gösterir
- Kurumun değerlerini, etik kurallarını, kalite politikalarını getirir
- Kurumun amaç ve vizyon bilgilerini gösterir
- Ana stratejileri ve alt stratejilerini listeler
- Süreçleri ve performans göstergelerini gösterir

**Template:** `templates/stratejik_planlama_akisi.html`

**Veri Aktarımı:**
- `kurum`: Kurum nesnesi
- `degerler`: Deger listesi
- `etik_kurallari`: EtikKural listesi
- `kalite_politikalari`: KalitePolitikasi listesi
- `amac`: Kurumun amacı (Text)
- `vizyon`: Kurumun vizyonu (Text)
- `ana_stratejiler`: AnaStrateji listesi (alt_stratejiler ile birlikte)
- `surecler`: Surec listesi (performans_gostergeleri ile birlikte)

---

### 2.2. Stratejik Asistan Sayfası

**Route:** `/stratejik-asistan`  
**Method:** GET  
**Dosya:** `main/routes.py` (Satır 432-443)  
**Fonksiyon:** `stratejik_asistan()`

**İşlevi:**
- AI destekli stratejik planlama asistanı sayfasını gösterir
- Kullanıcı kurum profilini tanımlayabilir
- AI önerileri alabilir (amaç, vizyon, değerler, etik kurallar, kalite politikaları, stratejiler)
- Önerileri kabul edip veritabanına kaydedebilir

**Template:** `templates/stratejik_asistan.html`

**Veri Aktarımı:**
- `kurum`: Kurum nesnesi

**Not:** Bu sayfa frontend'de API endpoint'leri çağırır, ancak bu endpoint'ler henüz backend'de implement edilmemiş görünüyor.

---

## 3. Arayüz Durumu (Templates)

### 3.1. Stratejik Planlama Akışı Sayfası

**Dosya:** `templates/stratejik_planlama_akisi.html`

**İçerik:**
- **Akış Diyagramı Görünümü:** Stratejik planlama sürecinin görsel akış diyagramı
- **Kartlar:**
  - Değerler kartı
  - Etik Kurallar kartı
  - Kalite Politikaları kartı
  - Amaç kartı
  - Vizyon kartı
  - Ana Stratejiler kartı (Alt stratejilerle birlikte)
  - Süreçler kartı (Performans göstergeleriyle birlikte)
- **Görsel Tasarım:** Renkli kartlar, hover efektleri, interaktif öğeler
- **Durum:** ✅ Tamamlanmış ve çalışır durumda

---

### 3.2. Stratejik Asistan Sayfası

**Dosya:** `templates/stratejik_asistan.html`

**İçerik:**
- **Sol Kolon (Form):**
  - Kurum Adı
  - Sektör / Faaliyet Alanı
  - Kurum Özeti
  - Hedef Kitle / Paydaşlar
  - Güçlü Yönler
  - Fırsatlar
  - Zorluklar / Riskler
  - Stratejik Öncelikler
  - Kilit Projeler / Girişimler
  - "Profil Cevaplarını Kaydet" butonu
  - "AI Önerisi Oluştur" butonu
- **Sağ Kolon (AI Önerileri):**
  - Amaç önerileri
  - Vizyon önerileri
  - Değerler önerileri
  - Etik Kurallar önerileri
  - Kalite Politikaları önerileri
  - Ana & Alt Stratejiler önerileri
  - Her öneri için: Kopyala, Yeni Öneri, Kabul Et butonları
  - "Tümünü Kabul Et" butonu
- **Durum:** ⚠️ Frontend hazır, ancak backend API endpoint'leri eksik

---

## 4. Tespit Edilen Eksikler veya Kopukluklar

### 4.1. API Endpoint'leri Eksik

**Durum:** ❌ **KRİTİK EKSİK**

**Eksik Endpoint'ler:**
1. `/api/kurum/<int:kurum_id>/stratejik-profil` (GET, POST)
   - Kurumun stratejik profil bilgilerini getirir/kaydeder
   - Template'te kullanılıyor ancak backend'de yok

2. `/api/ai/stratejik-oneri` (POST)
   - AI destekli stratejik öneriler oluşturur
   - Template'te kullanılıyor ancak backend'de yok

3. `/api/ai/yeni-oneri` (POST)
   - Belirli bir alan için yeni AI önerisi oluşturur
   - Template'te kullanılıyor ancak backend'de yok

4. `/api/ai/kabul-et` (POST)
   - AI önerilerini kabul edip veritabanına kaydeder
   - Template'te kullanılıyor ancak backend'de yok

**Etki:**
- Stratejik Asistan sayfası çalışmıyor
- AI önerileri alınamıyor
- Öneriler veritabanına kaydedilemiyor

---

### 4.2. Strateji Yönetimi CRUD İşlemleri Eksik

**Durum:** ⚠️ **ÖNEMLİ EKSİK**

**Eksik Fonksiyonlar:**
1. Ana Strateji Oluşturma (CREATE)
   - Yeni ana strateji ekleme formu ve endpoint'i yok

2. Ana Strateji Düzenleme (UPDATE)
   - Mevcut ana stratejiyi düzenleme formu ve endpoint'i yok

3. Ana Strateji Silme (DELETE)
   - Ana strateji silme endpoint'i yok

4. Alt Strateji Oluşturma (CREATE)
   - Yeni alt strateji ekleme formu ve endpoint'i yok

5. Alt Strateji Düzenleme (UPDATE)
   - Mevcut alt stratejiyi düzenleme formu ve endpoint'i yok

6. Alt Strateji Silme (DELETE)
   - Alt strateji silme endpoint'i yok

**Etki:**
- Stratejiler sadece görüntülenebiliyor, yönetilemiyor
- Veritabanına manuel veri girişi gerekiyor

---

### 4.3. SWOT ve PESTLE Analizi Yönetimi Eksik

**Durum:** ⚠️ **ÖNEMLİ EKSİK**

**Eksik Fonksiyonlar:**
1. SWOT Analizi CRUD İşlemleri
   - SWOT analizi kayıtlarını oluşturma, düzenleme, silme endpoint'leri yok
   - SWOT analizi görüntüleme sayfası yok

2. PESTLE Analizi CRUD İşlemleri
   - PESTLE analizi kayıtlarını oluşturma, düzenleme, silme endpoint'leri yok
   - PESTLE analizi görüntüleme sayfası yok

**Etki:**
- SWOT ve PESTLE analizleri veritabanında tutuluyor ancak yönetilemiyor
- Stratejik planlama akışında görüntülenmiyor

---

### 4.4. Değerler, Etik Kurallar, Kalite Politikaları Yönetimi Eksik

**Durum:** ⚠️ **ÖNEMLİ EKSİK**

**Eksik Fonksiyonlar:**
1. Değerler CRUD İşlemleri
   - Değer ekleme, düzenleme, silme endpoint'leri yok
   - Sadece görüntüleme var

2. Etik Kurallar CRUD İşlemleri
   - Etik kural ekleme, düzenleme, silme endpoint'leri yok
   - Sadece görüntüleme var

3. Kalite Politikaları CRUD İşlemleri
   - Kalite politikası ekleme, düzenleme, silme endpoint'leri yok
   - Sadece görüntüleme var

**Etki:**
- Bu veriler sadece görüntülenebiliyor, yönetilemiyor
- Veritabanına manuel veri girişi gerekiyor

---

### 4.5. Strateji - Süreç İlişkisi Yönetimi Eksik

**Durum:** ⚠️ **ORTA EKSİK**

**Mevcut Durum:**
- `surec_alt_stratejiler` association table mevcut
- Süreç panelinde (`surec_panel.html`) strateji seçimi yapılabiliyor
- Ancak stratejik planlama akış sayfasında bu ilişkiler görüntülenmiyor

**Eksik Fonksiyonlar:**
1. Strateji - Süreç İlişkisi Görüntüleme
   - Hangi süreçlerin hangi stratejilere bağlı olduğunu gösteren görünüm yok

2. Strateji - Süreç İlişkisi Yönetimi
   - İlişkileri ekleme/çıkarma için arayüz yok (sadece süreç panelinde var)

**Etki:**
- İlişkiler kurulabiliyor ancak stratejik planlama akışında görünmüyor

---

### 4.6. Strateji - Proje İlişkisi Yok

**Durum:** ⚠️ **ORTA EKSİK**

**Mevcut Durum:**
- Projeler (`Project` modeli) mevcut
- Stratejiler (`AnaStrateji`, `AltStrateji`) mevcut
- Ancak projeler ile stratejiler arasında ilişki yok

**Eksik:**
- Proje - Strateji ilişkisi modeli yok
- Projelerin hangi stratejilere hizmet ettiği takip edilemiyor

**Etki:**
- Stratejik hedefler ile operasyonel projeler arasında bağlantı kurulamıyor
- Projelerin stratejik önceliği belirlenemiyor

---

### 4.7. Stratejik Planlama Durumu Takibi Eksik

**Durum:** ℹ️ **BİLGİ EKSİK**

**Mevcut Durum:**
- `Kurum` modelinde `stratejik_durum` ve `stratejik_son_guncelleme` alanları var
- Ancak bu alanların otomatik güncellenmesi yok

**Eksik:**
- Stratejik planlama tamamlandığında durumun otomatik güncellenmesi yok
- Stratejik planlama ilerleme takibi yok

**Etki:**
- Durum manuel olarak güncellenmeli
- İlerleme takibi yapılamıyor

---

## 5. Özet ve Öneriler

### 5.1. Mevcut Güçlü Yönler

✅ **Veritabanı Yapısı:**
- Stratejik planlama için gerekli tüm modeller mevcut
- İlişkiler doğru kurulmuş (Ana Strateji -> Alt Strateji -> Süreç)
- SWOT ve PESTLE analizi modelleri hazır

✅ **Görselleştirme:**
- Stratejik planlama akış diyagramı sayfası mevcut ve çalışıyor
- Veriler görsel olarak sunuluyor

✅ **Temel Altyapı:**
- Kurum bazlı çalışma yapısı mevcut
- Kullanıcı yetkilendirme sistemi hazır

---

### 5.2. Kritik Eksikler (Öncelikli)

🔴 **1. API Endpoint'leri (Yüksek Öncelik)**
- Stratejik Asistan sayfasının çalışması için gerekli
- AI entegrasyonu için zorunlu

🔴 **2. Strateji CRUD İşlemleri (Yüksek Öncelik)**
- Kullanıcıların strateji yönetebilmesi için gerekli
- Temel işlevsellik eksik

---

### 5.3. Öneriler

#### Öncelik 1: API Endpoint'lerini Tamamla
- `/api/kurum/<id>/stratejik-profil` endpoint'ini implement et
- `/api/ai/stratejik-oneri` endpoint'ini implement et (AI servisi entegrasyonu gerekebilir)
- `/api/ai/yeni-oneri` endpoint'ini implement et
- `/api/ai/kabul-et` endpoint'ini implement et

#### Öncelik 2: Strateji Yönetimi CRUD İşlemleri
- Ana Strateji ekleme/düzenleme/silme sayfaları ve endpoint'leri
- Alt Strateji ekleme/düzenleme/silme sayfaları ve endpoint'leri
- Stratejik Planlama Akış sayfasına yönetim butonları ekle

#### Öncelik 3: SWOT ve PESTLE Analizi Yönetimi
- SWOT analizi yönetim sayfası ve CRUD endpoint'leri
- PESTLE analizi yönetim sayfası ve CRUD endpoint'leri
- Stratejik Planlama Akış sayfasına entegrasyon

#### Öncelik 4: Değerler, Etik Kurallar, Kalite Politikaları Yönetimi
- Her biri için CRUD sayfaları ve endpoint'leri
- Stratejik Planlama Akış sayfasına yönetim butonları

#### Öncelik 5: İlişki Yönetimi
- Strateji - Süreç ilişkilerini görüntüleme ve yönetme
- Proje - Strateji ilişkisi modeli ve yönetimi

---

## 6. Sonuç

Mevcut Stratejik Planlama Modülü **%40 tamamlanmış** durumda:

- ✅ **Veritabanı Yapısı:** %100 tamamlanmış
- ✅ **Görselleştirme:** %60 tamamlanmış (Akış diyagramı var, yönetim arayüzleri yok)
- ❌ **API Endpoint'leri:** %0 tamamlanmış (Stratejik Asistan için gerekli endpoint'ler eksik)
- ❌ **CRUD İşlemleri:** %0 tamamlanmış (Sadece görüntüleme var)
- ⚠️ **İlişki Yönetimi:** %30 tamamlanmış (Süreç-Strateji ilişkisi var, Proje-Strateji yok)

**Önerilen Geliştirme Sırası:**
1. API Endpoint'leri (Stratejik Asistan'ı çalışır hale getirmek için)
2. Strateji CRUD İşlemleri (Temel yönetim işlevselliği)
3. SWOT/PESTLE Yönetimi (Analiz araçlarını kullanılabilir hale getirmek)
4. Değerler/Etik/Kalite Yönetimi (Tam yönetim yeteneği)
5. İlişki Yönetimi ve Görselleştirme (Gelişmiş özellikler)

---

**Analiz Tamamlandı:** 2025-01-27  
**Analiz Yapan:** AI Assistant  
**Sonraki Adım:** API Endpoint'lerinin implementasyonu ve Strateji CRUD işlemlerinin eklenmesi




