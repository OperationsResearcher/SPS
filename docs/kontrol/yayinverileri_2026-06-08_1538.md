# Yayın Veri Kontrolü — Deploy Öncesi

**Tarih/Saat:** 2026-06-08 15:38 (yerel, Europe/Istanbul)
**Ortam:** Yayın (Canlı) — https://www.kokpitim.com · Oracle VM 129.159.30.175 · `kokpitim_db`
**Amaç:** Yerel→Yayın güncellemesi öncesi veri sayımı (deploy sonrası bu dosyayla doğrulanacak).

## Yayın durumu (deploy öncesi)
- **Prod git HEAD:** `44909c6` — feat: K-Radar UX, strateji haritasi, sektör benchmark, DB senkron (2026-06-01 01:18:31 +0300)
- **Alembic:** `alembic_version` tablosu YOK → şema `db.create_all()` ile yönetiliyor (Alembic migration izlenmiyor)
- **Yerel branch:** `claude/admin-araclari-hata-kontrolu` — main'in 144 commit önünde

## Temel tablo satır sayıları (deploy ÖNCESİ)

| Metrik | Tablo | Sayı |
|---|---|---|
| Kurum | tenants | **7** |
| Kullanıcı | users | **145** |
| Süreç | processes | **96** |
| PG (Gösterge) | process_kpis | **510** |
| PG Verisi | kpi_data | **92.492** |
| Süreç Faaliyeti | process_activities | 3 |
| Ana Strateji | strategies | 53 |
| Alt Strateji | sub_strategies | 135 |
| Proje | project | 1 |
| Proje Görevi | task | 0 |

## Deploy sonrası doğrulama kuralı
Deploy sonrası bu 10 sayı **birebir aynı** olmalı (kullanıcı verisi kırmızı çizgi).
Herhangi biri düşerse → veri kaybı → yedekten geri dönülür.

## Deploy öncesi alınan yedek (Yayın VM `/opt/kokpitim/backups/`)
- `pre_deploy_pg_20260608_124014.dump` (2.1 MB, pg_dump custom) — DB
- `pre_deploy_pg_20260608_124014.sql.gz` (1.6 MB, plain SQL) — DB
- `pre_deploy_code_20260608_124014.tar.gz` (572 MB) — kod
