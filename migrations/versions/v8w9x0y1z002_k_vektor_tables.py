"""K-Vektör: tenant bayrak, ağırlık tabloları, denetim snapshot.

Revision ID: v8w9x0y1z002
Revises: u4v5w6x7y001
"""

from alembic import op
import sqlalchemy as sa


revision = "v8w9x0y1z002"
down_revision = "u4v5w6x7y001"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("tenants", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("k_vektor_enabled", sa.Boolean(), nullable=False, server_default=sa.text("false"))
        )

    op.create_table(
        "k_vektor_strategy_weights",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("strategy_id", sa.Integer(), nullable=False),
        sa.Column("weight_raw", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["strategy_id"], ["strategies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "strategy_id", name="uq_kv_strat_w_tenant_strategy"),
    )
    op.create_index("ix_kv_strat_w_tenant", "k_vektor_strategy_weights", ["tenant_id"], unique=False)

    op.create_table(
        "k_vektor_sub_strategy_weights",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("sub_strategy_id", sa.Integer(), nullable=False),
        sa.Column("weight_raw", sa.Float(), nullable=True),
        sa.ForeignKeyConstraint(["sub_strategy_id"], ["sub_strategies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "sub_strategy_id", name="uq_kv_sub_w_tenant_sub"),
    )
    op.create_index("ix_kv_sub_w_tenant", "k_vektor_sub_strategy_weights", ["tenant_id"], unique=False)

    op.create_table(
        "k_vektor_config_snapshots",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("snapshot_type", sa.String(length=64), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_kv_snap_tenant", "k_vektor_config_snapshots", ["tenant_id"], unique=False)
    op.create_index("ix_kv_snap_created", "k_vektor_config_snapshots", ["created_at"], unique=False)


def downgrade():
    op.drop_index("ix_kv_snap_created", table_name="k_vektor_config_snapshots")
    op.drop_index("ix_kv_snap_tenant", table_name="k_vektor_config_snapshots")
    op.drop_table("k_vektor_config_snapshots")

    op.drop_index("ix_kv_sub_w_tenant", table_name="k_vektor_sub_strategy_weights")
    op.drop_table("k_vektor_sub_strategy_weights")

    op.drop_index("ix_kv_strat_w_tenant", table_name="k_vektor_strategy_weights")
    op.drop_table("k_vektor_strategy_weights")

    with op.batch_alter_table("tenants", schema=None) as batch_op:
        batch_op.drop_column("k_vektor_enabled")
