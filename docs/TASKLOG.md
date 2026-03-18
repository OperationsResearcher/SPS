# TASKLOG — Kokpitim Görev Takip Defteri
> Her kod değişikliği bu dosyaya işlenir.
> Format: TASK-[numara] | Tarih | Durum
> En yeni kayıt en üstte.

---

## TASK-009 | 2026-03-18 | ✅ Tamamlandı

**Görev:** SQLAlchemy `Multiple classes found for path "User"` ve duplicate tablo hatası giderildi
**Modül:** models / app/models
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `models/user.py` → `class User` → `class LegacyUser`, `class Notification` → `class LegacyNotification`; tüm `relationship('User', ...)` → `relationship('LegacyUser', ...)`
- `models/__init__.py` → import satırı `LegacyUser`, `LegacyNotification` olarak güncellendi; `User = LegacyUser` ve `Notification = LegacyNotification` alias'ları eklendi
- `app/models/notification.py` → `__tablename__ = 'notifications'` → `'notifications_ext'` (core.py ile çakışma giderildi)

### Yapılan İşlem
`models/user.py` ile `app/models/core.py`'de aynı isimde `User` ve `Notification` class'ları bulunuyordu; SQLAlchemy registry çakışma hatası veriyordu. Kök `models/` altındaki class'lar `Legacy` prefix'i alarak yeniden adlandırıldı, geriye dönük uyumluluk için alias'lar eklendi. Ayrıca `app/models/notification.py` ile `app/models/core.py` aynı `notifications` tablo adını kullanıyordu; `notification.py` tablosu `notifications_ext` olarak yeniden adlandırıldı. Uygulama `http://127.0.0.1:5001` üzerinde hatasız başlıyor.

### Notlar
`notifications_ext` tablosu yeni bir tablo — mevcut DB'de bu tablo yoksa migration gerekebilir.

---

## TASK-008 | 2026-03-18 | ✅ Tamamlandı

**Görev:** `app/models/__init__.py`'deki duplicate `db` instance kaldırıldı, kök `extensions.py::db`'ye yönlendirildi
**Modül:** micro / db / models
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `app/models/__init__.py` → `db = SQLAlchemy()` kaldırıldı, `from extensions import db` ile kök instance kullanılıyor
- `__init__.py` → `from app.models import db as app_db` ve `app_db.init_app(app)` satırları kaldırıldı

### Yapılan İşlem
Projede 3 ayrı `SQLAlchemy` instance mevcuttu: `extensions.py::db`, `app/extensions.py::db`, `app/models/__init__.py::db`. Micro modülleri `app.models.db`'yi kullanıyor, kök uygulama ise `extensions.py::db`'yi `init_app` yapıyordu. Bu iki farklı instance olduğu için `RuntimeError: not registered with this SQLAlchemy instance` hatası oluşuyordu. `app/models/__init__.py`'deki `db = SQLAlchemy()` kaldırılıp kök `extensions.py`'den import edildi; artık tüm modeller tek bir instance üzerinde çalışıyor.

### Notlar
`app/extensions.py::db` hâlâ kullanılmıyor — ileride bu dosya da temizlenebilir.

---

## TASK-007 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Micro modüllerinin kullandığı `app.models.db` instance'ı kök `__init__.py`'de `init_app` ile bağlandı
**Modül:** micro / db
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `__init__.py` → `from app.models import db as app_db` import edildi, `app_db.init_app(app)` eklendi

### Yapılan İşlem
Projede 3 farklı `SQLAlchemy` instance'ı mevcut: `extensions.py::db`, `app/extensions.py::db`, `app/models/__init__.py::db`. Micro modülleri `app.models.db`'yi kullanıyor ancak kök `__init__.py` yalnızca `extensions.py::db`'yi `init_app` yapıyordu. `app_db.init_app(app)` eklenerek `RuntimeError: not registered with this SQLAlchemy instance` hatası giderildi.

### Notlar
Uzun vadede tek bir `db` instance'ına geçilmesi teknik borcu azaltır.

---

## TASK-006 | 2026-03-18 | ✅ Tamamlandı

**Görev:** `__init__.py`'ye eksik `micro_bp` register satırı eklendi
**Modül:** micro / hgs
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `__init__.py` → `from micro import micro_bp` + `app.register_blueprint(micro_bp)` eklendi

### Yapılan İşlem
Kök `__init__.py`'de micro_bp hiç register edilmemişti; bu yüzden `/micro/*` altındaki tüm route'lar 404 veriyordu. Blueprint kaydı `v3_bp`'nin hemen altına eklendi. Doğrulama: `/micro/hgs` ve `/micro/hgs/login/<int:user_id>` route'ları artık url_map'te görünüyor.

### Notlar
Yok.

---

## TASK-005 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Login sayfası CSP bloğu nedeniyle bozulan inline style/script harici dosyalara taşındı
**Modül:** auth / login
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `templates/login.html` → Inline `<style>` ve `<script>` blokları kaldırıldı, harici dosyalara bağlandı
- `static/css/login.css` → Oluşturuldu (login sayfası tüm CSS'i)
- `static/js/login.js` → Oluşturuldu (quick login toggle JS)

### Yapılan İşlem
Flask-Talisman'ın `content_security_policy_nonce_in` ayarı inline style ve script bloklarını engelliyordu. Login sayfasındaki tüm CSS `static/css/login.css`'e, JS ise `static/js/login.js`'e taşındı. HTML'de sadece `<link>` ve `<script src>` referansları kaldı.

### Notlar
Tarayıcı erişimi sağlanamadı, kod analizi yapıldı.

---

## TASK-004 | 2026-03-18 | ✅ Tamamlandı

**Görev:** `config.py`'de eksik `get_config()` fonksiyonu eklendi
**Modül:** config
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `config.py` → `get_config()` fonksiyonu eklendi; `FLASK_ENV`'e göre `Config` veya `TestingConfig` döner

### Yapılan İşlem
`__init__.py` `get_config` adını import etmeye çalışıyordu ancak `config.py`'de yalnızca class tanımları vardı, fonksiyon yoktu. `TestingConfig`'in hemen altına `get_config()` factory fonksiyonu eklenerek `ImportError` giderildi.

### Notlar
Yok.

---

## TASK-003 | 2026-03-18 | ✅ Tamamlandı

**Görev:** TASKLOG.md UTF-8 BOM'suz yeniden yazıldı, eski_proje git'ten çıkarıldı
**Modül:** setup / git
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `docs/TASKLOG.md` → Python ile UTF-8 BOM'suz yeniden yazıldı
- `.gitignore` → `eski_proje/` satırı eklendi
- `eski_proje` → `git rm --cached` ile git index'ten kaldırıldı

### Yapılan İşlem
TASKLOG.md encoding sorunu giderildi; dosya artık BOM'suz saf UTF-8. eski_proje klasörü git'ten çıkarıldı ve .gitignore'a eklendi, git status'ta bir daha görünmeyecek.

### Notlar
Yok.

---

## TASK-002 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Tüm `px` font-size değerleri `var(--text-*)` CSS değişkenlerine geçirildi
**Modül:** css / tipografi
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/css/components.css` → Tüm sabit `px` font-size değerleri `var(--text-*)` token'larıyla değiştirildi; `html { font-size: 16px }` rem tabanı korundu

### Yapılan İşlem
`components.css` içindeki tüm sabit `px` font-size değerleri `:root` üzerinde tanımlı `--text-2xs` → `--text-3xl` token'larıyla değiştirildi. Böylece `html { font-size }` değeri değiştirildiğinde tüm tipografi orantılı ölçeklenir.

### Notlar
`sidebar.css` önceki oturumda güncellenmişti. `app.css` zaten `rem` kullanıyor, dokunulmadı.

---

## TASK-001 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Proje kurulum ve GitHub entegrasyonu tamamlandı
**Modül:** setup
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `docs/TASKLOG.md` → İlk kayıt oluşturuldu
- `.kiro/steering/proje-kurallari.md` → TASKLOG + otomatik push kuralları eklendi
- `github_sync.py` → Otomatik push desteği eklendi

### Yapılan İşlem
Proje GitHub entegrasyonu kuruldu. Steering kuralları, TASKLOG takip sistemi ve otomatik push mekanizması devreye alındı.

### Notlar
Sistem test ediliyor. Sonraki görevlerden itibaren her değişiklikte TASKLOG otomatik güncellenecek ve push edilecek.

---

## TASK-001 | 2026-03-17 | 🔄 Düzeltme

**Görev:** tenants.html'de duplicate `extra_js` bloğu hatası giderildi
**Modül:** admin
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/admin/tenants.html` → Duplicate `{% block extra_js %}` bloğu kaldırıldı

### Yapılan İşlem
Önceki oturumda `fsAppend` ile eklenen `extra_js` bloğu, dosyada zaten mevcut olan aynı blokla çakışıyordu. Jinja2 aynı isimde iki blok tanımına izin vermediği için `TemplateAssertionError` fırlatıyordu. Fazladan olan ikinci blok kaldırıldı.

### Notlar
Yok.

---
