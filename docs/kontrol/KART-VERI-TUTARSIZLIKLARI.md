# Kart Verisi — Tespit Edilen Tutarsızlıklar

> Kaynak: 2026-07-20 kart açıklaması zenginleştirme çalışması sırasında yapılan
> kod incelemesi (`services/k_radar_service.py`, `micro/modules/k_radar/*`).
> Bulgular kart açıklamalarının **"Sınır:"** bölümlerine şeffaflık gereği yazıldı
> — kullanıcı yanılmasın diye. Ancak bunlar **düzeltilmesi gereken gerçek
> sorunlardır**; açıklama yazmak çözüm değil, geçici dürüstlüktür.

Öncelik sırası: **G (güvenlik) > D (doğruluk) > T (tutarlılık) > İ (isimlendirme)**

---

## D0 — "Azalması iyi" göstergeler rapor katmanında TERS hesaplanıyordu ✅ KAPALI (2026-07-23)

> **Durum:** Kodda düzeltildi (`_azalmasi_iyi` + k_radar B7 → `compute_pg_score`).
> Keşif ölçümü (2026-07-23): `pi-dagilim` Decreasing scatter ≈ engine.
> **Yeni P0:** çift skor semantiği (SEM) — `status_percentage` band vs hedef oranı.
> Bkz. `docs/kontrol/HESAP-DOGRULUK-KESIF-2026-07-23.md`.

**Eski bulgu (tarihsel):** `lower_is_better` DB’de yoktu; koşul hiç tutmuyordu.
**Çözüm uygulandı:** Decreasing / decreasing / lower_is_better tuple + skor motoru.

---

## SEM — Çift skor semantiği (band vs oran) ⚠️ P0 AÇIK (ürün: etiket ayrımı 2026-07-23)

`kpi_data.status_percentage` çoğunlukla başarı bandı (50/70/90/100);
`compute_pg_score` hedef oranı üretir. Masaüstünde artık iki etiket ayrı gösterilir
(SEM-C kararı). Backfill / tek semantik birleştirme **yapılmadı**.

---

## G1 — KPR risk kartı yetki kapsamı ✅ DÜZELTİLDİ (2026-07-23)

`risk_heatmap_items.project_id` eklendi (FK → `project.id`). Scoped kullanıcıda
yalnız `project_id IN scope`; NULL kayıtlar kurum geneli (scope None) görür.
`source_type=project` backfill uygulandı. Migration: `hd01a2b3c4d5`.

---

## ~~G1 — KPR risk kartı yetki kapsamı uygulamıyor~~ (eski metin)

---

## D1 — Değer zinciri "eşlenen süreç" boşken maksimum ✅ DÜZELTİLDİ (2026-07-23)

Fallback kaldırıldı; `mapped_process_count` dürüst 0. UI mc-empty.

---

## D2 — Trend yapay yön ✅ DÜZELTİLDİ (2026-07-23)

Yetersiz veride `trend=None`; period health `compute_pg_score`+direction.

---

## T1 — Risk eşiği ✅ DÜZELTİLDİ (2026-07-23)

`app/services/rpn_severity.py`: ≥16 critical, ≥10 high, ≥5 medium.

---

## İ1 — Gösterge adları ölçülen şeyle örtüşmüyor (kısmen)

OEE ofsetli sahte bileşenler kaldırıldı (D3 mc-empty). Diğer İ1 satırları
(gantt/CPM/kapasite) **açık** — ürün kararı bekliyor.

---

## D3 — Veri yokken türetilmiş sayı ✅ DÜZELTİLDİ (2026-07-23)

Boş metrikler None + `data_available` + UI mc-empty.

---

## Not: 5 dakika önbellek

`get_*` fonksiyonları `@cache.memoize(timeout=300)`. Veri girildikten sonra kart
5 dakikaya kadar eski değeri gösterebiliyor. Bu bir hata değil ama kullanıcı
"kaydettim, değişmedi" diye tekrar kaydetmeye çalışıyor. Açıklamalara not
düşüldü; ayrıca veri girişi sonrası ilgili cache anahtarının
temizlenmesi düşünülebilir.

---

## Arşiv — eski D1/D2/T1/D3 metinleri

Eski detaylı teşhis metinleri keşif belgesinde:
`docs/kontrol/HESAP-DOGRULUK-KESIF-2026-07-23.md`
