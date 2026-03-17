# Teknik Tasarım Belgesi — Micro Platform Geçişi

## 1. Mimari Genel Bakış

### Tek Blueprint Mimarisi

```
┌─────────────────────────────────────────────────────────────────┐
│                        Flask Uygulaması                         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                    micro_bp  (/micro)                    │   │
│  │                                                          │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │ masaustu │ │    sp    │ │  surec   │ │  kurum   │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐   │   │
│  │  │bireysel  │ │  admin   │ │   hgs    │ │  analiz  │   │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘   │   │
│  │  ┌──────────┐ ┌──────────────────────────────────────┐  │   │
│  │  │  proje   │ │  shared: auth / ayarlar / bildirim   │  │   │
│  │  └──────────┘ └──────────────────────────────────────┘  │   │
│  │  ┌──────────────────────────────────────────────────┐   │   │
│  │  │                  api (v1)                        │   │   │
│  │  └──────────────────────────────────────────────────┘   │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                 │
│  ┌──────────────────────┐   ┌──────────────────────────────┐   │
│  │    app/models/       │   │       app/services/          │   │
│  │  (paylaşımlı, salt   │   │  (paylaşımlı, salt okunur)   │   │
│  │   okunur)            │   │                              │   │
│  └──────────────────────┘   └──────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
```

### Katman Yapısı

```
İstek (HTTP)
    │
    ▼
@login_required  ──► Yetkisiz → /micro/auth/login
    │
    ▼
micro_bp route fonksiyonu
    │
    ├── HTML rotası → app/services/ → app/models/ → render_template()
    │
    └── API rotası  → app/services/ → app/models/ → jsonify()
                                                        │
                                              {"success": True/False,
                                               "message": "Türkçe mesaj"}
```

---

## 2. Hedef Dizin Yapısı

```
micro/
├── __init__.py                          # [GÜNCELLE] tüm yeni modül importları
├── core/
│   ├── launcher.py                      # mevcut
│   └── module_registry.py               # [GÜNCELLE] yeni modüller eklenir
├── modules/
│   ├── __init__.py
│   ├── masaustu/
│   │   ├── __init__.py
│   │   └── routes.py                    # mevcut
│   ├── sp/
│   │   ├── __init__.py
│   │   └── routes.py                    # [GÜNCELLE] sub-strategy + flow + graph
│   ├── surec/
│   │   ├── __init__.py
│   │   └── routes.py                    # [GÜNCELLE] tam CRUD + karne + KPI + faaliyet
│   ├── kurum/                           # [YENİ]
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── bireysel/                        # [YENİ]
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── admin/                           # [YENİ]
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── hgs/                             # [YENİ]
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── analiz/
│   │   ├── __init__.py
│   │   └── routes.py                    # [GÜNCELLE] trend + health + forecast + anomaly
│   ├── api/                             # [YENİ]
│   │   ├── __init__.py
│   │   └── routes.py
│   ├── proje/
│   │   ├── __init__.py
│   │   └── routes.py                    # mevcut (iskelet)
│   └── shared/
│       ├── __init__.py
│       ├── auth/
│       │   └── routes.py                # mevcut
│       ├── ayarlar/
│       │   └── routes.py                # mevcut
│       └── bildirim/
│           └── routes.py                # mevcut
├── templates/
│   └── micro/
│       ├── base.html                    # mevcut
│       ├── launcher.html                # mevcut
│       ├── masaustu/
│       │   └── index.html               # mevcut
│       ├── sp/
│       │   ├── index.html               # mevcut
│       │   ├── swot.html                # mevcut
│       │   ├── flow.html                # [YENİ]
│       │   └── dynamic_flow.html        # [YENİ]
│       ├── surec/
│       │   ├── index.html               # [GÜNCELLE]
│       │   └── karne.html               # [YENİ]
│       ├── kurum/
│       │   └── index.html               # [YENİ]
│       ├── bireysel/
│       │   └── karne.html               # [YENİ]
│       ├── admin/
│       │   ├── users.html               # [YENİ]
│       │   ├── tenants.html             # [YENİ]
│       │   └── packages.html            # [YENİ]
│       ├── hgs/
│       │   └── index.html               # [YENİ]
│       ├── analiz/
│       │   └── index.html               # [GÜNCELLE]
│       ├── auth/
│       │   └── login.html               # mevcut
│       ├── ayarlar/
│       │   └── index.html               # mevcut
│       └── bildirim/
│           └── index.html               # mevcut
└── static/
    └── micro/
        ├── js/
        │   ├── surec.js                 # [YENİ] süreç CRUD + karne
        │   ├── sp.js                    # [GÜNCELLE] sub-strategy + flow
        │   ├── kurum.js                 # [YENİ]
        │   ├── bireysel.js              # [YENİ]
        │   ├── admin.js                 # [YENİ]
        │   ├── analiz.js                # [GÜNCELLE]
        │   └── profil.js                # mevcut
        └── css/
            ├── app.css                  # mevcut
            ├── surec.css                # [YENİ]
            └── admin.css                # [YENİ]
```

---

## 3. Modül Route Tabloları

### 3.1 Süreç Yönetimi (`surec`)

| Method | URL | Fonksiyon | Açıklama | Rol |
|--------|-----|-----------|----------|-----|
| GET | `/micro/surec` | `surec` | Süreç listesi (hiyerarşik) | Tümü |
| GET | `/micro/surec/<id>/karne` | `surec_karne` | Süreç karnesi sayfası | Tümü |
| POST | `/micro/surec/api/add` | `surec_api_add` | Yeni süreç oluştur | tenant_admin, executive_manager |
| POST | `/micro/surec/api/update/<id>` | `surec_api_update` | Süreç güncelle | tenant_admin, executive_manager |
| POST | `/micro/surec/api/delete/<id>` | `surec_api_delete` | Süreç soft delete | tenant_admin, executive_manager |
| POST | `/micro/surec/api/kpi/add` | `surec_api_kpi_add` | KPI ekle | tenant_admin, executive_manager |
| POST | `/micro/surec/api/kpi/update/<id>` | `surec_api_kpi_update` | KPI güncelle | tenant_admin, executive_manager |
| POST | `/micro/surec/api/kpi/delete/<id>` | `surec_api_kpi_delete` | KPI soft delete | tenant_admin, executive_manager |
| GET | `/micro/surec/api/kpi/list/<id>` | `surec_api_kpi_list` | Sürece ait KPI listesi | Tümü |
| POST | `/micro/surec/api/activity/add` | `surec_api_activity_add` | Faaliyet ekle | Tümü |
| POST | `/micro/surec/api/activity/update/<id>` | `surec_api_activity_update` | Faaliyet güncelle | Tümü |
| POST | `/micro/surec/api/activity/delete/<id>` | `surec_api_activity_delete` | Faaliyet soft delete | Tümü |
| POST | `/micro/surec/api/kpi-data/add` | `surec_api_kpi_data_add` | KPI veri girişi | Tümü |
| GET | `/micro/surec/api/kpi-data/list/<id>` | `surec_api_kpi_data_list` | KPI veri listesi | Tümü |
| GET | `/micro/surec/api/karne/<id>` | `surec_api_karne` | Karne AJAX verisi | Tümü |
| POST | `/micro/surec/api/activity/track/<id>` | `surec_api_activity_track` | Aylık faaliyet takibi toggle | Tümü |

### 3.2 Stratejik Planlama (`sp`)

| Method | URL | Fonksiyon | Açıklama | Rol |
|--------|-----|-----------|----------|-----|
| GET | `/micro/sp` | `sp` | SP ana sayfası | Tümü |
| GET | `/micro/sp/swot` | `sp_swot` | SWOT analizi sayfası | Tümü |
| POST | `/micro/sp/api/swot/add` | `sp_add_swot` | SWOT maddesi ekle | Tümü |
| POST | `/micro/sp/api/swot/delete/<id>` | `sp_delete_swot` | SWOT soft delete | Tümü |
| POST | `/micro/sp/api/strategy/add` | `sp_add_strategy` | Ana strateji ekle | tenant_admin, executive_manager, Admin |
| POST | `/micro/sp/api/strategy/delete/<id>` | `sp_delete_strategy` | Ana strateji soft delete | tenant_admin, executive_manager, Admin |
| POST | `/micro/sp/api/sub-strategy/add` | `sp_add_sub_strategy` | Alt strateji ekle | tenant_admin, executive_manager, Admin |
| POST | `/micro/sp/api/sub-strategy/update/<id>` | `sp_update_sub_strategy` | Alt strateji güncelle | tenant_admin, executive_manager, Admin |
| POST | `/micro/sp/api/sub-strategy/delete/<id>` | `sp_delete_sub_strategy` | Alt strateji soft delete | tenant_admin, executive_manager, Admin |
| GET | `/micro/sp/flow` | `sp_flow` | Stratejik planlama akış sayfası | Tümü |
| GET | `/micro/sp/flow/dynamic` | `sp_flow_dynamic` | Dinamik graf sayfası | Tümü |
| GET | `/micro/sp/api/graph` | `sp_api_graph` | Graf node/edge verisi (JSON) | Tümü |

### 3.3 Kurum Paneli (`kurum`)

| Method | URL | Fonksiyon | Açıklama | Rol |
|--------|-----|-----------|----------|-----|
| GET | `/micro/kurum` | `kurum` | Kurum paneli ana sayfası | tenant_admin, executive_manager |
| POST | `/micro/kurum/api/update-strategy` | `kurum_api_update_strategy` | Stratejik kimlik güncelle | tenant_admin, executive_manager |
| POST | `/micro/kurum/api/add-strategy` | `kurum_api_add_strategy` | Ana strateji ekle | tenant_admin, executive_manager |
| POST | `/micro/kurum/api/add-sub-strategy` | `kurum_api_add_sub_strategy` | Alt strateji ekle | tenant_admin, executive_manager |
| POST | `/micro/kurum/api/update-main-strategy/<id>` | `kurum_api_update_main_strategy` | Ana strateji güncelle | tenant_admin, executive_manager |
| POST | `/micro/kurum/api/delete-main-strategy/<id>` | `kurum_api_delete_main_strategy` | Ana strateji soft delete | tenant_admin, executive_manager |
| POST | `/micro/kurum/api/update-sub-strategy/<id>` | `kurum_api_update_sub_strategy` | Alt strateji güncelle | tenant_admin, executive_manager |
| POST | `/micro/kurum/api/delete-sub-strategy/<id>` | `kurum_api_delete_sub_strategy` | Alt strateji soft delete | tenant_admin, executive_manager |

### 3.4 Bireysel Performans (`bireysel`)

| Method | URL | Fonksiyon | Açıklama | Rol |
|--------|-----|-----------|----------|-----|
| GET | `/micro/bireysel/karne` | `bireysel_karne` | Bireysel karne sayfası | Tümü |
| POST | `/micro/bireysel/api/pg/add` | `bireysel_api_pg_add` | Bireysel PG ekle | Tümü |
| POST | `/micro/bireysel/api/pg/update/<id>` | `bireysel_api_pg_update` | Bireysel PG güncelle | Tümü |
| POST | `/micro/bireysel/api/pg/delete/<id>` | `bireysel_api_pg_delete` | Bireysel PG soft delete | Tümü |
| POST | `/micro/bireysel/api/faaliyet/add` | `bireysel_api_faaliyet_add` | Bireysel faaliyet ekle | Tümü |
| POST | `/micro/bireysel/api/faaliyet/update/<id>` | `bireysel_api_faaliyet_update` | Bireysel faaliyet güncelle | Tümü |
| POST | `/micro/bireysel/api/faaliyet/delete/<id>` | `bireysel_api_faaliyet_delete` | Bireysel faaliyet soft delete | Tümü |
| POST | `/micro/bireysel/api/veri/add` | `bireysel_api_veri_add` | Bireysel KPI veri girişi | Tümü |
| POST | `/micro/bireysel/api/faaliyet/track/<id>` | `bireysel_api_faaliyet_track` | Aylık faaliyet takibi toggle | Tümü |
| GET | `/micro/bireysel/api/karne` | `bireysel_api_karne` | Bireysel karne AJAX verisi | Tümü |
| POST | `/micro/bireysel/api/favori/toggle/<id>` | `bireysel_api_favori_toggle` | Favori KPI toggle | Tümü |

### 3.5 Admin (`admin`)

| Method | URL | Fonksiyon | Açıklama | Rol |
|--------|-----|-----------|----------|-----|
| GET | `/micro/admin/users` | `admin_users` | Kullanıcı listesi | Admin, tenant_admin, executive_manager |
| POST | `/micro/admin/users/add` | `admin_users_add` | Kullanıcı ekle | Admin, tenant_admin, executive_manager |
| POST | `/micro/admin/users/edit/<id>` | `admin_users_edit` | Kullanıcı düzenle | Admin, tenant_admin, executive_manager |
| POST | `/micro/admin/users/toggle/<id>` | `admin_users_toggle` | Kullanıcı aktif/pasif (soft delete) | Admin, tenant_admin, executive_manager |
| GET | `/micro/admin/tenants` | `admin_tenants` | Kurum listesi | Admin, tenant_admin, executive_manager |
| POST | `/micro/admin/tenants/add` | `admin_tenants_add` | Kurum ekle | Admin |
| POST | `/micro/admin/tenants/edit/<id>` | `admin_tenants_edit` | Kurum düzenle | Admin, tenant_admin |
| POST | `/micro/admin/tenants/toggle/<id>` | `admin_tenants_toggle` | Kurum arşivle (soft delete) | Admin |
| GET | `/micro/admin/packages` | `admin_packages` | Paket ve modül yönetimi | Admin |
| POST | `/micro/admin/components/sync` | `admin_components_sync` | Rota keşfi → RouteRegistry | Admin |
| POST | `/micro/admin/components/update` | `admin_components_update` | component_slug güncelle | Admin |
| POST | `/micro/admin/users/bulk-import` | `admin_users_bulk_import` | Toplu kullanıcı içe aktarma | Admin, tenant_admin |

### 3.6 HGS — Hızlı Giriş Sistemi (`hgs`)

| Method | URL | Fonksiyon | Açıklama | Rol |
|--------|-----|-----------|----------|-----|
| GET | `/micro/hgs` | `hgs` | Hızlı giriş kullanıcı listesi | Herkese açık |
| GET | `/micro/hgs/login/<id>` | `hgs_login` | Seçilen kullanıcı ile giriş | Herkese açık |

### 3.7 Analiz Merkezi (`analiz`)

| Method | URL | Fonksiyon | Açıklama | Rol |
|--------|-----|-----------|----------|-----|
| GET | `/micro/analiz` | `analiz` | Analiz merkezi ana sayfası | Tümü |
| GET | `/micro/analiz/api/trend/<id>` | `analiz_api_trend` | KPI trend analizi | Tümü |
| GET | `/micro/analiz/api/health/<id>` | `analiz_api_health` | Süreç sağlık skoru | Tümü |
| GET | `/micro/analiz/api/forecast/<id>` | `analiz_api_forecast` | KPI tahmin analizi | Tümü |
| POST | `/micro/analiz/api/comparison` | `analiz_api_comparison` | Çoklu süreç karşılaştırma | Tümü |
| GET | `/micro/analiz/api/report/<id>` | `analiz_api_report` | Performans raporu (JSON/Excel) | Tümü |
| GET | `/micro/analiz/api/anomalies` | `analiz_api_anomalies` | Anomali tespiti | Tümü |

### 3.8 REST API Katmanı (`api`)

| Method | URL | Fonksiyon | Açıklama | Rol |
|--------|-----|-----------|----------|-----|
| GET | `/micro/api/v1/processes` | `api_processes_list` | Süreç listesi | Tümü |
| GET | `/micro/api/v1/processes/<id>` | `api_processes_detail` | Süreç detayı | Tümü |
| POST | `/micro/api/v1/kpi-data` | `api_kpi_data_create` | KPI veri oluştur | Tümü |
| GET | `/micro/api/v1/kpi-data/<id>` | `api_kpi_data_get` | KPI veri detayı | Tümü |
| PATCH | `/micro/api/v1/kpi-data/<id>` | `api_kpi_data_update` | KPI veri güncelle | Tümü |
| DELETE | `/micro/api/v1/kpi-data/<id>` | `api_kpi_data_delete` | KPI veri soft delete | Tümü |
| GET | `/micro/api/v1/analytics/trend/<id>` | `api_analytics_trend` | Trend analizi | Tümü |
| GET | `/micro/api/v1/analytics/health/<id>` | `api_analytics_health` | Sağlık skoru | Tümü |
| POST | `/micro/api/v1/analytics/comparison` | `api_analytics_comparison` | Karşılaştırma analizi | Tümü |
| GET | `/micro/api/v1/analytics/forecast/<id>` | `api_analytics_forecast` | Tahmin analizi | Tümü |
| GET | `/micro/api/v1/reports/performance/<id>` | `api_reports_performance` | Performans raporu | Tümü |
| GET | `/micro/api/v1/reports/dashboard` | `api_reports_dashboard` | Dashboard raporu | Tümü |
| GET | `/micro/api/v1/ai/*` | `api_ai_*` | AI servisleri (app/api/ai.py delegasyonu) | Tümü |
| GET | `/micro/api/v1/push/*` | `api_push_*` | Push bildirim (app/api/push.py delegasyonu) | Tümü |
| GET | `/micro/api/docs` | `api_docs` | Swagger/OpenAPI dokümantasyonu | Tümü |

---

## 4. Veri Akışı

### 4.1 Genel Request → Response Akışı

```
HTTP İsteği
    │
    ▼
Flask URL Router
    │
    ▼
micro_bp route fonksiyonu
    │
    ├─[HTML rota]──► @login_required
    │                    │
    │                    ▼
    │               tenant_id = current_user.tenant_id
    │                    │
    │                    ▼
    │               app/services/*.py  (iş mantığı)
    │                    │
    │                    ▼
    │               app/models/*.py    (SQLAlchemy sorgusu)
    │                    │  .filter_by(is_active=True)
    │                    │  .filter_by(tenant_id=tenant_id)
    │                    ▼
    │               render_template("micro/modül/sayfa.html", **ctx)
    │
    └─[API rota]───► @login_required
                         │
                         ▼
                    data = request.get_json()
                         │
                         ▼
                    Validasyon (zorunlu alanlar, yetki kontrolü)
                         │
                    ┌────┴────┐
                  Başarı    Hata
                    │         │
                    ▼         ▼
               db.session  db.session.rollback()
               .commit()   current_app.logger.error(...)
                    │         │
                    ▼         ▼
             jsonify({      jsonify({
               "success":    "success":
                True,         False,
               "message":    "message":
                "..."})       "Türkçe hata"
                             }), HTTP 4xx/5xx
```

### 4.2 Tenant İzolasyonu

Her sorguda `current_user.tenant_id` zorunlu olarak filtre olarak eklenir:

```python
# Doğru — tenant izolasyonu sağlanmış
Process.query.filter_by(
    tenant_id=current_user.tenant_id,
    is_active=True
).all()

# Yanlış — tenant izolasyonu eksik (YASAK)
Process.query.filter_by(is_active=True).all()
```

`current_user.tenant_id` değeri `None` ise:
- HTML rotalar: boş liste ile template render edilir, hata fırlatılmaz.
- API rotalar: `{"success": False, "message": "Kurum bilgisi bulunamadı."}` döner, HTTP 400.

### 4.3 Soft Delete Akışı

```
Silme İsteği (POST /micro/.../delete/<id>)
    │
    ▼
Kayıt sorgusu: .filter_by(id=id, tenant_id=...).first_or_404()
    │
    ▼
kayit.is_active = False
[Süreç için ek olarak:]
kayit.deleted_at = datetime.now(timezone.utc)
kayit.deleted_by = current_user.id
    │
    ▼
db.session.commit()
    │
    ▼
{"success": True, "message": "... silindi."}

Sonraki sorgularda:
.filter_by(is_active=True)  →  silinen kayıt artık görünmez
```

---

## 5. Frontend Mimarisi

### 5.1 Template Hiyerarşisi

```
micro/templates/micro/base.html          ← tüm sayfaların extends ettiği temel
    └── micro/templates/micro/<modül>/sayfa.html
            └── {% block content %} ... {% endblock %}
```

`base.html` içinde SweetAlert2 CDN ve ortak JS/CSS linkleri bulunur. Her modül sayfası yalnızca `{% block content %}` bloğunu doldurur.

### 5.2 JS/CSS Dosya Organizasyonu

```
micro/static/micro/
├── js/
│   ├── surec.js        # Süreç CRUD, karne, KPI, faaliyet işlemleri
│   ├── sp.js           # SWOT, strateji, sub-strategy, flow/graph
│   ├── kurum.js        # Kurum paneli stratejik kimlik işlemleri
│   ├── bireysel.js     # Bireysel PG, faaliyet, veri girişi
│   ├── admin.js        # Kullanıcı/kurum/paket yönetimi, bulk import
│   ├── analiz.js       # Trend, health, forecast, anomaly grafikleri
│   └── profil.js       # Profil ve ayarlar işlemleri (mevcut)
└── css/
    ├── app.css         # Global stiller (mevcut)
    ├── surec.css       # Süreç/karne özel stiller
    └── admin.css       # Admin panel özel stiller
```

### 5.3 data-* Pattern — Jinja2 → JS Veri Aktarımı

Jinja2 değişkenleri `.js` dosyalarında kullanılamaz. Veri aktarımı HTML `data-*` attribute'ları üzerinden yapılır:

```html
<!-- Template (HTML) — Jinja2 burada kullanılır -->
<div id="surec-container"
     data-process-id="{{ process.id }}"
     data-tenant-id="{{ current_user.tenant_id }}"
     data-current-year="{{ current_year }}">
</div>

<button class="btn-kpi-delete"
        data-kpi-id="{{ kpi.id }}"
        data-kpi-name="{{ kpi.name }}">
  Sil
</button>
```

```javascript
// surec.js — data-* ile okuma (Jinja2 {{ }} YASAK)
const container = document.getElementById('surec-container');
const processId = container.dataset.processId;
const currentYear = container.dataset.currentYear;

document.querySelectorAll('.btn-kpi-delete').forEach(btn => {
  btn.addEventListener('click', () => {
    const kpiId = btn.dataset.kpiId;
    const kpiName = btn.dataset.kpiName;
    // ...
  });
});
```

### 5.4 SweetAlert2 Standart Kalıpları

```javascript
// Başarı bildirimi (yeşil)
Swal.fire({
  icon: 'success',
  title: 'Başarılı',
  text: 'Süreç başarıyla eklendi.',
  confirmButtonColor: '#16a34a'
});

// Hata bildirimi (kırmızı)
Swal.fire({
  icon: 'error',
  title: 'Hata',
  text: 'Kayıt sırasında bir hata oluştu.',
  confirmButtonColor: '#dc2626'
});

// Silme onayı
Swal.fire({
  title: 'Emin misiniz?',
  text: `"${name}" silinecek. Bu işlem geri alınamaz.`,
  icon: 'warning',
  showCancelButton: true,
  confirmButtonColor: '#dc2626',
  cancelButtonColor: '#6b7280',
  confirmButtonText: 'Evet, Sil',
  cancelButtonText: 'İptal'
}).then(result => {
  if (result.isConfirmed) {
    // silme isteği gönder
  }
});
```

**Kesinlikle yasak:**
```javascript
alert('...');      // YASAK
confirm('...');    // YASAK
prompt('...');     // YASAK
```

---

## 6. Module Registry Güncellemesi

`micro/core/module_registry.py` dosyasına aşağıdaki modüller eklenecek:

```python
MODULES = [
    # --- Mevcut modüller ---
    {"id": "masaustu",  "name": "Masaüstüm",          "url": "/micro/masaustu",  "icon": "🏠", ...},
    {"id": "sp",        "name": "Stratejik Planlama",  "url": "/micro/sp",        "icon": "🎯", ...},
    {"id": "surec",     "name": "Süreç Yönetimi",      "url": "/micro/surec",     "icon": "⚙️", ...},
    {"id": "proje",     "name": "Proje Yönetimi",      "url": "/micro/proje",     "icon": "📋", ...},
    {"id": "analiz",    "name": "Analiz Merkezi",      "url": "/micro/analiz",    "icon": "📊", ...},
    {"id": "ayarlar",   "name": "Ayarlar",             "url": "/micro/ayarlar",   "icon": "⚙️", ...},
    {"id": "bildirim",  "name": "Bildirim Merkezi",    "url": "/micro/bildirim",  "icon": "🔔", ...},

    # --- Yeni modüller ---
    {"id": "kurum",     "name": "Kurum Paneli",        "url": "/micro/kurum",     "icon": "🏢",
     "description": "Kurum performans özeti ve stratejik kimlik yönetimi"},
    {"id": "bireysel",  "name": "Bireysel Performans", "url": "/micro/bireysel/karne", "icon": "👤",
     "description": "Kişisel PG'ler, faaliyetler ve bireysel karne"},
    {"id": "admin",     "name": "Yönetim Paneli",      "url": "/micro/admin/users", "icon": "🛡️",
     "description": "Kullanıcı, kurum ve paket yönetimi"},
    {"id": "hgs",       "name": "Hızlı Giriş",         "url": "/micro/hgs",       "icon": "⚡",
     "description": "Geliştirme ortamı hızlı kullanıcı geçişi"},
    {"id": "api",       "name": "API Dokümantasyonu",  "url": "/micro/api/docs",  "icon": "🔌",
     "description": "REST API v1 S