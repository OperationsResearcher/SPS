# Yayın deploy öncesi kontrol — 2026-07-24

> Kırmızı çizgi ritüeli (KURALLAR §8.1 + REHBER §0.2 / §0.7).
> Hedef: `c65cb5dd` / şema `yb20c5e1a8d3` → `main` `46133796` / şema `hd01a2b3c4d5`.
> İçerik: kart 501/501 seed + hesap paketi (D1/D2/D3/T1/DIR/G1/SEM etiket) + Text migration.

## 4 katman — eksik listesi (deploy ÖNCESİ)

| Katman | Yayın şimdi | Hedef | Aksiyon |
|---|---|---|---|
| **Kod** | `c65cb5dd` | `46133796` | `oracle_safe_deploy` git pull + build |
| **Şema** | `yb20c5e1a8d3` · `description` = varchar | `hd01a2b3c4d5` (üstünde `391945351814` Text) + `risk_heatmap_items.project_id` | Alembic upgrade (2 migration) |
| **Veri** | aşağı tablo | canlı veri korunur | satır sayısı doğrulama; Yerel KMF **itilmez** |
| **Tek-seferlik** | açıklama ort. **85** krk | ort. ~464 (501 zengin) | `seed_card_descriptions.py --calistir` (Text migration SONRASI) |

## Deploy öncesi Yayın sayımları

| Tablo | Yayın | Yerel | Not |
|---|---|---|---|
| tenants | 13 | 13 | ✅ |
| users | 452 | 452 | ✅ |
| processes | 380 | 518 | Yerel fazla (KMF vb.) — Yayın'a itilmez |
| process_kpis | 1399 | 2399 | Yerel fazla — itilmez |
| kpi_data | 366684 | 366571 | Yayın fazla (canlı giriş) — NORMAL |
| process_activities | 3 | 14 | |
| strategies | 197 | 294 | |
| sub_strategies | 507 | 754 | |
| project | 1 | 22 | |
| task | 0 | 63 | |
| system_cards | 501 | 501 | ✅ sayı; **içerik** seed ile gelecek |

## Riskler

- Text migration olmadan seed → varchar truncation.
- `oracle_safe_deploy.sh` PG yedek + satır sayısı kilidi zorunlu.
- Bilinçli açık (bu deploy'da YOK): SEM backfill, İ1 kalan isim≠ölçüm.

## Akış

1. Test sıfırdan (bağlayıcı: Yerel → Test → Yayın)
2. Yayın: §3 yedek + `oracle_safe_deploy.sh`
3. Yayın: `seed_card_descriptions.py --calistir`
4. Health + satır sayısı + description ort. doğrula

---

## SONUÇ — 2026-07-24

| | |
|---|---|
| **Yedek** | `/opt/kokpitim/backups/pg_kokpitim_db_full_20260723_224634.sql.gz` |
| **Kod** | Yayın `46133796` |
| **Şema** | `yb20c5e1a8d3` → `391945351814` (Text) → `hd01a2b3c4d5` (G1) |
| **Satır sayıları** | script: değişmedi ✅ |
| **Seed** | 501 kart güncellendi; ort. **464**; tip `text`; `project_id` var |
| **Health** | `:5000` 200 + `www.kokpitim.com/health` 200 |
| **Test** | sıfırdan OK (health 200, ort. 464, `hd01a2b3c4d5`) |
| **Redis** | Yayın'da yok (bilinen uyarı; SimpleCache) |
