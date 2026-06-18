"""L1: tenant kimlik çok-satırlı (values/ethics/quality)

Toplamsal migration — yalnızca 3 YENİ tablo ekler. Mevcut tablo/veriye DOKUNMAZ.
Eski tenants.core_values/code_of_ethics/quality_policy TEXT kolonları KALIR
(geri-dönüş ağı; "temiz kesim" kararı — yeni tablolar canonical, eski TEXT
okunmaz/yazılmaz ama silinmez).

downgrade() 3 tabloyu drop eder → tam geri-dönüşlü.

Revision ID: a1b2c3d4e5f6
Revises: f5215370eebd
Create Date: 2026-06-17
"""
from alembic import op
import sqlalchemy as sa


revision = "a1b2c3d4e5f6"
down_revision = "f5215370eebd"
branch_labels = None
depends_on = None


def _create_identity_table(name: str) -> None:
    op.create_table(
        name,
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("baslik", sa.String(length=200), nullable=False),
        sa.Column("aciklama", sa.Text(), nullable=True),
        sa.Column("sira", sa.Integer(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    with op.batch_alter_table(name, schema=None) as batch_op:
        batch_op.create_index(batch_op.f(f"ix_{name}_is_active"), ["is_active"], unique=False)
        batch_op.create_index(batch_op.f(f"ix_{name}_tenant_id"), ["tenant_id"], unique=False)


def _drop_identity_table(name: str) -> None:
    with op.batch_alter_table(name, schema=None) as batch_op:
        batch_op.drop_index(batch_op.f(f"ix_{name}_tenant_id"))
        batch_op.drop_index(batch_op.f(f"ix_{name}_is_active"))
    op.drop_table(name)


def upgrade():
    _create_identity_table("tenant_values")
    _create_identity_table("tenant_ethics_codes")
    _create_identity_table("tenant_quality_policies")


def downgrade():
    _drop_identity_table("tenant_quality_policies")
    _drop_identity_table("tenant_ethics_codes")
    _drop_identity_table("tenant_values")
