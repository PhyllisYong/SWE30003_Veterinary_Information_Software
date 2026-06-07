from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.veterinarian import Veterinarian


def getAllVets(db: Session) -> list[Veterinarian]:
    return db.query(Veterinarian).all()


def getVetById(db: Session, vetId: str) -> Veterinarian | None:
    return db.query(Veterinarian).filter(Veterinarian.userID == vetId).first()


def getVetByUserId(db: Session, userId: str) -> Veterinarian | None:
    return db.query(Veterinarian).filter(Veterinarian.userID == userId).first()


def updateVet(db: Session, vet: Veterinarian) -> Veterinarian:
    db.commit()
    return vet


def getById(db: Session, bookingId: str) -> Booking | None:
    return db.query(Booking).filter(Booking.bookingID == bookingId).first()


def getByIdAndVet(db: Session, bookingId: str, vetId: str) -> Booking | None:
    return db.query(Booking).filter(
        Booking.bookingID == bookingId,
        Booking.veterinarianID == vetId,
    ).first()


def getByPetOwner(db: Session, ownerId: str) -> list[Booking]:
    return db.query(Booking).filter(Booking.petOwnerID == ownerId).all()


def getByVet(db: Session, vetId: str) -> list[Booking]:
    return db.query(Booking).filter(Booking.veterinarianID == vetId).all()


def getConflicting(db: Session, vetId: str, timeslot: str) -> Booking | None:
    return db.query(Booking).filter(
        Booking.veterinarianID == vetId,
        Booking.timeslot == timeslot,
        Booking.bookingStatus.in_(["pending", "accepted"]),
    ).first()


def add(db: Session, booking: Booking) -> Booking:
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


def update(db: Session, booking: Booking) -> Booking:
    db.commit()
    db.refresh(booking)
    return booking
