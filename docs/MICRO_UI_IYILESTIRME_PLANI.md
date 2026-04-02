# Micro Platform — UI/UX İyileştirme Planı

> Hedef: `micro/` yapısını kök uygulamanın görsel kalitesine çıkarmak.
> Kök dizin (`static/`, `templates/`) **kesinlikle kirletilmeyecek**.
> Tüm değişiklikler `ui/static/platform/` ve `ui/templates/platform/` altında kalır.

---

## Mevcut Durum Analizi

### Kök Uygulama (Referans Seviye)
- Bootstrap 5 + özel CSS (`custom.css`, `layout.css`, `kpi-cards-modern.css`)
- Sidebar + Navbar ikili navigasyon
- Vue.js ile interaktif KPI kartları
- Gradient progress bar'lar, hover animasyonları
- Profil fotoğrafı, logo, marka kimliği
- Responsive sidebar (mobilde drawer)

### Micro Yapısı (Mevcut Sorunlar)
- Sadece üst bar var, **sidebar yok** → en büyük görsel fark
- Tailwind utility class'ları ham kullanılmış, bileşen sistemi yok
- Kart tasarımları düz ve sade, shadow/gradient yok
- Tablolar stilsiz (`w-full text-sm` seviyesinde)
- Formlar modal içinde ham HTML
- Analiz sayfası `<pre>` tag ile JSON gösteriyor (kabul edilemez)
- Launcher sadece emoji + metin, görsel hiyerarşi yok
- Logo/marka kimliği yok
- Mobil deneyim eksik

---

## Tasarım Kararları

### Framework: Tailwind kalır, Bootstrap eklenmez
Tailwind + Alpine.js kombinasyonu micro'nun dark mode, modüler yapı ve
performans avantajlarını koruyor. Bootstrap eklemek çakışma yaratır.
Çözüm: Tailwind ile Bootstrap kalitesinde **özel bileşen kütüphanesi** oluşturmak.

### Yeni Dosya Yapısı (sadece micro/ altında)
```
ui/static/platform/
  css/
    app.css          ← mevcut, genişletilecek
    components.css   ← YENİ: kart, tablo, form, badge bileşenleri
    sidebar.css      ← YENİ: sidebar navigasyon
    animations.css   ← YENİ: geçiş animasyonları
    surec.css        ← mevcut, iyileştirilecek
    admin.css        ← mevcut, iyileştirilecek
  js/
    app.js           ← mevcut, sidebar toggle eklenecek
    (diğerleri korunur)
```

---

## Sprint Planı


### Sprint 1 — Temel Altyapı (base.html + Sidebar)
**Etki: Tüm sayfaları etkiler. En yüksek öncelik.**

**Dosyalar:**
- `ui/templates/platform/base.html` — sidebar navigasyon eklenir
- `ui/static/platform/css/sidebar.css` — YENİ
- `ui/static/platform/css/components.css` — YENİ
- `ui/static/platform/js/app.js` — sidebar toggle mantığı eklenir

**Yapılacaklar:**
1. `base.html`'e sol sidebar ekle
   - Modül listesi `module_registry`'den dinamik gelir
   - Aktif modül vurgulanır (`request.endpoint` ile)
   - Mobilde hamburger menü + overlay drawer
   - Kokpitim logosu + marka adı sidebar başında
2. Üst bar sadeleştirilir (sidebar varken tekrar nav gerekmez)
   - Sadece: hamburger (mobil), sayfa başlığı, bildirim zili, kullanıcı dropdown
3. `components.css` oluştur:
   - `.mc-card` — standart kart (shadow, border-radius, hover lift)
   - `.mc-table` — tablo stili (Bootstrap table benzeri)
   - `.mc-btn-primary`, `.mc-btn-secondary`, `.mc-btn-danger`
   - `.mc-badge-*` — durum badge'leri
   - `.mc-form-input` — form input stili
   - `.mc-stat-card` — istatistik kartı (büyük sayı + etiket)
4. Dark mode sidebar desteği

**Tahmini süre: 4-6 saat**

---

### Sprint 2 — Launcher & Masaüstü
**Dosyalar:**
- `ui/templates/platform/launcher.html`
- `ui/templates/platform/masaustu/index.html`

**Yapılacaklar:**
1. Launcher yeniden tasarımı:
   - Modül kartları: ikon (büyük, renkli arka plan), ad, kısa açıklama
   - Hover'da kart yükselir, renk tonu değişir
   - Rol bazlı erişilemeyen modüller gri/kilitli gösterilir
   - Karşılama mesajı + kullanıcı adı + tarih
2. Masaüstü yeniden tasarımı:
   - Üst satır: 4 istatistik kartı (`.mc-stat-card` ile)
   - KPI listesi: progress bar'lı, renk kodlu durum
   - Faaliyet listesi: tamamlanma yüzdesi görsel
   - Bildirim listesi: okunmamış badge

**Tahmini süre: 3-4 saat**

---

### Sprint 3 — Süreç Yönetimi
**Dosyalar:**
- `ui/templates/platform/surec/index.html`
- `ui/templates/platform/surec/karne.html`
- `ui/static/platform/css/surec.css`
- `ui/static/platform/js/surec.js`

**Yapılacaklar:**
1. Süreç listesi:
   - Hiyerarşik ağaç görünümü: indent + bağlantı çizgileri
   - Her kart: kod badge, ad, progress bar, KPI sayısı, lider avatarı
   - Hover'da işlem butonları görünür (Bootstrap'teki gibi)
   - Boş durum: illüstrasyon + CTA butonu
2. Karne sayfası:
   - Yıl seçici: tab veya dropdown
   - KPI kartları: gerçekleşen/hedef/sapma üçlüsü, renk kodlu
   - Aylık faaliyet takip tablosu: checkbox grid (12 ay × N faaliyet)
   - Grafik alanı: Chart.js ile trend çizgisi (mevcut `<pre>` yerine)
3. Süreç ekleme/düzenleme modal'ı: çok adımlı form (temel bilgi → lider/üye → alt strateji)

**Tahmini süre: 5-6 saat**

---

### Sprint 4 — Stratejik Planlama
**Dosyalar:**
- `ui/templates/platform/sp/index.html`
- `ui/templates/platform/sp/flow.html`
- `ui/templates/platform/sp/dynamic_flow.html`
- `ui/static/platform/js/sp.js`

**Yapılacaklar:**
1. SP ana sayfa:
   - Vizyon/misyon kutusu: gradient arka plan, büyük font
   - SWOT sayaçları: 4 renkli kart (yeşil/kırmızı/mavi/sarı)
   - Strateji listesi: accordion tarzı, alt stratejiler içinde
   - Strateji ekleme: inline form veya slide-over panel
2. Flow sayfası:
   - Vizyon → Strateji → Alt Strateji → Süreç → KPI hiyerarşisi
   - Her seviye farklı renk ve ikon
3. Dynamic flow:
   - Mevcut node-edge yapısı korunur, görsel iyileştirme

**Tahmini süre: 4-5 saat**

---

### Sprint 5 — Admin Modülü
**Dosyalar:**
- `ui/templates/platform/admin/users.html`
- `ui/templates/platform/admin/tenants.html`
- `ui/templates/platform/admin/packages.html`
- `ui/static/platform/css/admin.css`
- `ui/static/platform/js/admin.js`

**Yapılacaklar:**
1. Kullanıcı tablosu:
   - Avatar (baş harf + renk), ad, email, rol badge, kurum, durum toggle
   - Arama/filtreleme input'u (JS ile anlık filtre)
   - Sayfalama (client-side, 20'şer)
2. Kurum tablosu:
   - Paket badge'i, kullanıcı sayısı, durum
3. Paket yönetimi:
   - Kart görünümü: paket adı, modül listesi, tenant sayısı
4. Tüm tablolarda: sıralama başlıkları, boş durum mesajı

**Tahmini süre: 4-5 saat**

---

### Sprint 6 — Kurum & Bireysel Performans
**Dosyalar:**
- `ui/templates/platform/kurum/index.html`
- `ui/templates/platform/bireysel/karne.html`
- `ui/static/platform/js/kurum.js`
- `ui/static/platform/js/bireysel.js`

**Yapılacaklar:**
1. Kurum paneli:
   - Üst: logo alanı, kurum adı, paket bilgisi
   - İstatistik kartları: kullanıcı sayısı, aktif süreç, PG sayısı
   - Stratejik kimlik formu: vizyon, misyon, değerler — inline edit
   - Strateji ağacı: kurum modülündeki strateji listesi
2. Bireysel karne:
   - Süreç karnesiyle aynı kalite: KPI kartları + aylık takip grid
   - Favori PG toggle (yıldız ikonu)
   - Faaliyet ekleme: inline form

**Tahmini süre: 4-5 saat**

---

### Sprint 7 — Analiz Merkezi
**Dosyalar:**
- `ui/templates/platform/analiz/index.html`
- `ui/static/platform/js/analiz.js`

**Yapılacaklar:**
1. `<pre>` JSON gösterimi tamamen kaldırılır
2. Trend analizi: Chart.js çizgi grafiği
3. Sağlık skoru: dairesel gauge veya büyük sayı + renk
4. Tahmin: noktalı çizgi (gerçek vs tahmin)
5. Anomali listesi: tablo + kırmızı vurgu
6. Karşılaştırma: çoklu süreç seçici + bar grafik
7. Excel indirme butonu: belirgin, yeşil

**Tahmini süre: 5-6 saat**

---

### Sprint 8 — HGS, Auth, Bildirim, Ayarlar
**Dosyalar:**
- `ui/templates/platform/hgs/index.html`
- `ui/templates/platform/auth/login.html`
- `ui/templates/platform/auth/profil.html`
- `ui/templates/platform/auth/ayarlar.html`
- `ui/templates/platform/bildirim/index.html`
- `ui/templates/platform/ayarlar/index.html`

**Yapılacaklar:**
1. HGS: kullanıcı kartları grid görünümü, avatar, rol rengi
2. Login: merkezi kart, logo, gradient arka plan
3. Profil: fotoğraf yükleme alanı, bilgi kartları
4. Bildirim: okunmuş/okunmamış ayrımı, tip ikonları
5. Ayarlar: sekme (tab) yapısı

**Tahmini süre: 3-4 saat**

---

### Sprint 9 — API Docs & Hata Sayfaları
**Dosyalar:**
- `ui/templates/platform/api/docs.html`
- `ui/templates/platform/errors/403.html`

**Yapılacaklar:**
1. API docs: Swagger benzeri tablo (method badge renkli, URL, açıklama)
2. 403 sayfası: illüstrasyon + geri dön butonu

**Tahmini süre: 1-2 saat**

---

## Özet Tablo

| Sprint | Kapsam | Süre | Öncelik |
|--------|--------|------|---------|
| 1 | base.html + Sidebar + Bileşen Kütüphanesi | 4-6 saat | KRİTİK |
| 2 | Launcher + Masaüstü | 3-4 saat | Yüksek |
| 3 | Süreç Yönetimi | 5-6 saat | Yüksek |
| 4 | Stratejik Planlama | 4-5 saat | Yüksek |
| 5 | Admin Modülü | 4-5 saat | Orta |
| 6 | Kurum + Bireysel | 4-5 saat | Orta |
| 7 | Analiz Merkezi | 5-6 saat | Orta |
| 8 | HGS + Auth + Bildirim | 3-4 saat | Düşük |
| 9 | API Docs + Hata Sayfaları | 1-2 saat | Düşük |
| **Toplam** | | **~34-43 saat** | |

---

## Kurallar (Değişmez)

- Kök `static/` ve `templates/` dizinlerine **hiçbir dosya eklenmez**
- Tüm CSS: `ui/static/platform/css/` altında
- Tüm JS: `ui/static/platform/js/` altında
- HTML içinde `<script>` veya `<style>` bloğu yasak
- JS dosyalarında `{{ }}` Jinja2 ifadesi yasak, `data-*` kullanılır
- SweetAlert2 zorunlu, `alert()`/`confirm()` yasak
- Dark mode desteği her bileşende korunur

---

## Başlangıç Noktası

Sprint 1 (base.html + sidebar) tüm diğer sprintlerin temelini oluşturur.
Sidebar olmadan diğer sayfaları iyileştirmek anlamsız — önce bu yapılmalı.

Onay verirsen Sprint 1 ile başlayabiliriz.
