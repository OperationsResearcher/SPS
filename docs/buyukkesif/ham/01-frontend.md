# HAM BULGU — Frontend Denetimi

> Kaynak: paralel frontend uzmanı taraması · 88 JS (22.559 satır) + 167 şablon (25.051 satır)
> Tarih: 2026-07-21 · **Her bulgu ana oturumda yeniden doğrulandı** (aşağıda ✅/❌ ile işaretli)

---

## F1 — Karne yıl seçici standart kullanıcıda sessizce yanlış yıl gösteriyor ✅ DOĞRULANDI

`ui/static/platform/js/surec.js:2940` · **KRİTİK**

Karne sayfasındaki yıl seçici `POST /k-plan/strategy/api/plan-years/set-active` çağırıyor.
Bu uç `@sp_manage_required` ile korunuyor → standart kullanıcı **403** alır.

```js
await fetch("/k-plan/strategy/api/plan-years/set-active", {...});
} catch (e) { /* aktif yıl yazılamadıysa devam et */ }
```

`fetch` 403'te **reddedilmez, çözümlenir** → `catch` hiç tetiklenmez. Akış devam eder,
sayfa yeni yıl URL'sine gider ama `session["sp_active_year"]` **eski yılda kalır**.

**Sonuç:** Aynı ekranda iki farklı yıl. Karne 2025 gösterir, üst bar ve diğer kartlar 2026.
Test yöneticiyle yapıldığı için görünmez.

**Çözüm:** Tek satır — uç `/api/view-year` ile değiştirilsin (yalnız `@login_required`).
Bu uç zaten bu iş için yazıldı (`topbar_year.js:11-12` tuzağı belgeliyor) ama surec.js güncellenmedi.

---

## F2 — Yönetim panelinde saklı XSS, yetki yükseltme vektörü ✅ DOĞRULANDI + SÖMÜRÜLEBİLİR

`ui/static/platform/js/yonetim_paneli.js:164-168` · **KRİTİK**

```js
var userName = item.user_name || t("Bilinmiyor");
tr.innerHTML = "<td>" + (item.resource_icon || "📌") + "</td>" +
               "<td>" + (item.resource_type || "-") + "</td>" +
               "<td>" + userName + "</td>" + ...
```

Aynı dosyada `_esc()` **tanımlı ve satır 78'de kullanılıyor** — bu tabloda atlanmış.
4 alan kaçırılmıyor: `user_name`, `resource_type`, `action_label`, `resource_icon`.

### Sömürü zinciri (ana oturumda uçtan uca doğrulandı)

| # | Adım | Kanıt |
|---|---|---|
| 1 | Kullanıcı kendi profilinden adını değiştirir | `micro/modules/shared/auth/routes.py:57` |
| 2 | Sunucuda HTML temizliği **YOK** — sadece `.strip()` | aynı satır; `bleach`/`sanitize` kullanımı: **0** |
| 3 | Ad, denetim kaydı tablosunda `innerHTML` ile basılır | `yonetim_paneli.js:164` |
| 4 | Script, paneli açan **yöneticinin** oturumunda çalışır | — |

`first_name` = `varchar(64)`, kullanıcı kontrolünde. Düşük yetkili kullanıcıdan yöneticiye
yetki yükseltme. Çok kiracılı sistemde etki alanı geniş.

**Çözüm:** 4 alanı `_esc()` ile sar (tek satırlık). Ayrıca sunucu tarafında ad alanlarına
temizlik eklenmesi önerilir — savunmanın tek katmanda olması yeterli değil.

---

## F3 — Üç ayrı yıl seçici, aynı session anahtarını farklı uçlardan yazıyor ✅

`base.html:409` · `surec/index.html:42` · `surec/karne.html:105` · **YÜKSEK**

| Seçici | Uç | Yetki | Yıl yoksa |
|---|---|---|---|
| `#topbar-year-select` | `/api/view-year` | `login_required` | **404** |
| `#surec-plan-year-select` | `.../set-active` | `sp_manage_required` | **yeni yıl OLUŞTURUR** |
| `#year-select` (karne) | `.../set-active` | `sp_manage_required` | yeni yıl oluşturur |

Aynı jest, seçiciye göre farklı sonuç. Karne sayfasında üst üste **iki** yıl seçici görünüyor.

**Çözüm:** Sayfa içi seçiciler kaldırılıp tek global üst bar seçicisine indirgensin
(`topbar_year.js:3-8`'in belgelediği tasarım niyeti). Kaldırılamıyorsa hepsi `/api/view-year`'a bağlansın.

---

## F4 — Yıl seçici verinin çoğunu filtrelemiyor: S8 yarım kaldı ✅

`app/services/date_sovereign.py` + 20 route noktası · **YÜKSEK**

S8 kararı "backend session'a düşsün" idi. Ama fallback yalnız `resolve_request_year()`
**çağıran** route'larda çalışıyor:

| Ölçüm | Sayı |
|---|---|
| `?year=` gönderen JS dosyası | 9 / 88 |
| `resolve_request_year()` kullanan route dosyası | 15 |
| Hâlâ `date.today().year` kullanan nokta (`micro/`) | **20** |

Örnekler: `sp/routes_pages.py:169`, `sp/routes_donemler.py:66`, `masaustu/routes.py:320`,
`bireysel/routes.py:83`, `k_rapor/routes.py:122`

**Sonuç:** Kullanıcı 2025'e geçer; bazı kartlar 2025, bazıları sessizce 2026 gösterir.
Yıl bazlı sistemde bu **yanlış karar** demektir.

**Çözüm:** 20 noktayı `resolve_request_year()` ile değiştir + CI'da `date.today().year`
için grep yasağı (aksi halde tekrar birikir).

---

## F5 — Gizlenen ikinci yıl seçici için ölü kod duruyor ✅

`surec/karne.html:300` · `surec.js:205-207, 3138-3155` · **ORTA**

Element `hidden aria-hidden="true" tabindex="-1"` — `change` olayı **asla ateşlenemez**,
ama 17 satırlık dinleyici hâlâ bağlı. `syncPgKarneYilFromBanner()` görünmez bir `<select>`'i
senkronda tutuyor.

Zararsız ama yanıltıcı: kodu okuyan bir sonraki geliştirici çalışan mekanizma sanır.
**Çözüm:** ~25 satır silinsin.

---

## F6 — İki dosyada hata yönetimi olmayan fetch · ORTA

`reports/nlp_query.js` (3 fetch) · `sp_projeler.js` (2 fetch) — ne `.catch` ne `try`.
Ağ kesintisinde ekran donuk kalır, kullanıcı hata görmez.

> Bu alan genel olarak **iyi**: 88 dosyanın 86'sında hata yönetimi var.

---

## F7 — Ön taramanın "11 alert ihlali" bulgusu yanlıştı ❗ DÜZELTME

9'u SweetAlert2 yüklenmediğinde devreye giren **savunma yedeği** — iyi mühendislik:

```js
if (typeof Swal !== "undefined") { Swal.fire({...}); } else { alert(msg); }
```

**Gerçek ihlal 2 nokta:** `admin/sub_tenants.html:393` ve `:412` — koşulsuz `confirm()`,
üstelik aynı dosyada `Swal.fire` zaten kullanılıyor.

---

## F8 — Ön taramanın "19 Jinja-in-JS" bulgusu da yanlıştı ❗ DÜZELTME

18'i kuralın **kendisini alıntılayan yorum satırı**, 1'i JSDoc dönüş tipi.
**Gerçek ihlal: SIFIR.** Bu kural tam uygulanmış.

---

## F9 — 52 şablonda inline `<script>`, yoğunluk 6 dosyada · ORTA

| Dosya | Inline JS satırı |
|---|---|
| `sp/exec_dashboard.html` | 563 |
| `sp/strateji_haritasi.html` | 422 |
| `sp/tv.html` | 415 |
| `sp/okr.html` | 288 |
| `admin/hata_kontrolu.html` | 279 |
| `platform/base.html` | 254 |

Inline script **önbelleğe alınmaz** — `exec_dashboard.html` her açılışta ~20KB fazladan taşıyor.
CSP sıkılaştırması da bu dosyalar yüzünden engelleniyor.

**Çözüm:** İlk 5'i taşı — dosya sayısının %10'u, satırların ~%40'ı.
`base.html` istisna kalabilir (i18n sözlüğü sunucudan gelmeli).

---

## F10 — `esc()` fonksiyonu 36 dosyada birebir kopyalanmış · ORTA

Aynı SweetAlert toast kalıbı da 27 dosyada 32 kez tekrarlıyor.

> **F2'deki XSS tam olarak bu yüzden oluştu:** paylaşılan yardımcı olmadığı için her dosya
> kendi kaçışını taşıyor, biri atlanınca kimse fark etmiyor.

**Çözüm:** `app.js`'e `window.esc()` konsolide edilsin (`showAppToast` zaten var).

---

## F11 — Kesme işareti (`'`) kaçış listesinde yok · ORTA

Tüm `esc` uygulamaları `& < > "` kaçırıyor, **`'` kaçırmıyor**. `yonetim_paneli.js:78`
tek tırnaklı öznitelik kullanıyor → değer kaçırılmış olsa da öznitelikten çıkılabilir.

Bugün sömürülebilir değil (alan sunucu kontrollü) ama tek satırlık değişiklikle olur.

---

## F12 — Kanban durumu yalnız renkle taşınıyor · ORTA (erişilebilirlik)

`surec/karne.html:365,373,381,451,459,467` — durum noktaları `aria-hidden="true"`,
anlam yalnızca CSS renginde. `hedefte`(yeşil) / `risk`(sarı) / `disi`(kırmızı).

Kırmızı-yeşil renk körlüğü (**erkeklerin ~%8'i**) en kritik ayrımı yapamaz.
Yazdırma çıktısı gri tonlamada okunamaz. WCAG 1.4.1 ihlali.

---

## F13 — Yeni eklenen `topbar_year.js` çeviriden geçmiyor · DÜŞÜK

`topbar_year.js:53` → `var metin = mesaj || "Yıl değiştirilemedi.";`

`window.t()` yardımcısı var (`base.html:30`) ama kullanılmamış. İngilizce arayüzde
Türkçe çıkar. *(Bu, bu oturumda eklenen kod — i18n disiplinini bozuyor.)*

Aynı sorun: `app.js`, `bildirim.js`, `kurum_ayarlar.js`, `ayarlar_eposta.js`.

---

## F14 — Yıl değişiminde tam sayfa yenileme · DÜŞÜK

`topbar_year.js:43` → `window.location.reload()`. Kaydırma konumu, açık akordeonlar,
doldurulmuş form alanları kaybolur.

Bilinçli karar (yorumda belgeli) ama `sessionStorage` ile kaydırma konumu korunabilir — 5 satır.

---

## F15 — `pg_tablo_modal.js` başlık satırları kaçırılmadan basılıyor · DÜŞÜK

`:306, :317` → `thead.innerHTML = row1;` — `escHtml` dosyada mevcut ama kullanılmamış.
Bugün sunucu kontrollü; dönem adları kullanıcı tanımlı olursa XSS.

---

# UX / GÖRSEL İYİLEŞTİRME ÖNERİLERİ

**1. Geçmiş yıl uyarı şeridi** — Kullanıcı içinde bulunulan yıldan başkasına geçince üst
barın altında ince şerit: *"2024 verilerini görüntülüyorsunuz — bugüne dön"*. Mühürlü yılda
🔒 + "salt okunur" ibaresi eklenirse K8 kuralı ekranda görünür olur.

**2. Kanban noktalarına şekil kodlaması** — ● / ▲ / ■. Renk körü kullanıcılar için
erişilebilirlik, herkes için hızlı tarama (göz şekli renkten çabuk ayırır).

**3. Trend grafiğinde hedef çizgisi** — `karne.html:258` yalnız gerçekleşeni gösteriyor.
Hedef kesikli çizgi + tolerans bandı eklenirse "hedefte miyiz" sorusu bakar bakmaz cevaplanır.

**4. İskelet ekran tutarlılığı** — `yonetim_paneli.js:44` güzel bir iskelet uygulaması
içeriyor ama yalnız orada. Ortak yardımcıya çıkarılsın; algılanan hız artar, düzen kayması önlenir.

**5. Boş durumlara eylem çağrısı** — `karne.html:388` *"Henüz performans göstergesi
eklenmemiş."* diyor, kullanıcıyı çıkmazda bırakıyor. "PG ekle" butonu yanına konsun.
