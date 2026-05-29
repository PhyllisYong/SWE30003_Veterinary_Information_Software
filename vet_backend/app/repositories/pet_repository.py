from sqlalchemy.orm import Session

from app.models.booking import Booking
from app.models.pet import Pet


def get_by_id(db: Session, pet_id: str) -> Pet | None:
    return db.query(Pet).filter(Pet.petID == pet_id).first()


def get_by_id_and_owner(db: Session, pet_id: str, owner_id: str) -> Pet | None:
    return db.query(Pet).filter(Pet.petID == pet_id, Pet.ownerID == owner_id).first()


def get_by_owner(db: Session, owner_id: str) -> list[Pet]:
    return db.query(Pet).filter(Pet.ownerID == owner_id).all()


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
