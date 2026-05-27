from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.first_aid_content import FirstAidContent


class Quiz(FirstAidContent):
    __tablename__ = "quizzes"

    contentID = Column("content_id", String, ForeignKey("first_aid_contents.content_id"), primary_key=True)
    totalScore = Column("total_score", Integer, nullable=True, default=0)
    durationSec = Column("duration_sec", Integer, nullable=True)

    # Composition: questions cannot exist without quiz
    questions = relationship(
        "Question",
        back_populates="quiz",
        cascade="all, delete-orphan",
        lazy="select",
    )
    results = relationship("QuizResult", back_populates="quiz", lazy="select")

    __mapper_args__ = {
        "polymorphic_identity": "quiz",
    }

    def getQuestions(self) -> list:
        return self.questions
