"""L1 Dal 4: bireysel hedef katmanı (Standart / Stratejik)

Toplamsal migration — individual_performance_indicators tablosuna 2 kolon ekler:
  - katman      : 'Standart' (rutin/operasyonel) / 'Stratejik' (stratejiye bağlı)
  - strategy_id : opsiyonel kurum stratejisi bağı (SET NULL)

Veri taşıma heuristiği (idempotent — yalnızca yeni kolon doldurulur):
  source_process_kpi_id IS NOT NULL  →  'Stratejik'   (süreç PG'sinden atanmış)
  diğerleri                          →  'Standart'    (kolon default'u zaten)

Mevcut veri/kolonlara dokunmaz. downgrade() 2 kolonu drop eder → geri-dönüşlü.

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-06-19
"""
from alembic import op
import sqlalchemy as sa


revision = "b2c3d4e5f6a7"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None

_TABLE = "individual_performance_indicators"


def upgrade() -> None:
    with op.batch_alter_table(_TABLE, schema=None) as batch_op:
        # server_default ile mevcut satırlar otomatik 'Standart' alır
        batch_op.add_column(
            sa.Column("katman", sa.String(length=20), nullable=False,
                      server_default="Standart")
        )
        batch_op.add_column(
            sa.Column("strategy_id", sa.Integer(), nullable=True)
        )
        batch_op.create_index(batch_op.f(f"ix_{_TABLE}_katman"), ["katman"], unique=False)
        batch_op.create_index(batch_op.f(f"ix_{_TABLE}_strategy_id"), ["strategy_id"], unique=False)
        batch_op.create_foreign_key(
            batch_op.f(f"fk_{_TABLE}_strategy_id_strategies"),
            "strategies", ["strategy_id"], ["id"], ondelete="SET NULL",
        )

    # Heuristik: süreç PG'sinden atanmış hedefler 'Stratejik'
    op.execute(sa.text(
        f"UPDATE {_TABLE} SET katman = 'Stratejik' "
        f"WHERE source_process_kpi_id IS NOT NULL"
    ))


def downgrade() -> None:
    with op.batch_alter_table(_TABLE, schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f(f"fk_{_TABLE}_strategy_id_strategies"), type_="foreignkey")
        batch_op.drop_index(batch_op.f(f"ix_{_TABLE}_strategy_id"))
        batch_op.drop_index(batch_op.f(f"ix_{_TABLE}_katman"))
        batch_op.drop_column("strategy_id")
        batch_op.drop_column("katman")
