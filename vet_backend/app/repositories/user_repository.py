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


def get_by_id(db: Session, user_id: str) -> User | None:
    return db.query(User).filter(User.userID == user_id).first()


def get_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_all_by_role(db: Session, role: str) -> list[User]:
    return db.query(User).filter(User.role == role).all()


def get_pet_owner(db: Session, user_id: str) -> PetOwner | None:
    return db.query(PetOwner).filter(PetOwner.userID == user_id).first()


def get_veterinarian(db: Session, user_id: str) -> Veterinarian | None:
    return db.query(Veterinarian).filter(Veterinarian.userID == user_id).first()


def get_association_admin(db: Session, user_id: str) -> AssociationAdministrator | None:
    return db.query(AssociationAdministrator).filter(
        AssociationAdministrator.userID == user_id
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


def delete_cascade(db: Session, user: User) -> None:
    user_id = user.userID

    db.query(FirstAidContent).filter(
        FirstAidContent.authorVetID == user_id
    ).update({FirstAidContent.authorVetID: None}, synchronize_session=False)
    db.query(FirstAidContent).filter(
        FirstAidContent.assignedVetID == user_id
    ).update({FirstAidContent.assignedVetID: None}, synchronize_session=False)

    if user.role == "pet_owner":
        chat_ids = [
            c.chatID for c in db.query(VeterinaryAdviceChat.chatID).filter(
                VeterinaryAdviceChat.petOwnerID == user_id
            ).all()
        ]
        if chat_ids:
            db.query(Message).filter(Message.chatID.in_(chat_ids)).delete(
                synchronize_session=False
            )
        db.query(QuizResult).filter(QuizResult.petOwnerID == user_id).delete(
            synchronize_session=False
        )
        db.query(VeterinaryAdviceChat).filter(
            VeterinaryAdviceChat.petOwnerID == user_id
        ).delete(synchronize_session=False)
        db.query(Booking).filter(Booking.petOwnerID == user_id).delete(
            synchronize_session=False
        )
        db.query(Pet).filter(Pet.ownerID == user_id).delete(synchronize_session=False)

    if user.role == "veterinarian":
        chat_ids = [
            c.chatID for c in db.query(VeterinaryAdviceChat.chatID).filter(
                VeterinaryAdviceChat.vetID == user_id
            ).all()
        ]
        if chat_ids:
            db.query(Message).filter(Message.chatID.in_(chat_ids)).delete(
                synchronize_session=False
            )
        db.query(VeterinaryAdviceChat).filter(
            VeterinaryAdviceChat.vetID == user_id
        ).delete(synchronize_session=False)
        db.query(Booking).filter(Booking.vetID == user_id).delete(
            synchronize_session=False
        )

    db.delete(user)
    db.commit()
