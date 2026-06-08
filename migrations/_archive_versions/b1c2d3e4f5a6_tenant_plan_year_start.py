"""tenant_plan_year_start — Kurum geçmiş yıl başlangıç ayarı

Revision ID: b1c2d3e4f5a6
Revises: a0b1c2d3e4f5
Create Date: 2026-04-06

tenants tablosuna plan_year_start (Integer, nullable) kolonu eklenir.
Kurum yöneticisi "2021'den başla" seçince bu yıl kaydedilir ve
initialize_plan_years() fonksiyonu 2021-bugün arası tüm plan_year
kayıtlarını otomatik oluşturur.
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector

revision = "b1c2d3e4f5a6"
down_revision = "a0b1c2d3e4f5"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = Inspector.from_engine(bind)
    existing = {c["name"] for c in insp.get_columns("tenants")}
    if "plan_year_start" not in existing:
        op.add_column(
            "tenants",
            sa.Column("plan_year_start", sa.Integer(), nullable=True),
        )


def downgrade():
    op.drop_column("tenants", "plan_year_start")
