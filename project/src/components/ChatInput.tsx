import { useState, useRef } from 'react';
import { Send, Image } from 'lucide-react';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  onImageUpload: (file: File) => void;
  onNewChat: () => void;
  disabled: boolean;
}

export default function ChatInput({ onSendMessage, onImageUpload, onNewChat, disabled }: ChatInputProps) {
  const [input, setInput] = useState('');
  const imageInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim() && !disabled) {
      onSendMessage(input.trim());
      setInput('');
    }
  };

  const handleImageChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onImageUpload(file);
      e.target.value = '';
    }
  };

  return (
    <div className="border-t border-gray-100 bg-gradient-to-t from-gray-50 to-white px-5 py-4 shadow-lg">
      <form onSubmit={handleSubmit} className="flex gap-3 items-center">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Type your message…"
          disabled={disabled}
          className="flex-1 px-5 py-3 border-2 border-gray-200 rounded-2xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:bg-gray-100 disabled:cursor-not-allowed transition-all font-medium bg-white hover:border-gray-300"
        />

        <label className="cursor-pointer group">
          <input
            ref={imageInputRef}
            type="file"
            accept="image/*"
            onChange={handleImageChange}
            className="hidden"
            disabled={disabled}
          />
          <div className="px-5 py-3 border-2 border-gray-200 text-gray-700 rounded-2xl hover:border-blue-400 hover:bg-blue-50 disabled:bg-gray-100 disabled:cursor-not-allowed transition-all font-semibold flex items-center gap-2 group-hover:shadow-md hover:shadow-md">
            <Image className="w-5 h-5 text-blue-600" />
            Image
          </div>
        </label>

        <button
          type="submit"
          disabled={!input.trim() || disabled}
          className="px-6 py-3 bg-gradient-to-r from-blue-500 to-blue-600 text-white rounded-2xl hover:from-blue-600 hover:to-blue-700 hover:shadow-lg disabled:bg-gray-300 disabled:cursor-not-allowed transition-all flex items-center gap-2 font-semibold active:scale-95"
        >
          <Send className="w-5 h-5" />
          Send
        </button>
        <button
          type="button"
          onClick={onNewChat}
          disabled={disabled}
          className="px-6 py-3 border-2 border-gray-300 text-gray-700 rounded-2xl hover:border-gray-400 hover:bg-gray-100 hover:shadow-md disabled:bg-gray-100 disabled:cursor-not-allowed transition-all font-semibold active:scale-95"
        >
          New Chat
        </button>
      </form>
    </div>
  );
}
