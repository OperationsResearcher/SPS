"""users tenant_id + role_id index (perf)

users.tenant_id multi-tenant filtrenin ana kolonu ama indekssizdi; her istekte
seq scan'e düşüyordu. role_id de sidebar/yetki join'lerinde sık kullanılıyor.

PostgreSQL'de CONCURRENTLY ile oluşturulur — Yayın'da users tablosu yazmaya
kapanmasın diye. CONCURRENTLY transaction içinde çalışamaz, bu yüzden
autocommit bloğuna alınır. Diğer dialect'lerde (SQLite/test) normal CREATE.

Revision ID: da9b27f1a650
Revises: f6a7b8c9d0e1
Create Date: 2026-07-15 09:13:43.823573

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = 'da9b27f1a650'
down_revision = 'f6a7b8c9d0e1'
branch_labels = None
depends_on = None

_INDEXES = (
    ("ix_users_tenant_id", "tenant_id"),
    ("ix_users_role_id", "role_id"),
)


def _is_postgres() -> bool:
    return op.get_bind().dialect.name == "postgresql"


def upgrade():
    if _is_postgres():
        # CONCURRENTLY: kilitsiz oluşturma; IF NOT EXISTS: elle eklenmiş olabilir
        with op.get_context().autocommit_block():
            for name, col in _INDEXES:
                op.execute(f"CREATE INDEX CONCURRENTLY IF NOT EXISTS {name} ON users ({col})")
    else:
        for name, col in _INDEXES:
            op.create_index(name, "users", [col], unique=False)


def downgrade():
    if _is_postgres():
        with op.get_context().autocommit_block():
            for name, _col in _INDEXES:
                op.execute(f"DROP INDEX CONCURRENTLY IF EXISTS {name}")
    else:
        for name, _col in _INDEXES:
            op.drop_index(name, table_name="users")
