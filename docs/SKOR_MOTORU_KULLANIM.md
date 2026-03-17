# Skor Motoru – Projede Uygulama

SKOR_MOTORU_CEVAP.xml mimarisi projede uygulanmıştır. Vizyon puanı hesaplama mantığı **tüm hiyerarşide aktif**tir.

## Veritabanı modelleri (güncel)

- **AnaStrateji**: `weight` (Float, 0–100)
- **AltStrateji**: `weight` (Float, 0–100)
- **Surec**: `weight` (Float, 0–100)
- **SurecPerformansGostergesi**: `weight`, `calculated_score` (Float)
- **SurecFaaliyet**: `surec_pg_id` (FK → SurecPerformansGostergesi)

Migration (bir kez çalıştırın):

```bash
python scripts/migrate_score_engine_schema.py
```

## Servis: score_engine_service.py

- `compute_pg_score(hedef, gerceklesen, direction)` → PG başarı puanı (0–100)
- `get_pg_representative_data(kurum_id, as_of_date)` → PG bazında son veri
- `compute_vision_score(kurum_id, as_of_date, persist_pg_scores)` → Vizyon puanı + tüm hiyerarşi skorları
- `recalc_on_pg_data_change(kurum_id, as_of_date)` → PG verisi değişince tüm hiyerarşiyi yeniden hesaplar
- `recalc_on_faaliyet_change(surec_pg_id, kurum_id)` → Faaliyet güncellenince bağlı PG üzerinden recalc

## Vizyon puanı ne zaman hesaplanır (aktif tetikleyiciler)

1. **PG verisi kaydedildiğinde** – `POST /surec/<surec_id>/karne/kaydet` → `recalc_on_pg_data_change(kurum_id)`
2. **PG verisi güncellendiğinde** – `PUT /pg-veri/guncelle/<veri_id>` → `recalc_on_pg_data_change(kurum_id)`
3. **Faaliyet güncellendiğinde** – `POST /surec/<surec_id>/faaliyet/<faaliyet_id>/update` → `recalc_on_faaliyet_change(surec_pg_id, kurum_id)`
4. **Manuel yeniden hesaplama** – `POST /api/vision-score/recalc` → tüm hiyerarşi + PG `calculated_score` güncellenir

## API uç noktaları

| Metot | Endpoint | Açıklama |
|-------|----------|----------|
| GET | `/api/vision-score?as_of_date=YYYY-MM-DD&persist=1` | Point-in-time vizyon puanı; `persist=1` ile PG skorları kalıcı güncellenir |
| POST | `/api/vision-score/recalc` | Tüm hiyerarşide vizyon puanını yeniden hesapla ve PG `calculated_score` güncelle |

## Hiyerarşi akışı

PG verisi → PG skoru (0–100) → Süreç puanı (ağırlıklı) → Alt Strateji (StrategyProcessMatrix) → Ana Strateji → **Vizyon puanı (0–100)**. Ağırlık atanmamış kayıtlar için varsayılan: **Eşit dağılım** (100 / kardeş sayısı).
