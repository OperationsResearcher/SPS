"""system_cards.description varchar(512) -> Text (zengin kart aciklamalari)

Revision ID: 391945351814
Revises: yb20c5e1a8d3
Create Date: 2026-07-20 11:29:11.621030

NOT (2026-07-21): down_revision b7d3e1f4a920 -> yb20c5e1a8d3 guncellendi.
Dal main'den 4 migration geride kalmisti; oldugu gibi merge edilseydi
2 head olusur, deploy patlardi (REHBER §6.1 tek-head disiplini).

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '391945351814'
down_revision = 'yb20c5e1a8d3'
branch_labels = None
depends_on = None


def upgrade():
    # Zenginlestirilmis kart aciklamalari (hesap yontemi + yorum + sinir +
    # literatur dayanagi) 512 karaktere sigmiyor. PostgreSQL'de Text ile
    # varchar arasinda performans farki yoktur; genisletme veri kaybettirmez.
    op.alter_column(
        "system_cards",
        "description",
        existing_type=sa.String(length=512),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade():
    # DIKKAT: 512 karakteri asan aciklamalar bu islemde KESILIR.
    # Geri alinmadan once uzun metinlerin yedeklenmesi gerekir.
    op.alter_column(
        "system_cards",
        "description",
        existing_type=sa.Text(),
        type_=sa.String(length=512),
        existing_nullable=True,
    )
