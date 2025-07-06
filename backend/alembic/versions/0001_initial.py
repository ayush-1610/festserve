"""Initial migration creating core tables"""

from typing import Sequence, Union

from alembic import op
from festserve_api.models import Base

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create tables."""
    bind = op.get_bind()
    Base.metadata.create_all(bind=bind)


def downgrade() -> None:
    """Drop tables."""
    bind = op.get_bind()
    Base.metadata.drop_all(bind=bind)
