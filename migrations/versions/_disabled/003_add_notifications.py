"""
Add notifications tables
Sprint 7-9: Real-Time ve Bildirimler

Revision ID: 003
Revises: 002
Create Date: 2026-03-13
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade():
    """Notifications tablolarını oluştur"""
    
    # Notifications table
    op.create_table(
        'notifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=50), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('priority', sa.String(length=20), nullable=True),
        sa.Column('action_url', sa.String(length=500), nullable=True),
        sa.Column('metadata', sa.JSON(), nullable=True),
        sa.Column('is_read', sa.Boolean(), nullable=False, default=False),
        sa.Column('read_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # İndeksler
    op.create_index('idx_notification_user_read', 'notifications', ['user_id', 'is_read', 'created_at'])
    op.create_index('idx_notification_type', 'notifications', ['type', 'created_at'])
    op.create_index('idx_notification_priority', 'notifications', ['priority', 'is_read'])
    
    # Foreign key
    op.create_foreign_key(
        'fk_notifications_user_id',
        'notifications', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )
    
    # Notification Preferences table
    op.create_table(
        'notification_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('email_performance_alerts', sa.Boolean(), nullable=True, default=True),
        sa.Column('email_task_reminders', sa.Boolean(), nullable=True, default=True),
        sa.Column('email_collaboration', sa.Boolean(), nullable=True, default=True),
        sa.Column('email_achievements', sa.Boolean(), nullable=True, default=False),
        sa.Column('email_system', sa.Boolean(), nullable=True, default=True),
        sa.Column('inapp_performance_alerts', sa.Boolean(), nullable=True, default=True),
        sa.Column('inapp_task_reminders', sa.Boolean(), nullable=True, default=True),
        sa.Column('inapp_collaboration', sa.Boolean(), nullable=True, default=True),
        sa.Column('inapp_achievements', sa.Boolean(), nullable=True, default=True),
        sa.Column('inapp_system', sa.Boolean(), nullable=True, default=True),
        sa.Column('push_enabled', sa.Boolean(), nullable=True, default=False),
        sa.Column('push_performance_alerts', sa.Boolean(), nullable=True, default=True),
        sa.Column('push_task_reminders', sa.Boolean(), nullable=True, default=True),
        sa.Column('daily_digest', sa.Boolean(), nullable=True, default=False),
        sa.Column('weekly_digest', sa.Boolean(), nullable=True, default=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    # Foreign key
    op.create_foreign_key(
        'fk_notification_preferences_user_id',
        'notification_preferences', 'users',
        ['user_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    """Notifications tablolarını kaldır"""
    
    op.drop_constraint('fk_notification_preferences_user_id', 'notification_preferences', type_='foreignkey')
    op.drop_table('notification_preferences')
    
    op.drop_constraint('fk_notifications_user_id', 'notifications', type_='foreignkey')
    op.drop_index('idx_notification_priority', table_name='notifications')
    op.drop_index('idx_notification_type', table_name='notifications')
    op.drop_index('idx_notification_user_read', table_name='notifications')
    op.drop_table('notifications')
