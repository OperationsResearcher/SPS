# EFQM K6 plan notu — Paydaş Algıları (iç 100 · ağırlık 200)

> Karar: 2026-08-05 · Yol **A** · Dal: `claude/efqm-k1`
> Motor: `app/services/efqm_assessment.py` · Önceki: `EFQM-K5-PLAN.md`

## Kararlar

| # | Konu | Karar |
|---|---|---|
| Yol | RADAR matrisi | Yok — A: proxy; EFQM ağırlığı 200 |
| BSC | | **Kullanılmaz** |
| Sabit baz | | **Yok** — anket yoksa 0 |
| Kaynak | | `stakeholder_surveys` |
| Skor ölçeği | | 0–100 (ortalama / 100) |
| Tip tavanı | | 4 distinct `stakeholder_type` |

## Puan dağılımı (iç toplam 100)

| Alt | Max | Hesap |
|---|---|---|
| **6.1** Algı kapsamı | 35 | distinct tip / 4 × 35 |
| **6.2** Algı skoru | 40 | skoru dolu anket ort. / 100 × 40; skor yok → 0 |
| **6.3** Dinleme derinliği | 25 | min(1, anket / 5) × 25 |

## K3.3 ayrımı

K3.3 = dinleme varlığı (anket/3). K6 = algı sonucu (tip + skor + derinlik/5).

## Sınır

Anket kaydı = algı proxy’si; resmî EFQM perception matrix değil.

## Dokunulmayan

K7 · KD11 hub
