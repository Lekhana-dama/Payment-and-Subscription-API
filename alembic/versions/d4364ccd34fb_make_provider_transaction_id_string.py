"""make provider transaction id string

Revision ID: d4364ccd34fb
Revises: bd3635b69911
Create Date: 2026-10-07 10:39:46.503419

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'd4364ccd34fb'
down_revision: Union[str, Sequence[str], None] = 'bd3635b69911'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.alter_column(
        'payments',
        'provider_transaction_id',
        existing_type=sa.INTEGER(),
        type_=sa.String(),
        existing_nullable=False
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    op.alter_column(
        'payments',
        'provider_transaction_id',
        existing_type=sa.String(),
        type_=sa.INTEGER(),
        existing_nullable=False
    )
