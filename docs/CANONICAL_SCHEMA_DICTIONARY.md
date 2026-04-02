# Canonical Schema Dictionary

Bu doküman hard-migration sonrası tek isim standardını tanımlar.

## Kanonik Fiziksel Tablolar

- Kurum/Kullanıcı: `tenants`, `users`, `roles`
- Süreç: `processes`, `process_kpis`, `process_activities`, `kpi_data`, `kpi_data_audits`
- Bireysel: `individual_performance_indicators`, `individual_activities`, `individual_kpi_data`, `individual_kpi_data_audits`
- Proje: `project`, `task` (bu fazda singular korunur)

## Legacy -> Canonical

- `surec` -> `processes`
- `surec_performans_gostergesi` -> `process_kpis`
- `bireysel_performans_gostergesi` -> `individual_performance_indicators`
- `bireysel_faaliyet` -> `individual_activities`
- `performans_gosterge_veri` -> `kpi_data` / `individual_kpi_data` (ayrım kuralı migration dosyasında)

## Deterministic Ayrım Kuralı (`performans_gosterge_veri`)

- `bireysel_pg_id` doluysa -> `individual_kpi_data`
- `surec_pg_id` doluysa -> `kpi_data`
- İkisi de doluysa öncelik: `individual_kpi_data` ve olay loguna conflict notu
- İkisi de boşsa satır `kpi_data`'ya düşer ve `migration_notes` alanına `orphan_source_row` notu eklenir (alan yoksa migration logunda tutulur)

## Kod Standardı

- Yeni kodda legacy tablo adları kullanılmaz.
- Yeni kodda `app.models.*` ve `app.constants.canonical_schema` referans alınır.
