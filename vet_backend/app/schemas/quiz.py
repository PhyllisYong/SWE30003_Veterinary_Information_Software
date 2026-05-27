from pydantic import BaseModel
from typing import Optional


class AnswerResponse(BaseModel):
    id: str
    answerText: str

    model_config = {"from_attributes": True}


class QuestionResponse(BaseModel):
    id: str
    questionText: str
    explanation: Optional[str]
    answers: list[AnswerResponse]

    model_config = {"from_attributes": True}


class QuizResponse(BaseModel):
    id: str
    title: str
    description: Optional[str]
    petType: str
    emergencyCategory: str
    durationSec: Optional[int]
    totalScore: Optional[int]
    questions: list[QuestionResponse]

    model_config = {"from_attributes": True}


class QuizListItem(BaseModel):
    id: str
    title: str
    description: Optional[str]
    petType: str
    emergencyCategory: str
    questionCount: int
    durationSec: Optional[int]


class SubmitAnswerRequest(BaseModel):
    answers: dict[str, str]   # questionID → answerID


class QuizResultResponse(BaseModel):
    resultID: str
    petOwnerID: str
    quizID: str
    score: int
    attemptedAt: str
    passed: bool

    model_config = {"from_attributes": True}


class ExplanationRequest(BaseModel):
    explanation: str


class ExplanationResponse(BaseModel):
    questionID: str
    explanation: Optional[str]
