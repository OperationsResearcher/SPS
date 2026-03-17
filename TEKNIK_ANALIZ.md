# TE KNIK ANALIZ VE GUVENLIK DENETIM RAPORU

**Tarih:** 2026-01-21
**Konu:** Yerel Geliştirme ve Deployment Ortamı Analizi
**Hazırlayan:** Senior DevOps & Python Solutions Architect

---

## 1. File System Hierarchy

Projenin genel dosya yapısı aşağıdadır. Önemli yapılandırma dosyaları ve dizinler vurgulanmıştır.

```text
.
├── .env                  # [MEVCUT] Çevresel değişkenler
├── app.py                # [MEVCUT] Flask uygulama giriş noktası (Port: 5001)
├── baslat.bat            # [YOK] (Yerine DEV_UPDATE.bat ve deploy.bat mevcut)
├── config.py             # [MEVCUT] Konfigürasyon sınıfı
├── deploy.bat            # [MEVCUT] GitHub deployment scripti
├── DEV_UPDATE.bat        # [MEVCUT] Geliştirme/Migration güncelleme scripti
├── extensions.py         # [MEVCUT] Eklenti tanımları (db, login, csrf vb.)
├── migrations/           # [MEVCUT] Veritabanı versiyon geçmişi
├── requirements.txt      # [MEVCUT] Bağımlılık listesi
├── run.py                # [MEVCUT] Alternatif giriş noktası
├── web.config            # [BOS] IIS yapılandırma dosyası (0 byte!)
└── models/               # [MEVCUT] Veritabanı modelleri
```

---

## 2. Dependency & Environment Check

### Kritik Kütüphane Versiyonları (`requirements.txt`)
Aşağıdaki versiyonlar tespit edilmiştir:

- **Flask**: `2.3.3`
- **Werkzeug**: `2.3.7`
- **Flask-SQLAlchemy**: `3.0.5`
- **Flask-Migrate**: `4.0.5`
- **Flask-WTF**: `1.2.1`
- **waitress**: `3.0.0`

### Çevresel Değişkenler (`.env`)
Dosyada tanımlı anahtarlar (Değerler gizlenmiştir):
- `SQL_SERVER`
- `SQL_DATABASE`
- `SQL_USERNAME`
- `SQL_PASSWORD`
- `SQL_DRIVER`
- `FLASK_ENV`
- `SECRET_KEY`

---

## 3. Entry Point & WSGI Configuration

### Başlatma Yöntemi
Uygulama iki ana noktadan başlatılabiliyor:
1.  **`run.py`**: `create_app()` fonksiyonunu çağırır.
2.  **`app.py`**: `create_app()` çağırır ve `atexit` ile scheduler temizliği yapar. `port=5001` üzerinde çalışacak şekilde yapılandırılmıştır.

```python
# app.py (Özet)
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5001)
```

### ProxyFix Durumu (KRITIK BULGU)
**TESPİT:** `__init__.py`, `app.py` veya `run.py` dosyalarının hiçbirinde `werkzeug.middleware.proxy_fix.ProxyFix` kullanımı **YOKTUR**.

**RİSK:** Eğer uygulama bir Reverse Proxy (Nginx, IIS, Cloudflare vb.) arkasında çalışıyorsa, Flask istemci IP adresini ve protokolünü (HTTP/HTTPS) yanlış algılayacaktır. Bu durum **CSRF hatalarına**, **Login döngülerine** ve **Secure Cookie** sorunlarına yol açar.

---

## 4. Configuration & Security (config.py)

Mevcut `Config` sınıfı yapısı:

```python
class Config:
    # --- VERITABANI AYARLARI (HIBRIT YAPI) ---
    basedir = os.path.abspath(os.path.dirname(__file__))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'spsv2.db')) # [REDACTED]
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Guvenlik
    SECRET_KEY = os.getenv('SECRET_KEY', '[REDACTED]')
    DEBUG = True
```

### Eksik Güvenlik Ayarları
Aşağıdaki kritik ayarlar `config.py` içinde **TANIMSİZDIR**:
- `SESSION_COOKIE_SECURE`: (HTTPS zorlaması için gereklidir)
- `SESSION_COOKIE_DOMAIN`: (Subdomain/Domain cookie çakışmaları için gereklidir)
- `WTF_CSRF_TRUSTED_ORIGINS`: (CSRF korumasının güvenilir originleri tanıması için gereklidir)

---

## 5. IIS & Deployment Artifacts

### web.config
**DURUM:** Dosya mevcut ancak **BOŞ (0 Byte)**.
**ETKİ:** Eğer bu uygulama IIS üzerinde barındırılacaksa, `HttpPlatformHandler` veya `FastCGI` yapılandırması olmadığı için **ÇALIŞMAYACAKTIR**.

### Başlatma Scripti
Standart bir `baslat.bat` yerine `DEV_UPDATE.bat` ve `deploy.bat` bulunmaktadır. Deployment veya servis başlatma için özelleştirilmiş bir script eksiktir.

---

## 6. Database & Extensions Structure

### Başlatma (`extensions.py`)
Veritabanı ve migrasyon araçları standart şekilde başlatılmıştır:
```python
db = SQLAlchemy()
migrate = Migrate()
# ...
# __init__.py içinde:
db.init_app(app)
migrate.init_app(app, db)
```

### Modeller (`models/`)
`models/__init__.py` üzerinden dışarı açılan sınıflar (Bazıları "Mock" olarak işaretlenmiştir):

**Kullanıcı & Yetki:**
- `User`, `Kurum`, `YetkiMatrisi`, `OzelYetki`, `KullaniciYetki`

**Strateji:**
- `AnaStrateji`, `AltStrateji`, `StrategyProcessMatrix`, `StrategyMapLink`

**Süreç:**
- `Surec`, `SurecPerformansGostergesi`, `SurecFaaliyet`, `BireyselPerformansGostergesi`

**Proje Yönetimi:**
- `Project`, `Task`, `TaskImpact`, `Sprint`, `ProjectTemplate`, `TimeEntry`

**Diğer:**
- `AnalysisItem`, `TowsMatrix`, `AuditLog`, `Activity`

---

## 7. Auth & Login Flow

### Login Route (`auth/routes.py`)
- Login işlemi `/auth/login` route'unda, standart POST kontrolü ile yapılmaktadır.
- **CSRF İstisnası:** `@csrf.exempt` login metodunda **kullanılmamıştır** (Doğrudur, koruma aktif).
- **Profil Güncelleme:** `/auth/profile/update` ve `/auth/profile/upload-photo` metodlarında `@csrf.exempt` **kullanılmıştır**.

### Login Şablonu (`templates/login.html`)
- Form, `Flask-WTF` form nesnesi (`form.hidden_tag()`) yerine **manuel HTML formu** kullanmaktadır.
- CSRF Token manuel olarak eklenmiştir:
  ```html
  <input type="hidden" name="csrf_token" value="{{ csrf_token() }}" />
  ```
- **Analiz:** `Flask-WTF` CSRF koruması global olarak aktif olduğu için (`extensions.py`), manuel `csrf_token` inputu POST isteklerinde token doğrulamasını sağlar. Ancak `WTF_CSRF_TRUSTED_ORIGINS` eksikliği, farklı bir domainden/proxy arkasından gelen isteklerde "CSRF token missing or incorrect" hatasına neden olabilir.
