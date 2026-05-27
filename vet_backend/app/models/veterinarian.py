from sqlalchemy import Column, String, JSON, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.user import User


class Veterinarian(User):
    __tablename__ = "veterinarians"

    userID = Column("user_id", String, ForeignKey("users.user_id"), primary_key=True)
    licenseNumber = Column("license_number", String, nullable=False)
    specialisation = Column(String, nullable=True)
    availableSlots = Column("available_slots", JSON, nullable=True, default=list)
    # JSON list of ISO 8601 datetime strings e.g. ["2025-06-01T09:00:00Z", ...]

    bookings = relationship("Booking", back_populates="veterinarian", lazy="select")
    chats = relationship("VeterinaryAdviceChat", back_populates="veterinarian", lazy="select")

    __mapper_args__ = {
        "polymorphic_identity": "veterinarian",
    }
