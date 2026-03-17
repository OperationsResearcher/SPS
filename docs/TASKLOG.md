# TASKLOG — Kokpitim Görev Takip Defteri
> Her kod değişikliği bu dosyaya işlenir.
> Format: TASK-[numara] | Tarih | Durum

---

## TASK-003 | 2026-03-17 | ✅ Tamamlandı

**Görev:** Master dokümantasyon oluşturma ve tenant sayfası tasarım düzeltmesi
**Modül:** admin, docs
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `docs/martanaliz.md` → Sıfırdan oluşturuldu; 14 başlık, ~600+ satır master dokümantasyon
- `micro/templates/micro/admin/tenants.html` → Tablo 10→7 sütuna indirildi, modal form 3→2 kolon, detay modal mc-modal-overlay sistemine geçirildi
- `micro/static/micro/css/components.css` → `tm-grid-2` (2 kolonlu form grid) sınıfı eklendi
- `micro/static/micro/js/admin.js` → Detay modal açma/kapama `style.display` yerine `classList.add/remove("open")` ile güncellendi

### Yapılan İşlem
Tenant yönetimi sayfasının tablo genişliği sorunu giderildi: gereksiz sütunlar (Kısa Ad, Çalışan, Eklenme) kaldırılıp detay modalına taşındı. Modal form `tm-grid` (3 kolon) yerine `tm-grid-2` (2 kolon) kullanacak şekilde düzenlendi, sayfa genişliği kısıtlayan inline `max-width` style kaldırıldı. Ayrıca projeyi sıfırdan anlayabilmek için tüm modeller, API'lar, mimari ve kuralları kapsayan `martanaliz.md` oluşturuldu.

### Notlar
`RouteRegistry` modelinde `url_pattern` vs `url_rule` alan adı uyuşmazlığı tespit edildi (bkz. martanaliz.md §11.3). Düzeltilmesi önerilir.

---

## TASK-002 | 2026-03-17 | ✅ Tamamlandı

**Görev:** Micro admin kurum yönetimi sayfasına eksik alanlar ve arşiv filtresi eklenmesi
**Modül:** admin
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/modules/admin/routes.py` → `admin_tenants_add` endpoint'i tüm alanları kabul edecek şekilde genişletildi
- `micro/templates/micro/admin/tenants.html` → Düzenleme modalına paket seçimi, arşiv filtresi, data-* attribute'ları eklendi
- `micro/static/micro/js/admin.js` → SweetAlert2 tabanlı ekleme formu kaldırıldı, native modal sistemi (openTenantModal) eklendi
- `micro/static/micro/css/components.css` → `mc-modal-lg`, `tm-grid`, `tm-field`, `tm-full`, `tm-section-label` sınıfları eklendi

### Yapılan İşlem
Kök yapı `/admin/tenants` ile micro yapı `/micro/admin/tenants` karşılaştırması yapıldı. Eksik alanlar (sektör, iletişim, vergi, paket, lisans) eklendi. Kurum ekleme ve düzenleme tek bir native modal üzerinden yönetilir hale getirildi.

### Notlar
Arşivlenenleri göster/gizle butonu eklendi; varsayılan olarak arşivlenenler gizli.

---

## TASK-001 | 2026-03-17 | ✅ Tamamlandı

**Görev:** Micro UI/UX iyileştirme — mc-* bileşen sistemine geçiş ve bildirim/e-posta altyapısı
**Modül:** admin, ayarlar, bildirim, shared
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/css/components.css` → mc-* component kütüphanesi oluşturuldu
- `micro/templates/micro/` → Tüm micro şablonları Tailwind inline'dan mc-* sınıflarına geçirildi
- `micro/services/email_service.py` → Tenant SMTP e-posta servisi oluşturuldu
- `micro/services/notification_triggers.py` → Bildirim tetikleyicileri oluşturuldu
- `app/models/email_config.py` → TenantEmailConfig modeli oluşturuldu
- `micro/modules/shared/ayarlar/` → E-posta ayarları sayfası eklendi

### Yapılan İşlem
Tüm micro şablonları Tailwind CDN utility sınıflarından mc-* component sistemine taşındı. Uygulama içi bildirim sistemi ve tenant başına özel SMTP yapılandırması eklendi. E-posta ayarları sayfası oluşturuldu ve migration çalıştırıldı.

### Notlar
mc-* component sistemi tek CSS dosyasında (components.css) yönetiliyor; yeni bileşenler buraya eklenmeli.
