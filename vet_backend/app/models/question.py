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
    answerList = relationship(
        "Answer",
        back_populates="question",
        cascade="all, delete-orphan",
        lazy="select",
    )
    quiz = relationship("Quiz", back_populates="questionList")

    def getAnswers(self) -> list:
        return self.answerList

    def provideAnswerOptions(self) -> list:
        return self.getAnswers()

    def checkAnswer(self, answerID: str) -> bool:
        for answer in self.answerList:
            if answer.answerID == answerID:
                return answer.isCorrectAnswer()
        return False

    def getText(self) -> str:
        return self.questionText

    def setExplanation(self, text: str) -> None:
        self.explanation = text

    def updateQuestionText(self, text: str) -> None:
        self.questionText = text

    def updateAnswerText(self, answerID: str, text: str) -> None:
        for answer in self.answerList:
            if answer.answerID == answerID:
                answer.setText(text)
                return
        raise ValueError("Answer not found in this question")

    def getExplanation(self) -> str:
        return self.explanation

    def getID(self) -> str:
        return self.questionID
