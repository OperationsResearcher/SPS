# SONRAKİ İŞLER — Yıl Bazlı Programdan Sonra

> **Bu liste birikiyor.** Yıl bazlı iş bitmeden bu maddelere dokunulmaz.
> Kullanıcı "planlamayı yapmak adına" bu konuları şimdiden bildiriyor.
>
> Açılış: 2026-07-20

---

## Neden ayrı liste

Yıl bazlı program (`HASAR-TESPITI.md` + `MIMARI-KARAR.md`) tek bir hedefe odaklı:
sistemin tamamını yıl eksenine oturtmak. Bu liste, o iş sürerken tespit edilen
ama **kapsam dışı** kalan işleri tutar — böylece ne unutulur, ne de asıl işi böler.

---

## İ1 — "Kurum Paneli" isim/bilgi mimarisi karmaşası

**Bildiren:** Kullanıcı, 2026-07-20
**Tür:** UI / bilgi mimarisi · **Boyut:** Küçük · **Risk:** Düşük

### Sorun
Kullanıcı üç ayrı yerde "Kurum Paneli" görüyor ve karışıyor.

### Tespit (kod denetimi)
Kodda üçü de **farklı isimde** — karmaşa etiketten değil, **ikon ve kavram
örtüşmesinden** geliyor:

| # | Konum | Etiket (kodda) | URL | İçerik | Kaynak |
|---|---|---|---|---|---|
| 1 | Sidebar → **Girdi** | "Kurum Paneli" | `/organization` | Kurum kimliği, stratejik kimlik | `ui/templates/platform/base.html:151` |
| 2 | Sidebar → **Yönetim** | "Kurumlar" | `/admin/tenants` | Platform admin — tüm kurum listesi | `ui/templates/platform/base.html:284` |
| 3 | SP menü | "Yönetici Paneli" | `/k-plan/strategy/exec-dashboard` | Stratejik sağlık, özet panel | `ui/templates/platform/sp/menu.html:26` |

**Dördüncü görünüm noktası:** `micro/core/module_registry.py:38` — launcher
ekranında modül adı `_("Kurum Paneli")`, açıklama *"Stratejik kimlik, kurum
bilgileri ve strateji yönetimi"*.

### Kök neden
1. **#1 ve #2 aynı ikonu kullanıyor** — `fa-building` 🏢. Sidebar'da iki farklı
   başlık altında aynı bina ikonu → göz onları eşleştiriyor.
2. **#3 kavramsal olarak #1'e yakın** — adı "Yönetici Paneli" ama kurumun genel
   durumunu gösteriyor.
3. Kod yorumu ikiliği zaten itiraf ediyor (`module_registry.py:35-36`):
   > *"Katman mimarisi: KATMAN DIŞI bırakıldı (bilinçli). Kurum kimliği hem girdi
   > hem yönetim niteliği taşıdığı için /k-plan öneki verilmedi."*

Bilinçli bir kararın kullanıcıya karmaşa olarak yansıması.

### Öneri (onaylanmadı)

| # | Yeni ad | Gerekçe |
|---|---|---|
| 1 | **"Kurum Kimliği"** / "Kurum Bilgileri" | İçeriği bu — vizyon/misyon/kimlik girdisi |
| 2 | "Kurumlar" (kalsın) + **farklı ikon** (`fa-city` / `fa-sitemap`) | Zaten doğru adlandırılmış, ayrışması gereken ikon |
| 3 | "Yönetici Paneli" (kalsın) | Zaten farklı ad taşıyor |

### Dikkat
`.po` dosyalarına dokunulmalı (`msgid "Kurum Paneli"`), yoksa EN arayüzde eski
ad kalır. KURALLAR-MASTER §5.1: açıklama değişince `.po` + `compile` adımı
atlanmaz.

---

---

## İ2 — Kart açıklama zenginleştirme (YARIM KALDI, devam edecek)

**Bildiren:** Kullanıcı, 2026-07-20 ("eski oturumdan yarım kalan kart işi")
**Tür:** İçerik üretimi · **Boyut:** Büyük (405 kart) · **Risk:** Düşük

> **Devir belgesi hazır ve kapsamlı:** `docs/kontrol/KART-ACIKLAMA-DEVIR.md`
> (commit `ed1f0845`, dal `main`). **"Devam" denildiğinde ÖNCE O DOSYA OKUNUR** —
> sıfırdan keşif gerekmez, devam yordamı adım adım yazılı.

### Nerede kalındı

| | |
|---|---|
| Tamamlanan | K-Radar pilotu **97/97 kart** |
| **Kalan** | **405 kart** (501 toplam − 96 zengin) |
| K-Radar ortalaması | 67 → **582 karakter** |
| Katalog ortalaması | 87 → **189 karakter** |
| Son commit | `4a1a0bcc` — dal `claude/k-radar-kp-sayfa-tasarim` |
| Merge/push | **YAPILMADI** — kullanıcı onayı bekliyor |

### Kalan iş — modül bazında (önerilen sıra)

| Modül | Kart | Mevcut ort. | Not |
|---|---|---|---|
| `raporlar` | **94** | 49 krk | **En kötü** — çoğu `"X — rapor kartı."` şablon dolgusu |
| `sp` | 83 | 87 krk | Literatür ağırlıklı, K-Radar'a en yakın — hazır malzeme var |
| `admin` | 83 | 74 krk | |
| `project` | 21 | 90 krk | |
| `bireysel` | 14 | 68 krk | |
| `process` | 13 | 135 krk | |
| `yonetim` | 9 | 142 krk | |
| `ayarlar`/`kurum`/`auth` | 6+6+6 | ~90 krk | |
| `masaustu` + dağınık | ~70 | — | |

**Sıra:** `raporlar` → `sp` → `admin` → `project` → `bireysel` → kalanlar

### Kurulmuş altyapı — YENİDEN YAPMA (hepsi commit'li, çalışıyor)

1. **Şema:** `system_cards.description` `varchar(512)` → `Text`
   (migration `391945351814`)
2. **Modal:** `base.html` → `renderInfoBody()` — düz metni yapılandırılmış basar
   (`Başlık:` → kalın etiket, boş satır → paragraf, `- ` → madde). XSS-güvenli.
3. **Seed:** `scripts/seed_card_descriptions.py` — idempotent, kontrol modu
   varsayılan, `--sadece <önek>` filtresi var. İçerik
   `scripts/seed_data/card_descriptions_*.py` kalıbından otomatik toplanır.

### Yazım sözleşmesi — BAĞLAYICI
Bölüm sırası: tanım → `Hesap:` → `Sınır:` → `Eşik:` → `Yorum:` → `Kaynak:`

Üç kural: **(1)** Uydurma yok — formül koddan, literatür web'den doğrulanır.
**(2)** Şeffaflık zorunlu — gösterge adı ile gerçekte ölçülen ayrışıyorsa
`Sınır:`'da açıkça yazılır. **(3)** Düz metin — DB'de markdown yok, biçimi modal
verir (i18n zinciri bu sayede bozulmuyor).

⚠️ **SWOT atıf tuzağı:** "Albert Humphrey / SRI" atfını **KULLANMA** — Puyt, Lie &
Wilderom (2023) çürüttü. Güvenli ifade: *"1960'larda SRI'da SOFT yöntemi olarak
geliştirildi."*

### Deploy durumu
- Yerel: **uygulandı** (97 kart + migration)
- Test / Demo / Yayın: **hiçbiri uygulanmadı**
- Taşırken **sıra kritik**: önce `flask db upgrade` (Text migration), sonra
  `seed_card_descriptions.py --calistir`. Migration koşmadan seed → 512 sınırı hatası.
- Seed kod deploy'uyla otomatik çalışmaz (bilinen açık)

---

## İ3 — D0: 438 gösterge TERS hesaplanıyor ⚠️ KRİTİK

**Kaynak:** Kart açıklama işi sırasında bulundu · **Tür:** Hesaplama hatası
**Boyut:** Küçük (3 satır) · **Risk:** **YÜKSEK — yanlış rapor**

> Tam liste: `docs/kontrol/KART-VERI-TUTARSIZLIKLARI.md` (öncelik sıralı)

### Sorun
`micro/modules/k_rapor/routes.py` satır **991, 1901, 2161**:

```python
if kpi.direction == "lower_is_better":   # ← DB'de bu değer HİÇ YOK
```

**Ölçüm (2026-07-20):** `Increasing`=956 · `Decreasing`=**438** ·
`lower_is_better`=**0**

Koşul hiçbir zaman doğru olmuyor → **438 "azalması iyi" gösterge, artması iyiymiş
gibi hesaplanıyor.**

### Somut etki
Hedefi 5 olan hata oranı 2 ölçüldüğünde **%40** görünüyor; doğrusu **%100**.
**İyi performans kötü raporlanıyor.**

Skor motoru (`compute_pg_score`) doğru değeri kullandığı için **aynı gösterge
Kurumsal sekmesinde farklı, PG Dağılım sekmesinde farklı yüzde gösteriyor.**

### Durum
Düzeltme **3 satır**, ama rapor rakamlarını değiştireceği için **kullanıcı onayı
bekliyor**. Düzeltmeden önce/sonra birkaç göstergenin yüzdesi elle doğrulanmalı.

> **Not:** Bu madde yıl bazlı işten bağımsız ama onunla **kesişiyor** — her ikisi
> de rapor doğruluğunu etkiliyor. Yıl bazlı iş raporlara dokunacağı için, D0'ı o
> sırada birlikte düzeltmek mantıklı olabilir. Kullanıcı kararı.

---

## İ4 — _(bekleniyor)_

<!--
Her yeni madde bu formatta eklenir:

## İn — Başlık
**Bildiren:** kim, tarih · **Tür:** · **Boyut:** · **Risk:**
### Sorun
### Tespit
### Öneri
-->
