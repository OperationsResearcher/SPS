"""ProcessActivity V2: datetime, assignee, reminder

Revision ID: 4f3a2b1c9d8e
Revises: c7d8e9f0a1b2
Create Date: 2026-03-23
"""
from alembic import op
import sqlalchemy as sa


revision = "4f3a2b1c9d8e"
down_revision = "c7d8e9f0a1b2"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("process_activities", schema=None) as batch_op:
        batch_op.add_column(sa.Column("start_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("end_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("notify_email", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column("auto_complete_enabled", sa.Boolean(), nullable=False, server_default=sa.true()))
        batch_op.add_column(sa.Column("auto_pgv_created", sa.Boolean(), nullable=False, server_default=sa.false()))
        batch_op.add_column(sa.Column("auto_pgv_kpi_data_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("completed_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("cancelled_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("postponed_at", sa.DateTime(), nullable=True))
        batch_op.create_index(batch_op.f("ix_process_activities_start_at"), ["start_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_process_activities_end_at"), ["end_at"], unique=False)
        batch_op.create_index(batch_op.f("ix_process_activities_auto_pgv_created"), ["auto_pgv_created"], unique=False)
        batch_op.create_index(batch_op.f("ix_process_activities_auto_pgv_kpi_data_id"), ["auto_pgv_kpi_data_id"], unique=False)
        batch_op.create_foreign_key(
            "fk_process_activities_auto_pgv_kpi_data_id",
            "kpi_data",
            ["auto_pgv_kpi_data_id"],
            ["id"],
            ondelete="SET NULL",
        )

    op.create_table(
        "process_activity_assignees",
        sa.Column("activity_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("order_no", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("assigned_by", sa.Integer(), nullable=True),
        sa.Column("assigned_at", sa.DateTime(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["activity_id"], ["process_activities.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["assigned_by"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("activity_id", "user_id"),
    )
    op.create_index("ix_process_activity_assignees_assigned_by", "process_activity_assignees", ["assigned_by"], unique=False)

    op.create_table(
        "process_activity_reminders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("activity_id", sa.Integer(), nullable=False),
        sa.Column("minutes_before", sa.Integer(), nullable=False),
        sa.Column("remind_at", sa.DateTime(), nullable=False),
        sa.Column("channel_email", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("sent_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["activity_id"], ["process_activities.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("activity_id", "minutes_before", name="uq_activity_reminder_offset"),
    )
    op.create_index("ix_process_activity_reminders_activity_id", "process_activity_reminders", ["activity_id"], unique=False)
    op.create_index("ix_process_activity_reminders_remind_at", "process_activity_reminders", ["remind_at"], unique=False)
    op.create_index("ix_process_activity_reminders_sent_at", "process_activity_reminders", ["sent_at"], unique=False)

    # Legacy start_date/end_date -> start_at/end_at
    op.execute(
        sa.text(
            """
            UPDATE process_activities
            SET
              start_at = CASE
                WHEN start_date IS NOT NULL THEN datetime(start_date || ' 00:00:00')
                ELSE NULL
              END,
              end_at = CASE
                WHEN end_date IS NOT NULL THEN datetime(end_date || ' 23:59:59')
                ELSE NULL
              END
            """
        )
    )


def downgrade():
    op.drop_index("ix_process_activity_reminders_sent_at", table_name="process_activity_reminders")
    op.drop_index("ix_process_activity_reminders_remind_at", table_name="process_activity_reminders")
    op.drop_index("ix_process_activity_reminders_activity_id", table_name="process_activity_reminders")
    op.drop_table("process_activity_reminders")

    op.drop_index("ix_process_activity_assignees_assigned_by", table_name="process_activity_assignees")
    op.drop_table("process_activity_assignees")

    with op.batch_alter_table("process_activities", schema=None) as batch_op:
        batch_op.drop_constraint("fk_process_activities_auto_pgv_kpi_data_id", type_="foreignkey")
        batch_op.drop_index(batch_op.f("ix_process_activities_auto_pgv_kpi_data_id"))
        batch_op.drop_index(batch_op.f("ix_process_activities_auto_pgv_created"))
        batch_op.drop_index(batch_op.f("ix_process_activities_end_at"))
        batch_op.drop_index(batch_op.f("ix_process_activities_start_at"))
        batch_op.drop_column("postponed_at")
        batch_op.drop_column("cancelled_at")
        batch_op.drop_column("completed_at")
        batch_op.drop_column("auto_pgv_kpi_data_id")
        batch_op.drop_column("auto_pgv_created")
        batch_op.drop_column("auto_complete_enabled")
        batch_op.drop_column("notify_email")
        batch_op.drop_column("end_at")
        batch_op.drop_column("start_at")
