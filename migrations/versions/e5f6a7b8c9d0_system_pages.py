"""system_pages tablosu — sayfa kataloğu (kart code prefix + short_id)

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-06-23

Her sayfa = kartların code prefix'i (örn. raporlar_cfo_dashboard). short_id
modül-kısa kimlik (RP-CFO). Admin sayfa başında görür; sayfa-kart envanteri.
"""
from alembic import op
import sqlalchemy as sa


revision = "e5f6a7b8c9d0"
down_revision = "d4e5f6a7b8c9"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "system_pages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("url", sa.String(length=255), nullable=True),
        sa.Column("short_id", sa.String(length=16), nullable=True),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_system_pages_code", "system_pages", ["code"], unique=True)
    op.create_index("ix_system_pages_short_id", "system_pages", ["short_id"], unique=True)


def downgrade():
    op.drop_index("ix_system_pages_short_id", table_name="system_pages")
    op.drop_index("ix_system_pages_code", table_name="system_pages")
    op.drop_table("system_pages")
