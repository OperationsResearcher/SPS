"""okr_kpi_link — OkrKeyResult'a linked_process_kpi_id

Revision ID: e5f6g7h8i012
Revises: d4e5f6g7h011
Create Date: 2026-05-23

Sprint 33: KR (Key Result) bir ProcessKpi'ya bağlanabilir.
Bağlıysa: KR current_value otomatik olarak son KpiData ile sync edilebilir.
"""

from alembic import op
import sqlalchemy as sa

revision = "e5f6g7h8i012"
down_revision = "d4e5f6g7h011"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("okr_key_results") as batch_op:
        batch_op.add_column(
            sa.Column("linked_process_kpi_id", sa.Integer(),
                      sa.ForeignKey("process_kpis.id", ondelete="SET NULL"),
                      nullable=True)
        )
        batch_op.create_index(
            "ix_okr_kr_linked_process_kpi", ["linked_process_kpi_id"]
        )


def downgrade():
    with op.batch_alter_table("okr_key_results") as batch_op:
        batch_op.drop_index("ix_okr_kr_linked_process_kpi")
        batch_op.drop_column("linked_process_kpi_id")
