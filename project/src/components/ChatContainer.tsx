import { useEffect, useRef } from 'react';
import ChatMessage from './ChatMessage';
import TypingIndicator from './TypingIndicator';
import { Message } from '../lib/supabase';

interface ChatContainerProps {
  messages: Message[];
  isTyping: boolean;
}

export default function ChatContainer({ messages, isTyping }: ChatContainerProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isTyping]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 space-y-2">
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-full">
          <p className="text-gray-400 text-center">
            Start a conversation by sending a message below
          </p>
        </div>
      ) : (
        <>
          {messages.map((message) => (
            <ChatMessage
              key={message.id}
              role={message.role}
              content={message.content}
            />
          ))}
          {isTyping && <TypingIndicator />}
        </>
      )}
      <div ref={messagesEndRef} />
    </div>
  );
}
