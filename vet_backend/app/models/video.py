from sqlalchemy import Column, String, Integer, ForeignKey
from app.core.database import Base
from app.models.first_aid_content import FirstAidContent


class Video(FirstAidContent):
    __tablename__ = "videos"

    contentID = Column("content_id", String, ForeignKey("first_aid_contents.content_id"), primary_key=True)
    videoURL = Column("video_url", String, nullable=True)
    durationSec = Column("duration_sec", Integer, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "video",
    }

    def getURL(self) -> str:
        return self.videoURL

    def getDuration(self) -> int:
        return self.durationSec
