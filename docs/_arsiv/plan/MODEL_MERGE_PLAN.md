# Model Birleştirme Planı (Dalga B2)

> Durum: Planlama | Runtime `from models` yalnızca `app/models/*_legacy.py` shim'lerinde

## Mevcut tablo haritası

| Legacy (`models/`) | Canonical (`app/models/`) | Birleştirme |
|--------------------|---------------------------|-------------|
| `LegacyUser` (`user`) | `core.User` (`users`) | Orta — iki tablo; login `core.User`, main legacy `LegacyUser` |
| `Kurum` | `core.Tenant` | Düşük — `tenant_id` synonym |
| `AnaStrateji` / `AltStrateji` | `core.Strategy` / `SubStrategy` | Yüksek — plan_year klonlama |
| `Surec` | `process.Process` | ✅ Alias mevcut |
| `Project` | `portfolio_project.Project` | ✅ Tamamlandı |
| `IndividualKpiData` | `process.IndividualKpiData` | Düşük — aynı mantık, tek tablo adı |

## Fazlar

1. **B2.1** — Tüm runtime import'lar `legacy_bridge` veya `app.models.*` (✅ Dalga B)
2. **B2.2** — Strateji: `AnaStrateji` okuma/yazma dual-write veya tek seferlik migrasyon
3. **B2.3** — Kullanıcı: yeni kayıtlar yalnızca `users`; `user` tablosu salt okunur
4. **B2.4** — `models/` paketi yalnızca Alembic/seed için

## Kabul kriteri

- CI `check_no_raw_models_import.py` geçer
- `legacy_bridge` içinde doğrudan `from models` yok (shim dosyalarına taşındı)
