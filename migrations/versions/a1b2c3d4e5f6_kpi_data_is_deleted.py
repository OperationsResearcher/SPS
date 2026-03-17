"""Add is_deleted to kpi_data for soft delete

Revision ID: a1b2c3d4e5f6
Revises: 644e8ba0651f
Create Date: 2026-02-23

"""
from alembic import op
import sqlalchemy as sa


revision = 'a1b2c3d4e5f6'
down_revision = '644e8ba0651f'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('kpi_data', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade():
    op.drop_column('kpi_data', 'is_deleted')
