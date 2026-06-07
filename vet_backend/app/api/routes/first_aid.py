from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import getDb
from app.schemas.first_aid import ContentSearchResponse
from app.services import content_service
from app.services.search_engine import SearchEngine

router = APIRouter(tags=["first-aid"])


def getSearchEngine(db: Session = Depends(getDb)) -> SearchEngine:
    return SearchEngine(db)


@router.get("/first-aid/search", response_model=ContentSearchResponse)
def searchContent(
    petType: Optional[str] = Query(None),
    emergencyCategory: Optional[str] = Query(None),
    contentType: Optional[str] = Query(None),
    authorVeterinarianID: Optional[str] = Query(None),
    otherDescription: Optional[str] = Query(None),
    engine: SearchEngine = Depends(getSearchEngine),
):
    results = engine.searchContent(
        petType=petType,
        emergencyCategory=emergencyCategory,
        contentType=contentType,
        authorVeterinarianID=authorVeterinarianID,
        otherDescription=otherDescription,
    )
    if not results:
        return {
            "status": "warning",
            "data": [],
            "message": "No guides found. Please use the Veterinary Advice Chat for personalised help.",
        }
    return {"status": "ok", "data": [item.display() for item in results]}


@router.get("/first-aid/{contentId}")
def getContent(
    contentId: str,
    engine: SearchEngine = Depends(getSearchEngine),
    db: Session = Depends(getDb),
):
    item = engine.getContentByID(contentId)
    if item is None:
        item = content_service.getContentById(db, contentId)
    if item is None:
        return {"status": "error", "message": f"Content '{contentId}' not found."}
    return {"status": "ok", "data": item.display()}
