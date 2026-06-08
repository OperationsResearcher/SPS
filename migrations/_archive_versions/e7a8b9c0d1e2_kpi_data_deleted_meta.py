"""kpi_data soft delete meta: deleted_at, deleted_by_id

Revision ID: e7a8b9c0d1e2
Revises: 006_add_missing_tables
Create Date: 2026-03-21

VGS geçmişi: silen kullanıcı ve zaman damgası (satır üzerinde).
"""
from alembic import op
import sqlalchemy as sa


revision = "e7a8b9c0d1e2"
down_revision = "006_add_missing_tables"
branch_labels = None
depends_on = None


def _col_names(bind):
    insp = sa.inspect(bind)
    if not insp.has_table("kpi_data"):
        return None
    return {c["name"] for c in insp.get_columns("kpi_data")}


def upgrade():
    bind = op.get_bind()
    cols = _col_names(bind)
    if cols is None:
        return
    if "deleted_at" not in cols:
        op.add_column("kpi_data", sa.Column("deleted_at", sa.DateTime(), nullable=True))
    if "deleted_by_id" not in cols:
        op.add_column("kpi_data", sa.Column("deleted_by_id", sa.Integer(), nullable=True))
    insp = sa.inspect(bind)
    ix = {x["name"] for x in insp.get_indexes("kpi_data")}
    if "ix_kpi_data_deleted_at" not in ix:
        op.create_index("ix_kpi_data_deleted_at", "kpi_data", ["deleted_at"], unique=False)
    if "ix_kpi_data_deleted_by_id" not in ix:
        op.create_index("ix_kpi_data_deleted_by_id", "kpi_data", ["deleted_by_id"], unique=False)
    if insp.has_table("users"):
        try:
            op.create_foreign_key(
                "fk_kpi_data_deleted_by_id_users",
                "kpi_data",
                "users",
                ["deleted_by_id"],
                ["id"],
                ondelete="SET NULL",
            )
        except Exception:
            pass


def downgrade():
    bind = op.get_bind()
    cols = _col_names(bind)
    if cols is None:
        return
    try:
        op.drop_constraint("fk_kpi_data_deleted_by_id_users", "kpi_data", type_="foreignkey")
    except Exception:
        pass
    try:
        op.drop_index("ix_kpi_data_deleted_by_id", table_name="kpi_data")
    except Exception:
        pass
    try:
        op.drop_index("ix_kpi_data_deleted_at", table_name="kpi_data")
    except Exception:
        pass
    if "deleted_by_id" in cols:
        op.drop_column("kpi_data", "deleted_by_id")
    if "deleted_at" in cols:
        op.drop_column("kpi_data", "deleted_at")
