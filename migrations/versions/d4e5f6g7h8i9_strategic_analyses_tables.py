"""Stratejik analiz tabloları: PESTEL, Porter, plan_year_id ekleme.

Revision ID: d4e5f6g7h8i9
Revises: c2d3e4f5g6h7
Create Date: 2026-04-08
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

revision = "d4e5f6g7h8i9"
down_revision = "c2d3e4f5g6h7"
branch_labels = None
depends_on = None


def _col_exists(insp: Inspector, table: str, col: str) -> bool:
    return col in {c["name"] for c in insp.get_columns(table)}


def _table_exists(insp: Inspector, table: str) -> bool:
    return table in insp.get_table_names()


def upgrade():
    insp = Inspector.from_engine(op.get_bind())

    # ── 1. pestel_analyses ─────────────────────────────────────────────────────
    if not _table_exists(insp, "pestel_analyses"):
        op.create_table(
            "pestel_analyses",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("plan_year_id", sa.Integer,
                      sa.ForeignKey("plan_years.id", ondelete="CASCADE"),
                      nullable=False),
            sa.Column("tenant_id", sa.Integer,
                      sa.ForeignKey("tenants.id", ondelete="CASCADE"),
                      nullable=False),
            sa.Column("source_pestel_id", sa.Integer,
                      sa.ForeignKey("pestel_analyses.id", ondelete="SET NULL"),
                      nullable=True),
            sa.Column("political",     sa.Text, nullable=True),
            sa.Column("economic",      sa.Text, nullable=True),
            sa.Column("social",        sa.Text, nullable=True),
            sa.Column("technological", sa.Text, nullable=True),
            sa.Column("environmental", sa.Text, nullable=True),
            sa.Column("legal",         sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime, nullable=True),
            sa.Column("updated_at", sa.DateTime, nullable=True),
            sa.UniqueConstraint("plan_year_id", "tenant_id",
                                name="uq_pestel_plan_year_tenant"),
        )
        op.create_index("ix_pestel_plan_year_id", "pestel_analyses", ["plan_year_id"])
        op.create_index("ix_pestel_tenant_id",    "pestel_analyses", ["tenant_id"])

    # ── 2. porter_analyses ─────────────────────────────────────────────────────
    if not _table_exists(insp, "porter_analyses"):
        op.create_table(
            "porter_analyses",
            sa.Column("id", sa.Integer, primary_key=True),
            sa.Column("plan_year_id", sa.Integer,
                      sa.ForeignKey("plan_years.id", ondelete="CASCADE"),
                      nullable=False),
            sa.Column("tenant_id", sa.Integer,
                      sa.ForeignKey("tenants.id", ondelete="CASCADE"),
                      nullable=False),
            sa.Column("source_porter_id", sa.Integer,
                      sa.ForeignKey("porter_analyses.id", ondelete="SET NULL"),
                      nullable=True),
            sa.Column("rivalry_intensity",  sa.Text, nullable=True),
            sa.Column("supplier_power",     sa.Text, nullable=True),
            sa.Column("buyer_power",        sa.Text, nullable=True),
            sa.Column("new_entrant_threat", sa.Text, nullable=True),
            sa.Column("substitute_threat",  sa.Text, nullable=True),
            sa.Column("created_at", sa.DateTime, nullable=True),
            sa.Column("updated_at", sa.DateTime, nullable=True),
            sa.UniqueConstraint("plan_year_id", "tenant_id",
                                name="uq_porter_plan_year_tenant"),
        )
        op.create_index("ix_porter_plan_year_id", "porter_analyses", ["plan_year_id"])
        op.create_index("ix_porter_tenant_id",    "porter_analyses", ["tenant_id"])

    # ── 3. competitor_analyses → plan_year_id ──────────────────────────────────
    if _table_exists(insp, "competitor_analyses"):
        if not _col_exists(insp, "competitor_analyses", "plan_year_id"):
            op.add_column("competitor_analyses",
                          sa.Column("plan_year_id", sa.Integer, nullable=True))
            op.create_index("ix_competitor_plan_year_id",
                            "competitor_analyses", ["plan_year_id"])
            op.create_foreign_key(
                "fk_competitor_plan_year_id",
                "competitor_analyses", "plan_years",
                ["plan_year_id"], ["id"], ondelete="SET NULL",
            )

    # ── 4. stakeholder_maps → plan_year_id ────────────────────────────────────
    if _table_exists(insp, "stakeholder_maps"):
        if not _col_exists(insp, "stakeholder_maps", "plan_year_id"):
            op.add_column("stakeholder_maps",
                          sa.Column("plan_year_id", sa.Integer, nullable=True))
            op.create_index("ix_stakeholder_plan_year_id",
                            "stakeholder_maps", ["plan_year_id"])
            op.create_foreign_key(
                "fk_stakeholder_plan_year_id",
                "stakeholder_maps", "plan_years",
                ["plan_year_id"], ["id"], ondelete="SET NULL",
            )

    # ── 5. risk_heatmap_items → plan_year_id ──────────────────────────────────
    if _table_exists(insp, "risk_heatmap_items"):
        if not _col_exists(insp, "risk_heatmap_items", "plan_year_id"):
            op.add_column("risk_heatmap_items",
                          sa.Column("plan_year_id", sa.Integer, nullable=True))
            op.create_index("ix_risk_heatmap_plan_year_id",
                            "risk_heatmap_items", ["plan_year_id"])
            op.create_foreign_key(
                "fk_risk_heatmap_plan_year_id",
                "risk_heatmap_items", "plan_years",
                ["plan_year_id"], ["id"], ondelete="SET NULL",
            )


def downgrade():
    insp = Inspector.from_engine(op.get_bind())

    # risk_heatmap_items
    if _table_exists(insp, "risk_heatmap_items") and _col_exists(insp, "risk_heatmap_items", "plan_year_id"):
        op.drop_constraint("fk_risk_heatmap_plan_year_id", "risk_heatmap_items", type_="foreignkey")
        op.drop_index("ix_risk_heatmap_plan_year_id", table_name="risk_heatmap_items")
        op.drop_column("risk_heatmap_items", "plan_year_id")

    # stakeholder_maps
    if _table_exists(insp, "stakeholder_maps") and _col_exists(insp, "stakeholder_maps", "plan_year_id"):
        op.drop_constraint("fk_stakeholder_plan_year_id", "stakeholder_maps", type_="foreignkey")
        op.drop_index("ix_stakeholder_plan_year_id", table_name="stakeholder_maps")
        op.drop_column("stakeholder_maps", "plan_year_id")

    # competitor_analyses
    if _table_exists(insp, "competitor_analyses") and _col_exists(insp, "competitor_analyses", "plan_year_id"):
        op.drop_constraint("fk_competitor_plan_year_id", "competitor_analyses", type_="foreignkey")
        op.drop_index("ix_competitor_plan_year_id", table_name="competitor_analyses")
        op.drop_column("competitor_analyses", "plan_year_id")

    # porter_analyses
    if _table_exists(insp, "porter_analyses"):
        op.drop_index("ix_porter_tenant_id",    table_name="porter_analyses")
        op.drop_index("ix_porter_plan_year_id", table_name="porter_analyses")
        op.drop_table("porter_analyses")

    # pestel_analyses
    if _table_exists(insp, "pestel_analyses"):
        op.drop_index("ix_pestel_tenant_id",    table_name="pestel_analyses")
        op.drop_index("ix_pestel_plan_year_id", table_name="pestel_analyses")
        op.drop_table("pestel_analyses")
