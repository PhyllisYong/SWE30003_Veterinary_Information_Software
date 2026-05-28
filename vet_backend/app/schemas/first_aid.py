from pydantic import BaseModel
from typing import Optional


class ContentBase(BaseModel):
    contentID: str
    title: str
    description: Optional[str]
    petType: str
    emergencyCategory: str
    publicationStatus: str
    authorVetID: Optional[str]
    content_type: str


class GuideResponse(ContentBase):
    steps: list[str]
    stepCount: int

    model_config = {"from_attributes": True}


class VideoResponse(ContentBase):
    videoURL: Optional[str]
    durationSec: Optional[int]

    model_config = {"from_attributes": True}


class ContentSearchRequest(BaseModel):
    petType: Optional[str] = None
    category: Optional[str] = None
    contentType: Optional[str] = None


class ContentSearchResponse(BaseModel):
    status: str
    data: list[dict]
