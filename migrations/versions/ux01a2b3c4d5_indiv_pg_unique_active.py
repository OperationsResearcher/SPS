"""individual_performance_indicators: aktif (user, source_process_kpi) tekilliği (HATA-24)

Revision ID: ux01a2b3c4d5
Revises: gs01a2b3c4d5
Create Date: 2026-09-30

Uygulamadan önce mükerrer taraması yapıldı (Yerel/Yayın anlık görüntüsü: 0).
Yine de kural: mükerrer varsa en eski aktif kayıt kalır, diğerleri soft-delete edilir.
"""
from alembic import op

revision = "ux01a2b3c4d5"
down_revision = "gs01a2b3c4d5"
branch_labels = None
depends_on = None

_INDEX = "ux_indiv_pg_user_source_kpi_active"


def upgrade():
    op.execute(
        """
        UPDATE individual_performance_indicators
           SET is_active = FALSE
         WHERE is_active AND source_process_kpi_id IS NOT NULL
           AND id NOT IN (
                SELECT MIN(id) FROM individual_performance_indicators
                 WHERE is_active AND source_process_kpi_id IS NOT NULL
                 GROUP BY user_id, source_process_kpi_id)
        """
    )
    op.execute(
        f"CREATE UNIQUE INDEX IF NOT EXISTS {_INDEX} "
        "ON individual_performance_indicators (user_id, source_process_kpi_id) "
        "WHERE is_active AND source_process_kpi_id IS NOT NULL"
    )


def downgrade():
    op.execute(f"DROP INDEX IF EXISTS {_INDEX}")
