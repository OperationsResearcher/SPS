"""Add project and task tables (legacy / proje modulu)

Revision ID: c1d2e3f4a5b6
Revises: b8c9d0e1f2a3
Create Date: 2026-03-24

SQLite'taki project ve task verilerini tasiyabilmek icin.
kurum_id = tenant_id (tenants.id)
"""
from alembic import op
import sqlalchemy as sa


revision = "c1d2e3f4a5b6"
down_revision = "b8c9d0e1f2a3"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "project",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("kurum_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("manager_id", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("priority", sa.String(length=50), nullable=True),
        sa.Column("is_archived", sa.Boolean(), nullable=True),
        sa.Column("health_score", sa.Integer(), nullable=True),
        sa.Column("health_status", sa.String(length=50), nullable=True),
        sa.Column("notification_settings", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["kurum_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["manager_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_kurum_id", "project", ["kurum_id"], unique=False)
    op.create_index("ix_project_manager_id", "project", ["manager_id"], unique=False)

    op.create_table(
        "task",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("assignee_id", sa.Integer(), nullable=True),
        sa.Column("reporter_id", sa.Integer(), nullable=False),
        sa.Column("external_assignee_name", sa.String(length=200), nullable=True),
        sa.Column("parent_id", sa.Integer(), nullable=True),
        sa.Column("estimated_time", sa.Float(), nullable=True),
        sa.Column("actual_time", sa.Float(), nullable=True),
        sa.Column("progress", sa.Integer(), nullable=True),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("is_measurable", sa.Boolean(), nullable=True),
        sa.Column("planned_output_value", sa.Float(), nullable=True),
        sa.Column("related_indicator_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("priority", sa.String(length=50), nullable=True),
        sa.Column("is_archived", sa.Boolean(), nullable=True),
        sa.Column("due_date", sa.Date(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("reminder_date", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("process_kpi_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(["assignee_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["parent_id"], ["task.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["reporter_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["process_kpi_id"], ["process_kpis.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_project_id", "task", ["project_id"], unique=False)
    op.create_index("ix_task_parent_id", "task", ["parent_id"], unique=False)


def downgrade():
    op.drop_table("task")
    op.drop_table("project")
