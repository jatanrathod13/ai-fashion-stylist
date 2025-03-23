"""add_description_to_recommendations

Revision ID: 2debd155ce6f
Revises: a7c7f55ae60f
Create Date: 2025-03-22 06:13:49.964860

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2debd155ce6f'
down_revision: Union[str, None] = 'a7c7f55ae60f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('recommendations', sa.Column('description', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('recommendations', 'description')
