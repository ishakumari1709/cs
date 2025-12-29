# Backend Architecture

## Overview

The AI Customer Support Chatbot backend is built with FastAPI and implements a RAG (Retrieval Augmented Generation) pipeline for document-based question answering.

## Architecture Components

### 1. API Layer (`main.py`)
- FastAPI application with RESTful endpoints
- CORS middleware for frontend integration
- Request/response models using Pydantic
- Session and message management

### 2. Database Layer (`database.py`, `models.py`)
- SQLAlchemy ORM for database operations
- SQLite database (can be upgraded to PostgreSQL)
- Models: ChatSession, Message, UploadedFile
- Automatic session and message tracking

### 3. Document Processing (`services/document_processor.py`)
- PDF text extraction using PyPDF2
- DOCX text extraction using python-docx
- Text chunking with RecursiveCharacterTextSplitter
- Metadata preservation for source tracking

### 4. OCR Service (`services/ocr_service.py`)
- Image text extraction using Tesseract or EasyOCR
- Supports screenshots and image uploads
- Automatic fallback between OCR libraries
- Extracted text is processed as documents

### 5. RAG Service (`services/rag_service.py`)
- **Embeddings**: Sentence Transformers (all-MiniLM-L6-v2)
- **Vector Database**: ChromaDB for storing document embeddings
- **LLM Options**:
  - HuggingFace Inference API (recommended, free tier)
  - Local GPT-2 model (fallback, CPU-friendly)
- **Retrieval**: Semantic search for relevant document chunks
- **Generation**: Context-aware responses using retrieved chunks

## Data Flow

### Document Upload Flow
```
1. User uploads PDF/DOCX
   ↓
2. DocumentProcessor extracts text
   ↓
3. Text is split into chunks (1000 chars, 200 overlap)
   ↓
4. Chunks are embedded using Sentence Transformers
   ↓
5. Embeddings stored in ChromaDB (per session)
   ↓
6. File metadata saved to database
```

### Chat Flow
```
1. User sends message
   ↓
2. Message saved to database
   ↓
3. RAGService retrieves relevant chunks (semantic search)
   ↓
4. Context built from top 3 relevant chunks
   ↓
5. LLM generates response using context
   ↓
6. Response saved to database
   ↓
7. Sources returned to user
```

### OCR Flow
```
1. User uploads image/screenshot
   ↓
2. OCRService extracts text
   ↓
3. Extracted text processed as document
   ↓
4. Text chunked and embedded
   ↓
5. Stored in vector database
```

## Session Management

- Each chat session has a unique ID
- Sessions store their own vector database collection
- Messages are linked to sessions
- Uploaded files are tracked per session
- Session timestamps updated on activity

## Vector Database

- **Storage**: ChromaDB (local file-based)
- **Location**: `./chroma_db/`
- **Collections**: One per session (`session_{session_id}`)
- **Embeddings**: 384-dimensional vectors (MiniLM-L6-v2)
- **Search**: Cosine similarity for retrieval

## LLM Configuration

### Option 1: HuggingFace Inference API (Recommended)
- **Model**: Mistral-7B-Instruct-v0.1
- **Cost**: Free tier available
- **Setup**: Set `HUGGINGFACE_API_KEY` environment variable
- **Pros**: Fast, high-quality responses, no local resources

### Option 2: Local Model
- **Model**: GPT-2 (small, fast)
- **Cost**: Free (runs on CPU)
- **Setup**: Automatic fallback
- **Pros**: No API key needed, privacy
- **Cons**: Lower quality, slower, requires download

## API Endpoints

### Sessions
- `POST /api/sessions` - Create session
- `GET /api/sessions/{id}/messages` - Get messages

### Messages
- `POST /api/messages` - Create message
- `POST /api/chat` - Chat with RAG

### Uploads
- `POST /api/upload/document` - Upload PDF/DOCX
- `POST /api/upload/screenshot` - Upload image with OCR
- `POST /api/upload/image` - Upload image for chat

## File Structure

```
backend/
├── main.py                    # FastAPI app
├── database.py                # DB setup
├── models.py                  # SQLAlchemy models
├── start.py                   # Startup script
├── test_api.py                # API tests
├── requirements.txt           # Dependencies
├── README.md                  # Documentation
├── QUICKSTART.md              # Quick start guide
├── FRONTEND_INTEGRATION.md    # Frontend setup
├── ARCHITECTURE.md            # This file
└── services/
    ├── document_processor.py  # PDF/DOCX processing
    ├── ocr_service.py         # OCR functionality
    └── rag_service.py         # RAG pipeline
```

## Performance Considerations

1. **First Run**: Downloads models (~500MB-2GB)
2. **Embeddings**: Cached after first use
3. **Vector Search**: Fast with ChromaDB
4. **LLM**: HuggingFace API is fastest, local model slower
5. **OCR**: EasyOCR is more accurate but slower

## Scalability

- **Current**: Single server, SQLite, local ChromaDB
- **Production**: 
  - PostgreSQL for database
  - Redis for caching
  - Separate ChromaDB server
  - Load balancer for multiple instances
  - HuggingFace API or dedicated LLM server

## Security

- CORS configured for frontend origins
- File upload size limits (can be configured)
- SQL injection protection (SQLAlchemy)
- Input validation (Pydantic)
- Session isolation (per-session vector stores)

## Future Enhancements

1. User authentication
2. Multi-tenant support
3. Document versioning
4. Advanced OCR (handwriting, tables)
5. Multi-language support
6. Streaming responses
7. Document preview
8. Search across all sessions
9. Export chat history
10. Analytics and metrics

