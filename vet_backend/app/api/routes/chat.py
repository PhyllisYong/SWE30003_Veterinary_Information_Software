from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.routes.auth import getCurrentUser
from app.models.user import User
from app.models.chat import VeterinaryAdviceChat
from app.models.message import Message
from app.models.veterinarian import Veterinarian
from app.schemas.chat import (
    StartChatRequest,
    SendMessageRequest,
    EditMessageRequest,
    ChatResponse,
    MessageResponse,
)
from app.patterns.observer import WebSocketObserver

router = APIRouter(prefix="/api/chats", tags=["Chat"])

# chatID → list of active WebSocketObserver instances
_active_observers: dict[str, list[WebSocketObserver]] = {}


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _get_chat_or_404(chatID: str, db: Session) -> VeterinaryAdviceChat:
    chat = db.query(VeterinaryAdviceChat).filter(VeterinaryAdviceChat.chatID == chatID).first()
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return chat


def _assert_participant(chat: VeterinaryAdviceChat, user: User) -> None:
    if user.userID not in (chat.petOwnerID, chat.vetID):
        raise HTTPException(status_code=403, detail="Not a participant in this chat")


# POST /api/chats — startChat() [PetOwner only]
@router.post("")
def start_chat(
    body: StartChatRequest,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    if current_user.role != "pet_owner":
        raise HTTPException(status_code=403, detail="Only pet owners can start chats")

    vet = db.query(Veterinarian).filter(Veterinarian.userID == body.vetID).first()
    if not vet:
        raise HTTPException(status_code=404, detail="Veterinarian not found")

    chat = VeterinaryAdviceChat(
        createdAt=_now(),
        isUrgent=body.isUrgent,
        petOwnerID=current_user.userID,
        vetID=body.vetID,
    )
    db.add(chat)
    db.commit()
    db.refresh(chat)
    return {"status": "ok", "data": ChatResponse.model_validate(chat)}


# GET /api/chats — list chats for current user
@router.get("")
def list_chats(
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    if current_user.role == "pet_owner":
        chats = db.query(VeterinaryAdviceChat).filter(
            VeterinaryAdviceChat.petOwnerID == current_user.userID
        ).all()
    elif current_user.role == "veterinarian":
        chats = db.query(VeterinaryAdviceChat).filter(
            VeterinaryAdviceChat.vetID == current_user.userID
        ).all()
    else:
        raise HTTPException(status_code=403, detail="Only pet owners and vets can access chats")

    return {"status": "ok", "data": [ChatResponse.model_validate(c) for c in chats]}


# GET /api/chats/{chatID} — viewChatHistory()
@router.get("/{chatID}")
def get_chat(
    chatID: str,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    chat = _get_chat_or_404(chatID, db)
    _assert_participant(chat, current_user)

    messages = [MessageResponse.model_validate(m) for m in chat.viewChatHistory()]
    return {
        "status": "ok",
        "data": {
            **ChatResponse.model_validate(chat).model_dump(),
            "messages": messages,
        },
    }


# WS /api/chats/{chatID}/ws — subscribe as observer
@router.websocket("/{chatID}/ws")
async def chat_websocket(chatID: str, websocket: WebSocket, db: Session = Depends(get_db)):
    await websocket.accept()
    obs = WebSocketObserver(websocket)
    _active_observers.setdefault(chatID, []).append(obs)
    try:
        while True:
            await websocket.receive_text()  # keep-alive; client sends nothing
    except WebSocketDisconnect:
        observers = _active_observers.get(chatID, [])
        if obs in observers:
            observers.remove(obs)


# POST /api/chats/{chatID}/messages — sendMessage()
@router.post("/{chatID}/messages")
async def send_message(
    chatID: str,
    body: SendMessageRequest,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    chat = _get_chat_or_404(chatID, db)
    _assert_participant(chat, current_user)

    msg = Message(
        senderID=current_user.userID,
        content=body.content,
        timestamp=_now(),
        chatID=chatID,
    )
    db.add(msg)
    db.commit()
    db.refresh(msg)

    payload = MessageResponse.model_validate(msg).model_dump()
    for obs in list(_active_observers.get(chatID, [])):
        await obs.update("message_sent", payload)

    return {"status": "ok", "data": payload}


# PUT /api/chats/{chatID}/messages/{messageID} — editMessage()
@router.put("/{chatID}/messages/{messageID}")
def edit_message(
    chatID: str,
    messageID: str,
    body: EditMessageRequest,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    chat = _get_chat_or_404(chatID, db)
    _assert_participant(chat, current_user)

    msg = db.query(Message).filter(
        Message.messageID == messageID,
        Message.chatID == chatID,
    ).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg.senderID != current_user.userID:
        raise HTTPException(status_code=403, detail="Cannot edit another user's message")

    msg.content = body.content
    db.commit()
    db.refresh(msg)
    return {"status": "ok", "data": MessageResponse.model_validate(msg)}


# DELETE /api/chats/{chatID}/messages/{messageID} — deleteMessage()
@router.delete("/{chatID}/messages/{messageID}")
def delete_message(
    chatID: str,
    messageID: str,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    chat = _get_chat_or_404(chatID, db)
    _assert_participant(chat, current_user)

    msg = db.query(Message).filter(
        Message.messageID == messageID,
        Message.chatID == chatID,
    ).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
    if msg.senderID != current_user.userID:
        raise HTTPException(status_code=403, detail="Cannot delete another user's message")

    db.delete(msg)
    db.commit()
    return {"status": "ok", "data": {"message": "Message deleted"}}
