"""task_evm_fields — PlanProjectTask EVM + dependency (S62)

Revision ID: e8f9g0h1i012
Revises: d7e8f9g0h011
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa


revision = "e8f9g0h1i012"
down_revision = "d7e8f9g0h011"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("plan_project_tasks",
                  sa.Column("progress_pct", sa.Float(), nullable=False, server_default="0"))
    op.add_column("plan_project_tasks",
                  sa.Column("planned_budget", sa.Numeric(18, 2), nullable=True))
    op.add_column("plan_project_tasks",
                  sa.Column("actual_cost", sa.Numeric(18, 2), nullable=True, server_default="0"))
    op.add_column("plan_project_tasks",
                  sa.Column("depends_on_task_id", sa.Integer(),
                            sa.ForeignKey("plan_project_tasks.id", ondelete="SET NULL"),
                            nullable=True))
    op.create_index("idx_task_depends", "plan_project_tasks", ["depends_on_task_id"])


def downgrade():
    op.drop_index("idx_task_depends", table_name="plan_project_tasks")
    op.drop_column("plan_project_tasks", "depends_on_task_id")
    op.drop_column("plan_project_tasks", "actual_cost")
    op.drop_column("plan_project_tasks", "planned_budget")
    op.drop_column("plan_project_tasks", "progress_pct")
