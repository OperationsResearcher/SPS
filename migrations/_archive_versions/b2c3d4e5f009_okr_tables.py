"""okr_tables — OkrObjective + OkrKeyResult tabloları

Revision ID: b2c3d4e5f009
Revises: a1b2c3d4e008
Create Date: 2026-05-23

OKR modeli (app/models/okr.py) için migration:
  - okr_objectives: tenant + plan_year bazlı hedefler
  - okr_key_results: objective başına ölçülebilir sonuçlar
"""

from alembic import op
import sqlalchemy as sa

revision = "b2c3d4e5f009"
down_revision = "a1b2c3d4e008"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "okr_objectives",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("plan_year_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("quarter", sa.Integer(), nullable=True),
        sa.Column("owner", sa.String(200), nullable=True),
        sa.Column("order_no", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_year_id"], ["plan_years.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_okr_objectives_tenant_id", "okr_objectives", ["tenant_id"])
    op.create_index("ix_okr_objectives_plan_year_id", "okr_objectives", ["plan_year_id"])

    op.create_table(
        "okr_key_results",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("objective_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("metric", sa.String(100), nullable=True),
        sa.Column("start_value", sa.Float(), nullable=True),
        sa.Column("target_value", sa.Float(), nullable=True),
        sa.Column("current_value", sa.Float(), nullable=True),
        sa.Column("order_no", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["objective_id"], ["okr_objectives.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_okr_key_results_objective_id", "okr_key_results", ["objective_id"])


def downgrade():
    op.drop_index("ix_okr_key_results_objective_id", table_name="okr_key_results")
    op.drop_table("okr_key_results")
    op.drop_index("ix_okr_objectives_plan_year_id", table_name="okr_objectives")
    op.drop_index("ix_okr_objectives_tenant_id", table_name="okr_objectives")
    op.drop_table("okr_objectives")
