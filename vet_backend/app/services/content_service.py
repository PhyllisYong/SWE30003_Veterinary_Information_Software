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


def getMyContent(db: Session, authorId: str) -> list[dict]:
    items = content_repository.getByAuthor(db, authorId)
    return [item.display() for item in items]


def getAssignedContent(db: Session, assignedVetId: str) -> list[dict]:
    items = content_repository.getAssignedPending(db, assignedVetId)
    return [item.display() for item in items]


def getAllContent(db: Session) -> list[dict]:
    items = content_repository.getAll(db)
    return [item.display() for item in items]


def assignReviewer(
    db: Session, contentId: str, payload: AssignReviewerRequest
) -> dict:
    content = _getOrError(db, contentId)
    if content.authorVeterinarianID == payload.assignedVeterinarianID:
        raise HTTPException(
            status_code=422, detail="Cannot assign the author as the assigned vet."
        )
    content.assignedVeterinarianID = payload.assignedVeterinarianID
    content_repository.update(db, content)
    return content.getMetadata()


def createContent(
    db: Session, currentUser: User, payload: SubmitContentRequest
) -> dict:
    try:
        if payload.content_type == "guide":
            content = Guide(
                title=payload.title,
                description=payload.description,
                petType=payload.petType,
                emergencyCategory=payload.emergencyCategory,
                authorVeterinarianID=currentUser.userID,
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
                authorVeterinarianID=currentUser.userID,
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
                authorVeterinarianID=currentUser.userID,
                publicationStatus="draft",
                duration=payload.duration,
                totalScore=len(payload.questions),
            )
            content = content_repository.addQuizWithQuestions(
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
    db: Session, contentId: str, currentUser: User, payload: SubmitContentRequest
) -> dict:
    content = _getOrError(db, contentId)
    if content.authorVeterinarianID != currentUser.userID:
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
            content = content_repository.replaceQuizQuestions(
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
    db: Session, contentId: str, currentUser: User, payload: ReviewRequest
) -> dict:
    content = _getOrError(db, contentId)
    if content.assignedVeterinarianID != currentUser.userID:
        raise HTTPException(
            status_code=403,
            detail="You are not the assigned reviewer for this content.",
        )
    if content.authorVeterinarianID == currentUser.userID:
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
    db: Session, contentId: str, assignedVetId: str
) -> dict:
    content = _getOrError(db, contentId)
    if content.authorVeterinarianID == assignedVetId:
        raise HTTPException(
            status_code=422, detail="Cannot assign the author as the assigned vet."
        )
    try:
        content.assignedVeterinarianID = assignedVetId
        content.updatePublicationStatus("pending_verification")
        content_repository.update(db, content)
        return content.getMetadata()
    except Exception as e:
        content_repository.rollback(db)
        raise HTTPException(status_code=500, detail=str(e))


def requestAmend(db: Session, contentId: str, feedback: str) -> dict:
    if not feedback.strip():
        raise HTTPException(status_code=422, detail="Feedback is required.")
    content = _getOrError(db, contentId)
    try:
        content.updatePublicationStatus("rejected")
        content.reviewComment = feedback
        content_repository.update(db, content)
        return content.getMetadata()
    except Exception as e:
        content_repository.rollback(db)
        raise HTTPException(status_code=500, detail=str(e))


def setStatus(db: Session, contentId: str, newStatus: str) -> dict:
    content = _getOrError(db, contentId)
    try:
        content.updatePublicationStatus(newStatus)
        content_repository.update(db, content)
        return content.getMetadata()
    except ValueError as e:
        content_repository.rollback(db)
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        content_repository.rollback(db)
        raise HTTPException(status_code=500, detail=str(e))


def deleteContent(db: Session, contentId: str) -> None:
    content = _getOrError(db, contentId)
    try:
        content_repository.delete(db, content)
    except Exception as e:
        content_repository.rollback(db)
        raise HTTPException(status_code=500, detail=str(e))


def getContentById(db: Session, contentId: str) -> FirstAidContent | None:
    return content_repository.getById(db, contentId)


def _getOrError(db: Session, contentId: str) -> FirstAidContent:
    content = content_repository.getById(db, contentId)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found.")
    return content
