from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.chat import VeterinaryAdviceChat
from app.models.message import Message
from app.models.user import User
from app.repositories import chat_repository, user_repository
from app.repositories import booking_repository as vet_repo
from app.schemas.chat import ChatResponse, MessageResponse


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def startChat(db: Session, currentUser: User, body) -> ChatResponse:
    vet = vet_repo.getVetById(db, body.veterinarianID)
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinarian not found")

    chat = VeterinaryAdviceChat.startChat(
        createdAt=_now(),
        isUrgent=body.isUrgent,
        petOwnerID=currentUser.userID,
        veterinarianID=body.veterinarianID,
    )
    chat = chat_repository.addChat(db, chat)
    return ChatResponse.model_validate(chat)


def listChats(db: Session, currentUser: User) -> list[ChatResponse]:
    if currentUser.role == "pet_owner":
        chats = chat_repository.getByPetOwner(db, currentUser.userID)
    elif currentUser.role == "veterinarian":
        chats = chat_repository.getByVet(db, currentUser.userID)
    else:
        raise HTTPException(
            status_code=403, detail="Only pet owners and vets can access chats"
        )
    return [ChatResponse.model_validate(c) for c in chats]


def getChat(db: Session, chatId: str, currentUser: User) -> dict:
    chat = _getChatOr404(db, chatId)
    _assertParticipant(chat, currentUser)
    messages = [MessageResponse.model_validate(m) for m in chat.viewChatHistory()]
    return {
        **ChatResponse.model_validate(chat).model_dump(),
        "messages": messages,
    }


def getChatForWs(db: Session, chatId: str) -> VeterinaryAdviceChat | None:
    return chat_repository.getById(db, chatId)


def getUserForWs(db: Session, userId: str) -> User | None:
    return user_repository.getById(db, userId)


async def sendMessage(
    db: Session, chatId: str, currentUser: User, body
) -> MessageResponse:
    chat = _getChatOr404(db, chatId)
    _assertParticipant(chat, currentUser)

    msg = chat.createMessage(
        senderID=currentUser.userID,
        content=body.content,
        timestamp=_now(),
    )
    msg = chat_repository.addMessage(db, msg)
    payload = MessageResponse.model_validate(msg)
    await chat.sendMessage(payload.model_dump())
    return payload


def editMessage(
    db: Session, chatId: str, messageId: str, currentUser: User, body
) -> MessageResponse:
    chat = _getChatOr404(db, chatId)
    _assertParticipant(chat, currentUser)

    msg = chat_repository.getMessageById(db, messageId, chatId)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg.senderID != currentUser.userID:
        raise HTTPException(status_code=403, detail="Cannot edit another user's message")

    chat.editMessage(msg, body.content)
    msg = chat_repository.updateMessage(db, msg)
    return MessageResponse.model_validate(msg)


def deleteMessage(
    db: Session, chatId: str, messageId: str, currentUser: User
) -> None:
    chat = _getChatOr404(db, chatId)
    _assertParticipant(chat, currentUser)

    msg = chat_repository.getMessageById(db, messageId, chatId)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg.senderID != currentUser.userID:
        raise HTTPException(status_code=403, detail="Cannot delete another user's message")

    chat.deleteMessage(msg)
    chat_repository.deleteMessage(db, msg)


def _getChatOr404(db: Session, chatId: str) -> VeterinaryAdviceChat:
    chat = chat_repository.getById(db, chatId)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


def _assertParticipant(chat: VeterinaryAdviceChat, user: User) -> None:
    if user.userID not in (chat.petOwnerID, chat.veterinarianID):
        raise HTTPException(status_code=403, detail="Not a participant in this chat")
