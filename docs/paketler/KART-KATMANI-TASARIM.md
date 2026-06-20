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
1. **Yetkisiz veri → satır/alan düşer** (kart kalır). Komple gizleme YOK.
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
