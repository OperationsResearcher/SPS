"""initiatives_tables — Multi-Year Initiative (Sprint 55 — Ö4)

Revision ID: a4b5c6d7e008
Revises: z3a4b5c6d007
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa


revision = "a4b5c6d7e008"
down_revision = "f6g7h8i9j013"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "initiatives",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("code", sa.String(40), nullable=True),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("strategy_id", sa.Integer(),
                  sa.ForeignKey("strategies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("sub_strategy_id", sa.Integer(),
                  sa.ForeignKey("sub_strategies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("start_year", sa.Integer(), nullable=False),
        sa.Column("end_year", sa.Integer(), nullable=False),
        sa.Column("start_date", sa.Date(), nullable=True),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="planned"),
        sa.Column("priority", sa.String(20), nullable=False, server_default="medium"),
        sa.Column("budget_total", sa.Numeric(18, 2), nullable=True),
        sa.Column("budget_spent", sa.Numeric(18, 2), nullable=True, server_default="0"),
        sa.Column("progress_pct", sa.Float(), nullable=False, server_default="0"),
        sa.Column("owner_user_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_initiative_tenant", "initiatives", ["tenant_id"])
    op.create_index("idx_initiative_strategy", "initiatives", ["strategy_id"])
    op.create_index("idx_initiative_status", "initiatives", ["status"])

    op.create_table(
        "initiative_milestones",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("initiative_id", sa.Integer(),
                  sa.ForeignKey("initiatives.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(300), nullable=False),
        sa.Column("target_date", sa.Date(), nullable=True),
        sa.Column("completed_date", sa.Date(), nullable=True),
        sa.Column("status", sa.String(30), nullable=False, server_default="pending"),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_initiative_ms_initiative", "initiative_milestones", ["initiative_id"])


def downgrade():
    op.drop_index("idx_initiative_ms_initiative", table_name="initiative_milestones")
    op.drop_table("initiative_milestones")
    op.drop_index("idx_initiative_status", table_name="initiatives")
    op.drop_index("idx_initiative_strategy", table_name="initiatives")
    op.drop_index("idx_initiative_tenant", table_name="initiatives")
    op.drop_table("initiatives")
