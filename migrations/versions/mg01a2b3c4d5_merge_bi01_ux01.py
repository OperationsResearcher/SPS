"""merge: bi01c4e5f6a7 + ux01a2b3c4d5 tek head'e birleştirilir

İki paralel dal aynı atadan (hd01a2b3c4d5) ayrılmıştı:
  hd01 -> bi01 (bireysel PG yıl hizalama)
  hd01 -> gs01 (users.session_version) -> ux01 (bireysel PG aktif benzersiz indeks)
`alembic upgrade head` "Multiple head revisions" ile duruyordu (Yayın deploy'unu engellerdi).
Bu birleştirme ŞEMAYI DEĞİŞTİRMEZ (boş upgrade/downgrade); yalnız grafiği tek head yapar.

Revision ID: mg01a2b3c4d5
Revises: bi01c4e5f6a7, ux01a2b3c4d5
Create Date: 2026-10-24
"""

revision = "mg01a2b3c4d5"
down_revision = ("bi01c4e5f6a7", "ux01a2b3c4d5")
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
