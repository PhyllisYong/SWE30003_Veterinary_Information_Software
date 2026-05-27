import uuid
from abc import abstractmethod
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class FirstAidContent(Base):
    """
    Abstract base for all first-aid content types (Guide, Video, Quiz).
    Uses SQLAlchemy joined-table inheritance via the `content_type` discriminator.
    Implements the Template Method pattern: display() is abstract and must be
    overridden by each concrete subclass.
    """

    __tablename__ = "first_aid_contents"

    contentID = Column(
        "content_id", String, primary_key=True, default=lambda: str(uuid.uuid4())
    )
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    petType = Column(
        "pet_type", String, nullable=False
    )  # "cat" | "dog" | "rabbit" | "hamster" | "guinea_pig"
    emergencyCategory = Column("emergency_category", String, nullable=False)
    publicationStatus = Column(
        "publication_status", String, nullable=False, default="draft"
    )
    # "draft" | "pending_verification" | "verified" | "published" | "rejected"
    authorVetID = Column(
        "author_vet_id", String, ForeignKey("users.user_id"), nullable=True
    )
    content_type = Column(
        String, nullable=False
    )  # discriminator: "guide" | "video" | "quiz"

    __mapper_args__ = {
        "polymorphic_on": content_type,
        "polymorphic_identity": "first_aid_content",
    }

    # ------------------------------------------------------------------
    # Template Method pattern — subclasses MUST implement display()
    # ------------------------------------------------------------------

    @abstractmethod
    def display(self) -> dict:
        """
        Return a dict representation of the content ready for the API response.
        Each subclass renders its own type-specific fields on top of the
        base metadata.
        """
        raise NotImplementedError  # pragma: no cover

    # ------------------------------------------------------------------
    # Shared concrete methods (same for all subclasses)
    # ------------------------------------------------------------------

    def updateStatus(self, status: str) -> None:
        """
        Update the publication status of this content item.
        Valid values: "draft" | "pending_verification" | "verified"
                      | "published" | "rejected"
        The caller (domain method) is responsible for persisting via
        DatabaseManager after calling this.
        """
        valid_statuses = {
            "draft",
            "pending_verification",
            "verified",
            "published",
            "rejected",
        }
        if status not in valid_statuses:
            raise ValueError(f"Invalid status '{status}'. Must be one of {valid_statuses}.")
        self.publicationStatus = status

    def getMetadata(self) -> dict:
        """Return base metadata shared by all content types."""
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
