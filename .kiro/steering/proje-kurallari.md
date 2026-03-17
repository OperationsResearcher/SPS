---
inclusion: always
---

# Proje Kuralları (.cursorrules)

Bu projede aşağıdaki kurallar **kesinlikle** uygulanır.

## 0. Görsel Doğrulama
Bir görevi bitirince sadece koda bakma; mümkünse tarayıcı/konsol doğrulaması yap. Eğer yapılamazsa "Tarayıcı erişimi sağlanamadı, kod analizi yapıldı" şeklinde dürüst rapor ver.

## 1. Bildirim Standartları — SweetAlert2 Zorunluluğu
- `alert()`, `confirm()`, `prompt()` **KESİNLİKLE YASAK**.
- Tüm kullanıcı bildirimleri ve onay pencereleri **SweetAlert2 (`Swal.fire`)** ile yapılır.
- Mesajlar Türkçe, profesyonel tonda; başarıda yeşil, hatada kırmızı tema.

## 2. Terminoloji — PG = Performans Göstergesi
- `PG` kısaltması **Performans Göstergesi** demektir, asla PostgreSQL için kullanılmaz.
- Değişken isimlerinde `performance_indicator`, `pi_score`, `indicator_data` gibi açık isimler kullan.

## 3. Teknik Altyapı
- **Port: 5001** — `localhost:5000` yasaktır.
- **Backend (Python/DB):** %100 İngilizce, snake_case.
- **Frontend (UI/Mesajlar):** %100 Türkçe.
- Boş `except: pass` yasak — her hata `app.logger.error` ile loglanır, kullanıcıya Türkçe SweetAlert2 ile bilgi verilir.

## 4. Veri Güvenliği — Soft Delete
- **Hard delete yasak** — fiziksel veri silme yapılmaz.
- Tüm modellerde `is_active` (veya `is_deleted`) alanı kullanılır; silme = `is_active=False`.
- Veri çekerken daima `.filter_by(is_active=True)` kontrolü eklenir.

## 5. Frontend — Katı Katman Ayrımı
- HTML içinde `<script>` veya `<style>` blokları **yasak** — tüm kod `static/js/` ve `static/css/` altında.
- Harici `.js` dosyalarında `{{ }}` (Jinja2) ifadesi kullanılamaz; veri aktarımı için `data-*` öznitelikleri kullanılır.

## 6. Mimari ve Modülerlik
- `app.py`'ye doğrudan rota eklemek yasak — her özellik kendi Blueprint modülü altında.
- `eski_proje/` klasörü sadece okuma amaçlıdır; yeni koda taşırken İngilizce isimlendirme + soft delete standartlarına uygun modernize et.
- Tüm rotalar `@login_required` ile korunur; modüle özel rotalar `@require_component` dekoratörü ile.

---

## 7. TASKLOG — Görev Takip Zorunluluğu

Her kod değişikliği içeren görev tamamlandığında `docs/TASKLOG.md` dosyası **zorunlu olarak** güncellenir. Bu adım görevin ayrılmaz parçasıdır.

### 7.1 Güncelleme Formatı

Dosyanın en üstüne (başlığın hemen altına) yeni kaydı ekle:

```markdown
## TASK-[NUMARA] | [TARİH] | [DURUM EMOJİ] [DURUM]

**Görev:** [Tek cümle görev tanımı]
**Modül:** [Hangi micro modülü — örn: surec, admin, sp]
**Durum:** ✅ Tamamlandı | ⚠️ Kısmi | ❌ Hata

### Değiştirilen Dosyalar
- `[dosya yolu]` → [ne değişti, tek satır]
- `[dosya yolu]` → [ne değişti, tek satır]

### Yapılan İşlem
[2-4 cümle özet — ne yapıldı, neden, nasıl]

### Notlar
[Varsa: eksik kalan, dikkat edilmesi gereken, sonraki adım önerisi]

---
```

### 7.2 TASK Numarası Belirleme
- `docs/TASKLOG.md` içindeki en son TASK numarasını bul
- Bir artır (ilk görevse TASK-001'den başla)

### 7.3 Durum Kodları
| Emoji | Anlam |
|-------|-------|
| ✅ | Görev tam tamamlandı, test edildi |
| ⚠️ | Kısmi tamamlandı, devam gerekiyor |
| ❌ | Hata oluştu, çözülemedi |
| 🔄 | Önceki task güncellendi/düzeltildi |

### 7.4 Kod Değişikliği Olmayan Görevler
Sadece analiz, soru-cevap veya araştırma görevlerinde TASKLOG güncellenmez.
Kod yazıldıysa, değiştirildiyse veya silindiyse → **zorunlu güncelleme**.

### 7.5 docs/TASKLOG.md Yoksa
Dosya yoksa önce oluştur:

```markdown
# TASKLOG — Kokpitim Görev Takip Defteri
> Her kod değişikliği bu dosyaya işlenir.
> Format: TASK-[numara] | Tarih | Durum

---

[Kayıtlar buraya, en yeni en üstte]
```
