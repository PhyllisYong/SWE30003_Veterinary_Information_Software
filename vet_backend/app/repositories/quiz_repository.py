from sqlalchemy.orm import Session

from app.models.guide import Guide
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.quiz_result import QuizResult
from app.models.video import Video


def getAllPublished(db: Session) -> list[Quiz]:
    return db.query(Quiz).filter(Quiz.publicationStatus == "published").all()


def getById(db: Session, quizId: str) -> Quiz | None:
    return db.query(Quiz).filter(Quiz.contentID == quizId).first()


def getResultsByUser(db: Session, userId: str) -> list[QuizResult]:
    return db.query(QuizResult).filter(QuizResult.petOwnerID == userId).all()


def getResultById(db: Session, resultId: str) -> QuizResult | None:
    return db.query(QuizResult).filter(QuizResult.resultID == resultId).first()


def addResult(db: Session, result: QuizResult) -> QuizResult:
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def getQuestion(db: Session, questionId: str, quizId: str) -> Question | None:
    return db.query(Question).filter(
        Question.questionID == questionId,
        Question.quizID == quizId,
    ).first()


def updateQuestion(db: Session, question: Question) -> Question:
    db.commit()
    db.refresh(question)
    return question


def getRecommendedGuides(db: Session, petType: str, category: str) -> list[Guide]:
    return db.query(Guide).filter(
        Guide.publicationStatus == "published",
        Guide.petType == petType,
        Guide.emergencyCategory == category,
    ).limit(2).all()


def getRecommendedVideos(db: Session, petType: str, category: str) -> list[Video]:
    return db.query(Video).filter(
        Video.publicationStatus == "published",
        Video.petType == petType,
        Video.emergencyCategory == category,
    ).limit(2).all()
