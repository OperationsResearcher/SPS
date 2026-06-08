"""core_fk_ondelete — User/Strategy/SubStrategy FK ondelete düzeltmesi (H-44)

Revision ID: a1b2c3d4e008
Revises: z3a4b5c6d007
Create Date: 2026-06-01

users.tenant_id         → ON DELETE SET NULL   (tenant silinince kullanıcı orphan kalmaz)
strategies.tenant_id    → ON DELETE CASCADE    (tenant silinince stratejiler de silinir)
sub_strategies.strategy_id → ON DELETE CASCADE (strateji silinince alt stratejiler de silinir)
"""

from alembic import op
import sqlalchemy as sa

revision = "a1b2c3d4e008"
down_revision = "z3a4b5c6d007"
branch_labels = None
depends_on = None


def upgrade():
    # ── users.tenant_id ──────────────────────────────────────────────────────
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("users_tenant_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "users_tenant_id_fkey",
            "tenants",
            ["tenant_id"],
            ["id"],
            ondelete="SET NULL",
        )

    # ── strategies.tenant_id ─────────────────────────────────────────────────
    with op.batch_alter_table("strategies") as batch_op:
        batch_op.drop_constraint("strategies_tenant_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "strategies_tenant_id_fkey",
            "tenants",
            ["tenant_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # ── sub_strategies.strategy_id ───────────────────────────────────────────
    with op.batch_alter_table("sub_strategies") as batch_op:
        batch_op.drop_constraint("sub_strategies_strategy_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "sub_strategies_strategy_id_fkey",
            "strategies",
            ["strategy_id"],
            ["id"],
            ondelete="CASCADE",
        )


def downgrade():
    # ── sub_strategies.strategy_id ───────────────────────────────────────────
    with op.batch_alter_table("sub_strategies") as batch_op:
        batch_op.drop_constraint("sub_strategies_strategy_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "sub_strategies_strategy_id_fkey",
            "strategies",
            ["strategy_id"],
            ["id"],
        )

    # ── strategies.tenant_id ─────────────────────────────────────────────────
    with op.batch_alter_table("strategies") as batch_op:
        batch_op.drop_constraint("strategies_tenant_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "strategies_tenant_id_fkey",
            "tenants",
            ["tenant_id"],
            ["id"],
        )

    # ── users.tenant_id ──────────────────────────────────────────────────────
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("users_tenant_id_fkey", type_="foreignkey")
        batch_op.create_foreign_key(
            "users_tenant_id_fkey",
            "tenants",
            ["tenant_id"],
            ["id"],
        )
