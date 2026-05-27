import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Answer(Base):
    __tablename__ = "answers"

    answerID = Column("answer_id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    answerText = Column("answer_text", String, nullable=False)
    isCorrect = Column("is_correct", Boolean, nullable=False, default=False)
    questionID = Column("question_id", String, ForeignKey("questions.question_id"), nullable=False)

    question = relationship("Question", back_populates="answers")

    def getAnswerText(self) -> str:
        return self.answerText

    def getID(self) -> str:
        return self.answerID

    def setText(self, txt: str) -> None:
        self.answerText = txt
