# Yerel PostgreSQL vs VM SQLite yedek — karşılaştırma (2 Nisan 2026)

**Kaynaklar:** yerel `.env` içindeki PostgreSQL; `backups/vm_pull/20260402_033734_vm_kokpitim_sqlite.db`.

**Not:** Bu SQLite dosyası VM `instance` volume yedeğidir; içinde **birleşik** tablolar (`tenants`, `processes`, `kpi_data` …) dolu, **legacy** tablolar (`kurum`, `surec` …) çoğunlukla boştur. Karşılaştırma **aynı isimli birleşik tablolar** üzerinden yapılmıştır. Kesin üretim eşlemesi için **`pg_dump` (.dump)** dosyası da kullanılmalıdır.

## Özet fark (toplam)

- Kurum: yerel **18**, SQLite **16** (SQLite yedeği daha eski / eksik tenant içerebilir.)
- Kullanıcı, süreç, PG ve PGV sayıları yerelde daha yüksek; SQLite dosya tarihi VM volume ile sınırlıdır.

## Toplam karşılaştırma

| Öğe | Yerel PostgreSQL | VM SQLite yedeği |
|-----|------------------:|-----------------:|
| Kurum / tenant | 18 | 16 |
| Kullanıcı | 76 | 74 |
| Süreç | 55 | 46 |
| PG (süreç performans göstergesi) | 473 | 344 |
| PGV (performans gösterge verisi) | 5889 (tüm `kpi_data`) / 5598 (süreç PG zinciri) | 4686 (tüm) / 4394 (zincir) |

## Kurum bazlı detay — yerel PostgreSQL (`tenants`)

| tenant_id | Ad | Kullanıcı | Süreç | PG | PGV (süreç zinciri) |
|----------:|----|----------:|------:|---:|--------------------:|
| 1 | Default Corp | 14 | 2 | 42 | 298 |
| 2 | Test Kurum | 0 | 0 | 0 | 0 |
| 3 | Anadolu Sağlık Grubu | 3 | 5 | 15 | 926 |
| 4 | Ege Teknoloji A.Ş. | 5 | 5 | 22 | 1328 |
| 5 | Marmara Eğitim Vakfı | 7 | 5 | 30 | 1826 |
| 6 | Deneme | 0 | 0 | 0 | 0 |
| 7 | Boğaziçi Üniversitesi | 15 | 1 | 3 | 9 |
| 8 | Sistem Ynt | 2 | 0 | 0 | 0 |
| 10 | Deneme Danışmanlık | 2 | 1 | 1 | 0 |
| 11 | TechNova Bilişim Çözümleri A.Ş. | 9 | 12 | 102 | 0 |
| 12 | Mega Yapı ve İnşaat Sanayi Tic. Ltd. | 2 | 0 | 0 | 0 |
| 13 | EcoDoğa Geri Dönüşüm ve Enerji A.Ş. | 1 | 0 | 0 | 0 |
| 14 | Test A.Ş. | 1 | 1 | 1 | 0 |
| 15 | TechNova Bilişim Çözümleri A.Ş. | 4 | 3 | 6 | 0 |
| 16 | Kayseri Model Fabrika | 8 | 11 | 83 | 9 |
| 17 | EBB | 0 | 0 | 0 | 0 |
| 18 | label | 1 | 1 | 1 | 2 |
| 19 | ESOGU | 1 | 8 | 128 | 1200 |

## Kurum bazlı detay — VM SQLite (`tenants`)

| tenant_id | Ad | Kullanıcı | Süreç | PG | PGV (süreç zinciri) |
|----------:|----|----------:|------:|---:|--------------------:|
| 1 | Default Corp | 14 | 2 | 42 | 298 |
| 2 | Test Kurum | 0 | 0 | 0 | 0 |
| 3 | Anadolu Sağlık Grubu | 3 | 5 | 15 | 926 |
| 4 | Ege Teknoloji A.Ş. | 5 | 5 | 22 | 1328 |
| 5 | Marmara Eğitim Vakfı | 7 | 5 | 30 | 1826 |
| 6 | Deneme | 0 | 0 | 0 | 0 |
| 7 | Boğaziçi Üniversitesi | 15 | 1 | 3 | 7 |
| 8 | Sistem Ynt | 2 | 0 | 0 | 0 |
| 10 | Deneme Danışmanlık | 2 | 1 | 1 | 0 |
| 11 | TechNova Bilişim Çözümleri A.Ş. | 9 | 12 | 102 | 0 |
| 12 | Mega Yapı ve İnşaat Sanayi Tic. Ltd. | 2 | 0 | 0 | 0 |
| 13 | EcoDoğa Geri Dönüşüm ve Enerji A.Ş. | 1 | 0 | 0 | 0 |
| 14 | Test A.Ş. | 1 | 1 | 1 | 0 |
| 15 | TechNova Bilişim Çözümleri A.Ş. | 4 | 3 | 6 | 0 |
| 16 | Kayseri Model Fabrika | 8 | 11 | 83 | 9 |
| 17 | EBB | 0 | 0 | 0 | 0 |

## Şema notu

- SQLite yedek şeması tespiti: **unified (VM volume)**.
- PostgreSQL ve SQLite (birleşik) **PGV zinciri:** `kpi_data` → `process_kpis` → `processes` (silinmemiş ve aktif süreçler).
