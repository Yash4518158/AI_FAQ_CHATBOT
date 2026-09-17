"""create vector extension

Revision ID: 19a1b7f98776
Revises: ea3a602dedd5
Create Date: 2026-09-15 05:32:52.918009

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '19a1b7f98776'
down_revision: Union[str, Sequence[str], None] = 'ea3a602dedd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('CREATE EXTENSION IF NOT EXISTS vector;')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('DROP EXTENSION IF EXISTS vector;')
