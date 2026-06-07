import random

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import getDb
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
def listQuizzes(db: Session = Depends(getDb)):
    """Return all published quizzes. No auth required."""
    return quiz_service.listQuizzes(db)


@router.get("/{quizId}")
def getQuiz(quizId: str, db: Session = Depends(getDb)):
    """Return a single quiz with randomised question order."""
    quiz = quiz_service.getQuiz(db, quizId)
    questions = list(quiz.questionList)
    random.shuffle(questions)
    return {
        "id": quiz.contentID,
        "title": quiz.title,
        "description": quiz.description,
        "petType": quiz.petType,
        "emergencyCategory": quiz.emergencyCategory,
        "duration": quiz.duration,
        "totalScore": quiz.totalScore,
        "questions": [
            {
                "id": q.questionID,
                "questionText": q.questionText,
                "explanation": q.explanation,
                "answers": [
                    {"id": a.answerID, "answerText": a.answerText}
                    for a in random.sample(q.answerList, len(q.answerList))
                ],
            }
            for q in questions
        ],
    }


@router.post("/{quizId}/check")
def checkAnswer(quizId: str, request: CheckAnswerRequest, db: Session = Depends(getDb)):
    """Check a single answer without persisting a result."""
    return quiz_service.checkAnswer(db, quizId, request.questionID, request.answerID)


@router.post("/{quizId}/submit")
def submitQuiz(
    quizId: str,
    request: SubmitAnswerRequest,
    currentUser: User = Depends(requireRole("pet_owner")),
    db: Session = Depends(getDb),
):
    return quiz_service.submitQuiz(db, quizId, currentUser, request.answers)


@router.get("/results/all")
def getMyResults(
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    return quiz_service.getMyResults(db, currentUser)


@router.get("/results/{resultId}")
def getResult(
    resultId: str,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    return quiz_service.getResult(db, resultId, currentUser)


@router.put("/{quizId}/questions/{questionId}/explanation")
def setExplanation(
    quizId: str,
    questionId: str,
    body: ExplanationRequest,
    currentUser: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(getDb),
):
    data = quiz_service.setExplanation(db, quizId, questionId, body.explanation)
    return {"status": "ok", "data": data}


@router.put("/{quizId}/questions/{questionId}/text")
def updateQuestionText(
    quizId: str,
    questionId: str,
    body: QuestionTextRequest,
    currentUser: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(getDb),
):
    data = quiz_service.updateQuestionText(db, quizId, questionId, body.questionText)
    return {"status": "ok", "data": data}


@router.put("/{quizId}/questions/{questionId}/answers/{answerId}/text")
def updateAnswerText(
    quizId: str,
    questionId: str,
    answerId: str,
    body: AnswerTextRequest,
    currentUser: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(getDb),
):
    data = quiz_service.updateAnswerText(
        db, quizId, questionId, answerId, body.answerText
    )
    return {"status": "ok", "data": data}
