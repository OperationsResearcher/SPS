"""esg_models — ESG / Sürdürülebilirlik modülü tabloları

Revision ID: f6g7h8i9j013
Revises: e5f6g7h8i012
Create Date: 2026-05-23

Sprint 49: ESG modülü iskelet.
- esg_metrics: Scope 1/2/3 karbon, su, atık, çeşitlilik metrikleri
- esg_metric_values: Aylık/yıllık ölçümler
"""

from alembic import op
import sqlalchemy as sa

revision = "f6g7h8i9j013"
down_revision = "e5f6g7h8i012"
branch_labels = None
depends_on = None


def upgrade():
    # ESG Metric (tanım)
    op.create_table(
        "esg_metrics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(50), nullable=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(50), nullable=True),  # E/S/G
        sa.Column("scope", sa.String(20), nullable=True),  # scope1/scope2/scope3
        sa.Column("unit", sa.String(50), nullable=True),
        sa.Column("sdg_codes", sa.String(100), nullable=True),  # ör: "SDG7,SDG13"
        sa.Column("target_value", sa.Float(), nullable=True),
        sa.Column("baseline_year", sa.Integer(), nullable=True),
        sa.Column("baseline_value", sa.Float(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_esg_metrics_tenant", "esg_metrics", ["tenant_id"])
    op.create_index("ix_esg_metrics_category", "esg_metrics", ["category"])

    # ESG Metric Value (ölçüm)
    op.create_table(
        "esg_metric_values",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("metric_id", sa.Integer(), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("period_type", sa.String(20), nullable=True),  # Aylık/Yıllık
        sa.Column("period_no", sa.Integer(), nullable=True),
        sa.Column("value", sa.Float(), nullable=True),
        sa.Column("source", sa.String(100), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["metric_id"], ["esg_metrics.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_esg_metric_values_lookup", "esg_metric_values", ["metric_id", "year"])


def downgrade():
    op.drop_index("ix_esg_metric_values_lookup", table_name="esg_metric_values")
    op.drop_table("esg_metric_values")
    op.drop_index("ix_esg_metrics_category", table_name="esg_metrics")
    op.drop_index("ix_esg_metrics_tenant", table_name="esg_metrics")
    op.drop_table("esg_metrics")
