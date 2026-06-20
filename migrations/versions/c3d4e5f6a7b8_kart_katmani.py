"""KART katmanı: system_cards + card_data_sources

SaaS hiyerarşisinin en alt katmanı (paket→modül→bileşen→KART) + kart-içi veri
paket-farkındalığı (card_data_sources.required_component_code).

Toplamsal — yalnızca 2 YENİ tablo. Mevcut veri/tablolara dokunmaz.
downgrade() iki tabloyu drop eder → tam geri-dönüşlü.

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-20
"""
from alembic import op
import sqlalchemy as sa


revision = "c3d4e5f6a7b8"
down_revision = "b2c3d4e5f6a7"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "system_cards",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=128), nullable=False),
        sa.Column("code", sa.String(length=80), nullable=False),
        sa.Column("component_id", sa.Integer(), nullable=True),
        sa.Column("sira", sa.Integer(), nullable=True),
        sa.Column("description", sa.String(length=512), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["component_id"], ["system_components.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("code"),
    )
    with op.batch_alter_table("system_cards", schema=None) as b:
        b.create_index(b.f("ix_system_cards_component_id"), ["component_id"], unique=False)

    op.create_table(
        "card_data_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("data_key", sa.String(length=120), nullable=False),
        sa.Column("required_component_code", sa.String(length=80), nullable=True),
        sa.Column("label", sa.String(length=200), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["card_id"], ["system_cards.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("card_id", "data_key", name="uq_card_data_key"),
    )
    with op.batch_alter_table("card_data_sources", schema=None) as b:
        b.create_index(b.f("ix_card_data_sources_card_id"), ["card_id"], unique=False)
        b.create_index(b.f("ix_card_data_sources_required_component_code"), ["required_component_code"], unique=False)


def downgrade() -> None:
    op.drop_table("card_data_sources")
    op.drop_table("system_cards")
