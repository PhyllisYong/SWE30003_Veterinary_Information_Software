import uuid
from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Message(Base):
    __tablename__ = "messages"

    messageID = Column("message_id", String, primary_key=True, default=lambda: str(uuid.uuid4()))
    senderID = Column("sender_id", String, nullable=False)         # userID of sender
    content = Column(String, nullable=False)
    timestamp = Column(String, nullable=False)                     # ISO 8601
    chatID = Column("chat_id", String, ForeignKey("vet_advice_chats.chat_id"), nullable=False)

    chat = relationship("VeterinaryAdviceChat", back_populates="messages")

    def getContent(self) -> str:
        return self.content

    def getSenderID(self) -> str:
        return self.senderID

    def getTimestamp(self) -> str:
        return self.timestamp

    def getID(self) -> str:
        return self.messageID
