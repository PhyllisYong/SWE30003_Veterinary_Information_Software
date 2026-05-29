from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.veterinarian import Veterinarian


def get_all_vets(db: Session) -> list[Veterinarian]:
    return db.query(Veterinarian).all()


def get_vet_by_id(db: Session, vet_id: str) -> Veterinarian | None:
    return db.query(Veterinarian).filter(Veterinarian.userID == vet_id).first()


def get_vet_by_user_id(db: Session, user_id: str) -> Veterinarian | None:
    return db.query(Veterinarian).filter(Veterinarian.userID == user_id).first()


def update_vet(db: Session, vet: Veterinarian) -> Veterinarian:
    db.commit()
    return vet


def get_by_id(db: Session, booking_id: str) -> Booking | None:
    return db.query(Booking).filter(Booking.bookingID == booking_id).first()


def get_by_id_and_vet(db: Session, booking_id: str, vet_id: str) -> Booking | None:
    return db.query(Booking).filter(
        Booking.bookingID == booking_id,
        Booking.vetID == vet_id,
    ).first()


def get_by_pet_owner(db: Session, owner_id: str) -> list[Booking]:
    return db.query(Booking).filter(Booking.petOwnerID == owner_id).all()


def get_by_vet(db: Session, vet_id: str) -> list[Booking]:
    return db.query(Booking).filter(Booking.vetID == vet_id).all()


def get_conflicting(db: Session, vet_id: str, timeslot: str) -> Booking | None:
    return db.query(Booking).filter(
        Booking.vetID == vet_id,
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
