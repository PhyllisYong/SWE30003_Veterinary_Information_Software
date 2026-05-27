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
