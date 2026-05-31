# instance/

Bu klasör **yüklemeler** (`uploads/`) ve geçici JSON çıktıları içindir.

- **Veritabanı burada değildir.** Geliştirme ve üretim **PostgreSQL** kullanır (`SQLALCHEMY_DATABASE_URI` → `.env`).
- `*.db` (SQLite) dosyaları kaldırıldı; yeniden oluşturmayın.

Canlı veri VM (Oracle) ile hizalama: `backups/oracle_migration/kokpitim_db_migration_*.dump` → yerel `kokpitim_db` restore.
