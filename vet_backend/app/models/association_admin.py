from sqlalchemy import Column, String, ForeignKey
from app.core.database import Base
from app.models.user import User


class AssociationAdministrator(User):
    __tablename__ = "association_admins"

    userID = Column("user_id", String, ForeignKey("users.user_id"), primary_key=True)
    workID = Column("work_id", String, nullable=False, unique=True)

    __mapper_args__ = {
        "polymorphic_identity": "association_admin",
    }

    def deleteFirstAidContent(self, db, contentID: str) -> None:
        from app.repositories import content_repository
        content = content_repository.getById(db, contentID)
        content_repository.delete(db, content)

    def updateFirstAidStatus(self, db, contentID: str, publicationStatus: str) -> None:
        from app.repositories import content_repository
        content = content_repository.getById(db, contentID)
        content.updatePublicationStatus(publicationStatus)
        content_repository.update(db, content)

    def publishFirstAidContent(self, db, contentID: str) -> None:
        self.updateFirstAidStatus(db, contentID, "published")

    def assignVeterinarianContent(self, db, contentID: str, veterinarianID: str) -> None:
        from app.repositories import content_repository
        content = content_repository.getById(db, contentID)
        content.assignedVeterinarianID = veterinarianID
        content_repository.update(db, content)
