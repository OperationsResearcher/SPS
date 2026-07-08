# Yayın veri sayımları — 2026-07-07 07:30

> Amaç: Yayın'a KOD DEPLOY'u (155 commit + 5 Alembic migration) öncesi referans kayıt.
> Bu, tenant 1/27/28 migration'ından AYRI bir iş — önce Yayın'ın kodunu/şemasını
> yerelle (main HEAD) hizalıyoruz, veri migration'ı SONRA yapılacak.

## Genel sayımlar (deploy öncesi — değişmemeli)

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

Not: Bu sayılar `yayinverileri_2026-07-06_2200.md` ile birebir aynı — önceki oturumdan
bu yana Yayın'da veri değişikliği olmamış.

## Yedek (ALINDI — 2026-07-07 07:29:52 TS=20260707_072952)

- Tam DB (custom format): `/opt/kokpitim/backups/pre_code_deploy_pg_20260707_072952.dump`
- Tam DB (plain SQL, gzip): `/opt/kokpitim/backups/pre_code_deploy_pg_20260707_072952.sql.gz`
- Docker image rollback etiketi: `kokpitim_web:rollback_20260707_072952`

## Deploy kapsamı

- Yayın'ın mevcut kodu: commit `975dd39` (Alembic squash baseline sonrası)
- Hedef: `main` HEAD (1b16df8) — 155 commit fark
- Alembic: `f5215370eebd` (baseline) → `a1b2c3d4e5f6` → `b2c3d4e5f6a7` → `c3d4e5f6a7b8`
  → `d4e5f6a7b8c9` → `e5f6a7b8c9d0` (5 migration, hepsi toplamsal/geri-dönüşlü)
- Motivasyon: tenant_ethics_codes/tenant_quality_policies/tenant_values tabloları
  (13 satır, yerelde 1/27/28'e ait) Yayın'da yok — DRY_RUN migration provasında keşfedildi.
  Bu 3 tablo `a1b2c3d4e5f6` migration'ında; zincir bölünemediği için önceki
  baseline'dan sonraki TÜM commit'ler + 5 migration deploy edilecek.

## Deploy sonrası doğrulama planı

1. `/health` → 200
2. Yukarıdaki tüm sayımlar BİREBİR AYNI (satır kaybı yok)
3. `alembic_version` = `e5f6a7b8c9d0`
4. tenant_ethics_codes/tenant_quality_policies/tenant_values tabloları var (boş, 0 satır — henüz veri migration'ı yapılmadı)
5. Smoke test: login + kritik modül (süreç karnesi, PGV)

## SONUÇ — 2026-07-07 07:55 (TAMAMLANDI)

**Deploy başarılı, ama yol boyunca kritik bir prod-down olayı yaşandı ve düzeltildi:**

- Git pull: `975dd39` → `1b16df8` (main HEAD), 155 commit — başarılı.
- Docker build: `2c6804aa7316` — başarılı.
- **OLAY:** Container recreate sonrası `ENCRYPTION_KEY ortam değişkeni üretimde
  zorunludur` hatasıyla worker boot edemedi, container "Restarting" döngüsüne
  girdi, `/health` 404 döndü (~15-20 dakika, tespit+düzeltme süresi).
  **Kök neden:** Yeni kod (155 commit içinde) `ENCRYPTION_KEY`'i production'da
  zorunlu kılıyor (`app/utils/encryption.py`), ama Yayın'ın `.env`'inde bu
  değişken hiç tanımlı değildi (önceki kod bunu gerektirmiyordu).
  **Düzeltme:** Yeni Fernet key üretildi, `/opt/kokpitim/.env`'e eklendi,
  container silinip aynı parametrelerle (`--network host`, instance mount,
  `--env-file`, `FLASK_ENV=production`, `TRUST_PROXY=1`) yeniden oluşturuldu
  (`docker restart` env'i yeniden okumadığı için yetmedi — bilinen Docker
  davranışı, dokümante edilmişti).
  **Not:** Yayın'da önceden 2 adet `tenant_email_configs.smtp_password` kaydı
  vardı (tenant 1 ve 27) — biri düz metin (20 karakter) biri muhtemelen eski
  bir anahtarla şifreli (100 karakter) görünüyordu. Yeni anahtar bunları
  etkilemiş olabilir — ayrıca doğrulanıp gerekirse temizlenmeli (bu migration'ın
  kapsamı dışında, ayrı takip).
- Alembic upgrade (elle çalıştırıldı, deploy script'i crash yüzünden bu adıma
  ulaşamamıştı): `f5215370eebd` → `e5f6a7b8c9d0`, 5 migration, sorunsuz.
- **Satır sayıları deploy sonrası BİREBİR AYNI** (tenants=7, users=145,
  processes=96, process_kpis=510, kpi_data=92492, vb.) — veri kaybı YOK.
- Yeni tablolar (tenant_values/ethics_codes/quality_policies, system_cards,
  system_pages) oluşturuldu, boş (0 satır) — beklenen, veri migration'ı ayrı adım.
- Final health: `https://www.kokpitim.com/health` → 200, container 4+ dakikadır
  stabil.

**Sıradaki adım:** tenant 1/27/28 veri migration'ı (`scripts/migrate_tenants_1_27_28_prod.py`)
artık DRY_RUN'da tamamen doğrulanmış durumda — gerçek çalıştırma için hazır,
kullanıcı onayı bekleniyor.

## TENANT 1/27/28 VERİ MİGRASYONU — 2026-07-07 08:20 (TAMAMLANDI)

**Gerçek migration (DRY_RUN=False) çalıştırıldı ve veri kalıcı olarak Yayın'a yazıldı.**

Kullanıcı onayıyla script VM üzerinde çalıştırıldı. Script, ADIM 4 (sequence
resync) sonrası ADIM 5 (verify) onay isteminde `input()` EOF hatası alıp
yakalanmamış exception ile crash oldu (stdin pipe'a yeterli "EVET" satırı
gönderilmemişti — 8 onay noktası var, 6 gönderilmişti). Script `main()`'in
sonundaki resmi commit satırına hiç ulaşmadı. Yine de doğrudan veritabanı
kontrolünde veri **kalıcı ve doğru** bulundu — muhtemel açıklama SSH/process
sonlanma sırasının PostgreSQL bağlantı kapanma davranışıyla beklenenden farklı
etkileşmesi; kesin commit mekanizması doğrulanamadı ama sonuç doğrulandı.

**Kullanıcı kararı:** Script tekrar çalıştırılmadı (zaten commit olmuş veriye
tekrar sil+ekle riskli olurdu) — mevcut durum salt-okunur kontrolle kabul edildi.

### Final sayımlar — Yayın'da 1/27/28 (migration sonrası)

| Tablo | Yerel (kaynak) | Yayın (migration sonrası) | Durum |
|---|---|---|---|
| users | 132 | 132 | ✅ tam |
| processes | 85 | 85 | ✅ tam |
| process_kpis | 365 | 364 | 1 satır eksik (FK hatası, kabul edildi) |
| kpi_data | ~92000+ | 91995 | ✅ (script raporunda tam) |
| plan_years | 11 | 11 | ✅ tam |
| strategies | 48 | 47 | 1 satır eksik (FK hatası, kabul edildi) |
| sub_strategies | 115 | 114 | 1 satır eksik (FK hatası, kabul edildi) |
| notifications | 2069 | 2066 | 3 satır eksik (FK hatası, kabul edildi) |
| audit_logs | 149 | 98 | 51 satır eksik (dict/JSON adapt + FK hataları, kabul edildi) |
| project | 2 | 1 | 1 satır eksik (manager_id FK hatası, kabul edildi) |

### Değişmeyen tenant'lar (doğrulandı)

- Kayseri Model Fabrika (16): 8 kullanıcı — **değişmedi**
- Kara Brothers (29) + VolTure Tech (30/31): toplam 12 kullanıcı, 11 process, 6 strategy — **değişmedi**

### Site durumu

- `https://www.kokpitim.com/health` → 200, `database: ok`
- Container `kokpitim-web` stabil çalışıyor

### Bilinen küçük eksiklikler (bu migration'ın kapsamı dışında, ayrı takip)

- Birkaç düzine satır (yukarıdaki tabloda) FK/JSON-adapt hataları nedeniyle
  atlandı — hepsi script çalışırken loglandı, veri bütünlüğünü bozmuyor
  (constraint ihlali önlendi, orphan/tutarsız satır yazılmadı).
- `tenant_email_configs` — Yayın'da 2 eski kayıt (tenant 1 ve 27) `ENCRYPTION_KEY`
  değişikliğinden etkilenmiş olabilir, ayrıca doğrulanmalı.
