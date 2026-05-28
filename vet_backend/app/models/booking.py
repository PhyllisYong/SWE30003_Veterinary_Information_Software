import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Booking(Base):
    __tablename__ = "bookings"

    bookingID = Column("booking_id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    createdAt = Column("created_at", String, nullable=False)       # ISO 8601
    timeslot = Column(String, nullable=False)                      # ISO 8601 datetime string
    bookingStatus = Column("booking_status", String, nullable=False, default="pending")
    # "pending" | "accepted" | "cancelled" | "completed"
    petOwnerID = Column("pet_owner_id", String, ForeignKey("pet_owners.user_id"), nullable=False)
    vetID = Column("vet_id", String, ForeignKey("veterinarians.user_id"), nullable=False)
    petID = Column("pet_id", String, ForeignKey("pets.pet_id"), nullable=True)

    pet_owner = relationship("PetOwner", back_populates="bookings")
    veterinarian = relationship("Veterinarian", back_populates="bookings")
    pet = relationship("Pet")

    def getStatus(self) -> str:
        return self.bookingStatus

    def updateStatus(self, s: str) -> None:
        self.bookingStatus = s

    def acceptBookingSlot(self) -> None:
        self.updateStatus("accepted")

    def cancelBooking(self) -> None:
        self.updateStatus("cancelled")

    def getTimeslot(self) -> str:
        return self.timeslot

    def getID(self) -> str:
        return self.bookingID

    def getPetOwnerID(self) -> str:
        return self.petOwnerID
