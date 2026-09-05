"""Add confirmed reservation status

Revision ID: 5ce42f92673a
Revises: 1e263b2a267f
Create Date: 2026-08-31 11:57:11.658780

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5ce42f92673a'
down_revision = '1e263b2a267f'
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        "ALTER TYPE reservation_status ADD VALUE IF NOT EXISTS 'Confirmed'"
    )


def downgrade():
    pass
