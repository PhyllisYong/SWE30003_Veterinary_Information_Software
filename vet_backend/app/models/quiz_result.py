import uuid
from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class QuizResult(Base):
    __tablename__ = "quiz_results"

    resultID = Column("result_id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    petOwnerID = Column("pet_owner_id", String, ForeignKey("pet_owners.user_id"), nullable=False)
    quizID = Column("quiz_id", String, ForeignKey("quizzes.content_id"), nullable=False)
    score = Column(Integer, nullable=False, default=0)
    attemptedAt = Column("attempted_at", String, nullable=False)   # ISO 8601

    pet_owner = relationship("PetOwner", back_populates="quiz_results")
    quiz = relationship("Quiz", back_populates="results")

    def getScore(self) -> int:
        return self.score

    def getPassed(self) -> bool:
        # Passed if score >= 60% of quiz totalScore
        if self.quiz and self.quiz.totalScore:
            return self.score >= (self.quiz.totalScore * 0.6)
        return False

    def getSummary(self) -> str:
        passed = "Passed" if self.getPassed() else "Failed"
        return f"Score: {self.score} | {passed} | Attempted: {self.attemptedAt}"

    def getID(self) -> str:
        return self.resultID
