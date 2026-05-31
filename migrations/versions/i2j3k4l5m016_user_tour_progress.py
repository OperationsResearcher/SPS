"""user_tour_progress — Kule yardımcı sistemi tur durumları

Revision ID: i2j3k4l5m016
Revises: h1i2j3k4l015
Create Date: 2026-05-25

Her kullanıcı için her tur'un durumunu tutar:
- status: pending | completed | dismissed
- seen_count: kaç kez görüldü
- completed_at / dismissed_at: işaretleme zamanları
"""

from alembic import op
import sqlalchemy as sa


revision = "i2j3k4l5m016"
down_revision = "h1i2j3k4l015"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_tour_progress",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("tour_key", sa.String(64), nullable=False),
        sa.Column("status", sa.String(16), nullable=False, server_default="pending"),
        sa.Column("seen_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
        sa.Column("dismissed_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False,
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "tour_key", name="uq_user_tour"),
    )
    op.create_index("ix_user_tour_user", "user_tour_progress", ["user_id"])


def downgrade():
    op.drop_index("ix_user_tour_user", table_name="user_tour_progress")
    op.drop_table("user_tour_progress")
