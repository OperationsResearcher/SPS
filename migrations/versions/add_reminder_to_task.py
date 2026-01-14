"""Add reminder_date column to task table

Revision ID: task_reminder_001
Revises: 
Create Date: 2026-01-13 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'task_reminder_001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add reminder_date column to task table
    op.add_column('task', sa.Column('reminder_date', sa.DateTime(), nullable=True))


def downgrade():
    # Remove reminder_date column from task table
    op.drop_column('task', 'reminder_date')
