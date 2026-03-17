"""add_notifications_table

Revision ID: 644e8ba0651f
Revises: f7920a9ab0db
Create Date: 2026-02-23 00:39:45.779230

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '644e8ba0651f'
down_revision = 'f7920a9ab0db'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=True),
        sa.Column('tip', sa.String(50), nullable=False),
        sa.Column('baslik', sa.String(200), nullable=False),
        sa.Column('mesaj', sa.Text(), nullable=True),
        sa.Column('link', sa.String(500), nullable=True),
        sa.Column('okundu', sa.Boolean(), nullable=False, default=False),
        sa.Column('process_id', sa.Integer(), nullable=True),
        sa.Column('ilgili_user_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.ForeignKeyConstraint(['ilgili_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_notifications_user_id'), 'notifications', ['user_id'], unique=False)
    op.create_index(op.f('ix_notifications_tenant_id'), 'notifications', ['tenant_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_notifications_tenant_id'), table_name='notifications')
    op.drop_index(op.f('ix_notifications_user_id'), table_name='notifications')
    op.drop_table('notifications')
