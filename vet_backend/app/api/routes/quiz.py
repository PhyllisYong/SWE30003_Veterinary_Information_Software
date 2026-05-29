import random

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.routes.auth import getCurrentUser, requireRole
from app.models.user import User
from app.schemas.quiz import SubmitAnswerRequest, CheckAnswerRequest, ExplanationRequest
from app.services import quiz_service

router = APIRouter(prefix="/quizzes", tags=["Quizzes"])


class QuestionTextRequest(BaseModel):
    questionText: str


class AnswerTextRequest(BaseModel):
    answerText: str


@router.get("")
def list_quizzes(db: Session = Depends(get_db)):
    """Return all published quizzes. No auth required."""
    return quiz_service.list_quizzes(db)


@router.get("/{quiz_id}")
def get_quiz(quiz_id: str, db: Session = Depends(get_db)):
    """Return a single quiz with randomised question order."""
    quiz = quiz_service.get_quiz(db, quiz_id)
    questions = list(quiz.questions)
    random.shuffle(questions)
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
                "explanation": q.explanation,
                "answers": [
                    {"id": a.answerID, "answerText": a.answerText}
                    for a in random.sample(q.answers, len(q.answers))
                ],
            }
            for q in questions
        ],
    }


@router.post("/{quiz_id}/check")
def check_answer(quiz_id: str, request: CheckAnswerRequest, db: Session = Depends(get_db)):
    """Check a single answer without persisting a result."""
    return quiz_service.check_answer(db, quiz_id, request.questionID, request.answerID)


@router.post("/{quiz_id}/submit")
def submit_quiz(
    quiz_id: str,
    request: SubmitAnswerRequest,
    currentUser: User = Depends(requireRole("pet_owner")),
    db: Session = Depends(get_db),
):
    return quiz_service.submit_quiz(db, quiz_id, currentUser, request.answers)


@router.get("/results/all")
def get_my_results(
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    return quiz_service.get_my_results(db, currentUser)


@router.get("/results/{result_id}")
def get_result(
    result_id: str,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    return quiz_service.get_result(db, result_id, currentUser)


@router.put("/{quiz_id}/questions/{question_id}/explanation")
def set_explanation(
    quiz_id: str,
    question_id: str,
    body: ExplanationRequest,
    current_user: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(get_db),
):
    data = quiz_service.set_explanation(db, quiz_id, question_id, body.explanation)
    return {"status": "ok", "data": data}


@router.put("/{quiz_id}/questions/{question_id}/text")
def update_question_text(
    quiz_id: str,
    question_id: str,
    body: QuestionTextRequest,
    current_user: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(get_db),
):
    data = quiz_service.update_question_text(db, quiz_id, question_id, body.questionText)
    return {"status": "ok", "data": data}


@router.put("/{quiz_id}/questions/{question_id}/answers/{answer_id}/text")
def update_answer_text(
    quiz_id: str,
    question_id: str,
    answer_id: str,
    body: AnswerTextRequest,
    current_user: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(get_db),
):
    data = quiz_service.update_answer_text(
        db, quiz_id, question_id, answer_id, body.answerText
    )
    return {"status": "ok", "data": data}
