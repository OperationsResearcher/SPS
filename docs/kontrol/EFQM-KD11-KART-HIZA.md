# EFQM KD11 kart ↔ modal hizası

> Karar: 2026-08-05 · Dal: `claude/efqm-k1`

## Önce

| Alan | Kart (sahte) | Modal |
|---|---|---|
| Kriter | `strategy_count//2` | gerçek 7 kriter |
| Hazırlık | KS skor + 10 | `compute_efqm_assessment` 0–1000 |

## Sonra

Tek motor: `compute_efqm_assessment` → `summarize_efqm_for_card`

| Kart alanı | Kaynak |
|---|---|
| `criterion_coverage` | skoru > 0 kriter sayısı (0–7) |
| `readiness_score` | `total_points / 10` → 0–100 |
| `total_points` | badge (…/1000) |

Route: `/k-radar/api/ks/efqm` plan yılı ile özet.
`get_ks_extended_data["efqm"]` aynı helper (plan yılı yok).
