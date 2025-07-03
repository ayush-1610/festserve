"""init

Revision ID: 1fa772acc3ca
Revises: e798d9141c76
Create Date: 2025-07-03 23:42:11.917134

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1fa772acc3ca'
down_revision: Union[str, None] = 'e798d9141c76'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
