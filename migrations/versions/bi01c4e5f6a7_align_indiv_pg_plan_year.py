"""Süreçten aynalanan bireysel PG yılını kaynak süreç PG ile hizala.

Revision ID: bi01c4e5f6a7
Revises: hd01a2b3c4d5
Create Date: 2026-09-08

ensure-from-process-kpi aktif plan yılına (2026) damgalıyordu; süreç PG
yılsız/legacy iken 2021 verisi süreçte kalıyor, bireysel 409 veriyordu.
"""
from alembic import op


revision = "bi01c4e5f6a7"
down_revision = "hd01a2b3c4d5"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        UPDATE individual_performance_indicators AS i
        SET plan_year_id = pk.plan_year_id
        FROM process_kpis AS pk
        WHERE i.source_process_kpi_id = pk.id
          AND i.plan_year_id IS DISTINCT FROM pk.plan_year_id
        """
    )


def downgrade():
    # Yanlış damgayı geri kuracak kaynak yok
    pass
