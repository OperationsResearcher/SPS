# Sprint 7-9: Real-Time ve Bildirimler

**Tarih:** 13 Mart 2026  
**Durum:** ✅ Tamamlandı  
**Süre:** 150 saat

---

## 📋 ÖZET

Sprint 7-9'da real-time özellikler ve akıllı bildirim sistemi tamamlandı. WebSocket entegrasyonu, real-time collaboration ve bildirim yönetimi eklendi.

---

## ✅ TAMAMLANAN GÖREVLER

### 1. WebSocket (Flask-SocketIO) ✅
**Süre:** 60 saat

**Oluşturulan Dosyalar:**
- `app/socketio_events.py` (200+ satır)
- `app/extensions.py` (güncellendi)
- `static/js/modules/notification-manager.js` (400+ satır)

**Özellikler:**

**WebSocket Events:**
```python
@socketio.on('connect')
def handle_connect():
    # Kullanıcı bağlandı
    join_room(f'user_{user_id}')

@socketio.on('join_process')
def handle_join_process(data):
    # Süreç room'una katıl
    join_room(f'process_{process_id}')

@socketio.on('kpi_data_update')
def handle_kpi_data_update(data):
    # KPI güncellemesini broadcast et
    emit('kpi_updated', data, room=f'process_{process_id}')
```

**Client-Side:**
```javascript
// WebSocket bağlantısı
const socket = io();

// Yeni bildirim
socket.on('new_notification', (data) => {
    notificationManager.handleNewNotification(data);
});

// KPI güncellendi
socket.on('kpi_updated', (data) => {
    updateKpiInUI(data.kpi_id, data.field, data.value);
});
```

---

### 2. Real-Time Collaboration ✅
**Süre:** 40 saat

**Özellikler:**

**Aktif Kullanıcı Tracking:**
- Kullanıcı sayfaya katıldığında diğerlerine bildirim
- Kullanıcı ayrıldığında bildirim
- Aktif kullanıcı listesi

**Real-Time Data Updates:**
- KPI veri girişi anında diğer kullanıcılara yansır
- Typing indicators (kullanıcı yazıyor göstergesi)
- Conflict prevention (çakışma önleme)

**Kullanım:**
```javascript
// Süreç room'una katıl
notificationManager.joinProcess(processId);

// KPI güncellemesini broadcast et
notificationManager.broadcastKpiUpdate(processId, kpiId, 'actual_value', 85);

// Süreç room'undan ayrıl
notificationManager.leaveProcess(processId);
```

---

### 3. Akıllı Bildirim Sistemi ✅
**Süre:** 50 saat

**Oluşturulan Dosyalar:**
- `app/services/notification_service.py` (300+ satır)
- `app/models/notification.py` (150+ satır)
- `static/css/notifications.css` (300+ satır)
- `migrations/versions/003_add_notifications.py` (100+ satır)

**Bildirim Tipleri:**

**1. Performans Uyarıları:**
```python
NotificationService.send_performance_alert(
    user_id=user.id,
    kpi_name='Müşteri Memnuniyeti',
    actual=85,
    target=90,
    deviation=-5.5
)
```

**2. Görev Hatırlatıcıları:**
```python
NotificationService.send_task_reminder(
    user_id=user.id,
    task_description='5 KPI için veri girişi bekleniyor',
    due_date=datetime.now() + timedelta(days=2),
    days_remaining=2
)
```

**3. İşbirliği Bildirimleri:**
```python
NotificationService.send_collaboration_notification(
    user_id=user.id,
    actor_name='Ahmet Yılmaz',
    action='sizi SR4 sürecine lider olarak ekledi',
    resource='SR4 - Satış Süreci'
)
```

**4. Başarı Kutlamaları:**
```python
NotificationService.send_achievement_notification(
    user_id=user.id,
    achievement='Q1 Hedeflerinin %95\'ini Tamamladınız',
    description='Tebrikler! Bu çeyrekte harika bir performans gösterdiniz.'
)
```

**Bildirim Öncelikleri:**
- `urgent` - Acil (kırmızı)
- `high` - Yüksek (turuncu)
- `medium` - Orta (mavi)
- `low` - Düşük (gri)

---

## 📦 DOSYA YAPISI

```
app/
├── services/
│   └── notification_service.py      ✅ Yeni (300 satır)
├── models/
│   └── notification.py              ✅ Yeni (150 satır)
├── socketio_events.py               ✅ Yeni (200 satır)
└── extensions.py                    ✅ Güncellendi

static/
├── js/modules/
│   └── notification-manager.js      ✅ Yeni (400 satır)
└── css/
    └── notifications.css            ✅ Yeni (300 satır)

migrations/versions/
└── 003_add_notifications.py         ✅ Yeni (100 satır)
```

---

## 🚀 KURULUM

### 1. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

**Yeni Paketler:**
- Flask-SocketIO (WebSocket desteği)
- python-socketio (Socket.IO client)
- eventlet (Async server)

### 2. Database Migration
```bash
flask db upgrade
```

### 3. Frontend Entegrasyonu

**base.html'e ekle:**
```html
<!-- Socket.IO Client -->
<script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

<!-- Notification CSS -->
<link href="{{ url_for('static', filename='css/notifications.css') }}" rel="stylesheet">

<!-- Notification Manager -->
<script src="{{ url_for('static', filename='js/modules/notification-manager.js') }}"></script>
```

**Notification Bell:**
```html
<div class="notification-bell">
    <i class="fas fa-bell"></i>
    <span class="notification-badge" style="display: none;">0</span>
</div>

<div class="notification-panel">
    <div class="notification-header">
        <div class="notification-title">Bildirimler</div>
        <button class="mark-all-read">Tümünü Okundu İşaretle</button>
    </div>
    <div class="notification-list"></div>
</div>
```

### 4. Server Başlatma
```python
# app/__init__.py
from app.extensions import socketio
from app import socketio_events

def create_app():
    app = Flask(__name__)
    # ... diğer konfigürasyonlar
    
    socketio.init_app(app)
    return app

# run.py
from app import create_app
from app.extensions import socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, debug=True, port=5000)
```

---

## 📊 KULLANIM ÖRNEKLERİ

### Backend - Bildirim Gönderme

**Performans Uyarısı:**
```python
from app.services.notification_service import NotificationService

# KPI hedefin altında
if kpi.actual_value < kpi.target_value * 0.8:
    deviation = ((kpi.actual_value - kpi.target_value) / kpi.target_value) * 100
    
    NotificationService.send_performance_alert(
        user_id=kpi.owner_id,
        kpi_name=kpi.name,
        actual=kpi.actual_value,
        target=kpi.target_value,
        deviation=deviation
    )
```

**Görev Hatırlatıcısı:**
```python
# Veri girişi beklenen KPI'lar
pending_kpis = get_pending_kpis(user_id)

if len(pending_kpis) > 0:
    NotificationService.send_task_reminder(
        user_id=user_id,
        task_description=f'{len(pending_kpis)} KPI için veri girişi bekleniyor',
        due_date=datetime.now() + timedelta(days=2),
        days_remaining=2
    )
```

**İşbirliği Bildirimi:**
```python
# Kullanıcı sürece eklendi
NotificationService.send_collaboration_notification(
    user_id=new_member.id,
    actor_name=current_user.full_name,
    action='sizi süreç ekibine ekledi',
    resource=process.name
)
```

### Frontend - Real-Time Collaboration

**Süreç Sayfasında:**
```javascript
// Sayfa yüklendiğinde
const processId = 123;
notificationManager.joinProcess(processId);

// KPI güncellendiğinde
function updateKpi(kpiId, field, value) {
    // Backend'e kaydet
    await saveKpiData(kpiId, field, value);
    
    // Diğer kullanıcılara broadcast et
    notificationManager.broadcastKpiUpdate(processId, kpiId, field, value);
}

// Sayfa kapatılırken
window.addEventListener('beforeunload', () => {
    notificationManager.leaveProcess(processId);
});
```

**Bildirim Dinleme:**
```javascript
// Yeni bildirim geldiğinde
notificationManager.socket.on('new_notification', (notification) => {
    console.log('New notification:', notification);
    // Toast göster
    // Badge güncelle
    // Liste güncelle
});

// KPI güncellendiğinde
notificationManager.socket.on('kpi_updated', (data) => {
    console.log(`KPI ${data.kpi_id} updated by ${data.updated_by}`);
    // UI'da güncelle
    updateKpiInUI(data.kpi_id, data.field, data.value);
});
```

---

## 🎨 UI COMPONENT'LERİ

### Notification Bell
```html
<div class="notification-bell" onclick="toggleNotifications()">
    <i class="fas fa-bell"></i>
    <span class="notification-badge">3</span>
</div>
```

### Notification Panel
```html
<div class="notification-panel open">
    <div class="notification-header">
        <div class="notification-title">Bildirimler</div>
        <button class="mark-all-read">Tümünü Okundu İşaretle</button>
    </div>
    <div class="notification-list">
        <div class="notification-item unread priority-high">
            <div class="notification-icon">⚠️</div>
            <div class="notification-content">
                <div class="notification-title">Performans Uyarısı</div>
                <div class="notification-message">Müşteri Memnuniyeti hedefin %5.5 altında</div>
                <div class="notification-time">5 dakika önce</div>
            </div>
            <div class="notification-dot"></div>
        </div>
    </div>
</div>
```

### Notification Toast
```html
<div class="notification-toast priority-high">
    <div class="toast-icon">⚠️</div>
    <div class="toast-content">
        <div class="toast-title">Performans Uyarısı</div>
        <div class="toast-message">Müşteri Memnuniyeti hedefin %5.5 altında</div>
    </div>
    <button class="toast-close">&times;</button>
</div>
```

---

## 📈 PERFORMANS VE ÖLÇEKLENEBİLİRLİK

### WebSocket Connection Pooling
```python
# config.py
SOCKETIO_MESSAGE_QUEUE = 'redis://localhost:6379/0'
SOCKETIO_ASYNC_MODE = 'eventlet'
```

### Notification Batching
```python
# Toplu bildirim gönderimi
def send_daily_digest(user_id):
    notifications = get_unread_notifications(user_id, last_24_hours=True)
    
    if len(notifications) > 0:
        send_email_digest(user_id, notifications)
```

### Database Optimization
- İndeksler: user_id, is_read, created_at
- Eski bildirimleri temizleme (30 gün+)
- Pagination (50 bildirim/sayfa)

---

## 🔒 GÜVENLİK

### WebSocket Authentication
```python
@socketio.on('connect')
def handle_connect():
    if not current_user.is_authenticated:
        return False  # Bağlantıyı reddet
```

### Room Authorization
```python
@socketio.on('join_process')
def handle_join_process(data):
    process_id = data.get('process_id')
    
    # Kullanıcının bu sürece erişimi var mı?
    if not user_has_access(current_user.id, process_id):
        return False
    
    join_room(f'process_{process_id}')
```

### Rate Limiting
```python
# WebSocket event rate limiting
@limiter.limit("100 per minute")
@socketio.on('kpi_data_update')
def handle_kpi_data_update(data):
    # ...
```

---

## 🎯 SONRAKI ADIMLAR

### Sprint 10-12: Analytics ve Raporlama
- [ ] Dashboard builder
- [ ] Özel rapor oluşturma
- [ ] Trend analizi
- [ ] Export formatları (PDF, PPT)

---

**Tamamlanma Tarihi:** 13 Mart 2026  
**Sonraki Sprint:** Sprint 10-12 (Analytics ve Raporlama)  
**Toplam İlerleme:** Faz 2 - %45 (150/330 saat)
