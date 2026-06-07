from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.first_aid_content import FirstAidContent
from app.models.guide import Guide
from app.models.quiz import Quiz
from app.models.user import User
from app.models.video import Video
from app.repositories import content_repository
from app.schemas.content import (
    AmendRequest,
    AssignReviewerRequest,
    ReviewRequest,
    SubmitContentRequest,
    UpdateStatusRequest,
)
from app.services.video_hosting import video_hosting


def getMyContent(db: Session, author_id: str) -> list[dict]:
    items = content_repository.get_by_author(db, author_id)
    return [item.display() for item in items]


def getAssignedContent(db: Session, assigned_vet_id: str) -> list[dict]:
    items = content_repository.get_assigned_pending(db, assigned_vet_id)
    return [item.display() for item in items]


def getAllContent(db: Session) -> list[dict]:
    items = content_repository.get_all(db)
    return [item.display() for item in items]


def assignReviewer(
    db: Session, content_id: str, payload: AssignReviewerRequest
) -> dict:
    content = _getOrError(db, content_id)
    if content.authorVeterinarianID == payload.assignedVeterinarianID:
        raise HTTPException(
            status_code=422, detail="Cannot assign the author as the assigned vet."
        )
    content.assignedVeterinarianID = payload.assignedVeterinarianID
    content_repository.update(db, content)
    return content.getMetadata()


def createContent(
    db: Session, current_user: User, payload: SubmitContentRequest
) -> dict:
    try:
        if payload.content_type == "guide":
            content = Guide(
                title=payload.title,
                description=payload.description,
                petType=payload.petType,
                emergencyCategory=payload.emergencyCategory,
                authorVeterinarianID=current_user.userID,
                publicationStatus="draft",
                steps=payload.steps or [],
                stepCount=len(payload.steps or []),
            )
            content_repository.add(db, content)
        elif payload.content_type == "video":
            if not payload.videoURL or not video_hosting.isValidYouTubeURL(payload.videoURL):
                raise HTTPException(
                    status_code=422, detail="videoURL must be a valid YouTube URL."
                )
            content = Video(
                title=payload.title,
                description=payload.description,
                petType=payload.petType,
                emergencyCategory=payload.emergencyCategory,
                authorVeterinarianID=current_user.userID,
                publicationStatus="draft",
                videoURL=video_hosting.getEmbedURL(payload.videoURL),
                duration=payload.duration,
            )
            content_repository.add(db, content)
        elif payload.content_type == "quiz":
            if not payload.questions:
                raise HTTPException(
                    status_code=422, detail="Quiz must have at least one question."
                )
            quiz = Quiz(
                title=payload.title,
                description=payload.description,
                petType=payload.petType,
                emergencyCategory=payload.emergencyCategory,
                authorVeterinarianID=current_user.userID,
                publicationStatus="draft",
                duration=payload.duration,
                totalScore=len(payload.questions),
            )
            content = content_repository.add_quiz_with_questions(
                db, quiz, payload.questions
            )
        else:
            raise HTTPException(
                status_code=422,
                detail=f"Unknown content_type '{payload.content_type}'.",
            )
        return content.display()
    except HTTPException:
        raise
    except Exception as e:
        content_repository.rollback(db)
        raise HTTPException(status_code=500, detail=str(e))


def updateContent(
    db: Session, content_id: str, current_user: User, payload: SubmitContentRequest
) -> dict:
    content = _getOrError(db, content_id)
    if content.authorVeterinarianID != current_user.userID:
        raise HTTPException(status_code=403, detail="You can only edit your own content.")
    try:
        content.title = payload.title
        content.description = payload.description
        content.petType = payload.petType
        content.emergencyCategory = payload.emergencyCategory
        if isinstance(content, Guide) and payload.steps is not None:
            content.steps = payload.steps
            content.stepCount = len(payload.steps)
        if isinstance(content, Video):
            if not payload.videoURL or not video_hosting.isValidYouTubeURL(payload.videoURL):
                raise HTTPException(
                    status_code=422, detail="videoURL must be a valid YouTube URL."
                )
            content.videoURL = video_hosting.getEmbedURL(payload.videoURL)
            content.duration = payload.duration
        if isinstance(content, Quiz):
            if not payload.questions:
                raise HTTPException(
                    status_code=422, detail="Quiz must have at least one question."
                )
            content.duration = payload.duration
            content.totalScore = len(payload.questions)
            content = content_repository.replace_quiz_questions(
                db, content, payload.questions
            )
        content.publicationStatus = "draft"
        content.assignedVeterinarianID = None
        content_repository.update(db, content)
        return content.display()
    except HTTPException:
        raise
    except Exception as e:
        content_repository.rollback(db)
        raise HTTPException(status_code=500, detail=str(e))


def reviewContent(
    db: Session, content_id: str, current_user: User, payload: ReviewRequest
) -> dict:
    content = _getOrError(db, content_id)
    if content.assignedVeterinarianID != current_user.userID:
        raise HTTPException(
            status_code=403,
            detail="You are not the assigned reviewer for this content.",
        )
    if content.authorVeterinarianID == current_user.userID:
        raise HTTPException(status_code=403, detail="You cannot review your own content.")
    if payload.status not in ("verified", "rejected"):
        raise HTTPException(
            status_code=422, detail="Status must be 'verified' or 'rejected'."
        )
    if payload.status == "rejected" and not (payload.comment or "").strip():
        raise HTTPException(
            status_code=422, detail="A comment is required when rejecting content."
        )
    try:
        content.updatePublicationStatus(payload.status)
        content.reviewComment = payload.comment or None
        content_repository.update(db, content)
        return content.getMetadata()
    except ValueError as e:
        content_repository.rollback(db)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        content_repository.rollback(db)
        raise HTTPException(status_code=500, detail=str(e))


def setDraftAndAssign(
    db: Session, content_id: str, assigned_vet_id: str
) -> dict:
    content = _getOrError(db, content_id)
    if content.authorVeterinarianID == assigned_vet_id:
        raise HTTPException(
            status_code=422, detail="Cannot assign the author as the assigned vet."
        )
    try:
        content.assignedVeterinarianID = assigned_vet_id
        content.updatePublicationStatus("pending_verification")
        content_repository.update(db, content)
        return content.getMetadata()
    except Exception as e:
        content_repository.rollback(db)
        raise HTTPException(status_code=500, detail=str(e))


def requestAmend(db: Session, content_id: str, feedback: str) -> dict:
    if not feedback.strip():
        raise HTTPException(status_code=422, detail="Feedback is required.")
    content = _getOrError(db, content_id)
    try:
        content.updatePublicationStatus("rejected")
        content.reviewComment = feedback
        content_repository.update(db, content)
        return content.getMetadata()
    except Exception as e:
        content_repository.rollback(db)
        raise HTTPException(status_code=500, detail=str(e))


def setStatus(db: Session, content_id: str, new_status: str) -> dict:
    content = _getOrError(db, content_id)
    try:
        content.updatePublicationStatus(new_status)
        content_repository.update(db, content)
        return content.getMetadata()
    except ValueError as e:
        content_repository.rollback(db)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        content_repository.rollback(db)
        raise HTTPException(status_code=500, detail=str(e))


def deleteContent(db: Session, content_id: str) -> None:
    content = _getOrError(db, content_id)
    try:
        content_repository.delete(db, content)
    except Exception as e:
        content_repository.rollback(db)
        raise HTTPException(status_code=500, detail=str(e))


def getContentById(db: Session, content_id: str) -> FirstAidContent | None:
    return content_repository.get_by_id(db, content_id)


def _getOrError(db: Session, content_id: str) -> FirstAidContent:
    content = content_repository.get_by_id(db, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found.")
    return content
