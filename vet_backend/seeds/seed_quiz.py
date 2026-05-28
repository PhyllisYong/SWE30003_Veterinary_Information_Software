"""
Seed first-aid quizzes for every supported pet and emergency category.

Run from vet_backend/:
    python -m seeds.seed_quiz
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.answer import Answer
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.quiz_result import QuizResult


PET_LABELS = {
    "cat": "Cat",
    "dog": "Dog",
    "rabbit": "Rabbit",
    "hamster": "Hamster",
    "guinea_pig": "Guinea Pig",
}

CATEGORY_LABELS = {
    "choking": "Choking and Breathing",
    "bleeding": "Wounds and Bleeding",
    "poisoning": "Poisoning and Ingestion",
    "fracture": "Fractures and Injuries",
    "heatstroke": "Heatstroke and Shock",
}

QUESTION_BANK = {
    "choking": {
        "question": "What is the safest first action if your pet is struggling to breathe?",
        "correct": "Keep the pet calm and contact a veterinarian immediately",
        "wrong": "Put your fingers deep into the mouth repeatedly",
        "explanation": (
            "Breathing emergencies can worsen quickly. Keep the pet calm, avoid blind "
            "finger sweeps, and seek urgent veterinary help."
        ),
    },
    "bleeding": {
        "question": "What should you do for active bleeding while arranging veterinary care?",
        "correct": "Apply steady pressure with clean gauze or cloth",
        "wrong": "Rinse continuously and leave the wound uncovered",
        "explanation": (
            "Direct pressure helps slow bleeding. Use a clean material and keep pressure "
            "in place while preparing transport to a vet."
        ),
    },
    "poisoning": {
        "question": "What should you do if you think your pet swallowed something toxic?",
        "correct": "Call a veterinarian or poison helpline with details of the item",
        "wrong": "Force vomiting immediately without professional advice",
        "explanation": (
            "Some substances cause more harm if vomiting is induced. Get professional "
            "instructions and bring packaging or a sample when possible."
        ),
    },
    "fracture": {
        "question": "How should you handle a pet with a suspected fracture or serious injury?",
        "correct": "Limit movement and transport the pet on a stable surface",
        "wrong": "Pull or straighten the injured limb before travelling",
        "explanation": (
            "Movement can worsen fractures or spinal injuries. Keep the pet still and "
            "support the body during transport."
        ),
    },
    "heatstroke": {
        "question": "What is the safest first-aid response for suspected heatstroke?",
        "correct": "Move the pet to a cool place and contact a veterinarian",
        "wrong": "Use ice-cold water and wait to see if symptoms stop",
        "explanation": (
            "Heatstroke is life-threatening. Start gentle cooling, offer small amounts "
            "of water if alert, and seek urgent veterinary care."
        ),
    },
}


def seed() -> None:
    db = SessionLocal()
    try:
        db.query(QuizResult).delete(synchronize_session=False)
        for quiz in db.query(Quiz).all():
            db.delete(quiz)
        db.flush()

        quizzes_created = 0
        for pet_type, pet_label in PET_LABELS.items():
            for category, category_label in CATEGORY_LABELS.items():
                item = QUESTION_BANK[category]
                quiz = Quiz(
                    title=f"{pet_label} {category_label} Quiz",
                    description=f"Check your readiness for {category_label.lower()} emergencies in {pet_label.lower()}s.",
                    petType=pet_type,
                    emergencyCategory=category,
                    publicationStatus="published",
                    totalScore=1,
                    durationSec=60,
                )
                db.add(quiz)
                db.flush()

                question = Question(
                    questionText=item["question"],
                    explanation=item["explanation"],
                    quizID=quiz.contentID,
                )
                db.add(question)
                db.flush()

                db.add_all([
                    Answer(
                        answerText=item["correct"],
                        isCorrect=True,
                        questionID=question.questionID,
                    ),
                    Answer(
                        answerText=item["wrong"],
                        isCorrect=False,
                        questionID=question.questionID,
                    ),
                ])
                quizzes_created += 1

        db.commit()
        print(f"Seeded {quizzes_created} quizzes")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
