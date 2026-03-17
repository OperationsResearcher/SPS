# 🤖 AI Asistan İçin: Stratejik Planlama Sistemi Deployment Kılavuzu

**NOT: Bu dosyayı AI asistanına (ChatGPT, Claude, vb.) vererek deployment yapabilirsiniz.**

---

## 📋 Görev Tanımı

Merhaba AI Asistan! Senden bir Flask web uygulamasını test sunucusunda deploy etmeni istiyorum. Aşağıdaki adımları sırasıyla takip et ve her adımda bana sonucu bildir.

**Proje:** Stratejik Planlama Sistemi v2.2.0  
**Framework:** Flask 2.3.3 + SQLAlchemy + Waitress  
**Python:** 3.8+  
**Veritabanı:** SQL Server (veya SQLite fallback)

---

## 🎯 Genel Bilgiler

### Proje Yapısı
```
SP_Code/
├── app.py                          # Ana uygulama dosyası
├── __init__.py                     # Flask app factory
├── config.py                       # Konfigürasyon
├── requirements.txt                # Python bağımlılıkları
├── production_server.py            # Production server
├── pre_deployment_check.py         # Hazırlık kontrolü
├── init_db.py                      # Veritabanı başlatma
├── .env.template                   # Environment template
├── models/                         # Veritabanı modelleri
├── routes/                         # Flask route'lar
├── templates/                      # HTML şablonları
├── static/                         # CSS, JS, resimler
└── DEPLOYMENT_AI_PROMPT.md        # Bu dosya
```

### Gerekli Komutlar (OS'a göre)
- **Windows:** `py` veya `python`
- **Linux:** `python3`
- **Pip:** `pip` veya `pip3`

---

## 📝 ADIM ADIM DEPLOYMENT

### ✅ ADIM 1: Sistem Kontrolü

**Yapılacaklar:**
1. Python versiyonunu kontrol et (3.8+ gerekli)
2. Pip kurulu mu kontrol et
3. Mevcut dizini göster

**Komutlar:**
```bash
# Python versiyon
python --version
# veya
py --version

# Pip versiyon
pip --version

# Mevcut dizin
pwd
# veya (Windows)
cd
```

**Beklenen sonuç:** Python 3.8 veya üzeri

---

### ✅ ADIM 2: Virtual Environment Oluşturma

**Yapılacaklar:**
1. Virtual environment oluştur
2. Aktifleştir
3. Pip'i güncelle

**Komutlar:**

**Windows:**
```powershell
py -m venv venv
.\venv\Scripts\activate
python -m pip install --upgrade pip
```

**Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
```

**Beklenen sonuç:** Terminal prompt'unda `(venv)` görünmeli

---

### ✅ ADIM 3: Bağımlılıkları Yükleme

**Yapılacaklar:**
1. requirements.txt'den paketleri yükle

**Komut:**
```bash
pip install -r requirements.txt
```

**requirements.txt içeriği:**
```
Flask==2.3.3
Flask-SQLAlchemy==3.0.5
Flask-Login==0.6.3
Flask-Migrate==4.0.5
Flask-WTF==1.2.1
Flask-Limiter>=3.5.0
Flask-Caching>=2.1.0
Werkzeug==2.3.7
openpyxl==3.1.2
google-generativeai>=0.3.0
waitress==3.0.0
python-dotenv==1.0.0
pyodbc>=5.0.0
pytest==7.4.3
pytest-cov==4.1.0
pytest-flask==1.3.0
reportlab>=4.0.0
Flask-Talisman>=1.1.0
python-magic>=0.4.27
flask-restx>=1.3.0
requests>=2.31.0
Faker==24.0.0
```

**Beklenen sonuç:** Tüm paketler başarıyla yüklenmeli (2-3 dakika sürer)

---

### ✅ ADIM 4: Environment Variables (.env) Oluşturma

**Yapılacaklar:**
1. .env dosyası oluştur
2. Gerekli değişkenleri ayarla

**Komut:**
```bash
# .env.template'den kopyala (varsa)
cp .env.template .env
# veya Windows
copy .env.template .env

# Düzenle
nano .env
# veya Windows
notepad .env
```

**Eğer .env.template yoksa, yeni .env dosyası oluştur ve şu içeriği yaz:**

```env
# ==========================================
# FLASK ENVIRONMENT
# ==========================================
FLASK_ENV=production
FLASK_APP=app.py
FLASK_DEBUG=False

# ==========================================
# SECURITY - KRİTİK!
# ==========================================
# ÖNEMLI: Güçlü bir secret key kullan!
# Üretmek için: python -c "import secrets; print(secrets.token_hex(32))"
SECRET_KEY=DEPLOYMENT-TEST-SECRET-KEY-CHANGE-THIS-TO-64-CHARS-MIN

# ==========================================
# DATABASE - SQLITE (Test için basit)
# ==========================================
# SQLite kullanmak için SQL_SERVER'ı boş bırak
SQL_SERVER=
SQL_DATABASE=
SQL_USERNAME=
SQL_PASSWORD=

# ==========================================
# SERVER SETTINGS
# ==========================================
SERVER_HOST=0.0.0.0
SERVER_PORT=8080
SERVER_THREADS=4

# ==========================================
# SESSION SETTINGS
# ==========================================
SESSION_COOKIE_SECURE=False
SESSION_COOKIE_HTTPONLY=True
SESSION_COOKIE_SAMESITE=Lax
```

**ÇOK ÖNEMLİ:** 
- `SECRET_KEY` değerini değiştir! Güçlü bir değer üret:
```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

**Beklenen sonuç:** .env dosyası oluşturuldu ve yapılandırıldı

---

### ✅ ADIM 5: Gerekli Dizinleri Oluşturma

**Yapılacaklar:**
1. Eksik dizinleri oluştur
2. İzinleri ayarla

**Komutlar:**

**Windows:**
```powershell
New-Item -ItemType Directory -Force -Path "static\uploads\logos"
New-Item -ItemType Directory -Force -Path "logs"
New-Item -ItemType Directory -Force -Path "backups"
```

**Linux:**
```bash
mkdir -p static/uploads/logos
mkdir -p logs
mkdir -p backups
chmod 755 static/uploads/logos
chmod 755 logs
chmod 755 backups
```

**Beklenen sonuç:** Dizinler oluşturuldu

---

### ✅ ADIM 6: Pre-Deployment Check

**Yapılacaklar:**
1. Otomatik kontrol scriptini çalıştır
2. Tüm gereksinimlerin karşılandığını doğrula

**Komut:**
```bash
python pre_deployment_check.py
```

**Beklenen sonuç:** 
```
🎉 TÜM KONTROLLER BAŞARILI! Deployment için hazırsınız.
```

**Eğer hata varsa:**
- Eksik paketleri yükle: `pip install <paket-adi>`
- Dizin izinlerini düzelt
- .env dosyasını kontrol et

---

### ✅ ADIM 7: Veritabanını Başlatma

**Yapılacaklar:**
1. Veritabanını oluştur (SQLite)
2. Tabloları oluştur
3. Varsayılan admin kullanıcısı oluştur

**Komutlar:**
```bash
# Veritabanını başlat
python init_db.py

# Eğer init_db.py yoksa veya hata verirse, aşağıdaki kodu çalıştır:
python -c "from __init__ import create_app, db; app = create_app(); app.app_context().push(); db.create_all(); print('Veritabanı oluşturuldu')"

# Test kullanıcıları oluştur (varsa)
python create_test_users.py

# Veya manuel olarak admin kullanıcısı oluştur:
```

**Admin kullanıcısı oluşturma kodu (eğer gerekirse):**
```python
# create_admin.py oluştur
from __init__ import create_app, db
from models.auth import User
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # Önce kontrol et
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(
            username='admin',
            password=generate_password_hash('admin123'),
            ad='Admin',
            soyad='User',
            email='admin@system.com',
            rol='admin',
            aktif=True
        )
        db.session.add(admin)
        db.session.commit()
        print('✓ Admin kullanıcısı oluşturuldu: admin / admin123')
    else:
        print('✓ Admin kullanıcısı zaten mevcut')
```

**Çalıştır:**
```bash
python create_admin.py
```

**Beklenen sonuç:** 
- `spsv2.db` dosyası oluşturuldu
- Admin kullanıcısı: `admin` / `admin123`

---

### ✅ ADIM 8: Development Test

**Yapılacaklar:**
1. Development modunda test et
2. Uygulamanın çalıştığını doğrula

**Komut:**
```bash
python app.py
```

**Beklenen sonuç:**
```
* Running on http://127.0.0.1:5001
```

**Tarayıcıda test et:**
- URL: `http://localhost:5001` veya `http://sunucu-ip:5001`
- Login: `admin` / `admin123`

**Test checklist:**
- [ ] Login sayfası açılıyor
- [ ] Admin ile giriş yapılabiliyor
- [ ] Dashboard görüntüleniyor

**Çalışıyorsa, Ctrl+C ile durdur ve devam et.**

---

### ✅ ADIM 9: Production Server Başlatma

**Yapılacaklar:**
1. Production server'ı (Waitress) başlat
2. Logları kontrol et

**Komut:**
```bash
python production_server.py
```

**Beklenen sonuç:**
```
======================================================================
STRATEJIK PLANLAMA SİSTEMİ - PRODUCTION SERVER
======================================================================
Server: Waitress WSGI
Host: 0.0.0.0
Port: 8080
Threads: 4
Environment: production
======================================================================

🚀 Server başlatılıyor: http://0.0.0.0:8080

Server'ı durdurmak için: Ctrl+C
======================================================================
```

**Tarayıcıda test et:**
- URL: `http://sunucu-ip:8080`
- Login: `admin` / `admin123`

---

### ✅ ADIM 10: Firewall Ayarları (Gerekirse)

**Yapılacaklar:**
1. Port 8080'i aç

**Windows:**
```powershell
New-NetFirewallRule -DisplayName "Strategic Planning" -Direction Inbound -LocalPort 8080 -Protocol TCP -Action Allow
```

**Linux:**
```bash
sudo ufw allow 8080/tcp
sudo ufw reload
```

---

### ✅ ADIM 11: Arka Planda Çalıştırma (Opsiyonel)

**Yapılacaklar:**
1. Server'ı arka planda çalışacak şekilde yapılandır

**Linux - systemd service:**

```bash
# Service dosyası oluştur
sudo nano /etc/systemd/system/strategic-planning.service
```

**Dosya içeriği:**
```ini
[Unit]
Description=Strategic Planning System
After=network.target

[Service]
Type=simple
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

**Servisi başlat:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable strategic-planning
sudo systemctl start strategic-planning
sudo systemctl status strategic-planning
```

**Windows - NSSM ile:**
```powershell
# NSSM indir: https://nssm.cc/download
# Kuruluma göre yolu ayarla
nssm install StrategicPlanning "C:\path\to\venv\Scripts\python.exe" "C:\path\to\production_server.py"
nssm start StrategicPlanning
```

**Linux - nohup ile (basit):**
```bash
nohup python production_server.py > logs/server.log 2>&1 &
```

---

## 🧪 Test ve Doğrulama

### Fonksiyonel Testler

**1. Login Testi:**
- URL: `http://sunucu-ip:8080`
- Kullanıcı: `admin`
- Şifre: `admin123`

**2. Dashboard Testi:**
- Ana sayfa açılıyor mu?
- Menüler görünüyor mu?

**3. CRUD Testleri:**
- Yeni kullanıcı ekle
- Yeni organizasyon oluştur
- Değişiklikleri kaydet

**4. Raporlama Testleri:**
- Bir rapor oluştur
- Excel export dene

### Log Kontrolleri

```bash
# Log dosyalarını kontrol et
tail -f logs/production.log

# Windows
Get-Content logs\production.log -Tail 50 -Wait
```

### Health Check

```bash
# Server çalışıyor mu?
curl http://localhost:8080/login

# veya
wget http://localhost:8080/login
```

---

## 🔒 Güvenlik Kontrolleri

### Yapılacaklar:
- [ ] SECRET_KEY güçlü bir değer (64+ karakter)
- [ ] .env dosyası izinleri kısıtlanmış (chmod 600)
- [ ] Admin şifresi değiştirildi
- [ ] FLASK_ENV=production
- [ ] DEBUG=False
- [ ] Gereksiz portlar kapalı

---

## 🆘 Sorun Giderme

### Problem 1: "pyodbc.Error: SQL Server bağlantı hatası"

**Çözüm:** SQLite kullan
```env
# .env dosyasında
SQL_SERVER=
```

### Problem 2: "ImportError: No module named 'flask'"

**Çözüm:**
```bash
# Virtual environment aktif mi?
source venv/bin/activate  # Linux
.\venv\Scripts\activate   # Windows

# Bağımlılıkları yeniden yükle
pip install -r requirements.txt
```

### Problem 3: "Permission denied"

**Çözüm:**
```bash
# Linux
sudo chown -R $USER:$USER .
chmod 755 static/uploads/logos
chmod 755 logs
```

### Problem 4: "Port 8080 already in use"

**Çözüm:**
```env
# .env dosyasında portu değiştir
SERVER_PORT=8081
```

### Problem 5: "Secret key not set"

**Çözüm:**
```bash
# Yeni secret key üret
python -c "import secrets; print(secrets.token_hex(32))"

# .env dosyasına ekle
SECRET_KEY=<üretilen-değer>
```

---

## 📊 Deployment Başarı Kriterleri

### ✅ Tamamlanması Gerekenler:

1. **Sistem Hazırlığı:**
   - [x] Python 3.8+ kurulu
   - [x] Virtual environment oluşturuldu
   - [x] Bağımlılıklar yüklendi

2. **Konfigürasyon:**
   - [x] .env dosyası oluşturuldu
   - [x] SECRET_KEY ayarlandı
   - [x] Dizinler oluşturuldu

3. **Veritabanı:**
   - [x] spsv2.db oluşturuldu
   - [x] Admin kullanıcısı var

4. **Server:**
   - [x] Development test başarılı
   - [x] Production server çalışıyor
   - [x] Port 8080 erişilebilir

5. **Fonksiyonel:**
   - [x] Login yapılabiliyor
   - [x] Dashboard yükleniyor
   - [x] CRUD işlemleri çalışıyor

---

## 📞 Son Bilgiler

**Deployment Tamamlandı! 🎉**

**Erişim Bilgileri:**
- URL: `http://sunucu-ip:8080`
- Admin: `admin`
- Şifre: `admin123` (Değiştirin!)

**Önemli Dosyalar:**
- Veritabanı: `spsv2.db`
- Konfigürasyon: `.env`
- Loglar: `logs/production.log`
- Backups: `backups/`

**Yararlı Komutlar:**
```bash
# Server durumu
ps aux | grep python

# Logları izle
tail -f logs/production.log

# Server'ı durdur
pkill -f production_server.py

# Server'ı başlat
python production_server.py
```

---

## 🤖 AI Asistan İçin Notlar

**Çalışma Akışı:**
1. Her adımı sırayla yap
2. Her adımın sonucunu kullanıcıya bildir
3. Hata varsa, sorun giderme bölümüne bak
4. Başarılı deployment sonrası özet rapor ver

**Önemli Noktalar:**
- OS'u tespit et (Windows/Linux) ve komutları ona göre ayarla
- Virtual environment'ın aktif olduğundan emin ol
- .env dosyasındaki SECRET_KEY'i mutlaka değiştir
- Her adımda doğrulama yap

**Başarı Mesajı:**
```
✅ DEPLOYMENT BAŞARILI!

Stratejik Planlama Sistemi başarıyla deploy edildi.

🌐 URL: http://sunucu-ip:8080
👤 Admin: admin
🔑 Şifre: admin123 (Değiştirin!)

📊 Durum:
- Server: Çalışıyor (Waitress)
- Database: SQLite (spsv2.db)
- Port: 8080
- Environment: production

⚠️ Yapılması Gerekenler:
1. Admin şifresini değiştirin
2. .env dosyasındaki SECRET_KEY'i güçlü bir değere güncelleyin
3. Firewall ayarlarını kontrol edin
4. SSL sertifikası ekleyin (production için)
5. Düzenli backup stratejisi oluşturun

📚 Dokümantasyon:
- Detaylı kılavuz: DEPLOYMENT_GUIDE.md
- Checklist: DEPLOYMENT_CHECKLIST.md
- Hızlı başlangıç: DEPLOYMENT_QUICKSTART.md

İyi çalışmalar! 🚀
```

---

**Bu dosya AI asistanınıza verilmek üzere hazırlanmıştır.**  
**Versiyon: 2.2.0**  
**Tarih: 12 Ocak 2026**
