"""Process sub_strategy links with contribution_pct

Revision ID: a7f8c9d0e1f2
Revises: a1b2c3d4e5f6
Create Date: 2026-02-23

Replace process_sub_strategies with process_sub_strategy_links (contribution_pct).
"""
from alembic import op
import sqlalchemy as sa


revision = 'a7f8c9d0e1f2'
down_revision = 'a1b2c3d4e5f6'
branch_labels = None
depends_on = None


def upgrade():
    # Create new table with contribution_pct
    op.create_table('process_sub_strategy_links',
        sa.Column('process_id', sa.Integer(), nullable=False),
        sa.Column('sub_strategy_id', sa.Integer(), nullable=False),
        sa.Column('contribution_pct', sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(['process_id'], ['processes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sub_strategy_id'], ['sub_strategies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('process_id', 'sub_strategy_id')
    )

    # Migrate data from process_sub_strategies (contribution_pct = NULL for legacy)
    op.execute("""
        INSERT INTO process_sub_strategy_links (process_id, sub_strategy_id, contribution_pct)
        SELECT process_id, sub_strategy_id, NULL FROM process_sub_strategies
    """)

    op.drop_table('process_sub_strategies')


def downgrade():
    op.create_table('process_sub_strategies',
        sa.Column('process_id', sa.Integer(), nullable=False),
        sa.Column('sub_strategy_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['process_id'], ['processes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['sub_strategy_id'], ['sub_strategies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('process_id', 'sub_strategy_id')
    )
    op.execute("""
        INSERT INTO process_sub_strategies (process_id, sub_strategy_id)
        SELECT process_id, sub_strategy_id FROM process_sub_strategy_links
    """)
    op.drop_table('process_sub_strategy_links')
