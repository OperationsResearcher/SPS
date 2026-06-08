"""okr_strategy_link — OkrObjective'a linked_strategy_id ve linked_sub_strategy_id

Revision ID: c3d4e5f6g010
Revises: b2c3d4e5f009
Create Date: 2026-05-23

Sprint 17: OKR'ı stratejik plana bağlama altyapısı.
- okr_objectives.linked_strategy_id (Strategy FK, nullable)
- okr_objectives.linked_sub_strategy_id (SubStrategy FK, nullable)

İki tane çünkü bir OKR ana stratejiye veya alt stratejiye bağlanabilir.
"""

from alembic import op
import sqlalchemy as sa

revision = "c3d4e5f6g010"
down_revision = "b2c3d4e5f009"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("okr_objectives") as batch_op:
        batch_op.add_column(
            sa.Column("linked_strategy_id", sa.Integer(),
                      sa.ForeignKey("strategies.id", ondelete="SET NULL"),
                      nullable=True)
        )
        batch_op.add_column(
            sa.Column("linked_sub_strategy_id", sa.Integer(),
                      sa.ForeignKey("sub_strategies.id", ondelete="SET NULL"),
                      nullable=True)
        )
        batch_op.create_index("ix_okr_objectives_linked_strategy", ["linked_strategy_id"])
        batch_op.create_index("ix_okr_objectives_linked_sub_strategy", ["linked_sub_strategy_id"])


def downgrade():
    with op.batch_alter_table("okr_objectives") as batch_op:
        batch_op.drop_index("ix_okr_objectives_linked_sub_strategy")
        batch_op.drop_index("ix_okr_objectives_linked_strategy")
        batch_op.drop_column("linked_sub_strategy_id")
        batch_op.drop_column("linked_strategy_id")
