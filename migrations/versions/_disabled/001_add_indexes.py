"""Add performance indexes

Revision ID: 001_add_indexes
Revises: 
Create Date: 2026-03-13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_add_indexes'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Add indexes for better query performance"""
    
    # KPI Data indexes
    op.create_index(
        'idx_kpi_data_lookup',
        'kpi_data',
        ['process_kpi_id', 'data_date', 'is_active'],
        unique=False
    )
    
    op.create_index(
        'idx_kpi_data_created_by',
        'kpi_data',
        ['created_by', 'is_active'],
        unique=False
    )
    
    # Process indexes
    op.create_index(
        'idx_process_tenant_active',
        'processes',
        ['tenant_id', 'is_active', 'parent_id'],
        unique=False
    )
    
    op.create_index(
        'idx_process_code',
        'processes',
        ['code', 'tenant_id'],
        unique=False
    )
    
    # User indexes
    op.create_index(
        'idx_user_tenant_role',
        'users',
        ['tenant_id', 'role_id', 'is_active'],
        unique=False
    )
    
    op.create_index(
        'idx_user_email_active',
        'users',
        ['email', 'is_active'],
        unique=False
    )
    
    # ProcessKpi indexes
    op.create_index(
        'idx_process_kpi_process',
        'process_kpis',
        ['process_id', 'is_active'],
        unique=False
    )
    
    # Strategy indexes
    op.create_index(
        'idx_strategy_tenant',
        'strategies',
        ['tenant_id', 'is_active'],
        unique=False
    )
    
    op.create_index(
        'idx_sub_strategy_strategy',
        'sub_strategies',
        ['strategy_id', 'is_active'],
        unique=False
    )
    
    # Activity Track indexes
    op.create_index(
        'idx_activity_track_activity',
        'activity_tracks',
        ['process_activity_id', 'year', 'month'],
        unique=False
    )
    
    print("✅ Performance indexes created successfully")


def downgrade():
    """Remove indexes"""
    
    op.drop_index('idx_kpi_data_lookup', table_name='kpi_data')
    op.drop_index('idx_kpi_data_created_by', table_name='kpi_data')
    op.drop_index('idx_process_tenant_active', table_name='processes')
    op.drop_index('idx_process_code', table_name='processes')
    op.drop_index('idx_user_tenant_role', table_name='users')
    op.drop_index('idx_user_email_active', table_name='users')
    op.drop_index('idx_process_kpi_process', table_name='process_kpis')
    op.drop_index('idx_strategy_tenant', table_name='strategies')
    op.drop_index('idx_sub_strategy_strategy', table_name='sub_strategies')
    op.drop_index('idx_activity_track_activity', table_name='activity_tracks')
    
    print("✅ Performance indexes removed")
