---
name: project_yedekleme_ve_db
description: "Yedekleme bileşeni mimarisi + yerel DB'nin gerçekte PostgreSQL 18 olması"
metadata: 
  node_type: memory
  type: project
  originSessionId: 0265ef0d-566e-4066-930c-3200531599d0
---

**Yerel DB = PostgreSQL 18.3** (`kokpitim_db`, kullanıcı `kokpitim_user`, localhost). CLAUDE.md'deki "DB dosyası instance/kokpitim.db (SQLite)" bilgisi **güncel değil** — `instance/kokpitim.db` 0 byte/ölü. Tüm ortamlar PostgreSQL.

**pg_dump sürüm tuzağı:** Sunucu PG 18 → pg_dump da ≥18 olmalı (eski pg_dump yeni sunucuyu reddeder). Windows'ta 18'lik araçlar `C:\pgdata\bin`'de; `C:\Program Files\PostgreSQL\16\bin` 16.13 (kullanma). `yedekleme_service._resolve_pg_bin()` en yüksek sürümü seçer.

**Yedekleme bileşeni (TASK-180, Admin Araçları > Yedekleme):**
- `app/services/yedekleme_service.py`: pg_dump (-Fc tam DB), kod tar.gz (tam / mtime-fark), rotasyon (son 14), `run_auto_backup`, `restore_db` (pg_restore --clean), `auto_status`.
- Gece 02:00 APScheduler (`_init_yedekleme_scheduler` in app/__init__.py): tam DB + kod (haftada bir tam baseline, diğer günler fark).
- Çıktı `instance/yedekler/otomatik/` (gitignored). Route'lar Admin-only; restore şifre + onay metni `KOKPITIM-DB-GERIYUKLE`.

**Eski yedekleme tooling kaldırıldı** (admin_backup_service, backup_scheduler_service, yedekleyici.py, /ayarlar/yedekleme UI) + `backups/`+`Yedekler/` 7,5 GB kalıcı silindi (kullanıcı onayı).

**DİKKAT — `tenant_backup_service.py` KORUNDU:** [[project_demo_ortami_mutabakat]]'taki demo reset (`demo_reset_service.py` → `restore_tenant_data`) ve ops scriptleri buna bağımlı. Silersen demo sıfırlama çöker.

**Alembic baseline (TASK-182, 2026-06-08):** Eski 65 migration `migrations/_archive_versions/`'e taşındı; tek baseline `f5215370eebd` (down_revision=None, 161 tablo). Yerel+Test+Yayın DB'leri buna stamp'li. **Kurallar:**
- **Tek head disiplini:** paralel dal migration'ları birikince merge et — yoksa `flask db upgrade` "multiple heads" ile patlar (eski sorunun kök nedeni).
- **alembic_version sahipliği:** stamp'i `sudo -u postgres` ile yaparsan tablo postgres'in olur → app "permission denied for table alembic_version". `ALTER TABLE alembic_version OWNER TO kokpitim_user` (Test: kokpitim_test_user) şart.
- Yayın/Test şema yönetimi: otomatik create_all YOK; yeni tablo eklenince elle uygulanır. Şema değişikliği artık baseline üstüne yeni autogenerate migration olmalı.
- Deploy (`oracle_safe_deploy.sh`) Alembic adımı artık çalışıyor (no-op). Manuel stamp = sıfır DDL (sadece alembic_version satırı).
