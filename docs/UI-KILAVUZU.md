# Kokpitim UI Kılavuzu

> **Hedef kitle:** Üst yönetim (CEO/CFO/Yönetim Kurulu)
> **Felsefe:** *Az şey, daha iyi gözüksün.* Veri yoğun ama nefes alan, kurumsal güven veren ama yorucu olmayan.
> **Sürüm:** v1.0 — 2026-05-24

Bu belge, Kokpitim'in tüm sayfaları için **tek doğru kaynak**tır. Yeni sayfa eklerken veya eski sayfayı modernize ederken **önce buraya bak**. Mevcut `mc-*` bileşen sistemi + indigo paletinin üzerine kurulu — yıkmıyoruz, **rafine ediyoruz**.

---

## 1. Temel Prensipler (Hatırlanması Gereken 5 Madde)

| # | Prensip | Pratik karşılığı |
|---|---|---|
| 1 | **Tek odak, büyük yazı** | Her ekranda bir tane "büyük rakam" olsun (sağlık skoru, ay sonu hedef vb.). Diğer her şey ondan küçük |
| 2 | **Beyaz alan ucuz değil** | Sıkışık tablo → güvensizlik. 16-24 px iç boşluk minimum |
| 3 | **Renk anlam taşır** | Yeşil = iyi, kırmızı = kötü, sarı = dikkat. Estetik için renk kullanma |
| 4 | **Hareket bilgi taşır** | Animasyon "havalı görünmek" için değil; durumu işaret eder (yükleniyor, tamamlandı, hata) |
| 5 | **Veri yoksa boşluk olmaz** | Her sayfada "veri yok" durumu tasarlanır — boş tablo değil, yönlendirici mesaj |

---

## 2. Tipografi

### Font ailesi
```css
--font-base: 'Inter', system-ui, -apple-system, sans-serif;
```
Değişmeyecek. Inter zaten yüklü, sayısal okunabilirliği yüksek (CFO için kritik).

### Type scale (mevcut, üzerine kural eklendi)
| Token | Boyut | Ne için |
|---|---|---|
| `--text-2xs` | 10px | **Yalnızca** badge, etiket. Asla paragraf için değil |
| `--text-xs` | 11px | Tablo başlığı, dipnot, "son güncelleme" |
| `--text-sm` | 12px | Yardımcı metin (helper, label altı) |
| `--text-md` | 13px | Form input içi, ikincil metin |
| `--text-base` | 14px | **Varsayılan paragraf** ve buton |
| `--text-lg` | 15px | Vurgulanan paragraf, kart başlığı |
| `--text-xl` | 16px | Sayfa başlığı (page_title) |
| `--text-2xl` | 20px | Modal başlık, hero başlık |
| `--text-3xl` | 28px | **Hero rakam** — sağlık skoru, ay sonu hedefi |
| _yeni:_ `--text-display` | 48px | Exec dashboard'taki "ana skor" — sayfa başına 1 kez |

### Ağırlık (font-weight) hiyerarşisi
- `400` — paragraf, açıklama
- `500` — label, etiket
- `600` — başlık, vurgulanan değer, badge
- `700` — sayfa başlığı, hero rakam
- `800` — (varsa) display rakamlar

### Satır yüksekliği
- Başlık (`h1-h4`, kart başlığı): `line-height: 1.2`
- Paragraf: `line-height: 1.6`
- Tablo hücresi: `line-height: 1.4`

### Renk hiyerarşisi (metin)
| Token | Hex | Kullanım |
|---|---|---|
| `--text-strong` | `#0f172a` | Sayfa başlığı, hero rakam |
| `--text-default` | `#1e293b` | Paragraf, kart içi |
| `--text-muted` | `#475569` | Yardımcı metin |
| `--text-subtle` | `#64748b` | Dipnot, "son güncelleme" |
| `--text-disabled` | `#94a3b8` | Pasif, soluk |

---

## 3. Renk Paleti

### Marka (değişmeyecek)
```css
--color-primary:        #4f46e5;  /* Indigo 600 — birincil buton, link */
--color-primary-hover:  #4338ca;
--color-primary-soft:   #eef2ff;  /* Hover bg, badge bg */
--color-accent:         #8b5cf6;  /* Vurgu, decorative */
```

### Anlam renkleri (semantic — değiştirilemez)
```css
--color-success:  #10b981;   /* Yeşil — tamamlandı, hedef üstü */
--color-warning:  #f59e0b;   /* Sarı — dikkat, gecikme yaklaşıyor */
--color-danger:   #ef4444;   /* Kırmızı — kritik, hedef altı */
--color-info:     #0ea5e9;   /* Mavi — bilgi, nötr */

/* Soft varyantlar (background için) */
--color-success-soft: #d1fae5;
--color-warning-soft: #fef3c7;
--color-danger-soft:  #fee2e2;
--color-info-soft:    #e0f2fe;
```

### Nötrler (gri tonları)
Slate paletini kullan (zaten çoğu yerde var):
- Arka plan: `#f8fafc` (sayfa) → `#ffffff` (kart)
- Border: `#e2e8f0` (varsayılan), `#cbd5e1` (vurgu)
- Hover bg: `#f1f5f9`

### Status badge renkleri (Initiative, KPI, vb.)
| Durum | Bg | Text |
|---|---|---|
| Planlandı | `#f1f5f9` | `#475569` |
| Devam Ediyor | `#dbeafe` | `#1e40af` |
| Tamamlandı | `#d1fae5` | `#065f46` |
| Beklemede | `#fef3c7` | `#92400e` |
| İptal | `#fee2e2` | `#991b1b` |

**Yasak:** Pembe (`#ec4899`/`#db2777`) genel paletten kalkmalı — sadece Initiative node'unda kalsın (anlam taşıyor). Diğer yerlerde indigo + slate hakim olmalı. Mevcut `Initiative` sayfasında pembe vurgu fazla.

---

## 4. Spacing (Boşluk)

8'in katları sistemi — Tailwind ile uyumlu, hesabı kolay:

| Token | Değer | Kullanım |
|---|---|---|
| `--space-1` | 4px | Icon-text arası |
| `--space-2` | 8px | Badge iç padding |
| `--space-3` | 12px | Buton iç padding (Y) |
| `--space-4` | 16px | Kart iç padding, form alanları arası |
| `--space-5` | 20px | Bölüm içi başlık-içerik arası |
| `--space-6` | 24px | Kart-kart arası, bölüm-bölüm arası |
| `--space-8` | 32px | Sayfa başlık-içerik arası |
| `--space-10` | 40px | Hero bölüm + alttaki içerik |

**Kural:** Bir sayfanın tüm boşlukları bu 7 değerden biri olsun. `padding: 14px` yasak — `16px` kullan.

### Kart padding standardı
- Küçük kart (KPI tile): `16px`
- Orta kart (form, liste): `20px`
- Büyük kart (hero, dashboard widget): `24px`

### Sayfa max-width
- Liste/yönetim sayfaları: `1200px`
- Dashboard: `1400px`
- Form sayfaları: `800px`
- Detay sayfaları: `1100px`

---

## 5. Bileşen Standartları

### Sayfa başlığı (`page_title`)
```html
<div class="mc-page-header" style="margin-bottom: 24px;">
  <h2 style="font-size: 20px; font-weight: 700; color: #0f172a; margin: 0 0 4px;">
    <i class="fas fa-icon" style="color: #4f46e5; margin-right: 8px;"></i>
    Sayfa Başlığı
  </h2>
  <p style="font-size: 13px; color: #64748b; margin: 0;">
    Bu sayfada ne yapacağının 1 cümlelik açıklaması.
  </p>
</div>
```
**Kural:** Her sayfada **mutlaka** alt açıklama olur. Kullanıcı "burada ne yapacağım" diye sormasın.

### Hero kart (büyük rakam)
```html
<div class="mc-card" style="padding: 24px; background: linear-gradient(135deg, #1e293b, #334155); color: #fff;">
  <div style="font-size: 11px; opacity: 0.7; text-transform: uppercase; letter-spacing: 0.5px;">
    Strateji Sağlık Skoru
  </div>
  <div style="font-size: 48px; font-weight: 800; line-height: 1;">87</div>
  <div style="font-size: 12px; opacity: 0.7; margin-top: 4px;">2026 yılı</div>
</div>
```
**Kural:** Sayfa başına **1 tane** hero. Üst yönetim sayfasında olmazsa olmaz.

### KPI kartı (küçük)
```html
<div class="mc-card" style="padding: 16px; border-left: 4px solid #0ea5e9;">
  <div style="font-size: 12px; color: #64748b; text-transform: uppercase;">KPI Adı</div>
  <div style="font-size: 28px; font-weight: 700; color: #0f172a;">42</div>
  <div style="font-size: 12px; color: #64748b;">açıklama satırı</div>
</div>
```
Sol kenardaki 4px renkli şerit → kategoriyi/durumu işaret eder. (Mavi=nötr, yeşil=iyi, sarı=dikkat, kırmızı=sorun)

### Buton
```html
<!-- Primary -->
<button class="mc-btn mc-btn-primary">
  <i class="fas fa-save"></i> Kaydet
</button>

<!-- Secondary -->
<button class="mc-btn mc-btn-secondary">İptal</button>

<!-- Danger (silme, kritik aksiyon) -->
<button class="mc-btn mc-btn-danger">
  <i class="fas fa-trash"></i> Sil
</button>
```
**Kural:**
- Bir formda **en fazla 1 primary** buton (asıl aksiyon)
- İcon + metin → her zaman aynı sırada (icon solda, 6-8px ara)
- Hover'da renk **kararır**, açılmaz

### Tablo
```html
<table style="width:100%; border-collapse: collapse; font-size: 13px;">
  <thead>
    <tr style="background: #f8fafc; border-bottom: 2px solid #e2e8f0;">
      <th style="padding: 12px; text-align: left; color: #475569; font-weight: 600; text-transform: uppercase; font-size: 11px; letter-spacing: 0.5px;">
        Başlık
      </th>
    </tr>
  </thead>
  <tbody>
    <tr style="border-bottom: 1px solid #f1f5f9;">
      <td style="padding: 12px;">İçerik</td>
    </tr>
  </tbody>
</table>
```
**Kural:**
- Satır arası border `#f1f5f9` (zebra DEĞİL, sadece alt çizgi)
- Hover → satır `background: #f8fafc`
- Sayısal sütunlar `text-align: right` + `font-variant-numeric: tabular-nums`

### Form
- Label: `font-size: 12px; color: #64748b; margin-bottom: 4px; font-weight: 500;`
- Input: zorunlu olarak `mc-input` sınıfı; min yükseklik 36px
- Label-input grupları arasında 16px boşluk
- Hata mesajı: input'un hemen altında, `color: #ef4444; font-size: 12px;`

### Modal
KURALLAR-MASTER.md'deki `mc-modal-overlay` yapısı **standart** — SweetAlert2 modal yerine kullan. SweetAlert2 sadece:
- Onay diyaloğu (`Sil mi?`)
- Toast bildirimi (`Kaydedildi`)
- Basit bilgi mesajı

---

## 6. Grafikler (Chart.js)

### Renk paleti (grafikler için)
```js
const KOKPITIM_COLORS = [
  '#4f46e5', '#10b981', '#f59e0b', '#0ea5e9',
  '#8b5cf6', '#ef4444', '#06b6d4', '#84cc16',
];
```
İlk sıra **indigo**, son sıra **lime** — kurumsal hissi koru.

### Standart ayarlar
```js
Chart.defaults.font.family = 'Inter, sans-serif';
Chart.defaults.font.size = 12;
Chart.defaults.color = '#475569';
Chart.defaults.plugins.legend.labels.usePointStyle = true;
Chart.defaults.plugins.legend.labels.padding = 12;
```

### Grid/eksen
- Y ekseni grid: `color: '#f1f5f9'` (zorla gözükmeyen)
- X ekseni grid: kaldır (`display: false`)
- Eksen yazıları: `color: '#94a3b8'; fontSize: 11`

### Chart başlığı
Grafik üstündeki başlık **Chart.js içinden değil**, dışarıdan `<h4>` ile ver. Daha esnek + tutarlı tipografi.

---

## 7. Durum Tasarımları

### Loading (yükleniyor)
```html
<div style="padding: 40px; text-align: center; color: #64748b;">
  <i class="fas fa-spinner fa-spin" style="font-size: 24px;"></i>
  <div style="margin-top: 8px; font-size: 13px;">Yükleniyor...</div>
</div>
```
Veya: **skeleton** (yer tutucu kutular, animasyonlu)
```html
<div class="mc-skeleton" style="height: 60px; border-radius: 8px;"></div>
```
> CSS yeni eklenecek: `@keyframes shimmer` ile gri pulsing

### Empty state (veri yok)
```html
<div style="padding: 60px 20px; text-align: center;">
  <i class="fas fa-inbox" style="font-size: 48px; color: #cbd5e1;"></i>
  <h3 style="margin: 16px 0 4px; color: #475569;">Henüz veri yok</h3>
  <p style="color: #94a3b8; font-size: 13px; margin: 0 0 20px;">
    İlk kaydı oluşturarak başlayın.
  </p>
  <button class="mc-btn mc-btn-primary">
    <i class="fas fa-plus"></i> Yeni Kayıt
  </button>
</div>
```
**Kural:** Boş tablo göstermek yasak. Her boş durum **yönlendirir**.

### Error state (hata)
```html
<div class="mc-alert mc-alert-error" style="padding: 16px;">
  <i class="fas fa-exclamation-triangle" style="margin-right: 8px;"></i>
  Veriler yüklenemedi.
  <button onclick="location.reload()" style="margin-left: 12px;">Tekrar dene</button>
</div>
```

---

## 8. Mikro Etkileşim

### Geçiş süreleri (transition)
```css
--transition-fast:   120ms ease-out;   /* Hover */
--transition-base:   200ms ease-out;   /* Buton, kart */
--transition-slow:   320ms ease-out;   /* Modal açma/kapama */
```

### Hover davranışları
| Eleman | Hover etkisi |
|---|---|
| Buton | `background` koyulaşır, `transform: none` |
| Kart (tıklanabilirse) | `box-shadow` artar, `cursor: pointer` |
| Link | `color: #4338ca`, `text-decoration: underline` |
| Tablo satırı | `background: #f8fafc` |
| İkon-buton | `background: #eef2ff` daire içine alır |

**Yasak:** `transform: scale(1.05)` — kart zıplamasın. Üst yönetim ciddiyetle uyumsuz.

### Toast bildirimi (SweetAlert2)
```js
Swal.fire({
  toast: true,
  position: 'top-end',
  icon: 'success',
  title: 'Kaydedildi',
  showConfirmButton: false,
  timer: 2500,
  timerProgressBar: true,
});
```
Pozisyon **her zaman** `top-end` (sağ üst). Konum tutarlılığı = kullanıcı refleksi.

---

## 9. Veri Görselleştirme Kuralları (Exec Odaklı)

Üst yönetim grafiklerinin **3 altın kuralı**:

1. **3 saniye kuralı** — yönetici 3 saniyede grafiğin ne dediğini anlamalı. Eğer anlamıyorsa fazla detay var
2. **Yön ok'u** — KPI iyiye mi gidiyor kötüye mi? Sayının yanına ↑↓ ekle (renkli)
3. **Hedef çizgisi** — gerçekleşme bar/line ise, hedef değer **kesik çizgi** olarak hep görünsün

### Tercih edilen grafik tipleri
| Veri | Grafik |
|---|---|
| KPI trend (zaman) | Line chart |
| KPI kompozisyon | Donut (pie değil — okunmaz) |
| Karşılaştırma (kategori) | Yatay bar (dikey değil — Türkçe başlıklar uzun) |
| Korelasyon | Heatmap |
| Skor/durum | Gauge veya progress bar |
| Akış/süreç | Sankey (vis-network) |

### Kaçınılması gerekenler
- **3D grafik** — kurumsal değil
- **Pie chart 5'ten fazla dilim** — donut + "Diğer" grupla
- **Tek değer için tüm sayfa grafik** — KPI tile yeterli

---

## 10. Mobil & Responsive

### Breakpoint'ler (mevcut, korunacak)
- `<640px`  — mobil (sidebar hamburger)
- `<1024px` — tablet (grid 2 sütun)
- `≥1024px` — masaüstü (tam genişlik)

### Üst yönetim için **kritik**: Tablet uyumu
CEO/CFO çoğunlukla iPad'den bakar. Test edilecek 3 sayfa:
1. Exec dashboard
2. Süreç karne
3. Haftalık PDF (PDF olduğu için zaten OK)

### Mobil özel kurallar
- Tabloyu kart'a çevir (yatay kaydırma değil)
- Buton min `44px` yüksek (parmak hedefi)
- Form input'ları tam genişlik

---

## 11. Erişilebilirlik (a11y) Minimumu

| Kural | Pratik |
|---|---|
| Renk + ikon birlikte | Sadece renk ile bilgi verme (kırmızı = ✗, yeşil = ✓ ikon da olsun) |
| Kontrast ≥ 4.5:1 | Açık gri (`#94a3b8`) beyaz üstünde **sınır**. Önemli metinde kullanma |
| Form label | Her input'un kendi `<label for="...">` etiketi olmalı |
| Buton metin | "Tıkla", "Daha fazla" yerine ne yapacağını söyle: "Kaydet", "Detayları aç" |
| Focus | `outline: 2px solid #4f46e5` — gözükmeli |

---

## 12. Yeni Sayfa Hazırlık Kontrol Listesi

Bir sayfa "bitti" denmeden önce:

- [ ] Page header (başlık + 1 cümle açıklama) var
- [ ] Hero kart veya ana KPI tile'lar var (exec sayfaları için)
- [ ] Loading state tasarlandı
- [ ] Empty state tasarlandı
- [ ] Error state tasarlandı
- [ ] Tablo varsa: zebra yok, hover var, sayısallar sağa hizalı
- [ ] Buton sayısı: en fazla 1 primary
- [ ] Tüm padding/margin değerleri 8'in katı
- [ ] Renkler anlam taşıyor (random pembe yok)
- [ ] Mobile breakpoint test edildi
- [ ] Dark mode (varsa) çalışıyor

---

## 13. CSS Değişkenleri — Eklenmesi Gereken

Mevcut `components.css`'e şu blok eklenmeli (kullanıcı onayıyla):

```css
:root {
  /* Yeni: spacing */
  --space-1: 4px;  --space-2: 8px;  --space-3: 12px;
  --space-4: 16px; --space-5: 20px; --space-6: 24px;
  --space-8: 32px; --space-10: 40px;

  /* Yeni: text color hierarchy */
  --text-strong:   #0f172a;
  --text-default:  #1e293b;
  --text-muted:    #475569;
  --text-subtle:   #64748b;
  --text-disabled: #94a3b8;

  /* Yeni: semantic colors (soft varyantlar dahil) */
  --color-success: #10b981;  --color-success-soft: #d1fae5;
  --color-warning: #f59e0b;  --color-warning-soft: #fef3c7;
  --color-danger:  #ef4444;  --color-danger-soft:  #fee2e2;
  --color-info:    #0ea5e9;  --color-info-soft:    #e0f2fe;

  /* Yeni: transitions */
  --transition-fast: 120ms ease-out;
  --transition-base: 200ms ease-out;
  --transition-slow: 320ms ease-out;

  /* Yeni: shadows */
  --shadow-sm:  0 1px 2px rgba(15, 23, 42, 0.05);
  --shadow-md:  0 4px 6px rgba(15, 23, 42, 0.07);
  --shadow-lg:  0 10px 25px rgba(15, 23, 42, 0.1);
}

/* Yeni: skeleton loader */
@keyframes mc-shimmer {
  0%   { background-position: -1000px 0; }
  100% { background-position: 1000px 0; }
}
.mc-skeleton {
  background: linear-gradient(90deg, #f1f5f9 0%, #e2e8f0 50%, #f1f5f9 100%);
  background-size: 1000px 100%;
  animation: mc-shimmer 1.5s linear infinite;
  border-radius: 8px;
}
```

---

## 14. Uygulama Yol Haritası (Sayfa Bazlı)

### Faz 1 — Altyapı (1 saat)
- `components.css`'e §13'teki değişkenler + skeleton CSS
- `base.html`'e Chart.js defaults (script bloğu)
- Var olan toast/SweetAlert konum standardını uygula

### Faz 2 — Exec sayfalar (öncelik: üst yönetim odaklı)
| # | Sayfa | Mevcut durum | Tahmini efor |
|---|---|---|---|
| 1 | **Exec Dashboard** | Yeni, iyi ama 6 KPI tile rengi çok | XS — sadece renk + spacing rafine |
| 2 | **SP Index (hub)** | Modern ama tipografi karışık | S — başlık hiyerarşisi + boşluk |
| 3 | **Masaüstü** | Eski stil | M — yeniden tasarım |
| 4 | **Çeyreklik Review** | Yeni ama hero yok | S — hero kart ekle + grafikleştir |
| 5 | **Initiatives liste** | Pembe vurgu fazla | XS — renk paletine çek |

### Faz 3 — Operasyonel sayfalar
| # | Sayfa | Tahmini efor |
|---|---|---|
| 6 | **Süreç Karne** | L — 2936 satır CSS, dikkatli yenileme |
| 7 | **Bireysel Karne** | M — orta efor |
| 8 | **Proje List/Detail** | XS — zaten modern, rafine |
| 9 | **K-Radar Hub** | XS — zaten modern |
| 10 | **Login** | XS — sadece tipografi |

### Faz 4 — Cila (mikro etkileşim, transition, animasyon)
- Tüm sayfalarda skeleton loading
- Hover efektleri standardı
- Page transitions (gerekirse)

---

## Sözleşme

Bu kılavuz **yaşayan belge**. Bir kural pratikte işlemiyorsa burada güncellenir, sonra kod değişir. Tersi değil.

Bir sayfa modernize edildiğinde commit mesajında belirt:
```
ui(sp): exec dashboard kılavuz v1.0'a uyumlu
```

Bu kılavuza uygunluğu olmayan değişiklikler kod review'da reddedilir.
