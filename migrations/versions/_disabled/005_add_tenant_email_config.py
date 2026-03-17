"""Add tenant_email_configs table

Revision ID: 005
Revises: 004
Create Date: 2026-03-15
"""
from alembic import op
import sqlalchemy as sa

revision = '005'
down_revision = '004'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'tenant_email_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('use_custom_smtp', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('smtp_host', sa.String(255), nullable=True),
        sa.Column('smtp_port', sa.Integer(), nullable=True, server_default='587'),
        sa.Column('smtp_use_tls', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('smtp_use_ssl', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('smtp_username', sa.String(255), nullable=True),
        sa.Column('smtp_password', sa.String(512), nullable=True),
        sa.Column('sender_name', sa.String(128), nullable=True),
        sa.Column('sender_email', sa.String(255), nullable=True),
        sa.Column('notify_on_process_assign', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('notify_on_kpi_change', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('notify_on_activity_add', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('notify_on_task_assign', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('updated_by', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id']),
        sa.ForeignKeyConstraint(['updated_by'], ['users.id']),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('tenant_id'),
    )
    op.create_index('idx_tenant_email_config_tenant', 'tenant_email_configs', ['tenant_id'])


def downgrade():
    op.drop_index('idx_tenant_email_config_tenant', table_name='tenant_email_configs')
    op.drop_table('tenant_email_configs')
