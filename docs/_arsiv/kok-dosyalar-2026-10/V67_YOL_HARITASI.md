# 🚀 PROJECT OMEGA V67: MASTER YÜKSELTME PLANI (The Trinity Update)

Bu belge, sistemin statik yapıdan "Canlı, Akıllı ve Görsel" bir yapıya geçişini sağlayan teknik yol haritasıdır.

## 🎯 HEDEF
Aşağıdaki 3 ana modülün sisteme entegre edilmesi:
1.  **Gerçek Veri (Persistence):** Mock Data'nın kaldırılıp SQLite `Activity` tablosuna geçilmesi.
2.  **İş Zekası (Intelligence):** Faaliyetlerin proje sağlığını (Skor/Renk) otomatik etkilemesi.
3.  **Görsel Analiz (Visualization):** Verilerin Chart.js ile grafiklere dökülmesi.

---

## 🛠️ TEKNİK UYGULAMA ADIMLARI

### ADIM 1: OMURGA (Database Layer) 💾
*Şu anki uçucu "Mock Data" yerine kalıcı hafıza.*

* **İşlem:** `models.py` güncellenecek.
* **Yeni Model:** `Activity`
    * `id` (PK)
    * `source` (Redmine, Jira, CRM)
    * `subject` (String)
    * `priority` (High, Normal, Low)
    * `status` (Açık, Kapalı)
    * `date` (DateTime)
    * `project_id` (ForeignKey -> Project)
* **Aksiyon:** `app.py` başlangıcında Mock verileri bir kereye mahsus veritabanına aktaran bir "Seed Script" yazılacak.

### ADIM 2: BEYİN (Business Logic Layer) 🧠
*Projelerin durumu elle değil, verilere göre değişecek.*

* **Algoritma:** `Project` modeli içine `update_health()` metodu eklenecek.
* **Formül (Örnek):**
    * Başlangıç Puanı: 100
    * Her 'High' öncelikli açık iş: **-15 Puan**
    * Her 'Normal' öncelikli açık iş: **-5 Puan**
    * Son 7 gündür faaliyet yoksa: **Durum = 'Uyuyor'**
* **Sonuç:** Puan < 50 ise Proje Rengi **KIRMIZI** olur. Dashboard'da "X Projesi Riskte!" uyarısı çıkar.

### ADIM 3: YÜZ (Presentation Layer) 📊
*Sayıların grafiğe dökülmesi.*

* **Kütüphane:** `Chart.js` (CDN üzerinden `base.html`'e eklenecek).
* **Konum:** `dashboard.html` -> İstatistik kartlarının hemen altı.
* **Grafik Tipi:**
    * Sol: **Pasta Grafiği (Doughnut)** -> İşlerin Kaynak Dağılımı (Redmine vs Jira).
    * Sağ: **Bar Grafiği** -> Son 7 günün iş tamamlama performansı.

---

## 📅 UYGULAMA STRATEJİSİ

Risk almamak için bu plan **3 ayrı prompt** ile sırayla devreye alınacaktır:
1.  **Faz 5:** DB Migration (Mock Data -> SQLite).
2.  **Faz 6:** Algoritma Entegrasyonu (Puanlama Sistemi).
3.  **Faz 7:** Grafik Arayüzü.

---

## 📝 DETAYLI İMPLEMENTASYON NOTLARI

### Faz 5: DB Migration Detayları
- Mock data'dan gerçek veritabanına geçiş
- `Activity` modelinin oluşturulması
- Mevcut mock verilerin migration script'i ile veritabanına aktarılması
- `get_mock_data()` fonksiyonunun `Activity.query.all()` ile değiştirilmesi

### Faz 6: Business Logic Detayları
- Proje sağlık skoru hesaplama algoritması
- Real-time sağlık güncellemesi (Activity oluşturulduğunda/güncellendiğinde)
- Dashboard'da proje sağlık göstergeleri
- Risk uyarı sistemi

### Faz 7: Visualization Detayları
- Chart.js entegrasyonu
- Pasta grafiği: Kaynak dağılımı (Redmine, Jira, CRM, Dahili)
- Bar grafiği: Günlük tamamlama performansı
- Responsive grafik tasarımı
- Interaktif grafik özellikleri (hover, click eventleri)

---

## 🔄 MİGRASYON ADIMLARI

1. **Veritabanı Şema Güncellemesi:**
   ```python
   # models.py'ye eklenecek
   class Activity(db.Model):
       __tablename__ = 'activity'
       id = db.Column(db.Integer, primary_key=True)
       source = db.Column(db.String(50))
       subject = db.Column(db.String(200))
       priority = db.Column(db.String(20))
       status = db.Column(db.String(50))
       date = db.Column(db.DateTime)
       project_id = db.Column(db.Integer, db.ForeignKey('project.id'))
   ```

2. **Seed Script:**
   ```python
   # scripts/migrate_mock_to_db.py
   def migrate_mock_data():
       activities = get_mock_data()
       for activity_data in activities:
           activity = Activity(**activity_data)
           db.session.add(activity)
       db.session.commit()
   ```

3. **Route Güncellemeleri:**
   - `get_mock_data()` çağrıları yerine `Activity.query.all()` kullanılacak
   - Dashboard ve Redmine route'ları güncellenecek

---

## ⚠️ RİSK YÖNETİMİ

- Her faz ayrı bir commit olarak yapılmalı
- Her fazdan sonra test edilmeli
- Geri dönüş (rollback) planı hazır olmalı
- Mock data fonksiyonu geçici olarak korunmalı (fallback için)

---

## ✅ BAŞARI KRİTERLERİ

- [ ] Mock data tamamen kaldırıldı
- [ ] Tüm faaliyetler veritabanından çekiliyor
- [ ] Proje sağlık skoru otomatik hesaplanıyor
- [ ] Dashboard'da grafikler görüntüleniyor
- [ ] Performans kabul edilebilir seviyede
- [ ] Tüm testler başarılı

---

**Not:** Bu plan, sistemin mevcut yapısını bozmadan, adım adım uygulanacaktır.




