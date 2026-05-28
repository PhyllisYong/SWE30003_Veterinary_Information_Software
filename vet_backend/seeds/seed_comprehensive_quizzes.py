"""
Seed two comprehensive 5-question first-aid quizzes:
  - Dog First Aid Essentials
  - Cat First Aid Essentials

Run from vet_backend/:
    python -m seeds.seed_comprehensive_quizzes
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.core.database import SessionLocal
from app.models.answer import Answer
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.quiz_result import QuizResult

QUIZZES = [
    {
        "title": "Dog First Aid Essentials",
        "description": "Test your knowledge of common first-aid situations for dogs, from choking to heatstroke.",
        "petType": "dog",
        "emergencyCategory": "general",
        "totalScore": 5,
        "durationSec": 300,
        "questions": [
            {
                "questionText": "Your dog is choking and pawing at its mouth but is still conscious. What is the first thing you should do?",
                "explanation": "Open the mouth carefully and look for a visible object. Only attempt removal if you can clearly see and reach it — blind probing can push the object deeper. If unsuccessful, apply back blows between the shoulder blades and seek emergency vet care immediately.",
                "answers": [
                    {"text": "Open the mouth, look for a visible obstruction and remove it only if clearly reachable", "correct": True},
                    {"text": "Perform abdominal thrusts the same way you would on a human", "correct": False},
                    {"text": "Give the dog water to dislodge the object", "correct": False},
                    {"text": "Wait 10 minutes to see if the dog clears it on its own", "correct": False},
                ],
            },
            {
                "questionText": "Your dog has a deep cut on its leg that is bleeding heavily. What should you do while travelling to the vet?",
                "explanation": "Firm, steady pressure with a clean cloth is the most effective way to slow bleeding. Avoid removing the cloth once applied — if it soaks through, add more material on top. Do not apply a tourniquet unless bleeding is life-threatening and you have no other option.",
                "answers": [
                    {"text": "Apply firm pressure with a clean cloth and keep it in place", "correct": True},
                    {"text": "Rinse the wound repeatedly with water and leave it uncovered", "correct": False},
                    {"text": "Apply a tight tourniquet above the wound immediately", "correct": False},
                    {"text": "Let the wound air out to help clotting", "correct": False},
                ],
            },
            {
                "questionText": "On a hot day your dog collapses, is panting heavily, and has bright red gums. What is the correct response?",
                "explanation": "These are signs of heatstroke, which can be fatal. Move the dog to a cool area and apply cool (not ice cold) water to the body, especially the neck, armpits, and groin. Ice water can cause blood vessels to constrict and worsen the condition. Seek emergency vet care immediately.",
                "answers": [
                    {"text": "Move the dog to shade, apply cool water to the body, and call a vet", "correct": True},
                    {"text": "Submerge the dog in ice water to bring the temperature down quickly", "correct": False},
                    {"text": "Give the dog a large amount of cold water to drink", "correct": False},
                    {"text": "Keep the dog active to stimulate circulation", "correct": False},
                ],
            },
            {
                "questionText": "You suspect your dog has eaten rat poison. It is alert and showing no symptoms yet. What should you do?",
                "explanation": "Call a vet or animal poison control immediately — do not wait for symptoms, as many toxins cause delayed internal damage. Never induce vomiting without professional advice, as this can cause additional harm with certain substances. Bring the packaging if possible.",
                "answers": [
                    {"text": "Call a vet or poison helpline immediately with details of the substance", "correct": True},
                    {"text": "Induce vomiting straight away using salt or mustard", "correct": False},
                    {"text": "Give the dog milk to neutralise the poison", "correct": False},
                    {"text": "Wait and monitor for symptoms before contacting a vet", "correct": False},
                ],
            },
            {
                "questionText": "Your dog fell and is holding its front leg off the ground and crying when you touch it. How should you handle transport to the vet?",
                "explanation": "Suspected fractures must be kept as still as possible. Avoid attempting to splint unless trained to do so, as incorrect splinting can worsen the injury. Support the dog's body on a flat surface and minimise movement during transport. Muzzle the dog if there is a risk of biting due to pain.",
                "answers": [
                    {"text": "Keep the dog as still as possible and support its body on a flat surface", "correct": True},
                    {"text": "Straighten the leg and apply a makeshift splint before moving", "correct": False},
                    {"text": "Let the dog walk slowly to keep blood flowing to the limb", "correct": False},
                    {"text": "Massage the leg to check for swelling before travelling", "correct": False},
                ],
            },
        ],
    },
    {
        "title": "Cat First Aid Essentials",
        "description": "Test your knowledge of common first-aid situations for cats, from burns to breathing problems.",
        "petType": "cat",
        "emergencyCategory": "general",
        "totalScore": 5,
        "durationSec": 300,
        "questions": [
            {
                "questionText": "Your cat is having a seizure and is thrashing on the floor. What should you do?",
                "explanation": "Never restrain a seizing cat — you risk injury to yourself and the cat. Instead, clear the area of hazards and time the seizure. Most seizures last under two minutes. After it stops, keep the cat warm, quiet, and darkened, and contact your vet promptly.",
                "answers": [
                    {"text": "Clear the area of hazards, time the seizure, and contact a vet afterwards", "correct": True},
                    {"text": "Hold the cat firmly to prevent it from hurting itself", "correct": False},
                    {"text": "Put something in the cat's mouth to prevent it biting its tongue", "correct": False},
                    {"text": "Give the cat water immediately after the seizure stops", "correct": False},
                ],
            },
            {
                "questionText": "Your cat has a small burn on its paw from stepping on a hot surface. What is the correct immediate action?",
                "explanation": "Cool the burn with cool (not cold or iced) running water for at least 10 minutes to stop tissue damage. Do not apply butter, toothpaste, or any home remedy — these trap heat and increase infection risk. Cover loosely and see a vet.",
                "answers": [
                    {"text": "Run cool water over the burn for at least 10 minutes", "correct": True},
                    {"text": "Apply butter or coconut oil to soothe the skin", "correct": False},
                    {"text": "Wrap the paw tightly in a bandage and leave it", "correct": False},
                    {"text": "Apply ice directly to the burn to cool it fast", "correct": False},
                ],
            },
            {
                "questionText": "You find your cat unconscious and not breathing. What is the correct order of actions?",
                "explanation": "Check for responsiveness first, then clear the airway before attempting rescue breathing. Compress the chest at a rate of 100–120 per minute for cats (two fingers on the sternum). Always combine compressions with rescue breaths and get to a vet as fast as possible.",
                "answers": [
                    {"text": "Check responsiveness, clear the airway, begin CPR, and transport to a vet urgently", "correct": True},
                    {"text": "Begin chest compressions immediately without checking the airway", "correct": False},
                    {"text": "Give rescue breaths only — chest compressions can break ribs", "correct": False},
                    {"text": "Wait two minutes for the cat to recover before calling a vet", "correct": False},
                ],
            },
            {
                "questionText": "Your cat has eaten a lily flower. It seems fine right now. What should you do?",
                "explanation": "Lilies are highly toxic to cats and can cause acute kidney failure even in small amounts. Symptoms may be delayed by hours. This is a veterinary emergency — do not wait for signs of illness. Contact a vet or poison helpline immediately.",
                "answers": [
                    {"text": "Contact a vet immediately — lily ingestion is a life-threatening emergency in cats", "correct": True},
                    {"text": "Monitor the cat for 24 hours and call a vet only if symptoms appear", "correct": False},
                    {"text": "Give the cat milk to dilute the toxin", "correct": False},
                    {"text": "Induce vomiting at home to remove the lily", "correct": False},
                ],
            },
            {
                "questionText": "Your cat is breathing rapidly, has its mouth open, and its gums look bluish. What does this indicate and what should you do?",
                "explanation": "Open-mouth breathing and blue-tinged gums (cyanosis) in a cat signal a serious breathing emergency — cats almost never breathe through their mouths normally. Keep the cat as calm and still as possible, minimise handling, and get to an emergency vet immediately.",
                "answers": [
                    {"text": "This is a breathing emergency — keep the cat calm and go to an emergency vet immediately", "correct": True},
                    {"text": "The cat is overheated — place it in front of a fan", "correct": False},
                    {"text": "Offer food and water, as the cat may just be stressed", "correct": False},
                    {"text": "Perform back blows to help the cat clear its airway", "correct": False},
                ],
            },
        ],
    },
]


def seed() -> None:
    db = SessionLocal()
    try:
        created = 0
        for quiz_data in QUIZZES:
            quiz = Quiz(
                title=quiz_data["title"],
                description=quiz_data["description"],
                petType=quiz_data["petType"],
                emergencyCategory=quiz_data["emergencyCategory"],
                publicationStatus="published",
                totalScore=quiz_data["totalScore"],
                durationSec=quiz_data["durationSec"],
            )
            db.add(quiz)
            db.flush()

            for q_data in quiz_data["questions"]:
                question = Question(
                    questionText=q_data["questionText"],
                    explanation=q_data["explanation"],
                    quizID=quiz.contentID,
                )
                db.add(question)
                db.flush()

                for a in q_data["answers"]:
                    db.add(Answer(
                        answerText=a["text"],
                        isCorrect=a["correct"],
                        questionID=question.questionID,
                    ))

            created += 1
            print(f"  Created: {quiz_data['title']}")

        db.commit()
        print(f"\nDone — {created} quizzes added.")

    except Exception as e:
        db.rollback()
        print(f"Seed failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed()
