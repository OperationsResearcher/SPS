# -*- coding: utf-8 -*-
"""SWOT SaaS bileşen kayitlarini kaldir (system_components, module_component_slugs, route_registry)

Revision ID: q1w2e3r4t005
Revises: p0q1r2s3sw01
Create Date: 2026-03-26

"""
from alembic import op
import sqlalchemy as sa


revision = "q1w2e3r4t005"
down_revision = "p0q1r2s3sw01"
branch_labels = None
depends_on = None

def upgrade():
    bind = op.get_bind()
    insp = sa.inspect(bind)
    _del = (
        "DELETE FROM module_component_slugs WHERE component_slug IN ('swot_analizi', 'swot_analysis')"
    )
    if insp.has_table("module_component_slugs"):
        op.execute(sa.text(_del))
    if insp.has_table("route_registry"):
        op.execute(
            sa.text(
                "DELETE FROM route_registry WHERE component_slug IN ('swot_analizi', 'swot_analysis')"
            )
        )
    if insp.has_table("system_components"):
        op.execute(
            sa.text(
                "DELETE FROM system_components WHERE code IN ('swot_analizi', 'swot_analysis')"
            )
        )


def downgrade():
    pass
