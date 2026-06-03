"""rename attributes to match UML: duration, totalScore, petOwnerID

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-06-03 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


revision: str = 'c3d4e5f6a7b8'
down_revision: Union[str, None] = 'b2c3d4e5f6a7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # videos.duration_sec → duration
    op.alter_column('videos', 'duration_sec', new_column_name='duration')
    # quizzes.duration_sec → duration
    op.alter_column('quizzes', 'duration_sec', new_column_name='duration')
    # quiz_results.score → total_score (matches QuizResult.totalScore)
    op.alter_column('quiz_results', 'score', new_column_name='total_score')
    # pets.owner_id → pet_owner_id (matches Pet.petOwnerID)
    op.alter_column('pets', 'owner_id', new_column_name='pet_owner_id')


def downgrade() -> None:
    op.alter_column('pets', 'pet_owner_id', new_column_name='owner_id')
    op.alter_column('quiz_results', 'total_score', new_column_name='score')
    op.alter_column('quizzes', 'duration', new_column_name='duration_sec')
    op.alter_column('videos', 'duration', new_column_name='duration_sec')
