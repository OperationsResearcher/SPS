# Ocak 2026 Yapilacaklar - Tum Uygulama Planlama

## Kapsam ve hedefler (giris/kolay giris haric)
- Tum modullerde teknik kalite, guvenlik ve stabiliteyi artir
- Baslangictan uca fonksiyonel akislarin tutarliligini sagla
- UX'i rol ve baglama gore sade, hizli ve ogrenilebilir hale getir

## Uygulama kapsam haritasi (modul bazinda)
- Cekirdek: Dashboard, Bildirimler, Tema/Layout, Profil
- Strateji: Strateji Matrisi, KPI, Proje Portfoyu, Ust Yonetim ekranlari
- Surec: Surec Karnesi, surec performanslari, faaliyet akislari
- Proje/Gorev: Proje listesi, proje detay (kanban), Gantt, gorev formu, aktivite log
- Ileri moduller: Risk, MTBP, ONA, Simulation, Knowledge Graph, vb.
- PWA/Offline: Manifest, Service Worker, offline sayfalari

## Bulgular (ozet) - giris/kolay giris haric
### Mimari ve teknik borc
- Orta: `base.html` icinde cok fazla inline JS/CSS ve manuel dropdown yonetimi var; bakim ve cakisma riski.
- Orta: Tema/layout/bildirim mantigi tek kaynakta degil; global scriptler parca parca.
- Dusuk: PWA manifest linkinde `rel="manifest"` eksik; tarayici tanimasi zayif.

### Veri ve fonksiyonel tutarlilik
- Yuksek: Gorev status degerleri (EN/TR) karisik; kanban/raporlama ve filtreler tutarsiz calisabilir.
- Orta: Gantt ekraninda tarih/ilerleme degisimi kaydedilmiyor (sadece log).
- Orta: Proje bildirim ayarlari yeni projede var, duzenlemede yok; ayar yonetimi belirsiz.
- Orta: Moduller arasi secim/filtre davranislari farkli; kullanici mental modeli zorlasiyor.

### UX ve bilgi mimarisi
- Orta: Navigasyon cok kalabalik; rol bazli onceliklendirme eksik.
- Orta: Cok secimli alanlar (multi-select) mobil/uzaktan kullanimda zorlayici.
- Dusuk: Bildirim/tema/layout davranislarinda tutarsizlik algisi.

### Performans ve gozlemlenebilirlik
- Orta: JS/CSS butunluk ve cache stratejisi net degil; ilk yukleme degisken.
- Dusuk: Kritik akislarda metrik/log standardi yok (proje, gorev, bildirim).

## Ocak 2026 plan (onceliklendirilmis)
### 1) Kritik tutarlilik ve ana akislar (Hafta 1-2)
- Task status degerlerini tek standarda cek (TR veya EN) ve tum ekranlarda ayni seti kullan.
- Gantt update akisini API ile kaydet (tarih/ilerleme) ve UI geri bildirimi ekle.
- Broken link ve eksik route taramasi: proje/strateji/surec/gorev akislari.

### 2) Modul bazli UX sadelemesi (Hafta 3-4)
- Navigasyonu rol ve sikliga gore sadele (ana moduller vs ileri moduller).
- Multi-select yerine aramali/etiket secici kullan; mobil ve klavye akislarini netlestir.
- Formlarda alan yardimlari ve validasyon mesajlarini standarda bagla.

### 3) Teknik borc temizligi (Hafta 5-6)
- `base.html` icindeki inline JS/CSS parcalanip modullere ayrilsin.
- Tema/layout/bildirim scriptleri tek kaynaktan yonetilsin.
- PWA manifest ve service worker kaydi standartlastirilsin.

### 4) Uygulama geneli kalite ve performans (Hafta 7-8)
- Sayfa yukleme performansi icin bundle/caching kurallari belirle.
- Kritik moduller icin minimum log/telemetri standartlari ekle.
- Test kapsamini genislet: E2E (proje->task->kanban->gantt) ve API smoke testleri.

## Test ve dogrulama
- En az 2 E2E: proje olustur/duzenle, gorev ekle, kanban ve gantt akisi.
- Bildirim scheduler: geciken gorev ve deadline hatirlatma senaryolari.
- API smoke testleri: temel CRUD ve kritik endpointler.

## Basari metrikleri
- Gorev status tutarliligi: tum gorevler kanbanda gorunur
- Gantt degisiklik kaydetme basarisi: %95+ (log/telemetri ile)
- Broken link sayisi: 0
- Sayfa ilk yukleme suresi: %20+ iyilesme (kritik ekranlar)
