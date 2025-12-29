import { useState, useEffect } from 'react';
import Header from './components/Header';
import UploadSection from './components/UploadSection';
import ChatContainer from './components/ChatContainer';
import ChatInput from './components/ChatInput';
import Notification from './components/Notification';
import { useChat } from './hooks/useChat';
import { api } from './lib/api';

function App() {
  const { messages, isTyping, sendMessage, startNewChat, addUploadedFile, addImageMessage, sessionId, ensureSession } = useChat();
  const [notification, setNotification] = useState<string | null>(null);

  const handleDocumentUpload = async (file: File) => {
    // Ensure session exists before uploading
    let currentSessionId = sessionId;
    
    if (!currentSessionId) {
      setNotification('Creating session...');
      currentSessionId = await ensureSession();
      
      if (!currentSessionId) {
        setNotification('Error: Could not create session. Please check if backend is running at http://localhost:8000');
        return;
      }
    }

    try {
      setNotification('Uploading document...');
      const result = await api.uploadDocument(currentSessionId, file);
      addUploadedFile(file.name, file.type);
      setNotification(`Document uploaded! Processed ${result.chunks} chunks.`);
    } catch (error: any) {
      console.error('Upload error:', error);
      const errorMessage = error.message || 'Failed to upload document. Please try again.';
      
      // Check if it's a backend connection error
      if (errorMessage.includes('Failed to fetch') || errorMessage.includes('Network')) {
        setNotification('Error: Cannot connect to backend. Make sure the server is running at http://localhost:8000');
      } else {
        setNotification(`Error: ${errorMessage}`);
      }
    }
  };

  const handleScreenshotUpload = async (file: File) => {
    // Ensure session exists before uploading
    let currentSessionId = sessionId;
    
    if (!currentSessionId) {
      setNotification('Creating session...');
      currentSessionId = await ensureSession();
      
      if (!currentSessionId) {
        setNotification('Error: Could not create session. Please check if backend is running at http://localhost:8000');
        return;
      }
    }

    try {
      setNotification('Processing screenshot...');
      await api.uploadScreenshot(currentSessionId, file);
      addUploadedFile(file.name, file.type);
      setNotification('Screenshot processed successfully!');
    } catch (error: any) {
      console.error('Upload error:', error);
      const errorMessage = error.message || 'Failed to process screenshot. Please try again.';
      
      // Check if it's a backend connection error
      if (errorMessage.includes('Failed to fetch') || errorMessage.includes('Network')) {
        setNotification('Error: Cannot connect to backend. Make sure the server is running at http://localhost:8000');
      } else {
        setNotification(`Error: ${errorMessage}`);
      }
    }
  };

  const handleImageUpload = (file: File) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      const imageData = e.target?.result as string;
      addImageMessage(imageData, file.type);
      setNotification('Image sent successfully.');
    };
    reader.readAsDataURL(file);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 flex flex-col font-sans">
      <Header />

      <UploadSection
        onDocumentUpload={handleDocumentUpload}
        onScreenshotUpload={handleScreenshotUpload}
      />

      <div className="flex-1 flex items-center justify-center px-4 pb-4">
        <div className="w-full max-w-4xl h-[600px] bg-white rounded-3xl shadow-2xl flex flex-col overflow-hidden border border-gray-100">
          <ChatContainer messages={messages} isTyping={isTyping} />
          <ChatInput
            onSendMessage={sendMessage}
            onImageUpload={handleImageUpload}
            onNewChat={startNewChat}
            disabled={isTyping}
          />
        </div>
      </div>

      <footer className="py-8 text-center text-sm text-gray-500 font-medium">
        Built by Isha| Powered by React + AI
      </footer>

      {notification && (
        <Notification
          message={notification}
          onClose={() => setNotification(null)}
        />
      )}
    </div>
  );
}

export default App;
