# Görev Hatırlatma Özelliği - Kurulum ve Kullanım Kılavuzu

## 📋 Genel Bakış

Görev Hatırlatma özelliği, kullanıcıların belirledikleri tarih ve saatte otomatik bildirim almasını sağlar.

## ✅ Kurulum Tamamlandı

### Yapılan Değişiklikler:

#### 1. Veritabanı Değişiklikleri
- ✅ `task` tablosuna `reminder_date` kolonu eklendi (DATETIME, NULL)
- ✅ Migration başarıyla çalıştırıldı

#### 2. Backend Değişiklikleri
- ✅ Task modeli güncellendi ([models/project.py](models/project.py))
- ✅ API endpoint'leri güncellendi ([api/routes.py](api/routes.py))
  - POST /api/projeler/{project_id}/gorevler
  - PUT /api/projeler/{project_id}/gorevler/{task_id}
- ✅ Scheduler servisi oluşturuldu ([services/task_reminder_scheduler.py](services/task_reminder_scheduler.py))
- ✅ Bildirim servisi güncellendi ([services/notification_service.py](services/notification_service.py))

#### 3. Frontend Değişiklikleri
- ✅ Görev formuna hatırlatma input alanı eklendi ([templates/task_form.html](templates/task_form.html))
- ✅ HTML5 datetime-local input kullanıldı

#### 4. Sistem Entegrasyonu
- ✅ APScheduler yüklendi (v3.11.2)
- ✅ Scheduler app başlangıcında otomatik başlatılıyor
- ✅ Her 5 dakikada bir hatırlatmalar kontrol ediliyor

## 🎯 Kullanım

### Görev Oluştururken Hatırlatma Ekleme:

1. **Proje Detay Sayfasına Git:**
   - URL: `http://127.0.0.1:5001/projeler/[PROJE_ID]`

2. **"Görev Ekle" Butonuna Tıkla:**
   - Sayfadaki "Faaliyetler Listesi" kartında bulunan butona tıklayın

3. **Görev Bilgilerini Doldur:**
   - Görev Başlığı (zorunlu)
   - Atanan Kişi
   - Bitiş Tarihi
   - **Hatırlat (Tarih/Saat):** İstediğiniz hatırlatma zamanını seçin

4. **Kaydet:**
   - Görev kaydedildiğinde hatırlatma da kaydedilecektir

### Görev Düzenlerken Hatırlatma Değiştirme:

1. Mevcut göreve git
2. Düzenle butonuna tıkla
3. "Hatırlat (Tarih/Saat)" alanını güncelle
4. Kaydet

## ⚙️ Sistem Çalışma Mantığı

### 1. Hatırlatma Kaydı:
```
Kullanıcı → Form Doldurur → API (POST/PUT) → Veritabanı
```

### 2. Hatırlatma Kontrolü:
```
APScheduler (Her 5 dk) → check_task_reminders() → Veritabanı Sorgusu
```

### 3. Bildirim Gönderimi:
```
Hatırlatma Zamanı Geldi → create_task_reminder_notification() → 
→ Bildirim Oluştur → E-posta Gönder (opsiyonel)
```

### 4. Hatırlatma Temizleme:
```
Bildirim Gönderildi → reminder_date = NULL → Tekrar Gönderilmez
```

## 📊 Scheduler Detayları

**Çalışma Frekansı:** Her 5 dakika
**Job ID:** `task_reminder_check`
**Kontrol Penceresi:** Son 5 dakika + 1 dakika ileri
**Kontrol Kriterleri:**
- reminder_date dolu olmalı
- Görev durumu "Tamamlandı" olmamalı
- Görev arşivlenmemiş olmalı
- Hatırlatma zamanı gelmiş olmalı

## 🔧 Yapılandırma

### Scheduler Frekansını Değiştirme:

Dosya: `services/task_reminder_scheduler.py`

```python
scheduler.add_job(
    func=check_task_reminders,
    trigger=IntervalTrigger(minutes=5),  # Burayı değiştirin
    id='task_reminder_check',
    name='Görev Hatırlatma Kontrolü',
    replace_existing=True
)
```

### E-posta Bildirimi Aktifleştirme:

Dosya: `services/notification_service.py`

`send_task_reminder_email()` fonksiyonunu geliştirin:
```python
def send_task_reminder_email(user_id, task_id):
    user = User.query.get(user_id)
    task = Task.query.get(task_id)
    
    # E-posta gönderme kodunuz buraya
    send_email(
        to=user.email,
        subject=f'Görev Hatırlatması: {task.title}',
        body=f'Hatırlatma: "{task.title}" görevi hakkında...'
    )
```

## 🧪 Test

Test script'i çalıştırın:
```powershell
.\.venv\Scripts\python test_reminder_feature.py
```

**Test Edilen Özellikler:**
- ✅ Veritabanı kolon varlığı
- ✅ Model alanı varlığı
- ✅ Scheduler çalışma durumu
- ✅ API endpoint hazırlığı
- ✅ Notification service hazırlığı

## 📝 Notlar

### Önemli Bilgiler:

1. **Zaman Dilimi:** Sistem UTC kullanır, kullanıcı arayüzü local time gösterir
2. **Tek Seferlik:** Hatırlatma gönderildikten sonra `reminder_date` temizlenir
3. **Atama Gerekli:** Sadece atanmış görevler için hatırlatma gönderilir
4. **Tamamlanan Görevler:** Tamamlanan görevler için hatırlatma gönderilmez

### Bilinen Sınırlamalar:

- Hatırlatma zamanı geçmişe ayarlanamaz (frontend'de kontrol yok, manuel test edilmeli)
- Tekrarlayan hatırlatmalar desteklenmiyor
- E-posta bildirimi altyapı hazır ama aktif değil

## 🚀 Üretim Ortamına Alma

### 1. Migration'ı Çalıştır:
```bash
python migrate_add_reminder.py
```

### 2. Bağımlılıkları Yükle:
```bash
pip install -r requirements.txt
```

### 3. Sistemi Başlat:
```bash
# Development
python app.py

# Production (örnek: Waitress)
waitress-serve --host=0.0.0.0 --port=5001 app:app
```

### 4. Scheduler Kontrolü:
Uygulama loglarını kontrol edin:
```
[INFO] Görev hatırlatma scheduler başlatıldı
```

## 📞 Destek

Sorun yaşarsanız:

1. Test script'ini çalıştırın: `python test_reminder_feature.py`
2. Uygulama loglarını kontrol edin
3. Scheduler durumunu kontrol edin

## 🎉 Başarılı Kurulum!

Görev hatırlatma özelliği başarıyla kuruldu ve aktif. Artık kullanıcılar:
- ✅ Görev oluştururken hatırlatma tarihi belirleyebilir
- ✅ Belirlenen zamanda otomatik bildirim alabilir
- ✅ Hatırlatmaları düzenleyebilir veya kaldırabilir

**İyi çalışmalar! 🚀**
