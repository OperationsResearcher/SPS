"""Çoklu proje lideri: project_leaders ilişki tablosu

Revision ID: c7d8e9f0a1b2
Revises: a1c2d3e4f5a6
Create Date: 2026-03-19

Mevcut project.manager_id değerleri tabloya kopyalanır; manager_id sütunu (birincil lider) korunur.
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


revision = "c7d8e9f0a1b2"
down_revision = "a1c2d3e4f5a6"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "project_leaders",
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("project_id", "user_id"),
    )
    op.get_bind().execute(
        text(
            "INSERT INTO project_leaders (project_id, user_id) "
            "SELECT id, manager_id FROM project WHERE manager_id IS NOT NULL"
        )
    )


def downgrade():
    op.drop_table("project_leaders")
