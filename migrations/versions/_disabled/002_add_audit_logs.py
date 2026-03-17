"""
Add audit logs table
Sprint 5-6: Güvenlik ve Stabilite

Revision ID: 002
Revises: 001
Create Date: 2026-03-13
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade():
    """Audit logs tablosunu oluştur"""
    
    op.create_table(
        'audit_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('username', sa.String(length=100), nullable=True),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=50), nullable=False),
        sa.Column('resource_type', sa.String(length=50), nullable=True),
        sa.Column('resource_id', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
        sa.Column('request_method', sa.String(length=10), nullable=True),
        sa.Column('request_path', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # İndeksler
    op.create_index('idx_audit_user', 'audit_logs', ['user_id', 'created_at'])
    op.create_index('idx_audit_tenant', 'audit_logs', ['tenant_id', 'created_at'])
    op.create_index('idx_audit_action', 'audit_logs', ['action', 'created_at'])
    op.create_index('idx_audit_resource', 'audit_logs', ['resource_type', 'resource_id'])
    
    # Foreign keys
    op.create_foreign_key(
        'fk_audit_logs_user_id',
        'audit_logs', 'users',
        ['user_id'], ['id'],
        ondelete='SET NULL'
    )
    
    op.create_foreign_key(
        'fk_audit_logs_tenant_id',
        'audit_logs', 'tenants',
        ['tenant_id'], ['id'],
        ondelete='SET NULL'
    )


def downgrade():
    """Audit logs tablosunu kaldır"""
    
    op.drop_constraint('fk_audit_logs_tenant_id', 'audit_logs', type_='foreignkey')
    op.drop_constraint('fk_audit_logs_user_id', 'audit_logs', type_='foreignkey')
    
    op.drop_index('idx_audit_resource', table_name='audit_logs')
    op.drop_index('idx_audit_action', table_name='audit_logs')
    op.drop_index('idx_audit_tenant', table_name='audit_logs')
    op.drop_index('idx_audit_user', table_name='audit_logs')
    
    op.drop_table('audit_logs')
