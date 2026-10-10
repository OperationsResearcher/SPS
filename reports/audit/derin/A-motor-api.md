# Tek Hesap Motoru — API (Dalga 3, adım 1)

Kaynak: `app/services/score_engine_service.py` (imzalar dosya başı docstring'inde). Testler: `tests/test_dalga3_motor.py`.
Ekranlar sonraki adımda BU fonksiyonlara bağlanacak; kendi hesap yolu yazılmaz.

## Genel API
| Fonksiyon | Dönüş |
|---|---|
| `calculate_kpi_score(kpi_id, plan_year_id, as_of=None)` | `float 0-100` veya `None` (ölçülmedi / dahil değil / puanlanamadı) |
| `calculate_kpi_detail(kpi_id, plan_year_id, as_of=None)` | `{score, actual, target, direction, method, weight, is_included, entry_count}` — Karne/Score-detail için yıllık özet |
| `calculate_process_score(process_id, plan_year_id, as_of=None)` | `float` veya `None` (0 DEĞİL). Tenant bütünü hesaplanır (bir çağrı = bir tenant geçişi; toplu ekranlarda `compute_process_scores_internal` tercih edilsin) |
| `get_pg_scores_from_kpi_data(tenant, year, as_of, plan_year, cfg_map=None)` | `{pg_id: skor|None}` (toplu) |
| `compute_process_scores_internal(...)` / `compute_vision_score(...)` | mevcut toplu uçlar, aynı çekirdek |

`as_of=None` → `today_tr()`. `plan_year_id` zorunlu: yıllık config (hedef, yön, yöntem, ağırlık, `is_included`) buradan gelir.

## Saf fonksiyonlar (ekranlar/JS karşılığı bunları kullanmalı)
- `parse_tr_number(s)` — SERBEST METİN girişi (form/Excel). `,` ondalık; `.` yalnız geçerli binlik (`[1-9]\d{0,2}(\.\d{3})+`). `98.75`, `0.125`, `1.2.3`, `1,234.5` → `None` (reddet, kullanıcıya hata göster). `%`, `₺`, `TL`, `$`, `€`, boşluk atılır.
- `_parse_float(val)` — DB'de SAKLI değer okuyucu. Kanonik `x.y` doğrudan float (Türkçe yorumlanmaz), aksi halde `parse_tr_number`.
  Ölçüm (yerel PG, SELECT): aktif `kpi_data.actual_value` 366.668; `.` içeren 365.922; kanonik `x.y` 365.921; 3-haneli belirsiz 0; TR binlik 1 (`₺100.070.853`); virgüllü 7. Veri düzeltmesi gerekmiyor.
  Yazma tarafı sonraki adımda: kaydederken `parse_tr_number` → `str(float)` kanonik saklanmalı.
- `achievement(actual, target, direction)` — tek yön/oran kuralı (`compute_pg_score` bunun eski ad sarmalayıcısı). Azalan+actual≤0 → 100; azalan+hedef 0 → actual≤0?100:0; artan+hedef 0 → None; **hedef<0 → None** (A-011).
- `normalize_direction`, `normalize_aggregation_method` (AVG/SUM/LAST; AVG, Ortalama, ortalama, SUM, Toplama, toplam, Son Değer…), `aggregate_actuals`.
- `weighted_average([(skor|None, ağırlık|None)])` — ağırlıkları dağıt+normalize, None paydan düşer (A-005).
- `period_start(...)`, `entry_in_scope(entry, as_of)` — tarih kesimi (A-007): dönemin ilk günü (veya data_date) `as_of`'u geçmediyse dahil.

## Davranış kararları
- A-001: tüm alt süreç/PG ölçülmemiş → `None`. Çocuklu sürecin kendi PG'leri: **çocuk bloğu ile kendi-PG bloğu eşit (50/50)** ortalanır; biri yoksa diğeri.
- A-002: yıllık `is_included=False` PG dışlanır; ağırlık `cfg.weight` (yoksa `ProcessKpi.weight`).
- A-004 (`karne_hesaplamalar.hesapla_basari_puani`): bant boşluğunda uydurma 3 yerine değerin altındaki en yakın bandın puanı; alt bant yoksa `None`. Gerekçe: tam sayı bantlarda ondalık gerçekleşen bir alt banda aittir (99.5 → `80-99` bandı).
- A-005 (`hesapla_agirlikli_basari_puani`): ağırlık her zaman yüzde, her zaman `/100`.
- Soft delete: PG, Process, KpiData sorguları `is_active=True`; pasif PG için `calculate_kpi_*` → `None`.

## Henüz BAĞLANMADI (sonraki adım)
Karne API (`routes_karne.py`), `process_health_service`, `k_rapor`, `surec.js` Kanban, EFQM K7.1, legacy `services/score_engine_service.py`, `process_performance_service`, harici API `POST /api/v1/kpi-data` ve `calculated_score` persist (A-016) eski yollarını kullanıyor.
