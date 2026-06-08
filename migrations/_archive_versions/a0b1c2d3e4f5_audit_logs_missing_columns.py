"""audit_logs eksik kolonlar: username, description, request_method, request_path

Revision ID: a0b1c2d3e4f5
Revises: z3a4b5c6d007
Create Date: 2026-04-05

audit_logs tablosu PostgreSQL'de oluşturulurken bu 4 kolon eksik kalmıştı.
AuditLogger.log() bu kolonları yazmaya çalıştığı için tüm audit yazımları
sessizce başarısız oluyordu (UndefinedColumn hatası yutuluyordu).
"""
from alembic import op
import sqlalchemy as sa

revision = 'a0b1c2d3e4f5'
down_revision = 'z3a4b5c6d007'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('audit_logs') as batch_op:
        # IF NOT EXISTS Alembic'te yok; try/except ile idempotent yapıyoruz
        pass

    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing = {c['name'] for c in inspector.get_columns('audit_logs')}

    if 'username' not in existing:
        op.add_column('audit_logs', sa.Column('username', sa.String(100), nullable=True))

    if 'description' not in existing:
        op.add_column('audit_logs', sa.Column('description', sa.Text(), nullable=True))

    if 'request_method' not in existing:
        op.add_column('audit_logs', sa.Column('request_method', sa.String(10), nullable=True))

    if 'request_path' not in existing:
        op.add_column('audit_logs', sa.Column('request_path', sa.String(500), nullable=True))


def downgrade():
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing = {c['name'] for c in inspector.get_columns('audit_logs')}

    if 'request_path' in existing:
        op.drop_column('audit_logs', 'request_path')
    if 'request_method' in existing:
        op.drop_column('audit_logs', 'request_method')
    if 'description' in existing:
        op.drop_column('audit_logs', 'description')
    if 'username' in existing:
        op.drop_column('audit_logs', 'username')
