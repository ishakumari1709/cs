#!/usr/bin/env python3
"""
Simple startup script for the FastAPI backend
"""
import uvicorn
import os

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    print(f"Starting AI Customer Support Chatbot Backend...")
    print(f"API will be available at http://0.0.0.0:{port}")
    print(f"API docs available at http://0.0.0.0:{port}/docs")
    # Disable reload in production (Render sets PORT automatically)
    reload_enabled = os.getenv("ENVIRONMENT", "production") == "development"
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=reload_enabled,
        log_level="info"
    )

