"""kpi_data_audits old_target + new_target (TASK-261)

HEDEF DEĞİŞİKLİĞİ İZİ. `kpi_data_audits.old_value/new_value` yalnız
GERÇEKLEŞME'yi (actual_value) tutuyordu. Hedef (target_value) değişince
`action_detail`e sadece "hedef" etiketi düşüyor, NE'den NE'ye değiştiği
KAYBOLUYORDU — oysa `routes_kpi_data.py` old_target/new_target'ı zaten
hesaplıyordu, sadece audit'e yazmıyordu.

Neden önemli: "Hedef, dönem kapanışına yakın aşağı mı çekildi?" sorusu
Hedef Manipülasyonu Radarı'nın (TASK-262) tüm dayanağı. Bu iki kolon
olmadan o soru cevaplanamaz.

Geriye dönük veri YOK: eski 297 audit kaydında hedef izi hiç tutulmamış,
üretilemez (NULL kalır). Radar bu tarihten sonraki değişiklikleri görür.

Revision ID: c927a97a2fef
Revises: e9669efe440c
Create Date: 2026-07-15 16:43:43.367387

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'c927a97a2fef'
down_revision = 'e9669efe440c'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('kpi_data_audits', sa.Column('old_target', sa.Text(), nullable=True))
    op.add_column('kpi_data_audits', sa.Column('new_target', sa.Text(), nullable=True))

    # Radar sorgusu "hedefi değişen kayıtlar" ile başlar → kısmi index.
    # Kayıtların çoğunda hedef değişmez (NULL); tam index yerine partial
    # hem küçük hem hızlı. SQLite partial index'i desteklemez → yalnız PG.
    if op.get_bind().dialect.name == 'postgresql':
        op.execute(
            "CREATE INDEX ix_kpi_data_audits_hedef_degisim "
            "ON kpi_data_audits (kpi_data_id, created_at) "
            "WHERE new_target IS NOT NULL"
        )


def downgrade():
    if op.get_bind().dialect.name == 'postgresql':
        op.execute("DROP INDEX IF EXISTS ix_kpi_data_audits_hedef_degisim")
    op.drop_column('kpi_data_audits', 'new_target')
    op.drop_column('kpi_data_audits', 'old_target')
