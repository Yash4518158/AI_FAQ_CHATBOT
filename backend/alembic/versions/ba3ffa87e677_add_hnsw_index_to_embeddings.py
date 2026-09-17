"""add_hnsw_index_to_embeddings

Revision ID: ba3ffa87e677
Revises: 86491a023f05
Create Date: 2026-09-15 08:29:47.693378

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba3ffa87e677'
down_revision: Union[str, Sequence[str], None] = '86491a023f05'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_faq_chunks_embedding_hnsw "
        "ON faq_chunks USING hnsw (embedding vector_cosine_ops);"
    )

def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS ix_faq_chunks_embedding_hnsw;")
