# Kokpitim — Ürün İyileştirme Planı
> Hazırlanma: 2026-05-19 | Claude Code ürün analizi
> Kaynak: Kod tabanı incelemesi + EPM literatürü karşılaştırması

---

## Konumlandırma

Kokpitim, **EPM (Enterprise Performance Management)** kategorisinde; daha spesifik olarak **BSC yazılımı** ile **entegre süreç yönetimi** kesişim noktasında duran bir platformdur.

Piyasa muadilleri: Corporater, Spider Impact, Cascade, Quantive, SAP Strategy Management.  
**Rekabet avantajı:** Türk kamu/özel kurumlarının süreç kültürüne uygun arayüz ve erişilebilir fiyat.  
**Mevcut zayıflık:** Sistem şu an *veri toplama aracı* gibi çalışıyor; *karar destek aracı* olması hedeflenmeli.

---

## Bölüm 1 — Yeni Özellikler

### Ö-1 · Strateji Haritası (Strategy Map) Görselleştirmesi
**Öncelik:** 🔴 Kritik  
**Efor:** ~3 hafta

**Sorun:** Strateji → Alt Strateji → Süreç → KPI bağlantısı veride mevcut ancak kullanıcı bu hiyerarşiyi görsel olarak göremıyor. Sistem "veri deposu" olarak algılanıyor.

**Çözüm:** İnteraktif ağaç/diagram ekranı.
- Düğüme tıklayınca ilgili KPI'lar ve skor açılır
- Renk kodu: yeşil/sarı/kırmızı (hedef durumuna göre)
- SP modülüne yeni bir sayfa olarak eklenir

**Teknik not:** Veri zaten `Strategy → SubStrategy → Process → ProcessKpi` zincirinde mevcut. Frontend için D3.js veya vis.js yeterli.

---

### Ö-2 · Excel/CSV Toplu KPI Veri Girişi
**Öncelik:** 🔴 Kritik  
**Efor:** ~1 hafta

**Sorun:** Aylık raporlama döneminde onlarca KPI'a tek tek tıklayarak veri girmek pratik değil. Bu en sık duyulan kullanıcı şikâyeti.

**Çözüm:** Şablon indir → doldur → yükle akışı.
- Tenant'ın aktif KPI listesini Excel şablonu olarak indir
- Doldurulmuş dosyayı yükle → satırları doğrula → toplu kaydet
- Hatalı satırlar işaretli olarak geri döner

**Teknik not:** `openpyxl` zaten kurulu (karne export'ta kullanılıyor). `surec/routes_kpi_data.py`'ye yeni bir `/process/api/kpi-data/bulk-import` endpoint'i yeterli.

---

### Ö-3 · Otomatik Erken Uyarı Tetikleyicisi
**Öncelik:** 🟠 Yüksek  
**Efor:** ~1 hafta

**Sorun:** `services/ai_early_warning.py` mevcut ancak tetikleyici mekanizma yok. KPI kötüleşiyor, kimse haberdar olmuyor.

**Çözüm:** Zamanlanmış iş + bildirim entegrasyonu.
- Her gece çalışan bir görev: hedefin %80 altındaki ve son 3 ayda düşüş trendindeki KPI'ları tespit et
- Süreç sorumlusuna bildirim, yöneticiye özet
- `services/background_tasks.py` içine görev eklenir, mevcut bildirim altyapısı kullanılır

**Teknik not:** Bildirim altyapısı (`notification_service.py`, `push_notification_service.py`) hazır. Eksik olan sadece iş mantığı ve zamanlayıcı kaydı.

---

### Ö-4 · Dönemsel Karşılaştırma Raporu (PDF/Excel Export)
**Öncelik:** 🟠 Yüksek  
**Efor:** ~2 hafta

**Sorun:** `services/report_service.py` içinde TODO olarak açık. Kurumlar "geçen yıla göre ne kadar iyileştik?" sorusunu PDF olarak yönetime sunmak istiyor.

**Çözüm:** Yönetim raporu üreteci.
- Yıl seç → rapor türü seç (KPI özeti / süreç performansı / proje durumu)
- PDF veya Excel olarak indir
- Kurum logosu ve dönem başlığı otomatik eklenir

**Teknik not:** `reportlab` (PDF) veya `openpyxl` (Excel). Plan Year sistemi sayesinde yıl bazlı veri karşılaştırması için altyapı hazır.

---

### Ö-5 · Birey → Süreç → Strateji Hizalama Skoru
**Öncelik:** 🟡 Orta  
**Efor:** ~2 hafta

**Sorun:** Bireysel performans, süreç ve strateji modülleri ayrı çalışıyor. Aralarındaki hizalama yüzdesi hesaplanmıyor.

**Çözüm:** Hizalama paneli.
- "Bu kişinin hedefleri kurumun stratejik hedeflerine ne kadar katkı yapıyor?" skoru
- Kullanıcı profilinde rozet/yüzde gösterimi
- Yönetici için ekip hizalama tablosu

**Teknik not:** `IndividualPerformanceIndicator.source_process_kpi_id` → `ProcessKpi.sub_strategy_id` → `SubStrategy.strategy_id` zinciri zaten mevcut. Hesaplama servisi yazılması yeterli.

---

### Ö-6 · Yönetici Sabah Özeti Ekranı
**Öncelik:** 🔴 Kritik  
**Efor:** ~2 hafta

**Sorun:** `services/ai_executive_summary.py` mevcut ancak masaüstü modülüne entegre edilmemiş. Yönetici sistemi açtığında "bugün ne yapmalıyım?" sorusuna hızlı cevap bulamıyor.

**Çözüm:** Masaüstü ana ekranına "Yönetici Özeti" widget'ı.
- Kötüye giden KPI sayısı (kırmızı)
- Geciken proje sayısı
- Bu hafta vadesi dolan faaliyetler
- Harekete geçilmesi önerilen 3 öncelik (AI destekli)
- Tek sayfada, tıklanabilir kartlar

**Teknik not:** `masaustu/routes.py` iskeleti mevcut. `ai_executive_summary.py` servisi çağrılıp kart formatında sunulması yeterli.

---

## Bölüm 2 — Mevcut Özelliklerde Değişiklikler

### D-1 · K-Radar Ağırlıkları Konfigüre Edilebilir Olmalı
**Öncelik:** 🟠 Yüksek

**Sorun:** KS×2, KP×3, KPR×3, Bireysel×2 ağırlıkları `k_radar_service.py` içinde sabit kodlanmış. Her kurumun önceliği farklı.

**Çözüm:** Tenant admin ekranına "K-Radar Ağırlıkları" ayar bölümü ekle. Değerler `SystemSettings` tablosunda saklanır, servis oradan okur.

---

### D-2 · Plan Yılı Geçişi Sihirbaza İndirgenmeli
**Öncelik:** 🟡 Orta

**Sorun:** Yıl sonu geçişi teknik olarak çalışıyor ancak kullanıcı ne olduğunu anlamıyor. Süreç karmaşık görünüyor.

**Çözüm:** "Yeni Yıla Geç" adlı 3 adımlı sihirbaz:
1. Yeni yılı onayla
2. Hangi KPI'ları taşımak istiyorsun? (hepsini / seçilenleri)
3. Tamamlandı — özet göster

---

### D-3 · KPI Başarı Puanı Hesabı Şeffaf Olmalı
**Öncelik:** 🟡 Orta

**Sorun:** Kullanıcı puanı görüyor ancak nasıl hesaplandığını göremıyor. Güvensizlik yaratıyor.

**Çözüm:** Her KPI kartında "Nasıl hesaplandı?" bağlantısı. Tıklayınca: aralıklar, yöntem (artan/azalan), gerçekleşen değer, puan formülü gösterilir.

---

### D-4 · Masaüstü Gerçek Zamanlı Güncellenebilmeli
**Öncelik:** 🟡 Orta

**Sorun:** `flask_socketio` kurulu ve başlatılıyor ancak masaüstü verileri sayfa yenilemeden güncellenmiyor.

**Çözüm:** KPI veri girişinde ilgili masaüstü widget'ına WebSocket ile anlık güncelleme. Özellikle "bugünkü veri girişi tamamlandı" bildirimi.

---

## Bölüm 3 — Uygulama Sırası

| Sıra | İş | Efor | Neden Önce |
|------|---|------|------------|
| 1 | Ö-6 Yönetici sabah özeti | 2 hafta | Altyapı hazır, görünür etki en yüksek |
| 2 | Ö-2 Toplu KPI veri girişi | 1 hafta | En sık kullanıcı şikâyeti |
| 3 | Ö-3 Erken uyarı tetikleyicisi | 1 hafta | Altyapı hazır, iş mantığı eksik |
| 4 | D-1 K-Radar ağırlık ayarı | 3 gün | Teknik borç, kolay |
| 5 | Ö-4 Dönemsel rapor PDF/Excel | 2 hafta | Satış etkisi yüksek |
| 6 | Ö-1 Strateji haritası | 3 hafta | Görsel etki büyük, efor yüksek |
| 7 | Ö-5 Hizalama skoru | 2 hafta | Tamamlayıcı özellik |
| 8 | D-2 Plan yılı sihirbazı | 1 hafta | UX iyileştirme |
| 9 | D-3 KPI puan şeffaflığı | 3 gün | Güven artırıcı |
| 10 | D-4 WebSocket masaüstü | 2 hafta | Olgun altyapı gerekir |

---

## Uzun Vadeli Vizyon

Kokpitim'in 2027 hedefi: kurumun sabahları açtığı, **ne yapacağını söyleyen** bir platform olmak.

Bunun için kritik yol:
```
Veri toplama (✅ mevcut)
    → Görselleştirme (Ö-1, Ö-6)
        → Erken uyarı (Ö-3)
            → Karar desteği (AI entegrasyonu)
                → Aksiyon takibi (mevcut + Ö-5)
```

Rakiplerden ayrışma noktası: Türk kamu ihale mevzuatı, KYS (ISO 9001) süreç yapısı ve Balanced Scorecard'ı **tek platformda** çalıştırabilmek. Bu üçü bir arada başka bir yerde yok.
