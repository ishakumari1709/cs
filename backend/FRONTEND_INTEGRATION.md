# Frontend Integration Guide

This guide explains how to connect the existing React frontend to the FastAPI backend.

## Option 1: Update Frontend to Use FastAPI (Recommended)

Update the `project/src/lib/supabase.ts` file to use the FastAPI backend instead of Supabase.

### Step 1: Create API Client

Create a new file `project/src/lib/api.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export interface ChatSession {
  id: string;
  created_at: string;
  updated_at: string;
  title: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface UploadedFile {
  id: string;
  session_id: string;
  filename: string;
  file_type: string;
  created_at: string;
}

class APIClient {
  private baseURL: string;

  constructor() {
    this.baseURL = API_BASE_URL;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const response = await fetch(`${this.baseURL}${endpoint}`, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
    });

    if (!response.ok) {
      throw new Error(`API error: ${response.statusText}`);
    }

    return response.json();
  }

  async createSession(title: string = 'New Chat'): Promise<ChatSession> {
    return this.request<ChatSession>('/api/sessions', {
      method: 'POST',
      body: JSON.stringify({ title }),
    });
  }

  async getMessages(sessionId: string): Promise<Message[]> {
    return this.request<Message[]>(`/api/sessions/${sessionId}/messages`);
  }

  async createMessage(
    sessionId: string,
    role: 'user' | 'assistant',
    content: string
  ): Promise<Message> {
    return this.request<Message>('/api/messages', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, role, content }),
    });
  }

  async sendChatMessage(
    sessionId: string,
    message: string
  ): Promise<{ message: string; sources: string[] }> {
    return this.request<{ message: string; sources: string[] }>('/api/chat', {
      method: 'POST',
      body: JSON.stringify({ session_id: sessionId, message }),
    });
  }

  async uploadDocument(
    sessionId: string,
    file: File
  ): Promise<{ message: string; file_id: string; chunks: number }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(
      `${this.baseURL}/api/upload/document?session_id=${sessionId}`,
      {
        method: 'POST',
        body: formData,
      }
    );

    if (!response.ok) {
      throw new Error(`Upload error: ${response.statusText}`);
    }

    return response.json();
  }

  async uploadScreenshot(
    sessionId: string,
    file: File
  ): Promise<{ message: string; file_id: string; extracted_text: string }> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await fetch(
      `${this.baseURL}/api/upload/screenshot?session_id=${sessionId}`,
      {
        method: 'POST',
        body: formData,
      }
    );

    if (!response.ok) {
      throw new Error(`Upload error: ${response.statusText}`);
    }

    return response.json();
  }

  async uploadImage(
    sessionId: string,
    file: File
  ): Promise<{ message: string; file_id: string; extracted_text: string }> {
    return this.uploadScreenshot(sessionId, file);
  }
}

export const api = new APIClient();
```

### Step 2: Update useChat Hook

Update `project/src/hooks/useChat.ts` to use the new API client:

```typescript
import { useState, useEffect } from 'react';
import { api, Message } from '../lib/api';

export function useChat() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    const storedSessionId = sessionStorage.getItem('currentSessionId');
    if (storedSessionId) {
      setSessionId(storedSessionId);
      loadMessages(storedSessionId);
    } else {
      createNewSession();
    }
  }, []);

  const createNewSession = async () => {
    try {
      const data = await api.createSession('New Chat');
      setSessionId(data.id);
      sessionStorage.setItem('currentSessionId', data.id);
      setMessages([]);
    } catch (error) {
      console.error('Error creating session:', error);
    }
  };

  const loadMessages = async (sessionId: string) => {
    try {
      const data = await api.getMessages(sessionId);
      setMessages(data);
    } catch (error) {
      console.error('Error loading messages:', error);
    }
  };

  const addMessage = async (role: 'user' | 'assistant', content: string) => {
    if (!sessionId) return;

    try {
      const data = await api.createMessage(sessionId, role, content);
      setMessages((prev) => [...prev, data]);
    } catch (error) {
      console.error('Error adding message:', error);
    }
  };

  const sendMessage = async (content: string) => {
    if (!sessionId) return;

    await addMessage('user', content);
    setIsTyping(true);

    try {
      const response = await api.sendChatMessage(sessionId, content);
      await addMessage('assistant', response.message);
    } catch (error) {
      console.error('Error sending message:', error);
      await addMessage('assistant', 'Sorry, I encountered an error. Please try again.');
    } finally {
      setIsTyping(false);
    }
  };

  const startNewChat = () => {
    sessionStorage.removeItem('currentSessionId');
    createNewSession();
  };

  const addUploadedFile = async (filename: string, fileType: string) => {
    if (!sessionId) return;
    // File info is saved automatically by the backend
  };

  const addImageMessage = async (imageData: string, mimeType: string) => {
    const jsonContent = JSON.stringify({ type: 'image', data: imageData, mimeType });
    await addMessage('user', jsonContent);

    setIsTyping(true);
    try {
      // Convert base64 to blob and upload
      const response = await fetch(imageData);
      const blob = await response.blob();
      const file = new File([blob], 'image.png', { type: mimeType });
      
      await api.uploadImage(sessionId!, file);
      await addMessage('assistant', "I've received your image and extracted the text. How can I help you with this?");
    } catch (error) {
      console.error('Error processing image:', error);
      await addMessage('assistant', "I've received your image. How can I help you?");
    } finally {
      setIsTyping(false);
    }
  };

  return {
    messages,
    isTyping,
    sendMessage,
    startNewChat,
    addUploadedFile,
    addImageMessage,
  };
}
```

### Step 3: Update App.tsx

Update `project/src/App.tsx` to handle document uploads:

```typescript
// ... existing imports ...

function App() {
  const { messages, isTyping, sendMessage, startNewChat, addUploadedFile, addImageMessage } = useChat();
  const [notification, setNotification] = useState<string | null>(null);
  const [sessionId, setSessionId] = useState<string | null>(null);

  // Get sessionId from useChat or sessionStorage
  useEffect(() => {
    const storedSessionId = sessionStorage.getItem('currentSessionId');
    setSessionId(storedSessionId);
  }, []);

  const handleDocumentUpload = async (file: File) => {
    if (!sessionId) {
      setNotification('Please wait for session to initialize...');
      return;
    }

    try {
      const { api } = await import('./lib/api');
      await api.uploadDocument(sessionId, file);
      addUploadedFile(file.name, file.type);
      setNotification('Document uploaded and processed successfully!');
    } catch (error) {
      console.error('Upload error:', error);
      setNotification('Error uploading document. Please try again.');
    }
  };

  const handleScreenshotUpload = async (file: File) => {
    if (!sessionId) {
      setNotification('Please wait for session to initialize...');
      return;
    }

    try {
      const { api } = await import('./lib/api');
      await api.uploadScreenshot(sessionId, file);
      addUploadedFile(file.name, file.type);
      setNotification('Screenshot processed successfully!');
    } catch (error) {
      console.error('Upload error:', error);
      setNotification('Error processing screenshot. Please try again.');
    }
  };

  // ... rest of the component ...
}
```

### Step 4: Environment Variables

Create `project/.env`:

```
VITE_API_URL=http://localhost:8000
```

## Option 2: Keep Supabase for Storage, Use FastAPI for RAG

You can keep Supabase for session/message storage and use FastAPI only for RAG processing. This requires minimal frontend changes.

## Testing

1. Start the backend: `cd backend && python start.py`
2. Start the frontend: `cd project && npm run dev`
3. Open http://localhost:5173
4. Upload a document and start chatting!

