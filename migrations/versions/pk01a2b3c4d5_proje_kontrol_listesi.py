"""Proje kontrol listesi: şablon (kurum+yıl), proje maddeleri, kanıt + project.completed_at

Revision ID: pk01a2b3c4d5
Revises: mg01a2b3c4d5
Create Date: 2026-10-26
"""
from alembic import op
import sqlalchemy as sa

revision = "pk01a2b3c4d5"
down_revision = "mg01a2b3c4d5"
branch_labels = None
depends_on = None


def _has_table(name: str) -> bool:
    return sa.inspect(op.get_bind()).has_table(name)


def _has_column(table: str, column: str) -> bool:
    return column in {c["name"] for c in sa.inspect(op.get_bind()).get_columns(table)}


def _create_tables():
    op.create_table(
        "checklist_template",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("tenant_id", sa.Integer(), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(200), nullable=False, server_default="Kontrol Listesi"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
        sa.UniqueConstraint("tenant_id", "year", name="uq_checklist_template_tenant_year"),
    )
    op.create_index("ix_checklist_template_tenant_id", "checklist_template", ["tenant_id"])
    op.create_index("ix_checklist_template_year", "checklist_template", ["year"])

    op.create_table(
        "checklist_template_item",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("template_id", sa.Integer(), sa.ForeignKey("checklist_template.id", ondelete="CASCADE"), nullable=False),
        sa.Column("stage", sa.String(100), nullable=False),
        sa.Column("item_group", sa.String(60)),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("period_days", sa.Integer()),
        sa.Column("evidence_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
    )
    op.create_index("ix_checklist_template_item_template_id", "checklist_template_item", ["template_id"])

    op.create_table(
        "project_checklist_item",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("project.id", ondelete="CASCADE"), nullable=False),
        sa.Column("source_item_id", sa.Integer(), sa.ForeignKey("checklist_template_item.id", ondelete="SET NULL")),
        sa.Column("stage", sa.String(100), nullable=False),
        sa.Column("item_group", sa.String(60)),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("period_days", sa.Integer()),
        sa.Column("evidence_required", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("status", sa.String(20), nullable=False, server_default="Bekliyor"),
        sa.Column("done_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("done_at", sa.DateTime()),
        sa.Column("approved_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("approved_at", sa.DateTime()),
        sa.Column("note", sa.Text()),
        sa.Column("next_reminder_at", sa.DateTime()),
        sa.Column("last_reminded_at", sa.DateTime()),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime()),
        sa.Column("updated_at", sa.DateTime()),
    )
    op.create_index("ix_project_checklist_item_project_id", "project_checklist_item", ["project_id"])
    op.create_index("ix_project_checklist_item_status", "project_checklist_item", ["status"])
    op.create_index("ix_project_checklist_item_next_reminder_at", "project_checklist_item", ["next_reminder_at"])
    op.create_index("ix_project_checklist_item_is_active", "project_checklist_item", ["is_active"])

    op.create_table(
        "project_checklist_evidence",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("project_checklist_item.id", ondelete="CASCADE"), nullable=False),
        sa.Column("uploader_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("kind", sa.String(10), nullable=False, server_default="file"),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("file_path", sa.String(500)),
        sa.Column("url", sa.String(1000)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime()),
    )
    op.create_index("ix_project_checklist_evidence_item_id", "project_checklist_evidence", ["item_id"])

    op.create_table(
        "project_checklist_assignment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("item_id", sa.Integer(), sa.ForeignKey("project_checklist_item.id", ondelete="CASCADE"), nullable=False),
        sa.Column("target_type", sa.String(10), nullable=False),
        sa.Column("target_id", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("assigned_by", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL")),
        sa.Column("created_at", sa.DateTime()),
        sa.UniqueConstraint("item_id", "target_type", "target_id", name="uq_checklist_assignment_target"),
    )
    op.create_index("ix_project_checklist_assignment_item_id", "project_checklist_assignment", ["item_id"])


def upgrade():
    # İdempotent: tablolar/kolonlar elle (Yerel) açılmış olsa bile migration güvenle koşar.
    if not _has_table("checklist_template"):
        _create_tables()

    if not _has_column("project", "completed_at"):
        op.add_column("project", sa.Column("completed_at", sa.DateTime(), nullable=True))
        op.create_index("ix_project_completed_at", "project", ["completed_at"])
    if not _has_column("project", "completed_by"):
        op.add_column("project", sa.Column("completed_by", sa.Integer(), nullable=True))
        op.create_foreign_key("fk_project_completed_by", "project", "users", ["completed_by"], ["id"], ondelete="SET NULL")


def downgrade():
    op.drop_index("ix_project_completed_at", table_name="project")
    op.drop_constraint("fk_project_completed_by", "project", type_="foreignkey")
    op.drop_column("project", "completed_by")
    op.drop_column("project", "completed_at")
    op.drop_table("project_checklist_assignment")
    op.drop_table("project_checklist_evidence")
    op.drop_table("project_checklist_item")
    op.drop_table("checklist_template_item")
    op.drop_table("checklist_template")
