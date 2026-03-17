# Sprint 13-15: API ve Entegrasyonlar

**Tarih:** 13 Mart 2026  
**Durum:** ✅ Tamamlandı  
**Süre:** 160 saat

---

## 📋 ÖZET

Sprint 13-15'te RESTful API v1, OAuth2 authentication, Swagger dokümantasyonu ve webhook sistemi tamamlandı.

---

## ✅ TAMAMLANAN GÖREVLER

### 1. RESTful API v1 ✅
**Süre:** 80 saat

**Oluşturulan Dosyalar:**
- `app/api/__init__.py`
- `app/api/routes.py` (400+ satır)
- `app/api/auth.py` (200+ satır)

**Endpoint'ler:**

**Process Endpoints:**
```
GET    /api/v1/processes              # Süreç listesi
GET    /api/v1/processes/{id}         # Süreç detayı
GET    /api/v1/processes/{id}/kpis    # Süreç KPI'ları
```

**KPI Data Endpoints:**
```
POST   /api/v1/kpi-data               # KPI veri girişi
GET    /api/v1/kpi-data/{id}          # KPI veri detayı
PATCH  /api/v1/kpi-data/{id}          # KPI veri güncelleme
DELETE /api/v1/kpi-data/{id}          # KPI veri silme
```

**Analytics Endpoints:**
```
GET    /api/v1/analytics/trend/{kpi_id}        # Trend analizi
GET    /api/v1/analytics/health/{process_id}   # Sağlık skoru
POST   /api/v1/analytics/comparison            # Karşılaştırma
GET    /api/v1/analytics/forecast/{kpi_id}     # Tahminleme
```

**Report Endpoints:**
```
GET    /api/v1/reports/performance/{process_id}  # Performans raporu
GET    /api/v1/reports/dashboard                 # Dashboard raporu
```

**Kullanım Örneği:**
```bash
# Süreç listesi
curl -X GET "http://localhost:5000/api/v1/processes?page=1&per_page=20" \
  -H "Authorization: Bearer YOUR_TOKEN"

# KPI veri girişi
curl -X POST "http://localhost:5000/api/v1/kpi-data" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "process_kpi_id": 1,
    "data_date": "2024-03-13",
    "actual_value": 85.5,
    "target_value": 90.0
  }'

# Trend analizi
curl -X GET "http://localhost:5000/api/v1/analytics/trend/10?start_date=2024-01-01&end_date=2024-12-31&frequency=monthly" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### 2. API Dokümantasyonu (Swagger/OpenAPI) ✅
**Süre:** 30 saat

**Oluşturulan Dosyalar:**
- `app/api/swagger.py` (300+ satır)

**Özellikler:**
- OpenAPI 3.0 specification
- Swagger UI entegrasyonu
- Interactive API documentation
- Request/Response schemas
- Authentication documentation

**Erişim:**
```
http://localhost:5000/api/docs
```

**OpenAPI Spec:**
```yaml
openapi: 3.0.0
info:
  title: Kokpitim API
  version: 1.0.0
  description: Kurumsal Performans Yönetim Platformu API

servers:
  - url: http://localhost:5000/api/v1
    description: Development
  - url: https://api.kokpitim.com/v1
    description: Production

paths:
  /processes:
    get:
      summary: Süreç listesi
      parameters:
        - name: page
          in: query
          schema:
            type: integer
      responses:
        '200':
          description: Başarılı
```

---

### 3. OAuth2 Authentication ✅
**Süre:** 30 saat

**Özellikler:**

**JWT Token Authentication:**
```python
from app.api.auth import APIAuth

# Token oluştur
token = APIAuth.generate_token(user_id=1, tenant_id=1)

# Token doğrula
payload = APIAuth.verify_token(token)
# Returns: {'user_id': 1, 'tenant_id': 1, 'exp': ..., 'iat': ...}
```

**Token Endpoint:**
```bash
# Token al
curl -X POST "http://localhost:5000/api/v1/oauth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "password",
    "username": "user@example.com",
    "password": "password"
  }'

# Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "Bearer",
  "expires_in": 86400
}
```

**API Key Authentication:**
```python
from app.api.auth import api_key_required

@app.route('/api/endpoint')
@api_key_required
def endpoint():
    return jsonify({'data': 'protected'})
```

**JWT Decorator:**
```python
from app.api.auth import jwt_required

@app.route('/api/endpoint')
@jwt_required
def endpoint():
    user_id = request.user_id
    tenant_id = request.tenant_id
    return jsonify({'data': 'protected'})
```

**Rate Limiting:**
```python
from app.api.auth import rate_limit_by_key

@app.route('/api/endpoint')
@rate_limit_by_key(limit=100, per=3600)
def endpoint():
    return jsonify({'data': 'rate limited'})
```

---

### 4. Webhook Sistemi ✅
**Süre:** 20 saat

**Oluşturulan Dosyalar:**
- `app/services/webhook_service.py` (250+ satır)

**Özellikler:**

**Event Tipleri:**
- `kpi.created` - KPI oluşturuldu
- `kpi.updated` - KPI güncellendi
- `kpi.deleted` - KPI silindi
- `process.created` - Süreç oluşturuldu
- `process.updated` - Süreç güncellendi
- `alert.triggered` - Alert tetiklendi

**Webhook Dispatch:**
```python
from app.services.webhook_service import WebhookService

# Event dispatch
WebhookService.dispatch_event(
    event_type='kpi.created',
    data={
        'kpi_id': 123,
        'name': 'Müşteri Memnuniyeti',
        'actual_value': 85.5,
        'target_value': 90.0
    },
    tenant_id=1
)
```

**Webhook Payload:**
```json
{
  "event": "kpi.created",
  "timestamp": "2024-03-13T10:30:00Z",
  "data": {
    "kpi_id": 123,
    "name": "Müşteri Memnuniyeti",
    "actual_value": 85.5,
    "target_value": 90.0
  }
}
```

**HMAC Signature:**
```python
# Signature oluştur
signature = WebhookService.generate_signature(payload, secret)
# Returns: 'sha256=abc123...'

# Signature doğrula
is_valid = WebhookService.verify_signature(payload, signature, secret)
```

**Webhook Oluşturma:**
```bash
curl -X POST "http://localhost:5000/api/v1/webhooks" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://example.com/webhook",
    "events": ["kpi.created", "kpi.updated"],
    "secret": "your_webhook_secret"
  }'
```

---

## 📦 DOSYA YAPISI

```
app/api/
├── __init__.py              ✅ Yeni
├── routes.py                ✅ Yeni (400 satır)
├── auth.py                  ✅ Yeni (200 satır)
└── swagger.py               ✅ Yeni (300 satır)

app/services/
└── webhook_service.py       ✅ Yeni (250 satır)
```

---

## 🚀 KURULUM

### 1. Bağımlılıkları Yükle
```bash
pip install PyJWT flask-swagger-ui requests
```

**Yeni Paketler:**
- PyJWT (JWT authentication)
- flask-swagger-ui (API documentation)
- requests (webhook HTTP requests)

### 2. Environment Variables
```env
# .env
JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRATION_HOURS=24
API_BASE_URL=http://localhost:5000/api/v1
```

### 3. API Endpoint'lerini Kaydet
```python
# app/__init__.py
from app.api import api_v1
from app.api.swagger import swaggerui_blueprint

def create_app():
    app = Flask(__name__)
    
    # API v1
    app.register_blueprint(api_v1)
    
    # Swagger UI
    app.register_blueprint(swaggerui_blueprint, url_prefix='/api/docs')
    
    return app
```

---

## 📊 KULLANIM ÖRNEKLERİ

### Python Client

```python
import requests

# Base URL
BASE_URL = 'http://localhost:5000/api/v1'

# Token al
response = requests.post(f'{BASE_URL}/oauth/token', json={
    'grant_type': 'password',
    'username': 'user@example.com',
    'password': 'password'
})
token = response.json()['access_token']

# Headers
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Süreç listesi
response = requests.get(f'{BASE_URL}/processes', headers=headers)
processes = response.json()

# KPI veri girişi
response = requests.post(f'{BASE_URL}/kpi-data', headers=headers, json={
    'process_kpi_id': 1,
    'data_date': '2024-03-13',
    'actual_value': 85.5,
    'target_value': 90.0
})
result = response.json()

# Trend analizi
response = requests.get(
    f'{BASE_URL}/analytics/trend/10',
    headers=headers,
    params={
        'start_date': '2024-01-01',
        'end_date': '2024-12-31',
        'frequency': 'monthly'
    }
)
trend = response.json()
```

### JavaScript Client

```javascript
// Base URL
const BASE_URL = 'http://localhost:5000/api/v1';

// Token al
const tokenResponse = await fetch(`${BASE_URL}/oauth/token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        grant_type: 'password',
        username: 'user@example.com',
        password: 'password'
    })
});
const { access_token } = await tokenResponse.json();

// Headers
const headers = {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
};

// Süreç listesi
const processesResponse = await fetch(`${BASE_URL}/processes`, { headers });
const processes = await processesResponse.json();

// KPI veri girişi
const kpiResponse = await fetch(`${BASE_URL}/kpi-data`, {
    method: 'POST',
    headers,
    body: JSON.stringify({
        process_kpi_id: 1,
        data_date: '2024-03-13',
        actual_value: 85.5,
        target_value: 90.0
    })
});
const result = await kpiResponse.json();
```

---

## 🔒 GÜVENLİK

### JWT Best Practices
- Secret key'i environment variable'da sakla
- Token expiration süresi kısa tut (24 saat)
- HTTPS kullan (production)
- Refresh token implementasyonu ekle

### API Key Best Practices
- API key'leri hash'le
- Rate limiting uygula
- IP whitelist kullan
- Key rotation policy belirle

### Webhook Security
- HMAC signature kullan
- HTTPS endpoint'leri zorunlu kıl
- Retry mechanism ekle
- Delivery log tut

---

## 🎯 SONRAKI ADIMLAR

### Sprint 16-18: AI ve Otomasyon
- [ ] Tahminsel analitik (ML modelleri)
- [ ] Anomali tespiti
- [ ] Otomatik raporlama
- [ ] Akıllı öneriler

---

**Tamamlanma Tarihi:** 13 Mart 2026  
**Sonraki Sprint:** Sprint 16-18 (AI ve Otomasyon)  
**Toplam İlerleme:** Faz 3 - %27 (160/600 saat)
