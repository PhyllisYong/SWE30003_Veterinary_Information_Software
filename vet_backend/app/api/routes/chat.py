from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.api.routes.auth import getCurrentUser
from app.core.security import validateToken
from app.models.user import User
from app.schemas.chat import (
    StartChatRequest,
    SendMessageRequest,
    EditMessageRequest,
)
from app.services import chat_service
from app.services.observer import WebSocketObserver

router = APIRouter(prefix="/api/chats", tags=["Chat"])


# POST /api/chats — startChat() [PetOwner only]
@router.post("")
def start_chat(
    body: StartChatRequest,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    from fastapi import HTTPException
    if current_user.role != "pet_owner":
        raise HTTPException(status_code=403, detail="Only pet owners can start chats")
    chat = chat_service.start_chat(db, current_user, body)
    return {"status": "ok", "data": chat}


# GET /api/chats — list chats for current user
@router.get("")
def list_chats(
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    chats = chat_service.list_chats(db, current_user)
    return {"status": "ok", "data": chats}


# GET /api/chats/{chatID} — viewChatHistory()
@router.get("/{chatID}")
def get_chat(
    chatID: str,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    data = chat_service.get_chat(db, chatID, current_user)
    return {"status": "ok", "data": data}


# WS /api/chats/{chatID}/ws — subscribe as observer
@router.websocket("/{chatID}/ws")
async def chat_websocket(chatID: str, websocket: WebSocket, db: Session = Depends(get_db)):
    token = websocket.query_params.get("token")
    payload = validateToken(token) if token else None
    if payload is None:
        await websocket.close(code=1008)
        return

    user = chat_service.get_user_for_ws(db, payload["sub"])
    chat = chat_service.get_chat_for_ws(db, chatID)
    if user is None or chat is None or user.userID not in (chat.petOwnerID, chat.vetID):
        await websocket.close(code=1008)
        return

    await websocket.accept()
    obs = WebSocketObserver(websocket)
    chat.subscribe(obs)
    try:
        while True:
            await websocket.receive_text()  # keep-alive; client sends nothing
    except WebSocketDisconnect:
        chat.unsubscribe(obs)


# POST /api/chats/{chatID}/messages — sendMessage()
@router.post("/{chatID}/messages")
async def send_message(
    chatID: str,
    body: SendMessageRequest,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    payload = await chat_service.send_message(db, chatID, current_user, body)
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
    msg = chat_service.edit_message(db, chatID, messageID, current_user, body)
    return {"status": "ok", "data": msg}


# DELETE /api/chats/{chatID}/messages/{messageID} — deleteMessage()
@router.delete("/{chatID}/messages/{messageID}")
def delete_message(
    chatID: str,
    messageID: str,
    current_user: User = Depends(getCurrentUser),
    db: Session = Depends(get_db),
):
    chat_service.delete_message(db, chatID, messageID, current_user)
    return {"status": "ok", "data": {"message": "Message deleted"}}
