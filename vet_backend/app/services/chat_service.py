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


def start_chat(db: Session, current_user: User, body) -> ChatResponse:
    vet = vet_repo.get_vet_by_id(db, body.vetID)
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinarian not found")

    chat = VeterinaryAdviceChat.startChat(
        createdAt=_now(),
        isUrgent=body.isUrgent,
        petOwnerID=current_user.userID,
        vetID=body.vetID,
    )
    chat = chat_repository.add_chat(db, chat)
    return ChatResponse.model_validate(chat)


def list_chats(db: Session, current_user: User) -> list[ChatResponse]:
    if current_user.role == "pet_owner":
        chats = chat_repository.get_by_pet_owner(db, current_user.userID)
    elif current_user.role == "veterinarian":
        chats = chat_repository.get_by_vet(db, current_user.userID)
    else:
        raise HTTPException(
            status_code=403, detail="Only pet owners and vets can access chats"
        )
    return [ChatResponse.model_validate(c) for c in chats]


def get_chat(db: Session, chat_id: str, current_user: User) -> dict:
    chat = _get_chat_or_404(db, chat_id)
    _assert_participant(chat, current_user)
    messages = [MessageResponse.model_validate(m) for m in chat.viewChatHistory()]
    return {
        **ChatResponse.model_validate(chat).model_dump(),
        "messages": messages,
    }


def get_chat_for_ws(db: Session, chat_id: str) -> VeterinaryAdviceChat | None:
    return chat_repository.get_by_id(db, chat_id)


def get_user_for_ws(db: Session, user_id: str) -> User | None:
    return user_repository.get_by_id(db, user_id)


async def send_message(
    db: Session, chat_id: str, current_user: User, body
) -> MessageResponse:
    chat = _get_chat_or_404(db, chat_id)
    _assert_participant(chat, current_user)

    msg = chat.createMessage(
        senderID=current_user.userID,
        content=body.content,
        timestamp=_now(),
    )
    msg = chat_repository.add_message(db, msg)
    payload = MessageResponse.model_validate(msg)
    await chat.sendMessage(payload.model_dump())
    return payload


def edit_message(
    db: Session, chat_id: str, message_id: str, current_user: User, body
) -> MessageResponse:
    chat = _get_chat_or_404(db, chat_id)
    _assert_participant(chat, current_user)

    msg = chat_repository.get_message_by_id(db, message_id, chat_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg.senderID != current_user.userID:
        raise HTTPException(status_code=403, detail="Cannot edit another user's message")

    chat.editMessage(msg, body.content)
    msg = chat_repository.update_message(db, msg)
    return MessageResponse.model_validate(msg)


def delete_message(
    db: Session, chat_id: str, message_id: str, current_user: User
) -> None:
    chat = _get_chat_or_404(db, chat_id)
    _assert_participant(chat, current_user)

    msg = chat_repository.get_message_by_id(db, message_id, chat_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg.senderID != current_user.userID:
        raise HTTPException(status_code=403, detail="Cannot delete another user's message")

    chat.deleteMessage(msg)
    chat_repository.delete_message(db, msg)


def _get_chat_or_404(db: Session, chat_id: str) -> VeterinaryAdviceChat:
    chat = chat_repository.get_by_id(db, chat_id)
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


def _assert_participant(chat: VeterinaryAdviceChat, user: User) -> None:
    if user.userID not in (chat.petOwnerID, chat.vetID):
        raise HTTPException(status_code=403, detail="Not a participant in this chat")
