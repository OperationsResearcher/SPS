# EFQM K4 plan notu — Sürdürülebilir Değer Yaratma (iç 100 · ağırlık 200)

> Karar: 2026-08-05 · Yol **A** · Dal: `claude/efqm-k1`
> Motor: `app/services/efqm_assessment.py` · Önceki: `EFQM-K3-PLAN.md`

## Kararlar

| # | Konu | Karar |
|---|---|---|
| Yol | RADAR matrisi | Yok — A: proxy; EFQM ağırlığı 200 (iç skor 0–100) |
| 4.1 | Değer tasarımı | Strateji–süreç/girişim **hizası** (BSC değil) |
| 4.4 | Ölçüm | **A:** veri girilen PG (BSC yok — kullanıcı doluluğu düşük) |
| BSC | | K4’te kullanılmaz |

## Puan dağılımı (iç toplam 100)

| Alt | Max | Hesap |
|---|---|---|
| **4.1** Hiza | 30 | süreç–`process_sub_strategy_links` oranı ×15 + girişim `strategy_id` dolu oranı ×15 |
| **4.2** Portföy | 25 | min(1, aktif girişim / 10) × 25 |
| **4.3** Teslim | 25 | tamamlanan / aktif girişim × 25; girişim 0 → 0 |
| **4.4** Ölçüm | 20 | min(1, veri girilen PG / 30) × 20 |

## Sınır

Hiza/portföy/teslim/ölçüm yapı kanıtı; sürdürülebilir değer kalitesi veya RADAR Approach değil.

## Dokunulmayan

K5–K7 · KD11 hub
