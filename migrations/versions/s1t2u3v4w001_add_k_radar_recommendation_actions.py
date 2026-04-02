"""Add K-Radar recommendation actions table.

Revision ID: s1t2u3v4w001
Revises: r7s8t9u0v001
Create Date: 2026-03-26
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "s1t2u3v4w001"
down_revision = "r7s8t9u0v001"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "k_radar_recommendation_actions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("recommendation_key", sa.String(length=64), nullable=False),
        sa.Column("recommendation_text", sa.Text(), nullable=False),
        sa.Column("state", sa.String(length=20), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "tenant_id", "user_id", "recommendation_key", name="uq_k_radar_action_user_key"
        ),
    )
    op.create_index(
        "ix_k_radar_recommendation_actions_tenant_id",
        "k_radar_recommendation_actions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_k_radar_recommendation_actions_user_id",
        "k_radar_recommendation_actions",
        ["user_id"],
    )
    op.create_index(
        "ix_k_radar_recommendation_actions_recommendation_key",
        "k_radar_recommendation_actions",
        ["recommendation_key"],
    )


def downgrade():
    op.drop_index(
        "ix_k_radar_recommendation_actions_recommendation_key",
        table_name="k_radar_recommendation_actions",
    )
    op.drop_index("ix_k_radar_recommendation_actions_user_id", table_name="k_radar_recommendation_actions")
    op.drop_index(
        "ix_k_radar_recommendation_actions_tenant_id",
        table_name="k_radar_recommendation_actions",
    )
    op.drop_table("k_radar_recommendation_actions")
