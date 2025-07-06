"""make scanner.assigned_stall_id nullable

Revision ID: 2e446586fcf8
Revises:
Create Date: 2025-07-06 18:15:06.987479

"""

from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "2e446586fcf8"
down_revision: Union[str, None] = "0001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("scanner_users", "assigned_stall_id", nullable=True)
    """Upgrade schema."""


def downgrade() -> None:
    op.alter_column("scanner_users", "assigned_stall_id", nullable=False)
    """Downgrade schema."""
