from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.pet import Pet


def getById(db: Session, petId: str) -> Pet | None:
    return db.query(Pet).filter(Pet.petID == petId).first()


def getByIdAndOwner(db: Session, petId: str, ownerId: str) -> Pet | None:
    return db.query(Pet).filter(Pet.petID == petId, Pet.petOwnerID == ownerId).first()


def getByOwner(db: Session, ownerId: str) -> list[Pet]:
    return db.query(Pet).filter(Pet.petOwnerID == ownerId).all()


def add(db: Session, pet: Pet) -> Pet:
    db.add(pet)
    db.commit()
    db.refresh(pet)
    return pet


def update(db: Session, pet: Pet) -> Pet:
    db.commit()
    db.refresh(pet)
    return pet


def delete(db: Session, pet: Pet) -> None:
    db.query(Booking).filter(Booking.petID == pet.petID).update(
        {Booking.petID: None}, synchronize_session=False
    )
    db.delete(pet)
    db.commit()
