"""Proje yardımcı tabloları ve raid_item (PostgreSQL users/project uyumu)

Revision ID: eab1c2d3f4a5
Revises: c1d2e3f4a5b6
Create Date: 2026-03-24

ORM (models/project.py) ile uyumlu şema; owner_id vb. FK hedefi `users.id`.
Mevcut DB'de tablo varsa oluşturma atlanır (idempotent upgrade).
"""

from alembic import op
import sqlalchemy as sa

revision = "eab1c2d3f4a5"
down_revision = "c1d2e3f4a5b6"
branch_labels = None
depends_on = None


def _table_exists(name: str) -> bool:
    bind = op.get_bind()
    insp = sa.inspect(bind)
    return insp.has_table(name)


def upgrade():
    # ── project_risk ─────────────────────────────────────────────────────
    if not _table_exists("project_risk"):
        op.create_table(
            "project_risk",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("probability", sa.String(length=20), nullable=True),
            sa.Column("impact", sa.String(length=20), nullable=True),
            sa.Column("status", sa.String(length=20), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    # ── working_day ──────────────────────────────────────────────────────
    if not _table_exists("working_day"):
        op.create_table(
            "working_day",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("project_id", sa.Integer(), nullable=True),
            sa.Column("date", sa.Date(), nullable=False),
            sa.Column("is_working", sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_working_day_project_id", "working_day", ["project_id"], unique=False)
        op.create_index("ix_working_day_date", "working_day", ["date"], unique=False)

    # ── sla ──────────────────────────────────────────────────────────────
    if not _table_exists("sla"):
        op.create_table(
            "sla",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("project_id", sa.Integer(), nullable=True),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("target_hours", sa.Integer(), nullable=False),
            sa.Column("breach_policy", sa.String(length=200), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_sla_project_id", "sla", ["project_id"], unique=False)

    # ── integration_hook ─────────────────────────────────────────────────
    if not _table_exists("integration_hook"):
        op.create_table(
            "integration_hook",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("provider", sa.String(length=50), nullable=False),
            sa.Column("url", sa.String(length=500), nullable=False),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_integration_hook_project_id", "integration_hook", ["project_id"], unique=False)

    # ── rule_definition ──────────────────────────────────────────────────
    if not _table_exists("rule_definition"):
        op.create_table(
            "rule_definition",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("project_id", sa.Integer(), nullable=True),
            sa.Column("name", sa.String(length=200), nullable=False),
            sa.Column("trigger", sa.String(length=100), nullable=False),
            sa.Column("condition_json", sa.Text(), nullable=True),
            sa.Column("actions_json", sa.Text(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_rule_definition_project_id", "rule_definition", ["project_id"], unique=False)

    # ── capacity_plan ────────────────────────────────────────────────────
    if not _table_exists("capacity_plan"):
        op.create_table(
            "capacity_plan",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("project_id", sa.Integer(), nullable=True),
            sa.Column("user_id", sa.Integer(), nullable=True),
            sa.Column("weekly_hours", sa.Float(), nullable=False, server_default="40"),
            sa.Column("start_date", sa.Date(), nullable=True),
            sa.Column("end_date", sa.Date(), nullable=True),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_capacity_plan_project_id", "capacity_plan", ["project_id"], unique=False)
        op.create_index("ix_capacity_plan_user_id", "capacity_plan", ["user_id"], unique=False)

    # ── recurring_task ───────────────────────────────────────────────────
    if not _table_exists("recurring_task"):
        op.create_table(
            "recurring_task",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("cron_expr", sa.String(length=100), nullable=False),
            sa.Column("template_task_id", sa.Integer(), nullable=True),
            sa.Column("next_run_at", sa.DateTime(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=True),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["template_task_id"], ["task.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_recurring_task_project_id", "recurring_task", ["project_id"], unique=False)

    # ── task_baseline ─────────────────────────────────────────────────────
    if not _table_exists("task_baseline"):
        op.create_table(
            "task_baseline",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("task_id", sa.Integer(), nullable=False),
            sa.Column("planned_start", sa.Date(), nullable=True),
            sa.Column("planned_end", sa.Date(), nullable=True),
            sa.Column("planned_effort", sa.Float(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["task_id"], ["task.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_task_baseline_task_id", "task_baseline", ["task_id"], unique=False)

    # ── raid_item ────────────────────────────────────────────────────────
    if not _table_exists("raid_item"):
        op.create_table(
            "raid_item",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("project_id", sa.Integer(), nullable=False),
            sa.Column("item_type", sa.String(length=20), nullable=False),
            sa.Column("title", sa.String(length=200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("owner_id", sa.Integer(), nullable=True),
            sa.Column("status", sa.String(length=50), nullable=True),
            sa.Column("probability", sa.Integer(), nullable=True),
            sa.Column("impact", sa.Integer(), nullable=True),
            sa.Column("mitigation_plan", sa.Text(), nullable=True),
            sa.Column("assumption_validation_date", sa.Date(), nullable=True),
            sa.Column("assumption_validated", sa.Boolean(), nullable=True),
            sa.Column("assumption_notes", sa.Text(), nullable=True),
            sa.Column("issue_urgency", sa.String(length=50), nullable=True),
            sa.Column("issue_affected_work", sa.String(length=200), nullable=True),
            sa.Column("dependency_task_id", sa.Integer(), nullable=True),
            sa.Column("dependency_type", sa.String(length=50), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index("ix_raid_item_project_id", "raid_item", ["project_id"], unique=False)


def downgrade():
    if _table_exists("raid_item"):
        op.drop_index("ix_raid_item_project_id", table_name="raid_item")
        op.drop_table("raid_item")
    if _table_exists("task_baseline"):
        op.drop_index("ix_task_baseline_task_id", table_name="task_baseline")
        op.drop_table("task_baseline")
    if _table_exists("recurring_task"):
        op.drop_index("ix_recurring_task_project_id", table_name="recurring_task")
        op.drop_table("recurring_task")
    if _table_exists("capacity_plan"):
        op.drop_index("ix_capacity_plan_user_id", table_name="capacity_plan")
        op.drop_index("ix_capacity_plan_project_id", table_name="capacity_plan")
        op.drop_table("capacity_plan")
    if _table_exists("rule_definition"):
        op.drop_index("ix_rule_definition_project_id", table_name="rule_definition")
        op.drop_table("rule_definition")
    if _table_exists("integration_hook"):
        op.drop_index("ix_integration_hook_project_id", table_name="integration_hook")
        op.drop_table("integration_hook")
    if _table_exists("sla"):
        op.drop_index("ix_sla_project_id", table_name="sla")
        op.drop_table("sla")
    if _table_exists("working_day"):
        op.drop_index("ix_working_day_date", table_name="working_day")
        op.drop_index("ix_working_day_project_id", table_name="working_day")
        op.drop_table("working_day")
    if _table_exists("project_risk"):
        op.drop_table("project_risk")
