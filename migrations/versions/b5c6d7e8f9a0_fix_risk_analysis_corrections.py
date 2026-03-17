"""fix: risk_analysis_corrections

Revision ID: b5c6d7e8f9a0
Revises: 0de355ae95f4
Create Date: 2026-02-23

Risk-1: Auth fix (decorators) - code change only, no migration
Risk-2: Import fix (process) - code change only, no migration
Risk-3: Soft delete & consistency
  - IndividualPerformanceIndicator: add is_active
  - IndividualActivity: add is_active
  - KpiData: rename is_deleted to is_active, reverse logic
"""
from alembic import op
import sqlalchemy as sa


revision = 'b5c6d7e8f9a0'
down_revision = '0de355ae95f4'
branch_labels = None
depends_on = None


def upgrade():
    # IndividualPerformanceIndicator: add is_active (SQLite supports ADD COLUMN)
    op.add_column('individual_performance_indicators', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index('ix_individual_performance_indicators_is_active', 'individual_performance_indicators', ['is_active'], unique=False)

    # IndividualActivity: add is_active
    op.add_column('individual_activities', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
    op.create_index('ix_individual_activities_is_active', 'individual_activities', ['is_active'], unique=False)

    # KpiData: is_deleted -> is_active (reverse logic)
    # 1. Add is_active with default True (SQLite-friendly: no ALTER needed)
    op.add_column('kpi_data', sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()))
    # 2. Migrate: is_active = 0 WHERE is_deleted = 1 (soft-deleted rows)
    op.execute("UPDATE kpi_data SET is_active = 0 WHERE is_deleted = 1")
    # 3. Drop is_deleted
    op.drop_column('kpi_data', 'is_deleted')
    # 4. Create index
    op.create_index('ix_kpi_data_is_active', 'kpi_data', ['is_active'], unique=False)


def downgrade():
    # KpiData: revert is_active -> is_deleted
    op.add_column('kpi_data', sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default=sa.false()))
    op.execute("UPDATE kpi_data SET is_deleted = 1 WHERE is_active = 0")
    op.drop_index('ix_kpi_data_is_active', table_name='kpi_data')
    op.drop_column('kpi_data', 'is_active')

    # IndividualActivity: drop is_active
    op.drop_index('ix_individual_activities_is_active', table_name='individual_activities')
    op.drop_column('individual_activities', 'is_active')

    # IndividualPerformanceIndicator: drop is_active
    op.drop_index('ix_individual_performance_indicators_is_active', table_name='individual_performance_indicators')
    op.drop_column('individual_performance_indicators', 'is_active')
