# K-Radar Release Readiness (Go/No-Go)

Tarih: 2026-03-26  
Kapsam: K-Radar Faz A-F yerel doğrulama çıktıları

## Karar

- Karar: **GO (Yerel ortam için)**
- Not: Canlı öncesi son tur manuel UI kabul ve operasyon onayı önerilir.

## Faz Durumu

- Faz A (Omurga): Tamam
- Faz B (Domain Şema Paketi-1): Tamam
- Faz C (Alt Analiz Route/Template Paketi-1): Tamam
- Faz D (Analiz Motorları): Tamam (operasyonel ilk seviye)
- Faz E (Öneri Motoru Sertleştirme): Tamam (tetikleyici + dedup + öncelik)
- Faz F (Doğrulama/Kapanış): Tamamlandı (bu tur kapsamı)

## Doğrulama Kanıtı

- Regresyon testleri:
  - `tests/test_k_radar_regression.py` → **4 passed**
  - Kapsam:
    - Yeni endpoint smoke
    - Rol yetkisi (write forbidden)
    - Tenant izolasyonu
    - History + CSV kontratı
- Smoke:
  - `scripts/k_radar_smoke_check.py` → route/table eksik yok
- Perf baseline:
  - `scripts/k_radar_perf_baseline.py`
  - Gözlenen ortalama değerler:
    - `/k-radar/api/hub-summary` ~ 15.94 ms
    - `/k-radar/api/recommendations` ~ 4.76 ms
    - `/k-radar/api/recommendations/history` ~ 4.99 ms
    - `/k-radar/api/kp/darbogaz` ~ 13.62 ms
    - `/k-radar/api/kpr/evm` ~ 1.98 ms
    - `/k-radar/api/cross/risk-heatmap` ~ 3.91 ms

## Açık Riskler (Kabul Edilebilir)

- Bazı modüller özet metrik seviyesinde; ileri drill-down/rapor derinliği sonraki iterasyona kalabilir.
- Performans baseline yerel ve düşük veri seti ile ölçüldü; prod-benzeri veriyle tekrar ölçüm önerilir.
- Manuel UI kabul turu kullanıcı senaryoları ile tamamlanmalı.

## Go Kriterleri Kontrol Listesi

- [x] Yeni KS/KP/KPR/Cross modülleri açılıyor ve veri dönüyor
- [x] Faz E tetikleyici + aksiyon akışı çalışıyor
- [x] Role/tenant izolasyon testleri geçiyor
- [x] History/CSV kontratı doğrulandı
- [x] Smoke + lint + compile temiz
- [ ] Canlı öncesi son manuel UAT turu tamamlandı

## No-Go Tetikleyicileri

- Kritik endpointlerde 5xx artışı
- Tenant izolasyonu ihlali
- Öneri onay akışında task üretiminde hatalı çoğalma (dedup dışı)
- UAT sırasında bloklayıcı UX veya veri tutarsızlığı

## Sonuç

Bu kapsam için teknik olarak **GO** önerilir. Canlı geçişten hemen önce UAT checklist (`docs/KRADAR_UI_KABUL_CHECKLIST.md`) üzerinden son tur geçilmelidir.
