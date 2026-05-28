"""add review comment

Revision ID: a1b2c3d4e5f6
Revises: fc39be3c2e8e
Create Date: 2026-05-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'fc39be3c2e8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('first_aid_contents', sa.Column('review_comment', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('first_aid_contents', 'review_comment')
