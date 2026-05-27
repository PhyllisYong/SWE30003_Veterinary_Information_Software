from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import User


class PetOwner(User):
    __tablename__ = "pet_owners"

    userID = Column("user_id", String, ForeignKey("users.user_id"), primary_key=True)
    contactNumber = Column("contact_number", String, nullable=True)

    # relationships (string refs to avoid circular imports)
    pets = relationship("Pet", back_populates="owner", lazy="select")
    bookings = relationship("Booking", back_populates="pet_owner", lazy="select")
    chats = relationship("VeterinaryAdviceChat", back_populates="pet_owner", lazy="select")
    quiz_results = relationship("QuizResult", back_populates="pet_owner", lazy="select")

    __mapper_args__ = {
        "polymorphic_identity": "pet_owner",
    }
