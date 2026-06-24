"""kart short_id alanı (kısa görünen kimlik: 2 harf + numara)

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-06-21

system_cards.short_id — uzun code iç anahtar kalır; short_id kullanıcıya/admin'e
gösterilen kısa etikettir (örn. MA01).
"""
from alembic import op
import sqlalchemy as sa


revision = "d4e5f6a7b8c9"
down_revision = "c3d4e5f6a7b8"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("system_cards") as batch_op:
        batch_op.add_column(sa.Column("short_id", sa.String(length=12), nullable=True))
        batch_op.create_index(
            "ix_system_cards_short_id", ["short_id"], unique=True
        )


def downgrade():
    with op.batch_alter_table("system_cards") as batch_op:
        batch_op.drop_index("ix_system_cards_short_id")
        batch_op.drop_column("short_id")
