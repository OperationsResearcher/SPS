# Legacy / Platform Route Envanteri

> Otomatik üretim: `python scripts/dev/inventory_legacy_routes.py`
> Tarih: otomatik

| Katman | Dosya sayısı (py) | Route sayısı | Not |
|--------|-------------------|--------------|-----|
| Legacy main | 3 | 159 | `main_bp` |
| Legacy api | 3 | 96 | `api_bp` |
| Legacy auth | 2 | 11 | `auth_bp` |
| Legacy admin | 1 | 2 | `admin_bp` |
| Legacy app/routes | 8 | 84 | `çeşitli` |
| Platform micro | 70 | 329 | `app_bp` |

**Özet:** Legacy ~352 route, Platform (micro) ~329 route.

## Öncelik

1. Yeni özellikler yalnızca `micro/modules/` + `ui/templates/platform/`.
2. Legacy `main/` / `api/` yalnızca bakım; yeni endpoint eklenmez.
3. Kök `app/routes/process.py` ile `micro/modules/surec/` örtüşmesi — süreç API tekilleştirme fazı.

## Çift-model çift-veri borcu (2026-06-16)

Sayım envanterinin ötesinde, **aynı kavramın legacy + modern iki ayrı tabloda senkronsuz tutulduğu**
somut çakışmalar tespit edildi (Vizyon/Misyon, Ana/Alt Strateji, Değerler, Etik, Kalite, Süreç/PG).
Kullanıcı semptomu: `/kurum` ile `/sp` farklı Vizyon/Misyon gösteriyor.

→ Tam teşhis, kavram-bazlı harita ve faz planı: [`CIFT-MODEL-BORCU-KURUMSAL-KIMLIK.md`](CIFT-MODEL-BORCU-KURUMSAL-KIMLIK.md)
→ Bu konsolidasyon, L1 paketinin KOE ölçümü için **ön koşul**.
