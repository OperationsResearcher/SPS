# 17_Ocak_Revize_Master_Plan

Bu doküman, SPS arayüzünün uçtan uca kullanılabilirlik değerlendirmesi ve altyapısal risk analizini birlikte ele alan bütünleşik bir “Gap Analysis & Action Plan”dır. Odak: kolay giriş aşamasını atlayıp doğrudan `dashboard` üzerinden ana kullanıcı akışlarının değerlendirilmesi, aynı zamanda veri tutarlılığı, güvenlik ve operasyonel risklerin kapatılmasıdır.

## 1) Test matrisi

### 1.1 Rol x Sayfa erişim durumu (HTTP kontrol)
Not: Aşağıdaki durumlar oturum açma + GET kontrolü ile doğrulandı. 302, erişim yok/redirect anlamına gelir.

| Rol | /dashboard | /admin-panel | /kurum-paneli | /surec-paneli | /surec-karnesi | /performans-kartim | /stratejik-planlama-akisi | /stratejik-asistan | /strategy/projects |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| admin | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 |
| kurum_yoneticisi | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 |
| ust_yonetim | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 | 200 |
| surec_lideri | 200 | 302 -> /dashboard | 302 -> /dashboard | 200 | 200 | 200 | 200 | 200 | 200 |
| surec_uyesi | 200 | 302 -> /dashboard | 302 -> /dashboard | 200 | 200 | 200 | 200 | 200 | 200 |

### 1.2 Test kullanıcılar
- admin / 123456
- tech_cto (kurum_yoneticisi) / 123456
- tech_ceo (ust_yonetim) / 123456
- dev_lead (surec_lideri) / 123456
- dev_user (surec_uyesi) / 123456

## 2) Sayfa bazlı bulgular ve aksiyon planı

### 2.1 `http://127.0.0.1:5001/dashboard`
**Dosya:** `C:\SPY_Cursor\SP_Code\templates\dashboard.html`  
**Route:** `C:\SPY_Cursor\SP_Code\main\routes.py` (dashboard)

**Bileşenler**
- Özet kartları, karar destek özeti, Chart.js grafikler
- Hızlı erişim kartları (Süreç Karnesi, Faaliyetler, Görevlerim, Profil, Stratejik Asistan)
- Muda Hunter Efficiency ve AI Insights blokları
- Stratejik İlerleme Durumu (yeni widget)

**Bulgular**
- `performance_score` backend’de sabit 94 değerinden geliyor; kullanıcıya anlamlı değil.
- `process_performance` grafik verisi list olarak dönüyor, Chart.js tarafında process isimleri bekleniyor.
- “Görevlerim” kartı ve “Performans Kartım” sayfası semantik olarak uyumsuz (performans kartı yerine görev kanban).
- Dashboard metrikleri Activity üzerinden hesaplanıyor; gerçek görev/iş akışını yansıtmıyor.

**Aksiyon**
- `performance_score` hesaplamasını gerçek KPI/PG verileri ile değiştir.
- `process_performance` için süreç adları ile skor listesi üret.
- “Performans Kartım” kartını gerçek performans sayfasına bağla veya sayfayı görev paneli olarak yeniden adlandır.
- Activity tabanlı istatistikleri Task tabanlı istatistiklere dönüştür (doğru domain verisi).

---

### 2.2 `http://127.0.0.1:5001/admin-panel`
**Dosya:** `C:\SPY_Cursor\SP_Code\templates\admin_panel.html`  
**Route:** `C:\SPY_Cursor\SP_Code\main\routes.py` (admin_panel)

**Bileşenler**
- Kurum, kullanıcı, süreç yönetimi tabları
- Çok sayıda modal, avatar seçim alanı
- Excel yükleme, profil/kurum logo upload
- Yetki matrisi (rol-matrisi1/2)

**Bulgular**
- `fetch('/admin/add-process'...)` endpoint’i backend’de yok; mevcut endpoint `/admin/create-process`. Süreç ekleme modalı bu yüzden çalışmaz.
- Çok fazla inline JS/HTML karmaşıklığı; bakım maliyeti yüksek.
- Admin panel giriş hakkı olmayan kullanıcılar menüde hala görebilir (base.html kontrolü net değil).

**Aksiyon**
- `/admin/add-process` çağrısını `/admin/create-process` ile eşle.
- Admin paneli JS’lerini parçalara ayır (modülerleştir).
- Base menüde rol bazlı link görünürlüğünü netleştir (admin/kurum_yoneticisi/ust_yonetim).

---

### 2.3 `http://127.0.0.1:5001/kurum-paneli`
**Dosya:** `C:\SPY_Cursor\SP_Code\templates\kurum_panel.html`  
**Route:** `C:\SPY_Cursor\SP_Code\main\routes.py` (kurum_paneli)

**Bileşenler**
- Modern kartlar, istatistikler, accordion alanları
- Logo yükleme, rehber sistemi toggle

**Bulgular**
- Inline CSS çok büyük; performans ve bakım açısından riskli.
- Ağır animasyonlar mobil performansı düşürebilir.

**Aksiyon**
- CSS’i `static/css` içine taşı, gereksiz animasyonları sadeleştir.
- Mobil için kritik kartları ayrı düzenle.

---

### 2.4 `http://127.0.0.1:5001/surec-paneli`
**Dosya:** `C:\SPY_Cursor\SP_Code\templates\surec_panel.html`  
**Route:** `C:\SPY_Cursor\SP_Code\main\routes.py` (surec_paneli)

**Bileşenler**
- Süreç listesi, süreç ekleme/düzenleme, faaliyetler
- Admin süreç yönetim butonları

**Bulgular**
- Sayfa, admin endpointlerini (create/update/delete) tüm rollerde çağırmaya çalışıyor.
- surec_lideri/surec_uyesi rolünde butonlar görünürse hata alacak.

**Aksiyon**
- Role göre buton/işlem görünürlüğünü kapat.
- Süreç CRUD’ı admin/kurum_yoneticisi/ust_yonetim rolleriyle sınırla.
- Güvenlik sadece UI’da buton gizleyerek sağlanamaz. Backend route’larında mutlaka `@role_required` veya benzeri dekoratörlerle sunucu taraflı yetki kontrolü yapılmalı (Security by Obscurity uyarısı).

---

### 2.5 `http://127.0.0.1:5001/surec-karnesi`
**Dosya:** `C:\SPY_Cursor\SP_Code\templates\surec_karnesi.html`  
**Route:** `C:\SPY_Cursor\SP_Code\main\routes.py` (surec_karnesi)  
**API:** `C:\SPY_Cursor\SP_Code\api\routes.py`

**Bileşenler**
- KPI/PG detayları, faaliyet planları, wizard, performans dağıtımı
- Çok sayıda API entegrasyonu

**Bulgular**
- `/api/pg-veri/sil/<id>` endpoint’i yok (UI çağırıyor).
- `/api/pg-veri/proje-gorevleri` endpoint’i yok (UI çağırıyor).
- `/debug/surec-data` debug endpoint’i prod akışında kullanılıyor.
- Çok büyük JS dosyası; performans ve bakım zorluğu.

**Aksiyon**
- Eksik endpointleri ekle veya UI’dan kaldır.
- Eksik endpointler eklenirken **veritabanı modelleri ve migrasyonlar kontrol edilmeli/oluşturulmalı**; UI form verisinin nereye kaydedileceği netleştirilmeli (Integration Hell riski).
- Debug endpointini prod akıştan çıkar.
- JS’yi modüllere ayır, kritik akışları sadeleştir.

---

### 2.6 `http://127.0.0.1:5001/performans-kartim`
**Dosya:** `C:\SPY_Cursor\SP_Code\templates\bireysel_panel.html`  
**Route:** `C:\SPY_Cursor\SP_Code\main\routes.py` (performans_kartim)

**Bileşenler**
- Kanban görünümü (Görevlerim)

**Bulgular**
- Sayfa adı/amacı performans kartı değil, görev kanbanı.
- `static/js/bireysel_panel.js` dosyası yok; kanban görevleri yüklenmez.

**Aksiyon**
- Performans kartı için gerçek KPI/PG ekranı oluştur veya rotayı “Görevlerim” olarak değiştir.
- Eksik JS dosyasını ekle veya kanban scriptini mevcut dosyalara taşı.

---

### 2.7 `http://127.0.0.1:5001/stratejik-planlama-akisi`
**Dosya:** `C:\SPY_Cursor\SP_Code\templates\stratejik_planlama_akisi.html`  
**Route:** `C:\SPY_Cursor\SP_Code\main\routes.py` (stratejik_planlama_akisi)

**Bileşenler**
- SWOT/PESTLE alanları, planlama akış kartları

**Bulgular**
- UI `/api/save-swot-analysis`, `/api/get-swot-analysis`, `/api/save-pestle-analysis`, `/api/get-pestle-analysis` çağırıyor fakat bu endpointler yok.
- Büyük inline CSS/JS blokları.

**Aksiyon**
- SWOT/PESTLE API’lerini ekle veya UI’dan kaldır.
- Eksik endpointler eklenirken **veritabanı modelleri ve migrasyonlar kontrol edilmeli/oluşturulmalı**; UI form verisinin nereye kaydedileceği netleştirilmeli (Integration Hell riski).
- CSS/JS’yi statik dosyalara taşı.

---

### 2.8 `http://127.0.0.1:5001/stratejik-asistan`
**Dosya:** `C:\SPY_Cursor\SP_Code\templates\stratejik_asistan.html`  
**Route:** `C:\SPY_Cursor\SP_Code\main\routes.py` (stratejik_asistan)

**Bileşenler**
- Kurum profil formu, AI öneri üretimi

**Bulgular**
- API çağrıları (`/api/kurum/{id}/stratejik-profil`, `/api/ai/stratejik-oneri`, `/api/ai/yeni-oneri`, `/api/ai/kabul-et`) kodda bulunmuyor.
- `Content-Tip` typo (Content-Type olmalı), istekler bozulur.
- Metinlerde encoding bozukluğu (ör. “yapay zekÇ¢”).

**Aksiyon**
- Eksik AI ve profil API’lerini ekle.
- Eksik endpointler eklenirken **veritabanı modelleri ve migrasyonlar kontrol edilmeli/oluşturulmalı**; UI form verisinin nereye kaydedileceği netleştirilmeli (Integration Hell riski).
- Header typo düzelt.
- Encoding sorunlarını gider (UTF-8 tutarlılığı).
- OpenAI/LLM API anahtarlarının `.env` dosyasında yönetildiğinin kontrolü.
- Eksik endpoint çağrılarında sistemin tepki politikasını belirlemek için 403/404/500 hata sayfaları ve yönlendirmeleri tasarla.

---

### 2.9 `http://127.0.0.1:5001/strategy/projects`
**Dosya:** `C:\SPY_Cursor\SP_Code\templates\strategy\project_portfolio.html`  
**Route:** `C:\SPY_Cursor\SP_Code\main\routes.py` (strategy_projects)

**Bileşenler**
- Proje portföy tablosu, edit/clone/delete modalları

**Bulgular**
- Rol bazlı erişim kısıtı yok; tüm roller erişebiliyor.

**Aksiyon**
- Portföyü sadece yönetim rolleri için aç veya görüntüle/editle ayrımı yap.
- Güvenlik sadece UI’da buton gizleyerek sağlanamaz. Backend route’larında mutlaka `@role_required` veya benzeri dekoratörlerle sunucu taraflı yetki kontrolü yapılmalı (Security by Obscurity uyarısı).

---

## 3) Benzeri sayfalar (menüden çıkan diğer modüller)
Bu modüller mevcut plan kapsamının dışında fakat menüde aktif oldukları için ikinci turda incelenmeli:

- `http://127.0.0.1:5001/dashboard/executive`
- `http://127.0.0.1:5001/projeler`, `.../projeler/<id>`, `.../projeler/<id>/gantt`, `.../projeler/<id>/kanban`
- `http://127.0.0.1:5001/gorev-aktivite-log`
- `http://127.0.0.1:5001/proje-analitik`
- `http://127.0.0.1:5001/muda-hunter`
- `http://127.0.0.1:5001/ai-chat`
- `http://127.0.0.1:5001/mtbp`, `.../gemba`, `.../competencies`, `.../risks`
- `http://127.0.0.1:5001/executive-report`
- `http://127.0.0.1:5001/crisis`, `.../succession`, `.../reorg`, `.../ona`
- `http://127.0.0.1:5001/market-watch`, `.../wellbeing`, `.../simulation`
- `http://127.0.0.1:5001/synthetic-lab`, `.../governance`, `.../metaverse`, `.../legacy-chat`
- `http://127.0.0.1:5001/game-theory`, `.../knowledge-graph`, `.../black-swan`, `.../library`
- `http://127.0.0.1:5001/yardim-merkezi`, `.../settings`, `.../zaman-takibi`

## 4) Genel teknik bulgular
- Örnek veri oluşturma sırasında `bireysel_performans_gostergesi.ad` zorunlu alan hatası alındı. Bu, Performans Kartı ve Süreç Karnesi ekranlarında veri boşluğu ve hata yaratır.
- Bazı modüller (Stratejik Asistan, Stratejik Planlama Akışı) API sözleşmesi olmadan UI düzeyinde hazırlanmış görünüyor.

## 5) Teknik Borç ve Refactoring
- Inline CSS ve JS blokları bakım maliyetini artırıyor ve performans sorunları doğuruyor.
- HTML içine gömülü JS kodlarının `static/js` klasörüne taşınması **P1/P2** öncelikli refactoring olarak ele alınmalı.
- Büyük JS dosyaları (ör. `surec_karnesi.html`) modüllere bölünmeli, kritik akışlar sadeleştirilmeli.

## 6) Önceliklendirme (Revize Edilmiş)
1. **P0 (Kritik Altyapı)**: Eksik Backend Endpointleri, DB Migrasyonları, Mock verilerin temizlenmesi.
2. **P1 (Güvenlik & Temizlik)**: Backend Role Kontrolleri, Inline JS/CSS Refactoring.
3. **P2 (Fonksiyonel UI)**: UI bileşenlerinin bağlanması.
