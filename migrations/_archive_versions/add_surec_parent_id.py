# -*- coding: utf-8 -*-
"""Süreç tablosuna parent_id (üst süreç) sütunu ekler. Mevcut süreçler bağımsız kalır (parent_id=NULL).

Revision ID: add_surec_parent
Revises: e7a8b9c0d1e2
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_surec_parent'
down_revision = 'e7a8b9c0d1e2'
branch_labels = None
depends_on = None


def upgrade():
    # Eski şema: tablo adı `surec`. Güncel Alembic zincirinde süreçler `processes` + 461675'te parent_id var.
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("surec"):
        return
    cols = {c["name"] for c in insp.get_columns("surec")}
    if "parent_id" in cols:
        return
    try:
        op.add_column("surec", sa.Column("parent_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_surec_parent_id_surec",
            "surec",
            "surec",
            ["parent_id"],
            ["id"],
            ondelete="SET NULL",
        )
        op.create_index("ix_surec_parent_id", "surec", ["parent_id"], unique=False)
    except Exception:
        op.add_column("surec", sa.Column("parent_id", sa.Integer(), nullable=True))
        op.create_index("ix_surec_parent_id", "surec", ["parent_id"], unique=False)


def downgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if not insp.has_table("surec"):
        return
    cols = {c["name"] for c in insp.get_columns("surec")}
    if "parent_id" not in cols:
        return
    try:
        op.drop_index("ix_surec_parent_id", table_name="surec")
    except Exception:
        pass
    try:
        op.drop_constraint("fk_surec_parent_id_surec", "surec", type_="foreignkey")
    except Exception:
        pass
    op.drop_column("surec", "parent_id")
