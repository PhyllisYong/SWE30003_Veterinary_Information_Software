from datetime import datetime, timezone
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import User


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class PetOwner(User):
    __tablename__ = "pet_owners"

    userID = Column("user_id", String, ForeignKey("users.user_id"), primary_key=True)
    contactNumber = Column("contact_number", String, nullable=True)

    pets = relationship("Pet", back_populates="owner", lazy="select")
    bookings = relationship("Booking", back_populates="pet_owner", lazy="select")
    chats = relationship("VeterinaryAdviceChat", back_populates="pet_owner", lazy="select")
    quiz_results = relationship("QuizResult", back_populates="pet_owner", lazy="select")

    __mapper_args__ = {
        "polymorphic_identity": "pet_owner",
    }

    def accessFirstAidContent(self, db, petType: str, emergencyCategory: str) -> list:
        from app.services.search_engine import SearchEngine
        engine = SearchEngine(db)
        return engine.searchContent(petType=petType, emergencyCategory=emergencyCategory)

    def attemptQuiz(self, db, quizID: str):
        from app.repositories import quiz_repository
        return quiz_repository.get_by_id(db, quizID)

    def createPetProfile(self, db, petName: str, petType: str,
                         age: int | None = None, gender: str | None = None):
        from app.models.pet import Pet
        from app.repositories import pet_repository
        pet = Pet(petName=petName, petType=petType, age=age,
                  gender=gender, petOwnerID=self.userID)
        return pet_repository.add(db, pet)

    def updatePetProfile(self, db, petID: str, petName: str | None = None,
                         petType: str | None = None, age: int | None = None,
                         gender: str | None = None):
        from app.repositories import pet_repository
        pet = pet_repository.get_by_id_and_owner(db, petID, self.userID)
        pet.updatePetDetails(petName=petName, petType=petType, age=age, gender=gender)
        return pet_repository.update(db, pet)

    def deletePetProfile(self, db, petID: str) -> None:
        from app.repositories import pet_repository
        pet = pet_repository.get_by_id_and_owner(db, petID, self.userID)
        pet_repository.delete(db, pet)

    def accessVeterinaryAdviceChat(self, db, veterinarianID: str, isUrgent: bool = False):
        from app.models.chat import VeterinaryAdviceChat
        from app.repositories import chat_repository
        chat = VeterinaryAdviceChat.startChat(
            createdAt=_now(),
            isUrgent=isUrgent,
            petOwnerID=self.userID,
            veterinarianID=veterinarianID,
        )
        return chat_repository.add_chat(db, chat)

    def makeBooking(self, db, veterinarianID: str, timeslot: str,
                    petID: str | None = None):
        from app.models.booking import Booking
        from app.repositories import booking_repository
        vet = booking_repository.get_vet_by_id(db, veterinarianID)
        vet.availableSlots = [s for s in (vet.availableSlots or []) if s != timeslot]
        booking = Booking(
            createdAt=_now(),
            timeslot=timeslot,
            bookingStatus="pending",
            petOwnerID=self.userID,
            veterinarianID=veterinarianID,
            petID=petID,
        )
        return booking_repository.add(db, booking)
