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

---

## DEPLOY SONUCU (2026-06-08, Yerel→Test→Yayın)
**Yöntem:** Test'te (test.kokpitim.com) doğrulandı → Yayın'a kod tarball + docker build + container recreate. Alembic ATLANDI (prod db.create_all). Branch claude/admin-araclari-hata-kontrolu (prod 44909c6 üzerine ileri güncelleme).

### Deploy SONRASI Yayın satır sayıları — kontrol
| Metrik | Önce | Sonra | Durum |
|---|---|---|---|
| Kurum (tenants) | 7 | 7 | ✅ |
| Kullanıcı (users) | 145 | 145 | ✅ |
| Süreç (processes) | 96 | 96 | ✅ |
| PG (process_kpis) | 510 | 510 | ✅ |
| PG Verisi (kpi_data) | 92.492 | 92.492 | ✅ |
| Süreç Faaliyeti | 3 | 3 | ✅ |
| Ana Strateji | 53 | 53 | ✅ |
| Alt Strateji | 135 | 135 | ✅ |
| Proje | 1 | 1 | ✅ |
| Proje Görevi | 0 | 0 | ✅ |

**SONUÇ: 10/10 sayı aynı — VERİ KAYBI YOK.** www.kokpitim.com /health → 200.

### Rollback varlıkları (gerekirse)
- Image: `kokpitim_web:rollback_20260608_125823`
- DB: `/opt/kokpitim/backups/pre_deploy_pg_20260608_124014.dump`
- Kod: `/opt/kokpitim/backups/pre_deploy_code_20260608_124014.tar.gz`

### Not (deploy ile ilgisiz, önceden var)
- Yayın `/opt/kokpitim/.env`'de `ENCRYPTION_KEY` tanımlı değil → şifreli alanlar (SMTP/TOTP) restart'lar arası çözülemez. Deploy öncesi de böyleydi; ayrıca ele alınmalı.
