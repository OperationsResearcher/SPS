# Yayın veri sayımları — 2026-07-06 22:00

> Amaç: Yerelden yayına toplu kurum aktarımı ÖNCESİ referans kayıt (KURALLAR-MASTER §8 kırmızı çizgi).
> **Kayseri Model Fabrika (tenant_id=16) özel statülü — hiçbir veri kaybı olmamalı.**

## Kurum listesi (7 kurum)

| id | Ad | Aktif |
|---|---|---|
| 1 | Default Corp | evet |
| 16 | **Kayseri Model Fabrika** | evet |
| 27 | Tomofil Otomotiv Sanayi ve Ticaret A.Ş. | evet |
| 28 | Eskişehir Makine Sanayii A.Ş. | evet |
| 29 | Kara Brothers | evet |
| 30 | VolTure Tech Teknoloji Anonim Şirketi | **pasif** |
| 31 | VolTure Tech Teknoloji ve Ticaret Anonim Şirketi | evet |

## Genel sayımlar (tüm kurumlar toplamı)

| Tablo | Sayı |
|---|---|
| tenants | 7 |
| users | 145 |
| processes | 96 |
| process_kpis | 510 |
| kpi_data | 92492 |
| process_activities | 3 |
| strategies | 53 |
| sub_strategies | 135 |
| project | 1 |
| task | 0 |

## Kayseri Model Fabrika (tenant_id=16) — DETAY

| Metrik | Sayı |
|---|---|
| Kullanıcılar | 8 |
| Processes (PG bağlı süreçler) | 11 |
| Process KPIs (PG) | 146 |
| KPI Data (PG verisi) | 497 |
| Process Activities | 2 |
| Strategies | 6 |
| Project | 0 |
| Task | 0 |

## Yedek (ALINDI — 2026-07-06 20:01:22 TS=20260706_200122)

- Tam DB (custom format): `/opt/kokpitim/backups/pre_tenant_migration_pg_20260706_200122.dump` (2.17 MB) — `pg_restore -d kokpitim_db ...` ile tam geri dönüş
- Tam DB (plain SQL, gzip): `/opt/kokpitim/backups/pre_tenant_migration_pg_20260706_200122.sql.gz` (1.65 MB) — çapraz PG sürümünde de okunabilir
- **Kayseri MF izole ek kopya (ekstra güvence):**
  - `/opt/kokpitim/backups/kayseri_mf_tenant_row_20260706_200122.csv` — tenants tablosunda id=16 satırı
  - `/opt/kokpitim/backups/kayseri_mf_users_20260706_200122.csv` — tenant_id=16 olan 8 kullanıcı satırı
  - Not: Bu CSV'ler yalnız tenant+users; process/kpi/strategy verisi tam DB dump'ında mevcut, ayrıca CSV alınmadı (hacim küçük, tam dump zaten güvenilir kaynak).

## Sonraki adım / plan

Yerelden Yayın'a **Kayseri Model Fabrika (tenant_id=16) hariç** diğer kurumların verisini aktarma
işlemi planlanıyor. Bu işlem tamamlandıktan sonra bu dosyadaki sayımlarla **Kayseri MF satırları
birebir aynı** olmalı (deploy sonrası doğrulama — KURALLAR-MASTER §8 madde 2). Farklıysa dur, yedekten
geri dön.
