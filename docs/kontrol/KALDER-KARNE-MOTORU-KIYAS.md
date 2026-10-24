# KalDer ↔ ana proje: karne/skor motoru kıyası (P10, 2026-10-24)

KalDer'in karne testleri ana projede koşuldu; **hesaplama sonuçlarını değiştireceği için hiçbir şey TAŞINMADI**.

| Konu | KalDer | Ana proje | Sonuç |
|---|---|---|---|
| Puan sözleşmesi (`achievement`, `hesapla_basari_puani`; `test_puan_sozlesmesi`) | Faz 1.1/1.2 | var | **3/3 geçti** — ana projede zaten sağlanıyor |
| Başarı yüzdesi yalnız sunucudan (`test_basari_yuzdesi_sunucu`) | Faz 1.1 | sunucu tarafı var | 9/10 geçti; **`surec.js computeKpiYearlyMetrics` hâlâ istemcide `Math.min/round(...*100)`** (xfail) |
| Ortak sapma formülü `adverse_deviation_pct` (`test_sapma_formulleri`) | Faz 1.3 (`d7cfac6`) | **yok** | `muda_analyzer.py`, `process_deviation_service.py`, `services/notification_service.py` kendi formülünü kullanıyor |

## Neden taşınmadı
Her iki fark da kurumların ekranda/uyarıda gördüğü **rakamı** değiştirebilir (istemci yüzdesi negatif üretiyordu, sınır durumlar; sapma formülü hedef ≤ 0 ve yön konusunda farklı davranır). Bu bir kod uyarlaması değil iş kararı: hangi hesap "doğru" kabul edilecek.

## Karar gerekirse nasıl taşınır
1. `adverse_deviation_pct`: KalDer `d7cfac6` → `app/services/score_engine_service.py` (+20 satır) ve 3 çağıran (`git -C C:\projeler\KalDer show d7cfac6`).
2. İstemci yüzdesi: KalDer `3a2a7ff` → `surec.js`'te `k.achievement` kullan; sonra `test_basari_yuzdesi_sunucu` xfail kaldırılır.
Her ikisi için önce Test'te mevcut kurum verisiyle önce/sonra karne kıyası alınmalı (`docs/ekim2026/kiyas*` araçları).
