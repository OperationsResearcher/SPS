# Kokpitim Yetenekler Raporu

Bu dokuman, Kokpitim'in mevcut teknik kabiliyetlerini "veri nasil tutuluyor, nasil isleniyor, nasil gosteriliyor ve nasil raporlaniyor" perspektifinden ozetlemek icin hazirlandi.

Kapsam notu:
- Bu rapor, kurum geneli kabiliyetleri ve analiz altyapisini odak alir.
- Proje modulundeki analiz merkezi yapilari bu raporun disindadir.

## 1) Platformun Temel Kabiliyeti

Kokpitim, cok kiracili (tenant tabanli) bir kurumsal performans yonetim platformudur. Temel olarak su yetenekleri saglar:
- Kurum, kullanici ve rol yonetimi
- Strateji -> alt strateji -> surec -> KPI -> veri girisi zinciri
- Surec faaliyetleri, atamalar, hatirlatmalar ve otomatik isleme
- Gorev ve proje yonetimi (analiz haric)
- Uygulama ici + e-posta bildirimleri
- Analitik, karsilastirma, tahminleme, anomali tespiti
- Rapor olusturma ve Excel disa aktarma

## 2) Veri Nasil Tutuluyor?

### 2.1 Cok kiracili veri modeli
- Ana kurgu `tenants`, `users`, `roles` ile tenant izolasyonu uzerine kurulu.
- Modullerde veriler agirlikla `tenant_id` ve/veya `kurum_id` ile ayriliyor.
- Kullanici bazli ayarlar JSON alanlarinda saklanabiliyor (`notification_preferences`, `theme_preferences` vb.).

### 2.2 Cekirdek is varliklari
- Kurum/kimlik verileri: tenant, rol, kullanici
- Strateji verileri: `strategies`, `sub_strategies`
- Surec verileri: `processes`, `process_members`, `process_leaders`, `process_owners_table`
- KPI verileri: `process_kpis`, `kpi_data`
- Faaliyet verileri: `process_activities`, `process_activity_assignees`, `process_activity_reminders`, `activity_tracks`
- Bildirim verileri: `notifications`
- Kurum analiz verileri: `analysis_item` (SWOT/PESTLE), `tows_matrix`

### 2.3 Iliski modeli
- Coktan coga iliskiler yaygin: surec-kullanici, surec-alt strateji, faaliyet-kullanici vb.
- Cogu tabloda `is_active` veya soft-delete mantigi bulunuyor.
- Tarih/zaman alanlari (or. `start_at`, `end_at`, `created_at`) is akislarini zaman bazli izlemeye uygun.

## 3) Veri Nasil Isleniyor?

### 3.1 Is kurali ve servis katmani
- Analitik hesaplar servis katmaninda merkezi yurutuluyor:
  - `AnalyticsService`: trend, saglik skoru, karsilastirma, tahminleme
  - `ReportService`: performans raporu, dashboard ozeti, custom rapor
  - `AnomalyService`: z-score / IQR / hareketli ortalama ile anomali tespiti
- Uygulama ici bildirim olusturma + socket push merkezi:
  - `micro/services/notification_triggers.py`
- E-posta gonderim mantigi merkezi:
  - `micro/services/email_service.py`

### 3.2 Olay tabanli akislar
- Surece atama, KPI degisimi, faaliyet ekleme -> ilgili kullanicilara bildirim tetikleniyor.
- Gorev atama ve durum degisimi -> proje kanallari + tenant tercihleri dogrultusunda bildirim gidiyor.
- Faaliyet hatirlatma ve oto-tamamlama -> zamanlanmis kontrol ile calisiyor.

### 3.3 Asenkron ve zamanlanmis isleme
- Celery task seti mevcut:
  - gunluk/haftalik/aylik rapor uretimi
  - KPI anomali izleme
- Redis tabanli broker/backend kullanimi destekleniyor.

## 4) Veri Nasil Gosteriliyor?

### 4.1 Moduler ekran kurgusu (Micro)
- Modul kayit sistemi (`micro/core/module_registry.py`) ile ekranlar rol/paket bazli aciliyor.
- Ana moduller: Masaustum, SP, Surec, Kurum, Bireysel, Proje, Analiz, Bildirim, Ayarlar, Admin.

### 4.2 On yuzde gosterim bicimi
- Flask + Jinja tabanli server-side render agirlikli yapi.
- API destekli dinamik ekranlar mevcut (ozellikle analiz ve bildirim tarafi).
- Dashboard mantigi:
  - Kisiye ozel ozet (masaustu)
  - Surec/KPI durumu
  - Okunmamis bildirim rozetleri

### 4.3 Bildirimlerin gosterimi
- `Notification` kayitlari bildirim merkezinde listeleniyor.
- Okundu/okunmadi durumu API ile yonetiliyor.
- WebSocket ile anlik "new_notification" push kabiliyeti mevcut.

## 5) Veri Nasil Raporlaniyor?

### 5.1 Operasyonel raporlar
- Surec bazli performans raporu:
  - ozet skor
  - KPI detaylari
  - trendler
  - oneriler
- Dashboard ozet raporu:
  - toplam surec/KPI
  - ortalama performans
  - en iyi ve dikkat gerektiren alanlar

### 5.2 Cikti formatlari
- JSON: API/ekran entegrasyonu icin
- Excel: disa aktarim (pandas + openpyxl)
- PDF: su an placeholder durumunda

### 5.3 Otomatik raporlama
- Gunluk, haftalik, aylik rapor uretimi senaryolari var.
- Servis katmaninda rapor govdesi uretimi tamam; bazi email dagitim adimlari "placeholder" notuyla gelistirilebilir.

## 6) Kurum Analiz Merkezi Icin Hazir Yetenekler

Kurum Analiz Merkezi insasinda dogrudan kullanilabilir guclu parcalar:
- Tenant bazli veri izolasyonu (kurumlar arasi guvenli ayrim)
- Hazir analiz endpointleri (`/analiz` ve ilgili API'ler)
- Trend/saglik/forecast/comparison/anomaly hesap motorlari
- Rapor olusturma + Excel export
- Bildirim tetikleme altyapisi (in-app + email)
- Rol/paket bazli modul erisimi

## 7) Bosluklar ve Dikkat Noktalari

Yeni analiz merkezi tasariminda asagidaki noktalar netlestirilmeli:
- "Tek dogru analiz hatti" standardi: paralel/legacy analiz akislarinin sade lestirilmesi
- PDF export gercek implementasyonu
- Otomatik rapor dagitiminda (mail) placeholder kisimlarin tam urunlestirilmesi
- API/servis imza tutarliligi (tarih parametresi tipleri, method imzalari)
- Gozlemlenebilirlik: kritik analiz endpointleri icin standart metrik/log paneli

## 8) Onerilen Insa Stratejisi (Analiz Merkezi)

1. Kurum analizleri icin tek bilgi mimarisi ve tek route ailesi belirlenmeli.
2. Veri sozlugu cikartilmali:
   - analiz tipi
   - metrik
   - hesaplama metodu
   - kaynak tablo/alan
3. Analiz API katmani bir "facade service" altinda toplanmali.
4. UI tarafinda kart bazli bir bilgi mimarisi uygulanmali:
   - Ozet
   - Trend
   - Tahmin
   - Karsilastirma
   - Anomali
   - Raporlar
5. Bildirim ve rapor dagitim kurallari kurum bazli yonetilebilir hale getirilmeli.

## 9) Sonuc

Kokpitim'in mevcut yapisi, yeni bir Kurum Analiz Merkezi kurmak icin guclu bir temel sunuyor:
- Veri modeli olgun
- Isleme servisleri zengin
- Gosterim ve bildirim kanallari hazir
- Raporlama motoru kullanilabilir durumda

En buyuk kazanimi saglayacak adim, mevcut kabiliyetleri tek bir kurumsal analiz hattinda sade ve tutarli bir sekilde birlestirmektir.
