from sqlalchemy.orm import Session, with_polymorphic

from app.models.answer import Answer
from app.models.first_aid_content import FirstAidContent
from app.models.guide import Guide
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.video import Video


def get_by_id(db: Session, content_id: str) -> FirstAidContent | None:
    return db.query(FirstAidContent).filter(
        FirstAidContent.contentID == content_id
    ).first()


def get_by_author(db: Session, author_id: str) -> list[FirstAidContent]:
    return db.query(FirstAidContent).filter(
        FirstAidContent.authorVetID == author_id
    ).all()


def get_assigned_pending(db: Session, assigned_vet_id: str) -> list[FirstAidContent]:
    return db.query(FirstAidContent).filter(
        FirstAidContent.assignedVetID == assigned_vet_id,
        FirstAidContent.publicationStatus == "pending_verification",
    ).all()


def get_all(db: Session) -> list[FirstAidContent]:
    return db.query(FirstAidContent).all()


def get_all_published_polymorphic(db: Session) -> list[FirstAidContent]:
    polymorphic = with_polymorphic(FirstAidContent, "*")
    return (
        db.query(polymorphic)
        .filter(FirstAidContent.publicationStatus == "published")
        .all()
    )


def add(db: Session, content: FirstAidContent) -> FirstAidContent:
    db.add(content)
    db.commit()
    db.refresh(content)
    return content


def add_quiz_with_questions(
    db: Session,
    quiz: Quiz,
    questions_data: list[dict],
) -> Quiz:
    db.add(quiz)
    db.flush()
    for q_data in questions_data:
        question = Question(questionText=q_data["questionText"], quizID=quiz.contentID)
        db.add(question)
        db.flush()
        for a_data in q_data["answers"]:
            db.add(
                Answer(
                    answerText=a_data["answerText"],
                    isCorrect=a_data["isCorrect"],
                    questionID=question.questionID,
                )
            )
    db.commit()
    db.refresh(quiz)
    return quiz


def replace_quiz_questions(
    db: Session,
    quiz: Quiz,
    questions_data: list[dict],
) -> Quiz:
    for q in list(quiz.questions):
        db.delete(q)
    db.flush()
    for q_data in questions_data:
        question = Question(questionText=q_data["questionText"], quizID=quiz.contentID)
        db.add(question)
        db.flush()
        for a_data in q_data["answers"]:
            db.add(
                Answer(
                    answerText=a_data["answerText"],
                    isCorrect=a_data["isCorrect"],
                    questionID=question.questionID,
                )
            )
    db.commit()
    db.refresh(quiz)
    return quiz


def update(db: Session, content: FirstAidContent) -> FirstAidContent:
    db.commit()
    db.refresh(content)
    return content


def delete(db: Session, content: FirstAidContent) -> None:
    db.delete(content)
    db.commit()


def rollback(db: Session) -> None:
    db.rollback()
