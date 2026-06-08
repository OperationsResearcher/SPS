"""project_leaders / project_members / project_observers (PostgreSQL users FK)

Revision ID: f1a2b3c4d5e6
Revises: eab1c2d3f4a5

Bazi PostgreSQL kurulumlarinda proje tablolari vardi ancak coklu-lider iliski
tablolari yoktu. FK hedefi `users.id` (legacy `user` degil).
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision = "f1a2b3c4d5e6"
down_revision = "eab1c2d3f4a5"
branch_labels = None
depends_on = None


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return insp.has_table(name)


def upgrade():
    if not _table_exists("project"):
        return

    if not _table_exists("project_leaders"):
        op.create_table(
            "project_leaders",
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("project_id", "user_id"),
        )
        op.get_bind().execute(
            text(
                "INSERT INTO project_leaders (project_id, user_id) "
                "SELECT p.id, p.manager_id FROM project p "
                "WHERE p.manager_id IS NOT NULL "
                "AND NOT EXISTS ("
                "  SELECT 1 FROM project_leaders pl "
                "  WHERE pl.project_id = p.id AND pl.user_id = p.manager_id"
                ")"
            )
        )

    if not _table_exists("project_members"):
        op.create_table(
            "project_members",
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("project_id", "user_id"),
        )

    if not _table_exists("project_observers"):
        op.create_table(
            "project_observers",
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("user_id", sa.Integer(), nullable=False),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("project_id", "user_id"),
        )


def downgrade():
    if _table_exists("project_observers"):
        op.drop_table("project_observers")
    if _table_exists("project_members"):
        op.drop_table("project_members")
    if _table_exists("project_leaders"):
        op.drop_table("project_leaders")
