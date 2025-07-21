"""add password_hash to advertisers

Revision ID: d28ca03a8465
Revises: 2e446586fcf8
Create Date: 2025-07-06 18:37:02.636037

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "d28ca03a8465"
down_revision: Union[str, None] = "2e446586fcf8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column(
        "advertisers",
        sa.Column(
            "password_hash", sa.String(), nullable=False, server_default=sa.text("''")
        ),
    )
    op.alter_column("advertisers", "password_hash", server_default=None)


def downgrade():
    op.drop_column("advertisers", "password_hash")
