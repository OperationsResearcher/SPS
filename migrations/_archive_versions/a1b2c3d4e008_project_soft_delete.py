"""project_soft_delete — Project tablosuna is_active, deleted_at, deleted_by kolonları

Revision ID: a1b2c3d4e008
Revises: z3a4b5c6d007
Create Date: 2026-05-19

project tablosuna soft delete altyapısı eklenir:
  - is_active (Boolean, NOT NULL, default True)
  - deleted_at (DateTime, nullable)
  - deleted_by (Integer FK → users.id, nullable)
Mevcut satırlar is_active=True, deleted_at=NULL olarak işaretlenir.
"""

from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e008"
down_revision = "d4e5f6g7h8i9"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("project") as batch_op:
        batch_op.add_column(
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true())
        )
        batch_op.add_column(
            sa.Column("deleted_at", sa.DateTime(), nullable=True)
        )
        batch_op.add_column(
            sa.Column(
                "deleted_by",
                sa.Integer(),
                sa.ForeignKey("users.id", ondelete="SET NULL"),
                nullable=True,
            )
        )
        batch_op.create_index("ix_project_is_active", ["is_active"])

    # Arşivlenmiş projeler is_active=False olarak işaretlenir
    op.execute(
        "UPDATE project SET is_active = FALSE WHERE is_archived = TRUE AND is_active = TRUE"
    )


def downgrade():
    with op.batch_alter_table("project") as batch_op:
        batch_op.drop_index("ix_project_is_active")
        batch_op.drop_column("deleted_by")
        batch_op.drop_column("deleted_at")
        batch_op.drop_column("is_active")
