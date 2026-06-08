# -*- coding: utf-8 -*-
"""Legacy analysis_item ve swot_analyses tablolarini kaldir (SWOT/PESTLE modulleri)

Revision ID: p0q1r2s3sw01
Revises: k9l8m766p001
Create Date: 2026-03-26

"""
from alembic import op
import sqlalchemy as sa


revision = "p0q1r2s3sw01"
down_revision = "k9l8m766p001"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    if insp.has_table("swot_analyses"):
        op.drop_table("swot_analyses")
    if insp.has_table("analysis_item"):
        op.drop_table("analysis_item")


def downgrade():
    # Gelistirme icin bos sema; indeks adlari ortamlara gore degisebilir.
    op.create_table(
        "analysis_item",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("analysis_type", sa.String(length=20), nullable=False),
        sa.Column("category", sa.String(length=50), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "swot_analyses",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(length=32), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
