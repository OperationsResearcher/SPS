# KalDer ↔ ana proje: karne/skor motoru (P10) — TAŞINDI (2026-10-24, kullanıcı kararı)

İlk kıyasta (aynı gün, sabah) iki fark bulunmuş ve rakamı değiştireceği için bilerek taşınmamıştı. Kullanıcı
"tek kaynak olsun" dedi; ikisi de taşındı.

| Konu | Önce | Şimdi |
|---|---|---|
| Puan sözleşmesi (`achievement`, `hesapla_basari_puani`) | ana projede zaten vardı | `docs/kontrol/PUAN-SOZLESMESI.md` belgelendi |
| Başarı yüzdesi | `surec.js computeKpiYearlyMetrics` istemcide `Math.min/round(...*100)` | yüzde yalnız sunucu `achievement` alanından (`score_engine_service`); istemci yalnız sunucu yıl özeti yoksa görüntü için ortalamaya düşer |
| Sapma formülü | `muda_analyzer`, `process_deviation_service`, `services/notification_service` her biri kendi formülü | tek yardımcı `score_engine_service.adverse_deviation_pct(actual, target, direction)` |

## Davranış değişiklikleri (kurumların gördüğü rakamlar)
- **Hedef ≤ 0:** sapma/uyarı hesabı artık yapılmaz (`None`); `achievement` ile aynı kural. Eskiden hedef < 0 için anlamsız oran üretilebiliyordu.
- **Yön:** `Decreasing` için sapma `(gerçek − hedef)/hedef`, `Increasing` için `(hedef − gerçek)/hedef`; uyarılarda gösterilen "Sapma: %x" artık hep **olumsuz yönde** pozitif sayı (eskiden mutlak değer).
- **İstemci yüzdesi:** karne ekranındaki başarı yüzdesi sunucu puanıyla birebir aynı; eskiden istemci Toplama/Son Değer yöntemlerini ve negatif değerleri (istemci negatif yüzde üretiyordu) farklı ele alıyordu → bazı PG'lerde ekran yüzdesi değişebilir.

## Koruma
`tests/test_sapma_formulleri.py`, `tests/test_basari_yuzdesi_sunucu.py` (istemcide yüzde formülü geri gelirse kırılır), `tests/test_puan_sozlesmesi.py`.

## Yayın öncesi
Test ortamında gerçek kurum verisiyle karne ekranı ve uyarı bildirimleri önce/sonra kıyaslanmalı (rakam farkı beklenir, ama açıklanabilir olmalı).
