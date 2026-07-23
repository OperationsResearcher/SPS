"""risk_heatmap_items.project_id — KPR risk scope (G1)

Revision ID: hd01a2b3c4d5
Revises: 391945351814
Create Date: 2026-07-23

RiskHeatmapItem project kapsamı taşımıyordu; proje yetkili kullanıcı kurum
geneli risk görüyordu. Nullable project_id + source_type=project backfill.
"""
from alembic import op
import sqlalchemy as sa


revision = "hd01a2b3c4d5"
down_revision = "391945351814"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("risk_heatmap_items") as batch:
        batch.add_column(
            sa.Column("project_id", sa.Integer(), nullable=True)
        )
        batch.create_index(
            batch.f("ix_risk_heatmap_items_project_id"),
            ["project_id"],
            unique=False,
        )
        batch.create_foreign_key(
            batch.f("fk_risk_heatmap_items_project_id_project"),
            "project",
            ["project_id"],
            ["id"],
            ondelete="SET NULL",
        )

    # Kaynağı proje olan kayıtları doldur (source_id = project PK varsayımı).
    op.execute(
        """
        UPDATE risk_heatmap_items
        SET project_id = source_id
        WHERE source_type = 'project'
          AND source_id IS NOT NULL
          AND project_id IS NULL
          AND EXISTS (SELECT 1 FROM project p WHERE p.id = risk_heatmap_items.source_id)
        """
    )


def downgrade():
    with op.batch_alter_table("risk_heatmap_items") as batch:
        batch.drop_constraint(
            batch.f("fk_risk_heatmap_items_project_id_project"),
            type_="foreignkey",
        )
        batch.drop_index(batch.f("ix_risk_heatmap_items_project_id"))
        batch.drop_column("project_id")
