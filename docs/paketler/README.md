# Paketleme & Segmentasyon

Bu klasör, Kokpitim'in **paketlere (tier'lara) ayrılması** ve segment bazlı konumlandırması ile ilgili tüm dokümantasyonu tutar. Ürün geniş bir yüzeye ulaştı; amaç farklı olgunluk/yetkinlik seviyelerindeki kurumlara uygun paketler tasarlamak.

> **Çalışma kuralı:** Önce burada mutabık kalınır (strateji), sonra koda/`subscription_packages` verisine yansıtılır.

## İçindekiler
- [`PAKETLEME-STRATEJISI.md`](PAKETLEME-STRATEJISI.md) — Ana strateji: segment modeli (tier × olgunluk), 3+1 paket önerisi, modül/ekran sınıflandırma haritası (4 eksen), açık kararlar.

## İlgili kod (referans — burada DEĞİL)
- `micro/core/module_registry.py` — launcher modülleri + `get_accessible_modules` (paket→modül yetki kapısı; ÇALIŞIYOR).
- `subscription_packages`, `package_modules`, `system_modules`, `system_components`, `module_component_slugs`, `route_registry` (DB tabloları) — modül/bileşen taksonomisi + paket eşlemesi.
