# KART Katmanı + Kart-İçi Veri Paket-Farkındalığı — Tasarım

> 2026-06-20. Kullanıcı ile mutabakat. SaaS paket hiyerarşisinin en alt katmanı + asıl zor kısım.

## 4 Katmanlı Hiyerarşi

```
PAKET     subscription_packages   (L1/L2/L3/L4...)        [VAR — 4]
  └ MODÜL   system_modules         (Süreç, K-Radar...)     [VAR — 13]
      └ BİLEŞEN system_components   (Süreç Karnesi...)      [VAR — 35]
          └ KART  system_cards     (KPI kartı, Trend...)   [YENİ]
```

Bağ tabloları: `package_modules` (paket↔modül), `module_component_slugs` (modül↔bileşen).
Her seviyede: **gör / yer değiştir (sira) / içerik düzenle** — admin UI'dan.

## Asıl Zor Kısım: Kart-İçi Veri Paket-Farkındalığı

Bir kart, verisini **farklı bileşen/modül/paketlerden** çekebilir. Kullanıcının
paketinde **olmayan** veri parçası karttan **düşer** (kart kalır, sadece kendi paket
verisi görünür). Kart komple gizlenmez — kısmi çalışır.

**Örnek:** "Stratejik Sağlık Karnesi" kartı
| Veri parçası | Gerektirdiği bileşen | L1 müşterisi |
|---|---|---|
| strateji_skoru | strateji_netligi (L1) | ✓ görür |
| pgv_kapsami | performans_gostergesi_verisi (L2) | ✗ satır düşer |

## Yeni Modeller

### SystemCard (KART)
- `id, name, code (unique), component_id (FK→system_components), sira, is_active`
- `sira`: yer değiştirme için.

### CardDataSource (KART-VERİ → PAKET eşlemesi) — kritik
- `id, card_id (FK→system_cards)`
- `data_key`: kartın içindeki veri parçası adı (örn "pgv_kapsami")
- `required_component_code`: bu verinin gerektirdiği bileşen (NULL = kartın kendi bileşeni)
- `label`: UI'da görünen ad (opsiyonel)

## Kararlar (kullanıcı, 2026-06-20)
1. ~~**Yetkisiz veri → satır/alan düşer** (kart kalır). Komple gizleme YOK.~~
   **REVİZE (kullanıcı onayı, 2026-07-08): Kart-düzeyi KOMPLE gizleme VAR.**
   Paket dışı kartın tamamı gizlenir. Mekanizma:
   - Zincir: `SystemCard.component_id → SystemComponent.code (= component_slug) → paket modülleri`
     (DB doğrulaması 2026-07-08: 699 kartın 672'sinde component_id dolu, 553'ünde zincir tam;
     167 slug'ın tamamı SystemComponent.code ile birebir eşleşiyor — ek kolon/migration GEREKMEDİ).
   - Merkezî uygulama: `cards-meta` API yanıtındaki `hidden` listesi + `base.html` JS
     (`enforceHidden`) — 343+ template'e tek tek dokunmadan tüm kartlar kapsanır,
     MutationObserver ile AJAX kartları dahil.
   - Server-side: `{% if card_visible('kod') %}` helper'ı da mevcut (app/__init__.py) —
     kritik kartlarda progressive sertleştirme için.
   - Fail-open + Admin bypass deseni korunur (component_visible ile aynı):
     zinciri olmayan kart / hiçbir modüle atanmamış component → görünür.
   - NOT: JS gizleme derin güvenlik değildir; veri güvenliği route-düzeyi
     `require_component`/`require_module` decorator'larının işidir (ayrı iş, değişmedi).
   Veri-satırı düşürme (`card_data_visible`) mekanizması da geçerliliğini korur —
   iki mekanizma birlikte çalışır (kart komple paket dışıysa gizle; kart açık ama
   içindeki tek veri parçası üst pakete aitse satır düşer).
2. **Yönetim DB-tabanlı + admin UI** (4 katman gör/taşı/düzenle).
3. **Kart keşfi otomatik** — template/koddan taranır, admin'den **tekrar tetiklenebilir**
   (kullanmayı bırakıp tekrar aktif edilebilir; RouteRegistry sync felsefesi).
4. **Veri-kaynak eşlemesi DB'de** (CardDataSource), admin UI'dan yönetilir.

## Enforcement Mekanizması
- Template helper: `card_data_visible(card_code, data_key)` → bool.
  CardDataSource'tan `required_component_code` okunur; `component_visible()` ile kontrol.
- Render: her veri satırı `{% if card_data_visible('saglik_karnesi','pgv_kapsami') %}`.
- Platform Admin bypass; fail-open (eşleme yoksa göster).

## Fazlar
1. ✅ Modeller + migration (SystemCard, CardDataSource)
2. Otomatik kart keşfi (seed + admin tetikleyici)
3. card_data_visible helper + 1 örnek kartta kanıt (sağlık karnesi)
4. Admin UI: 4 katman ağacı + kart/veri yönetimi

## İlişki: mevcut altyapı
- `component_visible(slug)` helper'ı (BILESEN-GORUNURLUK-KALIBI.md) bu sistemin
  bileşen-düzeyi atası; card_data_visible onun kart-veri düzeyi uzantısı.
- `route_registry.component_slug` + `admin_components_sync` = keşif felsefesi örneği.

---

## 🎴 KART GÖRSEL STANDARDI — ZORUNLU (2026-06-21, kullanıcı mutabakatı)

> **Bağlayıcı.** Bundan sonra **yeni veya değiştirilen HER kart** bu yapıda olmalı.
> Mekanizma `ui/templates/platform/base.html` içinde merkezîdir — kart sadece
> doğru işaretlenirse standart otomatik uygulanır.

### Başlık satırı düzeni
```
[mini ikon]  Kart Başlığı  (i)                         [ KART ID ]
└─ solda ───────────────────┘                          └─ sağ üst köşe ─┘
   herkese görünür                                       yalnız sistem Admin
```

| Öğe | Konum | Kim görür | Kaynak |
|-----|-------|-----------|--------|
| **Mini ikon** | Başlığın solunda | Herkes | Template'te FontAwesome (`<i class="fas fa-...">`) — konuyla ilgili |
| **Kart Başlığı** | İkonun sağında | Herkes | Template başlık metni (`mc-card-title` / `mc-stat-label`) |
| **(i) bilgi butonu** | Başlığın hemen sağında, normal kelime-arası boşlukla | **Herkes** | JS otomatik ekler; tıkla → kartın amacı/içeriği (`system_cards.description`) modalde |
| **Kart ID (short_id)** | Kartın sağ üst köşesi | **Yalnız `role.name == 'Admin'`** | `system_cards.short_id` (2 harf + numara, örn. MA01) — salt gösterim, tıklanamaz |

### Bir kartı standarda sokmak için (geliştirici checklist)
1. Kart konteynerine **`data-card-code="<sayfa>.<kart>"`** ekle (örn. `data-card-code="sp.misyon"`).
2. Başlık elemanı **`mc-card-title`** veya **`mc-stat-label`** sınıfını taşısın (JS başlığı bununla bulur; yoksa (i) köşeye düşer).
   Başlık metni **Jinja `{{ _("...") }}`** ile yazılmalı — modal başlığı bu DOM metnini kullanır (bkz. §i18n).
3. Başlığın soluna konuyla ilgili **mini ikon** koy (`<i class="fas fa-...">`).
4. Admin'den **kart keşfi**ni tetikle (`/admin` → Kartları Keşfet) → kart `system_cards`'a yazılır.
5. Karta **kısa ID (short_id)** ata: `<HARF><numara>` (sayfa kısaltması + sıra).
6. **Açıklama (description)** yaz (admin UI'dan veya seed) → (i) bunu gösterir. **Zorunlu:** bu Türkçe metni
   `.po` kataloglarına (EN) msgid olarak ekleyip İngilizce çevirisini yaz (bkz. §i18n — aksi halde (i) modalı
   İngilizce seçilmiş dilde de Türkçe gösterir).

### (i) modal içeriği — i18n ZORUNLU (2026-07-01, kullanıcı mutabakatı)

> **Bağlayıcı.** (i) butonuyla açılan modal, hem **başlık** hem **açıklama** için aktif dile uymalıdır.
> Türkçe sabit metin EN seçiliyken görünmesi standart ihlalidir — TASLAK olarak bile bırakılmaz.

- **Modal başlığı**: backend'den ayrıca çekilmez — kartın DOM'daki zaten görünen başlığı (`mc-card-title` /
  `mc-stat-label`, adım 2'deki `{{ _() }}` metni) `base.html`'deki JS tarafından okunup modale taşınır.
  Geliştirici olarak yapman gereken TEK şey: başlığı Jinja `_()` ile yazmak. Ayrıca bir "name" alanı
  çevirmene gerek yok — `system_cards.name`/`code` teknik anahtardır (örn. `masaustu.bildirimler`),
  kullanıcıya **asla** gösterilmez.
- **Modal açıklaması**: `system_cards.description` DB'de Türkçe saklanır ama backend route'u
  (`admin_api_card_info`, `micro/modules/admin/routes.py`) `flask_babel.gettext` ile sarmalayıp döner.
  Bunun çalışması için o Türkçe açıklama metninin `translations/en/LC_MESSAGES/messages.po`'da
  msgid olarak bulunması ve çevrilmiş olması **şart** — DB'ye yeni açıklama yazınca otomatik pipeline'a
  girmez (kaynak dosya değil, runtime veri), bu yüzden elle/scriptle `.po`'ya eklenip
  `pybabel compile -d translations` ile derlenmesi gerekir.

### Sayfa → harf eşlemesi (short_id öneki)
| Sayfa | Harf | | Sayfa | Harf |
|-------|------|-|-------|------|
| masaustu | **MA** | | project | **PJ** |
| sp | **SP** | | k-rapor | **KR** |
| process | **PR** | | k-radar | **KD** |
| kurum | **KU** | | raporlar | **RP** |
| bireysel | **BR** | | | |

### Kart vurgu şeridi (sol kenar) — anlamlı, dekoratif değil
Standart kart **şeritsizdir** (düz `mc-card`). Sol renkli şerit yalnızca öne çıkan /
durum bildiren kartlarda kullanılır ve renk **anlam** taşır. İnline `border-left`
**YASAK** — `components.css`'teki modifier sınıfları kullanılır (tek kalınlık 4px):

| Sınıf | Anlam | Renk |
|-------|-------|------|
| `mc-card--accent-info` | bilgi / nötr vurgu | indigo |
| `mc-card--accent-success` | olumlu / skor / tamamlandı | yeşil |
| `mc-card--accent-warning` | dikkat / eksik veri | amber |
| `mc-card--accent-danger` | uyarı / risk / kritik | kırmızı |

Kullanım: `<div class="mc-card mc-card--accent-info">`. Renk token'larından (`--color-*`)
beslenir; rastgele hex kullanma. **Migrasyon borcu:** sitede ~34 dosyada eski inline
`border-left` var; kart kart geçerken bu sınıflara çevrilir (toplu değil, kademeli).

### Mekanizma notları (base.html)
- (i) → `GET /admin/api/card-info/<code>` (CSRF gerektirmez).
- short_id rozeti → `GET /admin/api/cards-meta?codes=a,b,c` (toplu, salt-okuma, **GET; POST CSRF'e takılır**).
- Dinamik (AJAX) gelen kartlar MutationObserver ile de yakalanır.
- **Tuzak:** Bu makinede Flask auto-reload güvenilmez → base.html/route değişince
  `python pybasla.py` ile **yeniden başlat**, yoksa tarayıcı eski JS'i görür.
