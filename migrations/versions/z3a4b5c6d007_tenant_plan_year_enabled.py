"""tenant_plan_year_enabled — Kurum bazlı yıllık dönem özelliği toggle

Revision ID: z3a4b5c6d007
Revises: y2z3a4b5c006
Create Date: 2026-04-05

tenants tablosuna plan_year_enabled (Boolean, default False) kolonu eklenir.
Kapalı olduğunda SP yıllık dönem çubuğu gizlenir ve skor motoru yıl konfigürasyon
tablolarına bakmaz; tüm KPI hesapları ProcessKpi orijinal değerlerine düşer.
"""

from alembic import op
import sqlalchemy as sa

revision = "z3a4b5c6d007"
down_revision = "y2z3a4b5c006"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tenants",
        sa.Column(
            "plan_year_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade():
    op.drop_column("tenants", "plan_year_enabled")
