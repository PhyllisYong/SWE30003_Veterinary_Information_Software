from sqlalchemy.orm import Session

from app.models.association_admin import AssociationAdministrator
from app.models.booking import Booking
from app.models.chat import VeterinaryAdviceChat
from app.models.first_aid_content import FirstAidContent
from app.models.message import Message
from app.models.pet import Pet
from app.models.pet_owner import PetOwner
from app.models.quiz_result import QuizResult
from app.models.user import User
from app.models.veterinarian import Veterinarian


def getById(db: Session, userId: str) -> User | None:
    return db.query(User).filter(User.userID == userId).first()


def getByEmail(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def getAllByRole(db: Session, role: str) -> list[User]:
    return db.query(User).filter(User.role == role).all()


def getPetOwner(db: Session, userId: str) -> PetOwner | None:
    return db.query(PetOwner).filter(PetOwner.userID == userId).first()


def getVeterinarian(db: Session, userId: str) -> Veterinarian | None:
    return db.query(Veterinarian).filter(Veterinarian.userID == userId).first()


def getAssociationAdmin(db: Session, userId: str) -> AssociationAdministrator | None:
    return db.query(AssociationAdministrator).filter(
        AssociationAdministrator.userID == userId
    ).first()


def add(db: Session, user: User) -> User:
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def update(db: Session, user: User) -> User:
    db.commit()
    db.refresh(user)
    return user


def deleteCascade(db: Session, user: User) -> None:
    userId = user.userID

    db.query(FirstAidContent).filter(
        FirstAidContent.authorVeterinarianID == userId
    ).update({FirstAidContent.authorVeterinarianID: None}, synchronize_session=False)
    db.query(FirstAidContent).filter(
        FirstAidContent.assignedVeterinarianID == userId
    ).update({FirstAidContent.assignedVeterinarianID: None}, synchronize_session=False)

    if user.role == "pet_owner":
        chatIds = [
            c.chatID for c in db.query(VeterinaryAdviceChat.chatID).filter(
                VeterinaryAdviceChat.petOwnerID == userId
            ).all()
        ]
        if chatIds:
            db.query(Message).filter(Message.chatID.in_(chatIds)).delete(
                synchronize_session=False
            )
        db.query(QuizResult).filter(QuizResult.petOwnerID == userId).delete(
            synchronize_session=False
        )
        db.query(VeterinaryAdviceChat).filter(
            VeterinaryAdviceChat.petOwnerID == userId
        ).delete(synchronize_session=False)
        db.query(Booking).filter(Booking.petOwnerID == userId).delete(
            synchronize_session=False
        )
        db.query(Pet).filter(Pet.petOwnerID == userId).delete(synchronize_session=False)

    if user.role == "veterinarian":
        chatIds = [
            c.chatID for c in db.query(VeterinaryAdviceChat.chatID).filter(
                VeterinaryAdviceChat.veterinarianID == userId
            ).all()
        ]
        if chatIds:
            db.query(Message).filter(Message.chatID.in_(chatIds)).delete(
                synchronize_session=False
            )
        db.query(VeterinaryAdviceChat).filter(
            VeterinaryAdviceChat.veterinarianID == userId
        ).delete(synchronize_session=False)
        db.query(Booking).filter(Booking.veterinarianID == userId).delete(
            synchronize_session=False
        )

    db.delete(user)
    db.commit()
