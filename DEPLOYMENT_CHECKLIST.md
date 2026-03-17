# 📋 Deployment Checklist

Test sunucusunda deployment yapmadan önce bu checklist'i kontrol edin.

## ✅ Deployment Öncesi Hazırlık

### 1. Yerel Geliştirme Ortamı
- [ ] Tüm değişiklikler commit edildi
- [ ] Kodlar test edildi ve çalışıyor
- [ ] Unit testler geçiyor (`pytest`)
- [ ] Full system test çalıştırıldı (`python full_system_test.py`)
- [ ] Git tag oluşturuldu (örn: `v2.2.0`)

### 2. Dokümantasyon
- [ ] README.md güncel
- [ ] DEPLOYMENT_GUIDE.md incelendi
- [ ] Deployment notları hazırlandı
- [ ] Rollback prosedürü biliniyor

### 3. Backup
- [ ] Mevcut veritabanı yedeklendi
- [ ] Konfigürasyon dosyaları yedeklendi
- [ ] Önemli veriler backup'landı
- [ ] Backup'ların geri yükleme testi yapıldı

---

## 🚀 Test Sunucusunda Deployment

### 1. Sunucu Hazırlığı
- [ ] Sunucuya erişim sağlandı (SSH/RDP)
- [ ] Gerekli izinler var
- [ ] Python 3.8+ kurulu
- [ ] Disk alanı yeterli (min 1GB)

### 2. Dosya Transferi
```bash
# Test sunucusuna bağlan
ssh user@test-server

# Proje dizini oluştur
mkdir -p /var/www/strategic-planning
cd /var/www/strategic-planning

# Dosyaları transfer et (seçeneklerden biri)
# Seçenek 1: Git clone
git clone <repo-url> .

# Seçenek 2: SCP ile transfer
# scp -r /local/path/* user@test-server:/var/www/strategic-planning/

# Seçenek 3: Zip ile transfer
# scp project.zip user@test-server:/var/www/strategic-planning/
# unzip project.zip
```

- [ ] Dosyalar sunucuya kopyalandı
- [ ] Dosya izinleri doğru ayarlandı

### 3. Pre-Deployment Check
```bash
cd /var/www/strategic-planning
python pre_deployment_check.py
```

- [ ] Pre-deployment check başarılı
- [ ] Tüm gereksinimler karşılandı
- [ ] Uyarılar gözden geçirildi

### 4. Virtual Environment Kurulumu
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux
python3 -m venv venv
source venv/bin/activate

# Pip güncelle
pip install --upgrade pip

# Bağımlılıkları yükle
pip install -r requirements.txt
```

- [ ] Virtual environment oluşturuldu
- [ ] Bağımlılıklar yüklendi
- [ ] pyodbc kurulu (SQL Server kullanacaksanız)

### 5. Environment Variables
```bash
# .env dosyası oluştur
nano .env
```

Aşağıdaki değerleri test sunucusu için yapılandır:

```env
# Flask
FLASK_ENV=production
FLASK_APP=app.py
SECRET_KEY=[GÜVENLİ BİR DEĞER GIRIN - MIN 32 KARAKTER]

# Database (SQL Server)
SQL_SERVER=test-sql-server
SQL_DATABASE=stratejik_planlama_test
SQL_USERNAME=test_user
SQL_PASSWORD=[ŞİFRE]
SQL_DRIVER=ODBC Driver 17 for SQL Server

# veya SQLite için (SQL_SERVER boş bırakın)
# SQL_SERVER=

# Server
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
SERVER_THREADS=4
```

- [ ] .env dosyası oluşturuldu
- [ ] Tüm gerekli değişkenler ayarlandı
- [ ] SECRET_KEY güçlü bir değere set edildi
- [ ] Dosya izinleri kısıtlandı (`chmod 600 .env`)

### 6. Statik Dosyalar
```bash
python download_static_assets.py
```

- [ ] Statik dosyalar indirildi (Bootstrap, jQuery, vb.)
- [ ] static/vendor/ dizini oluşturuldu

### 7. Dizin İzinleri
```bash
# Windows için (PowerShell)
New-Item -ItemType Directory -Force -Path static\uploads\logos
New-Item -ItemType Directory -Force -Path logs
New-Item -ItemType Directory -Force -Path backups

# Linux için
mkdir -p static/uploads/logos logs backups
chmod 755 static/uploads/logos
chmod 755 logs
chmod 755 backups
```

- [ ] Gerekli dizinler oluşturuldu
- [ ] Yazma izinleri ayarlandı

### 8. Veritabanı Kurulumu

**Seçenek A: SQLite (Hızlı Test)**
```bash
python init_db.py
python create_sample_data_v2.py  # Opsiyonel: örnek veri
```

**Seçenek B: SQL Server**
```bash
# SQL Server'da veritabanı oluştur (sqlcmd veya SSMS ile)
sqlcmd -S test-sql-server -U sa -P password -Q "CREATE DATABASE stratejik_planlama_test"

# Migration çalıştır
python migration_init.py
python apply_performance_indexes.py

# Test kullanıcıları oluştur
python create_test_users.py
```

- [ ] Veritabanı oluşturuldu
- [ ] Tablolar oluşturuldu
- [ ] İndeksler eklendi
- [ ] Varsayılan admin kullanıcısı oluşturuldu

### 9. İlk Test (Development Mode)
```bash
# Önce development modunda test et
python app.py
# veya
python debug_app.py
```

Tarayıcıda aç: `http://test-server:5001`

- [ ] Uygulama başlatıldı
- [ ] Login sayfası açıldı
- [ ] Admin ile giriş yapıldı (`admin` / `admin123`)
- [ ] Dashboard yüklendi
- [ ] Temel fonksiyonlar çalışıyor

### 10. Production Server Başlatma
```bash
# Development server'ı durdur (Ctrl+C)

# Production server'ı başlat
python production_server.py

# Arka planda çalıştırmak için (Linux)
nohup python production_server.py > logs/server.log 2>&1 &

# Windows Service olarak çalıştırmak için
# NSSM veya Task Scheduler kullanın
```

- [ ] Production server başlatıldı
- [ ] Waitress çalışıyor
- [ ] Port dinleniyor (default: 8080)
- [ ] Loglar kaydediliyor

---

## 🧪 Deployment Sonrası Testler

### 1. Health Check
```bash
# Server'ın çalıştığını kontrol et
curl http://test-server:8080/login
# veya tarayıcıda: http://test-server:8080
```

- [ ] Server cevap veriyor
- [ ] HTTP 200 response alınıyor

### 2. Fonksiyonel Testler

#### Kullanıcı Yönetimi
- [ ] Login çalışıyor
- [ ] Logout çalışıyor
- [ ] Yeni kullanıcı oluşturulabiliyor
- [ ] Kullanıcı düzenlenebiliyor
- [ ] Şifre değiştirilebiliyor

#### Organizasyon & Süreç
- [ ] Organizasyon oluşturulabiliyor
- [ ] Süreç tanımlanabiliyor
- [ ] Süreç lideri atanabiliyor
- [ ] Süreç üyeleri eklenebiliyor

#### Performans Göstergeleri
- [ ] KPI tanımlanabiliyor
- [ ] Hedef değerler ayarlanabiliyor
- [ ] Periyot seçilebiliyor

#### Veri Girişi
- [ ] VGS (Veri Giriş Sihirbazı) açılıyor
- [ ] Veri girişi yapılabiliyor
- [ ] Veriler kaydediliyor

#### Raporlama
- [ ] Süreç karnesi görüntülenebiliyor
- [ ] Excel export çalışıyor
- [ ] Grafikler yükleniyor
- [ ] Filtreleme çalışıyor

### 3. Güvenlik Testleri
- [ ] CSRF koruması aktif
- [ ] Session timeout çalışıyor
- [ ] Yetkisiz erişim engellenıyor
- [ ] SQL injection koruması var
- [ ] XSS koruması aktif
- [ ] File upload güvenlik kontrolleri çalışıyor

### 4. Performans Testleri
```bash
# Basit load test
ab -n 100 -c 10 http://test-server:8080/login
```

- [ ] Sayfa yükleme < 3 saniye
- [ ] Concurrent kullanıcı testi yapıldı
- [ ] Memory leak testi yapıldı
- [ ] Database connection pool çalışıyor

### 5. Log Kontrolleri
```bash
# Logları kontrol et
tail -f logs/production.log
tail -f logs/app.log
```

- [ ] Loglar yazılıyor
- [ ] Hata logları kontrol edildi
- [ ] Warning'ler gözden geçirildi

---

## 📊 Monitoring & Bakım

### 1. Server Monitoring
```bash
# Server durumunu kontrol et
# Linux
ps aux | grep python
netstat -tlnp | grep 8080

# Windows
netstat -ano | findstr :8080
tasklist | findstr python
```

- [ ] Server process çalışıyor
- [ ] Port dinleniyor
- [ ] CPU kullanımı normal
- [ ] Memory kullanımı normal

### 2. Database Monitoring
```bash
# SQLite için
ls -lh spsv2.db

# SQL Server için
sqlcmd -S server -Q "SELECT name, size*8/1024 as size_mb FROM sys.master_files WHERE database_id = DB_ID('stratejik_planlama_test')"
```

- [ ] Veritabanı boyutu kontrol edildi
- [ ] Bağlantı sayısı normal
- [ ] Query performansı iyi

### 3. Backup Stratejisi
```bash
# Otomatik backup scripti oluştur (örnek)
# backup_daily.sh
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cp spsv2.db backups/spsv2_$DATE.db
find backups/ -name "spsv2_*.db" -mtime +7 -delete  # 7 günden eski backupları sil
```

- [ ] Backup scripti oluşturuldu
- [ ] Otomatik backup zamanlandı (cron/Task Scheduler)
- [ ] Backup testi yapıldı

---

## 🔴 Sorun Durumunda

### Acil Müdahale
1. Server'ı durdur:
   ```bash
   # Process ID bul
   ps aux | grep production_server.py
   # Durdur
   kill <PID>
   ```

2. Logları kontrol et:
   ```bash
   tail -100 logs/production.log
   ```

3. Gerekirse rollback yap:
   ```bash
   git checkout <previous-version-tag>
   pip install -r requirements.txt
   python production_server.py
   ```

### Yaygın Sorunlar
- [ ] `pre_deployment_check.py` tekrar çalıştırıldı
- [ ] Log dosyaları incelendi
- [ ] DEPLOYMENT_GUIDE.md sorun giderme bölümü kontrol edildi
- [ ] Rollback planı hazır

---

## ✅ Final Checklist

### Deployment Başarılı
- [ ] Server çalışıyor ve erişilebilir
- [ ] Tüm fonksiyonel testler geçti
- [ ] Güvenlik testleri OK
- [ ] Performans testleri OK
- [ ] Monitoring aktif
- [ ] Backup stratejisi uygulandı
- [ ] Dokümantasyon güncellendi
- [ ] Kullanıcılar bilgilendirildi

### İletişim
- [ ] Deployment başarı durumu bildirildi
- [ ] Test sunucu adresi paylaşıldı
- [ ] Admin kullanıcı bilgileri iletildi
- [ ] Sorun durumunda iletişim kanalları belirlendi

---

## 📞 Destek Bilgileri

**Test Sunucu URL**: `http://test-server:8080`

**Varsayılan Admin:**
- Kullanıcı Adı: `admin`
- Şifre: `admin123`
- ⚠️ İlk girişte şifreyi değiştirin!

**Önemli Dosyalar:**
- Deployment Kılavuzu: `DEPLOYMENT_GUIDE.md`
- Pre-check Script: `pre_deployment_check.py`
- Production Server: `production_server.py`
- Logs: `logs/production.log`

**Deployment Tarihi**: _______________
**Deployment Yapan**: _______________
**Deployment Versiyonu**: v2.2.0

---

**✅ Tüm adımlar tamamlandıktan sonra bu dosyayı arşivleyin.**

**Sonraki Deployment**: `DEPLOYMENT_GUIDE.md` dosyasını referans alın.
