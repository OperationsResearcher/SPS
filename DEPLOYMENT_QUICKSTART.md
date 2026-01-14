# 🚀 Test Sunucu Deployment - Hızlı Başlangıç

## 📦 Oluşturulan Dosyalar

1. **DEPLOYMENT_GUIDE.md** - Kapsamlı deployment kılavuzu
2. **DEPLOYMENT_CHECKLIST.md** - Adım adım checklist
3. **pre_deployment_check.py** - Otomatik hazırlık kontrolü
4. **production_server.py** - Production server (Waitress)
5. **.env.template** - Environment variables şablonu

---

## ⚡ Hızlı Deployment Adımları

### 1️⃣ Test Sunucusunda Hazırlık

```bash
# Sunucuya bağlan
ssh user@test-server

# Proje dizini oluştur
mkdir -p /var/www/strategic-planning
cd /var/www/strategic-planning

# Dosyaları transfer et (git, scp veya başka yöntem)
git clone <repo-url> .
# veya
scp -r local-files/* user@test-server:/var/www/strategic-planning/
```

### 2️⃣ Virtual Environment Kurulumu

```bash
# Windows
py -m venv venv
venv\Scripts\activate

# Linux
python3 -m venv venv
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 3️⃣ Environment Variables

```bash
# .env.template'den kopyala
cp .env.template .env

# Düzenle
nano .env  # veya vi, notepad, vb.
```

**Kritik ayarlar:**
- `SECRET_KEY` - Güçlü bir değer girin (min 32 karakter)
- `FLASK_ENV=production`
- `SQL_SERVER` - SQL Server kullanacaksanız, yoksa boş bırakın (SQLite)
- `SQL_DATABASE`, `SQL_USERNAME`, `SQL_PASSWORD`

### 4️⃣ Pre-Deployment Check

```bash
# Windows
py pre_deployment_check.py

# Linux
python3 pre_deployment_check.py
```

✅ Tüm kontroller yeşil olmalı!

### 5️⃣ Veritabanı Kurulumu

**SQLite (Hızlı):**
```bash
py init_db.py
py create_sample_data_v2.py  # Opsiyonel: test verisi
```

**SQL Server:**
```bash
# SQL Server'da DB oluştur
sqlcmd -S server -U sa -P password -Q "CREATE DATABASE stratejik_planlama"

# Migration çalıştır
py migration_init.py
py apply_performance_indexes.py
py create_test_users.py
```

### 6️⃣ Test Deployment

```bash
# Development modunda test
py app.py

# Tarayıcıda: http://test-server:5001
# Login: admin / admin123
```

### 7️⃣ Production Deployment

```bash
# Production server başlat
py production_server.py

# Tarayıcıda: http://test-server:8080
```

---

## 🔍 Kontrol Noktaları

### ✅ Pre-Deployment
- [ ] `pre_deployment_check.py` başarılı
- [ ] `.env` dosyası yapılandırıldı
- [ ] Veritabanı hazır
- [ ] Backup alındı

### ✅ Post-Deployment
- [ ] Login sayfası açılıyor
- [ ] Admin girişi yapılabiliyor
- [ ] Dashboard yükleniyor
- [ ] CRUD işlemleri çalışıyor
- [ ] Excel export çalışıyor

---

## 🆘 Sorun Giderme

### Port 8080 kullanımda
```bash
# .env dosyasında değiştir
SERVER_PORT=8081
```

### Veritabanı bağlantı hatası
```bash
# SQL Server yerine SQLite kullan
# .env dosyasında SQL_SERVER'ı boş bırak veya comment out et
```

### Permission denied
```bash
# Linux için
chmod 755 static/uploads/logos
chmod 755 logs
```

### Import hatası
```bash
pip install -r requirements.txt --force-reinstall
```

---

## 📞 Önemli Komutlar

```bash
# Pre-check
py pre_deployment_check.py

# Development test
py app.py

# Production server
py production_server.py

# Veritabanı init
py init_db.py

# Full system test
py full_system_test.py

# Logları görüntüle
tail -f logs/production.log  # Linux
Get-Content logs/production.log -Wait  # Windows PowerShell
```

---

## 📚 Detaylı Dokümantasyon

- **DEPLOYMENT_GUIDE.md** - Tüm deployment detayları
- **DEPLOYMENT_CHECKLIST.md** - Adım adım checklist
- **README.md** - Proje dokümantasyonu
- **.env.template** - Environment variables açıklamaları

---

## 🎯 Varsayılan Kullanıcılar

**Admin:**
- Kullanıcı: `admin`
- Şifre: `admin123`
- ⚠️ İlk girişte şifreyi değiştirin!

---

## 🔐 Güvenlik Notları

1. `.env` dosyasını git'e commit etmeyin
2. `SECRET_KEY` güçlü olmalı (min 32 karakter)
3. Production'da `FLASK_ENV=production`
4. SQL Server şifreleri güçlü olmalı
5. Admin şifresini hemen değiştirin
6. `.env` dosya izinlerini kısıtlayın (`chmod 600 .env`)

---

## 📊 Sistem Gereksinimleri

**Minimum:**
- Python 3.8+
- 2GB RAM
- 1GB disk alanı
- Windows Server 2016+ / Ubuntu 20.04+

**Önerilen:**
- Python 3.10+
- 4GB+ RAM
- SQL Server 2017+
- HTTPS için SSL sertifikası

---

## ✅ Test Sunucu Hazır!

Pre-deployment check başarılıysa, test sunucusuna deployment için hazırsınız!

**Sorular için:** DEPLOYMENT_GUIDE.md dosyasının "Sorun Giderme" bölümüne bakın.

---

**Versiyon:** 2.2.0  
**Son Güncelleme:** 12 Ocak 2026  
**Framework:** Flask 2.3.3 + Waitress 3.0.0
