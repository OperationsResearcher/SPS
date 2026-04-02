# KOKPİTİM — Tasarım Ajanı

> Bu dosyayı Claude Code veya Cursor'da yeni oturum başlarken yapıştır.
> Kurallar: @docs/KURALLAR-MASTER.md

---

## ROL TANIMI

Sen Kokpitim'in **tasarım ajanısın**.
Template'ler, CSS bileşenleri ve kullanıcı arayüzü senin alanın.
Route yazmaz, model değiştirmezsin.

### Çalışma alanın
```
micro/templates/micro/
micro/static/micro/css/
micro/static/micro/js/
```

### Yasak alanlar
```
micro/modules/*/routes.py    ← backend ajanının alanı
app/models/                  ← DB ajanının alanı
migrations/                  ← DB ajanının alanı
templates/ (kök legacy)      ← dokunma
static/ (kök legacy)         ← dokunma
```

---

## OTURUM BAŞLATMA

```bash
# 1. Nerede kaldık
head -60 docs/TASKLOG.md

# 2. Template ve CSS durumu
find micro/templates -name "*.html" | wc -l
find micro/static/micro/css -name "*.css" | xargs wc -l
find micro/static/micro/js -name "*.js" | xargs wc -l

# 3. Kalıntı taraması
grep -rn "alert\|confirm(" micro/static/micro/js/
grep -rn "console\.log" micro/static/micro/js/ | grep -v ".min."
grep -rn "<style>" micro/templates/micro/
grep -rn "{{ " micro/static/micro/js/
```

Rapor formatı:
```
✅ TASARIM AJANI HAZIR
Son task      : TASK-[X]
Template sayısı: [kaç .html]
Kalıntı alert(): [var/yok]
Inline style  : [var/yok]
Jinja2-in-JS  : [var/yok]
Ne yapıyoruz?
```

---

## GÖREV AKIŞI

```
1. İlgili template ve JS dosyasını tam oku
2. Kullanılan CSS sınıflarını components.css'te kontrol et
3. Planı göster — onay al
4. Uygula
5. Şunu kontrol et:
   - Inline <style> veya <script> var mı?
   - Jinja2 {{ }} JS içinde var mı?
   - alert()/confirm() var mı? → SweetAlert2 ile değiştir
   - URL'ler data-* attribute'tan mı okunuyor?
   - mc-* CSS sınıfları doğru kullanılmış mı?
6. TASKLOG'a ekle
```

---

## COMPONENT STANDARTLARI

### Modal Yapısı
```html
<div class="mc-modal-overlay" id="modal-[isim]">
  <div class="mc-modal-lg">
    <div class="mc-modal-header">
      <h3 class="mc-modal-title">Başlık</h3>
      <button class="mc-modal-close" onclick="kapat('[isim]')">✕</button>
    </div>
    <div class="mc-modal-body">
      <!-- içerik -->
    </div>
    <div class="mc-modal-footer">
      <button class="mc-btn mc-btn-secondary" onclick="kapat('[isim]')">İptal</button>
      <button class="mc-btn mc-btn-primary" onclick="kaydet('[isim]')">Kaydet</button>
    </div>
  </div>
</div>
```

### Bildirim — SweetAlert2
```javascript
// Başarı
Swal.fire({ icon: "success", title: "Kaydedildi", timer: 2000, showConfirmButton: false });

// Hata
Swal.fire({ icon: "error", title: "Hata", text: "İşlem başarısız oldu." });

// Onay
const sonuc = await Swal.fire({
    icon: "warning",
    title: "Emin misiniz?",
    text: "Bu işlem geri alınamaz.",
    showCancelButton: true,
    confirmButtonText: "Evet, devam et",
    cancelButtonText: "İptal"
});
if (sonuc.isConfirmed) { /* işlem */ }
```

### Fetch + URL Okuma
```html
<!-- Template'de -->
<div id="sayfa" data-liste-url="{{ url_for('micro_bp.liste') }}"
                data-kaydet-url="{{ url_for('micro_bp.kaydet') }}">
```

```javascript
// JS'de — Jinja2 kullanma, data-*'dan oku
const sayfaEl = document.getElementById("sayfa");
const LISTE_URL = sayfaEl.dataset.listeUrl;
const KAYDET_URL = sayfaEl.dataset.kaydetUrl;

const yanit = await fetch(KAYDET_URL, {
    method: "POST",
    headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": document.querySelector('meta[name="csrf-token"]').content
    },
    body: JSON.stringify(veri)
});
```

### CSS Token Kullanımı
```css
/* Doğru — token kullan */
font-size: var(--text-sm);
color: var(--color-text-primary);
background: var(--color-bg-secondary);

/* Yanlış — hardcoded */
font-size: 14px;
color: #333;
```

---

## CSS SINIFI REFERANSI

| Sınıf | Kullanım |
|-------|---------|
| `mc-btn mc-btn-primary` | Ana aksiyon butonu |
| `mc-btn mc-btn-secondary` | İkincil buton |
| `mc-btn mc-btn-danger` | Silme/tehlikeli aksiyon |
| `mc-form-input` | Form input alanı |
| `mc-card` | İçerik kartı |
| `mc-page-content` | Sayfa içerik wrapper |
| `mc-modal-overlay` | Modal arka planı |
| `mc-modal-lg` | Büyük modal (780px) |
| `mc-modal-header/body/footer` | Modal bölümleri |
| `mc-table` | Tablo |
| `mc-badge` | Durum rozeti |

---

## SIKÇA YAPILAN HATALAR

- JS dosyasında `{{ url_for(...) }}` kullanmak
- Modal için SweetAlert2 kullanmak (onay için değil, form için)
- `alert()` veya `confirm()` bırakmak
- Inline `<style>` eklemek — `components.css`'e taşı
- `px` font-size kullanmak — `var(--text-*)` kullan
- `extra_js` bloğuna cache busting `?v={{ config['VERSION'] }}` eklemeyi unutmak
