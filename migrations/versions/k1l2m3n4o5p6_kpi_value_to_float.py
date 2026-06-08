"""H-43: kpi_data ve process_kpis — target_value/actual_value String→Float

Revision ID: k1l2m3n4o5p6
Revises: a3b4c5d6e008, i2j3k4l5m016
Create Date: 2026-06-01

Sorun: target_value ve actual_value kolonları VARCHAR(100) olarak tanımlıydı.
Skor motoru her hesaplamada string→float dönüşümü yapmak zorundaydı;
boş string ve boşluklu değerler NaN hatasına yol açabiliyordu.

Çözüm:
  - process_kpis.target_value      VARCHAR(100) → DOUBLE PRECISION (nullable)
  - kpi_data.target_value          VARCHAR(100) → DOUBLE PRECISION (nullable)
  - kpi_data.actual_value          VARCHAR(100) → DOUBLE PRECISION (nullable)

PostgreSQL USING ifadesi: NULLIF(TRIM(col),'')::FLOAT
  → boş string ve yalnızca boşluk içeren değerler NULL'a çevrilir
  → sayısal olmayan veri varsa migration hata verir (kasıtlı — temizlenmeli)

SQLite (yerel geliştirme): ALTER TYPE desteklenmediğinden
  yeni kolon ekle → veri kopyala → eski kolonu sil yolunu izle.
"""
from alembic import op
import sqlalchemy as sa


revision = "k1l2m3n4o5p6"
down_revision = ("a3b4c5d6e008", "i2j3k4l5m016")
branch_labels = None
depends_on = None


def _dialect(bind):
    return bind.dialect.name  # 'postgresql' veya 'sqlite'


# ─────────────────────────────────────────────────────────────
# UPGRADE
# ─────────────────────────────────────────────────────────────

def upgrade():
    bind = op.get_bind()
    dialect = _dialect(bind)

    if dialect == "postgresql":
        _upgrade_pg(bind)
    else:
        _upgrade_sqlite(bind)


def _upgrade_pg(bind):
    # process_kpis.target_value
    bind.execute(sa.text(
        "ALTER TABLE process_kpis "
        "ALTER COLUMN target_value TYPE DOUBLE PRECISION "
        "USING NULLIF(TRIM(target_value), '')::DOUBLE PRECISION"
    ))

    # kpi_data.target_value
    bind.execute(sa.text(
        "ALTER TABLE kpi_data "
        "ALTER COLUMN target_value TYPE DOUBLE PRECISION "
        "USING NULLIF(TRIM(target_value), '')::DOUBLE PRECISION"
    ))

    # kpi_data.actual_value — önce nullable yapıyoruz (was NOT NULL)
    bind.execute(sa.text(
        "ALTER TABLE kpi_data "
        "ALTER COLUMN actual_value TYPE DOUBLE PRECISION "
        "USING NULLIF(TRIM(actual_value), '')::DOUBLE PRECISION"
    ))
    # Kural: actual_value null olabilir (dönüşüm sonrası geriye dönük uyum)
    bind.execute(sa.text(
        "ALTER TABLE kpi_data ALTER COLUMN actual_value DROP NOT NULL"
    ))


def _upgrade_sqlite(bind):
    """SQLite için kolon adlandırma yoluyla tip değişikliği."""
    import re

    def _column_exists(table, col):
        result = bind.execute(sa.text(f"PRAGMA table_info({table})"))
        return any(row[1] == col for row in result)

    # --- process_kpis.target_value ---
    if _column_exists("process_kpis", "target_value"):
        op.add_column("process_kpis", sa.Column("target_value_f", sa.Float(), nullable=True))
        bind.execute(sa.text(
            "UPDATE process_kpis SET target_value_f = "
            "CAST(NULLIF(TRIM(target_value), '') AS REAL)"
        ))
        op.drop_column("process_kpis", "target_value")
        op.alter_column("process_kpis", "target_value_f", new_column_name="target_value")

    # --- kpi_data.target_value ---
    if _column_exists("kpi_data", "target_value"):
        op.add_column("kpi_data", sa.Column("target_value_f", sa.Float(), nullable=True))
        bind.execute(sa.text(
            "UPDATE kpi_data SET target_value_f = "
            "CAST(NULLIF(TRIM(target_value), '') AS REAL)"
        ))
        op.drop_column("kpi_data", "target_value")
        op.alter_column("kpi_data", "target_value_f", new_column_name="target_value")

    # --- kpi_data.actual_value ---
    if _column_exists("kpi_data", "actual_value"):
        op.add_column("kpi_data", sa.Column("actual_value_f", sa.Float(), nullable=True))
        bind.execute(sa.text(
            "UPDATE kpi_data SET actual_value_f = "
            "CAST(NULLIF(TRIM(actual_value), '') AS REAL)"
        ))
        op.drop_column("kpi_data", "actual_value")
        op.alter_column("kpi_data", "actual_value_f", new_column_name="actual_value")


# ─────────────────────────────────────────────────────────────
# DOWNGRADE
# ─────────────────────────────────────────────────────────────

def downgrade():
    bind = op.get_bind()
    dialect = _dialect(bind)

    if dialect == "postgresql":
        _downgrade_pg(bind)
    else:
        _downgrade_sqlite(bind)


def _downgrade_pg(bind):
    # actual_value: Float → VARCHAR(100), NOT NULL geri gelmiyor (veri kaybı riski)
    bind.execute(sa.text(
        "ALTER TABLE kpi_data "
        "ALTER COLUMN actual_value TYPE VARCHAR(100) "
        "USING actual_value::TEXT"
    ))
    bind.execute(sa.text(
        "ALTER TABLE kpi_data "
        "ALTER COLUMN target_value TYPE VARCHAR(100) "
        "USING target_value::TEXT"
    ))
    bind.execute(sa.text(
        "ALTER TABLE process_kpis "
        "ALTER COLUMN target_value TYPE VARCHAR(100) "
        "USING target_value::TEXT"
    ))


def _downgrade_sqlite(bind):
    def _column_exists(table, col):
        result = bind.execute(sa.text(f"PRAGMA table_info({table})"))
        return any(row[1] == col for row in result)

    # process_kpis.target_value
    if _column_exists("process_kpis", "target_value"):
        op.add_column("process_kpis", sa.Column("target_value_s", sa.String(100), nullable=True))
        bind.execute(sa.text(
            "UPDATE process_kpis SET target_value_s = CAST(target_value AS TEXT)"
        ))
        op.drop_column("process_kpis", "target_value")
        op.alter_column("process_kpis", "target_value_s", new_column_name="target_value")

    # kpi_data.target_value
    if _column_exists("kpi_data", "target_value"):
        op.add_column("kpi_data", sa.Column("target_value_s", sa.String(100), nullable=True))
        bind.execute(sa.text(
            "UPDATE kpi_data SET target_value_s = CAST(target_value AS TEXT)"
        ))
        op.drop_column("kpi_data", "target_value")
        op.alter_column("kpi_data", "target_value_s", new_column_name="target_value")

    # kpi_data.actual_value
    if _column_exists("kpi_data", "actual_value"):
        op.add_column("kpi_data", sa.Column("actual_value_s", sa.String(100), nullable=True))
        bind.execute(sa.text(
            "UPDATE kpi_data SET actual_value_s = CAST(actual_value AS TEXT)"
        ))
        op.drop_column("kpi_data", "actual_value")
        op.alter_column("kpi_data", "actual_value_s", new_column_name="actual_value")
