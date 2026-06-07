from sqlalchemy.orm import Session

from app.models.chat import VeterinaryAdviceChat
from app.models.message import Message


def getById(db: Session, chatId: str) -> VeterinaryAdviceChat | None:
    return db.query(VeterinaryAdviceChat).filter(
        VeterinaryAdviceChat.chatID == chatId
    ).first()


def getByPetOwner(db: Session, ownerId: str) -> list[VeterinaryAdviceChat]:
    return db.query(VeterinaryAdviceChat).filter(
        VeterinaryAdviceChat.petOwnerID == ownerId
    ).all()


def getByVet(db: Session, vetId: str) -> list[VeterinaryAdviceChat]:
    return db.query(VeterinaryAdviceChat).filter(
        VeterinaryAdviceChat.veterinarianID == vetId
    ).all()


def addChat(db: Session, chat: VeterinaryAdviceChat) -> VeterinaryAdviceChat:
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return chat


def getMessageById(db: Session, messageId: str, chatId: str) -> Message | None:
    return db.query(Message).filter(
        Message.messageID == messageId,
        Message.chatID == chatId,
    ).first()


def addMessage(db: Session, message: Message) -> Message:
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def updateMessage(db: Session, message: Message) -> Message:
    db.commit()
    db.refresh(message)
    return message


def deleteMessage(db: Session, message: Message) -> None:
    db.delete(message)
    db.commit()
