from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.quiz import Quiz
from app.models.quiz_result import QuizResult
from app.models.user import User
from app.repositories import quiz_repository


def listQuizzes(db: Session) -> list[dict]:
    quizzes = quiz_repository.getAllPublished(db)
    return [
        {
            "id": q.contentID,
            "title": q.title,
            "description": q.description,
            "petType": q.petType,
            "emergencyCategory": q.emergencyCategory,
            "questionCount": len(q.questionList),
            "duration": q.duration,
        }
        for q in quizzes
    ]


def getQuiz(db: Session, quizId: str) -> Quiz:
    quiz = quiz_repository.getById(db, quizId)
    if quiz is None:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz


def checkAnswer(db: Session, quizId: str, questionId: str, answerId: str) -> dict:
    quiz = getQuiz(db, quizId)
    question = next((q for q in quiz.questionList if q.questionID == questionId), None)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found in this quiz")
    isCorrect = question.checkAnswer(answerId)
    correctAnswerId = next((a.answerID for a in question.answerList if a.isCorrect), None)
    return {"isCorrect": isCorrect, "correctAnswerID": correctAnswerId}


def submitQuiz(
    db: Session, quizId: str, currentUser: User, answers: dict[str, str]
) -> dict:
    quiz = getQuiz(db, quizId)
    score, feedback = quiz.calculateScore(answers)

    result = QuizResult(
        petOwnerID=currentUser.userID,
        quizID=quiz.contentID,
        totalScore=score,
        attemptedAt=datetime.now(timezone.utc).isoformat(),
    )
    result = quiz_repository.addResult(db, result)
    passed = quiz.evaluatePassingThreshold(score)

    recommended = []
    if not passed:
        guides = quiz_repository.getRecommendedGuides(
            db, quiz.petType, quiz.emergencyCategory
        )
        videos = quiz_repository.getRecommendedVideos(
            db, quiz.petType, quiz.emergencyCategory
        )
        recommended = quiz.recommendFirstAidContent([*guides, *videos])

    return {
        "status": "success",
        "quizID": quiz.contentID,
        "totalScore": score,
        "passed": passed,
        "resultID": result.resultID,
        "feedback": feedback,
        "recommendedContent": recommended,
    }


def getMyResults(db: Session, currentUser: User) -> list[QuizResult]:
    return quiz_repository.getResultsByUser(db, currentUser.userID)


def getResult(db: Session, resultId: str, currentUser: User) -> QuizResult:
    result = quiz_repository.getResultById(db, resultId)
    if result is None:
        raise HTTPException(status_code=404, detail="Quiz result not found")
    if result.petOwnerID != currentUser.userID:
        raise HTTPException(status_code=403, detail="Not authorized")
    return result


def setExplanation(
    db: Session, quizId: str, questionId: str, explanation: str
) -> dict:
    quiz = getQuiz(db, quizId)
    question = quiz_repository.getQuestion(db, questionId, quiz.contentID)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found in this quiz")
    question.setExplanation(explanation)
    question = quiz_repository.updateQuestion(db, question)
    return {"questionID": question.questionID, "explanation": question.getExplanation()}


def updateQuestionText(
    db: Session, quizId: str, questionId: str, questionText: str
) -> dict:
    quiz = getQuiz(db, quizId)
    question = quiz_repository.getQuestion(db, questionId, quiz.contentID)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found in this quiz")
    if not questionText.strip():
        raise HTTPException(status_code=422, detail="Question text cannot be empty")
    question.updateQuestionText(questionText.strip())
    question = quiz_repository.updateQuestion(db, question)
    return {"questionID": question.questionID, "questionText": question.questionText}


def updateAnswerText(
    db: Session, quizId: str, questionId: str, answerId: str, answerText: str
) -> dict:
    quiz = getQuiz(db, quizId)
    question = quiz_repository.getQuestion(db, questionId, quiz.contentID)
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found in this quiz")
    if not answerText.strip():
        raise HTTPException(status_code=422, detail="Answer text cannot be empty")
    try:
        question.updateAnswerText(answerId, answerText.strip())
    except ValueError:
        raise HTTPException(status_code=404, detail="Answer not found in this question")
    quiz_repository.updateQuestion(db, question)
    return {"answerID": answerId, "answerText": answerText.strip()}
