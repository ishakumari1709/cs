#!/usr/bin/env python3
"""
Simple test script to verify the API is working
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    print("Testing AI Customer Support Chatbot API...")
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.json()}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test 2: Create session
    print("\n2. Creating a new session...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/sessions",
            json={"title": "Test Chat"}
        )
        session = response.json()
        session_id = session["id"]
        print(f"   Session ID: {session_id}")
        print(f"   Session: {json.dumps(session, indent=2)}")
    except Exception as e:
        print(f"   Error: {e}")
        return
    
    # Test 3: Create message
    print("\n3. Creating a message...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/messages",
            json={
                "session_id": session_id,
                "role": "user",
                "content": "Hello, this is a test message!"
            }
        )
        message = response.json()
        print(f"   Message ID: {message['id']}")
        print(f"   Message: {message['content']}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 4: Get messages
    print("\n4. Getting messages for session...")
    try:
        response = requests.get(f"{BASE_URL}/api/sessions/{session_id}/messages")
        messages = response.json()
        print(f"   Found {len(messages)} messages")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 5: Chat (without documents - should return fallback)
    print("\n5. Testing chat endpoint (no documents uploaded yet)...")
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            json={
                "session_id": session_id,
                "message": "What is the return policy?"
            }
        )
        chat_response = response.json()
        print(f"   Response: {chat_response['message']}")
        print(f"   Sources: {chat_response.get('sources', [])}")
    except Exception as e:
        print(f"   Error: {e}")
    
    print("\n✅ Basic API tests completed!")
    print(f"\nSession ID for further testing: {session_id}")

if __name__ == "__main__":
    test_api()

