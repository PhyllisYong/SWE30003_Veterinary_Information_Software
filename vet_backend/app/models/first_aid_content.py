import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class FirstAidContent(Base):
    __tablename__ = "first_aid_contents"

    contentID = Column("content_id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    petType = Column("pet_type", String, nullable=False)           # "cat" | "dog" | "rabbit" | "hamster" | "guinea_pig"
    emergencyCategory = Column("emergency_category", String, nullable=False)
    publicationStatus = Column("publication_status", String, nullable=False, default="draft")
    # "draft" | "pending_verification" | "verified" | "published" | "rejected"
    authorVetID = Column("author_vet_id", String, ForeignKey("users.user_id"), nullable=True)
    content_type = Column(String, nullable=False)                  # discriminator: "guide" | "video" | "quiz"

    __mapper_args__ = {
        "polymorphic_on": content_type,
        "polymorphic_identity": "first_aid_content",
    }

    def getMetadata(self) -> dict:
        return {
            "contentID": self.contentID,
            "title": self.title,
            "description": self.description,
            "petType": self.petType,
            "emergencyCategory": self.emergencyCategory,
            "publicationStatus": self.publicationStatus,
            "authorVetID": self.authorVetID,
            "content_type": self.content_type,
        }

    def getAuthorID(self) -> str:
        return self.authorVetID

    def getID(self) -> str:
        return self.contentID
