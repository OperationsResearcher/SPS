"""demo_requests tablosu — marketing /demo-talep form kayıtları

Revision ID: f6a7b8c9d0e1
Revises: e5f6a7b8c9d0
Create Date: 2026-07-08
"""
from alembic import op
import sqlalchemy as sa


revision = "f6a7b8c9d0e1"
down_revision = "e5f6a7b8c9d0"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "demo_requests",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("ad_soyad", sa.String(length=200), nullable=False),
        sa.Column("kurum", sa.String(length=200), nullable=False),
        sa.Column("gorev", sa.String(length=200), nullable=True),
        sa.Column("sektor", sa.String(length=100), nullable=True),
        sa.Column("calisan", sa.String(length=50), nullable=True),
        sa.Column("email", sa.String(length=200), nullable=False),
        sa.Column("telefon", sa.String(length=50), nullable=True),
        sa.Column("moduller", sa.String(length=500), nullable=True),
        sa.Column("mesaj", sa.Text(), nullable=True),
        sa.Column("email_gonderildi", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_read", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("idx_demo_request_created", "demo_requests", ["created_at"])


def downgrade():
    op.drop_index("idx_demo_request_created", table_name="demo_requests")
    op.drop_table("demo_requests")
