"""llm_usage_logs + llm_quota_overrides — LLM rate limit & maliyet izleme

Revision ID: f9g0h1i2j013
Revises: e8f9g0h1i012
Create Date: 2026-05-24
"""

from alembic import op
import sqlalchemy as sa


revision = "f9g0h1i2j013"
down_revision = "e8f9g0h1i012"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "llm_usage_logs",
        sa.Column("id", sa.BigInteger(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(),
                  sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("endpoint", sa.String(80), nullable=False),
        sa.Column("provider", sa.String(40), nullable=False, server_default="gemini"),
        sa.Column("model", sa.String(80), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cost_usd", sa.Numeric(10, 6), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="ok"),
        sa.Column("error_msg", sa.String(500), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index("idx_llm_log_tenant", "llm_usage_logs", ["tenant_id"])
    op.create_index("idx_llm_log_endpoint", "llm_usage_logs", ["endpoint"])
    op.create_index("idx_llm_log_created", "llm_usage_logs", ["created_at"])
    op.create_index("idx_llm_log_tenant_created", "llm_usage_logs", ["tenant_id", "created_at"])

    op.create_table(
        "llm_quota_overrides",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(),
                  sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column("daily_call_limit", sa.Integer(), nullable=True),
        sa.Column("monthly_call_limit", sa.Integer(), nullable=True),
        sa.Column("monthly_cost_limit_usd", sa.Numeric(10, 2), nullable=True),
        sa.Column("is_paused", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )


def downgrade():
    op.drop_table("llm_quota_overrides")
    op.drop_index("idx_llm_log_tenant_created", table_name="llm_usage_logs")
    op.drop_index("idx_llm_log_created", table_name="llm_usage_logs")
    op.drop_index("idx_llm_log_endpoint", table_name="llm_usage_logs")
    op.drop_index("idx_llm_log_tenant", table_name="llm_usage_logs")
    op.drop_table("llm_usage_logs")
