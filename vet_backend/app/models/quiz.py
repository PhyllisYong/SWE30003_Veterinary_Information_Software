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

    def display(self) -> dict:
        data = self.getMetadata()
        data.update({
            "totalScore": self.totalScore,
            "durationSec": self.durationSec,
            "questionCount": len(self.questions) if self.questions else 0,
            "questions": [
                {
                    "questionID": q.questionID,
                    "questionText": q.questionText,
                    "answers": [
                        {
                            "answerID": a.answerID,
                            "answerText": a.answerText,
                            "isCorrect": a.isCorrect,
                        }
                        for a in q.answers
                    ],
                }
                for q in (self.questions or [])
            ],
        })
        return data

    def getQuestions(self) -> list:
        return self.questions

    def startQuiz(self) -> list:
        return self.getQuestions()

    def evaluateAnswer(self, question, answerID: str | None) -> bool:
        if answerID is None:
            return False
        return question.checkAnswer(answerID)

    def calculateScore(self, submitted_answers: dict[str, str]) -> tuple[int, list[dict]]:
        score = 0
        feedback = []
        for question in self.startQuiz():
            submitted_answer_id = submitted_answers.get(question.questionID)
            correct_answer_id = next(
                (
                    answer.answerID
                    for answer in question.provideAnswerOptions()
                    if answer.isCorrectAnswer()
                ),
                None,
            )
            is_correct = self.evaluateAnswer(question, submitted_answer_id)
            if is_correct:
                score += 1
            feedback.append({
                "questionID": question.questionID,
                "correctAnswerID": correct_answer_id,
                "submittedAnswerID": submitted_answer_id,
                "isCorrect": is_correct,
            })
        return score, feedback

    def evaluatePassingThreshold(self, score: int) -> bool:
        max_score = self.totalScore or len(self.questions or [])
        return max_score > 0 and (score / max_score) >= 0.6

    def recommendFirstAidContent(self, content_items: list) -> list[dict]:
        return [
            item.display()
            for item in content_items
            if item.publicationStatus == "published"
            and item.petType == self.petType
            and item.emergencyCategory == self.emergencyCategory
        ]
