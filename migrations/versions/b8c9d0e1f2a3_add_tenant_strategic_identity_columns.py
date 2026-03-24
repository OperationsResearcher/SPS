"""Add tenant strategic identity columns (purpose, vision, etc.)

Revision ID: b8c9d0e1f2a3
Revises: 4f3a2b1c9d8e
Create Date: 2026-03-24

Tenant modelindeki Yeni Stratejik Kimlik alanlari: purpose, vision, core_values,
code_of_ethics, quality_policy. Model ile DB senkronize edildi.
"""
from alembic import op
import sqlalchemy as sa


revision = "b8c9d0e1f2a3"
down_revision = "4f3a2b1c9d8e"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("tenants", schema=None) as batch_op:
        batch_op.add_column(sa.Column("purpose", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("vision", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("core_values", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("code_of_ethics", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("quality_policy", sa.Text(), nullable=True))


def downgrade():
    with op.batch_alter_table("tenants", schema=None) as batch_op:
        batch_op.drop_column("quality_policy")
        batch_op.drop_column("code_of_ethics")
        batch_op.drop_column("core_values")
        batch_op.drop_column("vision")
        batch_op.drop_column("purpose")
