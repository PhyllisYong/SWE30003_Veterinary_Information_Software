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
        # ── Quiz 1: Dog Food Safety ───────────────────────────────────────
        quiz1 = Quiz(
            title="Dog Food Safety Quiz",
            description="Test your knowledge on which everyday foods are dangerous for dogs.",
            petType="dog",
            emergencyCategory="poisoning",
            publicationStatus="published",
            totalScore=1,
            durationSec=60,
        )
        db.add(quiz1)
        db.flush()

        q1 = Question(
            questionText="Which of the following foods is toxic to dogs?",
            explanation=(
                "Chocolate contains theobromine and caffeine, which dogs cannot "
                "metabolise. Even small amounts can cause vomiting, tremors, seizures, "
                "or death. Always keep chocolate completely out of your dog's reach."
            ),
            quizID=quiz1.contentID,
        )
        db.add(q1)
        db.flush()

        db.add_all([
            Answer(answerText="Chocolate", isCorrect=True, questionID=q1.questionID),
            Answer(answerText="Cooked chicken", isCorrect=False, questionID=q1.questionID),
        ])

        db.commit()
        print(f"✓ Quiz 1 seeded  (id={quiz1.contentID})")

        # ── Quiz 2: Cat Emergency First Aid ──────────────────────────────
        quiz2 = Quiz(
            title="Cat Emergency First Aid",
            description="How well do you know what to do in a cat emergency? Test yourself.",
            petType="cat",
            emergencyCategory="general",
            publicationStatus="published",
            totalScore=5,
            durationSec=300,
        )
        db.add(quiz2)
        db.flush()

        questions_data = [
            {
                "text": "Your cat is choking and pawing at its mouth. What is the first thing you should do?",
                "explanation": (
                    "Opening the mouth to check for a visible obstruction is always the first step. "
                    "Only attempt to remove an object if you can clearly see it — blind sweeping can "
                    "push the object deeper. If the cat is unconscious or you cannot dislodge it, "
                    "perform modified Heimlich compressions and get to a vet immediately."
                ),
                "answers": [
                    ("Open the mouth and look for a visible obstruction", True),
                    ("Give the cat water to help it swallow", False),
                    ("Leave it alone — cats resolve choking on their own", False),
                    ("Immediately perform CPR", False),
                ],
            },
            {
                "text": "A cat has a bleeding wound on its leg. Which action should you take first?",
                "explanation": (
                    "Direct pressure with a clean cloth slows or stops bleeding by allowing clotting "
                    "to begin. Tourniquets are a last resort for severe, uncontrollable limb bleeding "
                    "and can cause tissue damage if left on too long. Never remove an embedded object "
                    "as it may be acting as a plug."
                ),
                "answers": [
                    ("Apply firm, direct pressure with a clean cloth", True),
                    ("Rinse the wound under running water for 10 minutes", False),
                    ("Apply a tight tourniquet above the wound straight away", False),
                    ("Remove any embedded object to clean the wound", False),
                ],
            },
            {
                "text": "You suspect your cat has heatstroke. Its body temperature feels very high. What should you do?",
                "explanation": (
                    "Moving the cat to a cool area and applying cool (not ice cold) water helps lower "
                    "body temperature gradually. Ice water or ice packs can cause blood vessels to "
                    "constrict, trapping heat inside the body and worsening the condition. Always "
                    "follow up with a vet visit even if the cat appears to recover."
                ),
                "answers": [
                    ("Move to a cool area and apply cool (not ice cold) water to the fur", True),
                    ("Wrap the cat tightly in a wet towel to trap the coolness", False),
                    ("Give the cat cold water to drink immediately", False),
                    ("Place the cat in a bucket of ice water", False),
                ],
            },
            {
                "text": "Your cat has ingested a potentially toxic plant. It is conscious and alert. What is the correct first step?",
                "explanation": (
                    "Contacting a vet or animal poison control is always the correct first step — they "
                    "can advise whether the specific plant is toxic and what treatment is needed. "
                    "Never induce vomiting without professional guidance, as some toxins cause more "
                    "damage coming back up. Do not give milk; it does not neutralise plant toxins."
                ),
                "answers": [
                    ("Call a vet or animal poison control for guidance", True),
                    ("Induce vomiting immediately to remove the toxin", False),
                    ("Give the cat milk to neutralise the poison", False),
                    ("Wait and monitor — most plants are not harmful", False),
                ],
            },
            {
                "text": "A cat has been in a road accident and may have internal injuries. How should you transport it to the vet?",
                "explanation": (
                    "A flat, rigid surface like a board or a box minimises movement of the spine and "
                    "internal organs during transport, reducing the risk of worsening injuries. "
                    "Carrying a trauma cat loosely in your arms or letting it walk can aggravate "
                    "spinal, pelvic, or internal injuries. Keep the cat warm and calm throughout."
                ),
                "answers": [
                    ("Place on a flat, rigid surface such as a board or firm box", True),
                    ("Carry it gently in your arms, keeping it warm", False),
                    ("Let the cat walk to the car to assess if it can bear weight", False),
                    ("Hold the cat firmly by the scruff to prevent struggling", False),
                ],
            },
        ]

        for qdata in questions_data:
            q = Question(
                questionText=qdata["text"],
                explanation=qdata["explanation"],
                quizID=quiz2.contentID,
            )
            db.add(q)
            db.flush()
            for answer_text, is_correct in qdata["answers"]:
                db.add(Answer(
                    answerText=answer_text,
                    isCorrect=is_correct,
                    questionID=q.questionID,
                ))

        db.commit()
        print(f"✓ Quiz 2 seeded  (id={quiz2.contentID})")

    except Exception as e:
        db.rollback()
        print(f"✗ Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
