"""Encrypt existing plaintext smtp_password values in tenant_email_configs.

Revision ID: k1l2m3n4o015
Revises: (bir önceki revision id'yi buraya girin)
Create Date: 2026-06-01

KULLANIM:
    Bu script veritabanındaki mevcut düz-metin smtp_password değerlerini
    Fernet ile şifreleyerek günceller.

    Çalıştırmadan önce ENCRYPTION_KEY .env'de tanımlı olmalıdır:
        ENCRYPTION_KEY=<fernet_key>

    Elle çalıştırmak için:
        flask db upgrade k1l2m3n4o015
    veya doğrudan:
        flask shell
        >>> from migrations.versions.k1l2m3n4o015_encrypt_smtp_password import migrate_existing
        >>> migrate_existing()

UYARI:
    - Bu migration geri alınamaz (downgrade şifrelemeyi çözer ve yeniden düz yazar).
    - Çalıştırmadan önce veritabanı yedeği alın.
    - Migration sırasında ENCRYPTION_KEY değiştirilmemelidir.
"""

import logging

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

revision = "k1l2m3n4o015"
down_revision = "a3b4c5d6e008"  # bsc_kpi_perspectives — migration zincirinin son halkası
branch_labels = None
depends_on = None


def upgrade():
    """Düz-metin şifreleri Fernet ile şifrele."""
    # Lazy import — migration sırasında app context olmayabilir
    try:
        from app.utils.encryption import encrypt
    except ImportError:
        logger.error(
            "app.utils.encryption import edilemedi. "
            "ENCRYPTION_KEY ayarlı ve uygulama dizini PATH'te olmalı."
        )
        raise

    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        rows = session.execute(
            sa.text("SELECT id, smtp_password FROM tenant_email_configs WHERE smtp_password IS NOT NULL")
        ).fetchall()

        updated = 0
        skipped = 0
        for row in rows:
            plaintext = row[1]
            if not plaintext:
                continue
            # Zaten şifreli mi? Fernet token'ları "gAAAAA" ile başlar
            if plaintext.startswith("gAAAAA"):
                skipped += 1
                continue
            encrypted = encrypt(plaintext)
            session.execute(
                sa.text("UPDATE tenant_email_configs SET smtp_password = :enc WHERE id = :id"),
                {"enc": encrypted, "id": row[0]},
            )
            updated += 1

        session.commit()
        logger.info("smtp_password migration tamamlandı: %d güncellendi, %d zaten şifreli atlandı.", updated, skipped)
    except Exception:
        session.rollback()
        logger.exception("smtp_password migration başarısız")
        raise
    finally:
        session.close()


def downgrade():
    """Şifreli değerleri çözerek düz metne dönüştür (geri alma)."""
    try:
        from app.utils.encryption import decrypt
    except ImportError:
        logger.error("app.utils.encryption import edilemedi.")
        raise

    bind = op.get_bind()
    session = Session(bind=bind)

    try:
        rows = session.execute(
            sa.text("SELECT id, smtp_password FROM tenant_email_configs WHERE smtp_password IS NOT NULL")
        ).fetchall()

        for row in rows:
            ciphertext = row[1]
            if not ciphertext or not ciphertext.startswith("gAAAAA"):
                continue
            plaintext = decrypt(ciphertext)
            session.execute(
                sa.text("UPDATE tenant_email_configs SET smtp_password = :plain WHERE id = :id"),
                {"plain": plaintext, "id": row[0]},
            )

        session.commit()
        logger.info("smtp_password downgrade tamamlandı.")
    except Exception:
        session.rollback()
        logger.exception("smtp_password downgrade başarısız")
        raise
    finally:
        session.close()


def migrate_existing():
    """Flask shell'den elle çağırmak için yardımcı fonksiyon."""
    upgrade()
