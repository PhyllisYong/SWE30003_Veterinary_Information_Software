import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    userID = Column("user_id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    password = Column(String, nullable=False)
    role = Column(String, nullable=False)  # "pet_owner" | "veterinarian" | "association_admin"

    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": "user",
    }

    def getRole(self) -> str:
        return self.role

    def getID(self) -> str:
        return self.userID
