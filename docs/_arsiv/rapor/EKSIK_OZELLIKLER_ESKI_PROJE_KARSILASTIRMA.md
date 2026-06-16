# Kokpitim – Eski Projeden Yeniye Aktarılmamış Özellikler Listesi

**Konu:** Süreçler, Süreç, Süreç Karnesi, Performans Göstergesi, Performans Göstergesi Verisi  
**Tarih:** 2026-02-21

---

## 1. MODELLER (Veritabanı) – EKSİK OLANLAR

| Eski Proje | Yeni Proje | Durum |
|------------|------------|-------|
| `Surec` (kurum_id, stratejik_donem_id) | `Process` (tenant_id) | ✅ Var (stratejik_donem yok) |
| `SurecPerformansGostergesi` | `ProcessKpi` | ✅ Var |
| `SurecFaaliyet` | `ProcessActivity` | ✅ Var |
| `BireyselPerformansGostergesi` | — | ❌ **YOK** |
| `BireyselFaaliyet` | — | ❌ **YOK** |
| `PerformansGostergeVeri` (bireysel_pg_id) | `KpiData` (process_kpi_id) | Kısmen: KpiData süreç KPI’sına bağlı, bireysel PG yok |
| `PerformansGostergeVeriAudit` | — | ❌ **YOK** |
| `FaaliyetTakip` (bireysel faaliyet aylık takip) | `ActivityTrack` | Kısmen: ActivityTrack süreç faaliyetine bağlı |
| `FavoriPerformansGostergesi` | — | ❌ **YOK** |

---

## 2. ROTALAR (Routes) – EKSİK OLANLAR

### 2.1 Süreç Paneli (process panel)
| Eski Rota | Yeni Karşılık | Durum |
|-----------|----------------|-------|
| `/surec-paneli` | `/process/` | ✅ Var |
| `/surec/<id>` | — | ❌ Süreç detay sayfası yok |
| `/surec/update/<id>` | `/process/api/update/<id>` | ✅ Var |
| `/surec/get/<id>` | `/process/api/get/<id>` | ✅ Var |
| `/surec/add-simple` | `/process/api/add` | ✅ Var |
| `/surec/delete/<id>` | `/process/api/delete/<id>` | ✅ Var |
| `/admin/get-process/<id>` | — | ❌ Admin süreç get yok |
| `/admin/create-process` | — | ❌ Admin süreç oluşturma yok |
| `/admin/add-process` | — | ❌ Admin süreç ekleme yok |
| `/admin/delete-process/<id>` | — | ❌ Admin süreç silme yok |
| **Sayfalama (pagination)** | — | ❌ Eski projede surec_paneli sayfalı, yeni projede tüm liste tek sayfa |

### 2.2 Süreç Karnesi (process karne)
| Eski Rota | Yeni Karşılık | Durum |
|-----------|----------------|-------|
| `/surec-karnesi` | `/process/<id>/karne` | ✅ Var (URL farklı) |
| `/api/kullanici-surecleri` | — | ❌ Kullanıcının süreç listesi API’si yok |
| `/surec/<id>/faaliyetler` | `/process/api/...` (faaliyet listesi) | Kısmen: activity API’leri var |
| `/surec/<id>/faaliyet/add` | `/process/api/activity/add` | ✅ Var |
| `/surec/<id>/faaliyet/<id>/update` | `/process/api/activity/update/<id>` | ✅ Var |
| `/surec/<id>/faaliyet/<id>/delete` | `/process/api/activity/delete/<id>` | ✅ Var |
| `/api/surec/<id>/karne/performans` | `/process/api/karne/<id>` | ✅ Var |
| `/api/surec/<id>/karne/faaliyetler` | — | ❌ Karne faaliyet listesi API’si (bireysel takip dahil) |
| `/api/surec/<id>/karne/kaydet` | `/process/api/kpi-data/add` vb. | Kısmen: farklı veri yapısı |
| `/api/surec/karne/pg-veri-detay` | — | ❌ PG veri detay API’si yok |
| `/api/export/surec_karnesi/excel` | — | ❌ **Excel dışa aktarma yok** |
| `/api/surec/<id>/saglik-skoru` | — | ❌ Süreç sağlık skoru API’si yok |
| `/api/surec/<id>/uyeler` | — | ❌ Süreç üyeleri API’si yok |
| `/api/surec/<id>/faaliyet/<id>/create-bireysel` | — | ❌ Süreç faaliyetinden bireysel faaliyet oluşturma yok |
| `/api/faaliyet/<id>/takip` | `/process/api/activity/track` | ✅ Var (yapı farklı olabilir) |
| `/api/surec/<id>/performans-gostergesi/<id>/dagit` | — | ❌ PG’yi kullanıcılara dağıtma yok |

### 2.3 Performans Göstergesi (routes_process_pg)
| Eski Rota | Yeni Karşılık | Durum |
|-----------|----------------|-------|
| `/surec/<id>/performans-gostergesi/add` | `/process/api/kpi/add` | ✅ Var |
| `/surec/<id>/performans-gostergesi/<id>` (GET) | `/process/api/kpi/get/<id>` | ✅ Var |
| `/surec/<id>/performans-gostergesi/<id>/update` | `/process/api/kpi/update/<id>` | ✅ Var |
| `/surec/<id>/performans-gostergesi/<id>/delete` | `/process/api/kpi/delete/<id>` | ✅ Var |

### 2.4 Performans Kartım (Bireysel Panel)
| Eski Rota | Yeni Karşılık | Durum |
|-----------|----------------|-------|
| `/performans-kartim` | — | ❌ **Tamamen eksik** |

---

## 3. ŞABLONLAR (Templates) – EKSİK OLANLAR

| Eski Şablon | Yeni Karşılık | Durum |
|-------------|---------------|-------|
| `surec_panel.html` | `process/panel.html` | ✅ Var |
| `surec_karnesi.html` | `process/karne.html` | ✅ Var |
| `bireysel_panel.html` | — | ❌ **Performans Kartım sayfası yok** |

---

## 4. JAVASCRIPT / FRONTEND – EKSİK OLANLAR

| Eski Dosya/Özellik | Durum |
|--------------------|-------|
| `static/js/surec_karnesi.js` (monolitik) | Yeni projede karne.js veya benzeri parçalı yapı |
| `static/js/modules/surec_karnesi/main.js` | ❌ Modüler süreç karnesi JS yok |
| `static/js/modules/surec_karnesi/api.js` | ❌ |
| `static/js/modules/surec_karnesi/events.js` | ❌ |
| `static/js/modules/surec_karnesi/ui_render.js` | ❌ |
| `static/js/modules/surec_karnesi/calculations.js` | ❌ |
| `bireysel_panel.js` | ❌ Performans Kartım JS yok |
| **Süreç karnesi hesaplamaları** (başarı puanı, ağırlıklı puan, çeyreklik veri) | Kısmen: utils/karne_hesaplamalar benzeri yapı yeni projede yok |
| **Proje–PG görev ilişkisi** (`loadPGProjeGorevleri`) | ❌ |

---

## 5. YARDIMCI MODÜLLER / SERVİSLER – EKSİK OLANLAR

| Eski Modül | Durum |
|------------|-------|
| `utils/karne_hesaplamalar.py` | ❌ Başarı puanı, aralık parse, hesaplama fonksiyonları yok |
| `main/process_utils.py` | Kısmen: yeni projede benzer helper’lar route içinde |
| `services/score_engine_service.py` (PG veri → skor) | ❌ |
| `services/notification_service.py` (PG sapma uyarısı) | ❌ |
| `services/audit_service.py` (PG veri audit) | ❌ |
| `services/muda_analyzer.py` (PG veri analizi) | ❌ |

---

## 6. İŞLEVSEL ÖZELLİKLER – ÖZET

### 6.1 Tamamen Eksik
1. **Performans Kartım (Bireysel Panel)** – Kullanıcının kendi hedefleri, PG’leri ve faaliyetleri
2. **BireyselPerformansGostergesi** – Süreç PG’sinden kullanıcıya atanan hedefler
3. **BireyselFaaliyet** – Süreç faaliyetinden kullanıcıya atanan aksiyonlar
4. **PerformansGostergeVeri** (bireysel PG’ye bağlı) – Kullanıcı bazlı veri girişi
5. **PerformansGostergeVeriAudit** – Veri değişiklik denetim logu
6. **PG Dağıtım** – Süreç PG’sini seçili kullanıcılara bireysel hedef olarak atama
7. **Süreç faaliyetinden bireysel faaliyet oluşturma**
8. **Süreç karnesi Excel export**
9. **Süreç sağlık skoru API**
10. **Süreç üyeleri API**
11. **Karne PG veri detay API** (kullanıcı bazlı veri sorgulama)
12. **Karne hesaplama yardımcıları** (`karne_hesaplamalar.py`)
13. **Skor motoru** (PG verisi değişince vision/süreç skoru yenileme)
14. **Erken uyarı / PG performans sapması bildirimi**
15. **Admin süreç CRUD** (get-process, create-process, add-process, delete-process)
16. **Favori performans göstergeleri**

### 6.2 Kısmen Var
1. **Faaliyet takip** – ActivityTrack var ama bireysel faaliyet bağlantısı farklı
2. **KPI veri kaydetme** – KpiData var; bireysel PG ve çeyreklik/veri_tarihi yapısı farklı
3. **Süreç–strateji ilişkisi** – StrategyProcessMatrix eski projede var; yeni projede SubStrategy ilişkisi farklı

### 6.3 Mevcut (Yeni Projede Var)
1. Süreç listesi ve panel
2. Süreç CRUD (ekleme, güncelleme, silme)
3. Süreç Karnesi sayfası
4. Performans göstergesi (KPI) CRUD
5. Faaliyet CRUD
6. KPI veri (KpiData) ekleme ve listeleme
7. ActivityTrack (faaliyet takibi)
8. Karne API (process_id ile performans ve faaliyet verisi)

---

## 7. NAVİGASYON / MENÜ

| Eski | Yeni | Durum |
|------|------|-------|
| Süreç Paneli menü linki | process/ | Sidebar/navbar’da kontrol edilmeli |
| Süreç Karnesi menü linki | process/<id>/karne | Süreç seçildikten sonra |
| Performans Kartım menü linki | — | ❌ Yok |

---

*Bu liste eski proje (`eski_proje`) ile mevcut Kokpitim projesi karşılaştırmasına dayanmaktadır.*
