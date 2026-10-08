"""make subscription dates nullable

Revision ID: bd3635b69911
Revises: 1d8ce8525588
Create Date: 2026-10-06 23:31:21.827407

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bd3635b69911'
down_revision: Union[str, Sequence[str], None] = '1d8ce8525588'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "subscriptions",
        "started_at",
        existing_type=sa.DateTime(),
        nullable=True
    )

    op.alter_column(
        "subscriptions",
        "expires_at",
        existing_type=sa.DateTime(),
        nullable=True
    )

    op.alter_column(
        "subscriptions",
        "cancelled_at",
        existing_type=sa.DateTime(),
        nullable=True
    )


def downgrade() -> None:
    op.alter_column(
        "subscriptions",
        "started_at",
        existing_type=sa.DateTime(),
        nullable=False
    )

    op.alter_column(
        "subscriptions",
        "expires_at",
        existing_type=sa.DateTime(),
        nullable=False
    )

    op.alter_column(
        "subscriptions",
        "cancelled_at",
        existing_type=sa.DateTime(),
        nullable=False
    )