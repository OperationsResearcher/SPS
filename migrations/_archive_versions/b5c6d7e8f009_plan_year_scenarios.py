"""plan_year_scenarios — Scenario Branching (Sprint 56 — Ö5)

Revision ID: b5c6d7e8f009
Revises: a4b5c6d7e008
Create Date: 2026-05-24

scenario_of_id + scenario_label kolonları. Senaryo kayıtlar için
(tenant_id, year) unique kısıtı partial index'e dönüştürülür
(yalnızca scenario_of_id IS NULL olanlar için).
"""

from alembic import op
import sqlalchemy as sa


revision = "b5c6d7e8f009"
down_revision = "a4b5c6d7e008"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "plan_years",
        sa.Column("scenario_of_id", sa.Integer(),
                  sa.ForeignKey("plan_years.id", ondelete="CASCADE"), nullable=True),
    )
    op.add_column("plan_years", sa.Column("scenario_label", sa.String(80), nullable=True))
    op.create_index("idx_plan_year_scenario_of", "plan_years", ["scenario_of_id"])

    # Replace unique constraint with partial unique index (Postgres)
    op.drop_constraint("uq_plan_year_tenant_year", "plan_years", type_="unique")
    op.execute(
        "CREATE UNIQUE INDEX uq_plan_year_tenant_year_main "
        "ON plan_years (tenant_id, year) WHERE scenario_of_id IS NULL"
    )


def downgrade():
    op.execute("DROP INDEX IF EXISTS uq_plan_year_tenant_year_main")
    op.create_unique_constraint(
        "uq_plan_year_tenant_year", "plan_years", ["tenant_id", "year"]
    )
    op.drop_index("idx_plan_year_scenario_of", table_name="plan_years")
    op.drop_column("plan_years", "scenario_label")
    op.drop_column("plan_years", "scenario_of_id")
