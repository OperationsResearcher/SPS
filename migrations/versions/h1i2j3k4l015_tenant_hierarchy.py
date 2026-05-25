"""tenant_hierarchy — Bayi/Holding hiyerarşisi (Sprint A)

Revision ID: h1i2j3k4l015
Revises: g0h1i2j3k014
Create Date: 2026-05-25

Tenant tablosuna 3 alan:
- tenant_type: 'normal' / 'dealer' (bayi) / 'holding' (grup şirketi)
- parent_tenant_id: alt tenant ise parent FK (SET NULL on delete)
- sub_tenant_limit: bayi/holding kaç alt tenant açabilir
"""

from alembic import op
import sqlalchemy as sa


revision = "h1i2j3k4l015"
down_revision = "g0h1i2j3k014"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("tenants",
                  sa.Column("tenant_type", sa.String(20), nullable=False, server_default="normal"))
    op.add_column("tenants",
                  sa.Column("parent_tenant_id", sa.Integer(),
                            sa.ForeignKey("tenants.id", ondelete="SET NULL"),
                            nullable=True))
    op.add_column("tenants",
                  sa.Column("sub_tenant_limit", sa.Integer(), nullable=True))
    op.create_index("idx_tenant_parent", "tenants", ["parent_tenant_id"])
    op.create_index("idx_tenant_type", "tenants", ["tenant_type"])


def downgrade():
    op.drop_index("idx_tenant_type", table_name="tenants")
    op.drop_index("idx_tenant_parent", table_name="tenants")
    op.drop_column("tenants", "sub_tenant_limit")
    op.drop_column("tenants", "parent_tenant_id")
    op.drop_column("tenants", "tenant_type")
