"""audit log rewrite

Revision ID: b1a2c3d4e5f6
Revises: a65f2b9c5a59
Create Date: 2026-01-20

"""
from alembic import op
import sqlalchemy as sa


revision = 'b1a2c3d4e5f6'
down_revision = 'a65f2b9c5a59'
branch_labels = None
depends_on = None


def _column_exists(conn, table_name, column_name):
    result = conn.execute(sa.text(f"PRAGMA table_info({table_name})"))
    cols = {row[1] for row in result.fetchall()}
    return column_name in cols


def upgrade():
    conn = op.get_bind()

    with op.batch_alter_table('audit_log', schema=None) as batch_op:
        if not _column_exists(conn, 'audit_log', 'user_name'):
            batch_op.add_column(sa.Column('user_name', sa.String(length=150), nullable=True))
        if not _column_exists(conn, 'audit_log', 'module'):
            batch_op.add_column(sa.Column('module', sa.String(length=100), nullable=True))
        if not _column_exists(conn, 'audit_log', 'record_id'):
            batch_op.add_column(sa.Column('record_id', sa.Integer(), nullable=True))
        if not _column_exists(conn, 'audit_log', 'record_name'):
            batch_op.add_column(sa.Column('record_name', sa.String(length=255), nullable=True))

    # Backfill minimal values for existing rows (if any)
    try:
        op.execute("UPDATE audit_log SET user_name = 'Bilinmiyor' WHERE user_name IS NULL")
        # module: prefer target_model if exists, else fallback
        if _column_exists(conn, 'audit_log', 'target_model'):
            op.execute("UPDATE audit_log SET module = target_model WHERE module IS NULL")
        op.execute("UPDATE audit_log SET module = 'Bilinmiyor' WHERE module IS NULL")
        # record_id: prefer target_id if exists
        if _column_exists(conn, 'audit_log', 'target_id'):
            op.execute("UPDATE audit_log SET record_id = target_id WHERE record_id IS NULL")
        op.execute("UPDATE audit_log SET record_id = 0 WHERE record_id IS NULL")
        op.execute("UPDATE audit_log SET record_name = 'Kayıt' WHERE record_name IS NULL")
    except Exception:
        pass


def downgrade():
    # Geri dönüşte veri kaybı riskinden kaçınmak için boş bırakıldı
    pass
