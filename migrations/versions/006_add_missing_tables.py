"""Add missing tables: audit_logs, push_subscriptions, tenant_email_configs

Revision ID: 006_add_missing_tables
Revises: b5c6d7e8f9a0
Create Date: 2026-03-15

Bu migration 001-005 numaralı manuel script'lerin Alembic zincirine
dahil edilmemiş tablolarını ve yeni tenant_email_configs tablosunu ekler.
"""
from alembic import op
import sqlalchemy as sa

revision = '006_add_missing_tables'
down_revision = 'b5c6d7e8f9a0'
branch_labels = None
depends_on = None


def _table_exists(name):
    from alembic import op as _op
    from sqlalchemy import inspect
    bind = _op.get_bind()
    return inspect(bind).has_table(name)


def upgrade():
    # ── audit_logs ────────────────────────────────────────────────────────────
    if not _table_exists('audit_logs'):
        op.create_table(
            'audit_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=True),
            sa.Column('tenant_id', sa.Integer(), nullable=True),
            sa.Column('action', sa.String(100), nullable=False),
            sa.Column('resource_type', sa.String(100), nullable=True),
            sa.Column('resource_id', sa.Integer(), nullable=True),
            sa.Column('old_values', sa.JSON(), nullable=True),
            sa.Column('new_values', sa.JSON(), nullable=True),
            sa.Column('ip_address', sa.String(45), nullable=True),
            sa.Column('user_agent', sa.String(500), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('idx_audit_log_user', 'audit_logs', ['user_id', 'created_at'])
        op.create_index('idx_audit_log_resource', 'audit_logs', ['resource_type', 'resource_id'])
        op.create_index('idx_audit_log_tenant', 'audit_logs', ['tenant_id', 'created_at'])

    # ── push_subscriptions ────────────────────────────────────────────────────
    if not _table_exists('push_subscriptions'):
        op.create_table(
            'push_subscriptions',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('user_id', sa.Integer(), nullable=False),
            sa.Column('endpoint', sa.Text(), nullable=False),
            sa.Column('p256dh', sa.String(255), nullable=False),
            sa.Column('auth', sa.String(255), nullable=False),
            sa.Column('is_active', sa.Boolean(), nullable=True, server_default='1'),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.Column('updated_at', sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(['user_id'], ['users.id']),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index('idx_push_subscription_user', 'push_subscriptions', ['user_id', 'is_active'])
        op.create_index('idx_push_subscription_endpoint', 'push_subscriptions', ['endpoint'])

    # ── tenant_email_configs ──────────────────────────────────────────────────
    if not _table_exists('tenant_email_configs'):
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
    op.drop_index('idx_push_subscription_endpoint', table_name='push_subscriptions')
    op.drop_index('idx_push_subscription_user', table_name='push_subscriptions')
    op.drop_table('push_subscriptions')
    op.drop_index('idx_audit_log_tenant', table_name='audit_logs')
    op.drop_index('idx_audit_log_resource', table_name='audit_logs')
    op.drop_index('idx_audit_log_user', table_name='audit_logs')
    op.drop_table('audit_logs')
