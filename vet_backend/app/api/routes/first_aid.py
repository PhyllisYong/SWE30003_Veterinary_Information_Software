from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.first_aid_content import FirstAidContent
from app.schemas.first_aid import ContentSearchResponse
from app.services.search_engine import SearchEngine

router = APIRouter(tags=["first-aid"])


def get_search_engine(db: Session = Depends(get_db)) -> SearchEngine:
    return SearchEngine(db)


@router.get("/first-aid/search", response_model=ContentSearchResponse)
def search_content(
    petType: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    contentType: Optional[str] = Query(None),
    otherDesc: Optional[str] = Query(None),
    engine: SearchEngine = Depends(get_search_engine),
):
    results = engine.searchContent(
        petType=petType, category=category, contentType=contentType, otherDesc=otherDesc
    )
    if not results:
        return {
            "status": "warning",
            "data": [],
            "message": "No guides found. Please use the Veterinary Advice Chat for personalised help.",
        }
    return {"status": "ok", "data": [item.display() for item in results]}


@router.get("/first-aid/{content_id}")
def get_content(
    content_id: str,
    engine: SearchEngine = Depends(get_search_engine),
    db: Session = Depends(get_db),
):
    item = engine.getContentByID(content_id)
    if item is None:
        item = db.query(FirstAidContent).filter(FirstAidContent.contentID == content_id).first()
    if item is None:
        return {"status": "error", "message": f"Content '{content_id}' not found."}
    return {"status": "ok", "data": item.display()}
