import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.quiz import Quiz
from app.models.quiz_result import QuizResult
from app.models.question import Question
from app.models.guide import Guide
from app.models.video import Video

from app.api.routes.auth import getCurrentUser, requireRole
from app.models.user import User
from app.schemas.quiz import SubmitAnswerRequest, CheckAnswerRequest, ExplanationRequest

router = APIRouter(
    prefix="/quizzes",
    tags=["Quizzes"]
)

class QuizSubmitRequest(BaseModel):
    answers: dict[str, str]


class ExplanationRequest(BaseModel):
    explanation: str


class QuestionTextRequest(BaseModel):
    questionText: str


class AnswerTextRequest(BaseModel):
    answerText: str

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


def _recommend_content(quiz: Quiz, db: Session) -> list[dict]:
    guides = db.query(Guide).filter(
        Guide.publicationStatus == "published",
        Guide.petType == quiz.petType,
        Guide.emergencyCategory == quiz.emergencyCategory,
    ).limit(2).all()
    videos = db.query(Video).filter(
        Video.publicationStatus == "published",
        Video.petType == quiz.petType,
        Video.emergencyCategory == quiz.emergencyCategory,
    ).limit(2).all()
    return quiz.recommendFirstAidContent([*guides, *videos])

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
    """Return a single quiz with randomised question order. isCorrect is intentionally omitted."""
    quiz = getQuiz(quiz_id, db)
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
                    {
                        "id": a.answerID,
                        "answerText": a.answerText,
                        # isCorrect intentionally omitted — checked server-side on submit
                    }
                    for a in random.sample(q.answers, len(q.answers))
                ],
            }
            for q in questions
        ],
    }


@router.post("/{quiz_id}/check")
def check_answer(
    quiz_id: str,
    request: CheckAnswerRequest,
    db: Session = Depends(get_db),
):
    """Check a single answer without persisting a result — used for per-question feedback."""
    quiz = getQuiz(quiz_id, db)
    question = next((q for q in quiz.questions if q.questionID == request.questionID), None)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found in this quiz")
    is_correct = question.checkAnswer(request.answerID)
    correct_answer_id = next((a.answerID for a in question.answers if a.isCorrect), None)
    return {"isCorrect": is_correct, "correctAnswerID": correct_answer_id}


@router.post("/{quiz_id}/submit")
def submit_quiz(
    quiz_id: str,
    request: SubmitAnswerRequest,
    currentUser: User = Depends(requireRole("pet_owner")),
    db: Session = Depends(get_db),
):

    # Find quiz
    quiz = getQuiz(quiz_id, db)

    score, feedback = quiz.calculateScore(request.answers)

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
    db.refresh(result)

    passed = quiz.evaluatePassingThreshold(score)

    # Return response
    return {
        "status": "success",
        "quizID": quiz.contentID,
        "score": score,
        "passed": passed,
        "resultID": result.resultID,
        "feedback": feedback,
        "recommendedContent": [] if passed else _recommend_content(quiz, db),
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


@router.put("/{quiz_id}/questions/{question_id}/text")
def update_question_text(
    quiz_id: str,
    question_id: str,
    body: QuestionTextRequest,
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
    if not body.questionText.strip():
        raise HTTPException(status_code=422, detail="Question text cannot be empty")

    question.updateQuestionText(body.questionText.strip())
    db.commit()
    db.refresh(question)

    return {
        "status": "ok",
        "data": {
            "questionID": question.questionID,
            "questionText": question.questionText,
        },
    }


@router.put("/{quiz_id}/questions/{question_id}/answers/{answer_id}/text")
def update_answer_text(
    quiz_id: str,
    question_id: str,
    answer_id: str,
    body: AnswerTextRequest,
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
    if not body.answerText.strip():
        raise HTTPException(status_code=422, detail="Answer text cannot be empty")

    try:
        question.updateAnswerText(answer_id, body.answerText.strip())
    except ValueError:
        raise HTTPException(status_code=404, detail="Answer not found in this question")
    db.commit()
    db.refresh(question)

    return {
        "status": "ok",
        "data": {
            "answerID": answer_id,
            "answerText": body.answerText.strip(),
        },
    }
