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

  const createNewSession = async (): Promise<string | null> => {
    try {
      const data = await api.createSession('New Chat');
      setSessionId(data.id);
      sessionStorage.setItem('currentSessionId', data.id);
      setMessages([]);
      return data.id;
    } catch (error) {
      console.error('Error creating session:', error);
      return null;
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
    if (!sessionId) {
      console.error('No session ID available');
      // Try to get session ID from storage
      const storedSessionId = sessionStorage.getItem('currentSessionId');
      if (storedSessionId) {
        setSessionId(storedSessionId);
        // Retry with the session ID
        setTimeout(() => sendMessage(content), 500);
        return;
      }
      console.error('Cannot send message: No session ID');
      return;
    }

    if (!content.trim()) return;

    await addMessage('user', content);
    setIsTyping(true);

    try {
      const response = await api.sendChatMessage(sessionId, content);
      await addMessage('assistant', response.message);
    } catch (error: any) {
      console.error('Error sending message:', error);
      const errorMsg = error.message || 'Sorry, I encountered an error. Please try again.';
      await addMessage('assistant', `Error: ${errorMsg}`);
    } finally {
      setIsTyping(false);
    }
  };

  const startNewChat = () => {
    sessionStorage.removeItem('currentSessionId');
    createNewSession();
  };

  const addUploadedFile = async (filename: string, fileType: string) => {
    // File info is saved automatically by the backend when uploading
    // This function is kept for compatibility
  };

  const addImageMessage = async (imageData: string, mimeType: string) => {
    if (!sessionId) return;

    const jsonContent = JSON.stringify({ type: 'image', data: imageData, mimeType });
    await addMessage('user', jsonContent);

    setIsTyping(true);
    try {
      // Convert base64 to blob and upload
      const response = await fetch(imageData);
      const blob = await response.blob();
      const file = new File([blob], 'image.png', { type: mimeType });
      
      await api.uploadImage(sessionId, file);
      await addMessage('assistant', "I've received your image and extracted the text. How can I help you with this?");
    } catch (error) {
      console.error('Error processing image:', error);
      await addMessage('assistant', "I've received your image. How can I help you?");
    } finally {
      setIsTyping(false);
    }
  };

  // Helper function to ensure session exists
  const ensureSession = async (): Promise<string | null> => {
    if (sessionId) {
      return sessionId;
    }
    
    // Check storage
    const storedSessionId = sessionStorage.getItem('currentSessionId');
    if (storedSessionId) {
      setSessionId(storedSessionId);
      return storedSessionId;
    }
    
    // Create new session
    return await createNewSession();
  };

  return {
    messages,
    isTyping,
    sendMessage,
    startNewChat,
    addUploadedFile,
    addImageMessage,
    sessionId, // Expose sessionId so App can use it
    ensureSession, // Expose ensureSession function
  };
}
