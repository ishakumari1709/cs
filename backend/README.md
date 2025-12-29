# AI Customer Support Chatbot - Backend

FastAPI backend for the AI Customer Support Chatbot with RAG (Retrieval Augmented Generation) capabilities.

## Features

- 📄 **Document Processing**: Upload and process PDF, DOCX files
- 🖼️ **OCR Support**: Extract text from screenshots and images
- 🔍 **RAG Pipeline**: Retrieve relevant document chunks using vector search
- 💬 **Chat Interface**: Interactive chat with document-based responses
- 🗄️ **Session Management**: Store chat history and sessions
- 🆓 **Free & Open Source**: Uses free models (Sentence Transformers, ChromaDB, HuggingFace)

## Setup

### Prerequisites

- Python 3.8+
- For OCR with Tesseract: Install Tesseract OCR on your system
  - Windows: Download from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)
  - Mac: `brew install tesseract`
  - Linux: `sudo apt-get install tesseract-ocr`

### Installation

1. **Create a virtual environment** (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Run the server**:
```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Sessions
- `POST /api/sessions` - Create a new chat session
- `GET /api/sessions/{session_id}/messages` - Get messages for a session

### Messages
- `POST /api/messages` - Create a message
- `POST /api/chat` - Send a chat message and get AI response

### Uploads
- `POST /api/upload/document` - Upload a document (PDF, DOCX)
- `POST /api/upload/screenshot` - Upload a screenshot/image with OCR
- `POST /api/upload/image` - Upload an image for chat

## Configuration

### LLM Options

The backend supports multiple LLM options:

1. **Local CPU Model** (default): Uses GPT-2 or Phi-2 for local inference
2. **HuggingFace API**: Set `HUGGINGFACE_API_KEY` environment variable
3. **Custom Model**: Modify `rag_service.py` to use your preferred model

### OCR Options

Choose one:
- **Tesseract**: Requires system installation, faster
- **EasyOCR**: No system dependencies, more accurate, larger download

## Project Structure

```
backend/
├── main.py                 # FastAPI application
├── database.py            # Database setup
├── models.py              # SQLAlchemy models
├── requirements.txt       # Python dependencies
├── services/
│   ├── document_processor.py  # PDF/DOCX processing
│   ├── ocr_service.py        # OCR functionality
│   └── rag_service.py         # RAG pipeline
└── chroma_db/             # Vector database storage (created automatically)
```

## Usage Example

### Upload a Document
```bash
curl -X POST "http://localhost:8000/api/upload/document?session_id=YOUR_SESSION_ID" \
  -F "file=@document.pdf"
```

### Send a Chat Message
```bash
curl -X POST "http://localhost:8000/api/chat" \
  -H "Content-Type: application/json" \
  -d '{"session_id": "YOUR_SESSION_ID", "message": "What is the return policy?"}'
```

## Notes

- The first run will download models, which may take time
- ChromaDB stores vectors in `./chroma_db/`
- SQLite database is created at `./chatbot.db`
- For production, consider using PostgreSQL instead of SQLite

## Troubleshooting

1. **OCR not working**: Install Tesseract or use EasyOCR
2. **LLM loading slow**: First run downloads models (~500MB-2GB)
3. **Memory issues**: Use smaller models or HuggingFace API
4. **CORS errors**: Update `allow_origins` in `main.py` with your frontend URL

