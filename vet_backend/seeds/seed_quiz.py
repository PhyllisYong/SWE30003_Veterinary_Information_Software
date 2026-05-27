"""
Seed: one dog food-poisoning quiz with one question and two answers.

Run from vet_backend/:
    python -m seeds.seed_quiz
"""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer


def seed() -> None:
    db = SessionLocal()
    try:
        # ── Quiz (inherits FirstAidContent via joined-table inheritance) ──
        quiz = Quiz(
            title="Dog Food Safety Quiz",
            description="Test your knowledge on which everyday foods are dangerous for dogs.",
            petType="dog",
            emergencyCategory="poisoning",
            publicationStatus="published",
            totalScore=1,
            durationSec=60,
        )
        db.add(quiz)
        db.flush()  # assigns quiz.contentID before we reference it

        # ── Question ──────────────────────────────────────────────────────
        question = Question(
            questionText="Which of the following foods is toxic to dogs?",
            explanation=(
                "Chocolate contains theobromine and caffeine, which dogs cannot "
                "metabolise. Even small amounts can cause vomiting, tremors, seizures, "
                "or death. Always keep chocolate completely out of your dog's reach."
            ),
            quizID=quiz.contentID,
        )
        db.add(question)
        db.flush()  # assigns question.questionID before answers reference it

        # ── Answers ───────────────────────────────────────────────────────
        db.add_all([
            Answer(
                answerText="Chocolate",
                isCorrect=True,
                questionID=question.questionID,
            ),
            Answer(
                answerText="Cooked chicken",
                isCorrect=False,
                questionID=question.questionID,
            ),
        ])

        db.commit()
        print(f"✓ Quiz seeded  (id={quiz.contentID})")
        print(f"  Question     (id={question.questionID})")

    except Exception as e:
        db.rollback()
        print(f"✗ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
