# Puan Sözleşmesi (karne / sapma)

> Faz 1.2 (A7). Kaynak: kod incelemesi, 2026-10-22. Kodda değişiklik olursa bu belge **önce** güncellenir.

Sistemde **iki ayrı puan ekseni** vardır. Karıştırılmamalı; bir ekrandaki sayı hangi eksenden geliyorsa
etiketinde (veya (i) açıklamasında) bu belirtilir.

| | **Eksen 1 — Başarı oranı** | **Eksen 2 — Başarı puanı (bant)** |
|---|---|---|
| Aralık | **0–100** (%), `None` = puanlanamadı | **1–5** tamsayı, `None` = bant tanımsız |
| Tek kaynak | `app/services/score_engine_service.achievement()` (`compute_pg_score` aynı) | `app/utils/karne_hesaplamalar.hesapla_basari_puani()` |
| Girdi | gerçekleşen, hedef, yön | gerçekleşen, PG'nin `basari_puani_araliklari` (1–5 aralık tablosu), yön |
| Kim tanımlar | Formül sabit | Aralıkları kurum/PG tanımlar (şube çekirdek PG'de kilitli alan) |
| Toplama | `weighted_average()` (ölçülmeyen paydan düşer) | `hesapla_agirlikli_basari_puani()` (ağırlık × puan) |

## Eksen 1 kuralları (`achievement`)
- Artan: `gerçek / hedef`. Azalan: `hedef / gerçek`. Sonuç 0–100'e kırpılır, 2 ondalık.
- **Negatif hedef → puanlanmaz (`None`)**; sıfır hedef + artan → `None`.
- Azalan + gerçek ≤ 0 → 100. Azalan + hedef 0 → gerçek ≤ 0 ise 100, değilse 0.
- Yıl özeti (gerçekleşen) `aggregate_actuals`: **Toplama / Ortalama / Son Değer** yöntemiyle motor üretir.

## Hangi ekran hangi ekseni kullanır
- **Eksen 1 (0–100 %):** Süreç karnesi başarı yüzdesi/donut/sağlık skoru (sunucu `achievement`, istemci hesaplamaz — Faz 1.1),
  süreç sağlığı (`process_health_service`), holding konsolidasyonu, K-Rapor, raporlar (`raporlar/routes_faz*`), SP analiz/akış/
  dönemler, masaüstü, K-Vektör, bireysel karne yüzdeleri.
- **Eksen 2 (1–5 bant):** Karne tablosundaki **"Skor / Başarı Puanı"** sütunu (`basari_puani`, `basari_olcek`), ağırlıklı başarı puanı
  (`pg_tablo_modal.js`, `bireysel.js`, `surec.js` karne satırı), faaliyet/veri girişi sonrası bant gösterimi.
- Aynı PG'nin iki sayısı **farklı** olabilir ve bu hata değildir: biri oran, biri bant.

## Bilinen istisna (kayıtlı borç)
`pg_tablo_modal.js` periyot hücresinin **durum rengi** (tek periyot gerçekleşen/hedef) istemcide hesaplanır;
sunucuda hücre bazlı karşılığı yoktur. Yüzde olarak gösterilir ve kırpılmaz. Sunucu payload'ı eklendiğinde taşınacak.

## Kurallar
1. Yeni ekranda başarı oranı gerekiyorsa **yalnız** `achievement()` / `_score_pgs()` çağrılır; JS'te `/ hedef * 100` yazılmaz
   (`tests/test_basari_yuzdesi_sunucu.py` yakalar).
2. Bant gerekiyorsa `hesapla_basari_puani`; bant yoksa oran **bant gibi** yuvarlanıp gösterilmez.
3. Sapma formülleri yön/hedef kuralını `achievement` ile paylaşır (Faz 1.3).
