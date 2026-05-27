from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.quiz import Quiz
from app.models.quiz_result import QuizResult
from app.models.question import Question

from app.api.routes.auth import getCurrentUser, requireRole
from app.models.user import User

router = APIRouter(
    prefix="/quizzes",
    tags=["Quizzes"]
)

class QuizSubmitRequest(BaseModel):
    answers: dict[str, str]


class ExplanationRequest(BaseModel):
    explanation: str

# helper functions
def getQuiz(
    quiz_id: str,
    db: Session = Depends(get_db),
) -> Quiz:

    quiz = db.query(Quiz).filter(Quiz.contentID == quiz_id).first()

    if quiz is None:
        raise HTTPException(
            status_code=404,
            detail="Quiz not found"
        )

    return quiz

@router.get("")
def list_quizzes(db: Session = Depends(get_db)):
    """Return all published quizzes. No auth required."""
    quizzes = db.query(Quiz).filter(Quiz.publicationStatus == "published").all()
    return [
        {
            "id": q.contentID,
            "title": q.title,
            "description": q.description,
            "petType": q.petType,
            "emergencyCategory": q.emergencyCategory,
            "questionCount": len(q.questions),
            "durationSec": q.durationSec,
        }
        for q in quizzes
    ]


@router.get("/{quiz_id}")
def get_quiz(
    quiz_id: str,
    db: Session = Depends(get_db),
):
    """Return a single quiz with all questions and answers. isCorrect is intentionally omitted."""
    quiz = getQuiz(quiz_id, db)
    return {
        "id": quiz.contentID,
        "title": quiz.title,
        "description": quiz.description,
        "petType": quiz.petType,
        "emergencyCategory": quiz.emergencyCategory,
        "durationSec": quiz.durationSec,
        "totalScore": quiz.totalScore,
        "questions": [
            {
                "id": q.questionID,
                "questionText": q.questionText,
                "answers": [
                    {
                        "id": a.answerID,
                        "answerText": a.answerText,
                        # isCorrect intentionally omitted — checked server-side on submit
                    }
                    for a in q.answers
                ],
            }
            for q in quiz.questions
        ],
    }


@router.post("/{quiz_id}/submit")
def submit_quiz(
    quiz_id: str,
    request: QuizSubmitRequest,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):

    # Find quiz
    quiz = getQuiz(quiz_id, db)

    # Get all questions
    questions = quiz.getQuestions()

    score = 0

    # Loop through questions
    for q in questions:

        # Get submitted answer ID for this question
        submitted_answer_id = request.answers.get(q.questionID)

        # Skip if user did not answer this question
        if submitted_answer_id is None:
            continue

        # Check answer correctness
        if q.checkAnswer(submitted_answer_id):
            score += 1

    # Create quiz result
    result = QuizResult(
        petOwnerID=currentUser.userID,
        quizID=quiz.contentID,
        score=score,
        attemptedAt=datetime.now(timezone.utc).isoformat()
    )

    # Save to database
    db.add(result)
    db.commit()

    # Optional:
    # refresh reloads DB-generated fields into object
    db.refresh(result)

    # Return response
    return {
        "status": "success",
        "quizID": quiz.contentID,
        "score": score,
        "passed": result.getPassed(),
        "resultID": result.resultID,
    }

@router.get("/results/all")
def get_my_results(
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):

    results = db.query(QuizResult).filter(
        QuizResult.petOwnerID == currentUser.userID
    ).all()

    return results

@router.get("/results/{result_id}")
def get_result(
    result_id: str,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):

    result = db.query(QuizResult).filter(
        QuizResult.resultID == result_id
    ).first()

    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Quiz result not found"
        )

    # Security check:
    # prevent users accessing other users' results
    if result.petOwnerID != currentUser.userID:
        raise HTTPException(
            status_code=403,
            detail="Not authorized"
        )

    return result


# Scenario 5 — Vet provides quiz explanation
@router.put("/{quiz_id}/questions/{question_id}/explanation")
def set_explanation(
    quiz_id: str,
    question_id: str,
    body: ExplanationRequest,
    current_user: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(get_db),
):
    quiz = getQuiz(quiz_id, db)

    question = db.query(Question).filter(
        Question.questionID == question_id,
        Question.quizID == quiz.contentID,
    ).first()

    if question is None:
        raise HTTPException(status_code=404, detail="Question not found in this quiz")

    question.setExplanation(body.explanation)
    db.commit()
    db.refresh(question)

    return {
        "status": "ok",
        "data": {
            "questionID": question.questionID,
            "explanation": question.getExplanation(),
        },
    }