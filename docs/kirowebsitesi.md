# Kokpitim Tanıtım Sitesi — Kiro Geliştirme Dokümanı

> Bu dosya Kiro'ya doğrudan verilir. Analiz, tasarım kararları ve teknik uygulama talimatlarını tek belgede içerir.
> Hazırlayan: Claude | Güncelleme: 2026-05-04

---

## BÖLÜM 0 — ÖNCE OKU, SONRA KOD YAZ

### 0.1 Projenin Bağlamı

Kokpitim, Türkiye pazarına özel çok kiracılı (multi-tenant) bir SaaS uygulamasıdır. Stack: Python 3.11, Flask, SQLite, Docker, GCP VM.

**Mevcut durum:** `kokpitim.com/login` → doğrudan platform login sayfasına gidiyor. Tanıtım sitesi yok.

**Hedef:** `kokpitim.com/` → yeni tanıtım sitesi. Sağ üstteki "Giriş Yap" butonu → `kokpitim.com/login` (bu URL değişmeyecek, hiçbir şeye dokunulmayacak).

### 0.2 Altın Kural

**Mevcut hiçbir route, template veya dosya silinmeyecek, değiştirilmeyecek.**

Yapılacak tek şey: yeni `marketing_bp` Blueprint eklenmesi ve `/` route'unun bu blueprint'e devredilmesi.

### 0.3 Kodlamaya Başlamadan Önce Yapılacak

1. Mevcut `__init__.py`'yi (kök, `create_app` fonksiyonu) oku
2. `/` route'unun hangi blueprint'te tanımlı olduğunu bul
3. `main_bp`, `auth_bp` veya başka bir blueprint'te `/` varsa çakışma nasıl çözülecek — bunu söyle
4. Onay al, sonra kodlamaya başla

---

## BÖLÜM 1 — STRATEJİ (Neden Bu Site, Ne Anlatmalı)

Kokpitim'in rakiplerinden (Cascade Strategy, ClearPoint, Monday.com, Power BI) tek farkı:

> Strateji → Süreç → KPI → Bireysel Performans zincirini **tek platformda**, **Türkçe** kuran tek yazılım.

Rakipler bu adımları ayrı modüllerde, bazen ayrı yazılımlarda çözüyor. Sitenin her sayfası bu tek mesajı farklı açılardan anlatacak.

**Fiyat yok, müşteri yorumu yok** — hazır olmadan eklenirse güven zedeler. Tüm dönüşüm "Demo Talep" üzerinden.

---

## BÖLÜM 2 — MİMARİ VE TEKNİK YAPI

### 2.1 Blueprint Yapısı

```
marketing_bp
├── prefix: YOK (/ den çalışacak)
├── Dosya konumu: micro/modules/marketing/ (mevcut micro yapısına uygun)
│   ├── __init__.py
│   └── routes.py
├── Templates: templates/marketing/
│   ├── base.html          ← marketing'e özel base (micro/base.html'e BAĞIMLI DEĞİL)
│   ├── index.html
│   ├── ozellikler/
│   │   ├── index.html
│   │   ├── stratejik_planlama.html
│   │   ├── surec_yonetimi.html
│   │   ├── performans_takibi.html
│   │   ├── proje_yonetimi.html
│   │   └── analiz_merkezi.html
│   ├── nasil_calisir.html
│   ├── demo_talep.html
│   ├── blog/
│   │   ├── index.html
│   │   └── post.html
│   └── iletisim.html
└── Static: static/marketing/
    ├── css/marketing.css
    └── js/marketing.js
```

### 2.2 Route Tablosu

| URL | Metot | Fonksiyon | Açıklama |
|-----|-------|-----------|----------|
| `/` | GET | `index` | Ana sayfa |
| `/ozellikler` | GET | `ozellikler` | Özellikler genel |
| `/ozellikler/stratejik-planlama` | GET | `stratejik_planlama` | SP sayfası |
| `/ozellikler/surec-yonetimi` | GET | `surec_yonetimi` | Süreç sayfası |
| `/ozellikler/performans-takibi` | GET | `performans_takibi` | KPI sayfası |
| `/ozellikler/proje-yonetimi` | GET | `proje_yonetimi` | Proje sayfası |
| `/ozellikler/analiz-merkezi` | GET | `analiz_merkezi` | K-Radar + K-Rapor |
| `/nasil-calisir` | GET | `nasil_calisir` | Demo & tur |
| `/demo-talep` | GET, POST | `demo_talep` | Form sayfası |
| `/blog` | GET | `blog_index` | Blog listesi |
| `/blog/<slug>` | GET | `blog_post` | Blog yazısı |
| `/iletisim` | GET, POST | `iletisim` | İletişim formu |

### 2.3 Blueprint Kaydı

`__init__.py` içindeki `create_app()` fonksiyonuna eklenecek (diğer blueprint kayıtlarının SONUNA):

```python
from micro.modules.marketing import marketing_bp
app.register_blueprint(marketing_bp)
```

**Önemli:** Mevcut `/` route'u ile çakışma varsa marketing_bp en sona register edilmeli VEYA mevcut `/` route'u incelenerek çözüm belirlenmeli.

### 2.4 Teknik Kurallar

- `micro/base.html`'e dokunma — marketing sayfaları kendi `marketing/base.html`'ini kullanır
- Mevcut hiçbir route silinmez, değiştirilmez
- `/login` URL'i değişmez — "Giriş Yap" butonu `href="/login"`
- `@login_required` YOK — marketing sayfaları herkese açık
- Flask-WTF CSRF sadece `demo-talep` ve `iletisim` formlarında
- Inline JS/CSS yasak — `static/marketing/css/marketing.css` ve `static/marketing/js/marketing.js`
- SweetAlert2 CDN'den yüklenir (marketing sayfalarına özel, çakışma olmasın)
- Türkçe: tüm frontend metinler Türkçe
- Hata yönetimi: `try/except`, `app.logger.error` zorunlu, `except: pass` yasak
- Blog için: Markdown dosyaları `content/blog/` klasöründe, `python-markdown` ile parse
- Form gönderimi: mevcut `email_service.py` kullanılır
- TASKLOG'a TASK-035 olarak eklenir

---

## BÖLÜM 3 — TASARIM SİSTEMİ

### 3.1 CSS Değişkenleri (marketing.css başı)

```css
:root {
  --mk-primary:      #6366f1;   /* İndigo — mevcut platformla tutarlı */
  --mk-primary-dark: #4f46e5;   /* Derin indigo — hover, aktif */
  --mk-primary-light:#e0e7ff;   /* Açık indigo — badge, highlight */
  --mk-dark:         #1e1b4b;   /* Koyu — sidebar rengiyle aynı, footer/rakamlar */
  --mk-success:      #10b981;   /* Yeşil — başarı metrikleri */
  --mk-warning:      #f59e0b;   /* Amber — uyarı */
  --mk-bg:           #f8fafc;   /* Sayfa arka planı */
  --mk-surface:      #ffffff;   /* Kart yüzeyi */
  --mk-text:         #0f172a;   /* Ana metin */
  --mk-muted:        #475569;   /* İkincil metin */
  --mk-border:       #e2e8f0;   /* Kenarlık */
}
```

### 3.2 Tipografi

Google Fonts CDN'den yüklenecek:

```html
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&family=DM+Sans:wght@400;500&family=DM+Mono&display=swap" rel="stylesheet">
```

```css
/* Başlıklar */
font-family: 'Plus Jakarta Sans', sans-serif;
font-weight: 700 veya 800;

/* Gövde metni */
font-family: 'DM Sans', sans-serif;
font-weight: 400 veya 500;

/* Sayısal veriler (rakamlar çubuğu) */
font-family: 'DM Mono', monospace;
```

### 3.3 Animasyonlar

**Scroll fade-in (Intersection Observer):**
```javascript
// marketing.js içinde
const observer = new IntersectionObserver((entries) => {
  entries.forEach(e => {
    if (e.isIntersecting) e.target.classList.add('visible');
  });
}, { threshold: 0.15 });
document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
```

**Sayaç animasyonu (rakamlar bölümü):**
- 0'dan gerçek değere 1.5 saniyede
- Intersection Observer ile scroll tetiklemeli
- Bir kez çalışır (tekrar tetiklenmez)

**Navbar scroll efekti:**
- Başlangıç: `background: transparent`
- Scroll 50px sonra: `background: white`, `box-shadow` beliriyor
- CSS transition ile yumuşak geçiş

**Kart hover:**
```css
.mk-card { transition: transform 0.2s, box-shadow 0.2s; }
.mk-card:hover { transform: translateY(-4px); box-shadow: 0 12px 32px rgba(99,102,241,0.12); }
```

**Hamburger menü:**
- Vanilla JS (Alpine.js bu sayfada yok)
- Mobilde overlay ile açılır

---

## BÖLÜM 4 — SAYFA İÇERİKLERİ (Tam Metin)

### 4.1 NAVBAR (Tüm Sayfalarda Ortak)

```
[Sol] Kokpitim  (metin logo, font-weight:800, renk: var(--mk-primary))

[Orta] Özellikler ▾  |  Nasıl Çalışır?  |  Blog  |  İletişim

[Sağ] Giriş Yap  (outline buton, href="/login")
      Demo Talep Et  (dolu buton, href="/demo-talep")
```

**"Özellikler" dropdown içeriği:**
- Stratejik Planlama → /ozellikler/stratejik-planlama
- Süreç Yönetimi → /ozellikler/surec-yonetimi
- Performans Takibi → /ozellikler/performans-takibi
- Proje Yönetimi → /ozellikler/proje-yonetimi
- Analiz Merkezi (K-Radar & K-Rapor) → /ozellikler/analiz-merkezi

**Mobil hamburger:** Tüm menü öğeleri dikey sıralanır, "Giriş Yap" ve "Demo Talep" alta iner.

---

### 4.2 ANA SAYFA (/)

#### HERO

```
[Gradient arka plan: linear-gradient(135deg, #4338ca 0%, #6366f1 50%, #818cf8 100%)]
[Hafif noise texture overlay: opacity 0.04]

H1 (beyaz, Plus Jakarta Sans 800, 3.5rem masaüstü / 2.2rem mobil):
"Strateji Belgede Kalmasın.
Süreçte Yaşasın."

P (beyaz, opacity 0.9, DM Sans 400, 1.2rem):
"Kokpitim; stratejik planınızı alt stratejilere, alt stratejileri
süreçlere, süreçleri ölçülebilir performans göstergelerine bağlar.
Hepsini tek ekranda, Türkçe."

[Butonlar]
→ "Demo Talep Et"   (beyaz dolgu, indigo metin, /demo-talep)
→ "Nasıl Çalışır? →"  (şeffaf, beyaz border, beyaz metin, /nasil-calisir)

[Sağ taraf — masaüstünde yan yana, mobilde alta]
Platform ekran görüntüsü placeholder:
Gerçek screenshot yoksa: koyu arka planlı, indigo tonlarında
soyut dashboard mockup (CSS ile çizilmiş)
```

#### RAKAMLAR ÇUBUĞU

```
[Arka plan: var(--mk-dark) = #1e1b4b]
[4 kolon, beyaz metin, DM Mono font]

  17          82           64          4.674
Aktif      Kullanıcı    Takip Edilen   KPI
Kurum                    Süreç         Verisi
```
Sayaç animasyonu: scroll tetiklemeli, 0'dan hedefe 1.5sn.

#### SORUN BÖLÜMÜ

```
Başlık: "Yönetim toplantısında bu sorulardan birini sordunuz mu?"

5 kart (tıklanınca alt açıklama genişler — accordion):

❓ "Geçen yılki stratejik planımız nerede?"
   → Kokpitim cevabı: Plan yılı yönetimi ile her dönem arşivde.
     Geçmiş yıllarla anlık karşılaştırma yapabilirsiniz.

❓ "Bu KPI'yı kim güncelledi, ne zaman?"
   → Kokpitim cevabı: Tam audit log. Her veri girişinde
     kimin, ne zaman, ne değiştirdiği kayıt altında.

❓ "Sürecin performansı nasıl ölçülüyor?"
   → Kokpitim cevabı: Her sürece bağlı süreç karnesi.
     KPI bazlı otomatik başarı puanı hesaplanır.

❓ "Bireysel hedefler kurumsal hedefle nasıl bağlantılı?"
   → Kokpitim cevabı: Strateji → Süreç → Bireysel PG zinciri.
     Her çalışan "neden bu hedef var?" sorusunun yanıtını görür.

❓ "Aylık faaliyet raporunu hazırlamak neden bu kadar uzun sürüyor?"
   → Kokpitim cevabı: K-Rapor ile tek tıkla. 14 analiz sekmesi,
     Excel export, otomatik periyodik raporlama.
```

#### ZİNCİR BÖLÜMÜ

```
Başlık: "Rakipler bu adımları ayrı modüllerde çözüyor.
         Kokpitim'de her halka birbiriyle konuşuyor."

[Görsel zincir — masaüstünde yatay, mobilde dikey]
[Her kutu: indigo border, iç metin koyu, oklar animasyonlu beliriyor]

┌──────────────┐    ┌──────────────────────────┐    ┌────────────────┐
│ MİSYON &     │ →  │ ANALİZLER                │ →  │ ANA            │
│ VİZYON       │    │ SWOT · TOWS · PESTLE     │    │ STRATEJİLER    │
└──────────────┘    └──────────────────────────┘    └────────────────┘
                                                             ↓
┌─────────────────┐                              ┌────────────────────┐
│ BİREYSEL        │ ←                            │ ALT STRATEJİLER    │
│ HEDEFLER        │                              └────────────────────┘
└─────────────────┘                                        ↓
         ↑                                    ┌─────────────────────────┐
         └──────────────────────────────────  │ SÜREÇLER ↔ KPI / PG    │
                                              └─────────────────────────┘

Alt metin: "Bir strateji değiştiğinde bağlı süreçler, KPI'lar
ve bireysel hedefler otomatik olarak ilişkilendiriliyor."
```

Scroll trigger: kutular soldan sağa kademeli belirir (animation-delay ile).

#### ÖZELLİKLER KARTLARI

```
Başlık: "Kurumunuzun tamamı, tek platformda"

5 kart (2-2-1 grid, mobilde tek sütun):

🎯 Stratejik Planlama
   "SWOT, TOWS, PESTLE, OKR, BSC. Strateji haritanızı oluşturun,
   yıl boyunca canlı tutun. Geçmiş dönemlerle karşılaştırma yapın."
   [Devamını gör →] → /ozellikler/stratejik-planlama

⚙️ Süreç Yönetimi
   "Süreç karnesi, KPI bağlantısı, Veri Giriş Sihirbazı, tam audit log.
   Kim, ne zaman, ne girdi — hiçbir şey kaybolmaz."
   [Devamını gör →] → /ozellikler/surec-yonetimi

📊 Performans Takibi
   "Otomatik başarı puanı, trend analizi, sapma uyarıları,
   anomali tespiti. KPI'ınızı Excel'de kaybetmeyin."
   [Devamını gör →] → /ozellikler/performans-takibi

📁 Proje Yönetimi
   "Gantt, RAID, EVM, kaynak kapasitesi, sprint takibi.
   Projeler stratejiden bağımsız değil."
   [Devamını gör →] → /ozellikler/proje-yonetimi

🔍 K-Radar & K-Rapor
   "Analitik merkez + tek tıkla kurumsal raporlama.
   14 analiz sekmesi, Excel export, periyodik otomatik rapor."
   [Devamını gör →] → /ozellikler/analiz-merkezi
```

#### NASIL ÇALIŞIR? (ANA SAYFADA ÖZET — 3 ADIM)

```
Başlık: "İlk haftadan itibaren çalışıyor"

Adım 1 — Kurumunuzu tanımlayın (Gün 1)
  "Admin panelden kullanıcı ve rolleri oluşturun.
  Misyon, vizyon ve ana stratejilerinizi girin.
  Süreç ağacınızı kurun."

Adım 2 — Bağlantıları kurun (Hafta 1)
  "Her süreci ilgili alt stratejiye bağlayın.
  KPI'ları tanımlayın: hedef değer, periyot, sorumlu.
  Bireysel hedefleri süreçlere bağlayın."

Adım 3 — Takip edin, raporlayın (Hafta 2+)
  "Veri Giriş Sihirbazı ile periyodik giriş yapın.
  Dashboard'dan anlık performansı izleyin.
  K-Rapor ile yönetim raporunuzu dakikada hazırlayın."

[Detaylı Anlatım →] → /nasil-calisir
```

#### SON CTA

```
[Arka plan: var(--mk-dark) = #1e1b4b]

Başlık (beyaz): "Stratejik planınız bu yıl rafa kalkmayacak."
Alt metin (beyaz, opacity 0.8):
"30 dakikalık demo ile platformu canlı görün.
Kuruluma gerek yok, IT desteği gerekmez."

[Buton]: "Demo Talep Et →"  (beyaz dolgu, indigo metin, /demo-talep)

3 güven notu (ikonlu, beyaz):
🇹🇷  %100 Türkçe arayüz ve destek
🔒  Veriler Türkiye'deki sunucularda
📊  Kurumunuza özel izolasyon
```

#### FOOTER

```
[Arka plan: #0f172a — çok koyu, footer'a ayrı ton]

Sol sütun:
  Kokpitim  (metin logo, indigo)
  "Stratejiyi sahaya taşıyan platform."

Orta sütun — Özellikler:
  Stratejik Planlama
  Süreç Yönetimi
  Performans Takibi
  Proje Yönetimi
  Analiz Merkezi

Sağ sütun — Hızlı Erişim:
  Nasıl Çalışır?
  Demo Talep Et
  Blog
  İletişim
  Giriş Yap  → /login

İletişim:
  info@kokpitim.com

Alt çizgi:
© 2026 Kokpitim. Tüm hakları saklıdır.
KVKK Aydınlatma Metni  |  Gizlilik Politikası
```

---

### 4.3 ÖZELLİKLER GENEL SAYFASI (/ozellikler)

5 özellik kartı yan yana (büyük, tıklanabilir) — her biri alt sayfaya gider.
Ana sayfadaki özellik kartlarının büyütülmüş hali. Ek açıklama paragrafı her kartın altında.

---

### 4.4 STRATEJİK PLANLAMA (/ozellikler/stratejik-planlama)

```
Başlık: "Stratejik planınız yılda bir değil, her gün güncel"

Alt başlık:
"Misyon ve vizyonunuzdan alt stratejilere, SWOT'tan TOWS aksiyonlarına —
tüm stratejik yönetim döngüsü tek platformda."

Özellik listesi (ikon + başlık + açıklama formatında):

✅ Plan Yılı Yönetimi
   Yıllık dönemler bazlı planlama. Geçmiş yılların verileriyle
   anlık karşılaştırma yapın. Kaç stratejik hedef gerçekleşti?

✅ Misyon & Vizyon Yönetimi
   Kurumsal kimliği dijital ortamda tanımlayın.
   Tüm kullanıcılar görebilir, üst yönetim güncelleyebilir.

✅ Strateji Hiyerarşisi
   Ana Strateji → Alt Strateji → Süreç bağlantısı.
   Her alt strateji hangi süreci besliyor, görsel olarak izlenir.

✅ SWOT Analizi
   Güçlü/zayıf yönler, fırsatlar, tehditler.
   Yıllara göre SWOT trendi — kurumsal olgunluk izlenir.

✅ TOWS Matrisi
   SO, ST, WO, WT stratejik aksiyonları.
   SWOT çıktıları otomatik TOWS'u besler.

✅ PESTLE Analizi
   6 faktörlü dış çevre taraması:
   Politik, Ekonomik, Sosyal, Teknolojik, Yasal, Çevresel.

✅ OKR Yönetimi
   Çeyreklik hedefler ve anahtar sonuçlar.
   Hedef gerçekleşme takibi dönem bazlı.

✅ BSC — Balanced Scorecard
   4 perspektif: Finansal, Müşteri, İç Süreçler, Öğrenme & Gelişim.
   Her perspektif KPI'larla desteklenir.

✅ Strateji Haritası
   Görsel akış diyagramı — strateji hiyerarşisi tek ekranda.

✅ K-Vektör
   Strateji ağırlık dağılımı ve kota analizi.

Bölüm altında CTA: "Demo Talep Et →" → /demo-talep
```

---

### 4.5 SÜREÇ YÖNETİMİ (/ozellikler/surec-yonetimi)

```
Başlık: "Süreç tanımlamak yetmez. Ölçmek gerekir."

Alt başlık:
"Hiyerarşik süreç ağacından KPI bağlantısına, faaliyet takibinden
tam audit log'a — süreçleriniz artık ölçülebilir."

Özellik listesi:

✅ Hiyerarşik Süreç Ağacı
   Ana süreç → alt süreç. İstediğiniz derinlikte.
   Her süreç hangi stratejiye hizmet ettiğini gösterir.

✅ Süreç Karnesi
   Her sürece özgü KPI tabanlı performans kartı.
   Otomatik hesaplanan başarı skoru (1-5 skala).

✅ Çok Periyotlu Ölçüm
   Günlük, haftalık, aylık, çeyreklik veya yıllık.
   Her KPI'a uygun periyot seçilir.

✅ Veri Giriş Sihirbazı (VGS)
   Adım adım rehberli veri girişi.
   Hangi KPI girilmedi, kim girmedi — sistem hatırlatır.

✅ Faaliyet Takibi
   Süreç faaliyetleri oluştur, ata, takip et.
   Tamamlanma durumu, hatırlatmalar, oto-tamamlama.

✅ Tam Audit Log
   Kim, ne zaman, ne girdi — değişiklik geçmişi kayıt altında.
   Denetim raporları için eksiksiz iz.

✅ Süreç Olgunluk Değerlendirmesi
   1-5 arası olgunluk seviyesi.
   Kurumunuz hangi süreçlerde olgun, hangilerinde gelişmeli?

✅ Excel Export
   Süreç karnesi verilerini Excel'e aktarın.
   Yönetim sunumlarına hazır format.

✅ Otomatik Bildirimler
   Veri girişi hatırlatmaları, faaliyet güncellemeleri.
   WebSocket ile anlık push bildirimleri.

CTA: "Demo Talep Et →" → /demo-talep
```

---

### 4.6 PERFORMANS TAKİBİ (/ozellikler/performans-takibi)

```
Başlık: "KPI'ınızı Excel'de kaybetmeyin."

Alt başlık:
"Otomatik başarı puanından anomali tespitine, trend analizinden
tahminlemeye — verileriniz size konuşuyor."

Özellik listesi:

✅ Bireysel Performans Karnesi
   Çalışan bazlı PG takibi. Bireysel hedefler kurumsal
   stratejiye bağlı — "neden bu hedef var?" sorusu cevaplı.

✅ Otomatik Başarı Puanı
   1-5 skala, ağırlıklı hesaplama.
   Çalışan, süreç veya kurum bazında genel skor.

✅ Trend Analizi
   Zaman serisi grafikleri. Performans nereye gidiyor?
   Dönemler arası karşılaştırma.

✅ Sapma Uyarıları
   Hedeften sapma bildirim eşiği tanımlayın.
   WebSocket ile anlık push — gecikme yok.

✅ Favori PG'ler
   Sık kullandığınız göstergeleri sabitleyin.
   Hızlı erişim, kişiselleştirilmiş dashboard.

✅ Dönem Karşılaştırması
   Geçmiş periyotlarla yanyana görüntüleme.
   Bu ay geçen aya göre nerede?

✅ Anomali Tespiti
   z-score, IQR ve hareketli ortalama yöntemleriyle
   otomatik uyarı. Beklenmedik değişimleri kaçırmayın.

✅ Tahminleme
   Trend verisinden gelecek dönem projeksiyonu.
   Hedefe ulaşılacak mı? Sistem önceden söylüyor.

CTA: "Demo Talep Et →" → /demo-talep
```

---

### 4.7 PROJE YÖNETİMİ (/ozellikler/proje-yonetimi)

```
Başlık: "Projeler stratejiden bağımsız değil."

Alt başlık:
"Görev takibinden EVM'e, RAID yönetiminden kaynak kapasitesine —
projeleriniz stratejik hedeflerinizle konuşuyor."

Özellik listesi:

✅ Proje Portföyü
   Tüm projeler tek ekranda. Durum, sağlık skoru, tamamlanma oranı.

✅ Görev Yönetimi
   Görev oluştur, ata, takip et. Bağımlılıklar, öncelikler.

✅ Gantt Görünümü
   Zaman çizelgesi planlaması. Kritik yol görsel.

✅ RAID Yönetimi
   Risk, Aksiyon, Sorun, Karar. Proje riski sistematik takip.

✅ Kaynak Kapasite Planlaması
   Kişi bazlı iş yükü analizi. Kim ne kadar yüklü?

✅ EVM — Kazanılmış Değer Analizi
   SPI ve CPI metrikleri. Proje zamanında mı, bütçede mi?

✅ CPM — Kritik Yol Metodu
   Kritik görev zinciri. Hangi görev gecikirirse proje gecikir?

✅ Sprint Yönetimi
   Çevik proje takibi. Backlog, aktif sprint, tamamlanan.

✅ Proje Sağlık Skoru
   Otomatik hesaplanan sağlık göstergesi.
   Yeşil / sarı / kırmızı — durumu anlık görün.

✅ Strateji Bağlantısı
   Her proje hangi stratejik hedefe katkı sağlıyor?
   Portföy → strateji hizalama analizi.

CTA: "Demo Talep Et →" → /demo-talep
```

---

### 4.8 ANALİZ MERKEZİ — K-Radar & K-Rapor (/ozellikler/analiz-merkezi)

```
Başlık: "Kurumunuzun nabzını gerçek zamanlı tutun."

Alt başlık:
"K-Radar analitik motoru ve K-Rapor raporlama sistemi —
stratejik, operasyonel ve bireysel verileri tek merkezde birleştirir."

--- K-RADAR bölümü ---

K-Radar — Analitik Merkez:
"K-Radar; stratejik planlama (KS), süreç performansı (KP)
ve proje yönetimi (KPR) verilerini tek bir analitik merkezde birleştirir."

✅ Vizyon Skoru
   0-1000 ölçeğinde kurumsal performans skoru.
   Strateji, süreç ve proje verisinden hesaplanır.

✅ GAP Analizi
   Hedef vs gerçekleşen. Hangi süreçte ne kadar açık var?
   Görsel ısı haritası formatında.

✅ Strateji Kapsama Analizi
   Boş / kısmi / tam strateji oranı.
   Hangi stratejik alanlarda KPI tanımlı değil?

✅ Risk Isı Haritası
   Süreç ve proje risklerini görsel matris üzerinde izleyin.

✅ EVM Metrikleri
   SPI, CPI. Portföy bazlı proje sağlığı.

✅ Trend Analizi + Tahminleme
   Geçmiş veriden geleceğe projeksiyon.

✅ Anomali Tespiti
   z-score, IQR, hareketli ortalama — sistem sapmaları
   otomatik tespit eder ve uyarır.

✅ Kurumlar Arası Karşılaştırma
   Çok-tenant yapısında birimler arası benchmark.

--- K-RAPOR bölümü ---

K-Rapor — Raporlama Motoru:
"Aylık yönetim raporunuzu artık dakikalar içinde hazırlayın."

✅ 14 Analiz Sekmesi
   Kurumsal özet, Süreç performansı, Strateji kapsama,
   Faaliyet matrisi, Bireysel karne, Aktivite heatmap,
   Sorumlu analizi, SWOT/TOWS trend ve daha fazlası.

✅ Otomatik Başarı Skorları
   Her sekme için hesaplanmış, sunuma hazır metrikler.

✅ Excel Export
   Tüm rapor sekmelerini Excel'e aktarın.

✅ Periyodik Otomatik Raporlama
   Günlük, haftalık, aylık — zamanlanmış rapor üretimi.

CTA: "Demo Talep Et →" → /demo-talep
```

---

### 4.9 NASIL ÇALIŞIR? (/nasil-calisir)

```
Başlık: "İlk haftadan itibaren çalışıyor."

Alt başlık:
"Kurulum gerektirmez. IT departmanı gerekmez.
Tarayıcı yeterli."

3 adım (büyük, numaralı):

① Kurumunuzu tanımlayın — Gün 1
  Admin panelden kullanıcılarınızı ve rollerini (tenant_admin,
  executive_manager, kullanıcı) oluşturun.
  Misyon, vizyon ve ana stratejilerinizi girin.
  Süreç ağacınızı kurun.

② Bağlantıları kurun — Hafta 1
  Her süreci ilgili alt stratejiye bağlayın.
  Performans göstergelerini tanımlayın:
  hedef değer, ölçüm periyodu, sorumlu kişi.
  Bireysel hedefleri süreçlere bağlayın.

③ Takip edin, raporlayın — Hafta 2+
  Veri Giriş Sihirbazı (VGS) ile periyodik veri girişi yapın.
  Dashboard'dan anlık performansı izleyin.
  Aylık yönetim raporunuzu K-Rapor ile dakikalar içinde hazırlayın.

---

Ekran Görüntüleri Bölümü:
(Gerçek platform screenshot'ları buraya yerleştirilecek)
Placeholder olarak: 4 adet koyu arka planlı, indigo kenarlıklı
boş dikdörtgen — screenshot eklenmesine hazır yapı.

---

CTA:
"Platformu Canlı Görmek İster misiniz?"
[Demo Talep Et →] → /demo-talep
```

---

### 4.10 DEMO TALEP (/demo-talep)

```
Başlık: "Platformu 30 dakikada canlı görün."
Alt metin: "Formu doldurun, size en kısa sürede ulaşalım."

FORM (Flask-WTF, CSRF korumalı):

Ad Soyad *              [text input]
Kurum Adı *             [text input]
Görev / Unvan *         [text input]
Sektör *                [select]
                         → Kamu
                         → Sağlık
                         → Eğitim
                         → Üretim
                         → Hizmet / Danışmanlık
                         → Diğer

Kurum Çalışan Sayısı *  [select]
                         → 1 – 50
                         → 51 – 200
                         → 201 – 1.000
                         → 1.000+

E-posta *               [email input]
Telefon *               [tel input]

Görmek istediğiniz modüller: [checkbox grubu]
  ☐ Stratejik Planlama (SP)
  ☐ Süreç Yönetimi
  ☐ KPI & Performans Takibi
  ☐ Proje Yönetimi
  ☐ K-Radar & K-Rapor (Analiz)

Mesajınız (isteğe bağlı)  [textarea]

[Demo Talep Gönder]  (indigo, tam genişlik)

FORM ALTI (güven öğeleri):
🔒 Bilgileriniz üçüncü taraflarla paylaşılmaz.
📅 En geç 1 iş günü içinde size ulaşırız.
```

**Backend (routes.py):**
```python
@marketing_bp.route('/demo-talep', methods=['GET', 'POST'])
def demo_talep():
    if request.method == 'POST':
        try:
            # Validasyon
            # email_service.py ile gönder → info@kokpitim.com
            # Başarı: SweetAlert2 Türkçe başarı mesajı
            # redirect('/') veya aynı sayfa
        except Exception as e:
            app.logger.error(f"Demo talep hatası: {e}")
            # Hata: SweetAlert2 Türkçe hata mesajı
```

Spam koruması: honeypot alanı (gizli input, dolu gelirse görmezden gel).

---

### 4.11 BLOG (/blog ve /blog/<slug>)

**Blog listesi sayfası:**
```
Başlık: "Kurumsal Yönetim Üzerine"
Alt başlık: "Stratejik planlama, süreç yönetimi ve performans takibi hakkında."

İlk 10 yazı (öncelik sırasına göre oluşturulacak):
1. Stratejik Plan Neden Rafa Kalkar? 5 Temel Neden
2. Süreç Karnesi Nedir, Nasıl Hazırlanır?
3. KPI mı, OKR mı, BSC mi? Kurumunuz için Doğru Çerçeve
4. SWOT Analizini Aksiyona Dönüştürmenin Tek Yolu: TOWS Matrisi
5. Bireysel Hedef ile Kurumsal Strateji Nasıl Bağlanır?
6. Kamu Kurumlarında Stratejik Planlama: Mevzuat ve Pratik
7. Performans Göstergesi (PG) Tasarımında 7 Hata
8. Süreç Olgunluk Modeli: Kurumunuz Hangi Seviyede?
9. Otomatik Raporlama ile Aylık Faaliyet Raporunu Nasıl Hazırlarsınız?
10. Anomali Tespiti: KPI Verinizdeki Sinyalleri Nasıl Yakalarsınız?
```

**Blog altyapısı:**
- Yazılar `content/blog/` klasöründe Markdown dosyaları olarak saklanır
- Her dosya başında frontmatter: `title`, `slug`, `date`, `summary`, `author`
- `python-markdown` paketi ile HTML'e dönüştürülür
- `/blog` → listeyi gösterir | `/blog/<slug>` → ilgili yazıyı gösterir
- İlk aşamada en az 2 yazı gerçek içerikle oluşturulacak (1. ve 2. yazı)

---

### 4.12 İLETİŞİM (/iletisim)

```
Başlık: "İletişime Geçin"

FORM (Flask-WTF, CSRF korumalı):
Ad Soyad *   [text]
E-posta *    [email]
Konu *       [select: Demo Talebi / Teknik Soru / İş Birliği / Diğer]
Mesaj *      [textarea]
[Gönder]

Sağ taraf (veya alt):
📧 info@kokpitim.com
(Diğer iletişim bilgileri hazır olunca eklenir)
```

---

## BÖLÜM 5 — SEO

### 5.1 Her Sayfa İçin Meta Etiketleri

`marketing/base.html` içinde:

```html
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="{{ page_description }}">
<meta property="og:title" content="{{ page_title }} | Kokpitim">
<meta property="og:description" content="{{ page_description }}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://kokpitim.com{{ request.path }}">
<title>{{ page_title }} | Kokpitim</title>
```

### 5.2 Sayfa Başlıkları ve Açıklamaları

| Sayfa | Title | Description |
|-------|-------|-------------|
| / | Kokpitim — Stratejik Yönetim Platformu | Strateji, süreç, KPI ve bireysel performansı tek platformda yönetin. Türkiye'nin kurumsal performans yönetim yazılımı. |
| /ozellikler | Özellikler — Kokpitim | Stratejik planlama, süreç yönetimi, performans takibi, proje yönetimi ve analiz merkezi. |
| /ozellikler/stratejik-planlama | Stratejik Planlama — Kokpitim | SWOT, TOWS, OKR, BSC ile stratejik planınızı yıl boyunca canlı tutun. |
| /ozellikler/surec-yonetimi | Süreç Yönetimi — Kokpitim | Süreç karnesi, KPI bağlantısı ve tam audit log ile süreçlerinizi ölçün. |
| /ozellikler/performans-takibi | Performans Takibi — Kokpitim | Otomatik başarı puanı, anomali tespiti ve tahminleme ile KPI'larınızı izleyin. |
| /ozellikler/proje-yonetimi | Proje Yönetimi — Kokpitim | Gantt, RAID, EVM ve strateji bağlantısı ile projelerinizi yönetin. |
| /ozellikler/analiz-merkezi | K-Radar & K-Rapor — Kokpitim | Kurumsal analitik merkez ve tek tıkla raporlama. |
| /nasil-calisir | Nasıl Çalışır? — Kokpitim | İlk haftadan itibaren çalışan kurumsal yönetim platformu. |
| /demo-talep | Demo Talep — Kokpitim | 30 dakikalık ücretsiz demo için formu doldurun. |
| /blog | Blog — Kokpitim | Stratejik planlama ve kurumsal performans yönetimi üzerine içerikler. |

### 5.3 Sitemap

`/sitemap.xml` route'u eklenecek — tüm sayfaları ve blog yazılarını listeler.

### 5.4 robots.txt

`/robots.txt` route'u:
```
User-agent: *
Allow: /
Sitemap: https://kokpitim.com/sitemap.xml
```

---

## BÖLÜM 6 — DEPLOY VE ENTEGRASYON

### 6.1 Mevcut Yapıya Dokunulmayacaklar

- `micro/base.html` — değiştirilmez
- `/login`, `/micro/*`, `/auth/*` route'ları — değiştirilmez
- Docker container yapısı — değiştirilmez
- `requirements.txt` — sadece `python-markdown` eklenir (yoksa)

### 6.2 Yeni Eklenecekler

```
micro/modules/marketing/
    __init__.py
    routes.py

templates/marketing/
    base.html
    index.html
    ozellikler/index.html
    ozellikler/stratejik_planlama.html
    ozellikler/surec_yonetimi.html
    ozellikler/performans_takibi.html
    ozellikler/proje_yonetimi.html
    ozellikler/analiz_merkezi.html
    nasil_calisir.html
    demo_talep.html
    blog/index.html
    blog/post.html
    iletisim.html

static/marketing/
    css/marketing.css
    js/marketing.js

content/blog/
    stratejik-plan-neden-rafa-kalkar.md
    surec-karnesi-nedir.md
    (diğerleri sonra eklenir)
```

### 6.3 Analytics

`marketing/base.html` içinde, `</head>` öncesi:
```html
<!-- Google Analytics 4 -->
<!-- GA_MEASUREMENT_ID buraya gelecek — hazır olunca eklenir -->
```
Şimdilik placeholder olarak bırakılır.

---

## BÖLÜM 7 — TEST KONTROL LİSTESİ

Kiro, aşağıdakileri test etmeden işi bitirmiş sayma:

### Mevcut Sistem Bozulmadı mı?
- [ ] `kokpitim.com/login` → eski login sayfası hâlâ çalışıyor
- [ ] `kokpitim.com/micro/dashboard` → platform hâlâ çalışıyor
- [ ] `kokpitim.com/auth/login` → çalışıyor (varsa)

### Yeni Sayfalar Çalışıyor mu?
- [ ] `kokpitim.com/` → tanıtım ana sayfası açılıyor
- [ ] `kokpitim.com/ozellikler` → özellikler sayfası açılıyor
- [ ] `kokpitim.com/ozellikler/stratejik-planlama` → açılıyor
- [ ] `kokpitim.com/ozellikler/surec-yonetimi` → açılıyor
- [ ] `kokpitim.com/ozellikler/performans-takibi` → açılıyor
- [ ] `kokpitim.com/ozellikler/proje-yonetimi` → açılıyor
- [ ] `kokpitim.com/ozellikler/analiz-merkezi` → açılıyor
- [ ] `kokpitim.com/nasil-calisir` → açılıyor
- [ ] `kokpitim.com/demo-talep` → form açılıyor, POST çalışıyor
- [ ] `kokpitim.com/blog` → liste açılıyor
- [ ] `kokpitim.com/blog/stratejik-plan-neden-rafa-kalkar` → yazı açılıyor
- [ ] `kokpitim.com/iletisim` → form açılıyor
- [ ] `kokpitim.com/sitemap.xml` → XML döndürüyor
- [ ] `kokpitim.com/robots.txt` → düz metin döndürüyor

### Navbar ve Yönlendirmeler
- [ ] "Giriş Yap" butonu → `/login`'e gidiyor
- [ ] "Demo Talep Et" butonu → `/demo-talep`'e gidiyor
- [ ] Özellikler dropdown çalışıyor
- [ ] Mobilde hamburger açılıp kapanıyor

### Formlar
- [ ] Demo talep formu: boş gönderilince validasyon hatası veriyor
- [ ] Demo talep formu: dolu gönderilince SweetAlert2 başarı mesajı
- [ ] Demo talep formu: e-posta `info@kokpitim.com`'a ulaşıyor
- [ ] İletişim formu: aynı şekilde çalışıyor

### Görsel ve Animasyon
- [ ] Sayaç animasyonu scroll'da tetikleniyor
- [ ] Fade-in animasyonlar çalışıyor
- [ ] Navbar scroll'da arka plan beliriyor
- [ ] Zincir bölümü görünür
- [ ] Mobil görünüm düzgün (en az 375px)

### TASKLOG
- [ ] `docs/TASKLOG.md`'ye TASK-035 eklendi

---

## BÖLÜM 8 — LANSMAN ÖNCESİ KONTROL LİSTESİ

(Deploy sonrası yapılacaklar — Kiro değil, sen yapacaksın)

### İçerik
- [ ] Gerçek platform ekran görüntüleri alındı → `static/marketing/img/` klasörüne eklendi
- [ ] Tanıtım videosu hazırlandı (opsiyonel, sonra eklenebilir)
- [ ] İletişim bilgileri güncellendi (telefon, şehir)
- [ ] KVKK aydınlatma metni hazırlandı
- [ ] Gizlilik Politikası metni hazırlandı
- [ ] `info@kokpitim.com` e-posta adresi aktif ve demo taleplerini alıyor

### Teknik
- [ ] SSL sertifikası aktif
- [ ] Google Analytics 4 Measurement ID alındı, `base.html`'e eklendi
- [ ] `sitemap.xml` doğru URL'leri içeriyor
- [ ] Lighthouse skoru ölçüldü (hedef: Performance 85+, SEO 95+)
- [ ] Mobil gerçek cihazda test edildi

### Sosyal Medya
- [ ] LinkedIn Company Page oluşturuldu
- [ ] Open Graph meta etiketleri test edildi (og:image dahil)

---

*Bu doküman Kokpitim'in gerçek teknik yapısı, mevcut verileri (17 kurum, 82 kullanıcı, 64 süreç, 4.674 KPI verisi) ve rekabet konumu baz alınarak hazırlanmıştır.*
*Fiyatlandırma ve müşteri yorumları kasıtlı olarak çıkarılmıştır — hazır olmadan yayına girmemeli.*
