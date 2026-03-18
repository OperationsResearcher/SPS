# TASKLOG — Kokpitim Görev Takip Defteri
> Her kod değişikliği bu dosyaya işlenir.
> Format: TASK-[numara] | Tarih | Durum
> En yeni kayıt en üstte.

---

## TASK-019 | 2026-03-18 | ✅ Tamamlandı

**Görev:** micro_bp Blueprint'inden hatalı static_url_path parametresi kaldırıldı
**Modül:** micro / blueprint
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/__init__.py` → `static_url_path="/micro/static"` parametresi kaldırıldı

### Yapılan İşlem
`static_url_path="/micro/static"` ile `url_prefix="/micro"` birleşince `url_for` `/micro/micro/static/...` üretiyordu. Parametre kaldırıldığında Flask `url_prefix` + `/static` = `/micro/static` kullanıyor; `url_for('micro_bp.static', filename='micro/js/admin.js')` artık doğru `/micro/static/micro/js/admin.js` URL'ini üretiyor. Kök `/static/` route'u ile çakışma yok.

### Notlar
Yok.

---

## TASK-018 | 2026-03-18 | 🔄 Düzeltme

**Görev:** users.html extra_js bloğundaki admin.js path'i orijinal haline döndürüldü
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/admin/users.html` → `filename='js/admin.js'` → `filename='micro/js/admin.js'` olarak geri alındı

### Yapılan İşlem
TASK-017'de yapılan path değişikliği geri alındı. `filename='micro/js/admin.js'` orijinal değerine döndürüldü.

### Notlar
Yok.

---

## TASK-017 | 2026-03-18 | ✅ Tamamlandı

**Görev:** users.html extra_js bloğundaki admin.js path'i düzeltildi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/admin/users.html` → `filename='micro/js/admin.js'` → `filename='js/admin.js'` olarak düzeltildi

### Yapılan İşlem
Blueprint static dosya yolu `micro/js/admin.js` yerine `js/admin.js` olarak düzeltildi. `micro_bp.static` zaten `micro/static/micro/` prefix'ini ekliyor, dolayısıyla `micro/js/` tekrarı 404'e yol açıyordu.

### Notlar
Yok.

---

## TASK-016 | 2026-03-18 | ✅ Tamamlandı

**Görev:** JS/CSS dosyalarına cache busting için VERSION query string eklendi
**Modül:** admin / config / base
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `config.py` → `Config` sınıfına `VERSION = "1.0.1"` eklendi
- `micro/templates/micro/base.html` → 3 CSS + 1 JS include satırına `?v={{ config['VERSION'] }}` eklendi
- `micro/templates/micro/admin/users.html` → `extra_js` bloğundaki `admin.js` satırına `?v={{ config['VERSION'] }}` eklendi

### Yapılan İşlem
Tarayıcı cache'inin eski JS/CSS dosyalarını sunmasını önlemek için `config.py`'ye `VERSION` sabiti eklendi. `base.html`'deki tüm yerel CSS/JS include'ları ve `users.html`'deki `admin.js` include'u bu versiyonu query string olarak kullanacak şekilde güncellendi. Bundan sonra her JS/CSS değişikliğinde `config.py`'deki `VERSION` değeri artırılmalıdır.

### Notlar
`tenants.html` ve diğer admin sayfalarının `extra_js` bloklarında da aynı pattern uygulanmalı.

---

## TASK-015 | 2026-03-18 | ✅ Tamamlandı

**Görev:** admin.js ROLE_LABELS map'indeki ASCII Türkçe karakter hataları düzeltildi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/js/admin.js` → `ROLE_LABELS` map'inde 4 değer ve `buildRoleOptions` fallback string'i Türkçe karakterlerle düzeltildi

### Yapılan İşlem
`ROLE_LABELS` map'indeki `"Kullanici"`, `"Kurum Yoneticisi"`, `"Kurum Ust Yonetimi"`, `"Kurum Kullanicisi"` değerleri sırasıyla `"Kullanıcı"`, `"Kurum Yöneticisi"`, `"Kurum Üst Yönetimi"`, `"Kurum Kullanıcısı"` olarak güncellendi. `buildRoleOptions` fallback'i `"— Rol Sec —"` → `"— Rol Seç —"` yapıldı.

### Notlar
Yok.

---

## TASK-014 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Rol dropdown'ı Türkçe etiketlerle gösterilecek şekilde güncellendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/js/admin.js` → `ROLE_LABELS` map eklendi, `buildRoleOptions` fonksiyonu çeviri map'ini kullanacak şekilde güncellendi

### Yapılan İşlem
Backend'den gelen İngilizce rol isimleri (Admin, User, tenant_admin, executive_manager, standard_user) frontend'de Türkçe karşılıklarıyla gösterilmek üzere `ROLE_LABELS` map'i eklendi. Bilinmeyen rol isimleri olduğu gibi gösterilmeye devam eder.

### Notlar
Yok.

---

## TASK-013 | 2026-03-18 | ✅ Tamamlandı

**Görev:** users.html kullanıcı ekle/düzenle Swal modalları native HTML modal'a geçirildi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/admin/users.html` → `modal-user-add` ve `modal-user-edit` native modal'ları eklendi (mc-modal-overlay/mc-modal-lg yapısı)
- `micro/static/micro/js/admin.js` → btn-user-add ve btn-user-edit Swal.fire blokları kaldırıldı, native modal open/close/save fonksiyonları eklendi

### Yapılan İşlem
tenants.html'deki mc-modal-overlay/mc-modal-lg yapısı referans alınarak iki native modal oluşturuldu. admin.js'de Swal.fire bağımlılığı kaldırıldı; rol ve kurum select'leri admin-meta data-* attribute'larından dinamik dolduruluyor. API endpoint'leri (ADD_URL, EDIT_BASE) değişmedi.

### Notlar
toggle ve bulk-import işlemleri Swal.fire kullanmaya devam ediyor — bu kasıtlı, değiştirilmedi.

---

## TASK-012 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Excel şablonu sütunları güncellendi, Swal modal genişliği CSS ile sabitlendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → Excel şablonu başlıkları Ad/Soyad/E-posta/Sifre/Unvan/Telefon olarak güncellendi, 6 sütun genişliği ayarlandı
- `micro/static/micro/js/admin.js` → btn-user-add ve btn-user-edit Swal'larına `customClass: { popup: 'mc-swal-wide' }` eklendi
- `micro/static/micro/css/components.css` → `.mc-swal-wide` sınıfı eklendi (780px sabit genişlik)

### Yapılan İşlem
Excel şablonu kök yapıdaki kullanıcı alanlarıyla eşleştirildi. Swal modallarının gerçek genişliği tarayıcıda `width` parametresiyle tam uygulanmıyor olabildiğinden `customClass` + CSS ile 780px sabitlendi.

### Notlar
Yok.

---

## TASK-011 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Kullanıcı Swal modal genişlikleri 780px yapıldı, örnek Excel endpoint ve indirme butonu eklendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/js/admin.js` → btn-user-add width 560→780, btn-user-edit width 520→780, toplu içe aktar Swal'ına indirme butonu eklendi
- `micro/modules/admin/routes.py` → `/admin/users/sample-excel` GET endpoint'i eklendi (openpyxl ile xlsx üretir)

### Yapılan İşlem
Kullanıcı ekleme ve düzenleme Swal modalları tenant modal'ıyla aynı genişliğe (780px) getirildi. Toplu içe aktarma için örnek Excel şablonu üreten yeni bir endpoint eklendi. Swal'daki indirme butonu bu endpoint'e bağlandı; dosya kabul tipi `.csv,.xlsx` olarak güncellendi.

### Notlar
`openpyxl` paketi yüklü olmalı — `pip install openpyxl` ile kurulabilir.

---

## TASK-010 | 2026-03-18 | ✅ Tamamlandı

**Görev:** users.html kullanıcı yönetimi sayfası iyileştirmeleri ve admin.js e-posta alanı eklendi
**Modül:** admin / users
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/admin/users.html` → `data-email` eklendi, inline style kaldırıldı (`mc-page-content`), `mc-input`→`mc-form-input`, stat kartları eklendi, butonlar Admin kontrolüne alındı
- `micro/static/micro/js/admin.js` → `btn-user-edit` listener'ında `email` okunuyor, Swal formuna readonly e-posta alanı eklendi

### Yapılan İşlem
`users.html`'de 5 iyileştirme yapıldı: `data-email` attribute eklendi, `max-width` inline style `mc-page-content` sınıfıyla değiştirildi, arama kutusu sınıfı `mc-form-input` olarak düzeltildi, 3 stat kartı (toplam/aktif/pasif) eklendi, Düzenle ve Pasife Al butonları `Admin` rolü kontrolüne alındı. `admin.js`'de düzenleme Swal'ına readonly e-posta alanı eklendi.

### Notlar
E-posta alanı readonly — değiştirilemez, sadece bilgi amaçlı gösteriliyor.

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
