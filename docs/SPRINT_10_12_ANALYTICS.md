# Sprint 10-12: Analytics ve Raporlama

**Tarih:** 13 Mart 2026  
**Durum:** ✅ Tamamlandı  
**Süre:** 180 saat

---

## 📋 ÖZET

Sprint 10-12'de gelişmiş analytics ve raporlama özellikleri tamamlandı. Dashboard builder, trend analizi, karşılaştırmalı analiz, tahminleme ve özel rapor oluşturma eklendi.

---

## ✅ TAMAMLANAN GÖREVLER

### 1. Analytics Service ✅
**Süre:** 80 saat

**Oluşturulan Dosyalar:**
- `app/services/analytics_service.py` (500+ satır)

**Özellikler:**

**Performans Trend Analizi:**
```python
from app.services.analytics_service import AnalyticsService

# KPI trend analizi
trend = AnalyticsService.get_performance_trend(
    process_id=1,
    kpi_id=10,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    frequency='monthly'  # daily, weekly, monthly, quarterly
)

# Returns:
# {
#     'dates': ['2024-01', '2024-02', ...],
#     'actual_values': [85, 87, 90, ...],
#     'target_values': [90, 90, 90, ...],
#     'performance_rates': [94.4, 96.7, 100, ...]
# }
```

**Süreç Sağlık Skoru:**
```python
# Süreç genel sağlık durumu
health = AnalyticsService.get_process_health_score(process_id=1, year=2024)

# Returns:
# {
#     'overall_score': 85.5,
#     'kpi_scores': [
#         {'kpi_name': 'Müşteri Memnuniyeti', 'performance': 94.4, 'status': 'good'},
#         ...
#     ],
#     'status': 'good',  # excellent, good, fair, poor, critical
#     'recommendations': [
#         'Dikkat: Performans hedefin altında',
#         '2 KPI hedefin altında: KPI-1, KPI-2'
#     ]
# }
```

**Karşılaştırmalı Analiz:**
```python
# Süreçler arası karşılaştırma
comparison = AnalyticsService.get_comparative_analysis(
    process_ids=[1, 2, 3, 4],
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31)
)

# Returns:
# {
#     'processes': [
#         {'process_name': 'Satış', 'overall_score': 95.2, 'status': 'excellent'},
#         {'process_name': 'Pazarlama', 'overall_score': 87.5, 'status': 'good'},
#         ...
#     ],
#     'best_performer': {...},
#     'worst_performer': {...},
#     'average_score': 88.3
# }
```

**Anomali Tespiti:**
```python
# İstatistiksel anomali tespiti (z-score)
anomalies = AnalyticsService.get_anomaly_detection(
    kpi_id=10,
    lookback_days=90,
    threshold=2.0  # Standart sapma eşiği
)

# Returns:
# {
#     'anomalies': [
#         {'date': '2024-03-15', 'value': 120, 'z_score': 2.5, 'deviation': 33.3},
#         ...
#     ],
#     'statistics': {
#         'mean': 90.0,
#         'std': 12.0,
#         'min': 70.0,
#         'max': 120.0
#     }
# }
```

**Tahminleme (Forecasting):**
```python
# Basit tahminleme (moving average, linear trend)
forecast = AnalyticsService.get_forecast(
    kpi_id=10,
    periods=3,  # 3 ay tahmin
    method='moving_average'  # veya 'linear_trend'
)

# Returns:
# {
#     'forecast': [
#         {'date': '2024-04-01', 'forecast_value': 92.5, 'confidence': 'medium'},
#         {'date': '2024-05-01', 'forecast_value': 93.0, 'confidence': 'medium'},
#         {'date': '2024-06-01', 'forecast_value': 93.5, 'confidence': 'medium'}
#     ],
#     'method': 'moving_average',
#     'historical_data': [...]
# }
```

---

### 2. Report Service ✅
**Süre:** 50 saat

**Oluşturulan Dosyalar:**
- `app/services/report_service.py` (400+ satır)

**Özellikler:**

**Performans Raporu:**
```python
from app.services.report_service import ReportService

# Detaylı performans raporu
report = ReportService.generate_performance_report(
    process_id=1,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    format='json'  # json, excel, pdf
)

# Returns:
# {
#     'report_info': {
#         'title': 'SR3 - Pazarlama Performans Raporu',
#         'process_code': 'SR3',
#         'start_date': '2024-01-01',
#         'end_date': '2024-12-31'
#     },
#     'summary': {
#         'overall_score': 85.5,
#         'total_kpis': 10,
#         'excellent_kpis': 3,
#         'good_kpis': 5,
#         'poor_kpis': 2
#     },
#     'kpi_details': [...],
#     'recommendations': [...]
# }
```

**Dashboard Raporu:**
```python
# Tenant geneli özet rapor
dashboard = ReportService.generate_dashboard_report(
    tenant_id=1,
    year=2024
)

# Returns:
# {
#     'summary': {
#         'total_processes': 15,
#         'total_kpis': 120,
#         'average_performance': 88.3,
#         'excellent_processes': 5,
#         'good_processes': 8,
#         'poor_processes': 2
#     },
#     'top_performers': [...],
#     'needs_attention': [...]
# }
```

**Özel Rapor:**
```python
# Kullanıcı tanımlı özel rapor
custom_report = ReportService.generate_custom_report({
    'title': 'Q1 2024 Performans Raporu',
    'process_ids': [1, 2, 3],
    'kpi_ids': [10, 20, 30],
    'start_date': '2024-01-01',
    'end_date': '2024-03-31',
    'metrics': ['trend', 'comparison', 'forecast'],
    'format': 'json'
})
```

**Excel Export:**
```python
# Excel formatında rapor
excel_data = ReportService.generate_performance_report(
    process_id=1,
    start_date=datetime(2024, 1, 1),
    end_date=datetime(2024, 12, 31),
    format='excel'
)

# Excel dosyasını indir
return send_file(
    io.BytesIO(excel_data),
    mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    as_attachment=True,
    download_name='performance_report.xlsx'
)
```

---

### 3. Dashboard Builder ✅
**Süre:** 50 saat

**Oluşturulan Dosyalar:**
- `static/js/components/dashboard-builder.js` (300+ satır)
- `static/js/modules/chart-utils.js` (300+ satır)

**Özellikler:**

**Widget Tipleri:**
- KPI Kartı (tek metrik gösterimi)
- Trend Grafiği (zaman serisi)
- Performans Tablosu (liste)
- Süreç Sağlık Skoru
- Karşılaştırma Grafiği (radar chart)
- Tahmin Grafiği (forecast)

**Drag & Drop:**
```javascript
// Dashboard builder kullanımı
const { createApp } = Vue;

createApp({
    components: {
        'dashboard-builder': DashboardBuilder
    }
}).mount('#app');
```

**Widget Ekleme:**
```javascript
// Yeni widget ekle
dashboardBuilder.addWidget({
    type: 'kpi-card',
    name: 'Müşteri Memnuniyeti',
    config: {
        kpi_id: 10,
        value: 85,
        target: 90,
        unit: '%'
    }
});
```

**Layout Kaydetme:**
```javascript
// Dashboard layout'u kaydet
await dashboardBuilder.saveDashboard();
```

---

## 📦 DOSYA YAPISI

```
app/services/
├── analytics_service.py         ✅ Yeni (500 satır)
└── report_service.py            ✅ Yeni (400 satır)

static/js/
├── components/
│   └── dashboard-builder.js     ✅ Yeni (300 satır)
└── modules/
    └── chart-utils.js           ✅ Yeni (300 satır)
```

---

## 🚀 KURULUM

### 1. Bağımlılıkları Yükle
```bash
pip install pandas openpyxl
```

**Yeni Paketler:**
- pandas (veri analizi)
- openpyxl (Excel export)

### 2. Frontend Kütüphaneleri

**base.html'e ekle:**
```html
<!-- Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.js"></script>

<!-- Gridster.js (Dashboard Builder) -->
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/jquery.gridster/0.5.6/jquery.gridster.min.css">
<script src="https://cdnjs.cloudflare.com/ajax/libs/jquery.gridster/0.5.6/jquery.gridster.min.js"></script>

<!-- Chart Utils -->
<script src="{{ url_for('static', filename='js/modules/chart-utils.js') }}"></script>

<!-- Dashboard Builder -->
<script src="{{ url_for('static', filename='js/components/dashboard-builder.js') }}"></script>
```

---

## 📊 KULLANIM ÖRNEKLERİ

### Backend - Analytics

**Trend Grafiği Verisi:**
```python
@app.route('/api/analytics/trend/<int:kpi_id>')
def get_trend(kpi_id):
    trend = AnalyticsService.get_performance_trend(
        process_id=request.args.get('process_id'),
        kpi_id=kpi_id,
        start_date=datetime.strptime(request.args.get('start_date'), '%Y-%m-%d'),
        end_date=datetime.strptime(request.args.get('end_date'), '%Y-%m-%d'),
        frequency=request.args.get('frequency', 'monthly')
    )
    return jsonify(trend)
```

**Süreç Sağlık Skoru:**
```python
@app.route('/api/analytics/health/<int:process_id>')
def get_health(process_id):
    health = AnalyticsService.get_process_health_score(
        process_id=process_id,
        year=request.args.get('year', datetime.now().year)
    )
    return jsonify(health)
```

**Rapor İndirme:**
```python
@app.route('/api/reports/performance/<int:process_id>')
def download_report(process_id):
    excel_data = ReportService.generate_performance_report(
        process_id=process_id,
        start_date=datetime.strptime(request.args.get('start_date'), '%Y-%m-%d'),
        end_date=datetime.strptime(request.args.get('end_date'), '%Y-%m-%d'),
        format='excel'
    )
    
    return send_file(
        io.BytesIO(excel_data),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name=f'performance_report_{process_id}.xlsx'
    )
```

### Frontend - Charts

**Trend Grafiği:**
```javascript
// Trend verisi al
const response = await fetch(`/api/analytics/trend/${kpiId}?start_date=2024-01-01&end_date=2024-12-31&frequency=monthly`);
const data = await response.json();

// Grafik çiz
ChartUtils.createTrendChart('trendChart', data, {
    unit: '%'
});
```

**Performans Bar Chart:**
```javascript
// Performans verisi
const data = {
    labels: ['SR1', 'SR2', 'SR3', 'SR4', 'SR5'],
    values: [95, 87, 92, 78, 88]
};

// Bar chart çiz
ChartUtils.createPerformanceChart('performanceChart', data);
```

**Karşılaştırma Radar Chart:**
```javascript
// Karşılaştırma verisi
const data = {
    labels: ['KPI-1', 'KPI-2', 'KPI-3', 'KPI-4', 'KPI-5'],
    datasets: [
        {
            label: 'Süreç A',
            data: [95, 87, 92, 78, 88],
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.2)'
        },
        {
            label: 'Süreç B',
            data: [88, 92, 85, 90, 82],
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.2)'
        }
    ]
};

// Radar chart çiz
ChartUtils.createComparisonChart('comparisonChart', data);
```

**Tahmin Grafiği:**
```javascript
// Geçmiş ve tahmin verisi
const historical = {
    dates: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
    values: [85, 87, 90, 88, 92, 91]
};

const forecast = {
    dates: ['Jul', 'Aug', 'Sep'],
    values: [93, 94, 95]
};

// Forecast chart çiz
ChartUtils.createForecastChart('forecastChart', historical, forecast);
```

---

## 📈 ANALYTICS ÖZELL İKLERİ

### 1. Trend Analizi
- Günlük, haftalık, aylık, çeyreklik frekanslar
- Gerçekleşen vs Hedef karşılaştırması
- Performans oranı hesaplama
- Pandas ile veri işleme

### 2. Süreç Sağlık Skoru
- Ağırlıklı ortalama hesaplama
- Durum kategorileri (excellent, good, fair, poor, critical)
- Otomatik öneriler
- KPI bazlı detaylar

### 3. Karşılaştırmalı Analiz
- Çoklu süreç karşılaştırması
- En iyi/en kötü performans gösterenler
- Ortalama skor hesaplama
- Sıralama ve filtreleme

### 4. Anomali Tespiti
- Z-score yöntemi
- Standart sapma eşiği
- İstatistiksel analiz
- Sapma yüzdesi hesaplama

### 5. Tahminleme
- Moving average (hareketli ortalama)
- Linear trend (doğrusal trend)
- Güven seviyesi
- Geçmiş veri analizi

---

## 🎯 SONRAKI ADIMLAR

### Faz 2 Tamamlandı! 🎉

**Tamamlanan:**
- ✅ Sprint 7-9: Real-Time ve Bildirimler (150 saat)
- ✅ Sprint 10-12: Analytics ve Raporlama (180 saat)

**Faz 2 Toplam:** 330/330 saat (%100)

### Faz 3: İleri Seviye Özellikler
- Sprint 13-15: API ve Entegrasyonlar
- Sprint 16-18: AI ve Otomasyon
- Sprint 19-21: Mobil ve PWA

---

**Tamamlanma Tarihi:** 13 Mart 2026  
**Sonraki Faz:** Faz 3 (İleri Seviye)  
**Toplam İlerleme:** %68 (630/920 saat)
