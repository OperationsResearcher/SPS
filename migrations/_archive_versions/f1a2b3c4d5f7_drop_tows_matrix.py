"""TOWS matrisi tablosunu kaldır (K-Radar ile değiştirilecek)

Revision ID: f1a2b3c4d5f7
Revises: f1a2b3c4d5e6
Create Date: 2026-03-26

Eski `tows_matrix` tablosu ve verileri silinir. Geri alma (downgrade) boş tabloyu yeniden oluşturur.
"""
from alembic import op
import sqlalchemy as sa


revision = "f1a2b3c4d5f7"
down_revision = "f1a2b3c4d5e6"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if insp.has_table("tows_matrix"):
        op.drop_table("tows_matrix")


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if insp.has_table("tows_matrix"):
        return
    op.create_table(
        "tows_matrix",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("kurum_id", sa.Integer(), nullable=False),
        sa.Column("strength_id", sa.Integer(), nullable=False),
        sa.Column("opportunity_threat_id", sa.Integer(), nullable=False),
        sa.Column("strategy_text", sa.Text(), nullable=False),
        sa.Column("action_plan", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["kurum_id"], ["kurum.id"]),
        sa.ForeignKeyConstraint(["opportunity_threat_id"], ["analysis_item.id"]),
        sa.ForeignKeyConstraint(["strength_id"], ["analysis_item.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tows_matrix_kurum_id", "tows_matrix", ["kurum_id"], unique=False)
    op.create_index("ix_tows_matrix_strength_id", "tows_matrix", ["strength_id"], unique=False)
    op.create_index(
        "ix_tows_matrix_opportunity_threat_id",
        "tows_matrix",
        ["opportunity_threat_id"],
        unique=False,
    )
    op.create_index("ix_tows_matrix_created_at", "tows_matrix", ["created_at"], unique=False)
