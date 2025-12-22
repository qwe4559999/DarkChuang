from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(String, primary_key=True, index=True)
    title = Column(String, index=True, nullable=True)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(String, ForeignKey("conversations.id"))
    role = Column(String)  # user, assistant
    content = Column(Text)
    message_type = Column(String, default="text") # text, image, molecule
    image_path = Column(String, nullable=True)
    data = Column(Text, nullable=True) # JSON string for extra data (sdf, properties, etc.)
    created_at = Column(DateTime, default=datetime.now)

    conversation = relationship("Conversation", back_populates="messages")

class KnowledgeFile(Base):
    __tablename__ = "knowledge_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    file_path = Column(String)
    file_size = Column(Integer)
    upload_time = Column(DateTime, default=datetime.now)
    status = Column(String, default="pending") # pending, indexed, failed
    error_message = Column(Text, nullable=True)
    vector_ids = Column(Text, nullable=True) # JSON string of vector IDs if needed
