"""Add strategies and sub_strategies tables

Revision ID: c8d7e6f5a4b3
Revises: 87e9b1dcd08d
Create Date: 2026-03-19

Process models (461675c755b0) process_kpis ve process_sub_strategies tabloları
sub_strategies tablosuna FK referans veriyor. Bu migration o tabloları oluşturur.
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c8d7e6f5a4b3'
down_revision = '87e9b1dcd08d'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('strategies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('strategies', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_strategies_code'), ['code'], unique=False)
        batch_op.create_index(batch_op.f('ix_strategies_is_active'), ['is_active'], unique=False)
        batch_op.create_index(batch_op.f('ix_strategies_tenant_id'), ['tenant_id'], unique=False)

    op.create_table('sub_strategies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('strategy_id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=20), nullable=True),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['strategy_id'], ['strategies.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    with op.batch_alter_table('sub_strategies', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_sub_strategies_code'), ['code'], unique=False)
        batch_op.create_index(batch_op.f('ix_sub_strategies_is_active'), ['is_active'], unique=False)
        batch_op.create_index(batch_op.f('ix_sub_strategies_strategy_id'), ['strategy_id'], unique=False)


def downgrade():
    op.drop_table('sub_strategies')
    op.drop_table('strategies')
