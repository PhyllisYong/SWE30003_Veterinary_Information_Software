import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.patterns.observer import ChatSubject


class VeterinaryAdviceChat(Base, ChatSubject):
    __tablename__ = "vet_advice_chats"

    chatID = Column("chat_id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    createdAt = Column("created_at", String, nullable=False)   # ISO 8601
    isUrgent = Column("is_urgent", Boolean, nullable=False, default=False)
    petOwnerID = Column("pet_owner_id", String, ForeignKey("pet_owners.user_id"), nullable=False)
    vetID = Column("vet_id", String, ForeignKey("veterinarians.user_id"), nullable=False)

    # Composition: messages cannot exist without chat
    messages = relationship(
        "Message",
        back_populates="chat",
        cascade="all, delete-orphan",
        lazy="select",
        order_by="Message.timestamp",
    )
    pet_owner = relationship("PetOwner", back_populates="chats")
    veterinarian = relationship("Veterinarian", back_populates="chats")

    def __init__(self, **kwargs):
        Base.__init__(self)
        ChatSubject.__init__(self)
        for k, v in kwargs.items():
            setattr(self, k, v)

    def viewChatHistory(self) -> list:
        return self.messages

    def createMessage(self, senderID: str, content: str, timestamp: str):
        from app.models.message import Message

        return Message(
            senderID=senderID,
            content=content,
            timestamp=timestamp,
            chatID=self.chatID,
        )

    def editMessage(self, message, content: str) -> None:
        message.content = content

    def deleteMessage(self, message) -> None:
        if message in self.messages:
            self.messages.remove(message)

    def getID(self) -> str:
        return self.chatID
