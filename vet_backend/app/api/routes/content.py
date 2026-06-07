from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import getDb
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
def listUsersByRole(
    role: str = "veterinarian",
    currentUser: User = Depends(requireRole("association_admin")),
    db: Session = Depends(getDb),
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
def getMyContent(
    currentUser: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(getDb),
):
    """Vet only — all content authored by this vet."""
    return {"status": "ok", "data": content_service.getMyContent(db, currentUser.userID)}


# ------------------------------------------------------------------
# Vet — assigned reviews
# ------------------------------------------------------------------

@router.get("/content/assigned")
def getAssignedContent(
    currentUser: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(getDb),
):
    """Vet only — content assigned to this vet for review."""
    return {
        "status": "ok",
        "data": content_service.getAssignedContent(db, currentUser.userID),
    }


# ------------------------------------------------------------------
# Admin — all content
# ------------------------------------------------------------------

@router.get("/content")
def getAllContent(
    currentUser: User = Depends(requireRole("association_admin")),
    db: Session = Depends(getDb),
):
    """Admin only — all content."""
    return {"status": "ok", "data": content_service.getAllContent(db)}


# ------------------------------------------------------------------
# Admin — assign reviewer
# ------------------------------------------------------------------

@router.post("/content/{contentId}/assign")
def assignReviewer(
    contentId: str,
    payload: AssignReviewerRequest,
    currentUser: User = Depends(requireRole("association_admin")),
    db: Session = Depends(getDb),
):
    """Admin only — assign a vet as reviewer for a content item."""
    try:
        data = content_service.assignReviewer(db, contentId, payload)
        return {"status": "ok", "data": data}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


# ------------------------------------------------------------------
# Vet — submit content
# ------------------------------------------------------------------

@router.post("/content")
def createContent(
    payload: SubmitContentRequest,
    currentUser: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(getDb),
):
    """Vet only — submit new guide, video, or quiz."""
    try:
        data = content_service.createContent(db, currentUser, payload)
        return {"status": "ok", "data": data}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


@router.put("/content/{contentId}")
def updateContent(
    contentId: str,
    payload: SubmitContentRequest,
    currentUser: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(getDb),
):
    """Vet only — edit own content."""
    try:
        data = content_service.updateContent(db, contentId, currentUser, payload)
        return {"status": "ok", "data": data}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


# ------------------------------------------------------------------
# Vet — review assigned content
# ------------------------------------------------------------------

@router.post("/content/{contentId}/review")
def reviewContent(
    contentId: str,
    payload: ReviewRequest,
    currentUser: User = Depends(requireRole("veterinarian")),
    db: Session = Depends(getDb),
):
    """Vet only — verify or reject content assigned to them."""
    try:
        data = content_service.reviewContent(db, contentId, currentUser, payload)
        return {"status": "ok", "data": data}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


# ------------------------------------------------------------------
# Admin — set draft + assign reviewer (combined, moves to pending_verification)
# ------------------------------------------------------------------

class SetDraftRequest(BaseModel):
    assignedVeterinarianID: str


@router.post("/content/{contentId}/set-draft")
def setDraftAndAssign(
    contentId: str,
    payload: SetDraftRequest,
    currentUser: User = Depends(requireRole("association_admin")),
    db: Session = Depends(getDb),
):
    """Admin only — confirm submitted content, assign reviewer, set to pending_verification."""
    try:
        data = content_service.setDraftAndAssign(db, contentId, payload.assignedVeterinarianID)
        return {"status": "ok", "data": data}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


# ------------------------------------------------------------------
# Admin — request amend (reject + store feedback for vet)
# ------------------------------------------------------------------

class AmendRequest(BaseModel):
    feedback: str


@router.post("/content/{contentId}/request-amend")
def requestAmend(
    contentId: str,
    payload: AmendRequest,
    currentUser: User = Depends(requireRole("association_admin")),
    db: Session = Depends(getDb),
):
    """Admin only — reject content and send feedback to vet to amend."""
    try:
        data = content_service.requestAmend(db, contentId, payload.feedback)
        return {"status": "ok", "data": data}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


# ------------------------------------------------------------------
# Admin — status management
# ------------------------------------------------------------------

@router.put("/content/{contentId}/status")
def updateStatus(
    contentId: str,
    payload: UpdateStatusRequest,
    currentUser: User = Depends(requireRole("association_admin")),
    db: Session = Depends(getDb),
):
    """Admin only — set any valid publication status."""
    try:
        data = content_service.setStatus(db, contentId, payload.status)
        return {"status": "ok", "data": data}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


@router.post("/content/{contentId}/publish")
def publishContent(
    contentId: str,
    currentUser: User = Depends(requireRole("association_admin")),
    db: Session = Depends(getDb),
):
    """Admin only — publish content."""
    try:
        data = content_service.setStatus(db, contentId, "published")
        return {"status": "ok", "data": data}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}


@router.delete("/content/{contentId}")
def deleteContent(
    contentId: str,
    currentUser: User = Depends(requireRole("association_admin")),
    db: Session = Depends(getDb),
):
    """Admin only — permanently delete content."""
    try:
        content_service.deleteContent(db, contentId)
        return {"status": "ok", "message": f"Content '{contentId}' deleted."}
    except HTTPException as e:
        return {"status": "error", "message": e.detail}
