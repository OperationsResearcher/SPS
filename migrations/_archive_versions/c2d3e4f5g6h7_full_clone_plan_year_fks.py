"""full_clone_plan_year_fks — SP Tam Klon mimarisi için FK kolonları ve yeni tablolar

Revision ID: c2d3e4f5g6h7
Revises: b1c2d3e4f5a6, b9c0d1e2f3a8
Create Date: 2026-04-08

Değişiklikler:
1. strategies         → plan_year_id (FK, nullable), source_strategy_id (self-ref FK, nullable)
2. sub_strategies     → plan_year_id (FK, nullable), source_sub_strategy_id (self-ref FK, nullable)
3. processes          → plan_year_id (FK, nullable), source_process_id (self-ref FK, nullable)
4. process_kpis       → plan_year_id (FK, nullable), source_kpi_id (self-ref FK, nullable)
5. process_activities → plan_year_id (FK, nullable), source_activity_id (self-ref FK, nullable)
6. individual_performance_indicators → plan_year_id (FK, nullable), source_individual_kpi_id (self-ref FK, nullable)
7. CREATE TABLE tenant_year_identities
8. CREATE TABLE swot_analyses
9. CREATE TABLE tows_analyses
10. CREATE TABLE projects
11. CREATE TABLE project_tasks
12. CREATE TABLE project_activities

Tüm plan_year_id ve source_* kolonları nullable=True → mevcut veriler kırılmaz.
Sonraki adım: scripts/migrate_genesis_plan_year.py ile mevcut verileri genesis PlanYear'a ata.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

revision = "c2d3e4f5g6h7"
down_revision = ("b1c2d3e4f5a6", "b9c0d1e2f3a8")
branch_labels = None
depends_on = None


def _col_exists(insp, table, col):
    return col in {c["name"] for c in insp.get_columns(table)}


def _table_exists(insp, table):
    return table in insp.get_table_names()


def upgrade():
    bind = op.get_bind()
    insp = Inspector.from_engine(bind)

    # ── 1. strategies ──────────────────────────────────────────────────────────
    if not _col_exists(insp, "strategies", "plan_year_id"):
        op.add_column("strategies", sa.Column("plan_year_id", sa.Integer(), nullable=True))
        op.create_index("ix_strategies_plan_year_id", "strategies", ["plan_year_id"])
        op.create_foreign_key(
            "fk_strategies_plan_year_id", "strategies", "plan_years",
            ["plan_year_id"], ["id"], ondelete="CASCADE"
        )
    if not _col_exists(insp, "strategies", "source_strategy_id"):
        op.add_column("strategies", sa.Column("source_strategy_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_strategies_source_strategy_id", "strategies", "strategies",
            ["source_strategy_id"], ["id"], ondelete="SET NULL"
        )

    # ── 2. sub_strategies ──────────────────────────────────────────────────────
    if not _col_exists(insp, "sub_strategies", "plan_year_id"):
        op.add_column("sub_strategies", sa.Column("plan_year_id", sa.Integer(), nullable=True))
        op.create_index("ix_sub_strategies_plan_year_id", "sub_strategies", ["plan_year_id"])
        op.create_foreign_key(
            "fk_sub_strategies_plan_year_id", "sub_strategies", "plan_years",
            ["plan_year_id"], ["id"], ondelete="CASCADE"
        )
    if not _col_exists(insp, "sub_strategies", "source_sub_strategy_id"):
        op.add_column("sub_strategies", sa.Column("source_sub_strategy_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_sub_strategies_source_sub_strategy_id", "sub_strategies", "sub_strategies",
            ["source_sub_strategy_id"], ["id"], ondelete="SET NULL"
        )

    # ── 3. processes ───────────────────────────────────────────────────────────
    if not _col_exists(insp, "processes", "plan_year_id"):
        op.add_column("processes", sa.Column("plan_year_id", sa.Integer(), nullable=True))
        op.create_index("ix_processes_plan_year_id", "processes", ["plan_year_id"])
        op.create_foreign_key(
            "fk_processes_plan_year_id", "processes", "plan_years",
            ["plan_year_id"], ["id"], ondelete="CASCADE"
        )
    if not _col_exists(insp, "processes", "source_process_id"):
        op.add_column("processes", sa.Column("source_process_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_processes_source_process_id", "processes", "processes",
            ["source_process_id"], ["id"], ondelete="SET NULL"
        )

    # ── 4. process_kpis ────────────────────────────────────────────────────────
    if not _col_exists(insp, "process_kpis", "plan_year_id"):
        op.add_column("process_kpis", sa.Column("plan_year_id", sa.Integer(), nullable=True))
        op.create_index("ix_process_kpis_plan_year_id", "process_kpis", ["plan_year_id"])
        op.create_foreign_key(
            "fk_process_kpis_plan_year_id", "process_kpis", "plan_years",
            ["plan_year_id"], ["id"], ondelete="CASCADE"
        )
    if not _col_exists(insp, "process_kpis", "source_kpi_id"):
        op.add_column("process_kpis", sa.Column("source_kpi_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_process_kpis_source_kpi_id", "process_kpis", "process_kpis",
            ["source_kpi_id"], ["id"], ondelete="SET NULL"
        )

    # ── 5. process_activities ──────────────────────────────────────────────────
    if not _col_exists(insp, "process_activities", "plan_year_id"):
        op.add_column("process_activities", sa.Column("plan_year_id", sa.Integer(), nullable=True))
        op.create_index("ix_process_activities_plan_year_id", "process_activities", ["plan_year_id"])
        op.create_foreign_key(
            "fk_process_activities_plan_year_id", "process_activities", "plan_years",
            ["plan_year_id"], ["id"], ondelete="CASCADE"
        )
    if not _col_exists(insp, "process_activities", "source_activity_id"):
        op.add_column("process_activities", sa.Column("source_activity_id", sa.Integer(), nullable=True))
        op.create_foreign_key(
            "fk_process_activities_source_activity_id", "process_activities", "process_activities",
            ["source_activity_id"], ["id"], ondelete="SET NULL"
        )

    # ── 6. individual_performance_indicators ───────────────────────────────────
    if not _col_exists(insp, "individual_performance_indicators", "plan_year_id"):
        op.add_column(
            "individual_performance_indicators",
            sa.Column("plan_year_id", sa.Integer(), nullable=True)
        )
        op.create_index(
            "ix_indiv_pg_plan_year_id", "individual_performance_indicators", ["plan_year_id"]
        )
        op.create_foreign_key(
            "fk_indiv_pg_plan_year_id", "individual_performance_indicators", "plan_years",
            ["plan_year_id"], ["id"], ondelete="CASCADE"
        )
    if not _col_exists(insp, "individual_performance_indicators", "source_individual_kpi_id"):
        op.add_column(
            "individual_performance_indicators",
            sa.Column("source_individual_kpi_id", sa.Integer(), nullable=True)
        )
        op.create_foreign_key(
            "fk_indiv_pg_source_individual_kpi_id",
            "individual_performance_indicators", "individual_performance_indicators",
            ["source_individual_kpi_id"], ["id"], ondelete="SET NULL"
        )

    # ── 7. tenant_year_identities ──────────────────────────────────────────────
    if not _table_exists(insp, "tenant_year_identities"):
        op.create_table(
            "tenant_year_identities",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("plan_year_id", sa.Integer(), sa.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=False, unique=True),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("purpose", sa.Text(), nullable=True),
            sa.Column("vision", sa.Text(), nullable=True),
            sa.Column("core_values", sa.Text(), nullable=True),
            sa.Column("code_of_ethics", sa.Text(), nullable=True),
            sa.Column("quality_policy", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_tenant_year_id_plan_year", "tenant_year_identities", ["plan_year_id"])
        op.create_index("ix_tenant_year_id_tenant", "tenant_year_identities", ["tenant_id"])

    # ── 8. swot_analyses ───────────────────────────────────────────────────────
    if not _table_exists(insp, "swot_analyses"):
        op.create_table(
            "swot_analyses",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("plan_year_id", sa.Integer(), sa.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=False),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("source_swot_id", sa.Integer(), sa.ForeignKey("swot_analyses.id", ondelete="SET NULL"), nullable=True),
            sa.Column("strengths", sa.Text(), nullable=True),
            sa.Column("weaknesses", sa.Text(), nullable=True),
            sa.Column("opportunities", sa.Text(), nullable=True),
            sa.Column("threats", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.UniqueConstraint("plan_year_id", "tenant_id", name="uq_swot_plan_year_tenant"),
        )
        op.create_index("ix_swot_plan_year_id", "swot_analyses", ["plan_year_id"])

    # ── 9. tows_analyses ───────────────────────────────────────────────────────
    if not _table_exists(insp, "tows_analyses"):
        op.create_table(
            "tows_analyses",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("plan_year_id", sa.Integer(), sa.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=False),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("source_tows_id", sa.Integer(), sa.ForeignKey("tows_analyses.id", ondelete="SET NULL"), nullable=True),
            sa.Column("so_strategies", sa.Text(), nullable=True),
            sa.Column("st_strategies", sa.Text(), nullable=True),
            sa.Column("wo_strategies", sa.Text(), nullable=True),
            sa.Column("wt_strategies", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.UniqueConstraint("plan_year_id", "tenant_id", name="uq_tows_plan_year_tenant"),
        )
        op.create_index("ix_tows_plan_year_id", "tows_analyses", ["plan_year_id"])

    # ── 10. plan_projects ──────────────────────────────────────────────────────
    if not _table_exists(insp, "plan_projects"):
        op.create_table(
            "plan_projects",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("plan_year_id", sa.Integer(), sa.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=False),
            sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
            sa.Column("source_project_id", sa.Integer(), sa.ForeignKey("plan_projects.id", ondelete="SET NULL"), nullable=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(50), nullable=False, server_default="Planlandı"),
            sa.Column("progress", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("start_date", sa.Date(), nullable=True),
            sa.Column("end_date", sa.Date(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_plan_projects_plan_year_id", "plan_projects", ["plan_year_id"])
        op.create_index("ix_plan_projects_tenant_id", "plan_projects", ["tenant_id"])

    # ── 11. plan_project_tasks ────────────────────────────────────────────────
    if not _table_exists(insp, "plan_project_tasks"):
        op.create_table(
            "plan_project_tasks",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), sa.ForeignKey("plan_projects.id", ondelete="CASCADE"), nullable=False),
            sa.Column("plan_year_id", sa.Integer(), sa.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=False),
            sa.Column("assignee_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(50), nullable=False, server_default="Planlandı"),
            sa.Column("start_date", sa.Date(), nullable=True),
            sa.Column("end_date", sa.Date(), nullable=True),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_plan_project_tasks_project_id", "plan_project_tasks", ["project_id"])

    # ── 12. plan_project_activities ───────────────────────────────────────────
    if not _table_exists(insp, "plan_project_activities"):
        op.create_table(
            "plan_project_activities",
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("project_id", sa.Integer(), sa.ForeignKey("plan_projects.id", ondelete="CASCADE"), nullable=False),
            sa.Column("plan_year_id", sa.Integer(), sa.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(200), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("status", sa.String(50), nullable=False, server_default="Planlandı"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
        )
        op.create_index("ix_plan_project_activities_project_id", "plan_project_activities", ["project_id"])


def downgrade():
    bind = op.get_bind()
    insp = Inspector.from_engine(bind)

    # Yeni tablolar
    for tbl in ["plan_project_activities", "plan_project_tasks", "plan_projects",
                "tows_analyses", "swot_analyses", "tenant_year_identities"]:
        if _table_exists(insp, tbl):
            op.drop_table(tbl)

    # individual_performance_indicators
    if _col_exists(insp, "individual_performance_indicators", "source_individual_kpi_id"):
        op.drop_constraint("fk_indiv_pg_source_individual_kpi_id", "individual_performance_indicators", type_="foreignkey")
        op.drop_column("individual_performance_indicators", "source_individual_kpi_id")
    if _col_exists(insp, "individual_performance_indicators", "plan_year_id"):
        op.drop_constraint("fk_indiv_pg_plan_year_id", "individual_performance_indicators", type_="foreignkey")
        op.drop_index("ix_indiv_pg_plan_year_id", table_name="individual_performance_indicators")
        op.drop_column("individual_performance_indicators", "plan_year_id")

    # process_activities
    if _col_exists(insp, "process_activities", "source_activity_id"):
        op.drop_constraint("fk_process_activities_source_activity_id", "process_activities", type_="foreignkey")
        op.drop_column("process_activities", "source_activity_id")
    if _col_exists(insp, "process_activities", "plan_year_id"):
        op.drop_constraint("fk_process_activities_plan_year_id", "process_activities", type_="foreignkey")
        op.drop_index("ix_process_activities_plan_year_id", table_name="process_activities")
        op.drop_column("process_activities", "plan_year_id")

    # process_kpis
    if _col_exists(insp, "process_kpis", "source_kpi_id"):
        op.drop_constraint("fk_process_kpis_source_kpi_id", "process_kpis", type_="foreignkey")
        op.drop_column("process_kpis", "source_kpi_id")
    if _col_exists(insp, "process_kpis", "plan_year_id"):
        op.drop_constraint("fk_process_kpis_plan_year_id", "process_kpis", type_="foreignkey")
        op.drop_index("ix_process_kpis_plan_year_id", table_name="process_kpis")
        op.drop_column("process_kpis", "plan_year_id")

    # processes
    if _col_exists(insp, "processes", "source_process_id"):
        op.drop_constraint("fk_processes_source_process_id", "processes", type_="foreignkey")
        op.drop_column("processes", "source_process_id")
    if _col_exists(insp, "processes", "plan_year_id"):
        op.drop_constraint("fk_processes_plan_year_id", "processes", type_="foreignkey")
        op.drop_index("ix_processes_plan_year_id", table_name="processes")
        op.drop_column("processes", "plan_year_id")

    # sub_strategies
    if _col_exists(insp, "sub_strategies", "source_sub_strategy_id"):
        op.drop_constraint("fk_sub_strategies_source_sub_strategy_id", "sub_strategies", type_="foreignkey")
        op.drop_column("sub_strategies", "source_sub_strategy_id")
    if _col_exists(insp, "sub_strategies", "plan_year_id"):
        op.drop_constraint("fk_sub_strategies_plan_year_id", "sub_strategies", type_="foreignkey")
        op.drop_index("ix_sub_strategies_plan_year_id", table_name="sub_strategies")
        op.drop_column("sub_strategies", "plan_year_id")

    # strategies
    if _col_exists(insp, "strategies", "source_strategy_id"):
        op.drop_constraint("fk_strategies_source_strategy_id", "strategies", type_="foreignkey")
        op.drop_column("strategies", "source_strategy_id")
    if _col_exists(insp, "strategies", "plan_year_id"):
        op.drop_constraint("fk_strategies_plan_year_id", "strategies", type_="foreignkey")
        op.drop_index("ix_strategies_plan_year_id", table_name="strategies")
        op.drop_column("strategies", "plan_year_id")
