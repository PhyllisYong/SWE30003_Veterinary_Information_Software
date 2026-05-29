from sqlalchemy.orm import Session

from app.models.guide import Guide
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.quiz_result import QuizResult
from app.models.video import Video


def get_all_published(db: Session) -> list[Quiz]:
    return db.query(Quiz).filter(Quiz.publicationStatus == "published").all()


def get_by_id(db: Session, quiz_id: str) -> Quiz | None:
    return db.query(Quiz).filter(Quiz.contentID == quiz_id).first()


def get_results_by_user(db: Session, user_id: str) -> list[QuizResult]:
    return db.query(QuizResult).filter(QuizResult.petOwnerID == user_id).all()


def get_result_by_id(db: Session, result_id: str) -> QuizResult | None:
    return db.query(QuizResult).filter(QuizResult.resultID == result_id).first()


def add_result(db: Session, result: QuizResult) -> QuizResult:
    db.add(result)
    db.commit()
    db.refresh(result)
    return result


def get_question(db: Session, question_id: str, quiz_id: str) -> Question | None:
    return db.query(Question).filter(
        Question.questionID == question_id,
        Question.quizID == quiz_id,
    ).first()


def update_question(db: Session, question: Question) -> Question:
    db.commit()
    db.refresh(question)
    return question


def get_recommended_guides(db: Session, pet_type: str, category: str) -> list[Guide]:
    return db.query(Guide).filter(
        Guide.publicationStatus == "published",
        Guide.petType == pet_type,
        Guide.emergencyCategory == category,
    ).limit(2).all()


def get_recommended_videos(db: Session, pet_type: str, category: str) -> list[Video]:
    return db.query(Video).filter(
        Video.publicationStatus == "published",
        Video.petType == pet_type,
        Video.emergencyCategory == category,
    ).limit(2).all()
