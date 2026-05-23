"""user_2fa — User'a 2FA alanları

Revision ID: d4e5f6g7h011
Revises: c3d4e5f6g010
Create Date: 2026-05-23

Sprint 26: TOTP tabanlı 2FA altyapısı.
- users.totp_secret (String, nullable, encrypted-at-rest önerilir)
- users.totp_enabled (Boolean, default False)
- users.totp_backup_codes_json (JSON, recovery codes)
"""

from alembic import op
import sqlalchemy as sa

revision = "d4e5f6g7h011"
down_revision = "c3d4e5f6g010"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("totp_secret", sa.String(64), nullable=True))
        batch_op.add_column(sa.Column("totp_enabled", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column("totp_backup_codes_json", sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_column("totp_backup_codes_json")
        batch_op.drop_column("totp_enabled")
        batch_op.drop_column("totp_secret")
