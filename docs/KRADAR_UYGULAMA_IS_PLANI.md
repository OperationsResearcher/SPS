# K-Radar Uygulama İş Planı

Bu plan, `docs/KRadar.pdf` belgesindeki hedef yapıyı kontrollü paketler halinde canlıya yakın seviyede tamamlamak için hazırlanmıştır.

## Faz A — Omurga (Tamamlanan/Kısmi)
- K-Radar hub ve ana radar route'ları
- Temel skor motoru ve öneri üretimi
- Öneri onay/red + geçmiş + CSV
- Rol ve tenant izolasyonu

## Faz B — Domain Şema Paketi-1 (Bu tur başlatıldı)
- Yeni çekirdek tablolar:
  - `process_maturity`
  - `bottleneck_log`
  - `value_chain_items`
  - `evm_snapshots`
  - `risk_heatmap_items`
  - `stakeholder_maps`
  - `stakeholder_surveys`
  - `a3_reports`
  - `competitor_analyses`
- Alembic migration ile PostgreSQL'e uygulanması
- Model import zincirine eklenmesi

## Faz C — Alt Analiz Route/Template Paketi-1 (Bu tur başlatıldı)
- `/k-radar/ks/swot`
- `/k-radar/kp/olgunluk`
- `/k-radar/kpr/cpm`
- `/k-radar/cross/paydas`
- Her bir rota için temel sayfa + bir sonraki adım backlog notu

## Faz D — Analiz Motorları (Sonraki)
- KS: SWOT/PESTLE/TOWS/Gap/OKR/Hoshin/Ansoff/BCG/BSC/EFQM
- KP: Olgunluk, Darboğaz, Değer Zinciri, Pareto, SLA, Kapasite, Benchmark, OEE, VSM
- KPR: CPM, EVM, Risk, Kaynak Kapasite, Gantt
- Cross: Risk ısı haritası, Paydaş, Rekabet, A3/5Neden, Anket

## Faz E — Öneri Motoru Sertleştirme
- Radar bazlı tetikleyiciler
- Onay akışı sonrası otomatik görev üretimi (kural tabanlı)
- İzlenebilirlik/audit iyileştirmeleri

## Faz F — Doğrulama ve Kapanış
- API smoke testleri
- Rol/tenant regresyonu
- UI kabul testi
- Belgeye karşı satır bazlı tamamlama matrisi

## Bu tur teslimatı
- Faz B şema paketi-1 kodu
- Faz C rota/template paketi-1 kodu
