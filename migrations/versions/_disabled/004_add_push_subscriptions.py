"""Add push subscriptions table

Revision ID: 004
Revises: 003
Create Date: 2026-03-13

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '004'
down_revision = '003'
branch_labels = None
depends_on = None


def upgrade():
    # Create push_subscriptions table
    op.create_table(
        'push_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('endpoint', sa.Text(), nullable=False),
        sa.Column('p256dh', sa.String(length=255), nullable=False),
        sa.Column('auth', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True, default=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(
        'idx_push_subscription_user',
        'push_subscriptions',
        ['user_id', 'is_active']
    )
    
    op.create_index(
        'idx_push_subscription_endpoint',
        'push_subscriptions',
        ['endpoint'],
        unique=False
    )


def downgrade():
    op.drop_index('idx_push_subscription_endpoint', table_name='push_subscriptions')
    op.drop_index('idx_push_subscription_user', table_name='push_subscriptions')
    op.drop_table('push_subscriptions')
