"""user_year_assignments — Çalışanın yıllık snapshot rolü/departmanı

Revision ID: j3k4l5m6n017
Revises: i2j3k4l5m016
Create Date: 2026-05-27

Tarih egemen plan year doktrininin (Faz 3) parçası.

Kullanıcı kalıcı kimlik, ama job_title/department/role yıldan yıla değişebilir.
Bu tablo o yıla ait snapshot rolü saklar — historical raporlamada
"Mehmet Bey 2022'de uzmandı, 2026'da yöneticidir" sorgusu çalışabilsin diye.

Eksiklikte fallback: users.job_title/department alanları (geçmiş yıllar için
mevcut değerler kabul edilir).
"""
from alembic import op
import sqlalchemy as sa


revision = "j3k4l5m6n017"
down_revision = "i2j3k4l5m016"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "user_year_assignments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("plan_year_id", sa.Integer(), nullable=False),
        sa.Column("tenant_id", sa.Integer(), nullable=False),
        sa.Column("job_title", sa.String(150), nullable=True),
        sa.Column("department", sa.String(150), nullable=True),
        sa.Column("role_label", sa.String(80), nullable=True),
        sa.Column("note", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False,
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.Column("updated_at", sa.DateTime(), nullable=False,
                  server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_year_id"], ["plan_years.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.UniqueConstraint("user_id", "plan_year_id", name="uq_user_year_assignment"),
    )
    op.create_index("ix_uya_user", "user_year_assignments", ["user_id"])
    op.create_index("ix_uya_plan_year", "user_year_assignments", ["plan_year_id"])
    op.create_index("ix_uya_tenant", "user_year_assignments", ["tenant_id"])


def downgrade():
    op.drop_index("ix_uya_tenant", table_name="user_year_assignments")
    op.drop_index("ix_uya_plan_year", table_name="user_year_assignments")
    op.drop_index("ix_uya_user", table_name="user_year_assignments")
    op.drop_table("user_year_assignments")
