# Proje Yönetimi Yol Haritası – İşaretlenebilir Checklist

Bu dosya, proje yönetimi modülünü geliştirme çalışmalarını adım adım takip etmek için hazırlanmıştır. Aşağıdaki maddeleri tamamlandıkça işaretleyin.

- Durum sembolleri: [ ] Yapılacak · [x] Tamamlandı · [~] Devam ediyor
- Not eklemek için alt satırlara "Not:" ile açıklama yazabilirsiniz.

---

## Sprint Paketleri (Hızlı Kazanımlar)
- [~] Sprint 1: Kanban + Takvim (FullCalendar) MVP
  - [x] Kanban panosu (sürükle-bırak, WIP limitleri)
  - [x] FullCalendar entegrasyonu (hafta/ay/görev görünümü)
  - [x] Kanban ↔ Takvim çift yönlü sürükle-bırak
  - [x] Toast geri bildirim ve hatalar için güvenli fallback
- [~] Sprint 2: Gantt + Görev Bağımlılıkları + Kritik Yol
  - [x] Gantt bileşeni (Frappe Gantt veya eşdeğeri – lisans uygunluğu gözet)
  - [x] Bağımlılık veri modeli ve API (predecessors)
  - [x] Bağımlılık tipleri (FS/SS/FF/SF) ve lag/süre destekleri
  - [x] CPM hesaplamaları (ES/EF, LS/LF, Slack)
  - [x] Kritik yol vurgusu ve zoom
- [~] Sprint 3: EVM + Burnup/Burndown
  - [x] EVM metrikleri (PV/EV/AC, SPI, CPI)
  - [x] Sprint Burnup/Burndown grafikleri
  - [ ] Varyans raporları ve trend çizgileri
- [x] Sprint 4: Entegrasyonlar (Outlook/Teams/Slack) + Digest
  - [x] iCal export/import
  - [x] Outlook/Teams/Slack bildirimleri (webhook kayıtları)
  - [x] Haftalık e-posta digest (özet ve aksiyon listesi)
- [x] Sprint 5: Kural Motoru v1 + SLA
  - [x] Deadline ve bağımlılık tabanlı uyarılar (kural motoru tetikleyicisi)
  - [x] İş tipi bazlı SLA tanımları ve ihlal uyarıları
  - [x] Tekrarlayan görevler (periyodik spawn)

---

## Çekirdek PM Özellikleri
- [x] Görev bağımlılık veri modeli (FS/SS/FF/SF, lag)
- [x] Zamanlama hesapları (ES/EF/LS/LF, Slack)
- [x] Kritik yol hesaplama ve görselleştirme
- [x] Baseline alanları (planlanan/gerçekleşen tarih/effort)
- [ ] Baseline raporları (varyans, trend)
- [x] Kaynak kapasite planlama ve yük haritası (kapasite API)
- [ ] Durum akışları (konfigüre edilebilir state machine)
- [x] Çalışma günü takvimi ve resmi tatiller

## Görsel ve UX
- [x] Gantt entegrasyonu ve bağımlılık çizgileri
- [ ] Baseline overlay ve zoom
- [x] Kanban (sürükle-bırak, WIP limitleri, hızlı işlem menüleri)
- [x] FullCalendar görünümü (hafta/ay/görev)
- [ ] Erişilebilirlik (ARIA, klavye kısayolları, yüksek kontrast)

## Analitik ve Portföy
- [x] EVM metrikleri (PV/EV/AC, SPI, CPI)
- [x] Burnup/Burndown ve hız grafikleri
- [x] Gecikme risk skoru (basit regresyon)
- [x] Portföy çok-proje görünümü
- [x] Çapraz bağımlılık matrisi
- [x] RAID kayıtları (Risk, Assumption, Issue, Dependency)

## Entegrasyonlar
- [x] iCal export/import
- [x] Outlook/Teams/Slack webhook/connector
- [ ] OneDrive/SharePoint/Google Drive dosya ekleri
- [ ] GitHub/Azure DevOps linkleme
- [x] E-posta digest’leri

## Otomasyon ve Kurallar
- [x] Kural motoru v1 (tetikleyiciler + koşullar + eylemler)
- [x] SLA tanımları ve ihlal uyarıları
- [x] Tekrarlayan görevler

## Güvenlik ve Uyumluluk
- [ ] RBAC derinleştirme (alan düzeyi izinler)
- [ ] Audit log’lar (CRUD, login, ayar değişiklikleri)
- [ ] PII maskeleme ve veri koruma
- [ ] Onay akışları (iki aşamalı onay)

## Performans ve Operasyon
- [ ] DB indeksleri ve sorgu plan analizi
- [ ] N+1 taraması ve ORM optimizasyonu
- [ ] Sayfalama ve cache stratejisi
- [ ] Background job queue (hatırlatmalar, digest, skorlar)

## Dokümantasyon ve Süreç
- [ ] Proje charter/teslimat/kabul kriterleri şablonları
- [ ] Onboarding turu, tooltip’ler ve ilk görev sihirbazı
- [ ] Kalite standartları (Definition of Done, review checklist)
- [ ] Test seti (RBAC entegrasyon ve kritik E2E akışlar)

---

## İzleme ve Notlar
- [ ] Toplam ilerleme: (manuel) Tamamlanan / Toplam madde
- [ ] Engeller ve bağımlılıklar: 
- [ ] Kararlar ve tarihçesi: 

> İşaretleme ipucu: Bir maddeyi tamamladığınızda `[ ]` → `[x]` yapın; devam eden işler için `~` işaretini not düşebilirsiniz.
