# Hard Migration Inventory (Local)

## Tespit Edilen Çift Şema

- Legacy süreç tablosu ailesi:
  - `surec`
  - `surec_performans_gostergesi`
  - `bireysel_performans_gostergesi`
  - `bireysel_faaliyet`
  - `performans_gosterge_veri`
- Kanonik süreç tablosu ailesi:
  - `processes`
  - `process_kpis`
  - `individual_performance_indicators`
  - `individual_activities`
  - `kpi_data`
  - `individual_kpi_data`

## Tespit Edilen Proje Eksen Durumu

- Fiziksel tablo standardı: `project`, `task` (singular)
- Bu fazda singular korunmuştur; çoğul (`projects`, `tasks`) fiziksel rename yapılmamıştır.

## Kullanım Noktaları (Yüksek Riskli)

- `services/*` altında legacy model (`Surec`, `SurecPerformansGostergesi`, `PerformansGostergeVeri`) kullanım izleri vardır.
- `models/*` legacy paketinde legacy process tabloları doğrudan tanımlı.
- `app/models/*` kanonik paketinde micro process tabloları tanımlı.

## Risk Notu

- Hard migration sonrası legacy tablo adları fiziksel olarak kaldırılacağı için,
  legacy model kullanan servislerde runtime hata oluşur.
- Bu nedenle migration uygulanmadan önce servis katmanında kanonik modele geçiş tamamlanmalıdır.

## Bu Turda Yapılanlar

- Kanonik sözlük dosyası eklendi: `app/constants/canonical_schema.py`
- Hard migration dosyası eklendi: `migrations/versions/r7s8t9u0v001_hard_unify_legacy_process_tables.py`
- Admin backup özeti kanonik sözlükten beslenir hale getirildi.
