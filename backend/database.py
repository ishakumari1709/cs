from sqlalchemy import create_engine, Column, String, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# Database URL
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chatbot.db")

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})#create table and session binding
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)#create session for database         
Base = declarative_base()  #models.py defines classes that inherit from Base.


def init_db():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine) #create all tables in the database             Good for small projects; for production, migrations (Alembic) are better.


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

