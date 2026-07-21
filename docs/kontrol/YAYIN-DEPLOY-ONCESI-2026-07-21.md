# Yayın deploy öncesi kontrol — 2026-07-21

> Kırmızı çizgi ritüeli (KURALLAR §8.1 + REHBER §0.2): deploy ÖNCESİ veri sayımları.
> Deploy: `dbbe2ce` (TASK-245/246/247) → `c65cb5dd` (TASK-279 dahil, 109 commit).
> Şema: `f6a7b8c9d0e1` → `yb20c5e1a8d3` (9 migration, tek head, zincir doğrulandı).

## Deploy öncesi Yayın sayımları (2026-07-21, sudo -u postgres psql)

| Tablo | Yayın | Yerel | Not |
|---|---|---|---|
| tenants | 13 | 13 | ✅ eşit |
| users | 452 | 452 | ✅ eşit |
| system_modules | 13 | 13 | ✅ |
| subscription_packages | 4 | 4 | ✅ |
| package_modules | 30 | 30 | ✅ |
| module_component_slugs | 122 | 122 | ✅ |
| system_cards | 483 | 501 | Yayın'da 18 eksik → deploy sonrası kart keşfi + seed |
| system_cards (dolu description) | 480 | 489 | satır bazında yakın; İÇERİK farkı sayılamaz (K-Radar zenginleştirme yerel-only) |
| bsc_kpi_perspectives | 840 | 840 | ✅ |
| kpi_data | 366.684 | 366.571 | Yayın 113 FAZLA — canlı müşteri girişi, NORMAL. Yayın canonical, DOKUNULMAZ |
| process_kpis | 1.399 | 2.399 | Yerelde 1.000 fazla — KMF yerel verisi; Yayın'a İTİLMEZ (veri yönü kuralı §8.6) |
| tablo sayısı (public) | 169 | 170 | +1 = yeni migration'larla gelecek (plan_years vb.) |

## Veri dönüştüren migration riski (§6.5)

- `f0aa4591b689` — kpi_data numeric ayna kolonları: ADDITIVE, ham kolonlar korunur, backfill SQL.
- `e9669efe440c` — period_type normalize + orphan user_id NULL: UPDATE-only, satır silmez,
  kullanıcı onaylı (2026-07-15).
- İkisi de yereldeki Yayın-kopyası veri (2026-07-15 çekimi + KMF mutabakatı) üzerinde koştu,
  760 test yeşil, Test ortamı bugün bu şemayla sıfırdan kuruldu ve sağlıklı.

## Yedek

- `oracle_safe_deploy.sh` deploy başında PG dump alır (`/opt/kokpitim/backups/`).
- Ek güvence: bugünkü Test kurulumu için alınan yerel dump + Yayın'ın kendi backups dizini.

---

## SONUÇ — deploy sonrası (2026-07-21, aynı gün)

- **Yedek alındı:** `/opt/kokpitim/backups/pg_kokpitim_db_full_20260721_191702.sql.gz`
- **Kod:** Yayın `c65cb5dd` — container içi `tenant_guard.py` md5 = repo blob md5 birebir
  (yerel working-tree farkı yalnız CRLF).
- **Şema:** 9 migration temiz koştu → `yb20c5e1a8d3`. Backfill: actual 366.684 dolu / 18
  indirgenemedi; target 366.348 / 146 indirgenemedi (beklenen iş kuralı). 202 orphan user_id
  NULL'a çekildi, period_type normalize, FK validated=True / orphan=0.
- **Satır sayıları:** script doğrulaması "değişmedi" ✅
- **Health:** `127.0.0.1:5000/health` 200 + `https://www.kokpitim.com/health` 200
  (script sonundaki nginx-80 404'ü bilinen yanıltıcı kontrol).
- **Kart keşfi:** 18 yeni `k_radar_*` kartı eklendi → 501. `seed_yonetim_ozeti_kartlari.py`
  koştu (9 YO kartı meta).
- **system_cards nihai doğrulama:** 501 kart / 489 dolu açıklama / 12 boş — boş listesi
  yerelle birebir aynı; **code+description+short_id toplu md5 Yayın=Yerel eşit**
  (`08277fbbf3aad6c2d4cf29cd7a401a57`).
- **DÜZELTME (aynı gün):** "K-Radar zenginleştirme içeriği Yayın'da tam" ifadesi YANLIŞTI.
  md5 eşitliği doğru ama iki taraf da TEMEL açıklamaları taşıyor (max 361 krk, kolon
  varchar(512)). Zengin içerik (97 kart, ort. 582 krk) yalnızca merge edilmemiş
  `claude/k-radar-kp-sayfa-tasarim` dalının seed dosyalarında — hiçbir ortam DB'sinde değil.
  Bkz. devir notu: `git show ed1f0845:docs/kontrol/KART-ACIKLAMA-DEVIR.md`.
