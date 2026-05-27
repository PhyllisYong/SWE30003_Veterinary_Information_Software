from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.first_aid_content import FirstAidContent
from app.models.guide import Guide
from app.models.video import Video

router = APIRouter(tags=["content"])


# ------------------------------------------------------------------
# Schemas
# ------------------------------------------------------------------

class SubmitContentRequest(BaseModel):
    content_type: str           # "guide" | "video"
    title: str
    description: Optional[str] = None
    petType: str
    emergencyCategory: str
    authorVetID: str
    steps: Optional[list] = None        # guide only
    videoURL: Optional[str] = None      # video only
    durationSec: Optional[int] = None   # video only


class UpdateStatusRequest(BaseModel):
    status: str  # "draft" | "pending_verification" | "verified" | "published" | "rejected"


# ------------------------------------------------------------------
# Scenario 3 — Vet submits + Admin manages content
# ------------------------------------------------------------------

@router.post("/content")
def create_content(payload: SubmitContentRequest, db: Session = Depends(get_db)):
    """Vet only — submit new guide or video."""
    try:
        if payload.content_type == "guide":
            content = Guide(
                title=payload.title,
                description=payload.description,
                petType=payload.petType,
                emergencyCategory=payload.emergencyCategory,
                authorVetID=payload.authorVetID,
                publicationStatus="pending_verification",
                steps=payload.steps or [],
                stepCount=len(payload.steps or []),
            )
        elif payload.content_type == "video":
            content = Video(
                title=payload.title,
                description=payload.description,
                petType=payload.petType,
                emergencyCategory=payload.emergencyCategory,
                authorVetID=payload.authorVetID,
                publicationStatus="pending_verification",
                videoURL=payload.videoURL,
                durationSec=payload.durationSec,
            )
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
    db: Session = Depends(get_db),
):
    """Vet only — edit existing content."""
    content = db.query(FirstAidContent).filter(FirstAidContent.contentID == content_id).first()
    if content is None:
        return {"status": "error", "message": f"Content '{content_id}' not found."}
    try:
        content.title = payload.title
        content.description = payload.description
        content.petType = payload.petType
        content.emergencyCategory = payload.emergencyCategory
        if isinstance(content, Guide) and payload.steps is not None:
            content.steps = payload.steps
            content.stepCount = len(payload.steps)
        if isinstance(content, Video):
            content.videoURL = payload.videoURL
            content.durationSec = payload.durationSec
        db.commit()
        db.refresh(content)
        return {"status": "ok", "data": content.display()}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


@router.post("/content/{content_id}/verify")
def verify_content(content_id: str, db: Session = Depends(get_db)):
    """Vet only — mark content as verified."""
    return _set_status(content_id, "verified", db)


@router.post("/content/{content_id}/reject")
def reject_content(content_id: str, db: Session = Depends(get_db)):
    """Vet only — reject content."""
    return _set_status(content_id, "rejected", db)


@router.put("/content/{content_id}/status")
def update_status(
    content_id: str,
    payload: UpdateStatusRequest,
    db: Session = Depends(get_db),
):
    """Admin only — set any valid publication status."""
    return _set_status(content_id, payload.status, db)


@router.post("/content/{content_id}/publish")
def publish_content(content_id: str, db: Session = Depends(get_db)):
    """Admin only — publish content."""
    return _set_status(content_id, "published", db)


@router.delete("/content/{content_id}")
def delete_content(content_id: str, db: Session = Depends(get_db)):
    """Admin only — permanently delete content."""
    content = db.query(FirstAidContent).filter(FirstAidContent.contentID == content_id).first()
    if content is None:
        return {"status": "error", "message": f"Content '{content_id}' not found."}
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
    if content is None:
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
