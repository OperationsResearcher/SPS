"""plan_year_tables — yıllık stratejik planlama dönem sistemi (Faz 1-6)

Revision ID: y2z3a4b5c006
Revises: w1x2y3z4b004
Create Date: 2026-04-05

Yeni tablolar:
  plan_years                  — dönem kaydı (tenant × yıl)
  kpi_year_configs            — KPI başına yıllık hedef/metod override
  strategy_year_configs       — Strateji başına yıllık override
  sub_strategy_year_configs   — Alt strateji başına yıllık override
  process_year_configs        — Süreç başına yıllık override
  individual_kpi_year_configs — Bireysel PG başına yıllık override
"""

from alembic import op
import sqlalchemy as sa

revision = "y2z3a4b5c006"
down_revision = "w1x2y3z4b004"
branch_labels = None
depends_on = None


def upgrade():
    # ── plan_years ─────────────────────────────────────────────────────────────
    op.create_table(
        "plan_years",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=True),
        sa.Column("status", sa.String(20), nullable=False, server_default="active"),
        sa.Column("template_source_id", sa.Integer(), sa.ForeignKey("plan_years.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("closed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("idx_plan_year_tenant", "plan_years", ["tenant_id"])
    op.create_index("idx_plan_year_year", "plan_years", ["year"])
    op.create_index("idx_plan_year_tenant_status", "plan_years", ["tenant_id", "status"])
    op.create_unique_constraint("uq_plan_year_tenant_year", "plan_years", ["tenant_id", "year"])

    # ── kpi_year_configs ───────────────────────────────────────────────────────
    op.create_table(
        "kpi_year_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_year_id", sa.Integer(), sa.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=False),
        sa.Column("process_kpi_id", sa.Integer(), sa.ForeignKey("process_kpis.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_value", sa.String(100), nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("period", sa.String(50), nullable=True),
        sa.Column("direction", sa.String(20), nullable=True),
        sa.Column("target_method", sa.String(10), nullable=True),
        sa.Column("calculation_method", sa.String(20), nullable=True),
        sa.Column("basari_puani_araliklari", sa.Text(), nullable=True),
        sa.Column("onceki_yil_ortalamasi", sa.Float(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("is_included", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
    )
    op.create_index("idx_kpi_year_config_plan", "kpi_year_configs", ["plan_year_id"])
    op.create_index("idx_kpi_year_config_kpi", "kpi_year_configs", ["process_kpi_id"])
    op.create_index("idx_kpi_year_config_lookup", "kpi_year_configs", ["plan_year_id", "process_kpi_id"])
    op.create_unique_constraint("uq_kpi_year_config", "kpi_year_configs", ["plan_year_id", "process_kpi_id"])

    # ── strategy_year_configs ──────────────────────────────────────────────────
    op.create_table(
        "strategy_year_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_year_id", sa.Integer(), sa.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=False),
        sa.Column("strategy_id", sa.Integer(), sa.ForeignKey("strategies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("code", sa.String(20), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_included", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
    )
    op.create_index("idx_strategy_year_config", "strategy_year_configs", ["plan_year_id", "strategy_id"])
    op.create_unique_constraint("uq_strategy_year_config", "strategy_year_configs", ["plan_year_id", "strategy_id"])

    # ── sub_strategy_year_configs ──────────────────────────────────────────────
    op.create_table(
        "sub_strategy_year_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_year_id", sa.Integer(), sa.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=False),
        sa.Column("sub_strategy_id", sa.Integer(), sa.ForeignKey("sub_strategies.id", ondelete="CASCADE"), nullable=False),
        sa.Column("title", sa.String(200), nullable=True),
        sa.Column("code", sa.String(20), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_included", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
    )
    op.create_index("idx_sub_strategy_year_config", "sub_strategy_year_configs", ["plan_year_id", "sub_strategy_id"])
    op.create_unique_constraint("uq_sub_strategy_year_config", "sub_strategy_year_configs", ["plan_year_id", "sub_strategy_id"])

    # ── process_year_configs ───────────────────────────────────────────────────
    op.create_table(
        "process_year_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_year_id", sa.Integer(), sa.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=False),
        sa.Column("process_id", sa.Integer(), sa.ForeignKey("processes.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("is_included", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
    )
    op.create_index("idx_process_year_config", "process_year_configs", ["plan_year_id", "process_id"])
    op.create_unique_constraint("uq_process_year_config", "process_year_configs", ["plan_year_id", "process_id"])

    # ── individual_kpi_year_configs ────────────────────────────────────────────
    op.create_table(
        "individual_kpi_year_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("plan_year_id", sa.Integer(), sa.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=False),
        sa.Column("individual_performance_id", sa.Integer(), sa.ForeignKey("individual_performance_indicators.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_value", sa.String(100), nullable=True),
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("period", sa.String(50), nullable=True),
        sa.Column("direction", sa.String(20), nullable=True),
        sa.Column("target_method", sa.String(10), nullable=True),
        sa.Column("calculation_method", sa.String(20), nullable=True),
        sa.Column("basari_puani_araliklari", sa.Text(), nullable=True),
        sa.Column("weight", sa.Float(), nullable=True),
        sa.Column("is_included", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=True, server_default=sa.func.now()),
    )
    op.create_index("idx_indiv_kpi_year_config", "individual_kpi_year_configs", ["plan_year_id", "individual_performance_id"])
    op.create_unique_constraint("uq_indiv_kpi_year_config", "individual_kpi_year_configs", ["plan_year_id", "individual_performance_id"])


def downgrade():
    op.drop_table("individual_kpi_year_configs")
    op.drop_table("process_year_configs")
    op.drop_table("sub_strategy_year_configs")
    op.drop_table("strategy_year_configs")
    op.drop_table("kpi_year_configs")
    op.drop_table("plan_years")
