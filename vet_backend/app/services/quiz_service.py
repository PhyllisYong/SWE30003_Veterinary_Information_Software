from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.quiz import Quiz
from app.models.quiz_result import QuizResult
from app.models.user import User
from app.repositories import quiz_repository


def list_quizzes(db: Session) -> list[dict]:
    quizzes = quiz_repository.get_all_published(db)
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


def get_quiz(db: Session, quiz_id: str) -> Quiz:
    quiz = quiz_repository.get_by_id(db, quiz_id)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


def check_answer(db: Session, quiz_id: str, question_id: str, answer_id: str) -> dict:
    quiz = get_quiz(db, quiz_id)
    question = next((q for q in quiz.questions if q.questionID == question_id), None)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found in this quiz")
    is_correct = question.checkAnswer(answer_id)
    correct_answer_id = next((a.answerID for a in question.answers if a.isCorrect), None)
    return {"isCorrect": is_correct, "correctAnswerID": correct_answer_id}


def submit_quiz(
    db: Session, quiz_id: str, current_user: User, answers: dict[str, str]
) -> dict:
    quiz = get_quiz(db, quiz_id)
    score, feedback = quiz.calculateScore(answers)

    result = QuizResult(
        petOwnerID=current_user.userID,
        quizID=quiz.contentID,
        score=score,
        attemptedAt=datetime.now(timezone.utc).isoformat(),
    )
    result = quiz_repository.add_result(db, result)
    passed = quiz.evaluatePassingThreshold(score)

    recommended = []
    if not passed:
        guides = quiz_repository.get_recommended_guides(
            db, quiz.petType, quiz.emergencyCategory
        )
        videos = quiz_repository.get_recommended_videos(
            db, quiz.petType, quiz.emergencyCategory
        )
        recommended = quiz.recommendFirstAidContent([*guides, *videos])

    return {
        "status": "success",
        "quizID": quiz.contentID,
        "score": score,
        "passed": passed,
        "resultID": result.resultID,
        "feedback": feedback,
        "recommendedContent": recommended,
    }


def get_my_results(db: Session, current_user: User) -> list[QuizResult]:
    return quiz_repository.get_results_by_user(db, current_user.userID)


def get_result(db: Session, result_id: str, current_user: User) -> QuizResult:
    result = quiz_repository.get_result_by_id(db, result_id)
    if result is None:
        raise HTTPException(status_code=404, detail="Quiz result not found")
    if result.petOwnerID != current_user.userID:
        raise HTTPException(status_code=403, detail="Not authorized")
    return result


def set_explanation(
    db: Session, quiz_id: str, question_id: str, explanation: str
) -> dict:
    quiz = get_quiz(db, quiz_id)
    question = quiz_repository.get_question(db, question_id, quiz.contentID)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found in this quiz")
    question.setExplanation(explanation)
    question = quiz_repository.update_question(db, question)
    return {"questionID": question.questionID, "explanation": question.getExplanation()}


def update_question_text(
    db: Session, quiz_id: str, question_id: str, question_text: str
) -> dict:
    quiz = get_quiz(db, quiz_id)
    question = quiz_repository.get_question(db, question_id, quiz.contentID)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found in this quiz")
    if not question_text.strip():
        raise HTTPException(status_code=422, detail="Question text cannot be empty")
    question.updateQuestionText(question_text.strip())
    question = quiz_repository.update_question(db, question)
    return {"questionID": question.questionID, "questionText": question.questionText}


def update_answer_text(
    db: Session, quiz_id: str, question_id: str, answer_id: str, answer_text: str
) -> dict:
    quiz = get_quiz(db, quiz_id)
    question = quiz_repository.get_question(db, question_id, quiz.contentID)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found in this quiz")
    if not answer_text.strip():
        raise HTTPException(status_code=422, detail="Answer text cannot be empty")
    try:
        question.updateAnswerText(answer_id, answer_text.strip())
    except ValueError:
        raise HTTPException(status_code=404, detail="Answer not found in this question")
    quiz_repository.update_question(db, question)
    return {"answerID": answer_id, "answerText": answer_text.strip()}
