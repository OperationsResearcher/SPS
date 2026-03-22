"""task.process_kpi_id — proje görevi ↔ ProcessKpi

Revision ID: a1c2d3e4f5a6
Revises: 9504e9a7e70f
"""
from alembic import op
import sqlalchemy as sa


revision = "a1c2d3e4f5a6"
down_revision = "9504e9a7e70f"
branch_labels = None
depends_on = None


def _column_exists(bind, table: str, col: str) -> bool:
    insp = sa.inspect(bind)
    if not insp.has_table(table):
        return False
    return any(c["name"] == col for c in insp.get_columns(table))


def upgrade():
    bind = op.get_bind()
    if _column_exists(bind, "task", "process_kpi_id"):
        return

    insp = sa.inspect(bind)
    has_pk_table = insp.has_table("process_kpis")

    if has_pk_table:
        with op.batch_alter_table("task", schema=None) as batch_op:
            batch_op.add_column(sa.Column("process_kpi_id", sa.Integer(), nullable=True))
            batch_op.create_index(batch_op.f("ix_task_process_kpi_id"), ["process_kpi_id"], unique=False)
            batch_op.create_foreign_key(
                "fk_task_process_kpi_id_process_kpis",
                "process_kpis",
                ["process_kpi_id"],
                ["id"],
                ondelete="SET NULL",
            )
    else:
        op.add_column("task", sa.Column("process_kpi_id", sa.Integer(), nullable=True))
        op.create_index("ix_task_process_kpi_id", "task", ["process_kpi_id"], unique=False)


def downgrade():
    bind = op.get_bind()
    if not _column_exists(bind, "task", "process_kpi_id"):
        return
    insp = sa.inspect(bind)
    has_pk = insp.has_table("process_kpis")
    with op.batch_alter_table("task", schema=None) as batch_op:
        if has_pk:
            try:
                batch_op.drop_constraint("fk_task_process_kpi_id_process_kpis", type_="foreignkey")
            except Exception:
                pass
        try:
            batch_op.drop_index(batch_op.f("ix_task_process_kpi_id"))
        except Exception:
            try:
                op.drop_index("ix_task_process_kpi_id", table_name="task")
            except Exception:
                pass
        batch_op.drop_column("process_kpi_id")
