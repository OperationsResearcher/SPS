# -*- coding: utf-8 -*-
"""Süreç tablosuna parent_id (üst süreç) sütunu ekler. Mevcut süreçler bağımsız kalır (parent_id=NULL).

Revision ID: add_surec_parent
Revises: b1a2c3d4e5f6
Create Date: 2026-01-31

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_surec_parent'
down_revision = 'b1a2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # SQLite: ADD COLUMN parent_id, self-referencing FK. Mevcut kayıtlar NULL kalır.
    try:
        op.add_column('surec', sa.Column('parent_id', sa.Integer(), nullable=True))
        op.create_foreign_key(
            'fk_surec_parent_id_surec',
            'surec', 'surec',
            ['parent_id'], ['id'],
            ondelete='SET NULL'
        )
        op.create_index('ix_surec_parent_id', 'surec', ['parent_id'], unique=False)
    except Exception:
        # SQLite bazen FK adımında sorun çıkarabilir; sadece sütun ekle
        op.add_column('surec', sa.Column('parent_id', sa.Integer(), nullable=True))
        op.create_index('ix_surec_parent_id', 'surec', ['parent_id'], unique=False)


def downgrade():
    op.drop_index('ix_surec_parent_id', table_name='surec')
    try:
        op.drop_constraint('fk_surec_parent_id_surec', 'surec', type_='foreignkey')
    except Exception:
        pass
    op.drop_column('surec', 'parent_id')
