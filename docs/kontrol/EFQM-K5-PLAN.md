# EFQM K5 plan notu — Performans ve Dönüşüme Yön Verme (100)

> Karar: 2026-08-05 · Yol **A** · Dal: `claude/efqm-k1`
> Motor: `app/services/efqm_assessment.py` · Önceki: `EFQM-K4-PLAN.md`

## Kararlar

| # | Konu | Karar |
|---|---|---|
| Yol | RADAR matrisi | Yok — A: proxy; EFQM ağırlığı 100 |
| Boş risk / boş faaliyet | | **0 puan** (sistem yokluğu ödüllenmez) |
| 5.3 | maturity/A3 | Kullanılır — derinlik (K2.4 binary var/yok) |
| 5.1 vs K4.4 | | Oran vs mutlak PG sayısı |

## Puan dağılımı (toplam 100)

| Alt | Max | Hesap |
|---|---|---|
| **5.1** Performans izleme | 25 | (veri girilen PG / aktif PG) × 25; PG 0 → 0 |
| **5.2** Risk sistemi | 30 | min(1, risk/5)×15 + (1 − kritik/toplam)×15; risk 0 → 0 |
| **5.3** Dönüşüm | 25 | in_progress girişim/5 ×15 + (maturity+A3)/3 ×10 |
| **5.4** Operasyon disiplini | 20 | faaliyet >0 ise gecikme cezası ×20; faaliyet 0 → 0 |

## Sınır

Yönetişim/operasyon proxy; RADAR Approach değil. Boş kayıt = eksik sistem, mükemmel skor değil.

## Dokunulmayan

K6–K7 · KD11 hub
