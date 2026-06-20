# Bileşen Görünürlük Kalıbı (modül-içi paket gating)

> 2026-06-20. "67 bileşen sızıntısı" sorununun sistematik çözümü.

## Sorun
Route-düzeyi gating (`before_request` / `@require_module`) bir **modülün tamamını**
açar/kapatır. Ama bazı sayfalar açık olmalı (örn. `/kurum` — kimlik orada) **içindeki
bir bileşen** kapalı olmalı (örn. PG özet kartları L1'de görünmemeli).

## Çözüm: `component_visible(slug)` Jinja helper'ı
`app/__init__.py::_inject_component_visibility` context processor. Kullanıcının
paketindeki **modüllerin bileşenleri** (paket → modül → `component_slug` zinciri)
arasında slug var mı bakar. `require_component` decorator'ı ile **aynı kaynak**.

- Yalnız platform **Admin** bypass; kurum rolleri pakete tabi.
- Paketsiz / hata → `True` döner (fail-open, mevcut davranışı bozmaz).

## Kullanım (template)
```jinja
{% if component_visible('surec_performansi_karti') %}
  <!-- PG / süreç özet kartları, grafikleri -->
{% endif %}
```

## Bileşen slug'ları nereden?
`module_component_slugs` tablosu (paket yönetim sayfasında `/admin/packages` →
"Modüller" → her modülün bileşen önizlemesi). Mevcut PG/süreç slug'ları:
- `performans_gostergesi`, `performans_gostergesi_verisi` (PGV)
- `surec_performansi_karti`, `surec_verimlilik_analizi_karti`
- `surec_faaliyetleri`, `surec_faaliyetlerim_karti`
- `performans_trend_analizi_karti`

Yeni slug eklemek: `/admin/packages` veya doğrudan `module_component_slugs`'a satır.

## Uygulanan yerler
- ✅ `/kurum` — Süreç/PG özet bloğu (`surec_performansi_karti`)

## Uygulanacaklar (kademeli — sızıntı yüzeyi)
Aynı kalıpla sar: exec-dashboard PG kartları, masaüstü süreç widget'ları, raporlar
PG bölümleri vb. Her birinde doğru `component_slug`'u seçip `{% if component_visible(...) %}`
ile sarmak yeterli. Liste: PG/PGV gösteren ~67 bileşen (TASKLOG TASK-196 notu).

## Derinlik notu
Bu **template-düzeyi** gizleme (kart render edilmez → veri de gösterilmez). İleri
optimizasyon: route/servis de bileşen-farkında olup PG'yi hiç **hesaplamasın**
(performans). Şu an servis hesaplıyor, sadece kart gizli. Derin güvenlik (doğrudan
API çağrısı) için ayrı `@require_component` decorator'ı route'a eklenebilir.
