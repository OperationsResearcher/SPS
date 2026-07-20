# Kokpitim Projesi Bileşen ve Kod Analiz Raporu

**Analiz Tarihi:** 2026-06-09  
**Rapor Amacı:** Kokpitim projesinin aktif dizinlerindeki bileşenlerin, kod hacimlerinin ve işlevlerinin detaylı envanteri.  

## 📊 Genel Özet

| Metrik | Değer |
| :--- | :--- |
| **Toplam Dosya Sayısı** | 1417 |
| **Toplam Satır Sayısı** | 3,467,856 |
| **Boş Satır Sayısı** | 38,474 |
| **Yorum Satırı Sayısı** | 25,475 |
| **Net Kod Satırı sayısı (SLOC)** | 3,403,907 |

## 🧩 Bileşen Dağılımı ve Kod Oranları

| Bileşen (Klasör) | Dosya | Toplam Satır | Yorum Satırı | Net Kod Satırı | Oran (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| `docs` | 33 | 3,155,038 | 22 | 3,154,631 | 92.68% |
| `templates` | 135 | 61,454 | 838 | 55,902 | 1.64% |
| `ui` | 253 | 53,494 | 1,050 | 48,333 | 1.42% |
| `static` | 108 | 29,605 | 1,492 | 23,596 | 0.69% |
| `micro` | 106 | 27,529 | 2,226 | 21,867 | 0.64% |
| `app` | 144 | 29,433 | 5,500 | 19,568 | 0.57% |
| `Root` | 124 | 24,295 | 2,275 | 18,202 | 0.53% |
| `scripts` | 193 | 23,786 | 4,027 | 16,616 | 0.49% |
| `skills` | 77 | 16,699 | 1,260 | 12,407 | 0.36% |
| `migrations` | 76 | 10,127 | 1,102 | 7,874 | 0.23% |
| `services` | 42 | 11,173 | 1,643 | 7,571 | 0.22% |
| `prototypes` | 31 | 4,406 | 12 | 4,094 | 0.12% |
| `main` | 9 | 7,773 | 2,704 | 3,820 | 0.11% |
| `api` | 3 | 4,807 | 366 | 3,751 | 0.11% |
| `tests` | 52 | 4,187 | 424 | 2,813 | 0.08% |
| `models` | 7 | 1,082 | 203 | 670 | 0.02% |
| `brosur` | 1 | 697 | 25 | 628 | 0.02% |
| `v3` | 2 | 568 | 70 | 404 | 0.01% |
| `utils` | 5 | 581 | 150 | 291 | 0.01% |
| `data` | 3 | 279 | 0 | 279 | 0.01% |
| `auth` | 2 | 386 | 47 | 259 | 0.01% |
| `bsc` | 2 | 174 | 2 | 133 | 0.00% |
| `v2` | 2 | 191 | 33 | 126 | 0.00% |
| `platform_core` | 1 | 39 | 4 | 31 | 0.00% |
| `.github` | 1 | 34 | 0 | 28 | 0.00% |
| `app_platform` | 4 | 16 | 0 | 10 | 0.00% |
| `.vscode` | 1 | 3 | 0 | 3 | 0.00% |

---

## 🔍 Detaylı Bileşen Analizi

### 📦 Bileşen: docs/

Proje dizininde yer alan yardımcı veya özel amaçlı klasör bileşeni.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.json` | 6 | 3,149,780 | 0 | 0 | 3,149,780 |
| `.html` | 4 | 3,532 | 160 | 9 | 3,363 |
| `.yaml` | 19 | 1,573 | 199 | 0 | 1,374 |
| `.py` | 4 | 153 | 26 | 13 | 114 |

### 📦 Klasik Jinja2 Şablonları (templates/)

Uygulamanın ana Jinja2 HTML şablonlarıdır. Base şablonlar, giriş ekranları, süreç karnesi sayfaları ve çeşitli dashboard ekranlarının arayüz tasarımlarını içerir.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.html` | 135 | 61,454 | 4,714 | 838 | 55,902 |

### 📦 Kullanıcı Arayüzü Şablon ve Varlıkları (ui/)

Modüler mikro arayüzün şablonlarını (templates), JavaScript dosyalarını ve CSS stillerini barındırır. Modern arayüzün (Tailwind, Alpine.js vb.) frontend bileşenleri bu dizinden yüklenir.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.html` | 157 | 23,954 | 1,581 | 225 | 22,148 |
| `.js` | 77 | 20,940 | 1,410 | 580 | 18,950 |
| `.css` | 19 | 8,600 | 1,120 | 245 | 7,235 |

### 📦 Küresel Statik Dosyalar (static/)

Uygulama genelinde kullanılan CSS, JS, font ve resim dosyaları ile yerel olarak indirilen üçüncü parti kütüphaneleri (Bootstrap, Chart.js, jQuery vb.) içerir.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.js` | 60 | 19,748 | 3,254 | 1,230 | 15,264 |
| `.css` | 41 | 9,333 | 1,231 | 262 | 7,840 |
| `.html` | 5 | 301 | 32 | 0 | 269 |
| `.json` | 2 | 223 | 0 | 0 | 223 |

### 📦 Mikro Hizmet / Modül Katmanı (micro/)

SaaS mimarisine uygun olarak tasarlanmış modüler yapıdır. Her özellik alanı (admin, analiz, bireysel karne, süreç, stratejik planlama vb.) bağımsız birer modül olarak `/micro/modules` altında yer alır. Bu sayede modüller kolayca genişletilebilir veya devre dışı bırakılabilir.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 106 | 27,529 | 3,436 | 2,226 | 21,867 |

**Mikro Modüller (micro/modules/):**
- **`__pycache__`**: Modülün `/micro/modules/__pycache__` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`admin`**: Modülün `/micro/modules/admin` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`analiz`**: Modülün `/micro/modules/analiz` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`api`**: Modülün `/micro/modules/api` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`bireysel`**: Modülün `/micro/modules/bireysel` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`demo`**: Modülün `/micro/modules/demo` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`hgs`**: Modülün `/micro/modules/hgs` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`k_radar`**: Modülün `/micro/modules/k_radar` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`k_rapor`**: Modülün `/micro/modules/k_rapor` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`kurum`**: Modülün `/micro/modules/kurum` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`marketing`**: Modülün `/micro/modules/marketing` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`masaustu`**: Modülün `/micro/modules/masaustu` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`proje`**: Modülün `/micro/modules/proje` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`raporlar`**: Modülün `/micro/modules/raporlar` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`shared`**: Modülün `/micro/modules/shared` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`sp`**: Modülün `/micro/modules/sp` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.
- **`surec`**: Modülün `/micro/modules/surec` altındaki rotalarını, veri doğrulama mantığını ve özel fonksiyonlarını barındırır.

### 📦 Modern Flask Uygulama Katmanı (app/)

Uygulamanın yeni ve modern Flask katmanıdır. Blueprint rotaları, veritabanı modelleri, veri şemaları (schemas), iş mantığı servisleri, socketio olayları, çok dilli destek (i18n), yetkilendirme ve güvenlik middleware bileşenlerini barındırır. Projenin ana yürütme motorudur.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 143 | 29,359 | 4,365 | 5,500 | 19,494 |
| `.json` | 1 | 74 | 0 | 0 | 74 |

### 📦 Kök Dizin Dosyaları (Root/)

Uygulamanın giriş noktası (`app.py`), temel ayarlar (`config.py`), veritabanı ilklendiricisi (`init_db.py`), sunucu çalıştırma betiği (`run.py`) ve konfigürasyon dosyalarını içerir.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 111 | 18,626 | 2,870 | 1,927 | 13,829 |
| `.js` | 3 | 3,755 | 600 | 191 | 2,964 |
| `.html` | 2 | 672 | 72 | 0 | 600 |
| `.sql` | 6 | 920 | 226 | 156 | 538 |
| `.css` | 1 | 300 | 49 | 1 | 250 |
| `.yml` | 1 | 22 | 1 | 0 | 21 |

### 📦 Yönetim ve Operasyon Betikleri (scripts/)

Veritabanı migration'ları, test verisi üretme (seeding), veri aktarımı, üretim ortamı hazırlık kontrolleri ve bakım operasyonları için geliştirilmiş yardımcı Python ve SQL betikleridir.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 184 | 23,562 | 3,120 | 4,001 | 16,441 |
| `.sql` | 9 | 224 | 23 | 26 | 175 |

### 📦 Ajan Yetenekleri ve Otomasyon (skills/)

Yapay zeka asistanının ve geliştirme ajanlarının kullandığı otonom yetenekleri, otomasyon betiklerini ve özel geliştirici araçlarını barındırır.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 72 | 14,351 | 2,777 | 1,098 | 10,476 |
| `.html` | 3 | 2,070 | 219 | 38 | 1,813 |
| `.js` | 1 | 223 | 36 | 124 | 63 |
| `.json` | 1 | 55 | 0 | 0 | 55 |

### 📦 Veritabanı Göç Dosyaları (migrations/)

Alembic ve Flask-Migrate tarafından yönetilen, veritabanı şemasındaki değişikliklerin geçmişini tutan göç (migration) dosyalarıdır.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 76 | 10,127 | 1,151 | 1,102 | 7,874 |

### 📦 İş Mantığı ve Arka Plan Servisleri (services/)

Uygulamanın arka planda çalışan zamanlanmış görevleri (apscheduler), otomatik yedekleme (yedekleme_service), erken uyarı mekanizmaları (early_warning_service) ve raporlama motorlarını yöneten servis katmanıdır.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 42 | 11,173 | 1,959 | 1,643 | 7,571 |

### 📦 Prototip Tasarımlar (prototypes/)

Yeni geliştirilecek özelliklerin arayüz ve akış denemelerinin yapıldığı sandbox ortamı ve şablon tasarımlarıdır.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.html` | 24 | 3,474 | 176 | 4 | 3,294 |
| `.js` | 5 | 491 | 57 | 6 | 428 |
| `.css` | 2 | 441 | 67 | 2 | 372 |

### 📦 Klasik Ana Rotalar (main/)

Uygulamanın eski/klasik döneminden kalan monolitik yapıda ana sayfa yönlendirmelerini ve bazı süreç şablonlarını sunan route katmanıdır.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 9 | 7,773 | 1,249 | 2,704 | 3,820 |

### 📦 Klasik API Arayüzü (api/)

Eski mimariden kalan, projeler, RAID analizleri, görevler ve SLA takipleri için kullanılan REST API uç noktalarını barındırır.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 3 | 4,807 | 690 | 366 | 3,751 |

### 📦 Otomatik Testler (tests/)

Sistemin iş mantığını, yetkilendirme sınırlarını ve veri bütünlüğünü doğrulayan otomatik birim (unit) ve entegrasyon testlerini içerir.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 52 | 4,187 | 950 | 424 | 2,813 |

### 📦 Klasik Veritabanı Modelleri (models/)

Eski mimaride kullanılan veritabanı şablonlarını ve modellerini (LegacyUser, Surec, AnaStrateji vb.) tanımlayan sınıfları içerir.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 7 | 1,082 | 209 | 203 | 670 |

### 📦 Bileşen: brosur/

Proje dizininde yer alan yardımcı veya özel amaçlı klasör bileşeni.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.html` | 1 | 697 | 44 | 25 | 628 |

### 📦 Bileşen: v3/

Proje dizininde yer alan yardımcı veya özel amaçlı klasör bileşeni.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 2 | 568 | 94 | 70 | 404 |

### 📦 Yardımcı Araçlar (utils/)

Dosya işlemleri, veri formatlama ve şifreleme gibi genel amaçlı yardımcı fonksiyonları barındıran araç modülleridir.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 5 | 581 | 140 | 150 | 291 |

### 📦 Bileşen: data/

Proje dizininde yer alan yardımcı veya özel amaçlı klasör bileşeni.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.json` | 3 | 279 | 0 | 0 | 279 |

### 📦 Klasik Yetkilendirme (auth/)

Eski mimarideki oturum açma, kapama ve kullanıcı kaydı işlemlerini yöneten auth bileşenleridir.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 2 | 386 | 80 | 47 | 259 |

### 📦 Bileşen: bsc/

Proje dizininde yer alan yardımcı veya özel amaçlı klasör bileşeni.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 2 | 174 | 39 | 2 | 133 |

### 📦 Bileşen: v2/

Proje dizininde yer alan yardımcı veya özel amaçlı klasör bileşeni.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 2 | 191 | 32 | 33 | 126 |

### 📦 Bileşen: platform_core/

Proje dizininde yer alan yardımcı veya özel amaçlı klasör bileşeni.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 1 | 39 | 4 | 4 | 31 |

### 📦 Bileşen: .github/

Proje dizininde yer alan yardımcı veya özel amaçlı klasör bileşeni.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.yml` | 1 | 34 | 6 | 0 | 28 |

### 📦 Bileşen: app_platform/

Proje dizininde yer alan yardımcı veya özel amaçlı klasör bileşeni.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.py` | 4 | 16 | 6 | 0 | 10 |

### 📦 Bileşen: .vscode/

Proje dizininde yer alan yardımcı veya özel amaçlı klasör bileşeni.

**Kod Dağılım İstatistikleri:**

| Uzantı | Dosya Sayısı | Toplam Satır | Boş Satır | Yorum Satırı | Net Kod |
| :---: | :---: | :---: | :---: | :---: | :---: |
| `.json` | 1 | 3 | 0 | 0 | 3 |


✅ Sayfa tarayıcıda açıldı, konsol hatası taranmadı ve görsel olarak doğrulandı.
