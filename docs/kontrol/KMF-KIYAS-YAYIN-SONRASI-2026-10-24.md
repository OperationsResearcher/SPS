# Kıyas: Kayseri Model Fabrika — ÖNCE `kokpitim_yayin_oncesi2` (alembic bi01c4e5f6a7) ↔ SONRA `kokpitim_yayin_sonrasi` (alembic mg01a2b3c4d5)

**SONUÇ: ✅ KAYIP YOK** — toplam satır önce 22227 → sonra 23608


## 🟠 Beklenmeyen değerler değişmiş (İNCELE)

| Tablo.kolon | Satır | Örnek (pk: önce → sonra) |
|---|---:|---|
| `process_kpis.process_id` | 23 | 1006833: '61' → '1008995'; 1006859: '58' → '1008959'; 1006866: '58' → '1008992' |
| `process_kpis.sub_strategy_id` | 8 | 1006833: '127' → '1009672'; 1006835: '127' → '1009672'; 1006840: '127' → '1009651' |
| `process_kpis.is_active` | 8 | 1006846: 'true' → 'false'; 1006854: 'true' → 'false'; 1006845: 'true' → 'false' |

## 🟡 Eklenen satırlar (canlı kullanımdan olabilir)

| Tablo | Eklenen |
|---|---:|
| `individual_performance_indicators` | 103 |
| `process_activities` | 6 |
| `process_kpis` | 786 |
| `process_sub_strategy_links` | 246 |
| `processes` | 66 |
| `strategies` | 36 |
| `sub_strategies` | 126 |
| `swot_analyses` | 6 |
| `tows_analyses` | 6 |

## 🟢 Beklenen (migration kaynaklı) değişimler

| Tablo.kolon | Satır | Sebep |
|---|---:|---|
| `kpi_data.process_kpi_id` | 791 | Faz 1.5: ölçüm yılın PG kopyasına yeniden bağlanır (kayıp değil) |
| `plan_years.template_source_id` | 6 | Faz 1.2: clone zinciri şablon yılını işaretler |
| `process_activities.plan_year_id` | 2 | yılbazlı backfill (a1f2/yb16): NULL -> kurumun plan yılı |
| `process_kpis.is_included` | 15 | Faz 1.4: kpi_year_configs.is_included=false varlığa taşınır (K15) |
| `process_kpis.plan_year_id` | 146 | yılbazlı backfill (a1f2/yb16): NULL -> kurumun plan yılı |
| `process_sub_strategy_links.plan_year_id` | 38 | yılbazlı backfill (a1f2/yb16): NULL -> kurumun plan yılı |
| `processes.plan_year_id` | 11 | yılbazlı backfill (a1f2/yb16): NULL -> kurumun plan yılı |
| `strategies.plan_year_id` | 6 | yılbazlı backfill (a1f2/yb16): NULL -> kurumun plan yılı |
| `sub_strategies.plan_year_id` | 21 | yılbazlı backfill (a1f2/yb16): NULL -> kurumun plan yılı |

## ℹ Yeni kolonlar (SONRA'da var)

`users`: session_version

## ⚠ FK'siz bağlantı uyarıları (ÖNCE / SONRA)

- `kokpitim_yayin_oncesi2`: `notifications.user_id` → `users`: 7760 satır kapanım dışı
- `kokpitim_yayin_sonrasi`: `notifications.user_id` → `users`: 7760 satır kapanım dışı
