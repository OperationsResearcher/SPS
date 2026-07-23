---
name: project_kart_veri_tutarsizliklari
description: "Rapor katmanında bulunan gerçek hesaplama hataları — en kritiği D0: 438 gösterge ters hesaplanıyor (lower_is_better ölü koşulu)"
metadata: 
  node_type: memory
  type: project
  originSessionId: e77dc667-1e9b-4352-b2d9-78dfb468d0ba
  modified: 2026-07-20T09:06:58.316Z
---

Kart açıklaması yazmak için kodu okuturken bulunan **gerçek hatalar**. Tam liste
öncelik sıralı: `docs/kontrol/KART-VERI-TUTARSIZLIKLARI.md`. Açıklamalarda
dürüstçe kabul edildiler ama **düzeltilmediler** — kullanıcı onayı bekliyor.

**D0 — EN KRİTİK, 438 gösterge ters hesaplanıyor:**
`micro/modules/k_rapor/routes.py` satır 991, 1901, 2161'de
`if kpi.direction == "lower_is_better"` var. DB'de bu değer **HİÇ YOK**
(ölçüldü 2026-07-20: `Increasing`=956, `Decreasing`=438, `lower_is_better`=0).
Koşul hiç doğru olmuyor → 438 "azalması iyi" gösterge, artması iyiymiş gibi
hesaplanıyor. Hedefi 5 olan hata oranı 2 ölçüldüğünde %40 görünüyor, %100
olmalıydı — **iyi performans kötü raporlanıyor**.

Skor motoru (`compute_pg_score`) doğru değeri (`"Decreasing"`) kullandığı için
**aynı gösterge Kurumsal sekmesinde farklı, PG Dağılım sekmesinde farklı yüzde
gösteriyor** — kullanıcının fark edip nedenini bilemediği tutarsızlık büyük
olasılıkla budur.

Düzeltme 3 satır ama rapor rakamlarını değiştirir; önce/sonra elle doğrulama
gerekir.

**Diğerleri:** G1 KPR risk kartı yetki kapsamı uygulamıyor (yetki sızıntısı) ·
D1 değer zinciri eşleme yokken toplam süreç sayısını gösteriyor · D2 trend
önceki dönem boşken yapay "iyileşiyor" diyor · D3 veri yokken KP skorundan
türetilmiş sayı gösterme (yaygın desen — 7 metrik) · T1 risk eşiği iki ekranda
farklı (15 vs 16) · İ1 isim/ölçüm ayrışmaları (OEE A/P/Q tek sayının ofseti,
kapasite "utilization" aslında kapsama oranı, gantt "zamanında" aslında sadece
tamamlanma, CPM gerçek kritik yol değil).

İlgili: [[project_kart_aciklama_zenginlestirme]]
