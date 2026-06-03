from pydantic import BaseModel
from typing import Optional


class SubmitContentRequest(BaseModel):
    content_type: str
    title: str
    description: Optional[str] = None
    petType: str
    emergencyCategory: str
    steps: Optional[list] = None
    videoURL: Optional[str] = None
    duration: Optional[int] = None
    questions: Optional[list] = None  # [{questionText, answers: [{answerText, isCorrect}]}]

class UpdateStatusRequest(BaseModel):
    status: str

class ReviewRequest(BaseModel):
    status: str   # "verified" | "rejected"
    comment: Optional[str] = None

class AssignReviewerRequest(BaseModel):
    assignedVeterinarianID: str

class SetDraftRequest(BaseModel):
    assignedVeterinarianID: str

class AmendRequest(BaseModel):
    feedback: str