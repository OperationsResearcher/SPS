"""Add K-Radar domain tables pack-1.

Revision ID: t2u3v4w5x001
Revises: s1t2u3v4w001
Create Date: 2026-03-26
"""

from alembic import op
import sqlalchemy as sa


revision = "t2u3v4w5x001"
down_revision = "s1t2u3v4w001"
branch_labels = None
depends_on = None


def _common_cols():
    return [
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    ]


def upgrade():
    op.create_table(
        "process_maturity",
        *_common_cols(),
        sa.Column("process_id", sa.Integer(), nullable=False),
        sa.Column("maturity_level", sa.Integer(), nullable=False),
        sa.Column("dimension", sa.String(length=100), nullable=True),
        sa.Column("assessed_by", sa.Integer(), nullable=True),
        sa.Column("assessed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["process_id"], ["processes.id"]),
        sa.ForeignKeyConstraint(["assessed_by"], ["users.id"]),
    )
    op.create_table(
        "bottleneck_log",
        *_common_cols(),
        sa.Column("process_id", sa.Integer(), nullable=False),
        sa.Column("kpi_id", sa.Integer(), nullable=True),
        sa.Column("severity", sa.String(length=20), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("triggered_at", sa.DateTime(), nullable=True),
        sa.Column("resolved_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["process_id"], ["processes.id"]),
        sa.ForeignKeyConstraint(["kpi_id"], ["process_kpis.id"]),
    )
    op.create_table(
        "value_chain_items",
        *_common_cols(),
        sa.Column("category", sa.String(length=20), nullable=False),
        sa.Column("linked_process_id", sa.Integer(), nullable=True),
        sa.Column("muda_type", sa.String(length=50), nullable=True),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("note", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["linked_process_id"], ["processes.id"]),
    )
    op.create_table(
        "evm_snapshots",
        *_common_cols(),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("snapshot_date", sa.Date(), nullable=False),
        sa.Column("pv", sa.Float(), nullable=True),
        sa.Column("ev", sa.Float(), nullable=True),
        sa.Column("ac", sa.Float(), nullable=True),
        sa.Column("spi", sa.Float(), nullable=True),
        sa.Column("cpi", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
    )
    op.create_table(
        "risk_heatmap_items",
        *_common_cols(),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("probability", sa.Integer(), nullable=False),
        sa.Column("impact", sa.Integer(), nullable=False),
        sa.Column("rpn", sa.Integer(), nullable=True),
        sa.Column("owner_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("source_type", sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"]),
    )
    op.create_table(
        "stakeholder_maps",
        *_common_cols(),
        sa.Column("name", sa.String(length=200), nullable=False),
        sa.Column("role", sa.String(length=100), nullable=True),
        sa.Column("influence", sa.Integer(), nullable=True),
        sa.Column("interest", sa.Integer(), nullable=True),
        sa.Column("strategy", sa.String(length=200), nullable=True),
    )
    op.create_table(
        "stakeholder_surveys",
        *_common_cols(),
        sa.Column("stakeholder_type", sa.String(length=100), nullable=False),
        sa.Column("period", sa.String(length=50), nullable=True),
        sa.Column("score", sa.Float(), nullable=True),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=True),
    )
    op.create_table(
        "a3_reports",
        *_common_cols(),
        sa.Column("source_type", sa.String(length=50), nullable=True),
        sa.Column("source_id", sa.Integer(), nullable=True),
        sa.Column("problem", sa.Text(), nullable=True),
        sa.Column("root_cause_json", sa.Text(), nullable=True),
        sa.Column("countermeasures", sa.Text(), nullable=True),
    )
    op.create_table(
        "competitor_analyses",
        *_common_cols(),
        sa.Column("competitor_name", sa.String(length=200), nullable=False),
        sa.Column("dimension", sa.String(length=100), nullable=True),
        sa.Column("our_score", sa.Float(), nullable=True),
        sa.Column("their_score", sa.Float(), nullable=True),
    )


def downgrade():
    op.drop_table("competitor_analyses")
    op.drop_table("a3_reports")
    op.drop_table("stakeholder_surveys")
    op.drop_table("stakeholder_maps")
    op.drop_table("risk_heatmap_items")
    op.drop_table("evm_snapshots")
    op.drop_table("value_chain_items")
    op.drop_table("bottleneck_log")
    op.drop_table("process_maturity")
