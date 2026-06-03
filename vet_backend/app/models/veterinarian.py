from datetime import datetime, timezone
from sqlalchemy import Column, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import User


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


class Veterinarian(User):
    __tablename__ = "veterinarians"

    userID = Column("user_id", String, ForeignKey("users.user_id"), primary_key=True)
    licenseNumber = Column("license_number", String, nullable=False)
    specialisation = Column(String, nullable=True)
    availableSlots = Column("available_slots", JSON, nullable=True, default=list)

    bookings = relationship("Booking", back_populates="veterinarian", lazy="select")
    chats = relationship("VeterinaryAdviceChat", back_populates="veterinarian", lazy="select")

    __mapper_args__ = {
        "polymorphic_identity": "veterinarian",
    }

    def createFirstAidContent(self, db, title: str, description: str, petType: str,
                               emergencyCategory: str, contentType: str,
                               authorVeterinarianID: str, otherDescription: str):
        from app.repositories import content_repository
        from app.models.guide import Guide
        from app.models.video import Video
        from app.models.quiz import Quiz
        common = dict(
            title=title, description=description, petType=petType,
            emergencyCategory=emergencyCategory, publicationStatus="submitted",
            authorVeterinarianID=authorVeterinarianID,
        )
        if contentType == "guide":
            content = Guide(**common, steps=[], stepCount=0)
        elif contentType == "video":
            content = Video(**common, videoURL=otherDescription)
        else:
            content = Quiz(**common, totalScore=0)
        return content_repository.add(db, content)

    def updateFirstAidContent(self, db, contentID: str, title: str | None = None,
                               description: str | None = None, petType: str | None = None,
                               emergencyCategory: str | None = None,
                               contentType: str | None = None):
        from app.repositories import content_repository
        content = content_repository.get_by_id(db, contentID)
        if title:
            content.title = title
        if description:
            content.description = description
        if petType:
            content.petType = petType
        if emergencyCategory:
            content.emergencyCategory = emergencyCategory
        return content_repository.update(db, content)

    def verifyFirstAidContent(self, db, contentID: str, publicationStatus: str,
                               comment: str | None = None) -> None:
        from app.repositories import content_repository
        content = content_repository.get_by_id(db, contentID)
        content.updatePublicationStatus(publicationStatus)
        if comment:
            content.reviewComment = comment
        content_repository.update(db, content)

    def provideAdvice(self, db, chatID: str, content: str):
        from app.repositories import chat_repository
        chat = chat_repository.get_by_id(db, chatID)
        msg = chat.createMessage(
            senderID=self.userID,
            content=content,
            timestamp=_now(),
        )
        return chat_repository.add_message(db, msg)

    def provideExplanationForQuiz(self, db, quizID: str, questionID: str,
                                   explanation: str) -> None:
        from app.repositories import quiz_repository
        question = quiz_repository.get_question(db, questionID, quizID)
        question.setExplanation(explanation)
        quiz_repository.update_question(db, question)

    def acceptBookingSlot(self, db, bookingID: str):
        from app.repositories import booking_repository
        booking = booking_repository.get_by_id_and_vet(db, bookingID, self.userID)
        booking.acceptBookingSlot()
        return booking_repository.update(db, booking)

    def setAvailability(self, availableSlots: list) -> None:
        self.availableSlots = availableSlots
