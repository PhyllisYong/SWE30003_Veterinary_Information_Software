import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Question(Base):
    __tablename__ = "questions"

    questionID = Column("question_id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    questionText = Column("question_text", String, nullable=False)
    explanation = Column(String, nullable=True)
    quizID = Column("quiz_id", String, ForeignKey("quizzes.content_id"), nullable=False)

    # Composition: answers cannot exist without question
    answers = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="select",
    )
    quiz = relationship("Quiz", back_populates="questions")

    def getAnswers(self) -> list:
        return self.answers

    def provideAnswerOptions(self) -> list:
        return self.getAnswers()

    def checkAnswer(self, answerID: str) -> bool:
        for answer in self.answers:
            if answer.answerID == answerID:
                return answer.isCorrectAnswer()
        return False

    def getText(self) -> str:
        return self.questionText

    def setExplanation(self, txt: str) -> None:
        self.explanation = txt

    def updateQuestionText(self, txt: str) -> None:
        self.questionText = txt

    def updateAnswerText(self, answerID: str, txt: str) -> None:
        for answer in self.answers:
            if answer.answerID == answerID:
                answer.setText(txt)
                return
        raise ValueError("Answer not found in this question")

    def getExplanation(self) -> str:
        return self.explanation

    def getID(self) -> str:
        return self.questionID
