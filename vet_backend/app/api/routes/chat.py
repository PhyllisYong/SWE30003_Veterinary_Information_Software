from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session

from app.core.database import getDb
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
def startChat(
    body: StartChatRequest,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    from fastapi import HTTPException
    if currentUser.role != "pet_owner":
        raise HTTPException(status_code=403, detail="Only pet owners can start chats")
    chat = chat_service.startChat(db, currentUser, body)
    return {"status": "ok", "data": chat}


# GET /api/chats — list chats for current user
@router.get("")
def listChats(
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    chats = chat_service.listChats(db, currentUser)
    return {"status": "ok", "data": chats}


# GET /api/chats/{chatID} — viewChatHistory()
@router.get("/{chatID}")
def getChat(
    chatID: str,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    data = chat_service.getChat(db, chatID, currentUser)
    return {"status": "ok", "data": data}


# WS /api/chats/{chatID}/ws — subscribe as observer
@router.websocket("/{chatID}/ws")
async def chatWebsocket(chatID: str, websocket: WebSocket, db: Session = Depends(getDb)):
    token = websocket.query_params.get("token")
    payload = validateToken(token) if token else None
    if payload is None:
        await websocket.close(code=1008)
        return

    user = chat_service.getUserForWs(db, payload["sub"])
    chat = chat_service.getChatForWs(db, chatID)
    if user is None or chat is None or user.userID not in (chat.petOwnerID, chat.veterinarianID):
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
async def sendMessage(
    chatID: str,
    body: SendMessageRequest,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    payload = await chat_service.sendMessage(db, chatID, currentUser, body)
    return {"status": "ok", "data": payload}


# PUT /api/chats/{chatID}/messages/{messageID} — editMessage()
@router.put("/{chatID}/messages/{messageID}")
def editMessage(
    chatID: str,
    messageID: str,
    body: EditMessageRequest,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    msg = chat_service.editMessage(db, chatID, messageID, currentUser, body)
    return {"status": "ok", "data": msg}


# DELETE /api/chats/{chatID}/messages/{messageID} — deleteMessage()
@router.delete("/{chatID}/messages/{messageID}")
def deleteMessage(
    chatID: str,
    messageID: str,
    currentUser: User = Depends(getCurrentUser),
    db: Session = Depends(getDb),
):
    chat_service.deleteMessage(db, chatID, messageID, currentUser)
    return {"status": "ok", "data": {"message": "Message deleted"}}
