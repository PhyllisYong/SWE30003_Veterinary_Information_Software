import uuid
from sqlalchemy import Column, String
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

    @classmethod
    def createUser(
        cls,
        *,
        userID: str | None = None,
        name: str,
        email: str,
        password: str,
        role: str,
        contactNumber: str | None = None,
        licenseNumber: str | None = None,
        specialisation: str | None = None,
        workID: str | None = None,
    ) -> "User":
        from app.models.association_admin import AssociationAdministrator
        from app.models.pet_owner import PetOwner
        from app.models.veterinarian import Veterinarian

        userID = userID or str(uuid.uuid4())
        common = {
            "userID": userID,
            "name": name,
            "email": email,
            "password": password,
            "role": role,
        }

        if role == "pet_owner":
            return PetOwner(**common, contactNumber=contactNumber)
        if role == "veterinarian":
            return Veterinarian(
                **common,
                licenseNumber=licenseNumber,
                specialisation=specialisation,
            )
        if role == "association_admin":
            return AssociationAdministrator(**common, workID=workID)
        raise ValueError("Unsupported user role")

    def getRole(self) -> str:
        return self.role

    def getID(self) -> str:
        return self.userID

    def getName(self) -> str:
        return self.name

    def getEmail(self) -> str:
        return self.email

    def updateProfile(self, name: str | None = None, email: str | None = None) -> None:
        if name:
            self.name = name
        if email:
            self.email = email
