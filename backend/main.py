from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional
import uvicorn
from datetime import datetime
import uuid
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

from database import init_db, get_db
from models import ChatSession, Message, UploadedFile
from services.document_processor import DocumentProcessor
from services.rag_service import RAGService
from services.ocr_service import OCRService

app = FastAPI(title="AI Customer Support Chatbot API")

# CORS middleware - allow frontend URL from environment or use wildcard for development
frontend_url = os.getenv("FRONTEND_URL", "*")
# Support both single URL and comma-separated URLs
if frontend_url == "*":
    allowed_origins = ["*"]
else:
    allowed_origins = [url.strip() for url in frontend_url.split(",")] + ["http://localhost:5173", "http://localhost:3000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
document_processor = DocumentProcessor()
rag_service = RAGService()
ocr_service = OCRService()

# Initialize database
init_db()


# Pydantic models for request/response
class ChatSessionCreate(BaseModel):
    title: Optional[str] = "New Chat"


class ChatSessionResponse(BaseModel):
    id: str
    created_at: str
    updated_at: str
    title: str


class MessageCreate(BaseModel):
    session_id: str
    role: str
    content: str


class MessageResponse(BaseModel):
    id: str
    session_id: str
    role: str
    content: str
    created_at: str


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    message: str
    sources: List[str] = []


# API Endpoints
@app.get("/")
async def root():
    return {"message": "AI Customer Support Chatbot API"}


@app.post("/api/sessions", response_model=ChatSessionResponse)
async def create_session(session: ChatSessionCreate):
    """Create a new chat session"""
    db = next(get_db())
    new_session = ChatSession(
        id=str(uuid.uuid4()),
        title=session.title,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    return ChatSessionResponse(
        id=new_session.id,
        created_at=new_session.created_at.isoformat(),
        updated_at=new_session.updated_at.isoformat(),
        title=new_session.title
    )


@app.get("/api/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_messages(session_id: str):
    """Get all messages for a session"""
    db = next(get_db())
    messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.created_at).all()
    return [
        MessageResponse(
            id=msg.id,
            session_id=msg.session_id,
            role=msg.role,
            content=msg.content,
            created_at=msg.created_at.isoformat()
        )
        for msg in messages
    ]


@app.post("/api/messages", response_model=MessageResponse)
async def create_message(message: MessageCreate):
    """Create a new message"""
    db = next(get_db())
    new_message = Message(
        id=str(uuid.uuid4()),
        session_id=message.session_id,
        role=message.role,
        content=message.content,
        created_at=datetime.utcnow()
    )
    db.add(new_message)
    
    # Update session timestamp
    session = db.query(ChatSession).filter(ChatSession.id == message.session_id).first()
    if session:
        session.updated_at = datetime.utcnow()
    
    db.commit()
    db.refresh(new_message)
    return MessageResponse(
        id=new_message.id,
        session_id=new_message.session_id,
        role=new_message.role,
        content=new_message.content,
        created_at=new_message.created_at.isoformat()
    )


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat message with RAG"""
    db = next(get_db())
    
    # Check if session exists
    session = db.query(ChatSession).filter(ChatSession.id == request.session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Save user message
    try:
        user_message = Message(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            role="user",
            content=request.message,
            created_at=datetime.utcnow()
        )
        db.add(user_message)
        
        # Update session timestamp
        session.updated_at = datetime.utcnow()
        db.commit()
    except Exception as e:
        db.rollback()
        print(f"Error saving user message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error saving message: {str(e)}")
    
    # Get RAG response
    try:
        print(f"Processing chat request for session {request.session_id}")
        response, sources = await rag_service.get_response(request.message, request.session_id)
        print(f"RAG response generated: {len(response)} characters")
        
        # Save assistant message
        assistant_message = Message(
            id=str(uuid.uuid4()),
            session_id=request.session_id,
            role="assistant",
            content=response,
            created_at=datetime.utcnow()
        )
        db.add(assistant_message)
        db.commit()
        
        return ChatResponse(message=response, sources=sources)
    except Exception as e:
        db.rollback()
        print(f"Error generating RAG response: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error generating response: {str(e)}")


@app.post("/api/upload/document")
async def upload_document(session_id: str, file: UploadFile = File(...)):
    """Upload and process a document (PDF, DOCX)"""
    db = next(get_db())
    
    # Check if session exists
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Save file info
    file_record = UploadedFile(
        id=str(uuid.uuid4()),
        session_id=session_id,
        filename=file.filename,
        file_type=file.content_type or "application/octet-stream",
        created_at=datetime.utcnow()
    )
    db.add(file_record)
    db.commit()
    
    # Process document
    try:
        print(f"Processing document upload for session {session_id}, file: {file.filename}")
        content = await file.read()
        print(f"File size: {len(content)} bytes")
        
        chunks = await document_processor.process_document(content, file.filename, file.content_type)
        print(f"Document processed into {len(chunks)} chunks")
        
        # Store in vector database
        await rag_service.add_documents(chunks, session_id)
        print(f"Document chunks added to vector database")
        
        return {
            "message": "Document uploaded and processed successfully",
            "file_id": file_record.id,
            "chunks": len(chunks)
        }
    except Exception as e:
        print(f"Error processing document: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")


@app.post("/api/upload/screenshot")
async def upload_screenshot(session_id: str, file: UploadFile = File(...)):
    """Upload and process a screenshot/image with OCR"""
    db = next(get_db())
    
    # Check if session exists
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Save file info
    file_record = UploadedFile(
        id=str(uuid.uuid4()),
        session_id=session_id,
        filename=file.filename,
        file_type=file.content_type or "image/jpeg",
        created_at=datetime.utcnow()
    )
    db.add(file_record)
    db.commit()
    
    # Process image with OCR
    try:
        content = await file.read()
        extracted_text = await ocr_service.extract_text(content)
        
        if extracted_text:
            # Process extracted text as document
            chunks = await document_processor.process_text(extracted_text, file.filename)
            await rag_service.add_documents(chunks, session_id)
        
        return {
            "message": "Screenshot processed successfully",
            "file_id": file_record.id,
            "extracted_text": extracted_text[:200] if extracted_text else "No text found"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing screenshot: {str(e)}")


@app.post("/api/upload/image")
async def upload_image(session_id: str, file: UploadFile = File(...)):
    """Upload an image for chat (handles both OCR and chat)"""
    # This endpoint handles image uploads from chat
    # It will extract text via OCR and add to context
    return await upload_screenshot(session_id, file)


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)

