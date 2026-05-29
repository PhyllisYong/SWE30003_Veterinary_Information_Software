from sqlalchemy.orm import Session

from app.models.chat import VeterinaryAdviceChat
from app.models.message import Message


def get_by_id(db: Session, chat_id: str) -> VeterinaryAdviceChat | None:
    return db.query(VeterinaryAdviceChat).filter(
        VeterinaryAdviceChat.chatID == chat_id
    ).first()


def get_by_pet_owner(db: Session, owner_id: str) -> list[VeterinaryAdviceChat]:
    return db.query(VeterinaryAdviceChat).filter(
        VeterinaryAdviceChat.petOwnerID == owner_id
    ).all()


def get_by_vet(db: Session, vet_id: str) -> list[VeterinaryAdviceChat]:
    return db.query(VeterinaryAdviceChat).filter(
        VeterinaryAdviceChat.vetID == vet_id
    ).all()


def add_chat(db: Session, chat: VeterinaryAdviceChat) -> VeterinaryAdviceChat:
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def get_message_by_id(db: Session, message_id: str, chat_id: str) -> Message | None:
    return db.query(Message).filter(
        Message.messageID == message_id,
        Message.chatID == chat_id,
    ).first()


def add_message(db: Session, message: Message) -> Message:
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def update_message(db: Session, message: Message) -> Message:
    db.commit()
    db.refresh(message)
    return message


def delete_message(db: Session, message: Message) -> None:
    db.delete(message)
    db.commit()
