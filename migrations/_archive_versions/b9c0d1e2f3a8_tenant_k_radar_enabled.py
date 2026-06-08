"""tenant_k_radar_enabled — Kurum bazlı K-Radar modülü toggle

Revision ID: b9c0d1e2f3a8
Revises: a0b1c2d3e4f5
Create Date: 2026-04-06

tenants.k_radar_enabled: kapalıyken menü, launcher ve /k-radar uçları devre dışı.
"""

from alembic import op
import sqlalchemy as sa

revision = "b9c0d1e2f3a8"
down_revision = "a0b1c2d3e4f5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "tenants",
        sa.Column(
            "k_radar_enabled",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )


def downgrade():
    op.drop_column("tenants", "k_radar_enabled")
