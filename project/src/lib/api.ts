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
    try {
      const response = await fetch(`${this.baseURL}${endpoint}`, {
        ...options,
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
      });

      if (!response.ok) {
        let errorDetail = response.statusText;
        try {
          const error = await response.json();
          errorDetail = error.detail || error.message || errorDetail;
        } catch {
          // If JSON parsing fails, use status text
        }
        throw new Error(errorDetail || `API error: ${response.status} ${response.statusText}`);
      }

      return response.json();
    } catch (error: any) {
      if (error.message) {
        throw error;
      }
      throw new Error(`Network error: ${error.message || 'Failed to connect to server'}`);
    }
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
    try {
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
        let errorDetail = response.statusText;
        try {
          const error = await response.json();
          errorDetail = error.detail || error.message || errorDetail;
        } catch {
          // If JSON parsing fails, use status text
        }
        throw new Error(errorDetail || `Upload error: ${response.status} ${response.statusText}`);
      }

      return response.json();
    } catch (error: any) {
      if (error.message) {
        throw error;
      }
      throw new Error(`Upload failed: ${error.message || 'Network error'}`);
    }
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
      const error = await response.json().catch(() => ({ detail: response.statusText }));
      throw new Error(error.detail || `Upload error: ${response.statusText}`);
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

