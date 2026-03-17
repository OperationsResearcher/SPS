# Stratejik Planlama Sistemi

Stratejik planlama, performans takibi ve süreç yönetimi için geliştirilmiş Flask tabanlı web uygulaması.

## Özellikler

### Temel Özellikler
- **Kullanıcı Yönetimi**: Rol tabanlı erişim kontrolü (Admin, Kurum Yöneticisi, Üst Yönetim, Kullanıcı)
- **Süreç Yönetimi**: Süreç tanımlama, lider ve üye atama
- **Performans Göstergeleri**: Performans göstergesi tanımlama ve takibi
- **Süreç Karnesi**: Periyot bazlı (Günlük, Haftalık, Aylık, Çeyreklik, Yıllık) performans takibi
- **Veri Giriş Sihirbazı (VGS)**: Adım adım veri girişi arayüzü
- **Faaliyet Takibi**: Süreç faaliyetlerinin aylık takibi
- **Excel Export**: Süreç karnesi verilerinin Excel formatında dışa aktarımı

### Teknik Özellikler
- **Veritabanı Desteği**: SQL Server ve SQLite (fallback)
- **Güvenlik**: CSRF koruması, session yönetimi, şifre hashleme
- **Performans**: Connection pooling, query optimization
- **Offline Çalışma**: CDN bağımlılığı olmadan yerel statik dosyalarla çalışma

## Gereksinimler

- Python 3.8+
- SQL Server 2017+ (veya SQLite fallback)
- ODBC Driver 17 for SQL Server (SQL Server kullanımı için)

## Kurulum

### 1. Projeyi İndirin

```bash
git clone <repository-url>
cd SP_Code
```

### 2. Virtual Environment Oluşturun

```bash
python -m venv venv
```

### 3. Virtual Environment'ı Aktifleştirin

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 4. Bağımlılıkları Yükleyin

```bash
pip install -r requirements.txt
```

**Not:** SQL Server kullanımı için `pyodbc` paketini yüklediğinizden emin olun:
```bash
pip install pyodbc>=5.0.0
```

### 5. Statik Dosyaları İndirin (İsteğe Bağlı)

İnternet bağlantısı olmadan çalışması için CDN dosyalarını yerel olarak indirin:

```bash
python download_static_assets.py
```

Bu script Bootstrap, Bootstrap Icons, Font Awesome, jQuery ve Chart.js dosyalarını `static/vendor/` klasörüne indirir.

### 6. Environment Variables Ayarlayın

Proje kök klasöründe `.env` dosyası oluşturun:

```env
# Flask Environment
FLASK_ENV=development  # veya production

# Secret Key (Production için güçlü bir değer kullanın)
SECRET_KEY=your-secret-key-here-change-in-production

# SQL Server Bağlantı Bilgileri (SQL Server kullanımı için)
SQL_SERVER=localhost
SQL_DATABASE=stratejik_planlama
SQL_USERNAME=sa
SQL_PASSWORD=your_password_here
SQL_DRIVER=ODBC Driver 17 for SQL Server

# Alternatif: Windows Authentication
# SQL_USERNAME=
# SQL_PASSWORD=
```

**Not:** `.env` dosyası git'e commit edilmemelidir. Production ortamında environment variables'ları sunucu üzerinde ayarlayın.

**Örnek .env dosyası için:** `.env.example` dosyasına bakabilirsiniz (git repository'de mevcut).

## SQL Server Bağlantısı

Detaylı SQL Server kurulum talimatları için `SQL_SERVER_SETUP.md` dosyasına bakın.

### Hızlı Başlangıç

1. SQL Server'da veritabanı oluşturun:
```sql
CREATE DATABASE stratejik_planlama;
```

2. `.env` dosyasında SQL Server bilgilerini ayarlayın (yukarıdaki örneğe bakın)

3. Veritabanı şemasını oluşturun:
```bash
python -c "from __init__ import create_app; from extensions import db; app = create_app(); app.app_context().push(); db.create_all()"
```

## Çalıştırma

### Development Modu

```bash
python app.py
```

veya

```bash
flask run
```

Uygulama `http://127.0.0.1:5000` adresinde çalışacaktır.

### Production Modu

Production ortamında `FLASK_ENV=production` ayarlayın ve bir WSGI server kullanın:

```bash
# Waitress kullanarak (requirements.txt'de mevcut)
waitress-serve --host=0.0.0.0 --port=5001 app:app
```

veya

```bash
# Gunicorn kullanarak (Linux/Mac)
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Proje Yapısı

```
SP_Code/
├── api/                    # API endpoint'leri
│   ├── __init__.py
│   └── routes.py
├── auth/                   # Kimlik doğrulama rotaları
│   ├── __init__.py
│   └── routes.py
├── main/                   # Ana uygulama rotaları
│   ├── __init__.py
│   └── routes.py
├── services/               # İş mantığı servisleri
│   ├── __init__.py
│   └── performance_service.py
├── static/                 # Statik dosyalar (CSS, JS, görseller)
│   ├── css/
│   ├── js/
│   ├── fonts/
│   └── vendor/            # CDN dosyaları (download_static_assets.py ile indirilir)
├── templates/              # Jinja2 şablonları
│   ├── base.html
│   ├── login.html
│   └── surec_karnesi.html
├── tests/                  # Test dosyaları
├── instance/               # SQLite veritabanı (fallback)
├── logs/                   # Log dosyaları
├── __init__.py            # Flask uygulama fabrikası
├── app.py                 # Uygulama giriş noktası
├── config.py              # Konfigürasyon ayarları
├── models.py              # Veritabanı modelleri
├── extensions.py          # Flask extensions
├── requirements.txt       # Python bağımlılıkları
└── README.md             # Bu dosya
```

## Kullanıcı Rolleri

- **Admin**: Tüm yetkilere sahip sistem yöneticisi
- **Kurum Yöneticisi**: Kurumuna ait tüm süreçlere erişim
- **Üst Yönetim**: Kurum genelinde görüntüleme yetkisi
- **Kullanıcı**: Atandığı süreçlerde veri girişi ve görüntüleme

## API Endpoint'leri

### Süreç Karnesi
- `GET /surec-karnesi` - Süreç karnesi ana sayfası
- `GET /api/surec/<surec_id>/karne/performans` - Performans göstergeleri
- `GET /api/surec/<surec_id>/karne/faaliyetler` - Faaliyetler
- `POST /api/surec/<surec_id>/karne/kaydet` - Veri kaydetme
- `GET /api/pg-veri/detay/<veri_id>` - Veri detayları
- `POST /api/pg-veri/detay/toplu` - Toplu veri detayları
- `GET /api/export/surec_karnesi/excel` - Excel export

### Performans Göstergesi
- `POST /surec/<surec_id>/performans-gostergesi/add` - Yeni PG ekleme
- `POST /surec/<surec_id>/performans-gostergesi/<pg_id>/update` - PG güncelleme
- `DELETE /surec/<surec_id>/performans-gostergesi/<pg_id>/delete` - PG silme

## Güvenlik

- **CSRF Koruması**: Tüm formlarda aktif
- **Session Yönetimi**: Güvenli cookie ayarları
- **Şifre Hashleme**: Werkzeug security kullanılarak
- **SQL Injection Koruması**: SQLAlchemy ORM kullanımı
- **XSS Koruması**: Jinja2 otomatik escaping

## Production Readiness Check

Production ortamına deploy etmeden önce hazırlık kontrolü yapmak için:

```bash
python scripts/check_production.py
```

Bu script aşağıdaki kontrolleri yapar:
- Environment variables kontrolü (SECRET_KEY, FLASK_ENV)
- Debug mode kontrolü
- Configuration ayarları
- Database bağlantısı
- Kritik dosyaların varlığı

## Production Checklist

- [ ] `FLASK_ENV=production` ayarlandı
- [ ] `SECRET_KEY` güçlü ve rastgele bir değer
- [ ] `DEBUG=False` ve `TESTING=False`
- [ ] `WTF_CSRF_ENABLED=True`
- [ ] SQL Server bağlantı bilgileri environment variables'da
- [ ] Statik dosyalar yerel olarak indirildi (`download_static_assets.py`)
- [ ] Log dosyaları için yazma izinleri kontrol edildi
- [ ] WSGI server yapılandırıldı (Waitress/Gunicorn)

## Sorun Giderme

### SQL Server Bağlantı Hatası
- ODBC Driver'ın yüklü olduğundan emin olun
- `.env` dosyasındaki bağlantı bilgilerini kontrol edin
- Windows Authentication kullanıyorsanız `SQL_USERNAME` ve `SQL_PASSWORD` boş bırakın

### Statik Dosyalar Yüklenmiyor
- `download_static_assets.py` scriptini çalıştırın
- `static/vendor/` klasörünün mevcut olduğundan emin olun
- Tarayıcı konsolunda hata mesajlarını kontrol edin

### Veritabanı Şeması Oluşturulmuyor
- SQL Server'da veritabanının oluşturulduğundan emin olun
- Kullanıcının veritabanı oluşturma yetkisi olduğundan emin olun
- `.env` dosyasındaki bağlantı bilgilerini kontrol edin

## Lisans

Bu proje özel bir projedir.

## İletişim

Sorularınız için lütfen proje yöneticisi ile iletişime geçin.

