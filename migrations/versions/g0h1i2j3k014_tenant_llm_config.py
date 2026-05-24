"""tenant_llm_configs — BYOK (Bring Your Own Key)

Revision ID: g0h1i2j3k014
Revises: f9g0h1i2j013
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa


revision = "g0h1i2j3k014"
down_revision = "f9g0h1i2j013"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "tenant_llm_configs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"),
                  nullable=False, unique=True),
        sa.Column("provider", sa.String(40), nullable=False, server_default="gemini"),
        sa.Column("model", sa.String(120), nullable=True),
        sa.Column("api_key_encrypted", sa.Text(), nullable=True),
        sa.Column("base_url", sa.String(300), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("pii_mask_enabled", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("last_test_at", sa.DateTime(), nullable=True),
        sa.Column("last_test_status", sa.String(40), nullable=True),
        sa.Column("last_test_message", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("tenant_llm_configs")
