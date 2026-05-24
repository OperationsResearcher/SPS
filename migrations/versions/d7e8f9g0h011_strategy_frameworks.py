"""strategy_frameworks — Blue Ocean + VRIO (S60-S61)

Revision ID: d7e8f9g0h011
Revises: c6d7e8f9g010
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa


revision = "d7e8f9g0h011"
down_revision = "c6d7e8f9g010"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "blue_ocean_canvases",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("industry", sa.String(120), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("competitor_names", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_bo_canvas_tenant", "blue_ocean_canvases", ["tenant_id"])

    op.create_table(
        "blue_ocean_factors",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("canvas_id", sa.Integer(),
                  sa.ForeignKey("blue_ocean_canvases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(150), nullable=False),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("self_score", sa.Float(), nullable=False, server_default="5"),
        sa.Column("competitor_scores", sa.Text(), nullable=True),
    )
    op.create_index("idx_bo_factor_canvas", "blue_ocean_factors", ["canvas_id"])

    op.create_table(
        "blue_ocean_errc_items",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("canvas_id", sa.Integer(),
                  sa.ForeignKey("blue_ocean_canvases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("action", sa.String(20), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=True),
        sa.Column("impact", sa.String(20), nullable=True),
        sa.Column("order_index", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("idx_bo_errc_canvas", "blue_ocean_errc_items", ["canvas_id"])

    op.create_table(
        "vrio_resources",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("category", sa.String(80), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_valuable", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_rare", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_inimitable", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("is_organized", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_vrio_tenant", "vrio_resources", ["tenant_id"])


def downgrade():
    op.drop_index("idx_vrio_tenant", table_name="vrio_resources")
    op.drop_table("vrio_resources")
    op.drop_index("idx_bo_errc_canvas", table_name="blue_ocean_errc_items")
    op.drop_table("blue_ocean_errc_items")
    op.drop_index("idx_bo_factor_canvas", table_name="blue_ocean_factors")
    op.drop_table("blue_ocean_factors")
    op.drop_index("idx_bo_canvas_tenant", table_name="blue_ocean_canvases")
    op.drop_table("blue_ocean_canvases")
