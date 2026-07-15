# Legacy / Platform Route Envanteri

> Otomatik üretim: `python scripts/dev/inventory_legacy_routes.py`
> Üretim tarihi: 2026-07-15
>
> ⚠️ Bu dosya ELLE düzenlenmez — sayılar bayatlarsa script'i yeniden çalıştır.
> Çalışan uygulamadaki kanonik dağılım için `docs/SISTEM-HARITASI.md`'ye bak.

| Katman | Dosya sayısı (py) | Route sayısı | Not |
|--------|-------------------|--------------|-----|
| Legacy main | 8 | 96 | `main_bp` |
| Legacy api | 10 | 89 | `api_bp` |
| Legacy app/routes | 6 | 27 | `çeşitli` |
| Platform micro | 106 | 615 | `app_bp` |

**Özet:** Legacy ~212 route, Platform (micro) ~615 route → modern pay %74 (modern baskın ✅).

Strangler yönü: `micro/` büyür, legacy erir. Bu oran her ölçümde modern lehine
artmalı; azalıyorsa yeni iş yanlış katmana yazılıyor demektir.

## Öncelik

1. Yeni özellikler yalnızca `micro/modules/` + `ui/templates/platform/`.
2. Legacy `main/` / `api/` yalnızca bakım; yeni endpoint eklenmez.
3. `app/routes/process.py` 2026-07-15'te silindi (1806 satır ölü kod) —
   süreç yüzeyi artık tek: `micro/modules/surec/`.
