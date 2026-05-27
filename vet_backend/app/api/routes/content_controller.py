from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.first_aid_content import FirstAidContent
from app.models.guide import Guide
from app.models.video import Video
from app.services.search_engine import SearchEngine

router = APIRouter(prefix="/api", tags=["content"])


# ------------------------------------------------------------------
# Request / Response schemas (Pydantic)
# ------------------------------------------------------------------

class SubmitContentRequest(BaseModel):
    """Payload for a vet submitting new content."""
    content_type: str          # "guide" | "video"
    title: str
    description: Optional[str] = None
    petType: str
    emergencyCategory: str
    authorVetID: str
    # Guide-specific (optional)
    steps: Optional[list] = None
    # Video-specific (optional)
    videoURL: Optional[str] = None
    durationSec: Optional[int] = None


class UpdateStatusRequest(BaseModel):
    status: str  # "draft" | "pending_verification" | "verified" | "published" | "rejected"


# ------------------------------------------------------------------
# Dependency: SearchEngine per request
# (In production you would inject a singleton; this is sufficient for A3)
# ------------------------------------------------------------------

def get_search_engine(db: Session = Depends(get_db)) -> SearchEngine:
    return SearchEngine(db)


# ------------------------------------------------------------------
# Routes
# ------------------------------------------------------------------

@router.get("/search")
def search_content(
    petType: Optional[str] = Query(None, description="Pet type, e.g. 'cat', 'dog'"),
    category: Optional[str] = Query(None, description="Emergency category, e.g. 'bleeding'"),
    engine: SearchEngine = Depends(get_search_engine),
):
    """
    Search published first-aid content by petType and/or emergencyCategory.
    Returns a list of matching content items (guides and videos).

    Layer rule: ContentController → SearchEngine → FirstAidContent (no direct DB call here).
    """
    results = engine.searchContent(petType=petType, category=category)
    return {
        "status": "ok",
        "data": [item.display() for item in results],
    }


@router.get("/guide/{content_id}")
def get_guide(
    content_id: str,
    engine: SearchEngine = Depends(get_search_engine),
    db: Session = Depends(get_db),
):
    """
    Retrieve a single published Guide by its content ID.
    Returns guide metadata plus its step list.
    """
    item = engine.getContentByID(content_id)

    # If not in published cache, check DB directly (e.g. admin preview)
    if item is None:
        item = db.query(Guide).filter(Guide.contentID == content_id).first()

    if item is None or not isinstance(item, Guide):
        return {"status": "error", "message": f"Guide '{content_id}' not found."}

    return {"status": "ok", "data": item.display()}


@router.get("/video/{content_id}")
def get_video(
    content_id: str,
    engine: SearchEngine = Depends(get_search_engine),
    db: Session = Depends(get_db),
):
    """
    Retrieve a single published Video by its content ID.
    Returns video metadata including the stored URL.

    Note on VideoHosting façade: if your team's VideoHosting façade needs to
    resolve a streaming URL server-side, call it here before returning:
        from app.services.video_hosting import VideoHosting
        stream_url = VideoHosting.getStreamURL(item.videoURL)
        data["streamURL"] = stream_url
    """
    item = engine.getContentByID(content_id)

    if item is None:
        item = db.query(Video).filter(Video.contentID == content_id).first()

    if item is None or not isinstance(item, Video):
        return {"status": "error", "message": f"Video '{content_id}' not found."}

    return {"status": "ok", "data": item.display()}


@router.post("/submit")
def submit_content(
    payload: SubmitContentRequest,
    db: Session = Depends(get_db),
):
    """
    A Veterinarian submits new first-aid content (guide or video).
    Content is created with status 'pending_verification'.

    Layer rule: controller creates the domain object and persists via db session.
    All SQL stays inside the ORM / DatabaseManager layer.
    """
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
            return {
                "status": "error",
                "message": f"Unknown content_type '{payload.content_type}'. Use 'guide' or 'video'.",
            }

        db.add(content)
        db.commit()
        db.refresh(content)

        return {"status": "ok", "data": content.display()}

    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}


@router.patch("/content/{content_id}/status")
def update_content_status(
    content_id: str,
    payload: UpdateStatusRequest,
    db: Session = Depends(get_db),
):
    """
    An AssociationAdministrator updates the publication status of a content item.
    Valid transitions: draft → pending_verification → verified → published | rejected

    Layer rule: controller calls domain method updateStatus(), which validates the
    value. Controller then persists via db session.
    """
    content = (
        db.query(FirstAidContent)
        .filter(FirstAidContent.contentID == content_id)
        .first()
    )

    if content is None:
        return {"status": "error", "message": f"Content '{content_id}' not found."}

    try:
        content.updateStatus(payload.status)   # domain method validates the value
        db.commit()
        db.refresh(content)
        return {"status": "ok", "data": content.getMetadata()}
    except ValueError as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
    except Exception as e:
        db.rollback()
        return {"status": "error", "message": str(e)}
