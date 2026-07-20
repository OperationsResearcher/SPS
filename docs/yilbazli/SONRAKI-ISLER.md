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

## İ2 — _(bekleniyor)_

<!--
Kullanıcı bugün başka konular da bildirecek.
Her yeni madde bu formatta eklenir:

## İn — Başlık
**Bildiren:** kim, tarih · **Tür:** · **Boyut:** · **Risk:**
### Sorun
### Tespit
### Öneri
-->
