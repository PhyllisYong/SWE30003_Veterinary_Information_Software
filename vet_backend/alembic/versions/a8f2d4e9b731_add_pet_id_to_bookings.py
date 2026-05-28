"""add pet id to bookings

Revision ID: a8f2d4e9b731
Revises: a1b2c3d4e5f6
Create Date: 2026-05-28 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a8f2d4e9b731"
down_revision: Union[str, None] = "a1b2c3d4e5f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("bookings", sa.Column("pet_id", sa.String(), nullable=True))
    op.create_foreign_key(
        "fk_bookings_pet_id_pets",
        "bookings",
        "pets",
        ["pet_id"],
        ["pet_id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_bookings_pet_id_pets", "bookings", type_="foreignkey")
    op.drop_column("bookings", "pet_id")
