"""Add tenant logo columns.

Revision ID: u4v5w6x7y001
Revises: t2u3v4w5x001
Create Date: 2026-03-29
"""

from alembic import op
import sqlalchemy as sa


revision = "u4v5w6x7y001"
down_revision = "t2u3v4w5x001"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("tenants", schema=None) as batch_op:
        batch_op.add_column(sa.Column("logo_path", sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column("logo_updated_at", sa.DateTime(), nullable=True))


def downgrade():
    with op.batch_alter_table("tenants", schema=None) as batch_op:
        batch_op.drop_column("logo_updated_at")
        batch_op.drop_column("logo_path")
