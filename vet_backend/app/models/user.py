import uuid
from sqlalchemy import Column, String
from sqlalchemy.orm import relationship
from app.core.database import Base

from app.models.booking import Booking
from app.models.chat import VeterinaryAdviceChat
from app.models.first_aid_content import FirstAidContent
from app.models.message import Message
from app.models.pet import Pet
from app.models.quiz_result import QuizResult


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

    def deleteUser(self, db, authentication_service=None) -> None:

        user_id = self.userID
        db.query(FirstAidContent).filter(
            FirstAidContent.authorVetID == user_id
        ).update({FirstAidContent.authorVetID: None}, synchronize_session=False)
        db.query(FirstAidContent).filter(
            FirstAidContent.assignedVetID == user_id
        ).update({FirstAidContent.assignedVetID: None}, synchronize_session=False)

        if self.role == "pet_owner":
            chat_ids = [
                c.chatID for c in db.query(VeterinaryAdviceChat.chatID).filter(
                    VeterinaryAdviceChat.petOwnerID == user_id
                ).all()
            ]
            if chat_ids:
                db.query(Message).filter(Message.chatID.in_(chat_ids)).delete(
                    synchronize_session=False
                )
            db.query(QuizResult).filter(QuizResult.petOwnerID == user_id).delete(
                synchronize_session=False
            )
            db.query(VeterinaryAdviceChat).filter(
                VeterinaryAdviceChat.petOwnerID == user_id
            ).delete(synchronize_session=False)
            db.query(Booking).filter(Booking.petOwnerID == user_id).delete(
                synchronize_session=False
            )
            db.query(Pet).filter(Pet.ownerID == user_id).delete(synchronize_session=False)

        if self.role == "veterinarian":
            chat_ids = [
                c.chatID for c in db.query(VeterinaryAdviceChat.chatID).filter(
                    VeterinaryAdviceChat.vetID == user_id
                ).all()
            ]
            if chat_ids:
                db.query(Message).filter(Message.chatID.in_(chat_ids)).delete(
                    synchronize_session=False
                )
            db.query(VeterinaryAdviceChat).filter(
                VeterinaryAdviceChat.vetID == user_id
            ).delete(synchronize_session=False)
            db.query(Booking).filter(Booking.vetID == user_id).delete(
                synchronize_session=False
            )

        if authentication_service:
            authentication_service.invalidateSession(user_id)
        db.delete(self)

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
