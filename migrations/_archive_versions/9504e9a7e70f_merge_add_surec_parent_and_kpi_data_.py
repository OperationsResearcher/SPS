"""noop: eski merge düğümü — artık tek hat (e7a8 → add_surec_parent → 9504 → a1c2)

Revision ID: 9504e9a7e70f
Revises: add_surec_parent
Create Date: 2026-03-21 22:13:43.009269

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9504e9a7e70f'
down_revision = 'add_surec_parent'
branch_labels = None
depends_on = None


def upgrade():
    pass


def downgrade():
    pass
