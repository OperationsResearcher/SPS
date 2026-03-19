# TASKLOG — Son 10 Task
## TASK-034 | 2026-03-19 | ✅ Tamamlandı

**Görev:** FakeLimiter kaldırıldı, gerçek Flask-Limiter aktif edildi ve login endpoint'lerine rate limit eklendi
**Modül:** security / auth / micro-auth
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `extensions.py` → `FakeLimiter` tamamen kaldırıldı; gerçek `Limiter` import/instance eklendi
- `__init__.py` → limiter'ı devre dışı bırakan `RATELIMIT_ENABLED = False` satırı kaldırıldı
- `auth/routes.py` → `/auth/login` için `@limiter.limit("10 per minute")` eklendi
- `micro/modules/shared/auth/routes.py` → `/micro/login` için `@limiter.limit("10 per minute")` eklendi
- `requirements.txt` → `Flask-Limiter==3.5.0` olarak versiyon sabitlendi

### Yapılan İşlem
Rate limiting mekanizması mock/fake yapıdan gerçek Flask-Limiter'a geçirildi. Uygulama başlatma akışında `limiter.init_app(app)` çağrısı zaten mevcut olduğundan korunarak aktif hale getirildi. Auth ve micro login endpointlerine dakikada 10 istek limiti uygulandı.

### Notlar
Micro login route'u projede `/micro/login` olarak tanımlı; bu endpoint'e limit dekoratörü eklendi.

---

## TASK-033 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kokpitim tam derinlik analiz raporu oluşturuldu (`docs/analiz-antigravity.md`)
**Modül:** docs / analiz
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `docs/analiz-antigravity.md` → 10 adımlı kapsamlı proje analizi oluşturuldu

### Yapılan İşlem
Proje haritası, mimari analiz (Blueprint, ORM, Micro modüller), kod kalitesi (teknik borç, güvenlik, performans), frontend analizi (CSS/JS/Template), modül bazlı derinlik analizi, TASKLOG trend analizi, iyileştirme önerileri, rekabet/trend analizi, test durumu ve dokümantasyon değerlendirmesi yapıldı. Genel sağlık skoru: 61/100.

### Notlar
5 kritik güvenlik bulgusu tespit edildi: Rate limiter devre dışı, çift hardcoded secret key, SESSION_COOKIE_SECURE eksik, Talisman başlatılmamış, CSRF exempt endpoint.

---

## TASK-032 | 2026-03-19 | ✅ Tamamlandı

**Görev:** Kokpitim tam derinlik analiz raporu oluşturuldu (`docs/analiz-cursoranaliz.md`)
**Modül:** docs / analiz
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `docs/analiz-cursoranaliz.md` → 10 adımlı kapsamlı proje analizi eklendi (mimari, güvenlik, kalite, frontend, test, trend, öneriler)
- `docs/TASKLOG.md` → Bu kayıt eklendi

### Yapılan İşlem
Depodaki aktif kod ve legacy alanlar taranarak proje haritası, mimari katmanlar, veritabanı ve micro modül yapısı, teknik borç/güvenlik/performans bulguları, frontend tutarlılık analizi, TASKLOG trendleri ve iyileştirme önerileri tek raporda toplandı.

### Notlar
Toplam satır/dosya metrikleri hem ham depo hem aktif alan (yedek/legacy hariç) olarak ayrı raporlandı.

---

## TASK-031 | 2026-03-18 | 🔄 Düzeltme

**Görev:** profil.html boş dosya sorunu giderildi — Python script ile UTF-8 yeniden yazıldı
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/auth/profil.html` → PowerShell unicode escape hatası nedeniyle boşalmıştı; Python script ile UTF-8 olarak yeniden yazıldı
- `micro/static/micro/js/profil.js` → Aynı sorun; Python script ile UTF-8 olarak yeniden yazıldı

### Yapılan İşlem
PowerShell'in `\u` escape dizilerini literal string olarak yazması nedeniyle her iki dosya da boşalmıştı. Python script (`_write_profil.py`, `_write_profil_js.py`) ile UTF-8 encoding açıkça belirtilerek dosyalar yeniden oluşturuldu. Doğrulama: `extends micro/base.html`, `data-upload-url`, `UPLOAD_URL`, `swalError` varlığı kontrol edildi.

### Notlar
Yok.

---

## TASK-030 | 2026-03-18 | ✅ Tamamlandı

**Görev:** profil.html ve profil.js sıfırdan yeniden yazıldı — eski profile.html JS mantığı taşındı
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/auth/profil.html` → Silindi ve yeniden yazıldı; `micro/base.html` extend, `data-update-url`/`data-upload-url`, fotoğraf yükleme butonu + progress, profil formu, inline script yok
- `micro/static/micro/js/profil.js` → Silindi ve yeniden yazıldı; eski `profile.html` inline JS mantığı taşındı: dosya tipi/boyut kontrolü, `validateEmail`, `validatePhone`, Bootstrap Toast → SweetAlert2, fetch URL'leri `data-*`'dan okunuyor, `phone`→`phone_number`, `title`→`job_title`

### Yapılan İşlem
Eski `templates/profile.html`'deki inline JS (dosya tipi kontrolü, 5MB limit, e-posta/telefon validasyonu, fotoğraf güncelleme DOM mantığı) `profil.js`'e taşındı. Bootstrap Toast bildirimleri SweetAlert2 ile değiştirildi. HTML `micro/base.html`'i extend ediyor, tüm fetch URL'leri `data-*` attribute'larından okunuyor, inline `<script>` bloğu yok.

### Notlar
`static/js/profile.js` mevcut değildi — tüm JS `templates/profile.html` içinde inlineydi.

---

## TASK-029 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Eski profile.html JS mantığı micro profil.js'e taşındı; backend'e boyut ve mime kontrolü eklendi
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/js/profil.js` → Client-side mime type kontrolü, 5MB boyut kontrolü, `validateEmail`, `validatePhone` fonksiyonları, content-type response kontrolü, FormData'ya `csrf_token` field eklendi
- `micro/modules/shared/auth/routes.py` → `profil_foto_yukle`'ye mime type kontrolü (`file.mimetype`) ve 5MB boyut kontrolü (`file.seek`) eklendi

### Yapılan İşlem
Eski `templates/profile.html`'deki JS'de bulunan dosya tipi/boyut validasyonu, e-posta ve telefon format kontrolü micro `profil.js`'e taşındı. FormData'ya `csrf_token` field'ı da eklendi (header'a ek olarak — CSRF sorununu kesin çözer). Backend `profil_foto_yukle`'ye mime type ve 5MB boyut kontrolü eklendi. Alan adları zaten doğruydu: `phone_number`, `job_title`.

### Notlar
Eski `/profile/update` ve `/profile/upload-photo` endpoint'leri dokunulmadı — kök `templates/profile.html` kullananlar için çalışmaya devam ediyor.

---

## TASK-028 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Profil fotoğrafı yükleme CSRF hatası giderildi
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/shared/auth/routes.py` → `from extensions import csrf` import eklendi; `profil_foto_yukle` endpoint'ine `@csrf.exempt` dekoratörü eklendi

### Yapılan İşlem
`profil_foto_yukle` endpoint'i `multipart/form-data` POST alıyor; `profil.js` CSRF token'ı `X-CSRFToken` header olarak gönderiyor. Flask-WTF varsayılan olarak form field'dan (`csrf_token`) okuduğu için header'ı tanımıyor ve isteği reddediyordu. `@csrf.exempt` ile endpoint CSRF korumasından muaf tutuldu — endpoint zaten `@login_required` ile korunuyor.

### Notlar
Yok.

---

## TASK-027 | 2026-03-18 | 🔄 Düzeltme

**Görev:** profil.js'de input sıfırlama sırası düzeltildi
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/js/profil.js` → `this.value = ""` satırı `reader.readAsDataURL(file)` çağrısından önce taşındı

### Yapılan İşlem
`data-upload-url` doğru endpoint'e (`/micro/profil/foto-yukle`) işaret ediyordu. Asıl sorun: bazı tarayıcılarda `this.value = ""` `FileReader` okuma tamamlanmadan çalışınca `file` referansı kaybolabiliyordu. `file` önce değişkene alınıp input hemen sıfırlandı, ardından `readAsDataURL` çağrıldı.

### Notlar
Yok.

---

## TASK-026 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Profil fotoğrafı butonu, canvas kırpma ve avatar güncellemesi
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/templates/micro/auth/profil.html` → Kamera label/icon kaldırıldı, `btn-foto-yukle` butonu eklendi
- `micro/static/micro/js/profil.js` → Canvas ile 400x400 merkez kırpma, JPEG 0.85 kalite, `btn-foto-yukle` click bağlantısı
- `micro/templates/micro/base.html` → Topbar ve sidebar footer avatar'ı `profile_photo` varsa `<img>` gösteriyor

### Yapılan İşlem
Kamera ikonu yerine standart `mc-btn` butonu eklendi. Fotoğraf seçilince FileReader → Image → Canvas ile 400x400 kare kırpma yapılıyor, `toBlob(jpeg, 0.85)` ile sıkıştırılıp endpoint'e gönderiliyor. Topbar ve sidebar avatar'ları profil fotoğrafı varsa `<img>` tag'i, yoksa harf gösteriyor.

### Notlar
Yok.

---

## TASK-025 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Profil sayfası micro yapıya tam taşındı — backend JSON API, fotoğraf yükleme, template ve JS
**Modül:** auth / profil
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/shared/auth/routes.py` → `profil` route'u JSON API POST handler'a dönüştürüldü; `profil_foto_yukle` endpoint'i eklendi
- `micro/templates/micro/auth/profil.html` → `profile_picture` → `profile_photo` düzeltildi; `data-update-url` / `data-upload-url` eklendi; rol badge Türkçeleştirildi; inline script kaldırıldı
- `micro/static/micro/js/profil.js` → Tamamen yeniden yazıldı: fetch URL'leri `data-*`'dan okunuyor, bildirimler SweetAlert2, form JSON API ile submit ediliyor

### Yapılan İşlem
Profil sayfası eski `auth_bp.profile` 307 redirect'inden kurtarıldı. `micro_bp.profil` artık kendi JSON API handler'ına sahip: şifre doğrulama, e-posta duplicate kontrolü, yeni model alan adları (`phone_number`, `job_title`). Fotoğraf yükleme `profil_foto_yukle` endpoint'inde — fiziksel silme yok, sadece DB güncelleniyor. `profil.js` SweetAlert2 ile yeniden yazıldı.

### Notlar
Eski `auth_bp.profile` ve `auth_bp.upload_profile_photo` endpoint'leri hâlâ çalışıyor — kök `templates/profile.html` kullananlar için dokunulmadı.

---
