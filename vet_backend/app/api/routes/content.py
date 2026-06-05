from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.routes.auth import requireRole
from app.models.user import User
from app.schemas.content import (
    AssignReviewerRequest,
    ReviewRequest,
    SubmitContentRequest,
    UpdateStatusRequest,
)
from app.services import content_service, user_service

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
    users = user_service.getUsersByRole(db, role)
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
    return {"status": "ok", "data": content_service.getMyContent(db, current_user.userID)}


# ------------------------------------------------------------------
# Vet — assigned reviews
# ------------------------------------------------------------------

@router.get("/content/assigned")
def get_assigned_content(
    current_user: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(get_db),
):
    """Vet only — content assigned to this vet for review."""
    return {
        "status": "ok",
        "data": content_service.getAssignedContent(db, current_user.userID),
    }


# ------------------------------------------------------------------
# Admin — all content
# ------------------------------------------------------------------

@router.get("/content")
def get_all_content(
    current_user: User = Depends(requireRole("association_admin")),
    db: Session = Depends(get_db),
):
    """Admin only — all content."""
    return {"status": "ok", "data": content_service.getAllContent(db)}


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
    try:
        current_user.assignVeterinarianContent(db, content_id, payload.assignedVeterinarianID)
        from app.repositories import content_repository
        content = content_repository.get_by_id(db, content_id)
        return {"status": "ok", "data": content.getMetadata()}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


# ------------------------------------------------------------------
# Vet — submit content
# ------------------------------------------------------------------

@router.post("/content")
def create_content(
    payload: SubmitContentRequest,
    current_user: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(get_db),
):
    """Vet only — submit new guide, video, or quiz."""
    try:
        data = content_service.createContent(db, current_user, payload)
        return {"status": "ok", "data": data}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


@router.put("/content/{content_id}")
def update_content(
    content_id: str,
    payload: SubmitContentRequest,
    current_user: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(get_db),
):
    """Vet only — edit own content."""
    try:
        data = content_service.updateContent(db, content_id, current_user, payload)
        return {"status": "ok", "data": data}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


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
    try:
        current_user.verifyFirstAidContent(db, content_id, payload.status, payload.comment)
        from app.repositories import content_repository
        content = content_repository.get_by_id(db, content_id)
        return {"status": "ok", "data": content.getMetadata()}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


# ------------------------------------------------------------------
# Admin — set draft + assign reviewer (combined, moves to pending_verification)
# ------------------------------------------------------------------

class SetDraftRequest(BaseModel):
    assignedVeterinarianID: str


@router.post("/content/{content_id}/set-draft")
def set_draft_and_assign(
    content_id: str,
    payload: SetDraftRequest,
    current_user: User = Depends(requireRole("association_admin")),
    db: Session = Depends(get_db),
):
    """Admin only — confirm submitted content, assign reviewer, set to pending_verification."""
    try:
        data = content_service.setDraftAndAssign(db, content_id, payload.assignedVeterinarianID)
        return {"status": "ok", "data": data}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


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
    try:
        data = content_service.requestAmend(db, content_id, payload.feedback)
        return {"status": "ok", "data": data}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


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
    try:
        current_user.updateFirstAidStatus(db, content_id, payload.status)
        from app.repositories import content_repository
        content = content_repository.get_by_id(db, content_id)
        return {"status": "ok", "data": content.getMetadata()}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


@router.post("/content/{content_id}/publish")
def publish_content(
    content_id: str,
    current_user: User = Depends(requireRole("association_admin")),
    db: Session = Depends(get_db),
):
    """Admin only — publish content."""
    try:
        current_user.publishFirstAidContent(db, content_id)
        from app.repositories import content_repository
        content = content_repository.get_by_id(db, content_id)
        return {"status": "ok", "data": content.getMetadata()}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


@router.delete("/content/{content_id}")
def delete_content(
    content_id: str,
    current_user: User = Depends(requireRole("association_admin")),
    db: Session = Depends(get_db),
):
    """Admin only — permanently delete content."""
    try:
        current_user.deleteFirstAidContent(db, content_id)
        return {"status": "ok", "message": f"Content '{content_id}' deleted."}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}
