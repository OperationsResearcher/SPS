# 🚀 STRATEJİK VERİ MOTORU - Backend Güncelleme Raporu

## ✅ YAPILAN DEĞİŞİKLİKLER

### 📍 Dosya: `main/routes.py`
### 🔧 Fonksiyon: `kurum_paneli()` (Satır 1829-2064)

---

## 📊 YENİ VERİ KATMANLARI

### **A. VİZYON VE GLOBAL SKOR**
```python
vizyon = kurum.vizyon  # Kurum vizyonu
global_score = 85      # Tüm PG'lerin ağırlıklı ortalama başarı puanı
```

**SQL Optimizasyonu:**
- `db.func.avg()` kullanılarak veritabanı seviyesinde hesaplama
- Sadece aktif süreçler (`silindi=False`, `durum='Aktif'`)
- Kurum bazlı filtreleme (Admin hariç)

---

### **B. BSC PERSPEKTİF DAĞILIMI**
```python
bsc_distribution = {
    'labels': ['Finansal', 'Müşteri', 'Süreç', 'Öğrenme'],
    'data': [3, 5, 8, 4],  # Her perspektifteki strateji sayısı
    'colors': ['#667eea', '#11998e', '#4facfe', '#f093fb']
}
```

**Özellikler:**
- 4 BSC perspektifi (FINANSAL, MUSTERI, SUREC, OGRENME)
- Eksik perspektifler otomatik 0 ile doldurulur
- Radar/Pie chart için hazır format

---

### **C. STRATEJİK İLERLEME**
```python
strategic_progress = [
    {
        'id': 1,
        'code': 'ST1',
        'ad': 'Büyüme Stratejisi',
        'perspective': 'FINANSAL',
        'skor': 75,  # Alt stratejilerin ortalama başarı puanı
        'alt_strateji_sayisi': 3
    },
    ...
]
```

**Hesaplama Mantığı:**
1. Her ana stratejinin alt stratejilerini al
2. Her alt stratejiye bağlı PG'lerin ortalama başarı puanını hesapla
3. Tüm alt stratejilerin ortalamasını ana stratejiye ata

---

### **D. SÜREÇ ISI HARİTASI**
```python
top_processes = [
    {'id': 5, 'ad': 'Satış', 'code': 'SR5', 'skor': 92, 'ilerleme': 85},
    {'id': 2, 'ad': 'Üretim', 'code': 'SR2', 'skor': 88, 'ilerleme': 90},
    ...
]  # En başarılı 5 süreç

risky_processes = [
    {'id': 8, 'ad': 'Lojistik', 'code': 'SR8', 'skor': 45, 'ilerleme': 30},
    ...
]  # En riskli 5 süreç
```

**SQL Optimizasyonu:**
- `db.func.avg()` ile süreç bazlı PG ortalaması
- `outerjoin()` ile PG'si olmayan süreçler de dahil
- Python tarafında sıralama (skor bazlı)

---

### **E. PROJE ETKİSİ**
```python
project_impact = {
    'total': 15,  # Toplam aktif proje
    'health_distribution': {
        'Mükemmel': 8,
        'İyi': 5,
        'Dikkat': 2,
        'Kritik': 0
    },
    'completion_rate': 60  # Tamamlanma yüzdesi
}
```

**Özellikler:**
- Sağlık durumu dağılımı (health_status veya health_score bazlı)
- Bitiş tarihi geçmiş projeler = tamamlanmış
- Arşivlenmiş projeler hariç

---

## 🔧 OPTİMİZASYON TEKNİKLERİ

### **1. SQL Aggregation Fonksiyonları**
```python
# ✅ İYİ: Veritabanında hesaplama
db.func.avg(SurecPerformansGostergesi.agirlikli_basari_puani)

# ❌ KÖTÜ: Python'da hesaplama
sum([pg.agirlikli_basari_puani for pg in pgs]) / len(pgs)
```

### **2. Eager Loading**
```python
# Mevcut yapıda zaten var:
ana_strateji.alt_stratejiler  # Backref ile otomatik yükleme
```

### **3. Null/None Kontrolü**
```python
global_score = int(global_score_result) if global_score_result else 0
avg_score = int(total_score / total_count) if total_count > 0 else 0
```

### **4. Kurum İzolasyonu**
```python
if not is_admin:
    query = query.filter(Model.kurum_id == kurum_id)
```

---

## 📤 TEMPLATE'E GÖNDERİLEN VERİLER

### **Yeni Veriler (Stratejik Kokpit):**
```python
vizyon                  # str: Kurum vizyonu
global_score            # int: Global başarı skoru (0-100)
bsc_distribution        # dict: BSC perspektif dağılımı
strategic_progress      # list: Ana stratejilerin ilerleme durumu
top_processes           # list: En başarılı 5 süreç
risky_processes         # list: En riskli 5 süreç
project_impact          # dict: Proje sağlık durumu özeti
```

### **Mevcut Veriler (Uyumluluk):**
```python
kurum                   # Kurum objesi
kurumlar                # Admin için tüm kurumlar
ana_stratejiler         # Ana strateji listesi
degerler                # Kurum değerleri
etik_kurallari          # Etik kuralları
kalite_politikalari     # Kalite politikaları
surecler                # Süreç listesi
uyeler                  # Kullanıcı listesi
swot_count              # SWOT analiz sayısı
pestle_count            # PESTLE analiz sayısı
tows_strategy_count     # TOWS strateji sayısı
analysis_progress       # Analiz tamamlanma yüzdesi
```

---

## 🎯 KULLANIM ÖRNEKLERİ (Frontend)

### **1. Global Skor Gösterimi**
```html
<div class="global-score">
    <h2>{{ global_score }}%</h2>
    <p>Kurumsal Başarı Skoru</p>
</div>
```

### **2. BSC Radar Chart (Chart.js)**
```javascript
new Chart(ctx, {
    type: 'radar',
    data: {
        labels: {{ bsc_distribution.labels | tojson }},
        datasets: [{
            data: {{ bsc_distribution.data | tojson }},
            backgroundColor: 'rgba(102, 126, 234, 0.2)'
        }]
    }
});
```

### **3. Stratejik İlerleme Progress Bars**
```html
{% for strateji in strategic_progress %}
<div class="progress-item">
    <span>{{ strateji.code }} - {{ strateji.ad }}</span>
    <div class="progress">
        <div class="progress-bar" style="width: {{ strateji.skor }}%">
            {{ strateji.skor }}%
        </div>
    </div>
</div>
{% endfor %}
```

### **4. Süreç Isı Haritası**
```html
<h3>🔥 En Başarılı Süreçler</h3>
{% for surec in top_processes %}
<div class="process-card success">
    <strong>{{ surec.code }}</strong> - {{ surec.ad }}
    <span class="badge">{{ surec.skor }}%</span>
</div>
{% endfor %}

<h3>⚠️ Dikkat Gereken Süreçler</h3>
{% for surec in risky_processes %}
<div class="process-card danger">
    <strong>{{ surec.code }}</strong> - {{ surec.ad }}
    <span class="badge">{{ surec.skor }}%</span>
</div>
{% endfor %}
```

### **5. Proje Sağlık Dağılımı (Pie Chart)**
```javascript
new Chart(ctx, {
    type: 'pie',
    data: {
        labels: ['Mükemmel', 'İyi', 'Dikkat', 'Kritik'],
        datasets: [{
            data: [
                {{ project_impact.health_distribution.Mükemmel }},
                {{ project_impact.health_distribution.İyi }},
                {{ project_impact.health_distribution.Dikkat }},
                {{ project_impact.health_distribution.Kritik }}
            ],
            backgroundColor: ['#28a745', '#17a2b8', '#ffc107', '#dc3545']
        }]
    }
});
```

---

## 🚀 SONRAKI ADIMLAR

### **1. Frontend Görselleştirme (Önerilen)**
- Chart.js/ApexCharts entegrasyonu
- Responsive widget kartları
- Drill-down navigasyon

### **2. Gerçek Zamanlı Güncelleme (Opsiyonel)**
- WebSocket veya AJAX polling
- Canlı skor güncellemeleri

### **3. Export/Rapor (Gelecek)**
- PDF rapor oluşturma
- Excel export
- E-posta özeti

---

## ✅ TEST KONTROL LİSTESİ

- [ ] `/kurum-paneli` sayfası açılıyor mu?
- [ ] `global_score` doğru hesaplanıyor mu?
- [ ] BSC perspektif dağılımı görünüyor mu?
- [ ] Stratejik ilerleme listesi dolu mu?
- [ ] En iyi/riskli süreçler sıralı mı?
- [ ] Proje sağlık dağılımı doğru mu?
- [ ] Admin ve normal kullanıcı için farklı veri geliyor mu?

---

## 📌 ÖNEMLİ NOTLAR

1. **Performans:** SQL aggregation kullanıldığı için hızlı
2. **Null Safety:** Tüm hesaplamalarda None kontrolü var
3. **Kurum İzolasyonu:** Admin dışında sadece kendi kurumu
4. **Geriye Uyumluluk:** Eski veriler korundu
5. **Hata Yönetimi:** Try-except blokları ile güvenli

---

**🎯 Sonuç:** Backend hazır! Artık frontend'de bu verileri görselleştirebiliriz. 🚀
