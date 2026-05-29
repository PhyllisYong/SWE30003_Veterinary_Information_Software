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
from app.models.user import User


VET_AUTHOR_EMAILS = ("ann.vet@example.com", "ravi.vet@example.com")
REVIEW_STATUSES = ("draft", "pending_verification", "verified", "rejected")

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

REVIEW_QUIZZES = [
    {
        "title": "Draft Cat Burn Response Quiz",
        "description": "Draft quiz for cat burn first-aid review.",
        "petType": "cat",
        "emergencyCategory": "burns",
        "question": "What should you avoid putting on a cat's minor burn before seeing a vet?",
        "correct": "Creams, oils, butter, or adhesive dressings",
        "wrong": "Cool running water",
        "explanation": "Home remedies can trap heat or irritate tissue. Cool the area and seek veterinary advice.",
    },
    {
        "title": "Rabbit Eye Irritation Review Quiz",
        "description": "Pending verification quiz about rabbit eye irritation warning signs.",
        "petType": "rabbit",
        "emergencyCategory": "eye_injury",
        "question": "What is the safest response if a rabbit is squinting and rubbing one eye?",
        "correct": "Keep the rabbit calm and arrange prompt exotic-vet care",
        "wrong": "Use leftover human eye drops immediately",
        "explanation": "Rabbit eye issues can worsen quickly. Avoid unprescribed drops and seek exotic-vet assessment.",
    },
    {
        "title": "Verified Dog Paw Injury Quiz",
        "description": "Verified quiz awaiting publication for dog paw pad injuries.",
        "petType": "dog",
        "emergencyCategory": "paw_injury",
        "question": "What should you do if a dog has a bleeding paw pad cut?",
        "correct": "Apply light pressure and prevent licking while arranging vet care",
        "wrong": "Let the dog keep walking to see if the bleeding stops",
        "explanation": "Pressure helps bleeding control, and limiting licking reduces contamination before care.",
    },
    {
        "title": "Rejected Hamster Fall Injury Quiz",
        "description": "Rejected quiz draft that needs clearer handling guidance.",
        "petType": "hamster",
        "emergencyCategory": "fall_injury",
        "question": "What should you do after a hamster falls and starts limping?",
        "correct": "Move it gently to a small secure container and contact an exotic-pet vet",
        "wrong": "Keep handling the leg to check whether it improves",
        "explanation": "Repeated handling can worsen pain or injury. Keep movement low and seek veterinary advice.",
    },
    {
        "title": "Draft Guinea Pig Dental Warning Quiz",
        "description": "Draft quiz for guinea pig dental discomfort.",
        "petType": "guinea_pig",
        "emergencyCategory": "dental_issue",
        "question": "What is a common warning sign of dental discomfort in guinea pigs?",
        "correct": "Drooling, reduced appetite, or dropping food",
        "wrong": "Sleeping after eating hay",
        "explanation": "Guinea pig dental issues can quickly affect eating and gut function. Arrange exotic-vet care.",
    },
    {
        "title": "Dog Ear Injury Review Quiz",
        "description": "Pending verification quiz for dog ear injuries.",
        "petType": "dog",
        "emergencyCategory": "ear_injury",
        "question": "What should you avoid when a dog has an ear injury?",
        "correct": "Pushing cotton buds deep into the ear canal",
        "wrong": "Preventing scratching and arranging vet care",
        "explanation": "Deep probing can worsen pain or damage. Keep the dog calm and seek veterinary assessment.",
    },
    {
        "title": "Verified Rabbit Appetite Loss Quiz",
        "description": "Verified quiz awaiting publication for rabbit appetite loss.",
        "petType": "rabbit",
        "emergencyCategory": "appetite_loss",
        "question": "Why is appetite loss urgent in rabbits?",
        "correct": "It can signal serious gut slowdown and needs prompt vet care",
        "wrong": "Rabbits normally skip meals for a day",
        "explanation": "Rabbits that stop eating can deteriorate quickly. Prompt exotic-vet advice is important.",
    },
    {
        "title": "Rejected Cat Tail Injury Quiz",
        "description": "Rejected quiz draft that needs clearer neurological warning signs.",
        "petType": "cat",
        "emergencyCategory": "tail_injury",
        "question": "What is a warning sign after a cat tail injury?",
        "correct": "Dragging the tail or having toileting problems",
        "wrong": "Grooming normally after resting",
        "explanation": "Tail injuries can involve nerves. Changes in movement or toileting need veterinary care.",
    },
]


def get_author_ids(db):
    vets = (
        db.query(User)
        .filter(User.email.in_(VET_AUTHOR_EMAILS), User.role == "veterinarian")
        .all()
    )
    vet_by_email = {vet.email: vet.userID for vet in vets}
    return [vet_by_email[email] for email in VET_AUTHOR_EMAILS if email in vet_by_email]


def reviewer_for(author_id, author_ids):
    for candidate in author_ids:
        if candidate != author_id:
            return candidate
    return None


def seed() -> None:
    db = SessionLocal()
    try:
        author_ids = get_author_ids(db)
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
                    authorVetID=author_ids[quizzes_created % len(author_ids)] if author_ids else None,
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

        for index, quiz_data in enumerate(REVIEW_QUIZZES):
            status = REVIEW_STATUSES[index % len(REVIEW_STATUSES)]
            author_id = author_ids[index % len(author_ids)] if author_ids else None
            quiz = Quiz(
                title=quiz_data["title"],
                description=quiz_data["description"],
                petType=quiz_data["petType"],
                emergencyCategory=quiz_data["emergencyCategory"],
                publicationStatus=status,
                authorVetID=author_id,
                assignedVetID=(
                    reviewer_for(author_id, author_ids)
                    if status in {"pending_verification", "verified", "rejected"}
                    else None
                ),
                reviewComment=(
                    "Please revise the answer wording before resubmitting."
                    if status == "rejected"
                    else None
                ),
                totalScore=1,
                durationSec=60,
            )
            db.add(quiz)
            db.flush()

            question = Question(
                questionText=quiz_data["question"],
                explanation=quiz_data["explanation"],
                quizID=quiz.contentID,
            )
            db.add(question)
            db.flush()

            db.add_all([
                Answer(
                    answerText=quiz_data["correct"],
                    isCorrect=True,
                    questionID=question.questionID,
                ),
                Answer(
                    answerText=quiz_data["wrong"],
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
