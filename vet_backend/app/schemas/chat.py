from pydantic import BaseModel


class StartChatRequest(BaseModel):
    vetID: str
    isUrgent: bool = False


class SendMessageRequest(BaseModel):
    content: str


class EditMessageRequest(BaseModel):
    content: str


class MessageResponse(BaseModel):
    messageID: str
    senderID: str
    content: str
    timestamp: str
    chatID: str

    model_config = {"from_attributes": True}


class ChatResponse(BaseModel):
    chatID: str
    createdAt: str
    isUrgent: bool
    petOwnerID: str
    vetID: str

    model_config = {"from_attributes": True}
