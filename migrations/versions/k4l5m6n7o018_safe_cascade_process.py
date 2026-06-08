"""H-42: safe cascade — tenant backref ve plan_year FK'larını güvenli hale getir

Revision ID: k4l5m6n7o018
Revises: j3k4l5m6n017
Create Date: 2026-06-01

Sorun:
  - processes.tenant_id → DB-level cascade yoktu ama SQLAlchemy ORM
    cascade="all, delete-orphan" tenant silinince tüm süreçleri de
    uçuruyordu. Soft-delete yeterliyken hard-delete tetikleniyordu.
  - processes.plan_year_id, process_kpis.plan_year_id,
    process_activities.plan_year_id, individual_performance_indicators.plan_year_id
    ondelete="CASCADE" ile tanımlıydı → plan yılı silinince bağlı tüm
    kayıtlar da siliniyor, veri kaybı oluşuyordu.

Çözüm:
  - processes.tenant_id: DB-level ON DELETE kısıtı RESTRICT (örtülü) kalır,
    ORM cascade "save-update, merge" yapılır (model.py'de zaten güncellendi).
  - plan_year_id FK'lar: ON DELETE CASCADE → ON DELETE SET NULL
    nullable=True zaten vardı, bu yüzden ek sütun değişikliği gerekmez.

SQLite batch mode: SQLite ALTER TABLE CONSTRAINT değiştirmeyi desteklemez,
bu nedenle her tablo için batch_alter_table kullanılır.
"""
from alembic import op
import sqlalchemy as sa


revision = "k4l5m6n7o018"
down_revision = "j3k4l5m6n017"
branch_labels = None
depends_on = None


def upgrade():
    # SQLite FK constraint değişikliği için batch mode gerekir.
    # Her tablo için: mevcut FK DROP + yeni FK ADD (SET NULL ile).

    with op.batch_alter_table('processes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_processes_plan_year_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_processes_plan_year_id',
            'plan_years', ['plan_year_id'], ['id'],
            ondelete='SET NULL'
        )

    with op.batch_alter_table('process_kpis', schema=None) as batch_op:
        batch_op.drop_constraint('fk_process_kpis_plan_year_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_process_kpis_plan_year_id',
            'plan_years', ['plan_year_id'], ['id'],
            ondelete='SET NULL'
        )

    with op.batch_alter_table('process_activities', schema=None) as batch_op:
        batch_op.drop_constraint('fk_process_activities_plan_year_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_process_activities_plan_year_id',
            'plan_years', ['plan_year_id'], ['id'],
            ondelete='SET NULL'
        )

    with op.batch_alter_table('individual_performance_indicators', schema=None) as batch_op:
        batch_op.drop_constraint('fk_individual_performance_indicators_plan_year_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_individual_performance_indicators_plan_year_id',
            'plan_years', ['plan_year_id'], ['id'],
            ondelete='SET NULL'
        )


def downgrade():
    # CASCADE davranışını geri yükle (tehlikeli — sadece geliştirme ortamında)

    with op.batch_alter_table('individual_performance_indicators', schema=None) as batch_op:
        batch_op.drop_constraint('fk_individual_performance_indicators_plan_year_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_individual_performance_indicators_plan_year_id',
            'plan_years', ['plan_year_id'], ['id'],
            ondelete='CASCADE'
        )

    with op.batch_alter_table('process_activities', schema=None) as batch_op:
        batch_op.drop_constraint('fk_process_activities_plan_year_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_process_activities_plan_year_id',
            'plan_years', ['plan_year_id'], ['id'],
            ondelete='CASCADE'
        )

    with op.batch_alter_table('process_kpis', schema=None) as batch_op:
        batch_op.drop_constraint('fk_process_kpis_plan_year_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_process_kpis_plan_year_id',
            'plan_years', ['plan_year_id'], ['id'],
            ondelete='CASCADE'
        )

    with op.batch_alter_table('processes', schema=None) as batch_op:
        batch_op.drop_constraint('fk_processes_plan_year_id', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_processes_plan_year_id',
            'plan_years', ['plan_year_id'], ['id'],
            ondelete='CASCADE'
        )
