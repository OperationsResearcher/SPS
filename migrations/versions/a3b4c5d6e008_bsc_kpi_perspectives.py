"""bsc_kpi_perspectives — Balanced Scorecard 4 perspektif × KPI tablosu

Revision ID: a3b4c5d6e008
Revises: z3a4b5c6d007
Create Date: 2026-05-29

Yeni tablolar:
  bsc_kpi_perspectives — ProcessKpi'yı 4 BSC perspektifinden birine atar
"""

from alembic import op
import sqlalchemy as sa

revision = "a3b4c5d6e008"
down_revision = "j3k4l5m6n017"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "bsc_kpi_perspectives",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("plan_year_id", sa.Integer(),
                  sa.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=False),
        sa.Column("process_kpi_id", sa.Integer(),
                  sa.ForeignKey("process_kpis.id", ondelete="CASCADE"), nullable=False),
        sa.Column("perspective", sa.String(length=30), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("plan_year_id", "process_kpi_id",
                            name="uq_bsc_kpi_perspective"),
    )
    op.create_index("ix_bsc_kpi_perspectives_tenant_id",
                    "bsc_kpi_perspectives", ["tenant_id"])
    op.create_index("ix_bsc_kpi_perspectives_plan_year_id",
                    "bsc_kpi_perspectives", ["plan_year_id"])
    op.create_index("ix_bsc_kpi_perspectives_process_kpi_id",
                    "bsc_kpi_perspectives", ["process_kpi_id"])
    op.create_index("idx_bsc_kpi_persp_lookup",
                    "bsc_kpi_perspectives",
                    ["tenant_id", "plan_year_id", "perspective"])


def downgrade():
    op.drop_index("idx_bsc_kpi_persp_lookup", table_name="bsc_kpi_perspectives")
    op.drop_index("ix_bsc_kpi_perspectives_process_kpi_id", table_name="bsc_kpi_perspectives")
    op.drop_index("ix_bsc_kpi_perspectives_plan_year_id", table_name="bsc_kpi_perspectives")
    op.drop_index("ix_bsc_kpi_perspectives_tenant_id", table_name="bsc_kpi_perspectives")
    op.drop_table("bsc_kpi_perspectives")
