from sqlalchemy.orm import Session, with_polymorphic

from app.models.answer import Answer
from app.models.first_aid_content import FirstAidContent
from app.models.guide import Guide
from app.models.question import Question
from app.models.quiz import Quiz
from app.models.video import Video


def getById(db: Session, contentId: str) -> FirstAidContent | None:
    return db.query(FirstAidContent).filter(
        FirstAidContent.contentID == contentId
    ).first()


def getByAuthor(db: Session, authorId: str) -> list[FirstAidContent]:
    return db.query(FirstAidContent).filter(
        FirstAidContent.authorVeterinarianID == authorId
    ).all()


def getAssignedPending(db: Session, assignedVetId: str) -> list[FirstAidContent]:
    return db.query(FirstAidContent).filter(
        FirstAidContent.assignedVeterinarianID == assignedVetId,
        FirstAidContent.publicationStatus == "pending_verification",
    ).all()


def getAll(db: Session) -> list[FirstAidContent]:
    return db.query(FirstAidContent).all()


def getAllPublishedPolymorphic(db: Session) -> list[FirstAidContent]:
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


def addQuizWithQuestions(
    db: Session,
    quiz: Quiz,
    questionsData: list[dict],
) -> Quiz:
    db.add(quiz)
    db.flush()
    for qData in questionsData:
        question = Question(questionText=qData["questionText"], quizID=quiz.contentID)
        db.add(question)
        db.flush()
        for aData in qData["answers"]:
            db.add(
                Answer(
                    answerText=aData["answerText"],
                    isCorrect=aData["isCorrect"],
                    questionID=question.questionID,
                )
            )
    db.commit()
    db.refresh(quiz)
    return quiz


def replaceQuizQuestions(
    db: Session,
    quiz: Quiz,
    questionsData: list[dict],
) -> Quiz:
    for q in list(quiz.questionList):
        db.delete(q)
    db.flush()
    for qData in questionsData:
        question = Question(questionText=qData["questionText"], quizID=quiz.contentID)
        db.add(question)
        db.flush()
        for aData in qData["answers"]:
            db.add(
                Answer(
                    answerText=aData["answerText"],
                    isCorrect=aData["isCorrect"],
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
