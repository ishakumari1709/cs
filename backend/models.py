from sqlalchemy import Column, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class ChatSession(Base): #inherits from Base, which is defined in database.py, Represents one chat session (like one conversation tab in a UI).
    __tablename__ = "chat_sessions"
    
    id = Column(String, primary_key=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    title = Column(String, default="New Chat")
    
    messages = relationship("Message", back_populates="session", cascade="all, delete-orphan")
    uploaded_files = relationship("UploadedFile", back_populates="session", cascade="all, delete-orphan")


class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("ChatSession", back_populates="messages")


class UploadedFile(Base):
    __tablename__ = "uploaded_files"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, ForeignKey("chat_sessions.id"), nullable=False)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("ChatSession", back_populates="uploaded_files")

