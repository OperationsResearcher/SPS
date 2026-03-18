# TASKLOG — Kokpitim Görev Takip Defteri
> Her kod değişikliği bu dosyaya işlenir.
> Format: TASK-[numara] | Tarih | Durum
> En yeni kayıt en üstte.

---

## TASK-002 | 2026-03-18 | ✅ Tamamlandı

**Görev:** Tüm `px` font-size değerleri `var(--text-*)` CSS değişkenlerine geçirildi
**Modül:** css / tipografi
**Durum:** ✅ Tamamlandı

### Değiştirilen Dosyalar
- `micro/static/micro/css/components.css` → Tüm sabit `px` font-size değerleri `var(--text-*)` token'larıyla değiştirildi; `html { font-size: 16px }` rem tabanı korundu

### Yapılan İşlem
`components.css` içindeki `.mc-modal-title`, `.mc-modal-close`, `.mc-page-title`, `.mc-page-subtitle`, `.mc-alert`, `.mc-avatar*`, `.mc-empty-*`, `.mc-stat-icon`, `.mc-form-label`, `.mc-form-input`, `.mc-form-section`, `.bildirim-*`, `.api-method`, `.topbar-notif-badge`, `.ayarlar-hub-*`, `.eposta-*`, `.tm-section-label` sınıflarındaki tüm sabit `px` font-size değerleri `:root` üzerinde tanımlı `--text-2xs` → `--text-3xl` token'larıyla değiştirildi. Böylece `html { font-size }` değeri değiştirildiğinde tüm tipografi orantılı ölçeklenir.

### Notlar
`sidebar.css` önceki oturumda güncellenmişti. `app.css` zaten `rem` kullanıyor, dokunulmadı.

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
