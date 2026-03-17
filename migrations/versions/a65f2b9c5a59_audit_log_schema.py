"""audit log schema (audit_log only)

Revision ID: a65f2b9c5a59
Revises: 2047a12f5ca2
Create Date: 2026-01-20 07:03:58.576671

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a65f2b9c5a59'
down_revision = '2047a12f5ca2'
branch_labels = None
depends_on = None


def _column_exists(conn, table_name, column_name):
    result = conn.execute(sa.text(f"PRAGMA table_info({table_name})"))
    cols = {row[1] for row in result.fetchall()}
    return column_name in cols


def upgrade():
    conn = op.get_bind()

    with op.batch_alter_table('audit_log', schema=None) as batch_op:
        if not _column_exists(conn, 'audit_log', 'target_model'):
            batch_op.add_column(sa.Column('target_model', sa.String(length=100), nullable=True))
        if not _column_exists(conn, 'audit_log', 'target_id'):
            batch_op.add_column(sa.Column('target_id', sa.Integer(), nullable=True))
        if not _column_exists(conn, 'audit_log', 'changes'):
            batch_op.add_column(sa.Column('changes', sa.JSON(), nullable=True))
        if not _column_exists(conn, 'audit_log', 'timestamp'):
            batch_op.add_column(sa.Column('timestamp', sa.DateTime(), nullable=True))
        if not _column_exists(conn, 'audit_log', 'ip_address'):
            batch_op.add_column(sa.Column('ip_address', sa.String(length=50), nullable=True))
        if not _column_exists(conn, 'audit_log', 'action'):
            batch_op.add_column(sa.Column('action', sa.String(length=20), nullable=True))

    try:
        op.create_index('ix_audit_log_target_model', 'audit_log', ['target_model'], unique=False)
    except Exception:
        pass
    try:
        op.create_index('ix_audit_log_target_id', 'audit_log', ['target_id'], unique=False)
    except Exception:
        pass
    try:
        op.create_index('ix_audit_log_timestamp', 'audit_log', ['timestamp'], unique=False)
    except Exception:
        pass


def downgrade():
    pass
