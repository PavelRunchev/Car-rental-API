"""Add new column payment_method

Revision ID: a424573b8044
Revises: 5ce42f92673a
Create Date: 2026-08-31 12:28:54.181433

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a424573b8044'
down_revision = '5ce42f92673a'
branch_labels = None
depends_on = None


def upgrade():
    payment_method_enum = sa.Enum(
        "Online",
        "Terminal",
        name="payment_method"
    )

    payment_method_enum.create(op.get_bind(), checkfirst=True)

    with op.batch_alter_table("payments", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "payment_method",
                payment_method_enum,
                nullable=False
            )
        )


def downgrade():
    with op.batch_alter_table("payments", schema=None) as batch_op:
        batch_op.drop_column("payment_method")

    payment_method_enum = sa.Enum(
        "Online",
        "Terminal",
        name="payment_method"
    )

    payment_method_enum.drop(op.get_bind(), checkfirst=True)