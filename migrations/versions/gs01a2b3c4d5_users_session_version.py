"""users.session_version — parola değişince açık oturumları düşür (GUV-11)

Revision ID: gs01a2b3c4d5
Revises: hd01a2b3c4d5
Create Date: 2026-09-30
"""
from alembic import op
import sqlalchemy as sa


revision = "gs01a2b3c4d5"
down_revision = "hd01a2b3c4d5"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("users") as batch:
        batch.add_column(
            sa.Column("session_version", sa.Integer(), nullable=False, server_default="0")
        )


def downgrade():
    with op.batch_alter_table("users") as batch:
        batch.drop_column("session_version")
