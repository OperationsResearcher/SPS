# KART SİSTEMİ — MİMARİ & OTORİTE BELGE

> **Tek gerçek kaynak.** Kart/sayfa/paket/modül/bileşen hiyerarşisi, DB şeması,
> görsel standart, mekanizma ve oturum davranışı. 2026-06-23'te DB+koddan doğrulanarak yazıldı.
> Bir şey değişince ÖNCE bu belge güncellenir. Bağlayıcı kurallar: CLAUDE.md + KURALLAR-MASTER.md §5.1.

---

## 0. OTURUM AÇILINCA NASIL DAVRANMALISIN (gelecek oturumlar için)

1. **Bu belgeyi oku.** Kart sistemiyle ilgili her iş bu mimariye uyar.
2. **DB'ye güven, ajana/hafızaya değil.** Kart/sayfa sayısı, alan, içerik için
   `test_client` veya doğrudan sorgu ile teyit et. Bu projede defalarca "yok" denen şey DB'de vardı.
3. **Template/route/base.html değişince `python pybasla.py` ile YENİDEN BAŞLAT.**
   Bu makinede Flask auto-reload güvenilmez; restart yapmazsan tarayıcı eski JS/HTML görür
   (bir keresinde 5 prompt bu yüzden boşa gitti).
4. **JS toplu-meta endpoint'leri GET olmalı** — POST CSRF'e takılır.
5. **Canlı veri üstünde upsert testi YAPMA** — sentetik veri + temizlik (Porter dersi).
6. **Yeni/değişen her kart KART GÖRSEL STANDARDI'na (bkz §4) uymalı.**
7. **main'e doğrudan commit YOK**; iş `claude/<konu>` dalında, kullanıcı onayıyla merge.
8. Tüm bu iş **YEREL** (127.0.0.1:5001, PostgreSQL). Push/deploy kullanıcı açıkça isteyince.

---

## 1. HİYERARŞİ (5 katman + sayfa)

```
PAKET        subscription_packages   (baslangic/yonetim/strateji + master)   [4]
  └ MODÜL     system_modules          (surec, kurum, sp, k_radar...)          [13]
      └ BİLEŞEN system_components      (performans_gostergesi, swot...)        [35]
          └ KART  system_cards        (masaustu.takvimim ...)                 [343]
              └ VERİ card_data_sources (data_key + required_component_code)   [3]

SAYFA        system_pages            (kart code prefix'i = sayfa)            [68]
             — kartlar code prefix'i ile sayfaya eşlenir (FK değil, prefix eşleşme)
```

Bağ tabloları: `package_modules` (paket↔modül M2M), `module_component_slugs` (modül↔bileşen).

---

## 2. DB TABLOLARI — TAM ŞEMA (2026-06-23 doğrulandı)

### subscription_packages  [4 kayıt]
`id` PK · `name` · `code` (unique) · `description` · `is_active`
Kayıtlar: master_package, baslangic (L1), yonetim (L2), strateji (L3).

### system_modules  [13]
`id` · `name` · `code` (unique) · `description` · `is_active`
relationship: `component_slugs` → ModuleComponentSlug; `packages` ← package_modules.

### system_components  [35]
`id` · `name` · `code` (unique) · `description` · `is_active`
Not: mevcut 35 "bileşen"in çoğu aslında kart-seviyesi isim (eski yapı kalıntısı).

### module_component_slugs  [35]  (ara tablo)
`module_id` PK+FK · `component_slug` PK (= RouteRegistry.component_slug / component code)

### package_modules  (ara tablo, M2M)
`package_id` PK+FK · `module_id` PK+FK

### system_cards  [343]  ← ANA TABLO
| alan | tip | açıklama |
|------|-----|----------|
| id | INTEGER PK | |
| name | VARCHAR(128) NOT NULL | insan-okur Türkçe başlık |
| code | VARCHAR(80) UNIQUE NOT NULL | **`<sayfa>.<kart>`** (örn. masaustu.takvimim) |
| short_id | VARCHAR(12) UNIQUE NULL | kısa kimlik (MA01, RP05) — admin görür |
| component_id | INTEGER FK→system_components NULL | bağlı bileşen (ondelete SET NULL) |
| sira | INTEGER | gösterim sırası (template'ler henüz uygulamıyor) |
| description | VARCHAR(512) NULL | (i) butonu bunu gösterir |
| is_active | BOOLEAN NOT NULL | soft delete |
relationship: `data_sources` → CardDataSource (cascade delete-orphan).

### card_data_sources  [3]  ← KART-İÇİ VERİ PAKET-FARKINDALIĞI
| alan | tip | açıklama |
|------|-----|----------|
| id | PK | |
| card_id | FK→system_cards (ondelete CASCADE) NOT NULL | |
| data_key | VARCHAR(120) NOT NULL | kart içindeki veri parçası anahtarı |
| required_component_code | VARCHAR(80) NULL | bu veri hangi bileşene/pakete tabi |
| label | VARCHAR(200) NULL | UI etiketi |
| is_active | BOOLEAN | |
Unique: (card_id, data_key). **Amaç:** kullanıcının paketinde olmayan veri parçası
karttan DÜŞER (kart kalır, kısmi gösterilir). Şu an sadece kanıt örneği (3 kayıt) dolu.

### system_pages  [68]  ← SAYFA KATALOĞU (yeni, 2026-06-23)
| alan | tip | açıklama |
|------|-----|----------|
| id | PK | |
| code | VARCHAR(80) UNIQUE NOT NULL | kart code prefix'i (örn. raporlar_cfo_dashboard) |
| name | VARCHAR(160) NOT NULL | sayfa adı |
| url | VARCHAR(255) NULL | sayfa URL'i |
| short_id | VARCHAR(16) UNIQUE NULL | modül-kısa (MA, RP-CD, KR-K) — admin görür |
| description | VARCHAR(512) NULL | |
| is_active | BOOLEAN | |

### route_registry  [81]  (kart sistemi değil — bileşen auto-discovery)
`id` · `endpoint` (unique) · `url_rule` · `methods` · `component_slug`

**Model dosyası:** `app/models/saas.py` (TÜM yukarıdaki sınıflar burada).

---

## 3. short_id ÖNEK SİSTEMİ

### Kart short_id (system_cards.short_id) — 2 harf + numara
| önek | modül | kart sayısı |
|------|-------|-------------|
| MA | masaüstü | 19 |
| SP | sp + strateji-haritasi | 19 |
| PR | process | 7 |
| PK | process karne | 13 |
| PJ | project | 8 |
| KD | k-radar (ks+kp) | 16 |
| KR | k-rapor (16 sekme) | 81 |
| RP | raporlar/* (38 sayfa) | 179 |
**Toplam: 343 kart** (342 short_id'li; kurum_ozet_kartlar=KU dahil).

### Sayfa short_id (system_pages.short_id) — modül-kısa
- Tekil modül: `MA`, `PR`, `PK`, `PJ`, `KU`
- Alt-sayfalı: `SP`, `SP-HRT`, `KD-KS`, `KD-KP`
- Sekme/sayfa bazlı: `KR-<tab kısaltma>` (KR-K, KR-FAA...), `RP-<sayfa kısaltma>` (RP-CD...)
- 68 sayfa.

---

## 4. KART GÖRSEL STANDARDI (ZORUNLU — her yeni/değişen kart)

Başlık satırı: **[mini ikon]  Kart Başlığı  (i)** solda · **Kart ID** sağ üst köşe.

| Öğe | Konum | Kim görür | Kaynak |
|-----|-------|-----------|--------|
| Mini ikon | başlık solu | herkes | template FontAwesome `<i class="fas fa-...">` |
| Başlık | ikon sağı | herkes | `mc-card-title` / `mc-stat-label` |
| **(i) butonu** | başlığın hemen sağında | **herkes** | JS otomatik; tıkla→description modal |
| **Kart ID (short_id)** | sağ üst köşe | **yalnız Admin** | salt gösterim, tıklanamaz |
| **Sayfa ID** | sayfa üstü orta | **yalnız Admin** | system_pages.short_id |

### Kart vurgu şeridi (sol kenar) — anlamlı
`components.css` modifier'ları (inline border-left YASAK):
`mc-card--accent-info` (mavi) · `--accent-success` (yeşil) · `--accent-warning` (amber) · `--accent-danger` (kırmızı).

### Bir kartı standarda sokmak (geliştirici checklist)
1. Kart konteynerine `data-card-code="<sayfa>.<kart>"` ekle.
2. Başlık `mc-card-title` veya `mc-stat-label` taşısın (yoksa (i) köşeye düşer).
3. Sol mini ikon koy.
4. **JS ile üretilen kartlar:** helper'a `code` parametresi ekle → `${code?` data-card-code="${code}"`:''}`.
   JS kartları keşifle BULUNMAZ → elle DB'ye yazılır.
5. Admin'den kart keşfi (`POST /admin/cards/discover`) → system_cards'a yazılır.
6. short_id ata (sayfa öneki + no) + description yaz.
7. `python pybasla.py` ile restart.

---

## 5. MEKANİZMA — base.html (merkezî)

Konum: `ui/templates/platform/base.html`, `{% if current_user.is_authenticated %}` bloğu (~satır 526+).
Sadece `current_user.role.name == 'Admin'` → `kk_is_admin`.

- **(i) butonu** → `place()` JS, `data-card-code`'lu her kartta. `findTitle()` ile başlık
  bulunur (iç içe kartlarda `closest("[data-card-code]")===el` ile torun başlığı atlanır → çift (i) önlenir).
- **Kart ID rozeti** → admin-only, köşede; short_id `cards-meta`'dan toplu dolar (`fillBadges`).
- **Sayfa ID rozeti** → `kk-page-badge`, admin-only, üst-orta; ilk data-card-code prefix'i →
  `loadPageBadge()` → page-meta API.
- **(i) modal** → `openInfo()` → card-info API'den description.
- **AJAX kartlar** → MutationObserver `place()` + `loadMeta()` çağırır (JS-üretilen kartlar yakalanır).

### API'ler (micro/modules/admin/routes.py)
| route | method | erişim | döner |
|-------|--------|--------|-------|
| `/admin/api/card-info/<code>` | GET | giriş yapan herkes | short_id, name, description |
| `/admin/api/cards-meta?codes=a,b` | GET (+POST) | herkes | {code:{short_id,name}} toplu |
| `/admin/api/page-meta/<code>` | GET | **yalnız Admin (403)** | sayfa short_id, name, url |
| `/admin/api/cards/<id>` | POST | Admin | kart düzenle (name/description/sira/component) |
| `/admin/cards/discover` | POST | Admin | template tara → system_cards seed |

**CSRF notu:** toplu meta GET'tir; POST CSRF token ister, JS'te GET kullanılır.

---

## 6. KEŞİF SERVİSİ (otomatik kart bulma)

`app/services/card_discovery_service.py` → `discover_cards(dry_run=False)`.
- `ui/templates/platform/**/*.html` tarar, `data-card-code="..."` yakalar.
- İdempotent upsert: var olan güncellenir, yeni eklenir, silinen işaret → is_active=False.
- **Sadece template tarar — JS dosyalarını TARAMAZ.** JS-üretilen kartlar elle DB'ye yazılır.
- Guard: `${`, `{{`, `}` içeren code'lar atlanır (JS/Jinja literal'i kart sanmasın diye).

---

## 7. MIGRATION ZİNCİRİ (kart sistemi)

```
c3d4e5f6a7b8  kart_katmani         → system_cards + card_data_sources
d4e5f6a7b8c9  kart_short_id        → system_cards.short_id
e5f6a7b8c9d0  system_pages         → system_pages tablosu
```
Migration komutu: `python -m flask db upgrade`. DB öncesi pg_dump şart (C:/pgdata/bin).

---

## 8. DOSYA HARİTASI

| Ne | Nerede |
|----|--------|
| Modeller | `app/models/saas.py` |
| Keşif servisi | `app/services/card_discovery_service.py` |
| API'ler | `micro/modules/admin/routes.py` (card-info, cards-meta, page-meta, cards/<id>, discover) |
| Merkezî (i)+rozet mekanizması | `ui/templates/platform/base.html` |
| Accent şerit CSS | `ui/static/platform/css/components.css` (.mc-card--accent-*) |
| Favori PG (masaüstü) | `micro/modules/masaustu/routes.py` + index.html |
| Karne dropdown fix | `micro/modules/surec/routes_process.py` (include_null=True) |
| Hiyerarşi rehberi modalı | `ui/templates/platform/_hierarchy_help.html` (2-kollu) |
| Kart envanteri (kaynak) | `docs/paketler/kart-kimlik-standardi.csv` (388 satır) |
| İlerleme/sayfa takibi | `docs/paketler/KART-STANDART-ILERLEME.md` |
| Görsel standart yordamı | `docs/paketler/KART-KATMANI-TASARIM.md` §Kart Görsel Standardı |
| Bu belge (mimari) | `docs/paketler/KART-SISTEMI-MIMARI.md` |

---

## 9. KAPSAM SINIRLARI (dürüst)

- **Template-düzeyi gizleme:** kart render edilmezse veri gösterilmez; servis/route hâlâ
  veriyi hesaplar (boşa). Derin güvenlik (doğrudan API) ayrı iş.
- **sira alanı var ama template'ler sıraya göre render etmiyor** (görsel sürükle-bırak yok).
- **card_data_sources** sadece kanıt örneği dolu (3 kayıt); kart-içi paket-farkındalığı
  gerçek kullanımda her karta veri-kaynağı tanımlamayı gerektirir.
- **Veri-instance / launcher kartları bilinçli atlandı** (kart standardı dışı, çünkü
  her tenant'ta farklı / menü öğesi): sektorel (8 sektör), ai-danisman (AI öneri içeriği),
  okr-cascade objective örnekleri, k-radar hub launcher kartları.
- **strateji-haritasi** /sp dünyasında (SP-HRT), CSV'de sp_ prefix.

---

## 10. NASIL KULLANILIR (kullanıcı senaryosu)

- **Herhangi bir kullanıcı:** kartın **(i)**'sine basar → kartın ne işe yaradığını okur.
- **Admin:** kartın sağ üstünde **kısa ID** (MA07), sayfanın üstünde **sayfa ID** (PR) görür.
  "Şu kartta sorun var: PR03" diyebilir; "PR sayfasında" diye sayfa referansı verebilir.
- **Geliştirici/Claude:** code prefix'inden hangi sayfa, short_id'den hangi kart olduğunu
  anında bulur; system_pages ile "bu sayfada kaç kart var" sorgular.
