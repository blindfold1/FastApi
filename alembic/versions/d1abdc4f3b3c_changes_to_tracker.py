"""changes to tracker

Revision ID: d1abdc4f3b3c
Revises: 924605fb4b8c
Create Date: 2025-04-11 15:15:28.839871

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd1abdc4f3b3c'
down_revision: Union[str, None] = '924605fb4b8c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
