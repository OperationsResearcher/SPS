# 🚀 Test Deployment Kılavuzu

## 📋 İçindekiler
1. [Sistem Gereksinimleri](#sistem-gereksinimleri)
2. [Ön Koşul Kontrolleri](#ön-koşul-kontrolleri)
3. [Deployment Adımları](#deployment-adımları)
4. [Veritabanı Kurulumu](#veritabanı-kurulumu)
5. [Test Prosedürleri](#test-prosedürleri)
6. [Güvenlik Kontrolleri](#güvenlik-kontrolleri)
7. [Rollback Planı](#rollback-planı)
8. [Sorun Giderme](#sorun-giderme)

---

## 🖥️ Sistem Gereksinimleri

### Minimum Gereksinimler
- **İşletim Sistemi**: Windows Server 2016+ / Linux (Ubuntu 20.04+)
- **Python**: 3.8 veya üzeri
- **RAM**: Minimum 2GB, Önerilen 4GB+
- **Disk Alanı**: Minimum 1GB boş alan
- **Network**: HTTPS için 443 portu, HTTP için 80 veya özel port

### Veritabanı Seçenekleri
**Seçenek 1: SQL Server (Önerilen - Production)**
- SQL Server 2017 veya üzeri
- ODBC Driver 17 for SQL Server

**Seçenek 2: SQLite (Development/Test - Fallback)**
- Python ile birlikte gelir, ek kurulum gerektirmez

---

## ✅ Ön Koşul Kontrolleri

### 1. Otomatik Kontrol Scripti
Deployment öncesi tüm bileşenleri kontrol etmek için:

```bash
python pre_deployment_check.py
```

Bu script otomatik olarak kontrol eder:
- ✓ Python versiyonu
- ✓ Gerekli paketler
- ✓ Veritabanı bağlantısı
- ✓ Dizin yapısı
- ✓ Environment variables
- ✓ Port kullanılabilirliği
- ✓ Disk alanı

### 2. Manuel Kontroller

#### Python Kontrolü
```bash
python --version
# Beklenen: Python 3.8.x veya üzeri
```

#### Pip Kontrolü
```bash
pip --version
```

#### SQL Server Kontrolü (İsteğe Bağlı)
```bash
sqlcmd -S localhost -U sa -P YourPassword -Q "SELECT @@VERSION"
```

---

## 📦 Deployment Adımları

### Adım 1: Proje Dosyalarını Transferi
```bash
# Sunucuya bağlan ve dizin oluştur
mkdir -p /var/www/strategic-planning
cd /var/www/strategic-planning

# Dosyaları transfer et (örnek: rsync, git clone, scp)
git clone <repository-url> .
# veya
scp -r /local/path/* user@server:/var/www/strategic-planning/
```

### Adım 2: Virtual Environment Kurulumu
```bash
# Virtual environment oluştur
python -m venv venv

# Aktifleştir (Windows)
venv\Scripts\activate

# Aktifleştir (Linux)
source venv/bin/activate

# Pip'i güncelle
pip install --upgrade pip
```

### Adım 3: Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

**SQL Server kullanacaksanız:**
```bash
# Windows için ODBC Driver kurulumu
# https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server

# Linux için
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17
```

### Adım 4: Environment Variables Ayarları
```bash
# .env dosyası oluştur
nano .env
```

**.env Dosya İçeriği:**
```env
# ==========================================
# FLASK ENVIRONMENT
# ==========================================
FLASK_ENV=production
FLASK_APP=app.py

# ==========================================
# SECURITY
# ==========================================
# ÖNEMLI: Güçlü bir secret key kullanın!
SECRET_KEY=your-very-strong-secret-key-min-32-chars

# ==========================================
# DATABASE - SQL SERVER (Önerilen)
# ==========================================
SQL_SERVER=your-sql-server-hostname
SQL_DATABASE=stratejik_planlama
SQL_USERNAME=sa
SQL_PASSWORD=YourStrongPassword!123
SQL_DRIVER=ODBC Driver 17 for SQL Server

# ==========================================
# DATABASE - SQLITE (Fallback/Test)
# ==========================================
# SQL_SERVER bos bırakılırsa SQLite kullanılır
# Veritabanı dosyası: spsv2.db

# ==========================================
# SESSION SETTINGS
# ==========================================
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax

# ==========================================
# LOGGING
# ==========================================
LOG_LEVEL=INFO
LOG_FILE=/var/log/strategic-planning/app.log
```

**Güvenlik Notu:**
```bash
# .env dosyasının izinlerini kısıtla
chmod 600 .env
chown www-data:www-data .env  # Linux için
```

### Adım 5: Statik Dosyaları İndir (Offline Çalışma İçin)
```bash
python download_static_assets.py
```

### Adım 6: Dizin İzinlerini Ayarla
```bash
# Gerekli dizinleri oluştur
mkdir -p static/uploads/logos
mkdir -p logs
mkdir -p backups

# İzinleri ayarla (Linux)
chmod 755 static/uploads/logos
chmod 755 logs
chmod 755 backups

# Sahipliği ayarla (Linux)
chown -R www-data:www-data static/uploads
chown -R www-data:www-data logs
chown -R www-data:www-data backups
```

---

## 🗄️ Veritabanı Kurulumu

### Seçenek A: SQLite (Hızlı Test)
```bash
# Veritabanını başlat
python init_db.py

# Örnek veri oluştur (opsiyonel)
python create_sample_data_v2.py
```

### Seçenek B: SQL Server (Production)

#### 1. Veritabanı Oluştur
```sql
-- SQL Server Management Studio veya sqlcmd ile çalıştır
CREATE DATABASE stratejik_planlama;
GO

USE stratejik_planlama;
GO
```

#### 2. Migration Çalıştır
```bash
# Veritabanı şemasını oluştur
python migration_init.py

# İndeksleri ekle (performans için)
python apply_performance_indexes.py
```

#### 3. Varsayılan Admin Kullanıcısı Oluştur
```bash
python create_test_users.py
```

**Varsayılan Admin:**
- **Kullanıcı Adı**: `admin`
- **Şifre**: `admin123`
- ⚠️ **ÖNEMLI**: İlk giriş sonrası şifreyi değiştirin!

---

## 🧪 Test Prosedürleri

### 1. Ön Deployment Test (Development)
```bash
# Development modunda test çalıştır
python debug_app.py
```

Tarayıcıda açın: `http://localhost:5001`

### 2. Automated Tests
```bash
# Unit testleri çalıştır
pytest tests/ -v

# Coverage raporu
pytest --cov=. --cov-report=html

# Tam sistem testi
python full_system_test.py
```

### 3. Manuel Test Checklist

#### ✅ Temel Fonksiyonlar
- [ ] Login sayfası açılıyor
- [ ] Admin ile giriş yapılabiliyor
- [ ] Dashboard yükleniyor
- [ ] Kullanıcı oluşturulabiliyor
- [ ] Organizasyon oluşturulabiliyor
- [ ] Süreç eklenebiliyor
- [ ] Performans göstergesi tanımlanabiliyor
- [ ] Veri girişi yapılabiliyor
- [ ] Raporlar görüntülenebiliyor
- [ ] Excel export çalışıyor

#### ✅ Güvenlik Kontrolleri
- [ ] HTTPS çalışıyor (production)
- [ ] CSRF koruması aktif
- [ ] Session timeout çalışıyor
- [ ] SQL injection koruması var
- [ ] XSS koruması aktif
- [ ] Rate limiting çalışıyor

#### ✅ Performans Kontrolleri
- [ ] Sayfa yükleme < 3 saniye
- [ ] Veritabanı sorgu performansı OK
- [ ] Concurrent user testi geçti
- [ ] Memory leak yok
- [ ] Connection pool çalışıyor

### 4. Load Testing
```bash
# Apache Bench ile basit load test
ab -n 1000 -c 10 http://your-server/login

# veya
pip install locust
locust -f load_test.py
```

---

## 🔒 Güvenlik Kontrolleri

### Deployment Öncesi Güvenlik Checklist

#### 1. Environment Variables
- [ ] SECRET_KEY production değeriyle değiştirildi (min 32 karakter)
- [ ] Veritabanı şifreleri güçlü
- [ ] .env dosyası .gitignore'da
- [ ] .env dosya izinleri 600

#### 2. Flask Ayarları
- [ ] FLASK_ENV=production
- [ ] DEBUG=False
- [ ] SESSION_COOKIE_SECURE=True (HTTPS için)
- [ ] CSRF protection aktif

#### 3. Veritabanı
- [ ] Veritabanı kullanıcısı minimum yetkilere sahip
- [ ] Veritabanı uzaktan erişim kısıtlı
- [ ] Connection string güvenli saklanıyor
- [ ] Regular backup stratejisi var

#### 4. Sunucu
- [ ] Firewall kuralları aktif
- [ ] Sadece gerekli portlar açık
- [ ] SSL/TLS sertifikası kurulu
- [ ] Security updates güncel

#### 5. Uygulama
- [ ] Varsayılan admin şifresi değiştirildi
- [ ] File upload güvenlik kontrolleri aktif
- [ ] Rate limiting aktif
- [ ] Logging mekanizması çalışıyor

---

## ↩️ Rollback Planı

### Senaryo 1: Uygulama Hatası
```bash
# 1. Önceki versiyona dön
cd /var/www/strategic-planning
git checkout <previous-commit-hash>

# 2. Bağımlılıkları güncelle
pip install -r requirements.txt

# 3. Uygulamayı yeniden başlat
systemctl restart strategic-planning
```

### Senaryo 2: Veritabanı Sorunu
```bash
# 1. Veritabanını backup'tan geri yükle
sqlcmd -S localhost -U sa -P password -Q "RESTORE DATABASE stratejik_planlama FROM DISK='C:\backups\pre_deployment_backup.bak' WITH REPLACE"

# veya SQLite için
cp backups/spsv2_backup.db spsv2.db
```

### Senaryo 3: Konfigürasyon Hatası
```bash
# 1. Önceki .env dosyasını geri yükle
cp backups/.env.backup .env

# 2. Uygulamayı yeniden başlat
systemctl restart strategic-planning
```

### Pre-Deployment Backup Checklist
- [ ] Veritabanı backup alındı
- [ ] Konfigürasyon dosyaları yedeklendi
- [ ] Git commit/tag oluşturuldu
- [ ] Dosya sistemleri yedeklendi
- [ ] Backup'ların geri yükleme testi yapıldı

---

## 🚀 Production Deployment (Waitress)

### Windows için
```bash
# Waitress ile production server başlat
python production_server.py

# veya
waitress-serve --host=0.0.0.0 --port=8080 app:app
```

### Linux için (Systemd Service)
```bash
# Service dosyası oluştur
sudo nano /etc/systemd/system/strategic-planning.service
```

**Service Dosya İçeriği:**
```ini
[Unit]
Description=Strategic Planning System
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/strategic-planning
Environment="PATH=/var/www/strategic-planning/venv/bin"
ExecStart=/var/www/strategic-planning/venv/bin/python production_server.py

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Service'i Aktifleştir:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable strategic-planning
sudo systemctl start strategic-planning
sudo systemctl status strategic-planning
```

---

## 🔍 Sorun Giderme

### Yaygın Sorunlar ve Çözümleri

#### 1. "pyodbc.Error: SQL Server bağlantı hatası"
**Çözüm:**
- SQL Server'ın çalıştığından emin olun
- .env dosyasındaki bağlantı bilgilerini kontrol edin
- ODBC Driver 17'nin kurulu olduğunu kontrol edin
- Firewall kurallarını kontrol edin

#### 2. "ImportError: No module named 'flask'"
**Çözüm:**
```bash
# Virtual environment aktif mi kontrol edin
source venv/bin/activate  # veya venv\Scripts\activate

# Bağımlılıkları yeniden yükleyin
pip install -r requirements.txt
```

#### 3. "Permission Denied" Hataları
**Çözüm:**
```bash
# Linux için dizin izinlerini düzelt
sudo chown -R www-data:www-data /var/www/strategic-planning
chmod 755 static/uploads/logos
```

#### 4. "Secret Key Not Set" Uyarısı
**Çözüm:**
- .env dosyasında SECRET_KEY değişkenini ayarlayın
- Production ortamında environment variable olarak set edin

#### 5. Statik Dosyalar Yüklenmiyor
**Çözüm:**
```bash
# Statik dosyaları indirin
python download_static_assets.py

# Nginx kullanıyorsanız static dosya yolunu kontrol edin
```

### Log Dosyaları
```bash
# Uygulama logları
tail -f logs/app.log

# System logs (Linux)
sudo journalctl -u strategic-planning -f

# Windows Event Viewer
eventvwr.msc
```

---

## 📊 Deployment Checklist

### Deployment Öncesi
- [ ] Pre-deployment check script çalıştırıldı
- [ ] Tüm testler geçti
- [ ] Backup alındı
- [ ] .env dosyası production değerleriyle yapılandırıldı
- [ ] SECRET_KEY güçlü değere set edildi
- [ ] Veritabanı hazır
- [ ] Disk alanı yeterli
- [ ] Gerekli portlar açık

### Deployment Sırası
- [ ] Virtual environment oluşturuldu
- [ ] Bağımlılıklar yüklendi
- [ ] Veritabanı migrasyonları çalıştırıldı
- [ ] Statik dosyalar indirildi
- [ ] Dizin izinleri ayarlandı
- [ ] Production server yapılandırıldı

### Deployment Sonrası
- [ ] Uygulama başlatıldı
- [ ] Health check geçti
- [ ] Login testi yapıldı
- [ ] Temel fonksiyonlar test edildi
- [ ] Loglar kontrol edildi
- [ ] Performans metrikleri normal
- [ ] Monitoring aktif
- [ ] Documentation güncellendi

---

## 📞 Destek ve İletişim

### Deployment Sırasında Sorun Yaşarsanız:
1. `pre_deployment_check.py` scriptini tekrar çalıştırın
2. Log dosyalarını kontrol edin
3. Sorun Giderme bölümünü inceleyin
4. Gerekirse rollback yapın

### Önemli Dosyalar
- **Deployment Check**: `pre_deployment_check.py`
- **Production Server**: `production_server.py`
- **Konfigürasyon**: `config.py`, `.env`
- **Init Script**: `init_db.py`
- **Sample Data**: `create_sample_data_v2.py`

---

## 📝 Versiyon Bilgisi
- **Versiyon**: 2.2.0
- **Son Güncelleme**: 12 Ocak 2026
- **Python**: 3.8+
- **Framework**: Flask 2.3.3

---

**🎯 İyi Deployment'lar!**
