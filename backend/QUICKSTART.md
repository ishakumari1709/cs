# Quick Start Guide

Get your AI Customer Support Chatbot backend running in minutes!

## Step 1: Install Dependencies

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

# Install packages
pip install -r requirements.txt
```

**Note**: First installation may take 5-10 minutes as it downloads models and dependencies.

## Step 2: (Optional) Configure HuggingFace API

For better LLM performance, get a free API key from [HuggingFace](https://huggingface.co/settings/tokens):

```bash
# Create .env file
echo "HUGGINGFACE_API_KEY=your_key_here" > .env
```

If you don't set this, the system will use a local model (GPT-2) which is smaller but still functional.

## Step 3: Start the Server

```bash
python start.py
```

Or:

```bash
python main.py
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Step 4: Test the API

In another terminal:

```bash
python test_api.py
```

Or test manually:

```bash
# Create a session
curl -X POST "http://localhost:8000/api/sessions" -H "Content-Type: application/json" -d '{"title": "Test Chat"}'

# Send a chat message (replace SESSION_ID)
curl -X POST "http://localhost:8000/api/chat" -H "Content-Type: application/json" -d '{"session_id": "SESSION_ID", "message": "Hello!"}'
```

## Step 5: Connect Frontend

See `FRONTEND_INTEGRATION.md` for detailed instructions on connecting your React frontend.

## Troubleshooting

### Issue: "No module named 'langchain'"
**Solution**: Make sure you activated your virtual environment and installed requirements.

### Issue: OCR not working
**Solution**: 
- Install Tesseract OCR on your system, OR
- The system will automatically use EasyOCR if Tesseract is not available

### Issue: LLM loading slowly
**Solution**: 
- First run downloads models (~500MB for GPT-2)
- Use HuggingFace API key for faster, better responses
- Be patient on first run!

### Issue: Port 8000 already in use
**Solution**: Change the port in `start.py` or `main.py`:
```python
uvicorn.run(app, host="0.0.0.0", port=8001)  # Use port 8001
```

### Issue: Memory errors
**Solution**: 
- Use HuggingFace API instead of local model
- Or reduce model size in `rag_service.py`

## Next Steps

1. Upload a document (PDF or DOCX)
2. Ask questions about the document
3. Upload screenshots for OCR processing
4. Check the API docs at http://localhost:8000/docs

Enjoy your AI Customer Support Chatbot! 🚀

