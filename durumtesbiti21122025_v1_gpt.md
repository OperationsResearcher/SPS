# STRATEJİK PLANLAMA SİSTEMİ - DETAYLI DURUM TESPİTİ RAPORU

**Tarih:** 21 Aralık 2025  
**Versiyon:** V1.8.0  
**Rapor Tipi:** Tam Kod Tabanı Analizi + Kullanıcı Kılavuzu  
**Hazırlayan:** AI Code Reviewer (GPT)

---

## 📋 İÇİNDEKİLER

### BÖLÜM 1: SİSTEM GENEL BAKIŞ
1. [Proje Tanımı ve Amaç](#1-proje-tanımı-ve-amaç)
2. [Teknik Altyapı](#2-teknik-altyapı)
3. [Mimari Yapı](#3-mimari-yapı)

### BÖLÜM 2: MODÜLLER VE ÖZELLİKLER
4. [Kullanıcı Yönetimi](#4-kullanıcı-yönetimi)
5. [Süreç Yönetimi](#5-süreç-yönetimi)
6. [Performans Göstergeleri](#6-performans-göstergeleri)
7. [Proje Yönetimi](#7-proje-yönetimi)
8. [Executive Dashboard](#8-executive-dashboard)
9. [AI Özellikleri](#9-ai-özellikleri)
10. [Raporlama](#10-raporlama)

### BÖLÜM 3: KULLANICI KLAVUZU
11. [Rol Bazlı Kullanım Senaryoları](#11-rol-bazlı-kullanım-senaryoları)
12. [Tüm Ekranlar ve İşlemler](#12-tüm-ekranlar-ve-işlemler)
13. [API Kullanımı](#13-api-kullanımı)

### BÖLÜM 4: TEKNİK DETAYLAR
14. [Veritabanı Modelleri](#14-veritabanı-modelleri)
15. [Servis Katmanı](#15-servis-katmanı)
16. [Güvenlik](#16-güvenlik)
17. [Performans](#17-performans)

### BÖLÜM 5: TEKNİK BORÇLAR VE İYİLEŞTİRMELER
18. [Kritik Öncelikli İyileştirmeler](#18-kritik-öncelikli-iyileştirmeler)
19. [Orta Öncelikli İyileştirmeler](#19-orta-öncelikli-iyileştirmeler)
20. [Gelecek Özellikler](#20-gelecek-özellikler)

### BÖLÜM 6: DEPLOYMENT VE BAKIM
21. [Production Hazırlık](#21-production-hazırlık)
22. [Bakım ve İzleme](#22-bakım-ve-izleme)
23. [Yedekleme ve Güvenlik](#23-yedekleme-ve-güvenlik)

---

## BÖLÜM 1: SİSTEM GENEL BAKIŞ

### 1. PROJE TANIMI VE AMAÇ

#### 1.1. Sistem Adı
**Stratejik Planlama ve Performans Yönetim Sistemi (SPSV2)**

#### 1.2. Ana Amaç
Kurumların stratejik planlama süreçlerini, performans göstergelerini, süreç yönetimini ve proje yönetimini tek bir platformda entegre bir şekilde yönetmelerini sağlamak.

#### 1.3. Hedef Kullanıcı Grubu
- **Kurum Yöneticileri:** Tüm süreçleri ve performansları görüntüleyebilen üst düzey yöneticiler
- **Süreç Liderleri:** Süreç sorumluları, performans göstergesi ve faaliyet yöneticileri
- **Süreç Üyeleri:** Veri girişi yapan operasyonel personel
- **Proje Yöneticileri:** Proje ve görev yönetimi yapan ekip liderleri
- **Saha Personeli:** Mobil cihazlardan görev takibi yapan kullanıcılar

#### 1.4. Temel Değer Önerileri
- ✅ **Entegre Yönetim:** Stratejik planlama, süreç yönetimi, performans takibi ve proje yönetimi tek platformda
- ✅ **Otomatik Veri Akışı:** Proje görevleri tamamlandığında otomatik performans verisi girişi
- ✅ **AI Destekli Analizler:** Erken uyarı sistemleri, risk tahmini, stratejik öneriler
- ✅ **Executive Dashboard:** Üst yönetime özel görsel analitik ve raporlama
- ✅ **Mobil Uyumluluk:** Saha personeli için optimize edilmiş mobil arayüz
- ✅ **Esnek Periyot Yönetimi:** Günlük, haftalık, aylık, çeyreklik, yıllık veri takibi

---

### 2. TEKNİK ALTYAPI

#### 2.1. Teknoloji Stack'i

**Backend:**
- **Framework:** Flask 2.3.3 (Python Web Framework)
- **ORM:** SQLAlchemy 3.0.5 (Database ORM)
- **Authentication:** Flask-Login 0.6.3
- **Migration:** Flask-Migrate 4.0.5
- **Security:** Flask-WTF 1.2.1 (CSRF Protection)
- **Rate Limiting:** Flask-Limiter 3.5.0
- **Caching:** Flask-Caching 2.1.0

**Database:**
- **Primary:** Microsoft SQL Server (Production)
- **Fallback:** SQLite (Development/Testing)
- **Driver:** pyodbc 5.0.0 (ODBC Driver 17 for SQL Server)

**Frontend:**
- **CSS Framework:** Bootstrap 5.3.2
- **Icons:** Font Awesome 6.4.0 + Bootstrap Icons 1.11.1
- **JavaScript:** Vanilla JS (no framework dependency)
- **Charts:** Chart.js (Dashboard visualizations)

**Additional Libraries:**
- **Excel Export:** openpyxl 3.1.2
- **PDF Generation:** ReportLab 4.0.0
- **AI Integration:** google-generativeai 0.3.0
- **WSGI Server:** Waitress 3.0.0 (Production)
- **Environment Management:** python-dotenv 1.0.0

**Testing:**
- **Framework:** pytest 7.4.3
- **Coverage:** pytest-cov 4.1.0
- **Flask Testing:** pytest-flask 1.3.0

#### 2.2. Proje Yapısı

```
SP_Code/
├── api/                          # REST API Endpoints
│   └── routes.py                 # 40+ API endpoint
├── auth/                         # Authentication
│   └── routes.py                 # Login, logout, register
├── main/                         # Main Application Routes
│   └── routes.py                 # 25+ UI route
├── services/                     # Business Logic Layer
│   ├── ai_advisor_service.py     # AI Stratejik Danışman
│   ├── ai_early_warning.py       # AI Erken Uyarı
│   ├── ai_executive_summary.py   # AI Yönetici Özeti
│   ├── background_tasks.py       # Arka Plan İşlemleri
│   ├── executive_dashboard.py    # Dashboard Veri Toplama
│   ├── notification_service.py   # Bildirim Sistemi
│   ├── performance_service.py    # Performans Hesaplamaları
│   ├── project_analytics.py      # Proje Analitiği
│   ├── project_cloning.py        # Proje Klonlama
│   ├── project_service.py        # Proje İş Mantığı
│   ├── report_service.py         # PDF Raporlama
│   ├── resource_planning.py      # Kaynak Planlama
│   ├── smart_scheduling.py       # Akıllı Zamanlama
│   ├── task_activity_service.py  # Görev Aktivite
│   └── timesheet_service.py      # Zaman Takibi
├── templates/                    # Jinja2 HTML Templates
│   ├── admin_panel.html          # Admin Yönetim Paneli
│   ├── akilli_planlama.html      # Akıllı Planlama
│   ├── base.html                 # Ana Layout
│   ├── bireysel_panel.html       # Bireysel Panel
│   ├── corporate_files.html      # Kurumsal Dosyalar
│   ├── dashboard.html            # Ana Dashboard
│   ├── executive_dashboard.html  # Yönetim Kokpiti
│   ├── gorev_aktivite_log.html   # Görev Log
│   ├── kurum_panel.html          # Kurum Paneli
│   ├── login.html                # Giriş Sayfası
│   ├── profile.html              # Kullanıcı Profili
│   ├── proje_analitik.html       # Proje Analitiği
│   ├── project_detail.html       # Proje Detay
│   ├── project_form.html         # Proje Form
│   ├── project_gantt.html        # Gantt Chart
│   ├── project_list.html         # Proje Listesi
│   ├── settings.html             # Ayarlar
│   ├── stratejik_asistan.html    # Stratejik Asistan
│   ├── stratejik_planlama_akisi.html  # Planlama Akışı
│   ├── surec_karnesi.html        # Süreç Karnesi
│   ├── surec_panel.html          # Süreç Paneli
│   ├── task_form.html            # Görev Form
│   ├── zaman_takibi.html         # Zaman Takibi
│   └── errors/                   # Hata Sayfaları
│       ├── 404.html
│       └── 500.html
├── static/                       # Statik Dosyalar
│   ├── uploads/                  # Yüklenen Dosyalar
│   │   ├── logos/
│   │   └── profiles/
│   └── vendor/                   # CDN Fallback
├── tests/                        # Test Dosyaları
│   └── test_performance_service.py
├── __init__.py                   # Application Factory
├── app.py                        # Uygulama Giriş Noktası
├── config.py                     # Konfigürasyon
├── models.py                     # Database Models (971 satır)
├── extensions.py                 # Flask Extensions
├── decorators.py                 # Access Control Decorators
└── requirements.txt              # Python Dependencies
```

#### 2.3. Veritabanı Özellikleri

**Tablo Sayısı:** 30+ tablo

**Ana Tablolar:**
- `user` - Kullanıcılar
- `kurum` - Kurumlar
- `surec` - Süreçler
- `surec_performans_gostergesi` - Süreç PG'leri
- `bireysel_performans_gostergesi` - Bireysel PG'ler
- `performans_gosterge_veri` - PG Verileri
- `project` - Projeler
- `task` - Görevler
- `task_impact` - Görev-PG İlişkileri
- `project_risk` - Proje Riskleri
- `notification` - Bildirimler

**Association Tables:**
- `surec_uyeleri` - Süreç-Kullanıcı İlişkisi
- `surec_liderleri` - Süreç Lider İlişkisi
- `project_members` - Proje Üye İlişkisi
- `project_observers` - Proje Gözlemci İlişkisi
- `project_related_processes` - Proje-Süreç İlişkisi
- `task_predecessors` - Görev Bağımlılıkları

**Indexler:**
- Performance indexes (add_performance_indexes.sql)
- Foreign key indexes
- Composite indexes (task_id + status, project_id + kurum_id)

---

### 3. MİMARİ YAPI

#### 3.1. Katmanlı Mimari

```
┌─────────────────────────────────────────┐
│         PRESENTATION LAYER              │
│  (Jinja2 Templates + JavaScript)       │
│  - Dashboard, Forms, Charts             │
└─────────────────────────────────────────┘
                  ↕
┌─────────────────────────────────────────┐
│         APPLICATION LAYER               │
│  (Flask Routes: main, api, auth)        │
│  - Request Handling                     │
│  - Response Formatting                  │
│  - Authentication/Authorization         │
└─────────────────────────────────────────┘
                  ↕
┌─────────────────────────────────────────┐
│         BUSINESS LOGIC LAYER            │
│  (Services Directory)                   │
│  - project_service                      │
│  - performance_service                  │
│  - ai_advisor_service                   │
│  - notification_service                 │
│  - etc.                                 │
└─────────────────────────────────────────┘
                  ↕
┌─────────────────────────────────────────┐
│         DATA ACCESS LAYER               │
│  (SQLAlchemy ORM + Models)              │
│  - Database Models                      │
│  - Relationships                        │
│  - Query Methods                        │
└─────────────────────────────────────────┘
                  ↕
┌─────────────────────────────────────────┐
│         DATABASE LAYER                  │
│  (SQL Server / SQLite)                  │
└─────────────────────────────────────────┘
```

#### 3.2. Design Patterns

**1. Application Factory Pattern**
- `create_app()` fonksiyonu ile uygulama oluşturma
- Environment-based configuration
- Blueprint-based modularization

**2. Repository Pattern (Partial)**
- Service layer ile business logic ayrımı
- Models üzerinden data access

**3. Decorator Pattern**
- `@login_required` - Authentication
- `@project_access_required` - Authorization
- `@limiter.limit()` - Rate limiting
- `@csrf.exempt` - CSRF exemption

**4. Observer Pattern**
- SQLAlchemy Event Listeners
- Task status change → PG data creation
- Notification triggers

**5. Strategy Pattern**
- Different calculation methods for PG
- Multiple period types (daily, weekly, monthly, quarterly, yearly)

#### 3.3. API Architecture

**RESTful Principles:**
- GET - Veri okuma
- POST - Yeni kayıt oluşturma
- PUT - Kayıt güncelleme
- DELETE - Kayıt silme

**Response Format:**
```json
{
  "success": true/false,
  "message": "İşlem mesajı",
  "data": { ... }  // Opsiyonel
}
```

**Error Handling:**
- HTTP 200: Success
- HTTP 400: Bad Request
- HTTP 403: Forbidden
- HTTP 404: Not Found
- HTTP 500: Internal Server Error

---

## BÖLÜM 2: MODÜLLER VE ÖZELLİKLER

### 4. KULLANICI YÖNETİMİ

#### 4.1. Kullanıcı Rolleri

**4.1.1. Admin (Sistem Yöneticisi)**
- Tüm sisteme tam erişim
- Kullanıcı oluşturma/düzenleme/silme
- Kurum yönetimi
- Sistem ayarları

**4.1.2. Kurum Yöneticisi**
- Kuruma ait tüm süreçlere erişim
- Kurum bilgileri düzenleme
- Kullanıcı yönetimi (kendi kurumu)
- Tüm raporlara erişim

**4.1.3. Üst Yönetim**
- Executive Dashboard erişimi
- Tüm süreçleri görüntüleme (salt okunur)
- Raporlama ve analitik erişimi
- Stratejik planlama görünümü

**4.1.4. Kurum Kullanıcısı (Normal Kullanıcı)**
- Atandığı süreçlerde veri girişi
- Bireysel performans takibi
- Görev yönetimi
- Kendi projelerini görüntüleme

#### 4.2. Kullanıcı Özellikleri

**Profil Bilgileri:**
- Ad, Soyad
- Email, Telefon
- Unvan, Departman
- Profil fotoğrafı

**Özelleştirme:**
- Tema tercihi (Light/Dark)
- Layout tercihi (Classic/Sidebar)
- Dashboard düzeni
- Bildirim tercihleri

**Güvenlik:**
- Şifre hashleme (Werkzeug)
- Session yönetimi
- CSRF koruması
- Rate limiting

#### 4.3. Authentication Flow

```
1. Login sayfası (/auth/login)
   ↓
2. Kullanıcı adı + şifre kontrolü
   ↓
3. Flask-Login session oluşturma
   ↓
4. Dashboard'a yönlendirme
   ↓
5. Role-based access control (RBAC)
```

---

### 5. SÜREÇ YÖNETİMİ

#### 5.1. Süreç Tanımlama

**Süreç Özellikleri:**
- Süreç adı
- Doküman numarası
- Revizyon numarası ve tarihi
- İlk yayın tarihi
- Başlangıç/Bitiş sınırı
- Başlangıç/Bitiş tarihi
- Durum (Aktif/Pasif)
- İlerleme yüzdesi
- Açıklama

**Süreç İlişkileri:**
- **Liderler:** Birden fazla lider atanabilir
- **Üyeler:** Birden fazla üye eklenebilir
- **Alt Stratejiler:** Birden fazla strateji ile ilişkilendirilebilir
- **Performans Göstergeleri:** Her sürecin kendi PG'leri
- **Faaliyetler:** Aylık faaliyet takibi

#### 5.2. Süreç Karnesi (Scorecard)

**Özellikler:**
- Periyot bazlı performans takibi
- Görsel veri giriş sihirbazı
- Otomatik hedef değer hesaplama
- Durum göstergesi (İyi/Orta/Kötü)
- Excel export
- Veri audit trail

**Periyot Tipleri:**
- **Günlük:** Her gün veri girişi
- **Haftalık:** Haftalık veri (Cuma günü)
- **Aylık:** Aylık veri (ayın son Cuma'sı)
- **Çeyreklik:** 3 aylık periyot (çeyreğin son Cuma'sı)
- **Yıllık:** Yıllık veri (yılın son Cuma'sı)

**Veri Toplama Yöntemleri:**
- **Toplam/Toplama:** Değerler toplanır
- **Ortalama:** Ortalama alınır
- **Son Değer:** En son girilen değer

#### 5.3. Süreç Paneli

**Görüntüleme:**
- Süreç bilgileri
- Performans göstergeleri ve gerçek zamanlı durumları
- Faaliyet listesi
- İlişkili projeler
- Süreç sağlık skoru

**İşlemler:**
- Süreç düzenleme (liderler için)
- PG ekleme/düzenleme
- Faaliyet tanımlama
- Üye/lider yönetimi

---

### 6. PERFORMANS GÖSTERGELERİ (PG)

#### 6.1. PG Tipleri

**6.1.1. Süreç Performans Göstergeleri**
- Süreç seviyesinde tanımlı
- Tüm süreç üyelerine görünür
- Master PG

**6.1.2. Bireysel Performans Göstergeleri**
- Kullanıcı bazlı
- Süreç PG'sinden türetilebilir
- Kişisel hedefler

#### 6.2. PG Özellikleri

**Temel Bilgiler:**
- PG Adı
- PG Kodu
- Periyot (Günlük/Haftalık/Aylık/Çeyreklik/Yıllık)
- Hedef Değer
- Ölçü Birimi
- Açıklama

**Hesaplama:**
- Veri Toplama Yöntemi (Toplam/Ortalama/Son Değer)
- Otomatik hedef hesaplama
- Durum hesaplama (İyi: >90%, Orta: 70-90%, Kötü: <70%)

**Görselleştirme:**
- Trend grafikleri
- Hedef-gerçekleşen karşılaştırma
- Renkli durum göstergeleri

#### 6.3. Veri Girişi

**Yöntemler:**
1. **Manuel Giriş:**
   - Süreç karnesi üzerinden
   - Veri giriş sihirbazı
   - Toplu veri girişi

2. **Otomatik Giriş:**
   - Proje görevleri tamamlandığında
   - TaskImpact üzerinden
   - Periyoda göre otomatik tarih hesaplama

**Veri Doğrulama:**
- Hedef değer kontrolü
- Periyot kontrolü
- Duplicate check
- Audit trail (kim, ne zaman, ne değiştirdi)

---

### 7. PROJE YÖNETİMİ

#### 7.1. Proje Özellikleri

**Temel Bilgiler:**
- Proje adı
- Proje açıklaması
- Başlangıç/Bitiş tarihi
- Öncelik (Düşük/Orta/Yüksek/Acil)
- Proje yöneticisi

**İlişkiler:**
- **Üyeler:** Proje ekibi
- **Gözlemciler:** Sadece görüntüleme yetkisi
- **İlişkili Süreçler:** Birden fazla süreç bağlanabilir
- **Görevler:** Alt görevler
- **Riskler:** Risk kayıtları
- **Dosyalar:** Proje dosyaları

**Durum Takibi:**
- Toplam görev sayısı
- Tamamlanan görev sayısı
- Geciken görev sayısı
- Tamamlanma yüzdesi
- Sağlık skoru

#### 7.2. Görev Yönetimi

**Görev Özellikleri:**
- Görev başlığı/açıklaması
- Atanan kişi
- Durum (Yapılacak/Devam Ediyor/Beklemede/Tamamlandı)
- Öncelik
- Bitiş tarihi
- Tahmini süre / Gerçekleşen süre
- Üst görev (hiyerarşik yapı)
- Öncül görevler (bağımlılıklar)

**Görev İmpactları (TaskImpact):**
- Görev tamamlandığında hangi PG'ye veri girilecek
- Impact değeri (sayısal)
- İlişkili PG seçimi
- Otomatik veri akışı

**Görünümler:**
1. **Kanban Board:**
   - Sütunlar: Yapılacak, Devam Ediyor, Beklemede, Tamamlandı
   - Drag & drop
   - Mobil uyumlu

2. **Gantt Chart:**
   - Zaman çizelgesi
   - Bağımlılık okları
   - Kritik yol analizi

3. **Liste Görünümü:**
   - Tablo formatında görevler
   - Filtreleme
   - Sıralama

**Mobil Özellik:**
- Hızlı tamamlama butonu (✓)
- Tek tıkla "Tamamlandı" yapma
- Otomatik PG tetikleme

#### 7.3. Risk Yönetimi

**Risk Isı Haritası:**
- Olasılık (1-5)
- Etki (1-5)
- Risk Skoru (Olasılık × Etki = 1-25)
- Renkli gösterim (Yeşil/Sarı/Turuncu/Kırmızı)

**Risk Özellikleri:**
- Risk başlığı
- Risk açıklaması
- Risk seviyesi (Düşük/Orta/Yüksek/Kritik)
- Durum (Aktif/Azaltılmış/Kapatıldı)
- Aksiyon planı
- Sorumlu kişi

**AI Risk Tahmini:**
- Görev gecikmelerine göre risk tahmini
- Erken uyarı sistemi
- Gecikme olasılığı hesaplama

#### 7.4. Proje Klonlama/Şablon Sistemi

**Özellikler:**
- Proje kopyalama
- Görev yapısını kopyalama
- Alt görevleri kopyalama
- Risk yapısını kopyalama
- Dosya klasör yapısını kopyalama
- Yeni başlangıç tarihine göre tarihleri kaydırma
- Durum ve süreleri sıfırlama

**Kullanım Senaryoları:**
1. Geçmiş projeden yeni proje oluşturma
2. Kurumsal proje şablonları
3. Tekrarlayan projeler

#### 7.5. Dosya Yönetimi

**İkili Dosya Sistemi:**

1. **Proje Bazlı Dosyalar:**
   - Proje kapsamında
   - Proje üyeleri erişebilir
   - Proje klasör yapısı

2. **Kurumsal Dosyalar (Doküman Merkezi):**
   - Kurum genelinde
   - Kategori bazlı
   - Rol bazlı erişim
   - Şablon ve standart dosyalar

**Mobil Özellik:**
- Kamera ile fotoğraf çekme (`capture="camera"`)
- Büyük dosya yükleme butonu
- Saha raporlama

---

### 8. EXECUTIVE DASHBOARD (YÖNETİM KOKPİTİ)

#### 8.1. Dashboard Widgets

**1. Kurumsal Nabız (Gauge Chart):**
- Kurum geneli sağlık skoru (0-100)
- Tüm süreçlerin ortalaması
- Proje tamamlanma oranları
- Risk faktörleri
- Gecikme cezaları

**2. Neden Bu Skor? (Score Factors):**
- En çok skor kıran top 2 etken
- Gecikmiş görev sayısı
- Kritik risk sayısı
- Düşük performans gösteren süreçler

**3. Kritik Risk Radarı:**
- Top 5 kritik risk
- Risk skoru (1-25)
- İlişkili proje
- Sorumlu kişi

**4. Planlama Becerisi (Bar Chart):**
- Tahmini süre vs Gerçekleşen süre
- Proje bazlı karşılaştırma
- Planlama doğruluğu analizi

**5. Bekleyen İş Yükü (Pie Chart):**
- Durum bazlı görev dağılımı
- Yapılacak, Devam Ediyor, Beklemede
- Yüzdelik oranlar

**6. Personel Yükü Analizi (Bar Chart):**
- Kullanıcı bazlı aktif görev sayısı
- Departman bazlı yük dağılımı
- Bottleneck tespiti

**7. AI Yönetici Özeti:**
- Top 3 risk analizi
- Top 3 acil görev
- Tek paragraflık özet
- "Bugün odaklanmanız gereken alan..."

**8. AI Stratejik Danışman:**
- Sistem özeti
- Öne çıkan riskler
- AI tavsiyeleri
- İncele/Bildir butonları

#### 8.2. Filtreleme

**Filter Options:**
- Departman bazlı
- Proje yöneticisi bazlı
- Zaman aralığı (başlangıç-bitiş)
- Dinamik grafik güncelleme

#### 8.3. Export

**PDF Rapor:**
- Dashboard özet raporu
- Grafik ve görseller
- Tablo verileri
- ReportLab ile oluşturulur

---

### 9. AI ÖZELLİKLERİ

#### 9.1. AI Erken Uyarı Sistemi

**Kaynak:** `services/ai_early_warning.py`

**Özellikler:**
- Görev gecikmesi tahmini
- Risk faktörü hesaplama
- Gecikme olasılığı (%)
- Proje detay sayfasında gösterim

**Hesaplama Faktörleri:**
- Geciken görev sayısı
- Toplam görev sayısı
- Aktif kritik risk sayısı
- Ortalama gecikme süresi
- Risk ağırlıkları

**Formül:**
```
Task-based probability (70%) + Risk-based probability (30%)
```

#### 9.2. AI Yönetici Özeti

**Kaynak:** `services/ai_executive_summary.py`

**Özellikler:**
- Top 3 kritik risk analizi
- Top 3 acil/gecikmiş görev analizi
- Tek paragraflık özet üretimi
- Doğal dil işleme

**Örnek Output:**
> "Bugün odaklanmanız gereken alan şudur: 2 kritik risk tespit edildi: 'Teknik Altyapı Sorunu', 'Kaynak Yetersizliği' (Skorlar: 25, 20). Ayrıca, 1 gecikmiş görev var: 'Test Senaryoları Hazırlama' ve 2 acil görev yaklaşıyor. Bu konulara öncelik verilmesi önerilir."

#### 9.3. AI Stratejik Danışman

**Kaynak:** `services/ai_advisor_service.py`

**Analiz Kapsamı:**
- Tüm aktif projeler
- Sağlık skorları
- PG performans sapmaları (son 30 gün)
- Kritik riskler
- Görev gecikmeleri
- Kaynak dağılımı

**Üretilen Çıktılar:**
1. **Sistem Özeti:**
   - Aktif proje sayısı
   - Kritik risk sayısı
   - PG sapma sayısı
   - Gecikmiş görev sayısı

2. **Öne Çıkan Riskler:**
   - Top 5 kritik risk
   - İlişkili proje/süreç
   - Risk detayları

3. **AI Tavsiyeleri:**
   - Proje-süreç ilişki analizi
   - Kaynak aktarım önerileri
   - Öncelik sıralaması önerileri
   - Bottleneck uyarıları

**İnteraktif Aksiyonlar:**
- "İncele" butonu → Detay sayfasına git
- "Bildir" butonu → İlgili sorumluya bildirim gönder

#### 9.4. PG Performans Sapması Erken Uyarısı

**Tetikleyici:**
- PG gerçekleşen değer hedefin %10+ altında
- Otomatik bildirim oluşturma
- Kullanıcı + süreç liderine bildirim

**Kaynak:** `services/notification_service.py` → `check_pg_performance_deviation()`

---

### 10. RAPORLAMA

#### 10.1. Excel Export

**Süreç Karnesi Excel:**
- Periyot bazlı veri
- Tüm PG'ler
- Hedef-gerçekleşen karşılaştırma
- Openpyxl ile üretilir
- Styling ve formatlama

#### 10.2. PDF Raporlama

**Kaynak:** `services/report_service.py`

**Rapor Tipleri:**
1. **Proje Durum Raporu:**
   - Proje özeti
   - Görev analizi
   - Risk analizi
   - Dosya listesi

2. **Dashboard Raporu:**
   - Executive dashboard özeti
   - Grafikler (statik görsel)
   - Tablo verileri

**Özellikler:**
- ReportLab kullanımı
- Logo ve başlık
- Profesyonel tasarım
- Tarih damgası

---

## BÖLÜM 3: KULLANICI KLAVUZU

### 11. ROL BAZLI KULLANIM SENARYOLARI

#### 11.1. ADMIN ROL SENARYOSU

**Giriş Sonrası:**
1. Dashboard'da sistem geneli gösterir
2. Sol menüde tüm modüller görünür

**Yapabildiği İşlemler:**
- ✅ Kurum oluşturma/düzenleme
- ✅ Kullanıcı oluşturma/düzenleme/silme
- ✅ Rol atama
- ✅ Tüm süreçlere erişim
- ✅ Tüm projelere erişim
- ✅ Sistem ayarları
- ✅ Log görüntüleme

**Örnek İş Akışı:**
```
1. Admin Paneline git (/admin-panel)
2. "Yeni Kurum Ekle" buton
3. Kurum bilgilerini doldur
4. Kaydet
5. Kurum için kullanıcı oluştur
6. Rol ata (kurum_yoneticisi)
```

#### 11.2. KURUM YÖNETİCİSİ ROL SENARYOSU

**Giriş Sonrası:**
1. Dashboard - Kurum özeti
2. Executive Dashboard erişimi var
3. Kendi kurumunun tüm verileri görünür

**Yapabildiği İşlemler:**
- ✅ Kurum bilgilerini düzenleme
- ✅ Kurum logosu yükleme
- ✅ Süreç oluşturma
- ✅ Süreç lider/üye atama
- ✅ Tüm süreçlerin PG'lerini görüntüleme
- ✅ Proje oluşturma/düzenleme
- ✅ Tüm projeleri görüntüleme
- ✅ Executive Dashboard görüntüleme
- ✅ PDF rapor indirme
- ✅ Kullanıcı oluşturma (kendi kurumu)

**Örnek İş Akışı - Süreç Oluşturma:**
```
1. Süreç Paneline git (/surec-paneli)
2. "Yeni Süreç" butonu
3. Süreç bilgilerini doldur:
   - Ad, Doküman No, Rev No
   - Başlangıç/Bitiş tarihi
   - Açıklama
4. Lider ve üye seç
5. Kaydet
6. Süreç için PG tanımla
```

**Örnek İş Akışı - Executive Dashboard:**
```
1. Yönetim Kokpiti menüsüne tıkla
2. Dashboard açılır
3. Filtreleri uygula:
   - Departman seç
   - Tarih aralığı seç
   - Proje yöneticisi seç
4. Grafikleri incele:
   - Kurumsal Nabız
   - Kritik Risk Radarı
   - Planlama Becerisi
   - Personel Yükü
5. AI Stratejik Danışman'ı oku
6. "PDF Rapor İndir" ile rapor al
```

#### 11.3. ÜST YÖNETİM ROL SENARYOSU

**Giriş Sonrası:**
1. Executive Dashboard (otomatik yönlendirme)
2. Salt okunur erişim
3. Raporlama ve analitik odaklı

**Yapabildiği İşlemler:**
- ✅ Executive Dashboard görüntüleme
- ✅ Tüm süreçleri görüntüleme (düzenleme yok)
- ✅ Tüm projeleri görüntüleme (düzenleme yok)
- ✅ PDF rapor indirme
- ✅ AI özetlerini okuma
- ✅ Stratejik planlama akışını görüntüleme

**Örnek İş Akışı - Analiz:**
```
1. Yönetim Kokpiti açılır
2. Kurumsal Nabız skorunu kontrol et
3. "Neden Bu Skor?" bölümünü oku
4. Kritik riskleri incele
5. AI Stratejik Danışman önerilerini oku
6. Gerekirse ilgili proje detayına git
7. PDF rapor indir ve paylaş
```

#### 11.4. SÜREÇ LİDERİ ROL SENARYOSU

**Giriş Sonrası:**
1. Dashboard - Kendi süreçlerinin özeti
2. Süreç Karnesi erişimi
3. Liderlik yaptığı süreçlere full erişim

**Yapabildiği İşlemler:**
- ✅ Süreç bilgilerini düzenleme (kendi süreçleri)
- ✅ PG ekleme/düzenleme/silme
- ✅ Faaliyet tanımlama
- ✅ Üye ekleme/çıkarma
- ✅ Veri girişi (tüm PG'ler)
- ✅ Veri onaylama
- ✅ Süreç sağlık skorunu görüntüleme
- ✅ Raporlama

**Örnek İş Akışı - PG Tanımlama:**
```
1. Süreç Karnesi'ne git
2. Kendi sürecini seç
3. "Yeni PG Ekle" butonu
4. PG bilgilerini gir:
   - PG Adı, Kodu
   - Periyot (Aylık)
   - Hedef Değer
   - Veri Toplama Yöntemi (Toplam)
   - Ölçü Birimi
5. Kaydet
6. Bireysel PG'ler otomatik oluşturulur (tüm üyeler için)
```

**Örnek İş Akışı - Veri Girişi:**
```
1. Süreç Karnesi'ne git
2. Yıl ve periyot seç (2025, Aylık)
3. PG listesinde veri gir:
   - Gerçekleşen değer yaz
   - Hedef otomatik gösterilir
   - Durum (İyi/Orta/Kötü) otomatik hesaplanır
4. "Kaydet" butonu
5. Başarı mesajı
6. Dashboard'da güncellenen veriler
```

#### 11.5. SÜREÇ ÜYESİ ROL SENARYOSU

**Giriş Sonrası:**
1. Dashboard - Bireysel performans özeti
2. Atandığı süreçlerin listesi
3. Kendi PG'leri

**Yapabildiği İşlemler:**
- ✅ Kendi bireysel PG'lerine veri girişi
- ✅ Kendi görevlerini görüntüleme/tamamlama
- ✅ Süreç bilgilerini görüntüleme (düzenleme yok)
- ✅ Faaliyet takibi
- ✅ Zaman takibi

**Örnek İş Akışı - Bireysel Veri Girişi:**
```
1. Performans Kartım'a git
2. Kendi PG'lerini görüntüle
3. İlgili ay/periyodu seç
4. Veri gir
5. Kaydet
6. Durum göstergesini kontrol et
```

#### 11.6. PROJE YÖNETİCİSİ ROL SENARYOSU

**Giriş Sonrası:**
1. Dashboard - Proje özeti
2. Proje Yönetimi menüsü
3. Yönettiği projelerin listesi

**Yapabildiği İşlemler:**
- ✅ Proje oluşturma
- ✅ Proje düzenleme
- ✅ Görev oluşturma/atama
- ✅ Risk ekleme/yönetme
- ✅ Dosya yükleme
- ✅ Proje klonlama
- ✅ Üye/gözlemci yönetimi
- ✅ Proje analitik görüntüleme
- ✅ Gantt chart görüntüleme

**Örnek İş Akışı - Yeni Proje:**
```
1. Proje Yönetimi → Yeni Proje
2. Proje bilgilerini doldur:
   - Ad, Açıklama
   - Başlangıç/Bitiş tarihi
   - Öncelik (Yüksek)
3. İlişkili süreçleri seç
4. Üye ve gözlemci ekle
5. Kaydet
6. Proje detay sayfasına yönlendir
7. Görev eklemeye başla
```

**Örnek İş Akışı - Görev + PG Bağlantısı:**
```
1. Proje detayda "Yeni Görev"
2. Görev bilgilerini gir:
   - Başlık, Açıklama
   - Atanan kişi
   - Bitiş tarihi
   - Tahmini süre
3. "PG İmpact Ekle" bölümünde:
   - İlgili PG seç
   - Impact değerini gir (örn: 5 adet)
4. Kaydet
5. Görev "Tamamlandı" yapıldığında:
   → Otomatik PG'ye veri girilir
   → Bildirim gönderilir
   → Dashboard güncellenir
```

#### 11.7. SAHA PERSONELİ ROL SENARYOSU

**Mobil Cihazdan Giriş:**
1. Mobil tarayıcıdan giriş
2. Mobil optimize arayüz
3. Alt gezinti menüsü aktif

**Yapabildiği İşlemler:**
- ✅ Görevlerini görüntüleme
- ✅ Hızlı görev tamamlama (✓ butonu)
- ✅ Kamera ile fotoğraf çekme
- ✅ Dosya yükleme (saha raporu)
- ✅ Bildirim görüntüleme
- ✅ PG veri girişi

**Örnek İş Akışı - Saha Görevi:**
```
1. Mobil'den login
2. Alt menüden "Projelerim"
3. İlgili projeye gir
4. Görev kartında "✓" butonuna bas
5. Onay ver
6. Görev "Tamamlandı" olur
7. (Opsiyonel) Fotoğraf ekle:
   - "Dosya Yükle" butonu
   - Kamera açılır
   - Fotoğraf çek
   - Yükle
```

---

### 12. TÜM EKRANLAR VE İŞLEMLER

#### 12.1. ANA SAYFALAR (UI Routes)

**12.1.1. Ana Sayfa (`/`)**
- Giriş yapmışsa Dashboard'a yönlendirir
- Giriş yapmamışsa Login sayfasına yönlendirir

**12.1.2. Login (`/auth/login`)**
- Kullanıcı adı + şifre girişi
- "Beni Hatırla" seçeneği
- Hızlı giriş butonları (development)
- Tema seçimi

**12.1.3. Dashboard (`/dashboard`)**
**Görüntülenen:**
- Hoş geldin mesajı
- Son aktiviteler (10 kayıt)
- Hızlı erişim kartları
- Layout seçimi (Classic/Sidebar)

**Kartlar:**
- Süreç Karnesi
- Proje Yönetimi
- Performans Kartım
- Süreç Paneli
- Kurum Paneli (yöneticiler için)
- Admin Panel (admin için)

**12.1.4. Süreç Karnesi (`/surec-karnesi`)**
**Özellikler:**
- Süreç seçimi (dropdown)
- Yıl seçimi
- Periyot seçimi (Günlük/Haftalık/Aylık/Çeyreklik/Yıllık)
- Ay seçimi (haftalık/günlük için)
- PG listesi (accordion)
- Faaliyet listesi (accordion)

**Veri Giriş Sihirbazı:**
- Adım adım rehber
- Her PG için input
- Otomatik hesaplama
- Kaydetme butonu
- Excel export butonu

**İşlemler:**
- PG ekleme (süreç lideri)
- Veri girişi (lider + üyeler)
- Veri görüntüleme
- Grafik gösterimi
- Excel export

**12.1.5. Süreç Paneli (`/surec-paneli`)**
**Görüntülenen:**
- Kullanıcının süreç listesi
- Her süreç için kart görünümü
- Süreç bilgileri
- PG özet durumları
- Faaliyet durumları
- İlişkili projeler

**İşlemler:**
- Süreç detay görüntüleme
- PG yönetimi
- Faaliyet yönetimi
- Lider/üye yönetimi (liderler için)

**12.1.6. Performans Kartım (`/performans-kartim`)**
**Görüntülenen:**
- Kullanıcının bireysel PG'leri
- PG başına trend grafiği
- Hedef-gerçekleşen karşılaştırma
- Son 6 aylık veri (opsiyonel)

**İşlemler:**
- Veri girişi
- Veri güncelleme
- Grafik görüntüleme

**12.1.7. Proje Yönetimi (`/projeler`)**
**Görüntülenen:**
- Proje listesi (kart görünümü)
- Her proje için:
  - Proje adı
  - Proje yöneticisi
  - İlişkili süreçler
  - Oluşturulma tarihi

**İşlemler:**
- Yeni proje oluşturma
- Proje görüntüleme
- Proje kopyalama/şablon
- Proje detayına gitme

**12.1.8. Proje Detay (`/projeler/<project_id>`)**
**Görüntülenen:**

1. **Proje Bilgi Kartı:**
   - Proje adı, açıklama
   - Proje yöneticisi
   - Oluşturulma tarihi
   - Kopyala butonu

2. **AI Erken Uyarı Kartı:**
   - Gecikme olasılığı (%)
   - Risk faktörü
   - Uyarı mesajı

3. **Proje Özeti (3 Kart):**
   - Geciken görevler
   - Aktif üyeler
   - Tamamlanan görevler

4. **Risk Isı Haritası:**
   - 5x5 matrix
   - Riskler renkli gösterim
   - Risk ekleme butonu
   - Risk listesi

5. **Dosya Havuzu:**
   - Proje dosyaları
   - Yükle butonu (mobilde kamera)
   - Dosya listesi (icon, isim, tarih)
   - İndirme/silme butonları

6. **Görevler (Kanban Board):**
   - 4 sütun görünümü
   - Görev kartları
   - Drag & drop
   - Mobilde "✓" butonu (hızlı tamamlama)

**İşlemler:**
- Görev ekleme
- Görev düzenleme (tıkla)
- Görev sürükleme (durum değiştirme)
- Risk ekleme
- Dosya yükleme
- Proje kopyalama
- Gantt chart'a geçiş

**12.1.9. Görev Form (`/projeler/<project_id>/gorevler/yeni`)**
**Alanlar:**
- Görev başlığı *
- Durum
- Öncelik
- Atanan kişi
- Bitiş tarihi
- Tahmini süre
- Gerçekleşen süre (sadece tamamlandıysa)
- Açıklama
- Üst görev (hiyerarşi)
- Öncül görevler (bağımlılık)
- İlişkili PG (opsiyonel)

**PG Impact Bölümü:**
- "Impact Ekle" butonu
- İlişkili PG seçimi
- Impact değeri
- Birden fazla impact eklenebilir

**İşlemler:**
- Yeni görev kaydetme
- Görev güncelleme
- İptal

**12.1.10. Gantt Chart (`/projeler/<project_id>/gantt`)**
**Görüntülenen:**
- Zaman çizelgesi
- Görev barları
- Bağımlılık okları
- Kritik yol (opsiyonel)
- Milestone'lar (opsiyonel)

**İşlemler:**
- Zoom in/out
- Pan (kaydırma)
- Görev tıklama (detay)

**12.1.11. Executive Dashboard (`/dashboard/executive`)**
**Görüntülenen:**
- AI Yönetici Özeti
- Kurumsal Nabız (Gauge)
- Neden Bu Skor?
- Kritik Risk Radarı
- Planlama Becerisi (Bar Chart)
- Bekleyen İş Yükü (Pie Chart)
- Personel Yükü Analizi
- AI Stratejik Danışman

**Filtreler:**
- Departman
- Proje Yöneticisi
- Tarih Aralığı

**İşlemler:**
- Filtreleme
- PDF rapor indirme
- Grafik görüntüleme
- AI tavsiyeleri okuma
- Tavsiye üzerinden aksiy on alma (İncele/Bildir)

**12.1.12. Doküman Merkezi (`/dokuman-merkezi`)**
**Görüntülenen:**
- Kurumsal dosya listesi
- Kategori bazlı filtreleme
- Dosya arama
- Dosya detayları

**İşlemler:**
- Kurumsal dosya yükleme (yetki gerekli)
- Kategori seçimi
- Dosya indirme
- Dosya silme (yetki gerekli)

**12.1.13. Proje Analitik (`/proje-analitik`)**
**Görüntülenen:**
- Proje karşılaştırma grafikleri
- Tamamlanma oranları
- Gecikme analizleri
- Kaynak dağılımı
- Zaman analizi

**12.1.14. Zaman Takibi (`/zaman-takibi`)**
**Görüntülenen:**
- Kullanıcının zaman kayıtları
- Görev bazlı süre girişi
- Günlük/haftalık/aylık özet
- Toplam çalışma saatleri

**İşlemler:**
- Zaman kaydı ekleme
- Zaman düzeltme
- Rapor görüntüleme

**12.1.15. Görev Aktivite Log (`/gorev-aktivite-log`)**
**Görüntülenen:**
- Tüm görev değişiklikleri
- Kim, ne zaman, ne yaptı
- Durum değişiklikleri
- Yorum ekleme/düzenleme
- Atama değişiklikleri

**12.1.16. Akıllı Planlama (`/akilli-planlama`)**
**Özellikler:**
- AI destekli görev zamanlama
- Kaynak optimizasyonu
- Bottleneck tespiti
- Öneri sistemi

**12.1.17. Stratejik Planlama Akışı (`/stratejik-planlama-akisi`)**
**Görüntülenen:**
- SWOT Analizi
- PESTLE Analizi
- Stratejik hedefler
- Aksiyon planları
- Vizyon/Misyon

**12.1.18. Stratejik Asistan (`/stratejik-asistan`)**
**Özellikler:**
- AI sohbet arayüzü
- Stratejik soru-cevap
- Veri analizi
- Öneriler

**12.1.19. Kurum Paneli (`/kurum-paneli`)**
**Görüntülenen:**
- Kurum bilgileri
- Kurum logosu
- Değerler
- Etik kuralları
- Kalite politikaları
- Kullanıcı listesi
- Süreç listesi

**İşlemler (Yöneticiler):**
- Kurum bilgisi düzenleme
- Logo yükleme
- Değer/etik/kalite ekleme

**12.1.20. Admin Panel (`/admin-panel`)**
**Görüntülenen:**
- Sistem istatistikleri
- Kullanıcı yönetimi
- Kurum yönetimi
- Log görüntüleme
- Sistem ayarları

**İşlemler:**
- Kurum ekleme/düzenleme
- Kullanıcı ekleme/düzenleme/silme
- Rol atama
- Sistem parametreleri

**12.1.21. Profil (`/profile`)**
**Görüntülenen:**
- Kullanıcı bilgileri
- Profil fotoğrafı
- Rol bilgisi
- İstatistikler

**İşlemler:**
- Profil düzenleme
- Fotoğraf yükleme
- Şifre değiştirme
- Tema/layout değiştirme

**12.1.22. Ayarlar (`/settings`)**
**Görüntülenen:**
- Tema ayarları
- Layout ayarları
- Bildirim tercihleri
- Dil ayarları (gelecek)

---

### 13. API KULLANIMI

#### 13.1. API Endpoint Listesi (40+ Endpoint)

**Süreç Karnesi API:**
```
GET  /api/surec/<surec_id>/karne/performans
GET  /api/surec/<surec_id>/karne/faaliyetler
POST /api/surec/<surec_id>/karne/kaydet
GET  /api/pg-veri/detay/<veri_id>
POST /api/pg-veri/detay/toplu
PUT  /api/pg-veri/guncelle/<veri_id>
GET  /api/export/surec_karnesi/excel
```

**Proje API:**
```
GET  /api/projeler
POST /api/projeler
GET  /api/projeler/<project_id>
PUT  /api/projeler/<project_id>
POST /api/projeler/<project_id>/klonla
GET  /api/projeler/<project_id>/export-pdf
```

**Görev API:**
```
GET  /api/projeler/<project_id>/gorevler
POST /api/projeler/<project_id>/gorevler
GET  /api/projeler/<project_id>/gorevler/<task_id>
PUT  /api/projeler/<project_id>/gorevler/<task_id>
DELETE /api/projeler/<project_id>/gorevler/<task_id>
GET  /api/projeler/<project_id>/gorevler/<task_id>/asiri-yukleme-kontrol
```

**Risk API:**
```
GET  /api/projeler/<project_id>/riskler
POST /api/projeler/<project_id>/riskler
PUT  /api/projeler/<project_id>/riskler/<risk_id>
DELETE /api/projeler/<project_id>/riskler/<risk_id>
GET  /api/projeler/<project_id>/ai-tahmin
```

**Dosya API:**
```
GET  /api/projeler/<project_id>/dosyalar
POST /api/projeler/<project_id>/dosyalar
GET  /api/projeler/<project_id>/dosyalar/<file_id>/indir
DELETE /api/projeler/<project_id>/dosyalar/<file_id>
GET  /api/dokuman-merkezi
POST /api/dokuman-merkezi
DELETE /api/dokuman-merkezi/<file_id>
```

**Dashboard API:**
```
GET  /api/dashboard/executive
GET  /api/dashboard/filter-options
GET  /api/dashboard/export-pdf
GET  /api/dashboard/ai-advisor
POST /api/dashboard/ai-advisor/notify
```

**Bildirim API:**
```
GET  /api/notifications
GET  /api/notifications/count
POST /api/notifications/mark-all-read
```

**Kullanıcı API:**
```
POST /api/user/layout
POST /api/user/theme
```

**Kurum API:**
```
POST /api/kurum/upload-logo
POST /api/kurum/update-logo
```

**Süreç API:**
```
GET  /api/surec/<surec_id>/saglik-skoru
GET  /api/projeler/<project_id>/kaynak-isi-haritasi
```

#### 13.2. API Kullanım Örnekleri

**Örnek 1: Yeni Proje Oluşturma**
```javascript
fetch('/api/projeler', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        name: 'Yeni Proje',
        description: 'Proje açıklaması',
        manager_id: 1,
        start_date: '2025-01-01',
        end_date: '2025-12-31',
        priority: 'Yüksek',
        member_ids: [2, 3, 4],
        observer_ids: [5],
        related_process_ids: [1, 2]
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        console.log('Proje oluşturuldu:', data.project_id);
    }
});
```

**Örnek 2: Görev Tamamlama**
```javascript
fetch(`/api/projeler/${projectId}/gorevler/${taskId}`, {
    method: 'PUT',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken
    },
    body: JSON.stringify({
        status: 'Tamamlandı',
        actual_time: 8.5
    })
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        // Otomatik PG veri girişi tetiklendi
        // Bildirimler gönderildi
        console.log('Görev tamamlandı');
    }
});
```

**Örnek 3: Executive Dashboard Verisi**
```javascript
fetch(`/api/dashboard/executive?department=IT&manager_id=5&start_date=2025-01-01&end_date=2025-12-31`)
.then(response => response.json())
.then(data => {
    const healthScore = data.corporate_health.score;
    const criticalRisks = data.critical_risks;
    const personnel_workload = data.personnel_workload;
    // Grafikleri render et
});
```

---

## BÖLÜM 4: TEKNİK DETAYLAR

### 14. VERİTABANI MODELLERİ

#### 14.1. Core Models (30+ Tablo)

**14.1.1. User Model**
```python
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, index=True)
    email = db.Column(db.String(120), unique=True, index=True)
    password_hash = db.Column(db.String(120))
    first_name, last_name, phone, title, department
    sistem_rol = db.Column(db.String(50), index=True)
    # admin, kurum_yoneticisi, ust_yonetim, kurum_kullanici
    kurum_id = db.Column(db.Integer, db.ForeignKey('kurum.id'))
    profile_photo, theme_preferences, layout_preference
```

**14.1.2. Project Model**
```python
class Project(db.Model):
    id, kurum_id, name, manager_id
    description, start_date, end_date, priority
    is_archived = db.Column(db.Boolean, default=False, index=True)
    created_at, updated_at
    
    # Relationships
    members = relationship(User, secondary=project_members)
    observers = relationship(User, secondary=project_observers)
    related_processes = relationship(Surec, secondary=project_related_processes)
    tasks = relationship(Task, backref='project', cascade='all, delete-orphan')
    risks = relationship(ProjectRisk, backref='project', cascade='all, delete-orphan')
    files = relationship(ProjectFile, backref='project', cascade='all, delete-orphan')
```

**14.1.3. Task Model**
```python
class Task(db.Model):
    id, project_id, parent_id
    title, description, assigned_to_id
    due_date, priority, status
    estimated_time, actual_time, completed_at
    is_archived = db.Column(db.Boolean, default=False, index=True)
    created_at, updated_at
    
    # Relationships
    impacts = relationship(TaskImpact, backref='task', cascade='all, delete-orphan')
    subtasks = relationship(TaskSubtask)
    comments = relationship(TaskComment, cascade='all, delete-orphan')
    activities = relationship(TaskActivity, cascade='all, delete-orphan')
    predecessors = relationship(Task, secondary=task_predecessors)
```

**14.1.4. TaskImpact Model**
```python
class TaskImpact(db.Model):
    id, task_id, related_pg_id, related_faaliyet_id
    impact_value = db.Column(db.String(100))
    is_processed = db.Column(db.Boolean, default=False, index=True)
    processed_at = db.Column(db.DateTime)
    created_at
    
    # İlişkiler
    related_pg = relationship(BireyselPerformansGostergesi)
    related_faaliyet = relationship(BireyselFaaliyet)
```

**14.1.5. ProjectRisk Model**
```python
class ProjectRisk(db.Model):
    id, project_id, title, description
    probability = db.Column(db.Integer)  # 1-5
    impact = db.Column(db.Integer)  # 1-5
    risk_score = @property (probability × impact)
    risk_level = @property (Düşük/Orta/Yüksek/Kritik)
    status, mitigation_plan, responsible_user_id
    created_at, updated_at
```

**14.1.6. Notification Model**
```python
class Notification(db.Model):
    id, user_id, tip, baslik, mesaj
    okundu = db.Column(db.Boolean, default=False)
    link, created_at
```

**14.1.7. PerformansGostergeVeri Model**
```python
class PerformansGostergeVeri(db.Model):
    id, pg_id, user_id
    veri_tarihi, donem_tipi, donem_no, donem_ay
    hedef_deger, gerceklesen_deger
    durum, durum_yuzdesi
    aciklama, created_at, updated_at
```

#### 14.2. Relationship Matrix

```
User ←→ Kurum (Many-to-One)
User ←→ Surec (Many-to-Many: liderler, üyeler)
User ←→ Project (Many-to-Many: manager, members, observers)
User ←→ Task (One-to-Many: assigned_to)
User ←→ BireyselPerformansGostergesi (One-to-Many)

Project ←→ Surec (Many-to-Many: related_processes)
Project ←→ Task (One-to-Many)
Project ←→ ProjectRisk (One-to-Many)
Project ←→ ProjectFile (One-to-Many)

Task ←→ Task (Self-referential: parent-child, predecessors)
Task ←→ TaskImpact (One-to-Many)
Task ←→ TaskComment, TaskActivity, TimeEntry (One-to-Many)

TaskImpact ←→ BireyselPerformansGostergesi (Many-to-One)
TaskImpact ←→ BireyselFaaliyet (Many-to-One)

Surec ←→ SurecPerformansGostergesi (One-to-Many)
Surec ←→ SurecFaaliyet (One-to-Many)

BireyselPerformansGostergesi ←→ SurecPerformansGostergesi (Many-to-One: kaynak)
BireyselPerformansGostergesi ←→ PerformansGostergeVeri (One-to-Many)
```

#### 14.3. Index Stratejisi

**Mevcut Indexler:**
- `Task.project_id` (FK index)
- `Task.status` (Filter index)
- `Task.assigned_to_id` (FK index)
- `Task.due_date` (Date filter)
- `Task.project_id + Task.status` (Composite)
- `Project.kurum_id` (FK index)
- `Project.manager_id` (FK index)
- `TaskImpact.task_id + TaskImpact.is_processed` (Composite)
- `ProjectRisk.project_id + ProjectRisk.status` (Composite)
- `Notification.user_id` (FK index)
- `User.kurum_id` (FK index)
- `PerformansGostergeVeri.pg_id` (FK index)

---

### 15. SERVİS KATMANI

#### 15.1. Servis Dosyaları (15 Servis)

**15.1.1. project_service.py**
- `handle_task_completion()` - Görev tamamlama iş mantığı
- `_calculate_veri_tarihi()` - Periyoda göre tarih hesaplama
- `_get_periyot_bilgileri()` - Periyot meta data
- Transaction yönetimi
- Duplicate check
- PG veri otomasyon

**15.1.2. project_analytics.py**
- `calculate_surec_saglik_skoru()` - Süreç sağlık skoru hesaplama
- Proje tamamlanma oranı
- Gecikme cezası (%20)
- Kritik risk cezası (%15)
- Top 2 skor kıran faktör

**15.1.3. executive_dashboard.py**
- `get_corporate_health_score()` - Kurumsal sağlık skoru
- `get_critical_risks()` - Top 5 kritik risk
- `get_planning_efficiency()` - Planlama becerisi
- `get_task_workload_distribution()` - İş yükü dağılımı
- `get_personnel_workload_analysis()` - Personel yükü
- Filter desteği
- N+1 query optimizasyonu

**15.1.4. ai_early_warning.py**
- `calculate_delay_probability()` - Gecikme olasılığı
- Task analizi (%70 ağırlık)
- Risk analizi (%30 ağırlık)
- Faktör hesaplama

**15.1.5. ai_executive_summary.py**
- `generate_executive_summary()` - Yönetici özeti
- Top 3 risk analizi
- Top 3 görev analizi
- Doğal dil oluşturma

**15.1.6. ai_advisor_service.py**
- `generate_strategic_advice()` - Stratejik tavsiye
- `_generate_system_summary()` - Sistem özeti
- `_get_highlighted_risks()` - Öne çıkan riskler
- `_generate_ai_recommendations()` - AI tavsiyeleri
- `_analyze_project_process_relationships()` - İlişki analizi
- `_analyze_resource_distribution()` - Kaynak analizi
- `notify_recommendation()` - Tavsiye bildirimi

**15.1.7. notification_service.py**
- `create_task_overdue_notification()` - Gecikme bildirimi
- `create_critical_risk_notification()` - Risk bildirimi
- `check_pg_performance_deviation()` - PG sapma kontrolü
- `check_and_send_overdue_notifications()` - Background task

**15.1.8. report_service.py**
- `generate_project_pdf()` - Proje PDF raporu
- `generate_dashboard_pdf()` - Dashboard PDF raporu
- ReportLab entegrasyonu
- Grafik görselleri

**15.1.9. project_cloning.py**
- `clone_project()` - Proje klonlama
- Deep copy (tasks, subtasks, risks, files)
- Tarih kaydırma
- Durum sıfırlama

**15.1.10. performance_service.py**
- `generatePeriyotVerileri()` - Periyot verisi üretimi
- `calculateHedefDeger()` - Hedef değer hesaplama
- `hesapla_durum()` - Durum hesaplama (İyi/Orta/Kötü)
- `get_ceyrek_aylari()` - Çeyrek ay listesi
- `get_last_friday_of_month()` - Ayın son Cuma'sı

**15.1.11. background_tasks.py**
- `init_background_executor()` - APScheduler başlatma
- Periyodik görevler
- Bildirim kontrolü

**15.1.12. resource_planning.py**
- Kaynak optimizasyonu
- Yük dengeleme
- Bottleneck tespiti

**15.1.13. smart_scheduling.py**
- AI destekli zamanlama
- Görev önceliklendirme
- Tarih önerileri

**15.1.14. task_activity_service.py**
- Görev aktivite kaydı
- Değişiklik takibi
- Audit trail

**15.1.15. timesheet_service.py**
- Zaman kaydı yönetimi
- Süre hesaplamaları
- Rapor üretimi

---

### 16. GÜVENLİK

#### 16.1. Mevcut Güvenlik Önlemleri

**✅ İyi Yanlar:**
1. **CSRF Koruması:** Flask-WTF ile tüm form ve API istekleri korunuyor
2. **XSS Koruması:** Jinja2 otomatik escaping + manuel `escapeHtml()` fonksiyonları
3. **SQL Injection Koruması:** SQLAlchemy ORM kullanımı
4. **Password Hashing:** Werkzeug security ile şifre hashleme
5. **Session Security:** HTTP-only cookies, secure flag (production)
6. **Rate Limiting:** Flask-Limiter (200/hour, 50/minute)
7. **Authentication:** Flask-Login session yönetimi
8. **Authorization:** Decorator-based RBAC (`@project_access_required`)
9. **File Upload Security:** `secure_filename()` kullanımı
10. **Error Handling:** Custom 404/500 sayfaları, transaction rollback

**⚠️ İyileştirilebilir Alanlar:**
1. **Secret Key:** Hardcoded fallback var (production tehlikesi)
2. **CSP Headers:** Content Security Policy eksik
3. **Rate Limiting Storage:** Memory-based (Redis olmalı)
4. **Password Policy:** Minimum uzunluk/karmaşıklık kontrolü yok
5. **File MIME Check:** Sadece extension kontrolü var
6. **Session Timeout:** Activity-based renewal yok
7. **API Authentication:** JWT veya API key sistemi yok
8. **Logging:** Security event logging eksik (failed login, unauthorized access)
9. **Input Validation:** Schema validation eksik (Marshmallow/Pydantic)
10. **SSL/TLS:** HTTPS enforce yok

#### 16.2. Güvenlik Audit Checklist

**Yapılması Gerekenler:**
- [ ] SECRET_KEY production validation
- [ ] CSP headers ekleme
- [ ] Redis-based rate limiting
- [ ] Password complexity validation
- [ ] MIME type checking for uploads
- [ ] Failed login attempt logging
- [ ] API authentication system
- [ ] Input schema validation
- [ ] HTTPS redirect
- [ ] Security headers (X-Frame-Options, X-Content-Type-Options)

---

### 17. PERFORMANS

#### 17.1. Mevcut Optimizasyonlar

**✅ İyi Yanlar:**
1. **Database Indexing:** 20+ index tanımlı
2. **N+1 Query Fix:** `joinedload()`, `selectinload()` kullanımı
3. **Eager Loading:** İlişkili veriler tek sorguda
4. **Connection Pooling:** SQLAlchemy pool yapılandırması
5. **Query Optimization:** Composite indexler
6. **Archive Filter:** `is_archived=False` filtreleri
7. **Pagination:** Bazı listelerde sayfalama
8. **Caching Prep:** Flask-Caching yapılandırılmış

**⚠️ İyileştirilebilir Alanlar:**
1. **Cache Usage:** Redis cache kullanımı minimal
2. **Background Tasks:** Senkron işlemler (PDF, email)
3. **Query Caching:** Result caching yok
4. **Static File:** Minification yok
5. **Image Optimization:** WebP format yok
6. **CDN:** Static dosyalar için CDN yok
7. **Database Replication:** Read replica yok
8. **Load Balancing:** Horizontal scaling hazır değil

#### 17.2. Performans Metrikleri

**Test Edilmesi Gerekenler:**
- API response time (<200ms)
- Database query time (<100ms)
- Page load time (<2s)
- Dashboard render time (<3s)
- File upload speed
- PDF generation time
- Excel export time

---

## BÖLÜM 5: TEKNİK BORÇLAR VE İYİLEŞTİRMELER

### 18. KRİTİK ÖNCELİKLİ İYİLEŞTİRMELER

#### 18.1. Güvenlik (🔴 Acil)

**1. Secret Key Yönetimi**
```python
# Mevcut (tehlikeli)
SECRET_KEY = os.environ.get('SECRET_KEY') or 'your-secret-key-here-change-in-production'

# Önerilen
SECRET_KEY = os.environ.get('SECRET_KEY')
if not SECRET_KEY:
    if os.environ.get('FLASK_ENV') == 'production':
        raise ValueError("SECRET_KEY must be set in production")
    SECRET_KEY = 'dev-only-key'
```

**2. CSP Headers Ekleme**
```python
@app.after_request
def set_security_headers(response):
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    return response
```

**3. Rate Limiting Redis Migration**
```python
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200/hour", "50/minute"],
    storage_uri=os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
)
```

**4. Password Policy**
```python
def validate_password(password):
    if len(password) < 8:
        return False, "Şifre en az 8 karakter olmalı"
    if not re.search(r'[A-Z]', password):
        return False, "Şifre en az 1 büyük harf içermeli"
    if not re.search(r'[a-z]', password):
        return False, "Şifre en az 1 küçük harf içermeli"
    if not re.search(r'[0-9]', password):
        return False, "Şifre en az 1 rakam içermeli"
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Şifre en az 1 özel karakter içermeli"
    return True, "Geçerli"
```

**5. MIME Type Validation**
```python
import magic

def validate_file_type(file):
    # Extension check
    if not allowed_file(file.filename):
        return False
    
    # MIME type check
    mime = magic.Magic(mime=True)
    file_mime = mime.from_buffer(file.read(2048))
    file.seek(0)
    
    allowed_mimes = {
        'image/jpeg', 'image/png', 'image/gif',
        'application/pdf', 'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    }
    
    return file_mime in allowed_mimes
```

#### 18.2. Test Coverage (🔴 Acil)

**Mevcut Durum:**
- Sadece 1 test dosyası: `test_performance_service.py`
- Test coverage: ~%5-10 (tahmini)

**Hedef:**
- Test coverage: %80+
- Unit tests: Tüm servisler
- Integration tests: API endpoints
- E2E tests: Critical flows

**Eklenmesi Gereken Testler:**

1. **services/test_project_service.py**
```python
def test_handle_task_completion():
    # Task tamamlandığında PG verisi oluşturulmalı
    pass

def test_task_completion_rollback():
    # Hata durumunda task durumu geri dönmeli
    pass

def test_duplicate_prevention():
    # is_processed=True ise tekrar işlenmemeli
    pass
```

2. **services/test_project_analytics.py**
```python
def test_health_score_calculation():
    # Sağlık skoru doğru hesaplanmalı
    pass

def test_delay_penalty():
    # Geciken görevler %20 ceza vermeli
    pass

def test_critical_risk_penalty():
    # Kritik risk %15 düşürme yapmalı
    pass
```

3. **api/test_routes.py**
```python
def test_create_project():
    # POST /api/projeler başarılı olmalı
    pass

def test_unauthorized_access():
    # Yetkisiz erişim 403 dönmeli
    pass

def test_task_completion_triggers_pg():
    # Görev tamamlama PG tetiklemeli
    pass
```

4. **test_authentication.py**
```python
def test_login_success():
    pass

def test_login_failure():
    pass

def test_session_timeout():
    pass

def test_csrf_protection():
    pass
```

**Test Altyapısı:**
```python
# conftest.py
@pytest.fixture
def app():
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def auth_client(client):
    # Authenticated client
    pass
```

#### 18.3. Monitoring ve Logging (🔴 Önemli)

**Mevcut Durum:**
- Basic logging (RotatingFileHandler)
- Console logging (development)
- Error logging (500 errors)

**Önerilen İyileştirmeler:**

1. **Structured Logging**
```python
import structlog

logger = structlog.get_logger()
logger.info("user_login", user_id=user.id, ip=request.remote_addr)
logger.error("task_completion_failed", task_id=task.id, error=str(e))
```

2. **Security Event Logging**
```python
def log_security_event(event_type, user_id, details):
    SecurityLog.create(
        event_type=event_type,
        user_id=user_id,
        ip_address=request.remote_addr,
        details=details,
        timestamp=datetime.utcnow()
    )

# Kullanım
log_security_event('failed_login', user_id=None, details={'username': username})
log_security_event('unauthorized_access', user_id=current_user.id, details={'resource': '/admin-panel'})
```

3. **APM Integration (Sentry)**
```python
import sentry_sdk
from sentry_sdk.integrations.flask import FlaskIntegration

sentry_sdk.init(
    dsn=os.environ.get('SENTRY_DSN'),
    integrations=[FlaskIntegration()],
    traces_sample_rate=1.0
)
```

4. **Health Check Endpoint**
```python
@app.route('/health')
def health_check():
    try:
        # Database check
        db.session.execute(text('SELECT 1'))
        
        # Redis check (if available)
        # cache.get('health_check')
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'version': '1.8.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 503
```

#### 18.4. Caching Strategy (🔴 Önemli)

**Önerilen İmplementasyon:**

1. **Redis Setup**
```python
# config.py
CACHE_TYPE = 'redis'
CACHE_REDIS_URL = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
CACHE_DEFAULT_TIMEOUT = 300

# extensions.py
from flask_caching import Cache
cache = Cache()

# __init__.py
cache.init_app(app)
```

2. **Cache Usage**
```python
# Dashboard caching
@cache.cached(timeout=300, key_prefix='dashboard_exec')
def get_executive_dashboard(kurum_id, filters):
    return executive_dashboard.get_corporate_health_score(kurum_id, filters)

# User session caching
@cache.memoize(timeout=3600)
def get_user_permissions(user_id):
    return calculate_user_permissions(user_id)

# Query result caching
@cache.cached(timeout=600, key_prefix=lambda: f'projects_{current_user.kurum_id}')
def get_projects():
    return Project.query.filter_by(kurum_id=current_user.kurum_id).all()
```

3. **Cache Invalidation**
```python
# Görev tamamlandığında cache temizle
def handle_task_completion(task):
    # ... PG veri girişi ...
    cache.delete(f'dashboard_exec_{task.project.kurum_id}')
    cache.delete(f'health_score_{task.project.related_processes[0].id}')
```

#### 18.5. API Documentation (🔴 Önemli)

**Önerilen: Swagger/OpenAPI**

```python
from flask_restx import Api, Resource, fields, Namespace

api = Api(
    version='1.0',
    title='Stratejik Planlama API',
    description='SPSV2 REST API Dokümantasyonu',
    doc='/api/docs'
)

# Namespace'ler
projects_ns = Namespace('projects', description='Proje işlemleri')
tasks_ns = Namespace('tasks', description='Görev işlemleri')
dashboard_ns = Namespace('dashboard', description='Dashboard verileri')

# Model tanımları
project_model = api.model('Project', {
    'id': fields.Integer(description='Proje ID'),
    'name': fields.String(required=True, description='Proje adı'),
    'description': fields.String(description='Proje açıklaması'),
    'start_date': fields.Date(description='Başlangıç tarihi'),
    'end_date': fields.Date(description='Bitiş tarihi'),
    'priority': fields.String(description='Öncelik')
})

@projects_ns.route('/')
class ProjectList(Resource):
    @api.doc('list_projects')
    @api.marshal_list_with(project_model)
    def get(self):
        """Tüm projeleri listele"""
        return Project.query.all()
    
    @api.doc('create_project')
    @api.expect(project_model)
    @api.marshal_with(project_model, code=201)
    def post(self):
        """Yeni proje oluştur"""
        pass
```

**Erişim:** `http://localhost:5001/api/docs`

---

### 19. ORTA ÖNCELİKLİ İYİLEŞTİRMELER

#### 19.1. Code Quality

**1. Type Hints Ekleme**
```python
from typing import List, Dict, Optional, Tuple

def calculate_health_score(
    project_id: int, 
    filters: Optional[Dict] = None
) -> Tuple[float, List[str]]:
    """
    Proje sağlık skorunu hesapla
    
    Args:
        project_id: Proje ID
        filters: Filtreleme parametreleri
        
    Returns:
        Tuple[float, List[str]]: (skor, faktörler)
    """
    pass
```

**2. Custom Exceptions**
```python
# exceptions.py
class SPSException(Exception):
    """Base exception"""
    pass

class ProjectNotFoundError(SPSException):
    pass

class PermissionDeniedError(SPSException):
    pass

class InvalidDataError(SPSException):
    pass

# Kullanım
if not project:
    raise ProjectNotFoundError(f"Proje bulunamadı: {project_id}")
```

**3. Input Validation (Marshmallow)**
```python
from marshmallow import Schema, fields, validate

class ProjectSchema(Schema):
    name = fields.Str(required=True, validate=validate.Length(min=3, max=200))
    description = fields.Str()
    start_date = fields.Date(required=True)
    end_date = fields.Date(required=True)
    priority = fields.Str(validate=validate.OneOf(['Düşük', 'Orta', 'Yüksek', 'Acil']))
    manager_id = fields.Int(required=True)
    
    @validates_schema
    def validate_dates(self, data, **kwargs):
        if data['start_date'] > data['end_date']:
            raise ValidationError('Başlangıç tarihi bitiş tarihinden büyük olamaz')

# Kullanım
schema = ProjectSchema()
try:
    result = schema.load(request.json)
except ValidationError as err:
    return jsonify({'success': False, 'errors': err.messages}), 400
```

**4. Code Documentation**
- Tüm fonksiyonlara docstring
- Sphinx ile auto-documentation
- README improvement

**5. Code Linting**
```bash
# flake8 - PEP 8 compliance
flake8 . --max-line-length=120 --exclude=venv

# black - Code formatting
black . --line-length=120

# pylint - Code analysis
pylint **/*.py

# mypy - Type checking
mypy . --ignore-missing-imports
```

#### 19.2. Database Optimization

**1. Additional Composite Indexes**
```sql
-- Notification için
CREATE INDEX idx_notification_user_read 
ON notification(user_id, okundu, created_at DESC);

-- Task için
CREATE INDEX idx_task_due_status 
ON task(due_date, status) 
WHERE status != 'Tamamlandı';

-- Project için
CREATE INDEX idx_project_dates 
ON project(start_date, end_date, kurum_id);
```

**2. Query Optimization**
```python
# Mevcut
projects = Project.query.all()
for project in projects:
    tasks = project.tasks  # N+1 problem

# Önerilen
projects = Project.query.options(
    joinedload(Project.tasks),
    joinedload(Project.risks),
    joinedload(Project.manager),
    selectinload(Project.members)
).filter_by(kurum_id=kurum_id).all()
```

**3. Database Migrations**
- Alembic migration script'leri
- Version control
- Rollback capability

#### 19.3. Background Task Processing

**Celery Integration:**
```python
# celery_app.py
from celery import Celery

celery = Celery('sps', broker='redis://localhost:6379/0')

@celery.task
def generate_pdf_async(project_id):
    """PDF oluşturmayı background'da çalıştır"""
    pass

@celery.task
def send_notification_email(user_id, message):
    """Email gönderimi background'da"""
    pass

@celery.task(bind=True)
def check_overdue_tasks(self):
    """Her gün gecikmiş görevleri kontrol et"""
    pass
```

**Periodic Tasks:**
```python
from celery.schedules import crontab

celery.conf.beat_schedule = {
    'check-overdue-tasks-daily': {
        'task': 'tasks.check_overdue_tasks',
        'schedule': crontab(hour=8, minute=0),  # Her gün saat 08:00
    },
    'update-dashboard-cache': {
        'task': 'tasks.update_dashboard_cache',
        'schedule': crontab(minute='*/5'),  # Her 5 dakikada
    },
}
```

#### 19.4. Pagination Implementation

```python
# api/routes.py
@api_bp.route('/projeler', methods=['GET'])
@login_required
def api_projeler():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    per_page = min(per_page, 100)  # Max 100
    
    pagination = Project.query.filter_by(
        kurum_id=current_user.kurum_id,
        is_archived=False
    ).paginate(
        page=page,
        per_page=per_page,
        error_out=False
    )
    
    return jsonify({
        'success': True,
        'projects': [p.to_dict() for p in pagination.items],
        'total': pagination.total,
        'pages': pagination.pages,
        'current_page': pagination.page,
        'has_next': pagination.has_next,
        'has_prev': pagination.has_prev
    })
```

---

### 20. GELECEK ÖZELLİKLER (🟢 Düşük Öncelik)

#### 20.1. Real-time Features

**WebSocket Integration (Flask-SocketIO):**
```python
from flask_socketio import SocketIO, emit

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on('task_update')
def handle_task_update(data):
    # Görev güncellendiğinde tüm proje üyelerine bildir
    emit('task_updated', data, broadcast=True, room=f"project_{data['project_id']}")

@socketio.on('join_project')
def on_join(data):
    room = f"project_{data['project_id']}"
    join_room(room)
```

**Kullanım Senaryoları:**
- Real-time görev güncellemeleri
- Live bildirimler
- Canlı dashboard güncellemeleri
- Collaborative editing

#### 20.2. Mobile Native App

**React Native / Flutter:**
- iOS ve Android native app
- Push notifications
- Offline support
- Camera integration
- GPS tagging (saha raporu için)
- Biometric authentication

#### 20.3. Advanced Analytics

**Machine Learning:**
- Proje başarı tahmini
- Optimum kaynak dağılımı
- Anomaly detection
- Predictive maintenance

**Business Intelligence:**
- Custom dashboard builder
- Drill-down analizi
- What-if analizi
- Trend prediction

#### 20.4. Integration Capabilities

**Webhook Support:**
```python
@api_bp.route('/webhooks/<event_type>', methods=['POST'])
def webhook_handler(event_type):
    # External system'lere event gönderme
    pass
```

**Third-party Integrations:**
- Slack notifications
- Microsoft Teams integration
- Jira sync
- Google Calendar sync
- Email automation (SMTP)

**GraphQL API:**
```python
from flask_graphql import GraphQLView
from graphene import ObjectType, String, Schema

class Query(ObjectType):
    project = String(project_id=String())
    
    def resolve_project(self, info, project_id):
        return Project.query.get(project_id)

schema = Schema(query=Query)

app.add_url_rule('/graphql', view_func=GraphQLView.as_view('graphql', schema=schema, graphiql=True))
```

#### 20.5. Internationalization

**Flask-Babel:**
```python
from flask_babel import Babel, gettext as _

babel = Babel(app)

# Kullanım
_('Proje başarıyla oluşturuldu')
```

**Desteklenebilecek Diller:**
- Türkçe (mevcut)
- İngilizce
- Almanca
- Fransızca

---

## BÖLÜM 6: DEPLOYMENT VE BAKIM

### 21. PRODUCTION HAZIRLIK

#### 21.1. Production Checklist

**Environment Configuration:**
- [x] Flask environment variables
- [ ] SECRET_KEY güçlü ve benzersiz
- [ ] DEBUG=False
- [ ] TESTING=False
- [ ] Database credentials secure
- [ ] SESSION_COOKIE_SECURE=True
- [ ] WTF_CSRF_ENABLED=True
- [ ] Rate limiting Redis'e bağlı
- [ ] Logging production-ready
- [ ] Error tracking (Sentry)

**Infrastructure:**
- [ ] WSGI server (Waitress/Gunicorn)
- [ ] Reverse proxy (Nginx)
- [ ] SSL certificate (Let's Encrypt)
- [ ] Database backup automated
- [ ] Redis server
- [ ] Static files CDN

**Security:**
- [ ] Security headers eklendi
- [ ] File upload limits
- [ ] API rate limiting
- [ ] SQL injection testleri
- [ ] XSS testleri
- [ ] Penetration testing

**Performance:**
- [ ] Database indexes
- [ ] Query optimization
- [ ] Caching active
- [ ] Static file compression
- [ ] Image optimization
- [ ] Load testing completed

**Monitoring:**
- [ ] APM (Sentry/New Relic)
- [ ] Log aggregation (ELK)
- [ ] Uptime monitoring
- [ ] Alert system
- [ ] Health check endpoint

#### 21.2. Docker Deployment

**Dockerfile:**
```dockerfile
FROM python:3.11-slim

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    unixodbc-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ODBC Driver for SQL Server
RUN curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
    && curl https://packages.microsoft.com/config/debian/11/prod.list > /etc/apt/sources.list.d/mssql-release.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y msodbcsql17

WORKDIR /app

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code
COPY . .

# Environment
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5001

# Run with Waitress
CMD ["waitress-serve", "--host=0.0.0.0", "--port=5001", "--threads=4", "app:app"]
```

**docker-compose.yml:**
```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5001:5001"
    environment:
      - FLASK_ENV=production
      - SECRET_KEY=${SECRET_KEY}
      - SQL_SERVER=db
      - SQL_DATABASE=stratejik_planlama
      - SQL_USERNAME=sa
      - SQL_PASSWORD=${DB_PASSWORD}
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./static/uploads:/app/static/uploads
      - ./logs:/app/logs

  db:
    image: mcr.microsoft.com/mssql/server:2019-latest
    environment:
      - ACCEPT_EULA=Y
      - SA_PASSWORD=${DB_PASSWORD}
    ports:
      - "1433:1433"
    volumes:
      - db_data:/var/opt/mssql

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - web

volumes:
  db_data:
```

#### 21.3. CI/CD Pipeline

**GitHub Actions Example:**
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest pytest-cov flake8
      
      - name: Lint with flake8
        run: flake8 . --max-line-length=120
      
      - name: Run tests
        run: pytest --cov=. --cov-report=xml
      
      - name: Upload coverage
        uses: codecov/codecov-action@v3

  deploy:
    needs: test
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to production
        run: |
          # Docker build and push
          # Kubernetes deployment
          # Or server deployment
```

---

### 22. BAKIM VE İZLEME

#### 22.1. Monitoring Strategy

**1. Application Performance Monitoring (APM)**
- Sentry.io - Error tracking
- New Relic / DataDog - APM
- Grafana + Prometheus - Metrics

**2. Uptime Monitoring**
- UptimeRobot
- Pingdom
- StatusCake

**3. Log Aggregation**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- AWS CloudWatch
- Splunk

**4. Metrics to Track**
- Request per second (RPS)
- Response time (p50, p95, p99)
- Error rate
- Database query time
- Cache hit rate
- Active users
- Task completion rate
- PG data entry rate

#### 22.2. Alerting Rules

```yaml
alerts:
  - name: high_error_rate
    condition: error_rate > 5%
    severity: critical
    notification: email, slack
    
  - name: slow_response_time
    condition: p95_response_time > 2000ms
    severity: warning
    notification: slack
    
  - name: database_connection_failure
    condition: db_health_check_failed
    severity: critical
    notification: email, sms, slack
    
  - name: disk_space_low
    condition: disk_usage > 85%
    severity: warning
    notification: email
```

#### 22.3. Maintenance Tasks

**Günlük:**
- Log rotation check
- Backup verification
- Error rate monitoring
- Performance metrics review

**Haftalık:**
- Database query performance analysis
- Failed login attempts review
- Security audit log review
- User feedback review

**Aylık:**
- Dependency updates check
- Security vulnerability scan
- Database index optimization
- Performance baseline update

**Çeyreklik:**
- Full security audit
- Disaster recovery test
- Capacity planning
- Feature usage analysis

---

### 23. YEDEKLEME VE GÜVENLİK

#### 23.1. Backup Strategy

**Database Backup:**
```bash
# Daily full backup
0 2 * * * /usr/bin/backup-database.sh

# Hourly incremental backup
0 * * * * /usr/bin/backup-incremental.sh

# Weekly verification
0 3 * * 0 /usr/bin/verify-backup.sh
```

**File Backup:**
- `static/uploads/` klasörü
- Daily backup
- 30 gün retention

**Configuration Backup:**
- Environment variables
- nginx config
- SSL certificates
- Encryption keys

**Backup Storage:**
- Local storage (7 gün)
- Cloud storage (AWS S3, Azure Blob)
- Offsite backup (30 gün)

**Restoration SLA:**
- RTO (Recovery Time Objective): <4 saat
- RPO (Recovery Point Objective): <1 saat

#### 23.2. Disaster Recovery Plan

**Senaryolar:**
1. Database corruption
2. Server failure
3. Data center outage
4. Ransomware attack
5. Human error (data deletion)

**Recovery Steps:**
1. Assess damage
2. Notify stakeholders
3. Restore from backup
4. Verify data integrity
5. Resume operations
6. Post-mortem analysis

---

## 📊 ÖZET VE DEĞERLENDİRME

### Güçlü Yanlar ✅

1. **Kapsamlı Özellik Seti:** Stratejik planlama, süreç yönetimi, proje yönetimi, performans takibi entegre
2. **İyi Mimari:** Katmanlı mimari, service layer, clean separation
3. **Güvenlik Temel:** CSRF, XSS, SQL injection korumaları mevcut
4. **Mobil Uyumluluk:** Responsive tasarım, mobil optimizasyon
5. **AI Entegrasyonu:** Erken uyarı, stratejik danışman, özet üretimi
6. **Otomatik Veri Akışı:** Görev-PG otomasyonu
7. **Executive Dashboard:** Üst yönetim için görsel analitik
8. **Esnek Periyot:** 5 farklı periyot tipi desteği
9. **Rol Tabanlı Erişim:** RBAC decorator'ları
10. **Dokümantasyon:** Detaylı geliştirme durumu dokümanı

### Zayıf Yanlar ve İyileştirme Alanları ⚠️

1. **Test Coverage Düşük:** %5-10 (Hedef: %80+)
2. **Secret Key Risk:** Hardcoded fallback
3. **Cache Kullanımı:** Minimal, Redis entegrasyonu yok
4. **API Dokümantasyonu:** Swagger/OpenAPI eksik
5. **Background Tasks:** Senkron işlemler (PDF, email)
6. **Monitoring:** APM eksik
7. **Type Hints:** Tutarsız kullanım
8. **Input Validation:** Schema validation eksik
9. **Pagination:** Bazı endpoint'lerde yok
10. **Security Headers:** CSP, HSTS eksik

### Teknik Borç Skoru: 6.5/10

**Açıklama:**
- **Güvenlik:** 7/10 (Temel güvenlik iyi, ama iyileştirmeler gerekli)
- **Performans:** 7/10 (Index'ler iyi, cache eksik)
- **Test:** 3/10 (Çok yetersiz)
- **Dokümantasyon:** 8/10 (Code doc eksik, user doc iyi)
- **Maintainability:** 7/10 (İyi organize, ama type hints eksik)
- **Scalability:** 6/10 (Horizontal scaling hazır değil)

### Production Readiness: 75%

**Eksikler:**
- 25% → Test coverage + Security hardening + Monitoring

---

## 🎯 ÖNCELİK ROADMAP

### Faz 1: Acil (1-2 Hafta)
1. Secret key yönetimi düzeltme
2. Security headers ekleme
3. Health check endpoint
4. Unit test coverage başlangıcı (%30)
5. API dokümantasyonu (Swagger)

### Faz 2: Kısa Vade (1 Ay)
1. Test coverage %60'a çıkarma
2. Redis caching
3. Background task processing (Celery)
4. Input validation (Marshmallow)
5. Type hints ekleme

### Faz 3: Orta Vade (3 Ay)
1. Test coverage %80'e çıkarma
2. APM integration (Sentry)
3. CI/CD pipeline
4. Docker containerization
5. Performance optimization

### Faz 4: Uzun Vade (6+ Ay)
1. Real-time features (WebSocket)
2. Mobile app development
3. Advanced ML analytics
4. Microservices migration (opsiyonel)
5. Internationalization

---

## 📈 SON DEĞERLENDİRME

**Proje Durumu:** ✅ PRODUCTION-READY (Uyarılarla Birlikte)

**Kullanılabilir mi?** EVET, ancak:
- Secret key production'da mutlaka değiştirilmeli
- Test coverage artırılmalı
- Monitoring eklenmeli
- Backup stratejisi uygulanmalı

**Ölçeklenebilir mi?** KISMEN
- 100-500 kullanıcı: ✅ Sorunsuz
- 500-1000 kullanıcı: ⚠️ Cache ve optimization gerekli
- 1000+ kullanıcı: ❌ Microservices migration gerekli

**Güvenli mi?** KISMEN
- Temel güvenlik: ✅ İyi
- Advanced security: ⚠️ İyileştirme gerekli
- Compliance (ISO 27001): ❌ Ek kontroller gerekli

**Bakımı Kolay mı?** EVET
- İyi organize kod yapısı
- Service layer ayrımı
- Dokümantasyon mevcut

---

**Rapor Sonu**  
**Toplam Sayfa:** Rapor kapsam olarak ~50+ sayfa equivalent  
**Analiz Derinliği:** Detaylı  
**Tarih:** 21 Aralık 2025