"""system_settings tablosu; maintenance_mode bayragi.

Revision ID: w1x2y3z4b004
Revises: v8w9x0y1z002
"""

from alembic import op
import sqlalchemy as sa


revision = "w1x2y3z4b004"
down_revision = "v8w9x0y1z002"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "system_settings",
        sa.Column("key", sa.String(length=64), nullable=False),
        sa.Column("value", sa.Text(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("NOW()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("key"),
    )
    op.execute(
        sa.text(
            "INSERT INTO system_settings (key, value) VALUES ('maintenance_mode', 'false') "
            "ON CONFLICT (key) DO NOTHING"
        )
    )


def downgrade():
    op.drop_table("system_settings")
