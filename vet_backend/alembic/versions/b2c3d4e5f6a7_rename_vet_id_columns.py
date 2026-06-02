"""rename vet id columns to match UML

Revision ID: b2c3d4e5f6a7
Revises: a8f2d4e9b731
Create Date: 2026-06-02 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a8f2d4e9b731'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # first_aid_contents: author_vet_id → author_veterinarian_id
    op.alter_column('first_aid_contents', 'author_vet_id',
                    new_column_name='author_veterinarian_id')
    # first_aid_contents: assigned_vet_id → assigned_veterinarian_id
    op.alter_column('first_aid_contents', 'assigned_vet_id',
                    new_column_name='assigned_veterinarian_id')
    # bookings: vet_id → veterinarian_id
    op.alter_column('bookings', 'vet_id',
                    new_column_name='veterinarian_id')
    # vet_advice_chats: vet_id → veterinarian_id
    op.alter_column('vet_advice_chats', 'vet_id',
                    new_column_name='veterinarian_id')


def downgrade() -> None:
    op.alter_column('vet_advice_chats', 'veterinarian_id',
                    new_column_name='vet_id')
    op.alter_column('bookings', 'veterinarian_id',
                    new_column_name='vet_id')
    op.alter_column('first_aid_contents', 'assigned_veterinarian_id',
                    new_column_name='assigned_vet_id')
    op.alter_column('first_aid_contents', 'author_veterinarian_id',
                    new_column_name='author_vet_id')
