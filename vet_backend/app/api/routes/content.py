from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.routes.auth import requireRole
from app.models.user import User
from app.models.first_aid_content import FirstAidContent
from app.models.guide import Guide
from app.models.video import Video
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.answer import Answer
from app.services.video_hosting import video_hosting

from app.schemas.content import (
    SubmitContentRequest,
    UpdateStatusRequest,
    ReviewRequest,
    AssignReviewerRequest,
    SetDraftRequest,
    AmendRequest,
)

router = APIRouter(tags=["content"])


# ------------------------------------------------------------------
# Admin — list users by role (e.g. ?role=veterinarian)
# ------------------------------------------------------------------

@router.get("/users")
def list_users_by_role(
    role: str = "veterinarian",
    current_user: User = Depends(requireRole("association_admin")),
    db: Session = Depends(get_db),
):
    """Admin only — list users filtered by role."""
    users = db.query(User).filter(User.role == role).all()
    return {
        "status": "ok",
        "data": [{"userID": u.userID, "name": u.name, "email": u.email} for u in users],
    }


# ------------------------------------------------------------------
# Vet — own content
# ------------------------------------------------------------------

@router.get("/content/mine")
def get_my_content(
    current_user: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(get_db),
):
    """Vet only — all content authored by this vet."""
    items = (
        db.query(FirstAidContent)
        .filter(FirstAidContent.authorVetID == current_user.userID)
        .all()
    )
    return {"status": "ok", "data": [item.display() for item in items]}


# ------------------------------------------------------------------
# Vet — assigned reviews
# ------------------------------------------------------------------

@router.get("/content/assigned")
def get_assigned_content(
    current_user: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(get_db),
):
    """Vet only — content assigned to this vet for review."""
    items = (
        db.query(FirstAidContent)
        .filter(
            FirstAidContent.assignedVetID == current_user.userID,
            FirstAidContent.publicationStatus == "pending_verification",
        )
        .all()
    )
    return {"status": "ok", "data": [item.display() for item in items]}


# ------------------------------------------------------------------
# Admin — all content
# ------------------------------------------------------------------

@router.get("/content")
def get_all_content(
    current_user: User = Depends(requireRole("association_admin")),
    db: Session = Depends(get_db),
):
    """Admin only — all content."""
    items = db.query(FirstAidContent).all()
    return {"status": "ok", "data": [item.display() for item in items]}


# ------------------------------------------------------------------
# Admin — assign reviewer
# ------------------------------------------------------------------

@router.post("/content/{content_id}/assign")
def assign_reviewer(
    content_id: str,
    payload: AssignReviewerRequest,
    current_user: User = Depends(requireRole("association_admin")),
    db: Session = Depends(get_db),
):
    """Admin only — assign a vet as reviewer for a content item."""
    content = db.query(FirstAidContent).filter(FirstAidContent.contentID == content_id).first()
    if not content:
        return {"status": "error", "message": "Content not found."}
    if content.authorVetID == payload.assignedVetID:
        return {"status": "error", "message": "Cannot assign the author as the assigned vet."}
    try:
        content.assignedVetID = payload.assignedVetID
        db.commit()
        db.refresh(content)
        return {"status": "ok", "data": content.getMetadata()}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


# ------------------------------------------------------------------
# Vet — submit content
# ------------------------------------------------------------------

@router.post("/content")
def create_content(
    payload: SubmitContentRequest,
    current_user: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(get_db),
):
    """Vet only — submit new guide or video."""
    try:
        if payload.content_type == "guide":
            content = Guide(
                title=payload.title,
                description=payload.description,
                petType=payload.petType,
                emergencyCategory=payload.emergencyCategory,
                authorVetID=current_user.userID,
                publicationStatus="submitted",
                steps=payload.steps or [],
                stepCount=len(payload.steps or []),
            )
        elif payload.content_type == "video":
            if not payload.videoURL or not video_hosting.isValidYouTubeUrl(payload.videoURL):
                return {"status": "error", "message": "videoURL must be a valid YouTube URL."}
            content = Video(
                title=payload.title,
                description=payload.description,
                petType=payload.petType,
                emergencyCategory=payload.emergencyCategory,
                authorVetID=current_user.userID,
                publicationStatus="submitted",
                videoURL=video_hosting.getEmbedUrl(payload.videoURL),
                durationSec=payload.durationSec,
            )
        elif payload.content_type == "quiz":
            if not payload.questions:
                return {"status": "error", "message": "Quiz must have at least one question."}
            content = Quiz(
                title=payload.title,
                description=payload.description,
                petType=payload.petType,
                emergencyCategory=payload.emergencyCategory,
                authorVetID=current_user.userID,
                publicationStatus="submitted",
                durationSec=payload.durationSec,
                totalScore=len(payload.questions),
            )
            db.add(content)
            db.flush()
            for q_data in payload.questions:
                question = Question(questionText=q_data["questionText"], quizID=content.contentID)
                db.add(question)
                db.flush()
                for a_data in q_data["answers"]:
                    db.add(Answer(answerText=a_data["answerText"], isCorrect=a_data["isCorrect"], questionID=question.questionID))
        else:
            return {"status": "error", "message": f"Unknown content_type '{payload.content_type}'."}

        db.add(content)
        db.commit()
        db.refresh(content)
        return {"status": "ok", "data": content.display()}

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


@router.put("/content/{content_id}")
def update_content(
    content_id: str,
    payload: SubmitContentRequest,
    current_user: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(get_db),
):
    """Vet only — edit own content."""
    content = db.query(FirstAidContent).filter(FirstAidContent.contentID == content_id).first()
    if not content:
        return {"status": "error", "message": "Content not found."}
    if content.authorVetID != current_user.userID:
        return {"status": "error", "message": "You can only edit your own content."}
    try:
        content.title = payload.title
        content.description = payload.description
        content.petType = payload.petType
        content.emergencyCategory = payload.emergencyCategory
        if isinstance(content, Guide) and payload.steps is not None:
            content.steps = payload.steps
            content.stepCount = len(payload.steps)
        if isinstance(content, Video):
            if not payload.videoURL or not video_hosting.isValidYouTubeUrl(payload.videoURL):
                return {"status": "error", "message": "videoURL must be a valid YouTube URL."}
            content.videoURL = video_hosting.getEmbedUrl(payload.videoURL)
            content.durationSec = payload.durationSec
        if isinstance(content, Quiz):
            if not payload.questions:
                return {"status": "error", "message": "Quiz must have at least one question."}
            for q in list(content.questions):
                db.delete(q)
            db.flush()
            content.durationSec = payload.durationSec
            content.totalScore = len(payload.questions)
            for q_data in payload.questions:
                question = Question(questionText=q_data["questionText"], quizID=content.contentID)
                db.add(question)
                db.flush()
                for a_data in q_data["answers"]:
                    db.add(Answer(answerText=a_data["answerText"], isCorrect=a_data["isCorrect"], questionID=question.questionID))
        content.publicationStatus = "submitted"   # resets for admin to re-review
        db.commit()
        db.refresh(content)
        return {"status": "ok", "data": content.display()}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


# ------------------------------------------------------------------
# Vet — review assigned content
# ------------------------------------------------------------------

@router.post("/content/{content_id}/review")
def review_content(
    content_id: str,
    payload: ReviewRequest,
    current_user: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(get_db),
):
    """Vet only — verify or reject content assigned to them."""
    content = db.query(FirstAidContent).filter(FirstAidContent.contentID == content_id).first()
    if not content:
        return {"status": "error", "message": "Content not found."}
    if content.assignedVetID != current_user.userID:
        return {"status": "error", "message": "You are not the assigned reviewer for this content."}
    if content.authorVetID == current_user.userID:
        return {"status": "error", "message": "You cannot review your own content."}
    if payload.status not in ("verified", "rejected"):
        return {"status": "error", "message": "Status must be 'verified' or 'rejected'."}
    if payload.status == "rejected" and not (payload.comment or "").strip():
        return {"status": "error", "message": "A comment is required when rejecting content."}
    try:
        content.updateStatus(payload.status)
        content.reviewComment = payload.comment or None
        db.commit()
        db.refresh(content)
        return {"status": "ok", "data": content.getMetadata()}
    except ValueError as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}



# ------------------------------------------------------------------
# Admin — set draft + assign reviewer (combined, moves to pending_verification)
# ------------------------------------------------------------------

class SetDraftRequest(BaseModel):
    assignedVetID: str

@router.post("/content/{content_id}/set-draft")
def set_draft_and_assign(
    content_id: str,
    payload: SetDraftRequest,
    current_user: User = Depends(requireRole("association_admin")),
    db: Session = Depends(get_db),
):
    """Admin only — confirm submitted content, assign reviewer, set to pending_verification."""
    content = db.query(FirstAidContent).filter(FirstAidContent.contentID == content_id).first()
    if not content:
        return {"status": "error", "message": "Content not found."}
    if content.authorVetID == payload.assignedVetID:
        return {"status": "error", "message": "Cannot assign the author as the assigned vet."}
    try:
        content.assignedVetID = payload.assignedVetID
        content.updateStatus("pending_verification")
        db.commit()
        db.refresh(content)
        return {"status": "ok", "data": content.getMetadata()}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


# ------------------------------------------------------------------
# Admin — request amend (reject + store feedback for vet)
# ------------------------------------------------------------------

class AmendRequest(BaseModel):
    feedback: str

@router.post("/content/{content_id}/request-amend")
def request_amend(
    content_id: str,
    payload: AmendRequest,
    current_user: User = Depends(requireRole("association_admin")),
    db: Session = Depends(get_db),
):
    """Admin only — reject content and send feedback to vet to amend."""
    if not payload.feedback.strip():
        return {"status": "error", "message": "Feedback is required."}
    content = db.query(FirstAidContent).filter(FirstAidContent.contentID == content_id).first()
    if not content:
        return {"status": "error", "message": "Content not found."}
    try:
        content.updateStatus("rejected")
        content.reviewComment = payload.feedback
        db.commit()
        db.refresh(content)
        return {"status": "ok", "data": content.getMetadata()}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


# ------------------------------------------------------------------
# Admin — status management
# ------------------------------------------------------------------

@router.put("/content/{content_id}/status")
def update_status(
    content_id: str,
    payload: UpdateStatusRequest,
    current_user: User = Depends(requireRole("association_admin")),
    db: Session = Depends(get_db),
):
    """Admin only — set any valid publication status."""
    return _set_status(content_id, payload.status, db)


@router.post("/content/{content_id}/publish")
def publish_content(
    content_id: str,
    current_user: User = Depends(requireRole("association_admin")),
    db: Session = Depends(get_db),
):
    """Admin only — publish content."""
    return _set_status(content_id, "published", db)


@router.delete("/content/{content_id}")
def delete_content(
    content_id: str,
    current_user: User = Depends(requireRole("association_admin")),
    db: Session = Depends(get_db),
):
    """Admin only — permanently delete content."""
    content = db.query(FirstAidContent).filter(FirstAidContent.contentID == content_id).first()
    if not content:
        return {"status": "error", "message": "Content not found."}
    try:
        db.delete(content)
        db.commit()
        return {"status": "ok", "message": f"Content '{content_id}' deleted."}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


# ------------------------------------------------------------------
# Internal helper
# ------------------------------------------------------------------

def _set_status(content_id: str, status: str, db: Session):
    content = db.query(FirstAidContent).filter(FirstAidContent.contentID == content_id).first()
    if not content:
        return {"status": "error", "message": f"Content '{content_id}' not found."}
    try:
        content.updateStatus(status)
        db.commit()
        db.refresh(content)
        return {"status": "ok", "data": content.getMetadata()}
    except ValueError as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
