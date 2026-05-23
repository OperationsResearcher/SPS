"""replan_triggers — Trigger-based replan engine (Sprint 57 — Ö8)

Revision ID: c6d7e8f9g010
Revises: b5c6d7e8f009
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa


revision = "c6d7e8f9g010"
down_revision = "b5c6d7e8f009"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "replan_triggers",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("trigger_type", sa.String(40), nullable=False),
        sa.Column("target_kpi_id", sa.Integer(),
                  sa.ForeignKey("process_kpis.id", ondelete="CASCADE"), nullable=True),
        sa.Column("threshold_value", sa.Float(), nullable=True),
        sa.Column("threshold_operator", sa.String(5), nullable=True),
        sa.Column("consecutive_periods", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("action", sa.String(40), nullable=False, server_default="notify"),
        sa.Column("severity", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_fired_at", sa.DateTime(), nullable=True),
        sa.Column("fire_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_replan_trigger_tenant", "replan_triggers", ["tenant_id"])
    op.create_index("idx_replan_trigger_active", "replan_triggers", ["tenant_id", "is_active"])

    op.create_table(
        "replan_trigger_events",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("trigger_id", sa.Integer(),
                  sa.ForeignKey("replan_triggers.id", ondelete="CASCADE"), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("fired_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("payload", sa.Text(), nullable=True),
        sa.Column("action_taken", sa.String(40), nullable=True),
        sa.Column("acknowledged_at", sa.DateTime(), nullable=True),
        sa.Column("acknowledged_by_user_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
    )
    op.create_index("idx_replan_event_trigger", "replan_trigger_events", ["trigger_id"])
    op.create_index("idx_replan_event_tenant", "replan_trigger_events", ["tenant_id"])


def downgrade():
    op.drop_index("idx_replan_event_tenant", table_name="replan_trigger_events")
    op.drop_index("idx_replan_event_trigger", table_name="replan_trigger_events")
    op.drop_table("replan_trigger_events")
    op.drop_index("idx_replan_trigger_active", table_name="replan_triggers")
    op.drop_index("idx_replan_trigger_tenant", table_name="replan_triggers")
    op.drop_table("replan_triggers")
