"""rename_notification_turkish_fields_to_english

Revision ID: 0de355ae95f4
Revises: a7f8c9d0e1f2
Create Date: 2026-03-03 01:44:02.129715

Kural 3: Notification modelindeki Türkçe alan adları İngilizce'ye çevrildi.
  tip         → notification_type
  baslik      → title
  mesaj       → message
  okundu      → is_read
  ilgili_user_id → related_user_id

Ayrıca FavoriteKpi.is_active eklendi (Kural 4: soft-delete desteği).
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0de355ae95f4'
down_revision = 'a7f8c9d0e1f2'
branch_labels = None
depends_on = None


def upgrade():
    # Notifications: Türkçe alan adları → İngilizce (Kural 3)
    # SQLite'de batch_alter_table tabloyu yeniden oluşturur (rename column desteklenmediği için add+drop yapılır)
    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.add_column(sa.Column('notification_type', sa.String(length=50), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('title', sa.String(length=200), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('message', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('is_read', sa.Boolean(), nullable=False, server_default='0'))
        batch_op.add_column(sa.Column('related_user_id', sa.Integer(), nullable=True))
        batch_op.drop_column('okundu')
        batch_op.drop_column('mesaj')
        batch_op.drop_column('ilgili_user_id')
        batch_op.drop_column('tip')
        batch_op.drop_column('baslik')

    # FavoriteKpi: is_active eklendi (zaten var ise kontrol et; yoksa ekle)
    # Not: Eğer kolon zaten varsa bu adım atlanır
    try:
        with op.batch_alter_table('favorite_kpis', schema=None) as batch_op:
            batch_op.add_column(sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))
    except Exception:
        pass  # Kolon zaten mevcut


def downgrade():
    with op.batch_alter_table('notifications', schema=None) as batch_op:
        batch_op.add_column(sa.Column('baslik', sa.VARCHAR(length=200), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('tip', sa.VARCHAR(length=50), nullable=False, server_default=''))
        batch_op.add_column(sa.Column('ilgili_user_id', sa.INTEGER(), nullable=True))
        batch_op.add_column(sa.Column('mesaj', sa.TEXT(), nullable=True))
        batch_op.add_column(sa.Column('okundu', sa.BOOLEAN(), nullable=False, server_default='0'))
        batch_op.drop_column('related_user_id')
        batch_op.drop_column('is_read')
        batch_op.drop_column('message')
        batch_op.drop_column('title')
        batch_op.drop_column('notification_type')

    with op.batch_alter_table('favorite_kpis', schema=None) as batch_op:
        batch_op.drop_column('is_active')
